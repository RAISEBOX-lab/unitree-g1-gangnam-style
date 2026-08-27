# archive/ — third-party reference policies (not trained here)

Binary files in this folder are git-ignored (`*.pt`, `*.onnx`, `*.safetensors`);
re-download from the sources below if missing. None are used by the main
unitree_rl_lab sim2sim pipeline.

## model_5000.pt
- Source: https://huggingface.co/hardware-pathon-ai/unitree-g1-phase1-locomotion
- What: PathonAI "Phase 1: Baseline Locomotion (Frozen Arms)". PPO policy for the
  G1 29-DOF trained in NVIDIA **Isaac Gym** (not Isaac Lab), 5000 iterations,
  legs + waist active, arms frozen. RSL-RL checkpoint (`model_state_dict`,
  22 actions, 77-dim obs). Loading it requires the `isaacgym` package.
  Model card says MuJoCo sim2sim validation is pending.
- sha256: `427dd675c0e87707ac057b864f30ce4e46fbfa731aad4cde4544c09a1e0696ba`

## velocity_v28_iter44000/
- Source: https://huggingface.co/haixuantao/unitree-g1-velocity-v28/tree/main/velocity_v28_iter44000
- What: 12-DOF legs-only velocity policy from the "zealot" trainer (nexus GPU
  physics). `policy.onnx` input `obs [N, 265]` = 5-frame history x 53 with
  the obs normalizer baked in; output `action [N, 12]`,
  `q_target = default_pos + 0.5 * action`. `env.yaml` is the deploy contract
  (joint order, PD gains — ankles kp 40 / kd 2.0). Reference obs builder:
  `zealot/examples/biped/sim2sim_xval.py` (lag-2 last_action convention).
- Referenced by `_vendor/unitree_rl_gym/deploy/deploy_mujoco/configs/g1_policy_only.yaml`
  (experimental ONNX path in `policy_to_lowcmd_v11b_*.py`; obs layout there is
  a guess and unverified).
- sha256 policy.onnx: `fd17dc1f60e360882670572d21db1f8ac1e840bb37ffe059b066bbf2aef38de7`
- sha256 policy.safetensors: `9324f37506c11fc8485b4bae8f271cc71bb7d4314b18548d33eef76f5a1c94cc`
