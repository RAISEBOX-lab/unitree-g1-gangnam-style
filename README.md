# Unitree G1 Gangnam Style

## ⚠️ CRITICAL SAFETY RULE
**NEVER touch the real robot without first testing everything in simulation.**
- All code, scripts, and configurations MUST be tested in MuJoCo simulation first
- Only after simulator validation can you proceed to real robot

## Project Objective
Implement Gangnam Style dance choreography on Unitree G1 robot using official course repositories.

## Quick Start

```bash
# Activate environment
source g1/bin/activate

# Launch simulation
cd _vendor/unitree_mujoco_extras && python3 launch_unitree_v3.py
```

See [`PROJECT_GUIDELINES.md`](PROJECT_GUIDELINES.md) for full workflow and setup.

## Verification Commands

```bash
# Check Python environment
source g1/bin/activate && python3 -c "import unitree_sdk2py; import mujoco; print('✅ venv OK')"

# Check simulation files
ls _vendor/unitree_mujoco/simulate_python/unitree_mujoco.py

# Check RL policy
ls _vendor/unitree_rl_gym/deploy/pre_train/g1/motion.pt

# Check gamepad
ls -la /dev/input/js*
```

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
- **RL Policy:** Located at `_vendor/unitree_rl_gym/deploy/pre_train/g1/motion.pt`
- **Course Progress:** Ready to start Unit 3 SDK exercises
- **29DOF Models:** Available in `_vendor/unitree_rl_gym/resources/robots/g1_description/g1_29dof*.xml`

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

---

*Last updated: 2026-08-14*
