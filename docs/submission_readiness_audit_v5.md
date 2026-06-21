# Paper 86 Submission Readiness Audit v5

Last update: 2026-06-22 00:42 +08:00

## Terminal Decision

KILL_ARCHIVE for ICLR main.

## Evidence Added In v5

- Implemented a CPU-only, RAM-light, deterministic expanded actuator-asymmetry audit.
- Main evaluation: 199,680 rollouts across eight splits, thirteen methods, six tasks, and ten seeds.
- Dataset summary: 15,360 actuator-state summaries.
- Ablation evaluation: 33,600 rollouts over two hard splits and ten ablations.
- Stress evaluation: 302,400 rows over six axes, six levels, seven methods, six tasks, and ten seeds.
- Fixed-risk evaluation: 69,120 rows over two hard splits, four budgets, six methods, six tasks, and ten seeds.
- Negative cases: 24 retained failure cases.
- Figures, CSVs, summary text, manuscript source, references, and PDF are regenerated from scripts.

## Main Hard-Aggregate Evidence

- `latent_asymmetry_belief_policy_v5`: task success `0.14566 +/- 0.01168`; tracking error `0.70018`; safety violation `0.30466`; asymmetry error `0.24497`; robust utility `-0.46242`.
- `latent_asymmetry_policy_state_v4`: task success `0.12413 +/- 0.00938`; tracking error `0.68686`; safety violation `0.28271`; asymmetry error `0.24282`; robust utility `-0.46948`.
- Paired task-success difference versus v4: mean `0.02153`, ci95 `0.01651`, lower95 `0.00502`.
- Paired tracking difference versus v4: mean `0.01332`, ci95 `0.00552`, upper95 `0.01884`.
- Paired safety difference versus v4: mean `0.02195`, ci95 `0.00813`, upper95 `0.03008`.

## Gate Outcomes

- Main gate: failed. Success improves, but tracking and safety gates fail.
- Mechanism gate: failed. The full method does not achieve the clean robust-utility necessity margin and ablation tradeoffs remain.
- Stress gate: passed. At maximum combined stress no non-oracle method Pareto-dominates v5.
- Fixed-risk gate: failed. Budget `0.05` has zero accepted coverage on both fixed-risk splits.
- Scope gate: failed. No real robot or accepted high-fidelity benchmark evidence is present.

## Artifact Verification

- PDF: `C:/Users/wangz/Downloads/86.pdf`.
- Pages: `29`.
- SHA256: `B9BCA5A27CD6F5B14032E146AEC84D75B035C245131D777057B44089495BF826`.
- Desktop copy: absent.
- Validator: `python scripts\validate_submission_artifacts.py` passed.
- Visual QA: rendered and inspected representative pages; citation boxes are bright green and layout is readable.

## Revival Requirements

- Evaluate on robot hardware or an accepted high-fidelity actuator-fault/asymmetry benchmark.
- Demonstrate no safety regression against v4, online ID, control-barrier fault-tolerant MPC, and fault observers.
- Retain nonzero fixed-risk coverage at a meaningful safety budget.
- Replace deterministic proxy controllers with learned or deployed controllers where claimed.
- Provide a manual related-work synthesis around actuator faults, saturation, deadzones, adaptive control, and latent-state policies.
