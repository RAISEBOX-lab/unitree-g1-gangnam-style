# Unitree G1 Gangnam Style - System Architecture

## Communication Flow Diagram

```mermaid
flowchart TB
    subgraph "User Input Layer"
        GP[Gamepad Controller]
        CLI[CLI Scripts]
    end

    subgraph "Python Application Layer"
        RPC[RPC Bridge<br/>unitree_mujoco_extras]
        LOC[LocoClient<br/>SDK High-Level]
        LOW[LowLevel Client<br/>SDK Motor Control]
        FSM[State Machine<br/>Manager]
    end

    subgraph "DDS Communication Layer"
        PUB[DDS Publisher]
        SUB[DDS Subscriber]
    end

    subgraph "Robot/Simulation Layer"
        SIM[MuJoCo Simulator<br/>29DOF Model]
        ROB[Real Robot<br/>G1 29DOF]
    end

    subgraph "Feedback Loop"
        IMU[IMU State]
        MOT[Motor States]
        BMS[BMS State]
    end

    %% User inputs
    GP -->|Joystick/Buttons| RPC
    CLI -->|FSM Commands| FSM
    CLI -->|Motor Commands| LOW

    %% State Machine flow
    FSM -->|Set FSM ID| RPC
    FSM -->|Mode Selection| LOC

    %% RPC Bridge handles simulation control
    RPC -->|Physics Commands| SIM

    %% SDK clients send via DDS
    RPC -->|Publish| PUB
    LOC -->|Publish| PUB
    LOW -->|Publish rt/lowcmd| PUB

    %% DDS topics
    PUB -->|rt/wirelesscontroller| SIM
    PUB -->|rt/lowcmd| SIM
    PUB -->|rt/lowcmd| ROB

    %% Simulation/Robot feedback
    SIM -->|Subscribe rt/lowstate| SUB
    ROB -->|Subscribe rt/lowstate| SUB

    %% Feedback to application
    SUB -->|rt/lowstate| RPC
    SUB -->|rt/lowstate| LOC
    SUB -->|rt/lowstate| LOW

    %% Extract state components
    SUB --> IMU
    SUB --> MOT
    SUB --> BMS

    %% State feedback loop
    IMU -->|Orientation/Angular Vel| FSM
    MOT -->|Joint Positions/Velocities| FSM
    BMS -->|Battery Status| FSM

    %% RL Policy integration
    POL[RL Policy<br/>motion.pt] -.->|Actions| RPC
    POL -.->|Actions| LOC

    %% Style definitions
    style RPC fill:#e1f5ff
    style LOC fill:#e1f5ff
    style LOW fill:#e1f5ff
    style FSM fill:#fff4e6
    style PUB fill:#f0f0f0
    style SUB fill:#f0f0f0
    style SIM fill:#e8f5e9
    style ROB fill:#e8f5e9
    style POL fill:#fce4ec
```

## State Machine Transitions

```mermaid
stateDiagram-v2
    [*] --> ZeroTorque
    ZeroTorque --> Damping: User Command
    Damping --> LockedStanding: User Command
    LockedStanding --> PreWalk: User Command
    PreWalk --> WalkMotion: Balance Enabled
    WalkMotion --> PreWalk: Disable Balance
    PreWalk --> LockedStanding: User Command
    LockedStanding --> Damping: User Command
    Damping --> ZeroTorque: User Command
    WalkMotion --> [*]: Emergency Stop
    ZeroTorque --> [*]: Robot Falls

    note right of ZeroTorque
        FSM ID: 0
        Risk: DANGEROUS
        Robot falls, no resistance
    end note

    note right of Damping
        FSM ID: 1
        Risk: Safe
        Joints have resistance
    end note

    note right of LockedStanding
        FSM ID: 2
        Risk: Safe
        Robot locked in place
    end note

    note right of PreWalk
        FSM ID: 4
        Risk: Safe
        Preparing for motion
    end note

    note right of WalkMotion
        FSM ID: 500/801
        Risk: Balance enabled
        AI walking policy active
    end note
```

## DDS Topic Architecture

```mermaid
graph LR
    subgraph "Publishers"
        RPC_P[RPC Bridge]
        SDK_P[SDK Clients]
    end

    subgraph "DDS Topics"
        WCT[rt/wirelesscontroller]
        LOWCMD[rt/lowcmd]
        ARM_SDK[rt/arm_sdk]
    end

    subgraph "Subscribers"
        SIM_S[Simulation]
        ROBS[Real Robot]
    end

    subgraph "Publishers (Feedback)"
        SIM_P[Simulation]
        ROBP[Real Robot]
    end

    subgraph "DDS Topics (Feedback)"
        LOWSTATE[rt/lowstate]
    end

    subgraph "Subscribers (Feedback)"
        RPC_S[RPC Bridge]
        SDK_S[SDK Clients]
    end

    RPC_P -->|Gamepad Input| WCT
    SDK_P -->|Motor Commands| LOWCMD
    SDK_P -->|Arm Commands| ARM_SDK

    WCT --> SIM_S
    LOWCMD --> SIM_S
    LOWCMD --> ROBS
    ARM_SDK --> SIM_S

    SIM_P -->|State Feedback| LOWSTATE
    ROBP -->|State Feedback| LOWSTATE

    LOWSTATE --> RPC_S
    LOWSTATE --> SDK_S

    style RPC_P fill:#e1f5ff
    style SDK_P fill:#e1f5ff
    style SIM_P fill:#e8f5e9
    style ROBP fill:#e8f5e9
    style WCT fill:#f0f0f0
    style LOWCMD fill:#f0f0f0
    style ARM_SDK fill:#f0f0f0
    style LOWSTATE fill:#f0f0f0
```

## Development Workflow

```mermaid
graph TD
    A[Phase 1: Environment Setup] --> B[Phase 2: SDK Exercises]
    B --> C[Phase 3: RL Lab]
    C --> D[Phase 4: Gangnam Style]

    A --> A1[Install Dependencies]
    A --> A2[Clone Submodules]
    A --> A3[Test Simulation]
    A --> A4[Verify RPC Bridge]

    B --> B1[Exercise 1: State Machine]
    B --> B2[Exercise 2: Low Level]
    B --> B3[Exercise 3: WirelessController]
    B --> B4[Exercise 4: G1 Poses]
    B --> B5[Exercise 5-6: Arm SDK]

    C --> C1[Exercise 7: Sim2Sim]
    C --> C2[Exercise 8: Policy Deploy]
    C --> C3[Exercise 9: Custom Motion]

    D --> D1[Design Choreography]
    D --> D2[Implement Motion Sequences]
    D --> D3[Test in Simulation]
    D --> D4[Deploy to Real Robot]

    D3 -.->|Must Pass| D4

    style A fill:#e8f5e9
    style B fill:#fff4e6
    style C fill:#fce4ec
    style D fill:#e1f5ff
```

## File Structure Map

```mermaid
graph TD
    ROOT[project/] --> DOC[docs/]
    ROOT --> SCRIPT[scripts/]
    ROOT --> VENDOR[_vendor/]
    ROOT --> G1[g1/]

    DOC --> STATUS[STATUS_REPORT.md]
    DOC --> COURSE[Unitree_G1_Reinforcement_Learning_Course/]
    DOC --> ANALYSIS[official_repo_analysis.md]

    VENDOR --> SDK[unitree_sdk2_python/]
    VENDOR --> MUJ[unitree_mujoco/]
    VENDOR --> EXTR[unitree_mujoco_extras/]
    VENDOR --> COUR[unitree_mujoco_tc/]
    VENDOR --> RL[unitree_rl_gym/]

    SDK --> EX1[example/g1/]
    SDK --> LIB[unitree_sdk2py/]

    EXTR --> LAUNCH[launch_unitree_v3.py]
    EXTR --> RPC[rpc_bridge/]

    RL --> POLICY[deploy/pre_train/g1/]
    RL --> RES[resources/robots/]

    POLICY --> MOTION[policy/motion.pt]
    RES --> XML[g1_29dof.xml]

    style DOC fill:#f0f0f0
    style VENDOR fill:#e8f5e9
    style G1 fill:#fff4e6
```

## Network Configuration

```mermaid
graph LR
    subgraph "Development Machine"
        APP[Python Application]
        DDS[DDS Middleware<br/>CycloneDDS]
    end

    subgraph "Network"
        ETH[Ethernet/WiFi]
    end

    subgraph "Robot PC2 (192.168.123.164)"
        ROBD[Robot Daemon]
    end

    subgraph "Simulation Mode"
        SIM[MuJoCo<br/>Loopback Interface]
    end

    APP -->|Domain ID: 1| DDS
    DDS -->|lo (localhost)| SIM
    DDS -->|eth0/wlan0| ETH
    ETH -->|192.168.123.164| ROBD

    style APP fill:#e1f5ff
    style DDS fill:#f0f0f0
    style SIM fill:#e8f5e9
    style ROBD fill:#e8f5e9
```

---

## Legend

| Color | Component Type |
|-------|---------------|
| Light Blue | Application Layer |
| Light Gray | Communication Layer |
| Light Green | Robot/Simulation |
| Light Yellow | User Input/Workflow |
| Light Pink | ML/RL Components |

| Symbol | Meaning |
|--------|---------|
| Solid Arrow | Data flow |
| Dashed Arrow | Optional/Conditional |
| State Box | FSM state |
| Subgraph | Logical grouping |