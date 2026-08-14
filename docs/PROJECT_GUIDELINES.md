# Unitree G1 Reinforcement Learning Course - PROJECT GUIDELINES

## Objective
Implement Gangnam Style dance choreography on the Unitree G1 robot using the official Unitree G1 Reinforcement Learning Course as the foundation.

## Current State

- **Repo**: Initialized at `/home/raisebox/Projects/unitree-g1-gangnam-style`
- **Course Doc**: `Unitree G1 Reinforcement Learning Course.docx` (415MB)
- **Submodules**: 
  - `_vendor/unitree_sdk2_python` - Python SDK for DDS (GitHub)
  - `_vendor/unitree_mujoco` - MuJoCo simulator (GitHub, 29DOF)
  - `_vendor/unitree_mujoco_extras` - RPC bridge, gamepad GUI (third-party)
- **Gangnam Motion**: Not yet located (user will provide)

---

## 4-Phase Workflow

### Phase 1: Environment Setup (CURRENT)
Set up all dependencies and verify simulation works:
1. Clone official course repos from Bitbucket
2. Set up Python environment with all dependencies
3. Verify MuJoCo simulation runs with G1 robot
4. Test RPC bridge and gamepad GUI
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

## Key Constraints

1. **No real robot until simulator verified** - All work first in MuJoCo
2. **Document everything learned** - Each exercise creates analysis docs
3. **Follow course order (Unit 3 first)** - Build foundation before advanced topics
4. **All outputs in project folder** - All work outputs (diagrams, scripts, configs, notes) must be saved as files in the project folder

---

## Notes

- **Gangnam Motion**: User will provide the Gangnam Style motion data/sequence
- **Course Progress**: Start from Unit 3 (SDK exercises), not Unit 1-2 (already familiar)
- **Documentation**: Each exercise should have corresponding analysis in `docs/` folder
- **Code Organization**: All scripts go in `scripts/` or `g1/` folders, not root

---

## Repository Structure

```
unitree-g1-gangnam-style/
├── README.md                    # Project overview
├── PROJECT_GUIDELINES.md        # This file (rules, workflow)
├── BEHAVIOR.md                  # Interaction guidelines
├── docs/                        # Analysis documents
│   ├── environment_setup_checklist.md
│   ├── 23dof_vs_29dof_patched_files.md
│   ├── unitree_mujoco_comparison.md
│   ├── unitree_rl_gym_analysis.md
│   ├── official_repo_analysis.md
│   └── (exercise analysis docs)
├── _vendor/                     # Course dependencies (submodules)
│   ├── unitree_sdk2_python/    # Python SDK for DDS
│   ├── unitree_mujoco/          # MuJoCo simulator
│   └── unitree_mujoco_extras/   # RPC bridge, gamepad GUI
├── scripts/                     # Python scripts
│   └── (exercise scripts)
├── g1/                          # Python virtual environment
└── requirements.txt             # Python dependencies
```

---

## Next Steps

1. **Clone course repos**: Get `unitree_mujoco_tc` and `unitree_rl_gym` from Bitbucket
2. **Analyze course structure**: Review first exercise requirements
3. **Set up environment**: Install all dependencies
4. **Start Unit 3**: Begin with Exercise 1 (State Machine Control)

---

*Last updated: 2026-08-13*