# Plan

Paper 86 `actuator_asymmetry_policy_state` completed the frozen v5 expanded ICLR-main submission-readiness audit.

Executed plan:

1. Preserve a frozen plan before edits: `docs/paper86_expanded_submission_plan_20260621.md`.
2. Expand the local benchmark to ten seeds, six tasks, eight actuator-shift splits, thirteen main methods, ten ablations, six stress axes, four fixed-risk budgets, and negative cases.
3. Keep the runner CPU-only and RAM-light by streaming raw CSVs and aggregating seed metrics.
4. Apply the hostile-review gate without optimizing for pretty results.
5. Generate a 25+ page manuscript with theory, full appendices, figures, and bright boxed clickable citations.
6. Write the canonical numbered PDF to `C:/Users/wangz/Downloads/86.pdf` only.
7. Validate exact row counts, LaTeX/citation state, page count, SHA256 match, and Desktop absence with `scripts/validate_submission_artifacts.py`.

Outcome:

- Terminal decision: `KILL_ARCHIVE`.
- PDF: `C:/Users/wangz/Downloads/86.pdf`.
- Pages: `29`.
- SHA256: `B9BCA5A27CD6F5B14032E146AEC84D75B035C245131D777057B44089495BF826`.
- Main blocker: success improves over v4, but tracking, safety, mechanism, fixed-risk, and scope gates fail.
