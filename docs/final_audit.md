# Final Audit

1. Chosen thesis: Actuator Asymmetry as Policy State explores `Treat actuator asymmetry as latent policy state rather than calibration noise.` for robot adaptation and control.
2. ICLR-main decision: KILL_ARCHIVE.
3. Submission-hardening version: v5 expanded.
4. Reason: the expanded CPU-only actuator-asymmetry audit finds a real hard-aggregate success gain for belief-state v5, but tracking and safety regress relative to v4, mechanism and fixed-risk gates fail, and the evidence remains local synthetic only.
5. Closest hostile prior work: see `docs/hostile_prior_work.md`, `docs/hostile_prior_work_100_cards.csv`, `docs/hostile_reviewer_response.md`, and the bright-boxed citation table in `paper/main.tex`.
6. Reproducibility: `python src\run_experiment.py` regenerates metrics and figures; `python scripts\generate_manuscript.py` regenerates `paper/main.tex` and `paper/references.bib`.
7. Claim-validity status: positive main-conference claims killed; v5 expanded negative evidence audit retained.
8. Exact Downloads PDF path: `C:/Users/wangz/Downloads/86.pdf`.
9. PDF pages: `29`.
10. PDF SHA256: `B9BCA5A27CD6F5B14032E146AEC84D75B035C245131D777057B44089495BF826`.
11. GitHub URL: https://github.com/Jason-Wang313/86_actuator_asymmetry_policy_state
12. Confirmation: no visible Desktop copy was requested or retained.
13. v5 rerun: `199,680` main rollouts, `15,360` actuator summaries, `33,600` ablation rollouts, `302,400` stress rows, `69,120` fixed-risk rows, and `24` negative cases.
14. Hard-aggregate success gate: v5 task success `0.14566 +/- 0.01168`; v4 task success `0.12413 +/- 0.00938`; paired success lower95 `0.00502`.
15. Tracking gate: v5 tracking `0.70018`; v4 tracking `0.68686`; paired tracking upper95 `0.01884`; gate failed.
16. Safety gate: v5 safety violation `0.30466`; v4 safety violation `0.28271`; paired safety upper95 `0.03008`; gate failed.
17. Mechanism gate: failed because the full method did not clear the clean robust-utility necessity margin and ablation tradeoffs remain.
18. Fixed-risk gate: failed because budget `0.05` has zero accepted coverage on both fixed-risk splits.
19. Scope gate: failed because there is no robot hardware or accepted high-fidelity benchmark evidence.
20. Artifact validator: `scripts/validate_submission_artifacts.py` passed.
