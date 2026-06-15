# 86 Actuator Asymmetry as Policy State

Submission-hardening version: v4

Terminal decision: **KILL_ARCHIVE** for ICLR main conference.

Latest audit rerun: 2026-06-15.

This repository contains a reproducible local evidence audit for the research bet:

> Treat actuator asymmetry as latent policy state rather than calibration noise.

The v4 rebuild replaces the template scaffold with a deterministic actuator-asymmetry benchmark over four robotic control tasks, five shift splits, eight methods, ablations, stress sweeps, and negative cases.

## Why This Is Archived

- The 2026-06-15 rerun regenerated 40,320 main rollouts, 7,056 ablation rollouts, and 100,800 stress rollouts.
- On the combined hard-shift split, `latent_asymmetry_policy_state` reaches `0.15079 +/- 0.01646` task success.
- The strongest success baseline, `online_system_id`, reaches `0.09921 +/- 0.01178`.
- The paired task-success difference is `0.05159 +/- 0.02483`.
- The proposed method improves tracking (`0.66073`) and asymmetry error (`0.29399`) over the strongest non-oracle success baseline.
- Safety is not a decisive win: `online_system_id` has slightly lower safety violation (`0.18396`) than the proposed method (`0.18730`).
- The evidence is local and synthetic, not hardware or accepted high-fidelity benchmark validation.

## Reproduce

```powershell
python src\run_experiment.py
```

The runner writes:

- `results/rollouts.csv`
- `results/raw_seed_metrics.csv`
- `results/metrics.csv`
- `results/pairwise_stats.csv`
- `results/ablation_rollouts.csv`
- `results/ablation_seed_metrics.csv`
- `results/ablation_metrics.csv`
- `results/stress_sweep_raw.csv`
- `results/stress_sweep.csv`
- `results/negative_cases.csv`
- `results/summary.txt`
- `figures/asymmetry_*.png`

## Rebuild PDF

```powershell
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Canonical local PDF: `C:/Users/wangz/Downloads/86.pdf`
