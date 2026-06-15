# Paper 86 Terminal Audit

Date: 2026-06-15 09:52:18 +01:00

Paper: `86_actuator_asymmetry_policy_state`

Terminal decision: `KILL_ARCHIVE`

## Rerun Command

```powershell
python -m py_compile src\run_experiment.py
python src\run_experiment.py
```

The experiment runner completed successfully and printed `terminal=KILL_ARCHIVE`.

## Evidence Coverage

- `rollouts.csv`: 40,320 rows, 17 columns.
- `raw_seed_metrics.csv`: 280 rows, 11 columns.
- `metrics.csv`: 280 rows, 7 columns.
- `pairwise_stats.csv`: 210 rows, 6 columns.
- `ablation_rollouts.csv`: 7,056 rows, 17 columns.
- `ablation_seed_metrics.csv`: 49 rows, 11 columns.
- `ablation_metrics.csv`: 7 rows, 8 columns.
- `stress_sweep_raw.csv`: 100,800 rows, 19 columns.
- `stress_sweep.csv`: 180 rows, 9 columns.
- `negative_cases.csv`: 4 rows, 4 columns.

Verified seeds: `0, 1, 2, 3, 4, 5, 6`.

Verified splits: `balanced_nominal`, `left_right_gain_shift`, `deadzone_saturation_shift`, `thermal_drift_shift`, `combined_hard_shift`.

Verified tasks: `corridor_tracking`, `pivot_alignment`, `two_joint_reach`, `gripper_slide_insert`.

Verified methods: `nominal_policy`, `domain_randomized_policy`, `scalar_gain_calibration`, `online_system_id`, `adaptive_mpc`, `robust_tube_mpc`, `latent_asymmetry_policy_state`, `oracle_asymmetry_state`.

Verified ablations: `full_latent_asymmetry_policy_state`, `minus_persistent_latent_memory`, `minus_sign_specific_asymmetry`, `minus_deadzone_saturation_state`, `minus_online_residual_update`, `scalar_only_latent_gain`, `no_safety_aware_action_clipping`.

Verified stress axes: `gain_asymmetry`, `deadzone_saturation`, `latency`, `thermal_drift`, `combined`.

## Main Gate

Combined hard-shift task success:

- `latent_asymmetry_policy_state`: `0.15079 +/- 0.01646`.
- `online_system_id`: `0.09921 +/- 0.01178`.
- Paired task-success difference versus online system ID: `0.05159 +/- 0.02483`.
- `oracle_asymmetry_state`: `0.20635 +/- 0.03473`.

The proposed method also improves tracking error (`0.66073` vs `0.66581`) and asymmetry error (`0.29399` vs `0.33933`) relative to online system ID.

## Safety Gate

- `latent_asymmetry_policy_state`: `0.18730` safety violation.
- `online_system_id`: `0.18396` safety violation.
- `oracle_asymmetry_state`: `0.16128` safety violation.

The main hard-split safety gate does not pass because the proposed method is not safer than the strongest online system-identification baseline.

## Ablation Gate

- Full latent-asymmetry state: `0.15079 +/- 0.01646` task success.
- Minus persistent memory: `0.08532 +/- 0.02030`.
- Minus sign-specific asymmetry: `0.12500 +/- 0.02339`.
- Minus deadzone/saturation state: `0.09623 +/- 0.01407`.
- Minus online residual update: `0.09921 +/- 0.02115`.
- Scalar-only latent gain: `0.09424 +/- 0.01944`.
- No safety-aware clipping: `0.11012 +/- 0.02211`, with safety violation rising to `0.25724`.

Ablations support the local mechanism, but do not overcome the safety and external-validation blockers.

## Stress Gate

At maximum combined stress:

- `latent_asymmetry_policy_state`: `0.09107 +/- 0.02051` task success, `0.32929` safety violation.
- `online_system_id`: `0.05000 +/- 0.02268` task success, `0.36262` safety violation.
- `robust_tube_mpc`: `0.05357 +/- 0.01906` task success, `0.42298` safety violation.
- `oracle_asymmetry_state`: `0.10000 +/- 0.02726` task success.

Stress evidence is encouraging but local synthetic only and does not remove the main hard-split safety blocker.

## Submission Decision

Paper 86 is not ICLR-main ready. It should remain an archived near-miss unless future work adds real actuator-asymmetry hardware or recognized high-fidelity evidence, stronger adaptive/control-barrier/MPC baselines, and safety dominance alongside the existing success/tracking gains.

## PDF Artifact

- Canonical PDF: `C:/Users/wangz/Downloads/86.pdf`.
- SHA256: `43EB3061253F0737A8563816AD8E3B5B1F78B866FD6FA0BD4614931A260A078A`.
- Desktop copy: absent.
