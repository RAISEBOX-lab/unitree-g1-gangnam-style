# Unitree G1 Gangnam Style - Project Guidelines

## ⚠️ CRITICAL SAFETY RULE

**NEVER touch the real robot without first testing everything in simulation.**

### Development Workflow
1. **Simulator First**: All code, scripts, and configurations MUST be tested in Mujoco simulation
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
- **Submodules**: `_vendor/unitree_sdk2_python`, `_vendor/unitree_mujoco` (cloned)
- **Gangnam Motion**: Not yet located (user will provide)

---

## Environment

### Hardware
- **Robot**: Unitree G1 (physical, with ROS2)
- **Dev PC**: Ubuntu with ROS2 (Jazzy/Foxy)
- **Network**: Ethernet connection to robot (192.168.123.164)

### Software
- **ROS2**: Jazzy and Foxy installed
- **SDK**: Unitree SDK2 Python (in `_vendor/unitree_sdk2_python/`)
- **Simulation**: Unitree Mujoco (in `_vendor/unitree_mujoco/`)

### Submodules
```
_vendor/
├── unitree_sdk2_python/   # Python SDK for DDS communication
└── unitree_mujoco/        # MuJoCo simulator for G1
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
2. Test in Mujoco simulation (use `lo` interface)
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
│   └── unitree_mujoco/          # MuJoCo simulator
├── scripts/                     # Python scripts
│   └── set_fsm_state.py        # State machine control
├── sim/                         # Simulation configs
└── docs/                        # Notes from course
```

---

## Key Constraints

1. **No real robot until simulator verified**
2. **No changes without user confirmation**
3. **Document everything learned**
4. **Follow course order (Unit 3 first)**

---

## Notes

- Keyboard layout: pt-PT (set)
- GitHub MCP: Broken (use gh CLI)
- Tailscale: Working (raisebox-spark:8000 for vLLM)
- opencode config: Points to LAN IP (needs Tailscale fix)

---

*Last updated: 2026-08-12*

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

### Next: Set up Mujoco simulation
See Unit 3 of the course for simulation setup.

---

## Current Status

✅ **Completed:**
- Git repo initialized
- Submodules cloned: `unitree_sdk2_python`, `unitree_mujoco`
- Python venv created (`g1/`)
- Dependencies installed and verified

📋 **Next:** Unit 3 - Unitree SDK exercises