#!/usr/bin/env python3
"""
policy_to_lowcmd_v4_patched.py

Runs the locomotion policy and publishes LowCmd via DDS.
Behavior matches unitree_mujoco_local_policy(2).py:
- obs math: omega from base qvel[3:6], gravity from base quat qpos[3:7],
            qj = (q - default_angles), dqj = dq, phase period=0.8
- cadence:  publish PD EVERY inner tick; run policy only on decimated ticks

Usage:
  python3 policy_to_lowcmd_v4_patched.py \
    --config /abs/path/to/g1_policy_only.yaml \
    --iface lo --domain 1 --rate 400
"""

import argparse
import time
import threading
import math
import numpy as np
import torch
import yaml

# DDS / Unitree SDK2
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelPublisher
from unitree_sdk2py.core.channel import ChannelSubscriber

# G1/H1-2 use unitree_hg idl
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_, LowState_
# SportModeState lives under unitree_go for some robots; our bridge publishes this type
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_ as LowCmd_default


def get_gravity_orientation(quaternion: np.ndarray) -> np.ndarray:
    # EXACT formula used in the working local runner
    qw, qx, qy, qz = quaternion
    g = np.zeros(3, dtype=np.float32)
    g[0] = 2 * (-qz * qx + qw * qy)
    g[1] = -2 * (qz * qy + qw * qx)
    g[2] = 1 - 2 * (qw * qw + qz * qz)
    return g


def load_policy(policy_path: str, device: torch.device):
    # Try TorchScript, then eager
    try:
        pol = torch.jit.load(policy_path, map_location=device)
        pol.eval()
        return pol
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
    raise RuntimeError("Unsupported policy format (neither TorchScript nor a nn.Module)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, type=str)
    ap.add_argument("--iface", default="lo", help="DDS interface (lo for local)")
    ap.add_argument("--domain", type=int, default=1, help="DDS domain id")
    ap.add_argument("--rate", type=float, default=400.0, help="inner loop Hz")
    args = ap.parse_args()

    # Load YAML
    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    policy_path        = cfg["policy_path"]
    kps                = np.array(cfg["kps"], dtype=np.float32)
    kds                = np.array(cfg["kds"], dtype=np.float32)
    q0                 = np.array(cfg["default_angles"], dtype=np.float32)
    ang_vel_scale      = float(cfg["ang_vel_scale"])
    dof_pos_scale      = float(cfg["dof_pos_scale"])
    dof_vel_scale      = float(cfg["dof_vel_scale"])
    action_scale       = float(cfg["action_scale"])
    cmd_scale          = np.array(cfg["cmd_scale"], dtype=np.float32)
    num_actions        = int(cfg["num_actions"])  # 12
    num_obs            = int(cfg["num_obs"])      # 47
    cmd_init           = np.array(cfg["cmd_init"], dtype=np.float32)
    control_decimation = int(cfg["control_decimation"])
    simulation_dt      = float(cfg["simulation_dt"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    policy = load_policy(policy_path, device)

    # DDS init (use named args to avoid signature ambiguity)
    ChannelFactoryInitialize(args.domain, args.iface)

    # Shared state buffers (from DDS)
    state = {
        "q":    None,   # leg positions (12)
        "dq":   None,   # leg velocities (12)
        "quat": None,   # base quaternion (w,x,y,z)
        "omega":None,   # base angular velocity (xyz)
    }
    lock = threading.Lock()

    # --- Subscribers ---
    def on_lowstate(msg: LowState_):
        motors = getattr(msg, "motor_state", None) or getattr(msg, "motorState", None)
        if motors is None:
            return
        n = min(num_actions, len(motors))
        q_list  = [float(getattr(motors[i], "q", 0.0))  for i in range(n)]
        dq_list = [float(getattr(motors[i], "dq", 0.0)) for i in range(n)]
        with lock:
            state["q"]  = np.asarray(q_list, dtype=np.float32)
            state["dq"] = np.asarray(dq_list, dtype=np.float32)

    def on_sportstate(msg: SportModeState_):
        imu = getattr(msg, "imu_state", None)
        if imu is not None:
            quat_arr = getattr(imu, "quaternion", None)
            gyro_arr = getattr(imu, "gyroscope", None)
            if quat_arr is not None and len(quat_arr) >= 4:
                quat = (float(quat_arr[0]), float(quat_arr[1]),
                        float(quat_arr[2]), float(quat_arr[3]))
            else:
                quat = (1.0, 0.0, 0.0, 0.0)
            if gyro_arr is not None and len(gyro_arr) >= 3:
                omega = (float(gyro_arr[0]), float(gyro_arr[1]), float(gyro_arr[2]))
            else:
                omega = (0.0, 0.0, 0.0)
        else:
            # Legacy fallback (unlikely used with your bridge)
            iq = getattr(msg, "imu_quaternion", None)
            ig = getattr(msg, "imu_gyroscope", None)
            if iq is not None:
                quat = (float(getattr(iq, "w", 1.0)),
                        float(getattr(iq, "x", 0.0)),
                        float(getattr(iq, "y", 0.0)),
                        float(getattr(iq, "z", 0.0)))
            else:
                quat = (1.0, 0.0, 0.0, 0.0)
            if ig is not None:
                omega = (float(getattr(ig, "x", 0.0)),
                         float(getattr(ig, "y", 0.0)),
                         float(getattr(ig, "z", 0.0)))
            else:
                omega = (0.0, 0.0, 0.0)
        with lock:
            state["quat"]  = np.asarray(quat, dtype=np.float32)
            state["omega"] = np.asarray(omega, dtype=np.float32)

    # Subscribe
    sub_low = ChannelSubscriber("rt/lowstate", LowState_)
    sub_low.Init(on_lowstate, 50)

    tried_topics = ["rt/sportmodestate", "sportmodestate", "lf/sportmodestate"]
    sub_sport = None
    for t in tried_topics:
        try:
            s = ChannelSubscriber(t, SportModeState_)
            s.Init(on_sportstate, 50)
            sub_sport = s
            break
        except Exception:
            continue
    if sub_sport is None:
        print("[WARN] Could not subscribe to SportModeState — IMU terms will be missing.")

    # Publisher
    pub = ChannelPublisher("rt/lowcmd", LowCmd_)
    pub.Init()

    # Context
    obs      = np.zeros(num_obs, dtype=np.float32)
    action   = np.zeros(num_actions, dtype=np.float32)
    target_q = q0.copy()
    cmd      = cmd_init.astype(np.float32)

    inner_dt = 1.0 / float(args.rate)
    ctr = 0
    period = 0.8  # seconds

    # --- Warm hold: PD to default pose for 0.7s (stabilize while DDS settles) ---
    warm = LowCmd_default()
    mtrs = warm.motor_cmd
    N = min(num_actions, len(mtrs))
    for i in range(N):
        m = mtrs[i]
        m.q  = float(q0[i])
        m.dq = 0.0
        m.kp = float(kps[i]) if np.ndim(kps) else float(kps)
        m.kd = float(kds[i]) if np.ndim(kds) else float(kds)
        m.tau = 0.0
    t_end = time.time() + 0.7
    while time.time() < t_end:
        pub.Write(warm)
        time.sleep(0.01)

    print("[INFO] Running. Press Ctrl+C to stop.")
    try:
        while True:
            loop_start = time.time()

            # Snapshot state
            with lock:
                q     = state["q"]
                dq    = state["dq"]
                quat  = state["quat"]
                omega = state["omega"]

            # Flag to update policy this tick
            run_policy = False
            if q is not None and dq is not None and quat is not None and omega is not None:
                if ctr % control_decimation == 0:
                    # --- Build obs exactly like local runner ---
                    gravity = get_gravity_orientation(quat)
                    omega_s = omega * ang_vel_scale
                    qj      = (q  - q0) * dof_pos_scale
                    dqj     = (dq)     * dof_vel_scale

                    t = ctr * simulation_dt
                    phase = (t % period) / period
                    sinp, cosp = math.sin(2.0 * math.pi * phase), math.cos(2.0 * math.pi * phase)

                    obs[0:3] = omega_s
                    obs[3:6] = gravity
                    obs[6:9] = cmd * cmd_scale
                    obs[9:9+num_actions] = qj
                    obs[9+num_actions:9+2*num_actions] = dqj
                    obs[9+2*num_actions:9+3*num_actions] = action
                    obs[9+3*num_actions:9+3*num_actions+2] = np.array([sinp, cosp], dtype=np.float32)

                    with torch.no_grad():
                        out = policy(torch.from_numpy(obs).to(device).unsqueeze(0))
                        if isinstance(out, (tuple, list)):
                            out = out[0]
                        action = out.detach().cpu().numpy().squeeze().astype(np.float32)

                    target_q = action * action_scale + q0
                    run_policy = True

            # --- Always publish PD command each inner tick ---
            msg = LowCmd_default()
            motors = msg.motor_cmd
            N = min(num_actions, len(motors))
            if q is None or dq is None:
                # Hold default pose until state is ready
                for i in range(N):
                    m = motors[i]
                    m.q  = float(q0[i])
                    m.dq = 0.0
                    m.kp = float(kps[i]) if np.ndim(kps) else float(kps)
                    m.kd = float(kds[i]) if np.ndim(kds) else float(kds)
                    m.tau = 0.0
            else:
                # Use latest target_q (updated on decimated ticks, held in-between)
                for i in range(N):
                    m = motors[i]
                    m.q  = float(target_q[i])
                    m.dq = 0.0
                    m.kp = float(kps[i]) if np.ndim(kps) else float(kps)
                    m.kd = float(kds[i]) if np.ndim(kds) else float(kds)
                    m.tau = 0.0

            # Neutralize any remaining actuators (keep arms/waist inert)
            for i in range(N, len(motors)):
                mi = motors[i]
                mi.q = 0.0; mi.dq = 0.0; mi.kp = 0.0; mi.kd = 0.0; mi.tau = 0.0

            pub.Write(msg)

            ctr += 1
            # Timing
            sleep_time = inner_dt - (time.time() - loop_start)
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n[INFO] Stopped.")

if __name__ == "__main__":
    main()
