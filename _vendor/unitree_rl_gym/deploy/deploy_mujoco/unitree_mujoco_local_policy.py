#!/usr/bin/env python3
"""
unitree_mujoco_local_policy.py
Direct MuJoCo + policy runner (no DDS), mirroring deploy_mujoco_23dof.py.

Usage:
  python3 unitree_mujoco_local_policy.py \
    --scene /home/user/unitree_mujoco/unitree_robots/g1/scene_23dof.xml \
    --config /home/user/unitree_rl_gym/deploy/deploy_mujoco/configs/g1_policy_only.yaml \
    --device cpu \
    --sim-seconds 60
"""

import argparse
import math
import time
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np
import torch
import yaml


def get_gravity_orientation(quaternion: np.ndarray) -> np.ndarray:
    """
    EXACT formula used by deploy_mujoco_23dof.py
    (note the signs; these matter a lot)
    """
    qw = quaternion[0]
    qx = quaternion[1]
    qy = quaternion[2]
    qz = quaternion[3]
    g = np.zeros(3, dtype=np.float32)
    g[0] = 2 * (-qz * qx + qw * qy)
    g[1] = -2 * (qz * qy + qw * qx)
    g[2] = 1 - 2 * (qw * qw + qz * qz)
    return g


def pd_control(q_target, q_meas, kp, _ff, dq_meas, kd):
    # same signature as deploy; no separate feedforward term here
    return kp * (q_target - q_meas) - kd * dq_meas


def load_policy(policy_path: str, device: torch.device):
    """
    Load TorchScript first; if that fails, try torch.load() eager module.
    """
    try:
        policy = torch.jit.load(policy_path, map_location=device)
        policy.eval()
        return policy
    except Exception:
        pass

    obj = torch.load(policy_path, map_location=device)
    if hasattr(obj, "eval"):
        obj.eval()
        return obj
    if isinstance(obj, dict):
        for k in ("policy", "model", "actor"):
            if k in obj and hasattr(obj[k], "eval"):
                obj[k].eval()
                return obj[k]
    raise RuntimeError("Unsupported policy format: neither TorchScript nor an eager nn.Module found.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", type=str, required=True, help="Path to MuJoCo scene XML (23-DoF recommended).")
    ap.add_argument("--config", type=str, required=True, help="YAML with policy path, gains, scales, dims.")
    ap.add_argument("--device", type=str, default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--sim-seconds", type=float, default=60.0)
    args = ap.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    policy_path         = cfg["policy_path"]
    simulation_dt       = float(cfg["simulation_dt"])
    control_decimation  = int(cfg["control_decimation"])

    kps            = np.array(cfg["kps"], dtype=np.float32)
    kds            = np.array(cfg["kds"], dtype=np.float32)
    default_angles = np.array(cfg["default_angles"], dtype=np.float32)

    ang_vel_scale  = float(cfg["ang_vel_scale"])
    dof_pos_scale  = float(cfg["dof_pos_scale"])
    dof_vel_scale  = float(cfg["dof_vel_scale"])
    action_scale   = float(cfg["action_scale"])
    cmd_scale      = np.array(cfg["cmd_scale"], dtype=np.float32)

    num_actions = int(cfg["num_actions"])   # 12
    num_obs     = int(cfg["num_obs"])       # 47
    cmd         = np.array(cfg["cmd_init"], dtype=np.float32)  # e.g., [0.5, 0, 0]

    # Model
    xml_path = args.scene
    if not Path(xml_path).exists():
        raise FileNotFoundError(f"Scene not found: {xml_path}")
    m = mujoco.MjModel.from_xml_path(xml_path)
    d = mujoco.MjData(m)

    # Force dt parity
    if abs(m.opt.timestep - simulation_dt) > 1e-12:
        print(f"[INFO] timestep(current)={m.opt.timestep} -> set {simulation_dt}")
        m.opt.timestep = simulation_dt

    # Device + Policy
    device = torch.device("cuda" if (args.device == "cuda" and torch.cuda.is_available()) else "cpu")
    policy = load_policy(policy_path, device=device)

    # Context buffers
    action = np.zeros(num_actions, dtype=np.float32)
    target_dof_pos = default_angles.copy()
    obs = np.zeros(num_obs, dtype=np.float32)
    counter = 0

    # Phase features identical to deploy (period=0.8 s)
    period = 0.8

    # Viewer + loop
    with mujoco.viewer.launch_passive(m, d) as viewer:
        # Optional: visuals (safe if enums exist)
        try:
            viewer.user_scn.flags[mujoco.mjtRndFlag.mjRND_SHADOW] = 1
            viewer.user_scn.flags[mujoco.mjtRndFlag.mjRND_REFLECTION] = 1
        except Exception:
            pass

        end_time = time.time() + float(args.sim-seconds) if hasattr(args, "sim-seconds") else time.time() + float(args.sim_seconds)

        while viewer.is_running() and time.time() < end_time:
            step_start = time.time()

            # === PD + step every tick (matches deploy timing) ===
            qj_pd  = d.qpos[7:7 + num_actions]
            dqj_pd = d.qvel[6:6 + num_actions]
            tau = pd_control(target_dof_pos, qj_pd, kps, np.zeros_like(kds), dqj_pd, kds)

            d.ctrl[:] = 0.0
            d.ctrl[:num_actions] = tau

            mujoco.mj_step(m, d)
            viewer.sync()

            # === Update action every control_decimation steps ===
            counter += 1
            if counter % control_decimation == 0:
                # Base orientation/angular velocity like deploy (not sensor sites)
                quat  = d.qpos[3:7]                 # w x y z
                omega = d.qvel[3:6] * ang_vel_scale # base angular vel scaled

                gravity_orientation = get_gravity_orientation(quat)

                # Joint obs must subtract default_angles BEFORE scaling (critical)
                qj  = d.qpos[7:7 + num_actions]
                dqj = d.qvel[6:6 + num_actions]
                qj  = (qj - default_angles) * dof_pos_scale
                dqj = dqj * dof_vel_scale

                # Phase as in deploy: based on (counter*dt) modulo period
                t = counter * simulation_dt
                phase = (t % period) / period
                sin_phase = math.sin(2.0 * math.pi * phase)
                cos_phase = math.cos(2.0 * math.pi * phase)

                # Build obs = [omega(3), gravity(3), cmd(3)*scale, q(12), dq(12), prev_action(12), sin/cos(2)]
                obs[0:3] = omega
                obs[3:6] = gravity_orientation
                obs[6:9] = cmd * cmd_scale
                obs[9:9 + num_actions] = qj
                obs[9 + num_actions:9 + 2 * num_actions] = dqj
                obs[9 + 2 * num_actions:9 + 3 * num_actions] = action
                obs[9 + 3 * num_actions:9 + 3 * num_actions + 2] = np.array([sin_phase, cos_phase], dtype=np.float32)

                with torch.no_grad():
                    obs_t = torch.from_numpy(obs).to(device).unsqueeze(0)
                    out = policy(obs_t)
                    if isinstance(out, (tuple, list)):
                        out = out[0]
                    action = out.detach().cpu().numpy().squeeze().astype(np.float32)

                target_dof_pos = action * action_scale + default_angles

            # Rudimentary time keeping (same spirit as deploy)
            time_until_next = m.opt.timestep - (time.time() - step_start)
            if time_until_next > 0:
                time.sleep(time_until_next)


if __name__ == "__main__":
    main()
