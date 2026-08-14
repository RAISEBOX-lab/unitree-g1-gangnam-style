#!/usr/bin/env python3
"""
policy_to_lowcmd_v8_remote_trigger_dual_modes_with_rpc.py

Unified controller + fast RPC responder:
- Observes LOCO SetFsmId requests on multiple services (sport, unitree_loco_api, plus --also_service).
- Immediately sends a Response on the corresponding SEND channel (fast, like loco_rpc_server_bridge_no_ai.py).
- Executes modes:
    * FSM 500/801 -> AI walking (smooth policy loop publishing to rt/lowcmd)
    * FSM 0       -> ZeroTorque (one-shot; or --zero_stream to stream zeros)
    * FSM 1       -> DampHold (capture pose, ramp kp/kd, then hold)
    * FSM 4       -> LockedStanding (blend to pose, gain ramp)
- When no active mode: QUIET (no publish).

Run:
  python3 policy_to_lowcmd_v8_remote_trigger_dual_modes_with_rpc.py \
    --config deploy/deploy_mujoco/configs/g1_policy_only.yaml \
    --iface lo --domain 1 --rate 400 \
    --service sport --also_service unitree_loco_api \
    [--zero_stream] [--send_zero_on_disable]
"""
import argparse, time, threading, math, json, numpy as np, torch, yaml, traceback

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelPublisher, ChannelSubscriber
from unitree_sdk2py.core.channel_name import GetServerChannelName, ChannelType
from unitree_sdk2py.utils.crc import CRC

from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_ as LowCmd, LowState_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_ as LowCmd_default

# RPC IDL
from unitree_sdk2py.idl.unitree_api.msg.dds_ import Request_         as Request
from unitree_sdk2py.idl.unitree_api.msg.dds_ import Response_        as Response
from unitree_sdk2py.idl.unitree_api.msg.dds_ import ResponseHeader_  as ResponseHeader
from unitree_sdk2py.idl.unitree_api.msg.dds_ import ResponseStatus_  as ResponseStatus
from unitree_sdk2py.idl.unitree_api.msg.dds_ import RequestIdentity_ as RequestIdentity

CRC_CALC = CRC()
MOTOR_SIZE = 35
CONTROLLED_DOF = 29

try:
    from unitree_sdk2py.g1.loco.g1_loco_api import ROBOT_API_ID_LOCO_SET_FSM_ID
except Exception:
    ROBOT_API_ID_LOCO_SET_FSM_ID = 3502

# ---- Joint indices (for reference) ----
class G1J:
    LeftElbow = 18
    RightElbow = 25

Kp_DEFAULT_29 = [
    60,60,60,100,40,40, 60,60,60,100,40,40, 60,40,40,
    40,40,40,40,40,40,40, 40,40,40,40,40,40,40
]
Kd_DEFAULT_29 = [1,1,1,2,1,1, 1,1,1,2,1,1, 1,1,1, 1,1,1,1,1,1,1, 1,1,1,1,1,1,1]

def get_gravity_orientation(quat: np.ndarray) -> np.ndarray:
    qw,qx,qy,qz = quat
    g = np.zeros(3, dtype=np.float32)
    g[0] = 2 * (-qz*qx + qw*qy)
    g[1] = -2 * (qz*qy + qw*qx)
    g[2] = 1 - 2 * (qw*qw + qz*qz)
    return g

def load_policy(path: str, device):
    try:
        m = torch.jit.load(path, map_location=device); m.eval(); return m
    except Exception:
        pass
    obj = torch.load(path, map_location=device)
    if hasattr(obj, "eval"): obj.eval(); return obj
    if isinstance(obj, dict):
        for k in ("policy","model","actor"):
            if k in obj and hasattr(obj[k], "eval"):
                obj[k].eval(); return obj[k]
    raise RuntimeError("Unsupported policy file")

def pad(v, N, fill=0.0):
    v = list(v); 
    if len(v) < N: v += [fill]*(N-len(v))
    return v[:N]

def make_lowcmd(q_targets_29, kp_29, kd_29, tau=0.0):
    msg = LowCmd_default()
    N = len(msg.motor_cmd)
    q = pad(q_targets_29, N, 0.0)
    if isinstance(kp_29, (list, tuple, np.ndarray)): kp = pad(kp_29, N, 0.0)
    else: kp = [float(kp_29)]*N
    if isinstance(kd_29, (list, tuple, np.ndarray)): kd = pad(kd_29, N, 0.0)
    else: kd = [float(kd_29)]*N
    for i in range(N):
        m = msg.motor_cmd[i]
        m.mode = 1; m.q=float(q[i]); m.dq=0.0; m.kp=float(kp[i]); m.kd=float(kd[i]); m.tau=float(tau)
    return msg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--iface", default="lo")
    ap.add_argument("--domain", type=int, default=1)
    ap.add_argument("--rate", type=float, default=400.0)
    ap.add_argument("--service", default="sport")
    ap.add_argument("--also_service", action="append", default=[])
    ap.add_argument("--start_ids", default="500,801")
    ap.add_argument("--stop_ids",  default="0,1,4")
    ap.add_argument("--zero_stream", action="store_true")
    ap.add_argument("--send_zero_on_disable", action="store_true")
    ap.add_argument("--damp_kp", type=float, default=12.0)
    ap.add_argument("--damp_kd", type=float, default=6.0)
    ap.add_argument("--damp_warmup", type=float, default=0.3)
    ap.add_argument("--lock_blend_s", type=float, default=2.0)
    args = ap.parse_args()

    start_ids = {int(s) for s in str(args.start_ids).split(",") if s.strip()}
    stop_ids  = {int(s) for s in str(args.stop_ids).split(",")  if s.strip()}

    cfg = yaml.safe_load(open(args.config,"r"))
    policy_path        = cfg["policy_path"]
    kps_legs           = np.array(cfg["kps"], dtype=np.float32)
    kds_legs           = np.array(cfg["kds"], dtype=np.float32)
    q0_legs            = np.array(cfg["default_angles"], dtype=np.float32)
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

    # 29-dof default gains (copy legs tuning into first 12)
    kp29 = Kp_DEFAULT_29[:]; kd29 = Kd_DEFAULT_29[:]
    for i in range(min(12,len(kp29))):
        kp29[i] = float(kps_legs[i] if kps_legs.ndim>0 else kps_legs)
        kd29[i] = float(kds_legs[i] if kds_legs.ndim>0 else kds_legs)

    # LockedStanding target
    q_lock = [0.0]*CONTROLLED_DOF
    q_lock[G1J.LeftElbow] = -math.pi/2.0
    q_lock[G1J.RightElbow]= -math.pi/2.0

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    policy = load_policy(policy_path, device)

    ChannelFactoryInitialize(args.domain, args.iface)
    pub_lowcmd = ChannelPublisher("rt/lowcmd", LowCmd); pub_lowcmd.Init()

    # Sensors
    state = {"q29": None, "dq12": None, "quat": None, "omega": None}
    lock = threading.Lock()

    def on_lowstate(msg: LowState_):
        motors = getattr(msg, "motor_state", None) or getattr(msg, "motorState", None)
        if motors is None: return
        q29 = [float(getattr(motors[i], "q", 0.0)) for i in range(min(CONTROLLED_DOF, len(motors)))]
        dq12= [float(getattr(motors[i], "dq", 0.0)) for i in range(min(12, len(motors)))]
        with lock:
            state["q29"] = np.asarray(pad(q29, CONTROLLED_DOF), dtype=np.float32)
            state["dq12"]= np.asarray(pad(dq12, 12), dtype=np.float32)

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
            print(f"[AI] IMU state subscribed: {t}"); break
        except Exception:
            continue

    # Mode machine
    MODE_NONE=0; MODE_AI=1; MODE_ZERO=2; MODE_DAMP=3; MODE_LOCK=4
    mode_lock = threading.Lock(); mode = {"m": MODE_NONE}
    last_change = {"t": 0.0}
    damp_end = {"t": 0.0}; damp_q = {"q": None}
    lock_t0 = {"t": 0.0}; lock_t1 = {"t": 0.0}; lock_q0 = {"q": None}

    # RPC responder per service
    responders = {}  # svc -> (sub, pub)
    def make_response(req: Request, return_code=0, message="OK", parameter="{}"):
        rsp = Response()
        hdr = ResponseHeader()
        ident = RequestIdentity()
        try:
            ident.api_id = int(req.header.identity.api_id)
            ident.id     = int(req.header.identity.id)
        except Exception:
            pass
        hdr.identity = ident
        st = ResponseStatus()
        st.return_code = int(return_code)
        st.message = str(message)
        rsp.header = hdr
        rsp.status = st
        rsp.parameter = parameter
        return rsp

    def set_mode(new_mode: int, note: str):
        with mode_lock:
            if mode["m"] != new_mode:
                mode["m"] = new_mode
                last_change["t"] = time.time()
                print(f"[MODE] {note}")

    def on_request_factory(service_name: str, pub_rsp: ChannelPublisher):
        def on_request(req: Request):
            # Parse request
            try:
                api_id = int(req.header.identity.api_id)
            except Exception:
                api_id = -1
            raw = getattr(req, "parameter", "{}") or "{}"
            try:
                data = json.loads(raw) if isinstance(raw, str) else {}
            except Exception:
                data = {}
            rid = int(getattr(getattr(req, "header", object()), "identity", object()).id or 0)
            print(f"[REQ/{service_name}] id={rid} api_id={api_id} param={data}")

            # Default response
            rc, msg = 0, "OK"

            if api_id == ROBOT_API_ID_LOCO_SET_FSM_ID:
                fsm = int(data.get("data", -1))
                if fsm in {500,801}:     # AI
                    set_mode(MODE_AI, f"AI ENABLED (fsm={fsm})")
                elif fsm == 0:           # Zero
                    set_mode(MODE_ZERO, "ZeroTorque")
                elif fsm == 1:           # Damp
                    with lock:
                        q29 = state["q29"].copy() if state["q29"] is not None else np.zeros(CONTROLLED_DOF, np.float32)
                    damp_q["q"] = q29[:]
                    damp_end["t"] = time.time() + float(args.damp_warmup)
                    set_mode(MODE_DAMP, f"DampHold kp={args.damp_kp} kd={args.damp_kd}")
                elif fsm == 4:           # Lock
                    with lock:
                        q29 = state["q29"].copy() if state["q29"] is not None else np.zeros(CONTROLLED_DOF, np.float32)
                    lock_q0["q"] = q29[:]
                    lock_t0["t"] = time.time()
                    lock_t1["t"] = lock_t0["t"] + float(max(0.05, args.lock_blend_s))
                    set_mode(MODE_LOCK, f"LockedStanding blend {args.lock_blend_s:.2f}s")
                else:
                    rc, msg = 3104, f"Unsupported FSM id {fsm}"
            else:
                rc, msg = 3102, f"Unsupported api_id {api_id}"

            # Send response immediately
            try:
                rsp = make_response(req, rc, msg)
                pub_rsp.Write(rsp)
                print(f"[RSP/{service_name}] id={rid} rc={rc} msg='{msg}'")
            except Exception:
                traceback.print_exc(limit=6)
        return on_request

    # Build responders
    services = [args.service] + [s for s in args.also_service if s]
    for default in ("sport","unitree_loco_api"):
        if default not in services: services.append(default)
    for svc in services:
        req_topic = GetServerChannelName(svc, ChannelType.RECV)
        rsp_topic = GetServerChannelName(svc, ChannelType.SEND)
        try:
            sub = ChannelSubscriber(req_topic, Request)
            pub = ChannelPublisher(rsp_topic, Response); pub.Init()
            sub.Init(on_request_factory(svc, pub), 64)
            responders[svc] = (sub, pub)
            print(f"[RPC] Listening: {req_topic}  → Responding on: {rsp_topic}")
        except Exception as e:
            print(f"[RPC][WARN] Failed to init for service '{svc}': {e}")

    # AI loop context
    obs = np.zeros(num_obs, dtype=np.float32)
    action = np.zeros(num_actions, dtype=np.float32)
    target_q = q0_legs.copy()
    cmd = cmd_init.astype(np.float32)

    inner_dt = 1.0/float(args.rate)
    ctr = 0
    period = 0.8
    WARM_S = 0.7

    def publish(msg):
        try:
            msg.crc = CRC_CALC.Crc(msg)
        except Exception:
            pass
        pub_lowcmd.Write(msg)

    def publish_zero():
        msg = LowCmd_default()
        for i in range(MOTOR_SIZE):
            m = msg.motor_cmd[i]
            m.mode=1; m.q=0.0; m.dq=0.0; m.kp=0.0; m.kd=0.0; m.tau=0.0
        publish(msg)

    def publish_pd(q_targets_29, kp_vec_29, kd_vec_29):
        publish(make_lowcmd(q_targets_29, kp_vec_29, kd_vec_29, 0.0))

    print("[INFO] Unified controller + responder ready.")
    last_mode = MODE_NONE
    try:
        while True:
            t0 = time.time()
            with mode_lock:
                m = mode["m"]

            if m == MODE_NONE:
                pass

            elif m == MODE_ZERO:
                if args.zero_stream:
                    publish_zero()
                else:
                    if last_mode != MODE_ZERO:
                        publish_zero()

            elif m == MODE_DAMP:
                with lock:
                    q29 = state["q29"].copy() if state["q29"] is not None else np.zeros(CONTROLLED_DOF, np.float32)
                qt = damp_q["q"] if damp_q["q"] is not None else q29[:]
                now = time.time()
                if now < damp_end["t"]:
                    a = 1.0 - ((damp_end["t"] - now) / max(1e-3, args.damp_warmup))
                    kp = [a*args.damp_kp]*CONTROLLED_DOF
                    kd = [a*args.damp_kd]*CONTROLLED_DOF
                else:
                    kp = [args.damp_kp]*CONTROLLED_DOF
                    kd = [args.damp_kd]*CONTROLLED_DOF
                publish_pd(qt, kp, kd)

            elif m == MODE_LOCK:
                with lock:
                    q29 = state["q29"].copy() if state["q29"] is not None else np.zeros(CONTROLLED_DOF, np.float32)
                q0 = lock_q0["q"] if lock_q0["q"] is not None else q29[:]
                t0b = lock_t0["t"]; t1b = lock_t1["t"]; now = time.time()
                if now >= t1b:
                    q = q_lock[:]; kp = Kp_DEFAULT_29[:]; kd = Kd_DEFAULT_29[:]
                else:
                    a = (now - t0b)/max(1e-3, (t1b - t0b)); a = a*a*(3-2*a)
                    q = [(1-a)*q0[i] + a*q_lock[i] for i in range(CONTROLLED_DOF)]
                    kp = [(1-a)*20.0 + a*Kp_DEFAULT_29[i] for i in range(CONTROLLED_DOF)]
                    kd = [(1-a)* 2.0 + a*Kd_DEFAULT_29[i] for i in range(CONTROLLED_DOF)]
                publish_pd(q, kp, kd)

            elif m == MODE_AI:
                with lock:
                    q29 = state["q29"]; dq12 = state["dq12"]; quat = state["quat"]; omega = state["omega"]
                if q29 is not None and dq12 is not None and quat is not None and omega is not None:
                    if (time.time() - last_change["t"]) < WARM_S and last_mode != MODE_AI:
                        # on entry: warm PD hold on legs
                        q_targets = [0.0]*CONTROLLED_DOF
                        for i in range(12): q_targets[i] = float(q0_legs[i])
                        kp = Kp_DEFAULT_29[:]; kd = Kd_DEFAULT_29[:]
                        for i in range(12):
                            kp[i] = float(kps_legs[i] if kps_legs.ndim>0 else kps_legs)
                            kd[i] = float(kds_legs[i] if kds_legs.ndim>0 else kds_legs)
                        publish_pd(q_targets, kp, kd)
                    else:
                        if ctr % control_decimation == 0:
                            gravity = get_gravity_orientation(quat)
                            omega_s = omega * ang_vel_scale
                            qj  = (q29[:12] - q0_legs) * dof_pos_scale
                            dqj = (dq12) * dof_vel_scale
                            t   = ctr * simulation_dt
                            phase = (t % period)/period
                            sinp, cosp = math.sin(2*math.pi*phase), math.cos(2*math.pi*phase)

                            obs = np.zeros(num_obs, dtype=np.float32)
                            obs[0:3] = omega_s; obs[3:6] = gravity
                            obs[6:9] = cmd_init * cmd_scale
                            obs[9:21] = qj; obs[21:33] = dqj
                            obs[33:45] = 0.0  # previous action not strictly used
                            obs[45:47] = np.array([sinp, cosp], dtype=np.float32)

                            with torch.no_grad():
                                out = policy(torch.from_numpy(obs).to(device).unsqueeze(0))
                                if isinstance(out,(tuple,list)): out = out[0]
                                action = out.detach().cpu().numpy().squeeze().astype(np.float32)
                            target_q[:12] = action * action_scale + q0_legs

                        q_targets = [0.0]*CONTROLLED_DOF
                        for i in range(12): q_targets[i] = float(target_q[i])
                        kp = Kp_DEFAULT_29[:]; kd = Kd_DEFAULT_29[:]
                        for i in range(12):
                            kp[i] = float(kps_legs[i] if kps_legs.ndim>0 else kps_legs)
                            kd[i] = float(kds_legs[i] if kds_legs.ndim>0 else kds_legs)
                        publish_pd(q_targets, kp, kd)

            last_mode = m
            ctr += 1
            dt = inner_dt - (time.time() - t0)
            if dt > 0: time.sleep(dt)
    except KeyboardInterrupt:
        print("\\n[INFO] Stopped.")
    except Exception:
        traceback.print_exc(limit=12)

if __name__ == "__main__":
    main()
