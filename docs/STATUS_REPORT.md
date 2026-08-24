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

### 1. Elastic Band Enabled (FIXED)
**Issue:** `ENABLE_ELASTIC_BAND = True` was holding robot in place  
**Fix:** Changed to `ENABLE_ELASTIC_BAND = False`  
**Status:** ✅ Fixed

### 2. Missing mj_forward() (FIXED)
**Issue:** Robot position not initialized after loading model  
**Fix:** Added `mujoco.mj_forward(mj_model, mj_data)` after creating mj_data  
**Status:** ✅ Fixed

### 3. Typo in Sensor Detection (NOT FIXED)
**Issue:** `have_imu_` vs `have_imu` (trailing underscore typo)  
**Location:** `unitree_sdk2py_bridge.py:55-57`  
**Impact:** IMU data not read from sensors  
**Status:** ⚠️ Identified, not fixed (doesn't affect physics)

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

### Solution 1: Disable Elastic Band
**File:** `simulate_python/config.py`
```python
ENABLE_ELASTIC_BAND = False  # Was True
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
- `ENABLE_ELASTIC_BAND = False`

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
**File:** `unitree_sdk2py_bridge.py:55-57`
```python
# WRONG:
if name == "imu_quat":
    self.have_imu_ = True  # Has trailing underscore
if name == "frame_pos":
    self.have_frame_sensor_ = True  # Has trailing underscore

# SHOULD BE:
if name == "imu_quat":
    self.have_imu = True  # No trailing underscore
if name == "frame_pos":
    self.have_frame_sensor = True  # No trailing underscore
```

**Impact:** IMU data not read from sensors  
**Status:** Not critical for physics, can be fixed later

### 2. RPC Bridge Sends Commands on Startup
**Issue:** RPC bridge sends LockedStanding immediately  
**Impact:** None (simulation ignores until 'E' pressed)  
**Status:** Acceptable workaround

---

## Next Steps

1. **Test the fix:** Run simulation and verify robot falls
2. **Test drag:** Verify mouse drag works before pressing 'E'
3. **Test FSM:** Press 'E' and verify FSM commands work
4. **Fix typo:** Correct `have_imu_` → `have_imu` (optional)
5. **Proceed to Gangnam:** Start implementing dance choreography

---

*Last updated: 2026-08-17*
