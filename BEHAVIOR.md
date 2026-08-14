# BEHAVIOR.md - Interaction Guidelines

## Role
I am an AI assistant helping you implement Gangnam Style choreography on the Unitree G1 robot. I will:
- Propose actions before executing them
- Provide text-based diagrams (no images)
- Save all outputs as files in the project folder
- Follow the Unitree G1 Reinforcement Learning Course exactly

## Objective
- Set up Unitree G1 Gangnam Style project environment using official course repositories to run SDK exercises and course units in order.

## Important Details
- Official course repo: `https://bitbucket.org/theconstructcore/g1_mujoco_tc` (contains `unitree_mujoco`, `unitree_rl_gym`).
- Third-party repo used so far: `https://github.com/Michdo93/unitree_mujoco_extras` (RPC bridge, gamepad GUI).
- Behavior rules: Propose before acting, text-based diagrams only, all outputs in project folder.
- Simulation target: MuJoCo with gamepad input via RPC bridge (check if official repo has this).
- User requires following Unitree G1 Reinforcement Learning Course exactly.

## Work State
### Completed
- Cloned `unitree_sdk2_python`, `unitree_mujoco_extras` (third-party).
- Updated `docs/PROJECT_GUIDELINES.md` with 4-phase workflow and scope separation.
- Created `docs/environment_setup_checklist.md` and `docs/official_repo_analysis.md`.
- Ran `git submodule status` to check current submodule sources.

### Active
- Investigating source of current `_vendor/unitree_mujoco` submodule (commit `ae6a8403e272733e9996ef59990880330496177f`).
- Awaiting user confirmation to replace third-party repos with official course repos.

### Blocked
- None (waiting for user response to submodule source question).

## Next Move
1. Explain source of current `_vendor/unitree_mujoco` submodule based on `git submodule status` result.
2. Propose cloning official `unitree_mujoco` and `unitree_rl_gym` from Bitbucket to replace third-party versions.

## Relevant Files
- `docs/PROJECT_GUIDELINES.md`: Updated workflow, constraints, and scope separation.
- `docs/environment_setup_checklist.md`: Official vs third-party repo mapping and setup steps.
- `docs/official_repo_analysis.md`: Bitbucket repo structure and component details.
- `_vendor/unitree_mujoco`: Current simulator (source under investigation).
- `_vendor/unitree_mujoco_extras`: Third-party RPC bridge (may be redundant).
- `_vendor/unitree_sdk2_python`: Official SDK (kept).