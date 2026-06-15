# Plan

Paper 86 `actuator_asymmetry_policy_state` is in the 2026-06-15 ICLR-main submission-readiness audit pass.

Execution plan:

1. Rerun the full deterministic actuator-asymmetry benchmark from source.
2. Audit all main, ablation, stress, pairwise, and negative-case outputs.
3. Apply the ICLR-main evidence gate without overclaiming local synthetic evidence.
4. Preserve the terminal decision as `KILL_ARCHIVE` unless latent asymmetry state decisively improves success, tracking, and safety against system-ID/MPC baselines and ablations validate the mechanism.
5. Rebuild `C:/Users/wangz/Downloads/86.pdf` only, update root reports, commit, push, and verify the public GitHub repo.
