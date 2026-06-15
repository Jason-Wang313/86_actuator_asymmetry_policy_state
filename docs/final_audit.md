# Final Audit

1. Chosen thesis: Actuator Asymmetry as Policy State explores `Treat actuator asymmetry as latent policy state rather than calibration noise.` for robot adaptation and control.
2. ICLR-main decision: KILL_ARCHIVE.
3. Submission-hardening version: v4.1.
4. Reason: a local actuator-asymmetry benchmark shows a real success/tracking signal, but safety does not decisively beat online system ID and the evidence remains local synthetic only.
5. Closest hostile prior work: see `docs/hostile_prior_work.md`, `docs/hostile_prior_work_100_cards.csv`, and `docs/hostile_reviewer_response.md`.
6. Reproducibility: v4 benchmark code runs and regenerates metrics/figures, but no real robot or high-fidelity benchmark is reproduced.
7. Claim-validity status: positive main-conference claims killed; v4 near-miss evidence audit retained.
8. Exact Downloads PDF path: `C:/Users/wangz/Downloads/86.pdf`
9. GitHub URL: https://github.com/Jason-Wang313/86_actuator_asymmetry_policy_state
10. Confirmation: no visible Desktop copy was requested or made.
11. 2026-06-15 rerun: 40,320 main rollouts, 7,056 ablation rollouts, and 100,800 stress rollouts reproduced `KILL_ARCHIVE`.
12. Hard-split success gate: paired gain over online system ID is `0.05159 +/- 0.02483`.
13. Safety gate: online system ID has lower hard-split safety violation (`0.18396`) than the proposed method (`0.18730`).
14. Mechanism gate: persistent memory, sign-specific asymmetry, deadzone/saturation state, residual update, scalar-only latent gain, and safety clipping ablations support the local mechanism, but not ICLR-main readiness.
