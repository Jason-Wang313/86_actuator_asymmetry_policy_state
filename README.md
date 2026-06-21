# 86 Actuator Asymmetry as Policy State

Submission-hardening version: v5 expanded submission-readiness audit

Terminal decision: **KILL_ARCHIVE** for ICLR main conference.

Latest audit rerun: 2026-06-22 00:42 +08:00.

Canonical PDF: `C:/Users/wangz/Downloads/86.pdf`

Canonical PDF SHA256: `B9BCA5A27CD6F5B14032E146AEC84D75B035C245131D777057B44089495BF826`

This repository contains a reproducible local evidence audit for the research bet:

> Treat actuator asymmetry as latent policy state rather than calibration noise.

The v5 rebuild expands the old short v4 audit into a deterministic CPU-only benchmark over six robotic control tasks, eight actuator-shift splits, thirteen main methods, ten ablations, six stress axes, fixed-risk deployment tests, negative cases, and a 29-page ICLR-style manuscript with bright boxed clickable citations.

## Why This Is Archived

- The v5 runner regenerated `199,680` main rollouts, `15,360` actuator summaries, `33,600` ablation rollouts, `302,400` stress rows, `69,120` fixed-risk rows, and `24` negative cases.
- On the predefined hard aggregate, `latent_asymmetry_belief_policy_v5` reaches `0.14566 +/- 0.01168` task success.
- The strongest non-oracle success baseline is `latent_asymmetry_policy_state_v4` at `0.12413 +/- 0.00938`.
- The paired hard-aggregate success lower95 bound for v5 minus v4 is positive: `0.00502`.
- The result fails the main gate because v5 worsens hard-aggregate tracking (`0.70018` vs `0.68686`) and safety violation (`0.30466` vs `0.28271`) against v4.
- The mechanism gate fails, fixed-risk coverage at budget `0.05` is zero, and the evidence is local synthetic only.
- There is no robot hardware or accepted high-fidelity benchmark validation.

## Reproduce

```powershell
python src\run_experiment.py
python scripts\generate_manuscript.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
cd ..
Copy-Item -LiteralPath paper\main.pdf -Destination "$HOME\Downloads\86.pdf" -Force
python scripts\validate_submission_artifacts.py
```

The runner writes:

- `results/rollouts.csv`
- `results/dataset_summary.csv`
- `results/raw_seed_metrics.csv`
- `results/metrics.csv`
- `results/pairwise_stats.csv`
- `results/hard_aggregate_seed_metrics.csv`
- `results/hard_aggregate_metrics.csv`
- `results/hard_aggregate_pairwise_stats.csv`
- `results/ablation_rollouts.csv`
- `results/ablation_seed_metrics.csv`
- `results/ablation_metrics.csv`
- `results/stress_sweep_raw.csv`
- `results/stress_sweep_seed_metrics.csv`
- `results/stress_sweep.csv`
- `results/fixed_risk_raw.csv`
- `results/fixed_risk_seed_metrics.csv`
- `results/fixed_risk_metrics.csv`
- `results/fixed_risk_pairwise.csv`
- `results/negative_cases.csv`
- `results/summary.txt`
- `figures/asymmetry_*_v5.png`

The artifact validator confirmed `29` PDF pages, the SHA256 above, exact row counts, clean citations/references, bright citation-box settings, and no visible Desktop copy.
