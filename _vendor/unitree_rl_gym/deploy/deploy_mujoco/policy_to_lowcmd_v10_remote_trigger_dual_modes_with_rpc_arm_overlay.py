#!/usr/bin/env python3
"""
policy_to_lowcmd_v10_remote_trigger_dual_modes_with_rpc_arm_overlay.py

This is v9 + **arm SDK overlay**:

- Subscribes to rt/arm_sdk (LowCmd_). Uses motor_cmd[29].q as enable ("weight") > 0.5.
- **In AI walking (FSM 500/801):** publish the exact v7 AI legs; then **overwrite only waist+arms**
  joints with the values from arm_sdk. Legs remain untouched — preserves walk quality.
- **When no mode active (idle/MODE_NONE):** if arm_sdk is enabled, publish a frame that tracks
  current leg pose (low gains) and applies the arm/waist commands — so arm motions work even
  without walking, while legs stay as they are.
- Other modes (Zero/Damp/Lock) are left unchanged to avoid unexpected conflicts.

All other features from v9 are preserved: fast RPC responses, damp hold, locked standing,
quiet when idle otherwise, CRC, etc.
"""
import argparse, time, threading, math, json, numpy as np, torch, yaml, traceback

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelPublisher, ChannelSubscriber
from unitree_sdk2py.core.channel_name import GetServerChannelName, ChannelType
from unitree_sdk2py.utils.crc import CRC

from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_ as LowCmd, LowState_
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_ as LowCmd_default

from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_

# RPC IDL
from unitree_sdk2py.idl.unitree_api.msg.dds_ import Request_         as Request
from unitree_sdk2py.idl.unitree_api.msg.dds_ import Response_        as Response
from unitree_sdk2py.idl.unitree_api.msg.dds_ import ResponseHeader_  as ResponseHeader
from unitree_sdk2py.idl.unitree_api.msg.dds_ import ResponseStatus_  as ResponseStatus
from unitree_sdk2py.idl.unitree_api.msg.dds_ import RequestIdentity_ as RequestIdentity

CRC_CALC = CRC()
MOTOR_SIZE = 35
CONTROLLED_DOF = 29   # 0..28 used here (waist+arms cover a subset)

try:
    from unitree_sdk2py.g1.loco.g1_loco_api import ROBOT_API_ID_LOCO_SET_FSM_ID
except Exception:
    ROBOT_API_ID_LOCO_SET_FSM_ID = 3502

# ---- Joints of interest for overlay ----
kWaistYaw, kWaistRoll, kWaistPitch = 12, 13, 14
kLShoulderPitch, kLShoulderRoll, kLShoulderYaw = 15, 16, 17
kLElbowPitch, kLElbowRoll = 18, 19
kRShoulderPitch, kRShoulderRoll, kRShoulderYaw = 22, 23, 24
kRElbowPitch, kRElbowRoll = 25, 26

CONTROLLED = [
    kWaistYaw, kWaistRoll, kWaistPitch,
    kLShoulderPitch, kLShoulderRoll, kLShoulderYaw,
    kLElbowPitch, kLElbowRoll,
    kRShoulderPitch, kRShoulderRoll, kRShoulderYaw,
    kRElbowPitch, kRElbowRoll,
]
ENABLE_INDEX = 29  # convention used by your arm_sdk

# Default gains for non-AI full-body PD (same as v9)
Kp_DEFAULT_29 = [
    60, 60, 60, 100, 40, 40,
    60, 60, 60, 100, 40, 40,
    60, 40, 40,
    40, 40, 40, 40, 40, 40, 40,
    40, 40, 40, 40, 40, 40, 40
]
Kd_DEFAULT_29 = [
    1, 1, 1, 2, 1, 1,
    1, 1, 1, 2, 1, 1,
    1, 1, 1,
    1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1
]

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

def pad(vec, N, fill=0.0):
    v = list(vec)
    if len(v) < N: v += [fill]*(N-len(v))
    return v[:N]

def make_lowcmd_from_targets(q_targets_29, kp_29, kd_29, tau_scalar=0.0):
    msg = LowCmd_default()
    N = len(msg.motor_cmd)
    q_targets = pad(q_targets_29, N, 0.0)
    if isinstance(kp_29, (list, tuple, np.ndarray)):
        kp_vec = pad(kp_29, N, 0.0)
    else:
        kp_vec = [float(kp_29)]*N
    if isinstance(kd_29, (list, tuple, np.ndarray)):
        kd_vec = pad(kd_29, N, 0.0)
    else:
        kd_vec = [float(kd_29)]*N
    for i in range(N):
        m = msg.motor_cmd[i]
        m.mode = 1
        m.q    = float(q_targets[i])
        m.dq   = 0.0
        m.kp   = float(kp_vec[i])
        m.kd   = float(kd_vec[i])
        m.tau  = float(tau_scalar)
    return msg

def overlay_arms_on_msg(msg: LowCmd_default, desired: dict):
    """In-place: overwrite only CONTROLLED joints from desired {idx: {q,dq,kp,kd,tau}}."""
    arr = msg.motor_cmd
    N = len(arr)
    for j, d in desired.items():
        if j < 0 or j >= N: 
            continue
        if j not in CONTROLLED:
            continue
        m = arr[j]
        # keep mode=1
        m.q   = float(d.get("q",  m.q))
        m.dq  = float(d.get("dq", m.dq))
        m.kp  = float(d.get("kp", m.kp))
        m.kd  = float(d.get("kd", m.kd))
        m.tau = float(d.get("tau",m.tau))

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
    ap.add_argument("--zero_stream", action="store_true",
                    help="when FSM=0 ZeroTorque, continuously stream zero-torque cmds")
    ap.add_argument("--send_zero_on_disable", action="store_true",
                    help="on disabling edge from AI, send one zero-torque LowCmd once")
    # Damp params
    ap.add_argument("--damp_kp", type=float, default=12.0)
    ap.add_argument("--damp_kd", type=float, default=6.0)
    ap.add_argument("--damp_warmup", type=float, default=0.3)
    # LockedStanding blend duration
    ap.add_argument("--lock_blend_s", type=float, default=2.0)
    args = ap.parse_args()

    start_ids = {int(s) for s in str(args.start_ids).split(",") if s.strip()}
    stop_ids  = {int(s) for s in str(args.stop_ids).split(",")  if s.strip()}

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    policy_path        = cfg["policy_path"]
    kps_legs           = np.array(cfg["kps"], dtype=np.float32)
    kds_legs           = np.array(cfg["kds"], dtype=np.float32)
    q0_legs            = np.array(cfg["default_angles"], dtype=np.float32)  # first 12
    ang_vel_scale      = float(cfg["ang_vel_scale"])
    dof_pos_scale      = float(cfg["dof_pos_scale"])
    dof_vel_scale      = float(cfg["dof_vel_scale"])
    action_scale       = float(cfg["action_scale"])
    cmd_scale          = np.array(cfg["cmd_scale"], dtype=np.float32)
    num_actions        = int(cfg["num_actions"])  # 12 legs
    num_obs            = int(cfg["num_obs"])
    cmd_init           = np.array(cfg["cmd_init"], dtype=np.float32)
    control_decimation = int(cfg["control_decimation"])
    simulation_dt      = float(cfg["simulation_dt"])

    # Build 29-dof vectors for non-AI modes (legs+rest). Copy legs gains into first 12.
    kp29 = Kp_DEFAULT_29[:]
    kd29 = Kd_DEFAULT_29[:]
    for i in range(min(12, len(kp29))):
        kp29[i] = float(kps_legs[i] if kps_legs.ndim > 0 else kps_legs)
        kd29[i] = float(kds_legs[i] if kds_legs.ndim > 0 else kds_legs)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    policy = load_policy(policy_path, device)

    ChannelFactoryInitialize(args.domain, args.iface)
    pub = ChannelPublisher("rt/lowcmd", LowCmd); pub.Init()

    # ------------- State from DDS -------------
    state = {"q29": None, "dq12": None, "quat": None, "omega": None}
    lock = threading.Lock()

    def on_lowstate(msg: LowState_):
        try:
            motors = getattr(msg, "motor_state", None) or getattr(msg, "motorState", None)
            if motors is None: return
            q_list = [float(getattr(motors[i], "q", 0.0)) for i in range(min(CONTROLLED_DOF, len(motors)))]
            dq_list= [float(getattr(motors[i], "dq", 0.0)) for i in range(min(12, len(motors)))]
            with lock:
                state["q29"] = np.asarray(pad(q_list, CONTROLLED_DOF, 0.0), dtype=np.float32)
                state["dq12"]= np.asarray(pad(dq_list, 12, 0.0), dtype=np.float32)
        except Exception:
            traceback.print_exc(limit=4)

    def on_sportstate(msg: SportModeState_):
        try:
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
        except Exception:
            traceback.print_exc(limit=4)

    ChannelSubscriber("rt/lowstate", LowState_).Init(on_lowstate, 50)
    for t in ("rt/sportmodestate", "sportmodestate", "lf/sportmodestate"):
        try:
            ChannelSubscriber(t, SportModeState_).Init(on_sportstate, 50)
            print(f"[AI] Subscribed IMU state: {t}"); break
        except Exception:
            continue

    # ------------- arm_sdk subscription -------------
    arm = {"enabled": False, "desired": {}, "num_motors": MOTOR_SIZE}
    arm_lock = threading.Lock()

    def _get_motor_cmd_array(msg):
        try:
            return msg.motor_cmd
        except Exception:
            # fallback to accessor style
            return [ msg.motor_cmd().at(i) for i in range(MOTOR_SIZE) ]

    def on_arm_sdk(msg: LowCmd):
        arr = _get_motor_cmd_array(msg)
        try:
            en = float(arr[ENABLE_INDEX].q)
            enabled = en > 0.5
        except Exception:
            enabled = True
        latest = {}
        N = min(len(arr), MOTOR_SIZE)
        for j in CONTROLLED:
            if j < 0 or j >= N:
                continue
            mc = arr[j]
            latest[j] = {
                "q":  float(getattr(mc, "q",  0.0)),
                "dq": float(getattr(mc, "dq", 0.0)),
                "kp": float(getattr(mc, "kp", 40.0)),
                "kd": float(getattr(mc, "kd", 1.0)),
                "tau":float(getattr(mc, "tau",0.0)),
            }
        with arm_lock:
            arm["enabled"] = enabled
            arm["desired"] = latest
            arm["num_motors"] = N

    ChannelSubscriber("rt/arm_sdk", LowCmd).Init(on_arm_sdk, 50)

    # -------------------- RPC RESPONDERS (FAST) --------------------
    def build_response(req: Request, code: int, text: str) -> Response:
        try:
            rid = int(req.header.identity.id); apiid = int(req.header.identity.api_id)
        except Exception:
            rid, apiid = -1, -1
        try:
            ident = RequestIdentity(rid, apiid)
        except Exception:
            ident = RequestIdentity()
            try: ident.id = rid
            except Exception: pass
            try: ident.api_id = apiid
            except Exception: pass

        try:
            stat = ResponseStatus(int(code))
        except Exception:
            stat = ResponseStatus(int(code))
        try: setattr(stat, "message", str(text))
        except Exception: pass

        try:
            hdr = ResponseHeader(ident, stat)
        except Exception:
            hdr = ResponseHeader()
            try: hdr.identity = ident
            except Exception: pass
            try: hdr.status = stat
            except Exception: pass

        try:
            rsp = Response(hdr, str(text), bytes())
        except Exception:
            rsp = Response()
            try: rsp.header = hdr
            except Exception: pass
            try: rsp.data = str(text)
            except Exception: pass
            try: rsp.binary = bytes()
            except Exception: pass

        try:
            rsp.serialize()
        except Exception:
            pass
        return rsp

    MODE_NONE=0; MODE_AI=1; MODE_ZERO=2; MODE_DAMP=3; MODE_LOCK=4
    mode_lock = threading.Lock()
    mode = {"m": MODE_NONE}
    last_enable_change = {"t": 0.0}

    damp_end_t = {"t": 0.0}
    damp_target_q = {"q": None}

    lock_t0 = {"t": 0.0}; lock_t1 = {"t": 0.0}
    lock_q0 = {"q": None}
    q_lock = [0.0]*CONTROLLED_DOF
    q_lock[kLElbowPitch]  = -math.pi/2.0
    q_lock[kRElbowPitch]  = -math.pi/2.0

    def set_mode(new_mode: int, msg: str):
        with mode_lock:
            if mode["m"] != new_mode:
                mode["m"] = new_mode
                last_enable_change["t"] = time.time()
                print(f"[MODE] {msg}")

    def on_request_factory(service_name: str, pub_rsp: ChannelPublisher):
        def on_request(req: Request):
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
            rc, msg = 0, "OK"
            if api_id == ROBOT_API_ID_LOCO_SET_FSM_ID:
                fsm = int(data.get("data", -1))
                if fsm in {500,801}:     set_mode(MODE_AI, f"AI ENABLED (fsm={fsm})")
                elif fsm == 0:           set_mode(MODE_ZERO, "ZeroTorque")
                elif fsm == 1:
                    with lock:
                        q29 = state["q29"].copy() if state["q29"] is not None else np.zeros(CONTROLLED_DOF, dtype=np.float32)
                    damp_target_q["q"] = q29[:]; damp_end_t["t"] = time.time() + float(args.damp_warmup)
                    set_mode(MODE_DAMP, f"DampHold kp={args.damp_kp} kd={args.damp_kd}")
                elif fsm == 4:
                    with lock:
                        q29 = state["q29"].copy() if state["q29"] is not None else np.zeros(CONTROLLED_DOF, dtype=np.float32)
                    lock_q0["q"] = q29[:]; lock_t0["t"] = time.time(); lock_t1["t"] = lock_t0["t"] + float(max(0.05, args.lock_blend_s))
                    set_mode(MODE_LOCK, f"LockedStanding blend {args.lock_blend_s:.2f}s")
                else:
                    rc, msg = 3104, f"Unsupported FSM id {fsm}"
            else:
                rc, msg = 3102, f"Unsupported api_id {api_id}"
            try:
                rsp = build_response(req, rc, msg)
                pub_rsp.Write(rsp)
                print(f"[RSP/{service_name}] id={rid} rc={rc} msg='{msg}'")
            except Exception:
                traceback.print_exc(limit=8)
        return on_request

    services = [args.service] + [s for s in args.also_service if s]
    for default in ("sport","unitree_loco_api"):
        if default not in services: services.append(default)
    for svc in services:
        req_topic = GetServerChannelName(svc, ChannelType.RECV)
        rsp_topic = GetServerChannelName(svc, ChannelType.SEND)
        try:
            sub = ChannelSubscriber(req_topic, Request)
            pub_rsp = ChannelPublisher(rsp_topic, Response); pub_rsp.Init()
            sub.Init(on_request_factory(svc, pub_rsp), 64)
            print(f"[RPC] Listening: {req_topic}  → Responding on: {rsp_topic}")
        except Exception as e:
            print(f"[RPC][WARN] Failed to init for service '{svc}': {e}")

    # -------------------- AI LOOP (EXACT from v7) --------------------
    obs      = np.zeros(num_obs, dtype=np.float32)
    action   = np.zeros(num_actions, dtype=np.float32)
    target_q = q0_legs.copy()
    cmd      = cmd_init.astype(np.float32)

    inner_dt = 1.0 / float(args.rate)
    ctr = 0
    WARM_S = 0.7

    def publish(msg):
        try:
            msg.crc = CRC_CALC.Crc(msg)
        except Exception:
            pass
        pub.Write(msg)

    def publish_zero():
        msg = LowCmd_default()
        for i in range(MOTOR_SIZE):
            m = msg.motor_cmd[i]
            m.mode = 1; m.q=0.0; m.dq=0.0; m.kp=0.0; m.kd=0.0; m.tau=0.0
        publish(msg)

    def publish_pd(q_targets_29, kp_vec_29, kd_vec_29, overlay_arms=False):
        msg = make_lowcmd_from_targets(q_targets_29, kp_vec_29, kd_vec_29, 0.0)
        if overlay_arms:
            with arm_lock:
                if arm["enabled"] and arm["desired"]:
                    overlay_arms_on_msg(msg, arm["desired"])
        publish(msg)

    print("[INFO] Unified controller + RPC responder + arm overlay ready.")
    last_mode = MODE_NONE
    try:
        while True:
            t0 = time.time()
            with mode_lock:
                m = mode["m"]

            if m == MODE_NONE:
                # Quiet idle, unless arm SDK is enabled: then publish legs=measured pose hold + overlay arms
                with arm_lock:
                    arm_enabled = arm["enabled"]; desired = dict(arm["desired"])
                if arm_enabled and desired:
                    with lock:
                        q29 = state["q29"]
                    if q29 is not None:
                        q_targets = list(q29)  # track as-is
                        kp = [20.0]*CONTROLLED_DOF
                        kd = [1.0]*CONTROLLED_DOF
                        msg = make_lowcmd_from_targets(q_targets, kp, kd, 0.0)
                        overlay_arms_on_msg(msg, desired)
                        publish(msg)
                # else: be quiet

            elif m == MODE_ZERO:
                if last_mode != MODE_ZERO:
                    publish_zero()
                # remain quiet unless zero_stream requested
                # (explicitly avoiding overlay here to keep true zero torque intent)

            elif m == MODE_DAMP:
                with lock:
                    q29 = state["q29"].copy() if state["q29"] is not None else np.zeros(CONTROLLED_DOF, dtype=np.float32)
                qt = damp_target_q["q"] if damp_target_q["q"] is not None else q29[:]
                now = time.time()
                if now < damp_end_t["t"]:
                    alpha = 1.0 - ((damp_end_t["t"] - now) / max(1e-3, args.damp_warmup))
                    kp = [alpha*args.damp_kp]*CONTROLLED_DOF
                    kd = [alpha*args.damp_kd]*CONTROLLED_DOF
                else:
                    kp = [args.damp_kp]*CONTROLLED_DOF
                    kd = [args.damp_kd]*CONTROLLED_DOF
                publish_pd(qt, kp, kd, overlay_arms=False)

            elif m == MODE_LOCK:
                with lock:
                    q29 = state["q29"].copy() if state["q29"] is not None else np.zeros(CONTROLLED_DOF, dtype=np.float32)
                q0 = lock_q0["q"] if lock_q0["q"] is not None else q29[:]
                t0b = lock_t0["t"]; t1b = lock_t1["t"]; now = time.time()
                if now >= t1b:
                    q = q_lock[:]
                    kp = Kp_DEFAULT_29[:]
                    kd = Kd_DEFAULT_29[:]
                else:
                    a = (now - t0b) / max(1e-3, (t1b - t0b))
                    a = a*a*(3.0 - 2.0*a)  # smoothstep
                    q = [(1.0 - a)*q0[i] + a*q_lock[i] for i in range(CONTROLLED_DOF)]
                    kp = [ (1.0 - a)*20.0 + a*Kp_DEFAULT_29[i] for i in range(CONTROLLED_DOF) ]
                    kd = [ (1.0 - a)* 2.0 + a*Kd_DEFAULT_29[i] for i in range(CONTROLLED_DOF) ]
                publish_pd(q, kp, kd, overlay_arms=False)

            elif m == MODE_AI:
                with lock:
                    q29 = state["q29"]
                    dq12= state["dq12"]
                    quat= state["quat"]
                    omega=state["omega"]
                if q29 is not None and dq12 is not None and quat is not None and omega is not None:
                    if (time.time() - last_enable_change["t"]) < 0.7 and last_mode != MODE_AI:
                        q_targets = [0.0]*CONTROLLED_DOF
                        for i in range(12):
                            q_targets[i] = float(q0_legs[i])
                        kp = Kp_DEFAULT_29[:]; kd = Kd_DEFAULT_29[:]
                        for i in range(12):
                            kp[i] = float(kps_legs[i] if kps_legs.ndim > 0 else kps_legs)
                            kd[i] = float(kds_legs[i] if kds_legs.ndim > 0 else kds_legs)
                        # Warmup publish with arm overlay
                        msg = make_lowcmd_from_targets(q_targets, kp, kd, 0.0)
                        with arm_lock:
                            if arm["enabled"] and arm["desired"]:
                                overlay_arms_on_msg(msg, arm["desired"])
                        publish(msg)
                    else:
                        if ctr % control_decimation == 0:
                            gravity = get_gravity_orientation(quat)
                            omega_s = omega * ang_vel_scale
                            qj  = (q29[:12]  - q0_legs) * dof_pos_scale
                            dqj = (dq12)             * dof_vel_scale
                            t   = ctr * simulation_dt
                            phase = (t % 0.8) / 0.8
                            sinp, cosp = math.sin(2.0*math.pi*phase), math.cos(2.0*math.pi*phase)

                            obs = np.zeros(num_obs, dtype=np.float32)
                            obs[0:3] = omega_s
                            obs[3:6] = gravity
                            obs[6:9] = cmd * cmd_scale
                            obs[9:21] = qj
                            obs[21:33] = dqj
                            obs[33:45] = action
                            obs[45:47] = np.array([sinp, cosp], dtype=np.float32)

                            with torch.no_grad():
                                out = policy(torch.from_numpy(obs).to(device).unsqueeze(0))
                                if isinstance(out, (tuple, list)): out = out[0]
                                action_local = out.detach().cpu().numpy().squeeze().astype(np.float32)
                            target_q[:12] = action_local * action_scale + q0_legs

                        q_targets = [0.0]*CONTROLLED_DOF
                        for i in range(12):
                            q_targets[i] = float(target_q[i])
                        kp = Kp_DEFAULT_29[:]; kd = Kd_DEFAULT_29[:]
                        for i in range(12):
                            kp[i] = float(kps_legs[i] if kps_legs.ndim > 0 else kps_legs)
                            kd[i] = float(kds_legs[i] if kds_legs.ndim > 0 else kds_legs)
                        # Publish with arm overlay
                        msg = make_lowcmd_from_targets(q_targets, kp, kd, 0.0)
                        with arm_lock:
                            if arm["enabled"] and arm["desired"]:
                                overlay_arms_on_msg(msg, arm["desired"])
                        publish(msg)

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
