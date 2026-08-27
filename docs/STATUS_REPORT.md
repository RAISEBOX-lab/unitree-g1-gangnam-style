# Unitree G1 Gangnam Style - Status Report

## Project Objective
Implement Gangnam Style dance choreography on Unitree G1 robot using MuJoCo simulation.

---

## Current State

### ✅ Working
- Python venv created (`g1/`)
- All dependencies installed
- All repos cloned:
  - `unitree_sdk2_python` (GitHub)
  - `unitree_mujoco` (GitHub, 29DOF)
  - `unitree_mujoco_extras` (Third-party)
  - `unitree_mujoco_tc` (Bitbucket)
  - `unitree_rl_gym` (Bitbucket)
- RPC bridge starts and receives FSM commands
- LocoClient connects and sends FSM commands
- Simulation viewer opens

### ❌ NOT Working
- **Robot physics not responding** - Robot stays in place, doesn't fall
- **Mouse drag doesn't work** - Robot is locked in place
- **FSM commands have no effect** - ZeroTorque, Damp, LockedStanding all ignored

---

## Problems Identified

### 1. Elastic Band Enabled (RESOLVED — band re-enabled)
**Issue:** `ENABLE_ELASTIC_BAND = True` appeared to hold the robot in place  
**Root cause:** the real lock came from `rt/lowcmd` being applied before any FSM was set (see #5)  
**Current setting:** `ENABLE_ELASTIC_BAND = True` again (needed to hang the robot before stand-up); the `fsm_set` gate (#5) is what prevents the lock  
**Status:** ✅ Resolved

### 2. Missing mj_forward() (FIXED)
**Issue:** Robot position not initialized after loading model  
**Fix:** Added `mujoco.mj_forward(mj_model, mj_data)` after creating mj_data  
**Status:** ✅ Fixed

### 3. Typo in Sensor Detection (FIXED 2026-08-24)
**Issue:** `have_imu_` vs `have_imu` (trailing underscore typo)  
**Location:** `unitree_sdk2py_bridge.py:55-57`  
**Impact:** IMU data not read from sensors  
**Status:** ✅ Fixed in the `unitree_mujoco` fork (branch `raisebox-fixes`, commit `fc97c71`)

### 4. RPC Bridge Sends LockedStanding on Startup (PARTIALLY FIXED)
**Issue:** RPC bridge sends LockedStanding (kp=120) immediately on startup  
**Impact:** Robot stays locked in place even before FSM command  
**Status:** ⚠️ Partially fixed (see below)

### 5. No FSM State Tracking (FIXED)
**Issue:** Simulation processes lowcmd immediately, even before FSM is set  
**Impact:** Robot locked by RPC commands before user can interact  
**Fix:** Added `fsm_set` flag - simulation ignores lowcmd until 'E' is pressed  
**Status:** ✅ Fixed

---

## Solutions Implemented

### Solution 1: Elastic Band + FSM gate
**File:** `simulate_python/config.py`
```python
ENABLE_ELASTIC_BAND = True   # keep the band; the fsm_set gate below prevents the lock
```

### Solution 2: Initialize Position
**File:** `simulate_python/unitree_mujoco.py`
```python
mj_model = mujoco.MjModel.from_xml_path(config.ROBOT_SCENE)
mj_data = mujoco.MjData(mj_model)
mujoco.mj_forward(mj_model, mj_data)  # Added this line
```

### Solution 3: FSM State Tracking (NEW)
**File:** `simulate_python/unitree_sdk2py_bridge.py`
```python
# In __init__:
self.fsm_set = False  # Only process lowcmd after FSM is set

# In LowCmdHandler:
def LowCmdHandler(self, msg: LowCmd_):
    if not self.fsm_set:
        return  # Ignore lowcmd until FSM is set
    # ... rest of handler
```

**File:** `simulate_python/unitree_mujoco.py`
```python
# Added import:
import mujoco.glfw.glfw as glfw

# Added print:
print("[INFO] Press E to enable FSM processing (robot will fall until then)")

# Added key check in simulation loop:
if glfw.glfwKeyPressed(viewer.window, glfw.KEY_E):
    unitree.fsm_set = True
    print("[DEBUG] FSM enabled - lowcmd processing started")
```

---

## What Works Now

### Before Fix
1. RPC bridge starts → sends LockedStanding
2. Simulation receives LockedStanding → robot locked
3. User can't drag robot
4. FSM commands have no effect

### After Fix
1. Simulation starts → `fsm_set = False`
2. RPC bridge starts → sends LockedStanding
3. Simulation **ignores** lowcmd (fsm_set=False)
4. **Robot falls naturally** with gravity
5. **User can drag robot** with mouse
6. Press **'E'** → `fsm_set = True`
7. Simulation **starts processing** lowcmd
8. FSM commands now work

---

## Files Modified

### unitree_mujoco/simulate_python/config.py
- `ROBOT = "g1"`, `ROBOT_SCENE = scene_29dof.xml`, `ENABLE_ELASTIC_BAND = True`, `USE_JOYSTICK = 0`

### unitree_mujoco/simulate_python/unitree_mujoco.py
- Added `import mujoco.glfw.glfw as glfw`
- Added `mujoco.mj_forward(mj_model, mj_data)`
- Added `print("[INFO] Press E...")`
- Added key check for 'E' key

### unitree_mujoco/simulate_python/unitree_sdk2py_bridge.py
- Added `self.fsm_set = False` in `__init__`
- Added `if not self.fsm_set: return` in `LowCmdHandler`

---

## Test Steps

### Terminal 1: Simulation
```bash
cd /home/raisebox/Projects/unitree-g1-gangnam-style/_vendor/unitree_mujoco/simulate_python
source /home/raisebox/Projects/unitree-g1-gangnam-style/g1/bin/activate
python3 unitree_mujoco.py
```

**Expected:**
- Robot appears at 0.793m
- Robot falls naturally
- You can drag robot with mouse
- Press 'E' to enable FSM

### Terminal 2: RPC Bridge
```bash
cd /home/raisebox/Projects/unitree-g1-gangnam-style/_vendor/unitree_mujoco_extras
source /home/raisebox/Projects/unitree-g1-gangnam-style/g1/bin/activate
python3 loco_rpc_server_bridge.py --iface lo --domain 1
```

### Terminal 3: LocoClient
```bash
cd /home/raisebox/Projects/unitree-g1-gangnam-style/_vendor/unitree_mujoco_extras
source /home/raisebox/Projects/unitree-g1-gangnam-style/g1/bin/activate
python3 example_use_lococlient_simversion_v2.py lo 1
```

---

## Known Issues

### 1. Typo in Sensor Detection
**Status:** ✅ Fixed 2026-08-24 (`have_imu`, `have_frame_sensor`), see Problem #3 above

### 2. RPC Bridge Sends Commands on Startup
**Issue:** RPC bridge sends LockedStanding immediately  
**Impact:** None (simulation ignores until 'E' pressed)  
**Status:** Acceptable workaround

---

## Next Steps

1. **Velocity policy:** continue `Unitree-G1-29dof-Velocity` training (resume from `2026-08-24_15-17-54/model_300.pt`), re-export with `play.py`, re-test in MuJoCo
2. **Reference check:** run Unitree's bundled `config/policy/velocity/v0` through the same sim2sim chain to see a finished policy
3. **Gangnam:** train `Unitree-G1-29dof-Mimic-Gangnanm-Style` (note the typo in the task id) and run it via the `Mimic_Gangnam_Style` FSM state (`L2` held 2 s + D-pad Left from Velocity mode)

---

## Sim2sim Setup — unitree_rl_lab C++ pipeline (2026-08-24)

The Python simulator above is the course (Unit 3) path. Policies trained in Isaac Lab are tested with
Unitree's C++ pipeline instead:

```
Isaac Lab checkpoint (.pt) ─ play.py ─► exported/policy.onnx + params/deploy.yaml
        └─► g1_ctrl (C++ FSM + ONNX Runtime) ◄─ DDS on lo ─► unitree_mujoco (C++ sim, 29-DOF G1, gamepad)
```

### Build (done on this machine)
```bash
sudo apt install -y libyaml-cpp-dev libboost-all-dev libeigen3-dev libspdlog-dev libfmt-dev libglfw3-dev
# unitree_sdk2 (C++) -> /opt/unitree_robotics
cd _vendor && git clone https://github.com/unitreerobotics/unitree_sdk2.git && cd unitree_sdk2
mkdir -p build && cd build && cmake .. -DBUILD_EXAMPLES=OFF && sudo make install
# MuJoCo release inside the C++ simulator (3.3.6: https://github.com/google-deepmind/mujoco/releases/tag/3.3.6)
cd _vendor/unitree_mujoco/simulate && tar xzf mujoco-3.3.6-linux-x86_64.tar.gz && mv mujoco-3.3.6 mujoco
mkdir -p build && cd build && cmake .. && make -j$(nproc)
# controller
cd _vendor/unitree_rl_lab/deploy/robots/g1_29dof && mkdir -p build && cd build && cmake .. && make -j$(nproc)
```
Fixes applied (in the `RAISEBOX-lab/unitree_mujoco` fork): `#include <cstdint>` in `jstest.cc` (GCC 13);
new `PS4Joystick` layout in `physics_joystick.h` (`joystick_type: "ps4"`) for the REV-31-2983 /
"ZEROPLUS P4" pad — axes 0/1 LX/LY, 2 RX, 3 L2, 4 R2, 5 RY, 6/7 D-pad; buttons 0 □, 1 ✕, 2 ○, 3 △, 4 L1, 5 R1, 8 Share, 9 Options
(verified with `scripts/js_probe.py`).

### Config
- `_vendor/unitree_mujoco/simulate/config.yaml`: `robot: g1`, `scene_29dof.xml`, `domain_id: 0`, `interface: lo`, `use_joystick: 1`, `joystick_type: ps4`, `enable_elastic_band: 1`
- `_vendor/unitree_rl_lab/deploy/robots/g1_29dof/config/config.yaml`: `Velocity.policy_dir: ../../../logs/rsl_rl/unitree_g1_29dof_velocity` (newest run containing `exported/` is used)

### Run
```bash
# T1
cd _vendor/unitree_mujoco/simulate/build && ./unitree_mujoco
# T2  (--network lo is required: the default binds the LAN interface and never sees the sim)
cd _vendor/unitree_rl_lab/deploy/robots/g1_29dof/build && ./g1_ctrl --network lo
```
PS4 chords: `L2 + D-pad Up` → FixStand · MuJoCo window key `8` → lower to floor · `R1 + □` → Velocity policy ·
key `9` → release band · left stick → walk · `L2 + ○` → Passive.

### Train / export (venv `g1`, `OMNI_KIT_ACCEPT_EULA=YES`, from `_vendor/unitree_rl_lab`)
```bash
python scripts/rsl_rl/train.py --task Unitree-G1-29dof-Velocity --headless --num_envs 2048 [--resume --load_run <run> --checkpoint model_N.pt]
python scripts/rsl_rl/play.py  --task Unitree-G1-29dof-Velocity --headless --num_envs 1 --checkpoint logs/rsl_rl/unitree_g1_29dof_velocity/<run>/model_N.pt   # writes <run>/exported/policy.onnx, then Ctrl+C
```
Checkpoints every 100 iterations (~9.6 MB each); ~2.3 s/iteration at 2048 envs on the RTX 5060 8 GB.

---

*Last updated: 2026-08-24*
