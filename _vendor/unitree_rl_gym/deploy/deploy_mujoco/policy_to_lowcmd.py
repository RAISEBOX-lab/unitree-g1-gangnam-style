#!/usr/bin/env python3
"""
policy_to_lowcmd.py
Run a Torch JIT policy and publish desired joint positions to Unitree SDK2 "rt/lowcmd".
No MuJoCo viewer here; assumes *something else* (real robot or unitree_mujoco) is publishing states.

Usage:
  python3 policy_to_lowcmd.py --config /abs/path/to/g1.yaml --iface lo --domain 1

YAML must contain the same fields you used in deploy_mujoco:
  policy_path, kps, kds, default_angles, ang_vel_scale, dof_pos_scale, dof_vel_scale,
  cmd_scale, action_scale, num_actions, num_obs, cmd_init, control_decimation, simulation_dt
"""

import argparse
import time
import threading
import math
import numpy as np
import torch
import yaml

# Unitree SDK2 (Python)
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelPublisher
from unitree_sdk2py.core.channel import ChannelSubscriber


# G1/H1-2 use unitree_hg idl
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_, LowState_
# SportModeState lives under unitree_go for some robots; for G1 it's hg:
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_ as LowCmd_default


def get_gravity_orientation(quaternion):
    qw, qx, qy, qz = quaternion
    g = np.zeros(3, dtype=np.float32)
    g[0] =  2 * (-qz*qx + qw*qy)
    g[1] = -2 * ( qz*qy + qw*qx)
    g[2] =  1 - 2 * (qw*qw + qz*qz)
    return g

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, type=str)
    ap.add_argument("--iface", default="lo", help="DDS network interface (lo for local sim)")
    ap.add_argument("--domain", type=int, default=1, help="CycloneDDS domain id (match the sim)")
    ap.add_argument("--rate", type=float, default=400.0, help="inner loop Hz (policy decimated)")
    args = ap.parse_args()

    # Load YAML
    cfg = yaml.safe_load(open(args.config, "r"))
    policy_path = cfg["policy_path"]
    kps  = np.array(cfg["kps"], dtype=np.float32)
    kds  = np.array(cfg["kds"], dtype=np.float32)
    q0   = np.array(cfg["default_angles"], dtype=np.float32)
    ang_vel_scale = float(cfg["ang_vel_scale"])
    dof_pos_scale = float(cfg["dof_pos_scale"])
    dof_vel_scale = float(cfg["dof_vel_scale"])
    action_scale  = float(cfg["action_scale"])
    cmd_scale     = np.array(cfg["cmd_scale"], dtype=np.float32)
    num_actions   = int(cfg["num_actions"])
    num_obs       = int(cfg["num_obs"])
    cmd_init      = np.array(cfg["cmd_init"], dtype=np.float32)
    control_decimation = int(cfg["control_decimation"])
    simulation_dt      = float(cfg["simulation_dt"])

    # Load policy
    policy = torch.jit.load(policy_path)
    policy.eval()

    # DDS init
    ChannelFactoryInitialize(args.domain, args.iface)

    # Shared state buffer (from DDS)
    state = {
        "q": None,    # joint positions (np.float32 [N])
        "dq": None,   # joint velocities
        "quat": None, # base orientation (w,x,y,z)
        "omega": None # base angular velocity (xyz)
    }
    lock = threading.Lock()

    # --- Subscribers ---
    def on_lowstate(msg: LowState_):
        # Accept both .motor_state (snake_case) and .motorState (camelCase)
        motors = getattr(msg, "motor_state", None)
        if motors is None:
            motors = getattr(msg, "motorState", None)
        if motors is None:
            # Some SDK builds wrap motors differently; fail soft
            return

        q_list, dq_list = [], []
        n = len(q0)  # assume policy uses first len(q0) actuated joints
        for i in range(n):
            m = motors[i]
            # Fields are consistently 'q' and 'dq' across variants
            q_list.append(float(getattr(m, "q", 0.0)))
            dq_list.append(float(getattr(m, "dq", 0.0)))

        with lock:
            state["q"] = np.asarray(q_list, dtype=np.float32)
            state["dq"] = np.asarray(dq_list, dtype=np.float32)


    def on_sportstate(msg: SportModeState_):
        # Prefer the common container: msg.imu_state.{quaternion,gyroscope}
        imu = getattr(msg, "imu_state", None)

        if imu is not None:
            quat_arr = getattr(imu, "quaternion", None)
            gyro_arr = getattr(imu, "gyroscope", None)
            if quat_arr is not None and len(quat_arr) >= 4:
                quat = (float(quat_arr[0]), float(quat_arr[1]),
                        float(quat_arr[2]), float(quat_arr[3]))
            else:
                quat = (1.0, 0.0, 0.0, 0.0)  # fallback

            if gyro_arr is not None and len(gyro_arr) >= 3:
                omega = (float(gyro_arr[0]), float(gyro_arr[1]), float(gyro_arr[2]))
            else:
                omega = (0.0, 0.0, 0.0)

        else:
            # Older/camelCase style: msg.imu_quaternion.{w,x,y,z}, msg.imu_gyroscope.{x,y,z}
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


    # Subscribe (topic names differ across stacks; try common ones)
    sub_low  = ChannelSubscriber("rt/lowstate", LowState_)
    sub_low.Init(on_lowstate, 50)

    tried_topics = ["sportmodestate", "rt/sportmodestate", "lf/sportmodestate"]
    sub_sport = None
    for t in tried_topics:
        try:
            ss = ChannelSubscriber(t, SportModeState_)
            ss.Init(on_sportstate, 50)
            sub_sport = ss
            break
        except Exception:
            continue

    if sub_sport is None:
        print("[WARN] Could not subscribe to SportModeState (tried:", tried_topics, ") — policy obs will miss IMU terms.")

    # --- Publisher ---
    pub = ChannelPublisher("rt/lowcmd", LowCmd_)
    pub.Init()

    # Context
    action = np.zeros(num_actions, dtype=np.float32)
    target_q = q0.copy()
    obs = np.zeros(num_obs, dtype=np.float32)
    cmd = cmd_init.astype(np.float32)

    # Loop timing
    inner_dt = 1.0 / args.rate
    ctr = 0


    # --- Warm hold: PD to default_angles for 0.7 s ---
    msg = LowCmd_default()
    motors = msg.motor_cmd
    N = min(len(q0), len(motors))
    for i in range(N):
        m = motors[i]
        m.q  = float(q0[i])
        m.dq = 0.0
        m.kp = float(kps[i]) if np.ndim(kps) else float(kps)
        m.kd = float(kds[i]) if np.ndim(kds) else float(kds)
        m.tau = 0.0

    t_end = time.time() + 0.7
    while time.time() < t_end:
        pub.Write(msg)
        time.sleep(0.01)



    print("[INFO] Running. Press Ctrl+C to stop.")
    try:
        last = time.time()
        while True:
            t0 = time.time()

            # Build observation when we have fresh state
            with lock:
                q   = state["q"]
                dq  = state["dq"]
                quat  = state["quat"]
                omega = state["omega"]

            if q is not None and dq is not None:
                qj  = (q - q0) * dof_pos_scale
                dqj = dq * dof_vel_scale

                if quat is None:
                    gravity_orientation = np.zeros(3, dtype=np.float32)
                else:
                    gravity_orientation = get_gravity_orientation(quat)

                if omega is None:
                    omega_s = np.zeros(3, dtype=np.float32)
                else:
                    omega_s = np.array(omega, dtype=np.float32) * ang_vel_scale

                # simple phase features (as in your snippet)
                period = 0.8
                count  = ctr * simulation_dt
                phase  = (count % period) / period
                sinp, cosp = math.sin(2*math.pi*phase), math.cos(2*math.pi*phase)

                # pack obs
                # [0:3]=omega, [3:6]=gravity, [6:9]=cmd*scale, then qj, dqj, previous action, then [sin,cos]
                obs[:3] = omega_s
                obs[3:6] = gravity_orientation
                obs[6:9] = cmd * cmd_scale
                obs[9:9+num_actions] = qj
                obs[9+num_actions:9+2*num_actions] = dqj
                obs[9+2*num_actions:9+3*num_actions] = action
                obs[9+3*num_actions:9+3*num_actions+2] = np.array([sinp, cosp], dtype=np.float32)

                # policy
                with torch.no_grad():
                    action = policy(torch.from_numpy(obs).unsqueeze(0)).cpu().numpy().squeeze().astype(np.float32)

                # desired joint positions
                target_q = action * action_scale + q0

                # publish LowCmd with desired q and PD gains (zero desired dq, zero tau)
                msg = LowCmd_default()  # zero-initialized, all required fields present

                # Access the SDK's snake_case array
                motors = msg.motor_cmd
                N = min(len(q0), len(motors))  # don't exceed available motors

                for i in range(N):
                    m = motors[i]
                    m.q  = float(target_q[i])
                    m.dq = 0.0
                    m.kp = float(kps[i]) if np.ndim(kps) else float(kps)
                    m.kd = float(kds[i]) if np.ndim(kds) else float(kds)
                    m.tau = 0.0
                
                #print(f"[DBG] filling {N}/{len(motors)} motors; policy DOFs={len(q0)}")

                pub.Write(msg)

            ctr += 1
            # decimated timing aligned to your sim dt
            sleep_time = inner_dt - (time.time() - t0)
            if sleep_time > 0:
                time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("\n[INFO] Stopped.")

if __name__ == "__main__":
    main()
