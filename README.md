# Unitree G1 Gangnam Style

## ⚠️ CRITICAL SAFETY RULE
**NEVER touch the real robot without first testing everything in simulation.**
- All code, scripts, and configurations MUST be tested in MuJoCo simulation first
- Only after simulator validation can you proceed to real robot

## Project Objective
Implement Gangnam Style dance choreography on Unitree G1 robot using official course repositories.

## Project Layout

```
/home/raisebox/Projects/unitree-g1-gangnam-style/
├── _vendor/                     # Course dependencies (DO NOT MODIFY unless fixing)
│   ├── unitree_sdk2_python/    # Python SDK for DDS communication
│   ├── unitree_mujoco/          # MuJoCo simulator (29DOF G1)
│   ├── unitree_mujoco_extras/   # RPC bridge, gamepad controller
│   ├── unitree_mujoco_tc/       # Course repo (23DOF)
│   └── unitree_rl_gym/          # RL training/deployment
├── g1/                          # Python virtual environment (activate with `source g1/bin/activate`)
├── docs/                        # Analysis documents
├── scripts/                     # User scripts (exercise implementations)
├── PROJECT_GUIDELINES.md        # 4-phase workflow
└── BEHAVIOR.md                  # Interaction guidelines
```

## Key Constraints

1. **Simulation First** - All work must be verified in MuJoCo before real robot
2. **Follow Course Order** - Unit 3 (SDK exercises) → Unit 4-5 (RL) → Gangnam Style
3. **No Unverified Changes** - Propose before executing destructive operations
4. **Document Everything** - Save analysis outputs as files in `docs/`

## Environment Setup

### Python Environment
```bash
cd /home/raisebox/Projects/unitree-g1-gangnam-style
source g1/bin/activate
```

### Launch Simulation
```bash
cd /home/raisebox/Projects/unitree-g1-gangnam-style/_vendor/unitree_mujoco_extras
python3 launch_unitree_v3.py
```

This launches 3 processes:
1. MuJoCo simulator with G1 robot
2. Odom/Mode/State bridge
3. RL policy to LowCmd bridge

### Manual Simulation (no RL policy)
```bash
cd /home/raisebox/Projects/unitree-g1-gangnam-style/_vendor/unitree_mujoco/simulate_python
/home/raisebox/Projects/unitree-g1-gangnam-style/g1/bin/python3 unitree_mujoco.py
```

## Config Path Issue (KNOWN BUG)

**Problem:** Config files have hardcoded paths pointing to `/home/simulations/` instead of your project location.

**Affected files:**
- `_vendor/unitree_rl_gym/deploy/deploy_mujoco/configs/g1_policy_only.yaml`
- `_vendor/unitree_rl_gym/deploy/deploy_mujoco/configs/g1.yaml`

**Fix:** Update `policy_path` and `xml_path` to:
```
/home/raisebox/Projects/unitree-g1-gangnam-style/_vendor/...
```

**Detection mechanism:** `launch_unitree_v3.py` (lines 26-46) auto-detects base directory by checking:
1. `/home/simulations`
2. `/home/user`
3. Script's parent directory (your `_vendor/`)

## Common Commands

### Check gamepad
```bash
ls -la /dev/input/js*
sudo chmod 666 /dev/input/js0  # If permission denied
```

### Test simulation without RL policy
```bash
cd _vendor/unitree_mujoco/simulate_python
/home/raisebox/Projects/unitree-g1-gangnam-style/g1/bin/python3 unitree_mujoco.py
```

### View logs after crash
```bash
tail -f _vendor/unitree_rl_gym/policy_to_lowcmd.log
tail -f _vendor/unitree_mujoco/simulate_python/unitree_mujoco.log
```

## Current State

- **Simulation:** Working (physics verified, graphics issues resolved)
- **Gamepad:** Detected (ZEROPLUS P4) but may need permissions
- **RL Policy:** Exists at `_vendor/unitree_rl_gym/deploy/pre_train/g1/motion.pt`
- **Config paths:** UPDATED to correct paths (Aug 14)
- **Course Progress:** Ready to start Unit 3 SDK exercises

## DO NOT

- ❌ Modify robot code without simulation verification
- ❌ Change hardcoded config paths without user confirmation
- ❌ Delete files or repos (catastrophic deletion happened before)
- ❌ Execute commands without user running them (trust issue)

## DO

- ✅ Test everything in simulation first
- ✅ Save analysis outputs as files in `docs/`
- ✅ Follow the 4-phase workflow in `PROJECT_GUIDELINES.md`
- ✅ Ask before making destructive changes
- ✅ Run verification commands before proceeding

## Troubleshooting

**"No gamepad detected"**
- Gamepad is optional - simulation works without it
- Use Ctrl+click to drag robot in viewer
- Check: `ls -la /dev/input/js*`

**"video system not initialized"**
- Graphics/display issue, not physics
- Physics works without viewer
- Try switching from Wayland to X11 at login

**"FileNotFoundError: motion.pt"**
- Config has wrong path
- Update `policy_path` in config to use your project path

**"GLXBadDrawable"**
- NVIDIA driver/OpenGL issue
- Switch to X11 or use virtual framebuffer

## User Preferences

- User runs all commands themselves (agent provides commands only)
- User has 29DOF G1 robot
- Keyboard layout: pt-PT
- Tailscale: Working (raisebox-spark:8000 for vLLM)

---

*Last updated: 2026-08-14*
