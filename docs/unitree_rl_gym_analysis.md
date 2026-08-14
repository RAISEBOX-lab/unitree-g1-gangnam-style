# unitree_rl_gym - 23DOF vs 29DOF Analysis

## Repository Location
**Bitbucket:** `https://bitbucket.org/theconstructcore/g1_mujoco_tc/unitree_rl_gym`

## G1 Models in unitree_rl_gym

The repo contains **BOTH** 23DOF and 29DOF models - **not patched for 23DOF only**.

### Available Models

| Model | DOF | Location |
|-------|-----|----------|
| `g1_23dof.urdf` | 23 | `resources/robots/g1_description/` |
| `g1_23dof_rev_1_0.xml` | 23 | `resources/robots/g1_description/` |
| `g1_29dof.xml` | 29 | `resources/robots/g1_description/` |
| `g1_29dof_lock_waist_rev_1_0.xml` | 29 | `resources/robots/g1_description/` |
| `g1_29dof_with_hand.urdf` | 29+hand | `resources/robots/g1_description/` |
| `g1_29dof_rev_1_0.xml` | 29 | `resources/robots/g1_description/` |
| `g1_12dof.xml` | 12 | `resources/robots/g1_description/` |

---

## Files to Use (29DOF Compatible)

### Robot Models
| File | Use With |
|------|----------|
| `g1_29dof.xml` | ✅ Your 29DOF |
| `g1_29dof_rev_1_0.xml` | ✅ Your 29DOF |
| `g1_29dof_lock_waist_rev_1_0.xml` | ✅ Your 29DOF (waist locked) |

### Config Files
| File | Use With |
|------|----------|
| `deploy/deploy_mujoco/configs/g1_policy_only.yaml` | ✅ Generic |
| `legged_gym/scripts/` | ✅ Generic |
| `resources/` | ✅ Generic |

---

## Files to Skip (23DOF Only)

| File | Reason |
|------|--------|
| `g1_23dof.urdf` | Wrong DOF |
| `g1_23dof_rev_1_0.xml` | Wrong DOF |
| `g1_12dof.xml` | Wrong DOF |

---

## Comparison: unitree_mujoco_tc vs unitree_rl_gym

| Component | unitree_mujoco_tc | unitree_rl_gym |
|-----------|-------------------|----------------|
| **Purpose** | MuJoCo simulator | RL training environment |
| **G1 Models** | 23DOF only | Both 23DOF and 29DOF |
| **Bridge Files** | Multiple versions | None |
| **Training** | No | Yes (Isaac Gym) |
| **Deployment** | No | Yes (Sim2Real) |

---

## Key Finding

**unitree_rl_gym has 29DOF models!**

This means:
- ✅ You can use `unitree_rl_gym` with your 29DOF setup
- ✅ No patching needed for RL training
- ✅ Use `g1_29dof.xml` or `g1_29dof_rev_1_0.xml`

---

## Files to Copy from unitree_rl_gym

### When Needed
| File | Purpose |
|------|---------|
| `legged_gym/` | RL training environment |
| `deploy/` | Sim2Real deployment scripts |
| `resources/robots/g1_description/g1_29dof*.xml` | 29DOF models |
| `setup.py` | Installation |

### Skip These
| File | Reason |
|------|--------|
| `resources/robots/g1_description/g1_23dof*` | Wrong DOF |
| `resources/robots/g1_description/g1_12dof*` | Wrong DOF |

---

## Recommendation

**Use unitree_rl_gym as-is** (it has 29DOF models).

**No need to patch anything** for your 29DOF setup.

---

*Last updated: 2026-08-13*