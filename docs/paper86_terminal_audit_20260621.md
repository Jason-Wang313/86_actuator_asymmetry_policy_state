# Paper 86 Terminal Audit

Date: 2026-06-22 00:42 +08:00

Paper: `86_actuator_asymmetry_policy_state`

Terminal recommendation: `KILL_ARCHIVE`

ICLR main ready: no

## Executed Evidence

- Main rollout rows: `199680`.
- Dataset summary rows: `15360`.
- Ablation rollout rows: `33600`.
- Stress raw rows: `302400`.
- Fixed-risk raw rows: `69120`.
- Negative cases: `24`.

## Primary Result

`latent_asymmetry_belief_policy_v5` improves hard-aggregate task success over `latent_asymmetry_policy_state_v4`:

- v5 success: `0.14566 +/- 0.01168`.
- v4 success: `0.12413 +/- 0.00938`.
- Paired success lower95: `0.00502`.

The paper remains killed because the same comparison fails the hostile-review tracking and safety gates:

- v5 tracking: `0.70018`; v4 tracking: `0.68686`; paired tracking upper95: `0.01884`.
- v5 safety violation: `0.30466`; v4 safety violation: `0.28271`; paired safety upper95: `0.03008`.

## Gate Summary

- Main gate: false.
- Mechanism gate: false.
- Stress gate: true.
- Fixed-risk gate: false.
- Scope gate: false.

## Artifact Summary

- PDF: `C:/Users/wangz/Downloads/86.pdf`.
- Pages: `29`.
- SHA256: `B9BCA5A27CD6F5B14032E146AEC84D75B035C245131D777057B44089495BF826`.
- Desktop copy: absent.
- Validator: passed.
- Visual QA: passed.
