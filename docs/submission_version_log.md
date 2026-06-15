# Submission Version Log

## v1 - Generated Draft
- Original continuation-batch generated paper and toy single-seed experiment.

## v2 - Submission Hardening
- Added hostile reviewer attack log and response docs.
- Replaced the toy experiment with seven-seed metrics, stronger baselines, ablations, stress tests, and negative cases.
- Narrowed claims to synthetic diagnostic evidence.
- Recompiled canonical PDF at `C:/Users/wangz/Downloads/86.pdf`.
- Terminal decision: WORKSHOP_ONLY.

## v3 - ICLR Main Gate Archive
- Applied the stricter ICLR-main-conference standard.
- Re-read local paper, docs, experiments, prior-work artifacts, PDF state, and repo state.
- Determined that missing real-robot/high-fidelity evidence, template-generated experiments, and unresolved novelty threats are not recoverable from local artifacts.
- Recompiled the canonical PDF with `Submission-hardening version: v3`.
- Terminal decision: KILL_ARCHIVE.

## v4 - Actuator-Asymmetry Evidence Audit
- Replaced the generic archive state with a deterministic local actuator-asymmetry benchmark.
- Added four control tasks, eight methods, five asymmetry-shift splits, ablations, stress sweeps, negative cases, and figures.
- Main result: latent asymmetry state improves hard-shift success and tracking over online system ID, adaptive MPC, robust tube MPC, and scalar calibration.
- Blocker: hard-split safety does not decisively beat online system ID, absolute success remains low, and evidence is local synthetic only.
- Terminal decision: KILL_ARCHIVE.

## v4.1 - 2026-06-15 Rerun Audit
- Added the paper-specific ICLR-main execution plan before running any new evidence.
- Re-ran `python src\run_experiment.py` from source and reproduced `terminal=KILL_ARCHIVE`.
- Verified 40,320 main rollouts, 7,056 ablation rollouts, 100,800 stress rollouts, seven seeds, eight methods, seven ablations, five stress axes, four tasks, and four negative cases.
- Preserved the terminal decision because the local mechanism signal is not enough without safety dominance or external validation.
