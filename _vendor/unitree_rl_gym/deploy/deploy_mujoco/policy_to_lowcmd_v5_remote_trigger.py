#!/usr/bin/env python3
"""
policy_to_lowcmd_v6_remote_trigger_dual_quiet.py

Behavior:
- Listens to LOCO API SetFsmId on multiple services (e.g., "sport" and "unitree_loco_api").
- When ENABLED (FSM in {500,801}): runs the same smooth policy publisher loop to rt/lowcmd.
- When DISABLED (FSM in {0,1,4}): **publishes NOTHING** (quiet). Optional one-shot zero-torque
  on the disabling edge with --send_zero_on_disable.

Why:
- You reported that even when disabled the prior version still wrote a PD-hold, masking limp mode.
- This version is "quiet when disabled" so other sources can own rt/lowcmd, and disconnect shows limp.

Usage:
  python3 policy_to_lowcmd_v6_remote_trigger_dual_quiet.py \
    --config /abs/path/to/g1_policy_only.yaml \
    --iface lo --domain 1 --rate 400 \
    --service sport --also_service unitree_loco_api \
    [--send_zero_on_disable]

"""
import argparse, time, threading, math, json, numpy as np, torch, yaml

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelPublisher, ChannelSubscriber
from unitree_sdk2py.core.channel_name import GetServerChannelName, ChannelType

from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_, LowState_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_ as LowCmd_default
from unitree_sdk2py.idl.unitree_api.msg.dds_ import Request_ as ApiRequest

try:
    from unitree_sdk2py.g1.loco.g1_loco_api import ROBOT_API_ID_LOCO_SET_FSM_ID
except Exception:
    ROBOT_API_ID_LOCO_SET_FSM_ID = 3502

def get_gravity_orientation(quaternion: np.ndarray) -> np.ndarray:
    qw, qx, qy, qz = quaternion
    g = np.zeros(3, dtype=np.float32)
    g[0] = 2 * (-qz * qx + qw * qy)
    g[1] = -2 * (qz * qy + qw * qx)
    g[2] = 1 - 2 * (qw * qw + qz * qz)
    return g

def load_policy(policy_path: str, device: torch.device):
    try:
        pol = torch.jit.load(policy_path, map_location=device); pol.eval(); return pol
    except Exception:
        pass
    obj = torch.load(policy_path, map_location=device)
    if hasattr(obj, "eval"):
        obj.eval(); return obj
    if isinstance(obj, dict):
        for k in ("policy","model","actor"):
            if k in obj and hasattr(obj[k], "eval"):
                obj[k].eval(); return obj[k]
    raise RuntimeError("Unsupported policy format")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--iface", default="lo")
    ap.add_argument("--domain", type=int, default=1)
    ap.add_argument("--rate", type=float, default=400.0)
    ap.add_argument("--service", default="sport", help="primary service to observe")
    ap.add_argument("--also_service", action="append", default=[], help="extra services to observe (repeatable)")
    ap.add_argument("--start_ids", default="500,801")
    ap.add_argument("--stop_ids",  default="0,1,4")
    ap.add_argument("--send_zero_on_disable", action="store_true",
                    help="on disable edge, publish one LowCmd with kp=kd=tau=0 (limp)")
    args = ap.parse_args()

    start_ids = {int(s) for s in str(args.start_ids).split(",") if s.strip()}
    stop_ids  = {int(s) for s in str(args.stop_ids).split(",")  if s.strip()}

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
    num_actions        = int(cfg["num_actions"])
    num_obs            = int(cfg["num_obs"])
    cmd_init           = np.array(cfg["cmd_init"], dtype=np.float32)
    control_decimation = int(cfg["control_decimation"])
    simulation_dt      = float(cfg["simulation_dt"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    policy = load_policy(policy_path, device)

    ChannelFactoryInitialize(args.domain, args.iface)

    # State from DDS
    state = {"q":None, "dq":None, "quat":None, "omega":None}
    lock = threading.Lock()

    def on_lowstate(msg: LowState_):
        motors = getattr(msg, "motor_state", None) or getattr(msg, "motorState", None)
        if motors is None: return
        n = min(num_actions, len(motors))
        with lock:
            state["q"]  = np.asarray([float(getattr(motors[i], "q", 0.0)) for i in range(n)], dtype=np.float32)
            state["dq"] = np.asarray([float(getattr(motors[i], "dq", 0.0)) for i in range(n)], dtype=np.float32)

    def on_sportstate(msg: SportModeState_):
        imu = getattr(msg, "imu_state", None)
        if imu is not None:
            q = getattr(imu, "quaternion", [1,0,0,0])
            g = getattr(imu, "gyroscope",  [0,0,0])
            quat = (float(q[0]), float(q[1]), float(q[2]), float(q[3]))
            omega= (float(g[0]), float(g[1]), float(g[2]))
        else:
            quat=(1.0,0.0,0.0,0.0); omega=(0.0,0.0,0.0)
        with lock:
            state["quat"]  = np.asarray(quat, dtype=np.float32)
            state["omega"] = np.asarray(omega, dtype=np.float32)

    ChannelSubscriber("rt/lowstate", LowState_).Init(on_lowstate, 50)
    for t in ("rt/sportmodestate", "sportmodestate", "lf/sportmodestate"):
        try:
            ChannelSubscriber(t, SportModeState_).Init(on_sportstate, 50)
            print(f"[AI] Subscribed IMU state: {t}")
            break
        except Exception:
            continue

    # Enable gating from multiple services
    enable_lock = threading.Lock()
    enabled = {"on": False}
    last_change = {"t": 0.0}

    def set_enabled(v: bool, src: str):
        with enable_lock:
            if enabled["on"] != v:
                enabled["on"] = v
                last_change["t"] = time.time()
                print(f"[AI] Walking {'ENABLED' if v else 'DISABLED'} (source service='{src}').")

    def on_api_request_factory(service_name: str):
        def on_api_request(req: ApiRequest):
            try:
                api_id = int(req.header.identity.api_id)
            except Exception:
                return
            if api_id != ROBOT_API_ID_LOCO_SET_FSM_ID:
                return
            raw = getattr(req, "parameter", "{}") or "{}"
            try:
                data = json.loads(raw) if isinstance(raw, str) else {}
            except Exception:
                data = {}
            fsm = int(data.get("data", -1))
            if fsm in start_ids:
                set_enabled(True, service_name)
            elif fsm in stop_ids:
                set_enabled(False, service_name)
        return on_api_request

    services = [args.service] + [s for s in args.also_service if s]
    for default_name in ("sport", "unitree_loco_api"):
        if default_name not in services:
            services.append(default_name)

    for svc in services:
        topic = GetServerChannelName(svc, ChannelType.RECV)
        try:
            ChannelSubscriber(topic, ApiRequest).Init(on_api_request_factory(svc), 64)
            print(f"[AI] Observing LOCO API requests on '{topic}' (service='{svc}').")
        except Exception as e:
            print(f"[AI][WARN] Could not subscribe to '{topic}': {e}")

    pub = ChannelPublisher("rt/lowcmd", LowCmd_); pub.Init()

    obs      = np.zeros(num_obs, dtype=np.float32)
    action   = np.zeros(num_actions, dtype=np.float32)
    target_q = q0.copy()
    cmd      = cmd_init.astype(np.float32)

    inner_dt = 1.0 / float(args.rate)
    ctr = 0
    period = 0.8
    WARM_S = 0.7

    def publish_pd_hold():
        msg = LowCmd_default()
        motors = msg.motor_cmd
        N = min(num_actions, len(motors))
        for i in range(N):
            m = motors[i]
            m.q  = float(q0[i]); m.dq = 0.0
            m.kp = float(kps[i]) if np.ndim(kps) else float(kps)
            m.kd = float(kds[i]) if np.ndim(kds) else float(kds)
            m.tau= 0.0
        for i in range(N, len(motors)):
            mi = motors[i]; mi.q=0.0; mi.dq=0.0; mi.kp=0.0; mi.kd=0.0; mi.tau=0.0
        pub.Write(msg)

    def publish_zero_once():
        msg = LowCmd_default()
        for i in range(len(msg.motor_cmd)):
            m = msg.motor_cmd[i]
            m.mode = 1; m.q=0.0; m.dq=0.0; m.kp=0.0; m.kd=0.0; m.tau=0.0
        pub.Write(msg)

    print("[INFO] Ready. Publishing to rt/lowcmd at %.1f Hz when ENABLED." % (1.0/inner_dt,))
    last_enabled_state = False
    try:
        while True:
            t0 = time.time()
            with enable_lock:
                is_on = bool(enabled["on"])
                t_enable = float(last_change["t"])

            # Edge detection: if just disabled, optionally send one zero-torque
            if (last_enabled_state is True) and (is_on is False):
                if args.send_zero_on_disable:
                    publish_zero_once()

            last_enabled_state = is_on

            if not is_on:
                # QUIET when disabled: publish nothing
                time.sleep(max(0.0, inner_dt))
                continue

            # Enabled: need sensor state
            with lock:
                q = state["q"]; dq = state["dq"]; quat = state["quat"]; omega = state["omega"]

            if q is None or dq is None or quat is None or omega is None:
                # No publish if state not ready; stay quiet to avoid interfering writers
                time.sleep(max(0.0, inner_dt))
                continue

            # Warmup hold before stepping
            if (time.time() - t_enable) < WARM_S:
                publish_pd_hold()
            else:
                if ctr % control_decimation == 0:
                    gravity = get_gravity_orientation(quat)
                    omega_s = omega * ang_vel_scale
                    qj  = (q  - q0) * dof_pos_scale
                    dqj = (dq)     * dof_vel_scale
                    t   = ctr * simulation_dt
                    phase = (t % period) / period
                    sinp, cosp = math.sin(2.0*math.pi*phase), math.cos(2.0*math.pi*phase)

                    obs[0:3] = omega_s
                    obs[3:6] = gravity
                    obs[6:9] = cmd * cmd_scale
                    obs[9:9+num_actions] = qj
                    obs[9+num_actions:9+2*num_actions] = dqj
                    obs[9+2*num_actions:9+3*num_actions] = action
                    obs[9+3*num_actions:9+3*num_actions+2] = np.array([sinp, cosp], dtype=np.float32)

                    with torch.no_grad():
                        out = policy(torch.from_numpy(obs).to(device).unsqueeze(0))
                        if isinstance(out, (tuple, list)): out = out[0]
                        action = out.detach().cpu().numpy().squeeze().astype(np.float32)
                    target_q = action * action_scale + q0

                msg = LowCmd_default()
                motors = msg.motor_cmd
                N = min(num_actions, len(motors))
                for i in range(N):
                    m = motors[i]
                    m.q  = float(target_q[i]); m.dq = 0.0
                    m.kp = float(kps[i]) if np.ndim(kps) else float(kps)
                    m.kd = float(kds[i]) if np.ndim(kds) else float(kds)
                    m.tau= 0.0
                for i in range(N, len(motors)):
                    mi = motors[i]; mi.q=0.0; mi.dq=0.0; mi.kp=0.0; mi.kd=0.0; mi.tau=0.0
                pub.Write(msg)

            ctr += 1
            dt = inner_dt - (time.time() - t0)
            if dt > 0: time.sleep(dt)

    except KeyboardInterrupt:
        print("\\n[INFO] Stopped.")

if __name__ == "__main__":
    main()