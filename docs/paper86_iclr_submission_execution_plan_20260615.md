# Paper 86 ICLR-Main Submission-Readiness Execution Plan

Date: 2026-06-15

Paper: `86_actuator_asymmetry_policy_state`

Target venue standard: ICLR main conference, with an evidence-first gate. The paper can advance only if the rebuilt evidence shows that latent actuator-asymmetry policy state decisively improves success, tracking, and safety against strong system-identification and MPC baselines, with ablations validating the mechanism. Local synthetic success alone is not enough.

## Current State

The repository currently reports a v4 terminal decision of `KILL_ARCHIVE`. The existing claim is that actuator asymmetry should be represented as persistent latent policy state rather than treated as calibration noise. The prior audit found a real local success/tracking signal over online system identification, but safety was not decisively better and the evidence remained local synthetic simulation rather than robot hardware or an accepted high-fidelity benchmark.

## Execution Order

1. Verify repository hygiene before touching evidence.
   - Confirm the worktree is clean except for this plan.
   - Record the pre-audit commit.
   - Confirm the GitHub remote exists and is public.

2. Re-run the full evidence generator from source.
   - Compile-check `src/run_experiment.py`.
   - Run `python src/run_experiment.py`.
   - Preserve all generated CSVs, figures, and `results/summary.txt`.

3. Audit evidence completeness.
   - Confirm seven seeds are present.
   - Confirm all splits, tasks, methods, ablations, stress axes, and negative cases are represented.
   - Confirm row counts and schemas for rollout, seed metric, aggregate metric, pairwise, ablation, stress, and negative-case files.

4. Apply the ICLR-main decision gate.
   - Require the proposed latent-state controller to beat the strongest non-oracle baseline on combined hard-shift task success with paired uncertainty supporting the claim.
   - Require tracking error and asymmetry estimation error to improve against online system ID, adaptive MPC, and robust tube MPC.
   - Require safety violation to improve or at least not regress versus the safest strong baseline.
   - Require ablations to degrade when persistent memory, sign-specific asymmetry, deadzone/saturation state, residual updates, or safety clipping are removed.
   - Require stress tests to support the same conclusion under gain asymmetry, deadzone/saturation, latency, thermal drift, and combined stress.

5. Decide honestly.
   - If success/tracking/mechanism gates pass but evidence remains local synthetic and safety is incomplete, mark at most `STRONG_REVISE`.
   - If safety regresses against a strong baseline or ablations fail, preserve `KILL_ARCHIVE`.
   - Do not claim ICLR-main readiness without robot or recognized high-fidelity benchmark evidence.

6. Update the paper and child documentation.
   - Make `README.md`, `child_status.md`, `plan.md`, audit docs, attack log, readiness decision, hostile reviewer response, and version log match the rerun.
   - Add a terminal audit document with exact row counts, seed coverage, metric conclusions, and PDF hash.

7. Build and verify the PDF.
   - Build `paper/main.pdf` with LaTeX.
   - Copy only the numbered PDF to `C:/Users/wangz/Downloads/86.pdf`.
   - Do not copy any PDF to the visible Desktop.
   - Scan logs for LaTeX/BibTeX warnings that affect submission quality.

8. Update root reports.
   - Update `GLOBAL_POOL_STATUS.md`, `BATCH_STATUS.md`, `SUBMISSION_STATUS.md`, `MASTER_REPORT.md`, and `MASTER_SUBMISSION_REPORT.md`.
   - Mark Paper 86 with the final terminal decision, commit hash, PDF hash, GitHub URL, and concise evidence.

9. Commit, push, and verify.
   - Commit only Paper 86 files inside its child repo.
   - Push `main` to the public GitHub repo.
   - Verify local `HEAD` equals `origin/main`.
   - Verify `C:/Users/wangz/Downloads/86.pdf` exists and `C:/Users/wangz/Desktop/86.pdf` does not.

## Expected Outcome Risk

The likely outcome is still `KILL_ARCHIVE`, because the prior v4 evidence shows success and tracking gains but incomplete safety dominance plus no hardware or high-fidelity validation. The rerun will still be performed end-to-end; the decision will be evidence-bound, not assumed.
