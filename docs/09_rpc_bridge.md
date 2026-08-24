# RPC Bridge - Complete Documentation

## What It Does

The **RPC Bridge** (`loco_rpc_server_bridge.py`) is a **request-response server** that:

1. **Receives RPC commands** (FSM changes, velocity, etc.) via DDS
2. **Translates commands** to motor control actions
3. **Streams motor commands** to `rt/lowcmd` at 500Hz
4. **Sends acknowledgments** back to the caller

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    RPC Bridge                                │
│  (loco_rpc_server_bridge.py)                                 │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ RPC Subscriber│→ │ Request      │→ │ Action       │       │
│  │ (sport API)   │  │ Handler      │  │ Methods      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                            │                   │              │
│                            ▼                   ▼              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ RPC Publisher│← │ Response     │  │ Stream Thread│       │
│  │ (sport API)  │  │ Builder      │  │ (500Hz)      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                            │                   │              │
│                            ▼                   ▼              │
│                    ┌──────────────┐  ┌──────────────┐       │
│                    │ RPC Response │  │ LowCmd       │       │
│                    │ (ACK)        │  │ Publisher    │       │
│                    └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## Inputs

### 1. **RPC Requests** (sport API)

**Topic:** `rt/sport/api/request` (RECV channel)

**Message Type:** `Request_` (unitree_api)

**Fields:**
```python
header:
  identity:
    id: int          # Request ID
    api_id: int      # API command ID
parameter: str       # JSON string with command data
```

**Supported API IDs:**

| API ID | Name | Data Format | Action |
|--------|------|-------------|--------|
| 1 | `LOCO_SET_FSM_ID` | `{"data": fsm_id}` | Set FSM state |
| 2 | `LOCO_SET_BALANCE_MODE` | `{"data": mode}` | Enable/disable balance |
| 3 | `LOCO_SET_STAND_HEIGHT` | `{"data": height}` | Set standing height |
| 4 | `LOCO_SET_VELOCITY` | `{"velocity": [vx, vy, wz], "duration": T}` | Set walking velocity |
| 5 | `LOCO_SET_ARM_TASK` | `{"data": task}` | Set arm task |

**Example:**
```python
# From CLI: SetFsmId(500)
req = Request()
req.header.identity.id = 123
req.header.identity.api_id = 1  # LOCO_SET_FSM_ID
req.parameter = '{"data": 500}'
```

### 2. **LowState Feedback** (rt/lowstate)

**Topic:** `rt/lowstate`

**Message Type:** `LowState_` (unitree_hg)

**Purpose:** Capture current robot pose for actions like `DampHold`

**Fields Used:**
```python
motor_state[0..28].q  # Joint positions
motor_state[0..28].dq # Joint velocities
imu.quaternion        # Orientation
```

---

## Outputs

### 1. **LowCmd Commands** (rt/lowcmd)

**Topic:** `rt/lowcmd`

**Message Type:** `LowCmd_` (unitree_hg)

**Frequency:** 500Hz (every 2ms)

**Fields:**
```python
motor_cmd[0..34]:
  mode: int           # 1 = PD control
  q: float            # Target position
  dq: float           # Target velocity (usually 0)
  kp: float           # Proportional gain
  kd: float           # Derivative gain
  tau: float          # Feedforward torque
```

**Example (LockedStanding):**
```python
cmd = LowCmd_default()
for i in range(29):
    cmd.motor_cmd[i].mode = 1
    cmd.motor_cmd[i].q = 0.0  # Standing pose
    cmd.motor_cmd[i].kp = 60.0 if i < 12 else 40.0
    cmd.motor_cmd[i].kd = 1.0 if i < 12 else 1.0
    cmd.motor_cmd[i].tau = 0.0
```

### 2. **RPC Responses** (sport API)

**Topic:** `rt/sport/api/response` (SEND channel)

**Message Type:** `Response_` (unitree_api)

**Fields:**
```python
header:
  identity:
    id: int           # Request ID (echoed)
    api_id: int       # API command ID (echoed)
  status:
    code: int         # 0 = success, non-zero = error
    message: str      # Status message
data: str            # Response data (optional)
```

**Example:**
```python
# Response to SetFsmId(500)
rsp = Response()
rsp.header.identity.id = 123
rsp.header.identity.api_id = 1
rsp.header.status.code = 0
rsp.header.status.message = "RunningMode stub (fsm=500)"
rsp.data = ""
```

---

## Action Methods

### 1. **ZeroTorque** (FSM=0)

**Purpose:** Disable all motor resistance (robot falls)

**Implementation:**
```python
def action_zero_torque(self):
    q = [0.0] * 29
    cmd = _make_lowcmd(q, 0.0, 0.0, 0.0)  # kp=0, kd=0
    self._set_stream_cmd(cmd, cancel_damp=True)
```

**Output:** All motors with `kp=0, kd=0` → no resistance

---

### 2. **DampHold** (FSM=1)

**Purpose:** Hold current pose with soft resistance

**Implementation:**
```python
def action_damp_hold(self, kp=12.0, kd=6.0, warmup_s=0.3):
    qt = _capture_q(self._last_lowstate, 29)  # Current pose
    base = _make_lowcmd(qt, 0.0, 0.0, 0.0)
    
    with self._stream_lock:
        self._stream_cmd = base
        self._damp_active = True
        self._damp_kp = kp
        self._damp_qt = qt[:]
        self._damp_end_t = time.time() + warmup_s
```

**Output:** Motor commands with `kp=12, kd=6` ramping over 0.3s

---

### 3. **LockedStanding** (FSM=4)

**Purpose:** Lock robot in standing pose with high gains

**Implementation:**
```python
def action_locked_standing(self):
    q = [0.0] * 29
    q[LeftElbow] = -pi/2
    q[RightElbow] = -pi/2
    
    kp = Kp_DEFAULT_29[:]
    kd = Kd_DEFAULT_29[:]
    
    # Stronger leg/waist gains
    for i in range(15):  # Legs + waist
        kp[i] = max(kp[i], 120.0)
        kd[i] = max(kd[i], 3.0)
    
    cmd = _make_lowcmd(q, kp, kd, 0.0)
    self._set_stream_cmd(cmd, cancel_damp=True)
```

**Output:** Motor commands with `kp=120, kd=3` (legs/waist)

---

### 4. **RunningMode** (FSM=500/801)

**Purpose:** Enable AI walking mode (stub - no action)

**Implementation:**
```python
def action_running_mode(self):
    print("[RUN] StartWalkingModel() — stub (no motion yet)")
```

**Output:** No motor commands (does nothing)

**Note:** Your actual RL policy (`policy_to_lowcmd_v11b...`) handles this!

---

## Stream Thread

### Purpose

Keeps publishing motor commands at 500Hz even when no RPC commands are received.

### Implementation

```python
def _stream_tick(self):
    """Called every 2ms (500Hz)"""
    cmd = None
    damp_active = False
    
    with self._stream_lock:
        cmd = self._stream_cmd
        damp_active = self._damp_active
    
    # If DAMP mode, ramp kp/kd smoothly
    if damp_active and cmd is not None:
        alpha = calculate_progress()
        use_kp = self._damp_kp * alpha
        use_kd = self._damp_kd * alpha
        
        for i in range(29):
            cmd.motor_cmd[i].kp = use_kp
            cmd.motor_cmd[i].kd = use_kd
    
    # Publish
    if cmd is not None:
        cmd.crc = _crc.Crc(cmd)
        self.pub_lowcmd.Write(cmd)
```

### Key Behaviors

1. **Always publishes** (even if no new commands)
2. **Maintains last command** in stream
3. **Ramps gains** during DAMP warmup
4. **Thread-safe** with lock

---

## Request Handler Flow

```
1. Receive RPC request (sport API)
   ↓
2. Parse api_id and parameter (JSON)
   ↓
3. Select action method based on api_id
   ↓
4. Execute action (e.g., action_locked_standing())
   ↓
5. Update stream command
   ↓
6. Build response message
   ↓
7. Publish response (sport API)
   ↓
8. Stream thread continues publishing motor commands
```

---

## State Feedback Integration

### Why It Matters

The bridge subscribes to `rt/lowstate` to:

1. **Capture current pose** for DampHold
2. **Maintain state** during stream
3. **Enable smooth transitions**

### Implementation

```python
# Subscribe to lowstate
self.sub_lowstate = ChannelSubscriber("rt/lowstate", LowState_)
self.sub_lowstate.Init(lambda msg: setattr(self, "_last_lowstate", msg), 50)

# Capture pose
def action_damp_hold(self, kp=12.0, kd=6.0, warmup_s=0.3):
    qt = _capture_q(self._last_lowstate, 29)  # Current pose
    # ... use qt as target positions
```

---

## Key Differences from Policy Script

| Feature | RPC Bridge | Policy Script |
|---------|------------|---------------|
| **Purpose** | RPC server, command translation | RL policy, motion generation |
| **FSM=500** | Stub (no action) | Full RL walking policy |
| **FSM=4** | LockedStanding pose | LockedStanding with blend |
| **FSM=1** | DampHold with warmup | DampHold with warmup |
| **Output** | PD commands | PD commands + RL actions |
| **Frequency** | 500Hz stream | 500Hz stream |
| **State** | Captures pose | Full observation pack |

---

## Current Status in Your Simulation

### **NOT RUNNING**

**Running instead:** `policy_to_lowcmd_v11b_remote_trigger_dual_modes_with_rpc_arm_overlay.py`

**Why:** The policy script handles both RPC commands AND RL policy in one process.

### **When RPC Bridge IS Used**

1. **Without RL policy** - Only basic FSM commands
2. **Testing RPC layer** - Verify DDS communication
3. **Simple pose control** - Standing, damping, zero torque

---

## Diagram Summary

**See `docs/09_rpc_bridge_flow.mmd`** for visual flow diagram.

**Key Flow:**
```
CLI → RPC Request → Bridge Handler → Action → Stream → rt/lowcmd → MuJoCo
                                                    ↓
                                              rt/lowstate (feedback)
                                                    ↓
                                               Bridge (pose capture)
```