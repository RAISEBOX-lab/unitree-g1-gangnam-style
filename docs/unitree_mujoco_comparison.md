# unitree_mujoco Comparison: GitHub vs Bitbucket

## Summary

**Your current (GitHub):** `https://github.com/unitreerobotics/unitree_mujoco`  
**Course version (Bitbucket):** `https://bitbucket.org/theconstructcore/g1_mujoco_tc/unitree_mujoco`

---

## Key Differences

### Files Only in Bitbucket (Course)

| File | Purpose |
|------|---------|
| `mujoco-3.3.6-linux-x86_64.tar.gz` | MuJoCo binaries (13MB) |
| `simulate_python/unitree_mujoco_optim.py` | Optimized simulator |
| `simulate_python/unitree_mujoco_original.py` | Original simulator |
| `simulate_python/unitree_sdk2py_bridge_v2.py` | Bridge v2 |
| `simulate_python/unitree_sdk2py_bridge_v3.py` | Bridge v3 |
| `simulate_python/unitree_sdk2py_bridge_v4.py` | Bridge v4 |
| `simulate_python/unitree_sdk2py_bridge_v4_wireless.py` | Bridge v4 with wireless |
| `unitree_robots/g1/g1_23dof_patched_v2.xml` | Patched G1 23DOF model |
| `unitree_robots/g1/g1_12dof_with_sensors.xml` | G1 12DOF model |
| `unitree_robots/g1/meshes/torso_link_23dof_rev_1_0.STL` | Mesh file |

### Files Only in GitHub (Your Current)

| File | Purpose |
|------|---------|
| `unitree_robots/a2/` | A2 robot models |
| `unitree_robots/b2/` | B2 robot models |
| `unitree_robots/b2w/` | B2W robot models |
| `unitree_robots/go2/` | Go2 robot models |
| `unitree_robots/go2w/` | Go2W robot models |
| `unitree_robots/h1/` | H1 robot models |
| `unitree_robots/h1_2/` | H1-2 robot models |
| `unitree_robots/h2/` | H2 robot models |
| `unitree_robots/r1/` | R1 robot models |
| `terrain_tool/readme.md` | Terrain tool docs |

### Modified Files

| File | Difference |
|------|------------|
| `readme.md` | Different documentation |
| `readme_zh.md` | Different Chinese docs |
| `simulate/CMakeLists.txt` | Different build config |
| `simulate/config.yaml` | Different config |
| `simulate/src/main.cc` | Different main code |
| `simulate/src/unitree_sdk2_bridge.h` | Different bridge header |
| `simulate_python/config.py` | Different config |
| `simulate_python/unitree_mujoco.py` | Different simulator |
| `unitree_robots/g1/g1_23dof.xml` | Different model |
| `unitree_robots/g1/g1_29dof.xml` | Different model |
| `unitree_robots/g1/scene_23dof.xml` | Different scene |

---

## Key Findings

### 1. Bitbucket Has Course-Specific Files
- Multiple bridge versions (v2, v3, v4, v4_wireless)
- Patched G1 models
- Optimized simulator versions

### 2. GitHub Has More Robots
- Your version has A2, B2, B2W, Go2, Go2W, H1, H1_2, H2, R1
- Bitbucket version has fewer robots (likely G1-focused for course)

### 3. Core Simulator Differs
- `unitree_mujoco.py` is different
- Bridge files are different
- Config files are different

### 4. Missing in Your Setup
- `unitree_rl_gym/` - **NOT in either repo as submodule**
- Course uses `unitree_rl_gym` from same Bitbucket repo

---

## Recommendation

### Option 1: Use Current GitHub Version
- Has more robot models
- More complete
- May work fine for course

### Option 2: Switch to Bitbucket Course Version
- Has course-specific patches
- Has multiple bridge versions
- May be required for some exercises

### Option 3: Hybrid Approach
- Keep GitHub `unitree_mujoco` (more robots)
- Copy course-specific files from Bitbucket:
  - `simulate_python/unitree_sdk2py_bridge_v4_wireless.py`
  - `unitree_robots/g1/g1_23dof_patched_v2.xml`
  - `unitree_robots/g1/g1_12dof_with_sensors.xml`

---

## Next: unitree_rl_gym

**Status:** You DON'T have this.

**Location:** `https://bitbucket.org/theconstructcore/g1_mujoco_tc/unitree_rl_gym`

**Contains:**
- `legged_gym/` - Training environment
- `deploy/` - Deployment scripts
- `resources/` - Robot configs
- `setup.py` - Installation

**Action:** Clone this from Bitbucket.

---

*Last updated: 2026-08-13*