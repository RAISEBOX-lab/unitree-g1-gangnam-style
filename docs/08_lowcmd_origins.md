# rt/lowcmd Origins - Full Path from Source to Publisher

## Current Active Publisher (Your Simulation)

### **Policy Script: `policy_to_lowcmd_v11b_remote_trigger_dual_modes_with_rpc_arm_overlay.py`**

**Location:**
```
_vendor/unitree_rl_gym/deploy/deploy_mujoco/policy_to_lowcmd_v11b_remote_trigger_dual_modes_with_rpc_arm_overlay.py
```

**Process:** Running (PID 11489)
```bash
python3 policy_to_lowcmd_v11b...py --iface lo --domain 1 --service sport --also_service unitree_loco_api
```

**Code (Line 184):**
```python
pub = ChannelPublisher("rt/lowcmd", LowCmd); pub.Init()
```

**Publishs at:** 500Hz (every 2ms)

**What it does:**
1. Receives FSM commands via sport API (FSM=500/801 → AI mode)
2. Receives state feedback from rt/lowstate
3. Runs RL policy inference
4. Publishes motor commands to rt/lowcmd

---

## Other rt/lowcmd Publishers (Not Running)

### 1. **G1 Poses Scripts** (Manual Pose Control)

**Files:**
- `g1_poses.py`
- `g1_poses_v2.py`

**Location:**
```
_vendor/unitree_mujoco_extras/g1_poses.py
```

**Code (Line 170-171):**
```python
self.lowcmd_pub = ChannelPublisher("rt/lowcmd", LowCmd_)
self.lowcmd_pub.Init()
```

**What it does:**
- Manually sets joint positions for G1 robot
- Used for testing poses, not walking
- **Status:** Not running

---

### 2. **Low Level Examples** (SDK Examples)

**Files:**
- `_vendor/unitree_sdk2_python/example/g1/low_level/g1_low_level_example.py`
- `_vendor/unitree_mujoco/example/python/stand_go2.py`
- `_vendor/unitree_mujoco_tc/example/python/stand_go2.py`

**Code (Line 101):**
```python
self.lowcmd_publisher_ = ChannelPublisher("rt/lowcmd", LowCmd_)
```

**What it does:**
- Official Unitree SDK examples
- Sends PD commands to motors
- Used for learning SDK basics
- **Status:** Not running

---

### 3. **Arm SDK Bridge** (Arm Overlay)

**Files:**
- `arm_sdk_bridge.py`
- `arm_sdk_overlay_bridge.py`
- `arm_sdk_bridge_overlay_v5.py`
- `arm_sdk_bridge_overlay_v6_safe.py`
- `arm_sdk_bridge_overlay_v7_guarded.py`

**Location:**
```
_vendor/unitree_mujoco_extras/arm_sdk_bridge.py
```

**Code (Line 44):**
```python
TOPIC_LOWCMD = "rt/lowcmd"
```

**What it does:**
- Subscribes to rt/lowcmd_base (AI baseline)
- Subscribes to rt/arm_sdk (arm commands)
- Merges arm commands onto leg commands
- Publishes final combined command to rt/lowcmd
- **Status:** Not running (your policy script already does arm overlay)

---

### 4. **RPC Server Bridge** (Loco RPC to LowCmd)

**Files:**
- `loco_rpc_server_bridge_v3_ai_base_split.py`
- `loco_rpc_server_bridge_v3_ai_base_split_bk.py`

**Location:**
```
_vendor/unitree_mujoco_extras/loco_rpc_server_bridge_v3_ai_base_split.py
```

**Code (Line 256-257):**
```python
self.pub_lowcmd      = ChannelPublisher(TOPIC_LOWCMD, LowCmd)
self.pub_lowcmd_base = ChannelPublisher(TOPIC_LOWCMD_BASE, LowCmd)
```

**What it does:**
- Receives RPC commands for locomotion
- Publishes to rt/lowcmd (final) and rt/lowcmd_base (AI baseline)
- **Status:** Not running (your policy script handles this)

---

## Complete Path: Origin → MuJoCo

### **Your Current Setup (Active)**

```
1. Policy Script (policy_to_lowcmd_v11b...)
   │
   │ Line 184: pub = ChannelPublisher("rt/lowcmd", LowCmd)
   │
   ▼
2. DDS Middleware (rt/lowcmd topic)
   │
   │ Publish/Subscribe pattern
   │
   ▼
3. UnitreeSdk2Bridge (unitree_mujoco.py)
   │
   │ Line 355: OnLowCmd(data) - receives message
   │
   ▼
4. MuJoCo Physics Engine
   │
   │ Applies motor commands
   │ mj_step(model, data)
   │
   ▼
5. New State (joint positions, velocities)
   │
   ▼
6. UnitreeSdk2Bridge → rt/lowstate
   │
   ▼
7. Back to Policy Script (for next action)
```

---

## Timeline of rt/lowcmd Publishing

### **When FSM=500/801 (AI Mode)**

| Time | Action | Publisher |
|------|--------|-----------|
| T=0s | FSM received | Policy Script |
| T=0-0.7s | Warmup: standing pose | Policy Script (500Hz) |
| T>0.7s | RL policy actions | Policy Script (500Hz) |

### **When FSM=4 (LockedStanding)**

| Time | Action | Publisher |
|------|--------|-----------|
| T=0s | FSM received | Policy Script |
| T=0-2s | Blend to locked pose | Policy Script (500Hz) |
| T>2s | Hold locked pose | Policy Script (500Hz) |

### **When FSM=1 (Damping)**

| Time | Action | Publisher |
|------|--------|-----------|
| T=0s | FSM received | Policy Script |
| T>0.3s | Damping mode | Policy Script (500Hz) |

---

## Key Points

1. **Only ONE script should publish to rt/lowcmd at a time**
   - Multiple publishers = conflicting commands = unpredictable behavior

2. **Your current publisher:** `policy_to_lowcmd_v11b...`
   - Handles both legs AND arms (arm overlay built-in)
   - Receives RPC commands (FSM, sport API)
   - Publishes at 500Hz

3. **Bridge receives rt/lowcmd:**
   - `unitree_mujoco.py` → `UnitreeSdk2Bridge`
   - Applies to MuJoCo motors

4. **State feedback loop:**
   - MuJoCo → `rt/lowstate` → Policy Script
   - Policy uses state for next action