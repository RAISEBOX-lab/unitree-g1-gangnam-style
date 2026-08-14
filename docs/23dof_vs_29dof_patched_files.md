# 23DOF vs 29DOF G1 - Patched Files Analysis

## G1 Versions

| Version | DOF | Description |
|---------|-----|-------------|
| **G1-23DOF** | 23 | 23 degrees of freedom (no wrist joints) |
| **G1-29DOF** | 29 | 29 degrees of freedom (with wrist joints) |

**Your Setup:** G1-29DOF  
**Course Setup:** G1-23DOF (patched)

---

## Files Patched for 23DOF (DO NOT WANT)

These files were modified specifically for the 23DOF model. **Skip these** since you use 29DOF.

### Robot Models
| File | Purpose | Skip? |
|------|---------|-------|
| `unitree_robots/g1/g1_23dof.xml` | 23DOF robot model | ✅ SKIP |
| `unitree_robots/g1/g1_23dof_patched_v2.xml` | Patched 23DOF model | ✅ SKIP |
| `unitree_robots/g1/g1_12dof_with_sensors.xml` | 12DOF model | ✅ SKIP |
| `unitree_robots/g1/scene_23dof.xml` | 23DOF scene | ✅ SKIP |
| `unitree_robots/g1/meshes/torso_link_23dof_rev_1_0.STL` | 23DOF mesh | ✅ SKIP |

### Config Files (23DOF-specific)
| File | Purpose | Skip? |
|------|---------|-------|
| `simulate_python/config.py` | Course config (may reference 23DOF) | ⚠️ CHECK |

---

## Files to Copy (Not 23DOF-specific)

These are course exercises, examples, and tools. **Copy these as needed.**

### Simulator Versions
| File | Purpose | Copy? |
|------|---------|-------|
| `simulate_python/unitree_mujoco_optim.py` | Optimized simulator | ✅ YES |
| `simulate_python/unitree_mujoco_original.py` | Original simulator | ✅ YES |

### Bridge Versions (Different Implementations)
| File | Purpose | Copy? |
|------|---------|-------|
| `simulate_python/unitree_sdk2py_bridge_v2.py` | Bridge v2 | ✅ YES |
| `simulate_python/unitree_sdk2py_bridge_v3.py` | Bridge v3 | ✅ YES |
| `simulate_python/unitree_sdk2py_bridge_v4.py` | Bridge v4 | ✅ YES |
| `simulate_python/unitree_sdk2py_bridge_v4_wireless.py` | Bridge v4 + wireless | ✅ YES |

### Build Files
| File | Purpose | Copy? |
|------|---------|-------|
| `simulate/build/` | Compiled binaries | ⚠️ Rebuild |
| `simulate/CMakeLists.txt` | Build config | ⚠️ Check |
| `simulate/config.yaml` | Simulator config | ⚠️ Check |
| `simulate/src/main.cc` | Main code | ⚠️ Check |
| `simulate/src/unitree_sdk2_bridge.h` | Bridge header | ⚠️ Check |

### Documentation
| File | Purpose | Copy? |
|------|---------|-------|
| `readme.md` | Documentation | ✅ Reference |
| `readme_zh.md` | Chinese docs | ✅ Reference |
| `doc/readme.md` | More docs | ✅ Reference |

### Other
| File | Purpose | Copy? |
|------|---------|-------|
| `mujoco-3.3.6-linux-x86_64.tar.gz` | MuJoCo binaries | ⚠️ Check version |
| `terrain_tool/` | Terrain generation | ✅ YES |

---

## What You Already Have (29DOF)

Your current `unitree_mujoco` already has:
- ✅ `g1_29dof.xml` - Your 29DOF model
- ✅ `g1_29dof scene` - Your scene
- ✅ All robot models (Go2, H1, B2, etc.)
- ✅ Working bridge

---

## Proposed Setup

### Directory Structure
```
_vendor/
├── unitree_sdk2_python/          # ✅ Keep (GitHub)
├── unitree_mujoco/               # ✅ Keep (GitHub, 29DOF)
│   └── (your current setup)
├── unitree_mujoco_tc/            # 📚 New (Bitbucket course)
│   └── (clone from Bitbucket)
└── unitree_rl_gym/               # 📚 New (Bitbucket course)
    └── (clone from Bitbucket)
```

### Workflow
1. **Keep current setup** - Your 29DOF works
2. **Clone course repos** - For reference and exercises
3. **Copy non-23DOF files** - As needed for exercises
4. **Skip 23DOF files** - Use your 29DOF models

---

## Files to Copy (When Needed)

### From unitree_mujoco_tc/
| File | When to Copy |
|------|--------------|
| `simulate_python/unitree_mujoco_optim.py` | If you need optimized simulator |
| `simulate_python/unitree_sdk2py_bridge_v4_wireless.py` | If you need wireless bridge |
| `terrain_tool/` | If you need terrain generation |
| `example/` | Course examples |

### From unitree_rl_gym/
| File | When to Copy |
|------|--------------|
| `legged_gym/` | For RL training |
| `deploy/` | For Sim2Real deployment |
| `resources/` | Robot configs |

---

## What About config.py?

**Check first:** The course `config.py` may reference 23DOF.

**Your config.py** (29DOF):
```python
ROBOT = "g1"
ROBOT_SCENE = "../unitree_robots/g1/scene_29dof.xml"  # Your 29DOF
```

**Course config.py** (23DOF):
```python
ROBOT = "g1"
ROBOT_SCENE = "../unitree_robots/g1/scene_23dof.xml"  # Their 23DOF
```

**Action:** Keep your `config.py`, don't copy theirs.

---

## Next Steps

1. **Clone course repos:**
   ```bash
   cd _vendor
   git clone https://bitbucket.org/theconstructcore/g1_mujoco_tc/unitree_mujoco unitree_mujoco_tc
   git clone https://bitbucket.org/theconstructcore/g1_mujoco_tc/unitree_rl_gym
   ```

2. **When doing exercises:**
   - Copy specific files as needed
   - Skip 23DOF-specific files
   - Use your 29DOF models

3. **Document what you copy:**
   - Track which files work with 29DOF
   - Note any modifications needed

---

*Last updated: 2026-08-13*