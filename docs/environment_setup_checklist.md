# Environment Setup Checklist

## Goal
Set up environment exactly as in the Unitree G1 Reinforcement Learning Course.

---

## 1. Repository Structure

### Official Course Repositories
| Repo | Location | Source |
|------|----------|--------|
| `unitree_sdk2_python` | `_vendor/unitree_sdk2_python/` | GitHub (official) |
| `unitree_mujoco` | `_vendor/unitree_mujoco/` | GitHub (official, 29DOF) |
| `unitree_mujoco_tc` | `_vendor/unitree_mujoco_tc/` | Bitbucket (course, 23DOF) |
| `unitree_rl_gym` | `_vendor/unitree_rl_gym/` | Bitbucket (course) |
| `unitree_mujoco_extras` | `_vendor/unitree_mujoco_extras/` | Third-party (RPC bridge) |

### Your Setup
- **G1 Model:** 29DOF (your current setup)
- **Course Model:** 23DOF (patched in course repo)
- **Strategy:** Keep your 29DOF, copy course files as needed

---

## 2. Git Submodules

### ✅ Completed
- [x] `unitree_sdk2_python` - GitHub (official)
- [x] `unitree_mujoco` - GitHub (official, 29DOF)
- [x] `unitree_mujoco_extras` - Third-party (RPC bridge)

### ⬜ To Add
- [ ] `unitree_mujoco_tc` - Bitbucket (course, 23DOF)
- [ ] `unitree_rl_gym` - Bitbucket (course)

---

## 3. Python Environment

### Required Packages
```bash
# From requirements.txt
cyclonedds>=0.10.2
unitree_sdk2py
mujoco
pygame
```

### Installation Steps
```bash
# Create venv
cd /home/raisebox/Projects/unitree-g1-gangnam-style
python3 -m venv g1
source g1/bin/activate
pip install --upgrade pip

# Install cyclonedds first
pip install 'cyclonedds>=0.10.2'

# Install unitree_sdk2_python
cd _vendor/unitree_sdk2_python
pip install -e .

# Install MuJoCo and pygame
pip install mujoco pygame

# Install other dependencies
pip install -r requirements.txt
```

### Verification
```bash
python3 -c "import unitree_sdk2py; import mujoco; import pygame; print('All imports successful')"
```

---

## 4. MuJoCo Simulation Setup

### Your Setup (Keep This)
**Location:** `_vendor/unitree_mujoco/simulate_python/`

**Config:** `_vendor/unitree_mujoco/simulate_python/config.py`
```python
ROBOT = "g1"
ROBOT_SCENE = "../unitree_robots/g1/scene_29dof.xml"  # Your 29DOF
DOMAIN_ID = 1
INTERFACE = "lo"
USE_JOYSTICK = 1
JOYSTICK_TYPE = "xbox"
JOYSTICK_DEVICE = 0
ENABLE_ELASTIC_BAND = True
SIMULATE_DT = 0.005
VIEWER_DT = 0.02
```

**Launch:**
```bash
cd _vendor/unitree_mujoco/simulate_python
python3 unitree_mujoco.py
```

### Course Setup (Reference Only)
**Location:** `_vendor/unitree_mujoco_tc/unitree_mujoco/simulate_python/`

**Note:** Course uses 23DOF model. Do NOT use their config.py.

---

## 5. RPC Server Bridge

### Source
**Third-party:** `_vendor/unitree_mujoco_extras/loco_rpc_server_bridge.py`

**Course alternatives (in `_vendor/unitree_mujoco_tc/unitree_mujoco/simulate_python/`):**
- `unitree_sdk2py_bridge_v2.py`
- `unitree_sdk2py_bridge_v3.py`
- `unitree_sdk2py_bridge_v4.py`
- `unitree_sdk2py_bridge_v4_wireless.py`

### Launch RPC Bridge
```bash
cd _vendor/unitree_mujoco_extras
python3 loco_rpc_server_bridge.py --iface lo --domain 1
```

---

## 6. Gamepad GUI

### Source
**Third-party:** `_vendor/unitree_mujoco_extras/wireless_controller_gui_v2.py`

### Launch Gamepad GUI
```bash
cd _vendor/unitree_mujoco_extras
python3 wireless_controller_gui_v2.py lo 1
```

---

## 7. Unitree SDK Examples

### Low Level Examples
From `_vendor/unitree_sdk2_python/example/g1/low_level/`:
- `g1_low_level_example.py` - Motor control

### High Level Examples
From `_vendor/unitree_sdk2_python/example/g1/high_level/`:
- `g1_loco_client_example.py` - LocoClient commands
- `g1_arm_action_example.py` - Arm control

### Wireless Controller
From `_vendor/unitree_sdk2_python/example/wireless_controller/`:
- `wireless_controller.py` - Gamepad subscriber

### Run Examples (in order)
```bash
# Terminal 1: Launch simulation
cd _vendor/unitree_mujoco/simulate_python
python3 unitree_mujoco.py

# Terminal 2: Launch RPC bridge
cd _vendor/unitree_mujoco_extras
python3 loco_rpc_server_bridge.py --iface lo --domain 1

# Terminal 3: Run SDK example
cd _vendor/unitree_sdk2_python/example/g1/low_level
python3 g1_low_level_example.py
```

---

## 8. Course Exercises

### Unit 3: Unitree SDK
1. **Exercise 1**: State Machine Control
   - Script: `scripts/set_fsm_state.py`
   - Test: FSM transitions (0, 1, 4, 500)

2. **Exercise 2**: Low Level Control
   - Example: `g1_low_level_example.py`
   - Test: Motor commands, Kp/Kd gains

3. **Exercise 3**: WirelessController GUI
   - Script: `wireless_controller_gui_v2.py`
   - Test: Gamepad input

### Unit 4-5: Simulations & RL Lab
1. **Exercise 4**: Sim2Sim Setup
   - Launch: `launch_unitree_v3.py`
   - Test: Full pipeline with RL policy

2. **Exercise 5**: Policy Deployment
   - Script: `policy_to_lowcmd_v11b_*.py`
   - Test: RL policy in MuJoCo

### Unit 6-9: Training & Deployment
- Follow course document step by step

### Unit 10+: Advanced topics
- ROS 2
- VLA
- GR00T

---

## 9. RL Gym (Optional)

### Setup
```bash
cd _vendor/unitree_rl_gym
pip install -e .
```

### Training
```bash
python legged_gym/scripts/train.py --task=g1
```

### Play (Visualize)
```bash
python legged_gym/scripts/play.py --task=g1
```

### Sim2Sim (Mujoco)
```bash
python deploy/deploy_mujoco/deploy_mujoco.py {config_name}
```

---

## 10. Testing Checklist

### Basic Communication
- [ ] DDS initialized (domain 1, interface lo)
- [ ] Can publish to `rt/lowcmd`
- [ ] Can subscribe to `rt/lowstate`
- [ ] Can publish to `rt/wirelesscontroller`

### MuJoCo Simulation
- [ ] G1 robot loads in viewer
- [ ] Elastic band works (keys 7, 8, 9)
- [ ] Robot responds to commands
- [ ] Gamepad input visible in `wireless_controller.py`

### RPC Bridge
- [ ] `loco_rpc_server_bridge.py` starts
- [ ] LocoClient can call `SetFsmId()`
- [ ] LocoClient can call `Damp()`, `WaveHand()`
- [ ] RPC responses received

### SDK Examples
- [ ] `g1_low_level_example.py` runs
- [ ] `g1_loco_client_example.py` runs
- [ ] `wireless_controller.py` runs

### Course Exercises
- [ ] Unit 3 exercises complete
- [ ] Unit 4-5 exercises complete
- [ ] Unit 6-9 exercises complete

---

## 11. Repository Summary

| Repo | URL | Status |
|------|-----|--------|
| unitree_sdk2_python | https://github.com/unitreerobotics/unitree_sdk2_python | ✅ Cloned |
| unitree_mujoco | https://github.com/unitreerobotics/unitree_mujoco | ✅ Cloned (29DOF) |
| unitree_mujoco_tc | https://bitbucket.org/theconstructcore/g1_mujoco_tc | ⬜ Need to clone |
| unitree_rl_gym | https://bitbucket.org/theconstructcore/g1_mujoco_tc | ⬜ Need to clone |
| unitree_mujoco_extras | https://github.com/Michdo93/unitree_mujoco_extras | ✅ Cloned |

---

## 12. Next Steps

### Immediate (This Session)
1. ✅ Clone official repos (done)
2. ⬜ Verify Python environment
3. ⬜ Test MuJoCo simulation
4. ⬜ Test RPC bridge
5. ⬜ Test gamepad GUI

### Short Term
1. ⬜ Complete Unit 3 exercises
2. ⬜ Test all SDK examples
3. ⬜ Document each exercise

### Medium Term
1. ⬜ Complete Unit 4-5 (Sim2Sim)
2. ⬜ Set up unitree_rl_gym (if needed)
3. ⬜ Complete Unit 6-9 (Training)

### Long Term
1. ⬜ Gangnam Style choreography
2. ⬜ Motion sequence implementation
3. ⬜ Real robot deployment

---

## 13. Files to Copy from Course (When Needed)

### From `_vendor/unitree_mujoco_tc/unitree_mujoco/`
| File | When to Copy |
|------|--------------|
| `simulate_python/unitree_mujoco_optim.py` | Optimized simulator |
| `simulate_python/unitree_sdk2py_bridge_v4_wireless.py` | Wireless bridge |
| `terrain_tool/` | Terrain generation |
| `example/` | Course examples |

### Skip These (23DOF-specific)
| File | Reason |
|------|--------|
| `unitree_robots/g1/g1_23dof.xml` | Wrong DOF |
| `unitree_robots/g1/g1_23dof_patched_v2.xml` | Wrong DOF |
| `unitree_robots/g1/scene_23dof.xml` | Wrong DOF |
| `simulate_python/config.py` | References 23DOF |

---

*Last updated: 2026-08-13*