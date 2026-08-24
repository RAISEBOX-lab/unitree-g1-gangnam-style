# Unitree G1 Gangnam Style - Project Guidelines

## ⚠️ CRITICAL SAFETY RULE

**NEVER touch the real robot without first testing everything in simulation.**

### Development Workflow
1. **Simulator First**: All code, scripts, and configurations MUST be tested in MuJoCo simulation
2. **Verified & Proven**: Only after simulator validation can we proceed to real robot
3. **Incremental**: Test each state/transition individually before combining

---

## Project Objective

Execute the "Unitree G1 Reinforcement Learning Course" to enable the Unitree G1 robot to perform the Gangnam Style dance.

### Course Structure
1. **Unit 1-2**: Introduction & Network Configuration
2. **Unit 3**: Unitree SDK (start here)
3. **Unit 4-5**: Simulations & RL Lab pipeline
4. **Unit 6-9**: Training & Deployment
5. **Unit 10+**: Advanced topics (ROS 2, VLA, GR00T)

---

## Current State

- **Repo**: Initialized at `/home/raisebox/Projects/unitree-g1-gangnam-style`
- **Course Doc**: `Unitree G1 Reinforcement Learning Course.docx` (415MB)
- **Submodules**:
  - `_vendor/unitree_sdk2_python` - Python SDK for DDS (GitHub)
  - `_vendor/unitree_mujoco` - MuJoCo simulator (GitHub, 29DOF)
  - `_vendor/unitree_mujoco_extras` - RPC bridge, gamepad GUI (third-party)
  - `_vendor/unitree_mujoco_tc` - Course repo (Bitbucket, 23DOF)
  - `_vendor/unitree_rl_gym` - RL training/deployment (Bitbucket)
- **Gangnam Motion**: Located at `_vendor/unitree_rl_gym/deploy/pre_train/g1/motion.pt`
- **29DOF Models**: `_vendor/unitree_rl_gym/resources/robots/g1_description/g1_29dof*.xml`

---

## 4-Phase Workflow

### Phase 1: Environment Setup (CURRENT)
Set up all dependencies and verify simulation works:
1. ✅ Clone official course repos from Bitbucket
2. ✅ Set up Python environment with all dependencies
3. ✅ Verify MuJoCo simulation runs with G1 robot
4. ✅ Test RPC bridge and gamepad GUI
5. **Document all setup steps** for reproducibility

### Phase 2: SDK Exercises (Unit 3)
Complete all Unitree SDK exercises in order:
1. **Exercise 1**: State Machine Control - FSM transitions
2. **Exercise 2**: Low Level Control - Motor commands, Kp/Kd
3. **Exercise 3**: WirelessController GUI - Gamepad integration
4. **Exercise 4**: G1 Poses - Full robot pose control
5. **Exercise 5**: Arm SDK PreRecorded Movements
6. **Exercise 6**: Arm SDK Capture Movements

### Phase 3: RL Lab Exercises (Unit 4-5)
Complete RL simulation and deployment exercises:
1. **Exercise 7**: Sim2Sim Setup - Full pipeline with RL policy
2. **Exercise 8**: Policy Deployment - RL policy in MuJoCo
3. **Exercise 9**: Custom motion training (if time permits)

### Phase 4: Gangnam Style (Final Goal)
After mastering all exercises:
1. Design Gangnam choreography sequence
2. Implement motion sequences using learned SDK/RL techniques
3. Test in simulation
4. Deploy to real robot (ONLY after simulation verified)

---

## Environment

### Hardware
- **Robot**: Unitree G1 (physical, with ROS2)
- **Dev PC**: Ubuntu with ROS2 (Jazzy/Foxy)
- **Network**: Ethernet connection to robot (192.168.123.164)

### Software
- **ROS2**: Jazzy and Foxy installed
- **SDK**: Unitree SDK2 Python (in `_vendor/unitree_sdk2_python/`)
- **Simulation**: Unitree MuJoCo (in `_vendor/unitree_mujoco/`)

### Submodules
```
_vendor/
├── unitree_sdk2_python/   # Python SDK for DDS
├── unitree_mujoco/        # MuJoCo simulator (29DOF)
├── unitree_mujoco_extras/ # RPC bridge, gamepad GUI
├── unitree_mujoco_tc/     # Course repo (23DOF)
└── unitree_rl_gym/        # RL training/deployment
```

---

## First Steps

### Exercise 1: Unitree SDK - State Machine Control (Unit 3)

**Goal**: Learn to transition between robot states (FSM IDs)

**States:**
| ID | Mode | Risk |
|---|---|---|
| 0 | Zero Torque | ⚠️ DANGEROUS - robot falls |
| 1 | Damping | ✅ Safe - joints have resistance |
| 4 | Lock Standing | ✅ Safe |
| 500 | Walk Motion | ⚡ Balance enabled |

**Workflow:**
1. Create state machine script in `scripts/set_fsm_state.py`
2. Test in MuJoCo simulation (use `lo` interface)
3. Verify state transitions work correctly
4. Only then test on real robot (via Ethernet)

---

## Project Structure

```
unitree-g1-gangnam-style/
├── README.md                    # Project overview
├── PROJECT_GUIDELINES.md        # This file (rules, workflow)
├── _vendor/                     # Course dependencies (submodules)
│   ├── unitree_sdk2_python/    # Python SDK for DDS
│   ├── unitree_mujoco/          # MuJoCo simulator
│   ├── unitree_mujoco_extras/   # RPC bridge, gamepad GUI
│   ├── unitree_mujoco_tc/       # Course repo (23DOF)
│   └── unitree_rl_gym/          # RL training/deployment
├── scripts/                     # User scripts (exercise implementations)
├── g1/                          # Python virtual environment
├── docs/                        # Analysis documents
└── requirements.txt             # Python dependencies
```

---

## Key Constraints

1. **No real robot until simulator verified**
2. **No changes without user confirmation**
3. **Document everything learned** - Each exercise creates analysis docs in `docs/`
4. **Follow course order (Unit 3 first)**
5. **All outputs in project folder** - Scripts, configs, notes in project folders

---

## Notes

- Keyboard layout: pt-PT (set)
- GitHub MCP: Broken (use gh CLI)
- Tailscale: Working (raisebox-spark:8000 for vLLM)
- opencode config: Points to LAN IP (needs Tailscale fix)
- **Course Progress**: Start from Unit 3 (SDK exercises), not Unit 1-2

---

*Last updated: 2026-08-14*

---

## Setup Instructions

### Create Python Environment
```bash
cd ~/Projects/unitree-g1-gangnam-style
python3 -m venv g1
source g1/bin/activate
pip install --upgrade pip
```

### Install Dependencies
```bash
# Install cyclonedds first (needed by SDK)
pip install 'cyclonedds>=0.10.2'

# Install unitree_sdk2_python (modify setup.py if needed)
cd _vendor/unitree_sdk2_python
sed -i 's/cyclonedds==0.10.2/cyclonedds>=0.10.2/' setup.py
pip install -e .

# Install MuJoCo and pygame
cd ..
pip install mujoco pygame
```

### Verification
```bash
python3 -c "import unitree_sdk2py; import mujoco; print('All imports successful')"
```

### Next: Set up MuJoCo simulation
See Unit 3 of the course for simulation setup.

---

## Current Status

✅ **Completed:**
- Git repo initialized
- Submodules cloned: `unitree_sdk2_python`, `unitree_mujoco`, `unitree_mujoco_extras`, `unitree_mujoco_tc`, `unitree_rl_gym`
- Python venv created (`g1/`)
- Dependencies installed and verified
- `scripts/` directory created

📋 **Next:** Unit 3 - Unitree SDK exercises

---

## 29DOF vs 23DOF

**Your robot:** 29DOF G1

**Use these files:**
- `_vendor/unitree_rl_gym/resources/robots/g1_description/g1_29dof.xml`
- `_vendor/unitree_rl_gym/resources/robots/g1_description/g1_29dof_rev_1_0.xml`

**DO NOT USE:** Any `g1_23dof*` or `g1_12dof*` files (wrong DOF)

---

## DO NOT

- ❌ Modify robot code without simulation verification
- ❌ Delete files or repos (catastrophic deletion happened before)
- ❌ Execute commands without user running them (trust issue)

## DO

- ✅ Test everything in simulation first
- ✅ Save analysis outputs as files in `docs/`
- ✅ Follow the 4-phase workflow
- ✅ Ask before making destructive changes
- ✅ Run verification commands before proceeding