#!/usr/bin/env python3
import time
import traceback
import mujoco
import mujoco.viewer
from threading import Thread
import threading
import argparse
import os

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
#from unitree_sdk2py_bridge import UnitreeSdk2Bridge, ElasticBand
#from unitree_sdk2py_bridge_v4 import UnitreeSdk2Bridge, ElasticBand
from unitree_sdk2py_bridge_v4_wireless import UnitreeSdk2Bridge, ElasticBand

import config

# ---------------- Diagnostics / toggles ----------------
# You can also set these in config.py; these are fallbacks.
BYPASS_BRIDGE     = getattr(config, "BYPASS_BRIDGE", False)   # <-- start True to prove stepping works
USE_JOYSTICK      = getattr(config, "USE_JOYSTICK", False)    # make non-blocking; default False here
PRINT_INFO        = getattr(config, "DIAG_PRINT_INFO", True)
PRINT_HEARTBEAT   = getattr(config, "DIAG_PRINT_HEART", True)
FORCE_TEST_2S     = getattr(config, "DIAG_FORCE_TEST", True)  # 2s torque on actuator 0 to prove motion
PD_TEST           = getattr(config, "DIAG_PD_TEST", False)    # simple PD on actuator 0
PD_Q_TARGET       = getattr(config, "PD_Q_TARGET", 0.5)
PD_KP             = getattr(config, "PD_KP", 200.0)
PD_KD             = getattr(config, "PD_KD", 5.0)

locker = threading.Lock()

# --- NEW: tiny helper to resolve --scene argument ---
def resolve_scene_path(cli_scene: str | None) -> str:
    """
    If cli_scene is:
      - None: return config.ROBOT_SCENE
      - absolute/relative path: return as-is
      - bare filename: resolve relative to dirname(config.ROBOT_SCENE)
    """
    if not cli_scene:
        return config.ROBOT_SCENE

    if os.path.isabs(cli_scene) or os.path.sep in cli_scene:
        return cli_scene

    base_dir = os.path.dirname(os.path.abspath(config.ROBOT_SCENE))
    return os.path.join(base_dir, cli_scene)

# --- Parse optional --scene ---
parser = argparse.ArgumentParser(description="Unitree MuJoCo simulator")
parser.add_argument("--scene", help="scene.xml to load (filename in same folder as config.ROBOT_SCENE, or a path)")
args, unknown = parser.parse_known_args()  # don't break if other tooling passes extras

ROBOT_SCENE = resolve_scene_path(args.scene)

print("[BOOT] Loading model:", ROBOT_SCENE)
mj_model = mujoco.MjModel.from_xml_path(ROBOT_SCENE)
mj_data  = mujoco.MjData(mj_model)

# Initial forward (required after any direct qpos edits; safe on startup)
mujoco.mj_forward(mj_model, mj_data)

if PRINT_INFO:
    print(f"[INFO] timestep(current)={mj_model.opt.timestep} -> will set {config.SIMULATE_DT}")
    print(f"[INFO] nu(actuators)={mj_model.nu}, nq={mj_model.nq}, nv={mj_model.nv}")
    print(f"[INFO] disableflags={mj_model.opt.disableflags}, enableflags={mj_model.opt.enableflags}")
    print(f"[INFO] DDS DOMAIN_ID={getattr(config,'DOMAIN_ID',None)} INTERFACE={getattr(config,'INTERFACE',None)}")

# Viewer
if getattr(config, "ENABLE_ELASTIC_BAND", False):
    elastic_band = ElasticBand()
    if getattr(config, "ROBOT", "") in ("h1", "g1"):
        band_attached_link = mj_model.body("torso_link").id
    else:
        band_attached_link = mj_model.body("base_link").id
    viewer = mujoco.viewer.launch_passive(
        mj_model, mj_data, key_callback=elastic_band.MujuocoKeyCallback
    )
else:
    viewer = mujoco.viewer.launch_passive(mj_model, mj_data)

# Apply desired dt
mj_model.opt.timestep = config.SIMULATE_DT

# Actuator 0 joint addresses (for diagnostics)
act0 = 0 if mj_model.nu > 0 else None
if act0 is not None:
    j0 = mj_model.actuator_trnid[act0, 0]   # joint id for actuator 0
    qadr0  = mj_model.jnt_qposadr[j0]      # index in qpos
    dqadr0 = mj_model.jnt_dofadr[j0]       # index in qvel
else:
    j0 = qadr0 = dqadr0 = None

time.sleep(0.2)

def SimulationThread():
    print("[SIM] SimulationThread starting…")
    try:
        # DDS init
        print(f"[SIM] ChannelFactoryInitialize(domain={config.DOMAIN_ID}, iface='{config.INTERFACE}')")
        ChannelFactoryInitialize(config.DOMAIN_ID, config.INTERFACE)
        print("[SIM] DDS initialized.")

        unitree = None
        if not BYPASS_BRIDGE:
            print("[SIM] Creating UnitreeSdk2Bridge…")
            unitree = UnitreeSdk2Bridge(mj_model, mj_data)
            print("[SIM] UnitreeSdk2Bridge created.")

            if USE_JOYSTICK:
                try:
                    print("[SIM] Setting up joystick (background)…")
                    def _joy_init():
                        unitree.SetupJoystick(device_id=getattr(config, "JOYSTICK_DEVICE", 0),
                                              js_type=getattr(config, "JOYSTICK_TYPE", None))
                    jt = Thread(target=_joy_init, name="joy_init", daemon=True)
                    jt.start()
                    jt.join(timeout=1.5)  # don't block the sim if joystick init hangs
                    if jt.is_alive():
                        print("[WARN] Joystick init still running; continuing without blocking.")
                    else:
                        print("[SIM] Joystick setup done.")
                except Exception as e:
                    print(f"[WARN] Joystick setup failed (continuing): {e}")
            else:
                print("[SIM] Joystick disabled.")

            if getattr(config, "PRINT_SCENE_INFORMATION", False):
                try:
                    unitree.PrintSceneInformation()
                except Exception as e:
                    print(f"[WARN] PrintSceneInformation failed (continuing): {e}")
        else:
            print("[SIM] BYPASS_BRIDGE=True → not creating Unitree bridge (diagnostic mode).")

        heart_every = max(1, int(round(1.0 / mj_model.opt.timestep)))
        heart_i = 0

        print("[SIM] Entering main step loop.")
        while viewer.is_running():
            step_start = time.perf_counter()
            locker.acquire()

            # Optional elastic band external force
            if getattr(config, "ENABLE_ELASTIC_BAND", False):
                if elastic_band.enable:
                    mj_data.xfrc_applied[band_attached_link, :3] = elastic_band.Advance(
                        mj_data.qpos[:3], mj_data.qvel[:3]
                    )

            # 2s torque to prove motion (actuator 0)
            if FORCE_TEST_2S and act0 is not None:
                if mj_data.time < 2.0:
                    mj_data.ctrl[act0] = 20.0  # try 10–30 Nm
                else:
                    mj_data.ctrl[act0] = 0.0  # <— reset so it releases the limit

            # Optional PD test on actuator 0
            if PD_TEST and act0 is not None:
                q  = mj_data.qpos[qadr0]
                qd = mj_data.qvel[dqadr0]
                mj_data.ctrl[act0] = PD_KP * (PD_Q_TARGET - q) - PD_KD * qd

            mujoco.mj_step(mj_model, mj_data)
            locker.release()

            # 1 Hz heartbeat
            if PRINT_HEARTBEAT:
                heart_i += 1
                if heart_i % heart_every == 0:
                    if act0 is not None:
                        c0 = float(mj_data.ctrl[act0])
                        q0 = float(mj_data.qpos[qadr0])
                        print(f"[t={mj_data.time:7.3f}] ctrl0={c0:8.3f} q0={q0:7.3f}")
                    else:
                        print(f"[t={mj_data.time:7.3f}] (no actuators)")

            # pacing
            dt = mj_model.opt.timestep - (time.perf_counter() - step_start)
            if dt > 0:
                time.sleep(dt)

        print("[SIM] viewer closed → exiting sim loop.")

    except Exception as e:
        print("[ERROR] Exception in SimulationThread:")
        traceback.print_exc()

def PhysicsViewerThread():
    print("[VIEW] PhysicsViewerThread starting…")
    try:
        while viewer.is_running():
            locker.acquire()
            viewer.sync()
            locker.release()
            time.sleep(config.VIEWER_DT)
        print("[VIEW] viewer closed → exiting viewer loop.")
    except Exception as e:
        print("[ERROR] Exception in PhysicsViewerThread:")
        traceback.print_exc()

if __name__ == "__main__":
    viewer_thread = Thread(target=PhysicsViewerThread, name="viewer")
    sim_thread    = Thread(target=SimulationThread,    name="sim")

    viewer_thread.start()
    sim_thread.start()
