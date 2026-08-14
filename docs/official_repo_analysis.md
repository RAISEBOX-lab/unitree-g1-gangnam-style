# Official Course Repository Analysis

## Course Repository Structure

**URL:** `https://bitbucket.org/theconstructcore/g1_mujoco_tc`

### Components

```
g1_mujoco_tc/
├── unitree_mujoco/       # Course-modified MuJoCo simulator (23DOF)
└── unitree_rl_gym/       # Course RL training environment
```

---

## unitree_mujoco (Course Version)

### Location
`bitbucket.org/theconstructcore/g1_mujoco_tc/unitree_mujoco`

### Structure
```
unitree_mujoco/
├── doc/                  # Documentation
├── example/              # Example scripts
├── simulate/             # C++ simulator build
│   ├── build/
│   ├── CMakeLists.txt
│   ├── config.yaml
│   └── src/
│       ├── main.cc
│       └── unitree_sdk2_bridge.h
├── simulate_python/      # Python simulator
│   ├── unitree_mujoco.py
│   ├── unitree_mujoco_optim.py
│   ├── unitree_mujoco_original.py
│   ├── config.py
│   ├── unitree_sdk2py_bridge_v2.py
│   ├── unitree_sdk2py_bridge_v3.py
│   ├── unitree_sdk2py_bridge_v4.py
│   └── unitree_sdk2py_bridge_v4_wireless.py
├── terrain_tool/         # Terrain generation
└── unitree_robots/       # Robot URDF/XML files
    ├── g1/
    │   ├── g1_23dof.xml
    │   ├── g1_23dof_patched_v2.xml
    │   ├── g1_12dof_with_sensors.xml
    │   ├── scene_23dof.xml
    │   └── meshes/
    └── (other robots)
```

### Key Files for Course

| File | Purpose |
|------|---------|
| `simulate_python/unitree_mujoco.py` | Main simulator entry point |
| `simulate_python/unitree_mujoco_optim.py` | Optimized version |
| `simulate_python/unitree_sdk2py_bridge_v4_wireless.py` | Wireless bridge |
| `unitree_robots/g1/g1_23dof_patched_v2.xml` | Patched 23DOF model |
| `terrain_tool/` | Terrain generation tools |

### 23DOF-Specific Files (SKIP for 29DOF)
- `g1_23dof.xml`
- `g1_23dof_patched_v2.xml`
- `g1_12dof_with_sensors.xml`
- `scene_23dof.xml`
- `config.py` (references 23DOF)

---

## unitree_rl_gym (Course Version)

### Location
`bitbucket.org/theconstructcore/g1_mujoco_tc/unitree_rl_gym`

### Structure
```
unitree_rl_gym/
├── legged_gym/           # Training environment
│   ├── configs/
│   ├── envs/
│   ├── scripts/
│   │   ├── train.py
│   │   └── play.py
│   └── utils/
├── deploy/               # Deployment scripts
│   └── deploy_mujoco/
│       ├── deploy_mujoco.py
│       ├── policy_to_lowcmd_*.py
│       └── configs/
│           └── g1_policy_only.yaml
├── resources/            # Robot models, policies
│   ├── robots/
│   │   └── g1_description/
│   │       ├── g1_23dof.urdf
│   │       ├── g1_23dof_rev_1_0.xml
│   │       ├── g1_29dof.xml
│   │       ├── g1_29dof_rev_1_0.xml
│   │       └── g1_29dof_lock_waist_rev_1_0.xml
│   └── pre_train/
│       └── g1/
│           └── motion.pt          # Pretrained policy
└── setup.py              # Installation
```

### Key Files for Course

| File | Purpose |
|------|---------|
| `legged_gym/scripts/train.py` | Train RL policy |
| `legged_gym/scripts/play.py` | Visualize trained policy |
| `deploy/deploy_mujoco/` | Sim2Sim deployment |
| `resources/pre_train/g1/motion.pt` | Pretrained motion policy |
| `resources/robots/g1_description/g1_29dof*.xml` | 29DOF models |

---

## Comparison with Official Repos

| Component | Official (GitHub) | Course (Bitbucket) |
|-----------|-------------------|-------------------|
| **unitree_mujoco** | `unitreerobotics/unitree_mujoco` | Modified for 23DOF |
| **unitree_rl_gym** | Not in official repo | Included in course |
| **G1 Models** | 29DOF standard | 23DOF patched |
| **Bridge Scripts** | Standard versions | Multiple versions |
| **Pretrained Policies** | None | Included |

---

## What to Use from Course

### From unitree_mujoco_tc
| File | Use When |
|------|----------|
| `simulate_python/unitree_mujoco_optim.py` | Need optimized simulator |
| `simulate_python/unitree_sdk2py_bridge_v4_wireless.py` | Need wireless bridge |
| `terrain_tool/` | Need terrain generation |
| `example/` | Course exercises |

### From unitree_rl_gym
| File | Use When |
|------|----------|
| `legged_gym/` | RL training |
| `deploy/deploy_mujoco/` | Sim2Sim deployment |
| `resources/pre_train/g1/motion.pt` | Pretrained policy |
| `resources/robots/g1_description/g1_29dof*.xml` | 29DOF models |

### Skip These (23DOF-specific)
| File | Reason |
|------|--------|
| All `g1_23dof*` files | Wrong DOF |
| `g1_12dof*` files | Wrong DOF |
| Course `config.py` | References 23DOF |

---

## Clone Commands

```bash
cd _vendor
git clone https://bitbucket.org/theconstructcore/g1_mujoco_tc/unitree_mujoco unitree_mujoco_tc
git clone https://bitbucket.org/theconstructcore/g1_mujoco_tc/unitree_rl_gym
```

---

*Last updated: 2026-08-13*