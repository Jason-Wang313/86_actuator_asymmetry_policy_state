# Paper 86 Expanded Submission-Readiness Plan

Date: 2026-06-21

Paper: `86_actuator_asymmetry_policy_state`

Target venue posture: ICLR-main hostile-review readiness audit.

Execution constraint: CPU-only, RAM-light, deterministic, no visible Desktop PDFs, canonical numbered PDF only at `C:/Users/wangz/Downloads/86.pdf`.

## Objective

Rebuild Paper 86 from a 6-page v4 archive memo into a 25+ page ICLR-style submission-readiness audit without padding. The rebuild must add substantive theory, a stronger frozen experiment suite, more seeds, stronger adaptive-control baselines, fixed-risk deployment tests, stress sweeps, ablations, negative cases, bright boxed clickable citations, validation scripts, public GitHub update, and root-ledger updates.

The central hypothesis remains:

> A robot policy should carry actuator asymmetry as latent policy state rather than treating asymmetric gain, deadzone, saturation, latency, thermal drift, and intermittent faults as calibration noise.

The v5 method under test will be `latent_asymmetry_belief_policy_v5`: a deterministic CPU-light proxy for an actuator-asymmetry belief-state policy with sign-specific latent memory, deadzone/saturation inference, thermal-drift update, latency compensation, safety-aware action clipping, and calibrated deployment risk scoring.

## Non-Negotiable Honesty Rules

- Do not claim real robot validation.
- Do not claim accepted high-fidelity simulation.
- Do not claim trained neural SOTA.
- Do not claim ICLR-main readiness unless all frozen evidence gates pass and the remaining evidence limitation is explicitly discussed.
- Report all predefined results, including failures and ablations that beat the proposed method.
- Treat synthetic-only evidence as a fatal deployment blocker unless the paper is framed as a diagnostic benchmark/negative audit.

## Frozen Experimental Design

### Seeds, Tasks, Splits, and Episodes

- Seeds: `0..9` (10 seeds).
- Tasks: 6 tasks:
  - `corridor_tracking`
  - `pivot_alignment`
  - `two_joint_reach`
  - `gripper_slide_insert`
  - `mobile_base_docking`
  - `cable_tension_following`
- Splits: 8 splits:
  - `balanced_nominal`
  - `left_right_gain_shift`
  - `deadzone_saturation_shift`
  - `thermal_drift_shift`
  - `latency_hysteresis_shift`
  - `intermittent_fault_shift`
  - `payload_contact_shift`
  - `combined_hard_shift`
- Episodes per task/split/seed: 32.
- Main methods: 13 methods:
  - `nominal_policy`
  - `domain_randomized_policy`
  - `scalar_gain_calibration`
  - `online_system_id`
  - `adaptive_mpc`
  - `robust_tube_mpc`
  - `control_barrier_fault_tolerant_mpc`
  - `unscented_kalman_fault_observer`
  - `recurrent_hidden_state_policy_proxy`
  - `robust_l1_adaptive_control`
  - `latent_asymmetry_policy_state_v4`
  - `latent_asymmetry_belief_policy_v5`
  - `oracle_asymmetry_state`

Expected main rollout rows: `10 * 6 * 8 * 32 * 13 = 199680`.

Expected episode summary rows: `10 * 6 * 8 * 32 = 15360`.

### Metrics

Primary metrics:

- `task_success`
- `tracking_error`
- `safety_violation`
- `asymmetry_error`

Secondary and deployment metrics:

- `actuator_energy`
- `adaptation_regret`
- `calibration_error`
- `constraint_margin`
- `recovery_time`
- `control_smoothness`
- `state_uncertainty`
- `risk_score`
- `robust_utility`

### Hard Aggregate

The hard aggregate is predeclared as:

- `intermittent_fault_shift`
- `payload_contact_shift`
- `combined_hard_shift`

All main gate decisions use seed means over these three splits, not post-hoc selected rows.

### Ablations

Ablations are evaluated on `payload_contact_shift` and `combined_hard_shift` with 28 episodes per task/seed.

Ten ablations:

- `full_latent_asymmetry_belief_policy_v5`
- `minus_persistent_latent_memory`
- `minus_sign_specific_asymmetry`
- `minus_deadzone_saturation_state`
- `minus_latency_compensation`
- `minus_thermal_drift_update`
- `minus_online_residual_update`
- `minus_safety_aware_action_clipping`
- `scalar_only_latent_gain`
- `no_belief_uncertainty`

Expected ablation rollout rows: `10 * 6 * 2 * 28 * 10 = 33600`.

### Stress Sweeps

Stress sweeps are evaluated on `combined_hard_shift`, 20 episodes per task/seed, 6 axes, 6 levels, and 7 methods:

- Stress axes:
  - `gain_asymmetry`
  - `deadzone_saturation`
  - `latency`
  - `thermal_drift`
  - `intermittent_fault`
  - `combined`
- Levels: `0.0, 0.2, 0.4, 0.6, 0.8, 1.0`.
- Methods:
  - `domain_randomized_policy`
  - `online_system_id`
  - `control_barrier_fault_tolerant_mpc`
  - `unscented_kalman_fault_observer`
  - `robust_l1_adaptive_control`
  - `latent_asymmetry_belief_policy_v5`
  - `oracle_asymmetry_state`

Expected stress raw rows: `10 * 6 * 20 * 6 * 6 * 7 = 302400`.

### Fixed-Risk Deployment Tests

Fixed-risk tests evaluate whether each policy can retain nontrivial deployment coverage under safety-risk budgets.

- Splits: `payload_contact_shift`, `combined_hard_shift`.
- Budgets: `0.02, 0.05, 0.08, 0.10`.
- Methods:
  - `online_system_id`
  - `control_barrier_fault_tolerant_mpc`
  - `unscented_kalman_fault_observer`
  - `robust_l1_adaptive_control`
  - `latent_asymmetry_belief_policy_v5`
  - `oracle_asymmetry_state`
- Episodes per task/seed: 24.

Expected fixed-risk raw rows: `10 * 6 * 2 * 24 * 4 * 6 = 69120`.

### Negative Cases

Create 24 negative cases covering:

- complete actuator failure;
- sensor bias mimicking actuator asymmetry;
- contact slip dominating actuator mismatch;
- rapid sign-flipping asymmetry;
- payload shifts outside the latent-state family;
- latency-driven instability under otherwise correct gain inference.

## Frozen Decision Gates

The terminal decision will be `STRONG_REVISE` only if all recoverable gates pass. Otherwise it will be `KILL_ARCHIVE`.

### Main Hard-Aggregate Gate

Let `best_success_reference` be the strongest non-oracle baseline by hard-aggregate `task_success`, `best_tracking_reference` the lowest non-oracle hard-aggregate `tracking_error`, and `best_safety_reference` the lowest non-oracle hard-aggregate `safety_violation`.

The v5 method must satisfy:

- hard-aggregate `task_success >= best_success_reference + 0.030`;
- hard-aggregate `tracking_error <= best_tracking_reference - 0.015`;
- hard-aggregate `safety_violation <= best_safety_reference + 0.002`;
- hard-aggregate `robust_utility >= best_utility_reference + 0.030`;
- paired lower95 seed difference for `task_success` versus `best_success_reference` is positive;
- paired upper95 seed difference for `tracking_error` versus `best_tracking_reference` is negative;
- paired upper95 seed difference for `safety_violation` versus `best_safety_reference` is at most `0.002`.

### Mechanism Gate

The full v5 method must beat every non-full ablation on hard-split robust utility by at least `0.015`, and no ablation may improve both task success and safety violation simultaneously.

### Stress Gate

At maximum combined stress, v5 must not be dominated by any non-oracle method on the tuple:

`task_success`, `tracking_error`, `safety_violation`, `asymmetry_error`, `robust_utility`.

### Fixed-Risk Gate

At risk budget `0.05`, v5 must have:

- nonzero accepted-deployment coverage on both fixed-risk splits;
- coverage at least as high as the best non-oracle feasible method satisfying the same budget;
- accepted task success no worse than the best non-oracle feasible method by more than `0.010`;
- accepted safety violation no worse than the best non-oracle feasible method by more than `0.002`.

### Scope Gate

Even if all synthetic gates pass, mark as at most `STRONG_REVISE` unless real robot or accepted high-fidelity evidence exists. If any main, mechanism, stress, or fixed-risk gate fails, mark `KILL_ARCHIVE`.

## Manuscript Requirements

- Generate a 25+ page ICLR-style manuscript.
- Include theory/proposition section covering:
  - identifiability of asymmetric gain/deadzone under persistent excitation;
  - why scalar calibration fails for sign-specific deadzones and saturation;
  - why persistent latent memory can fail under rapidly switching faults;
  - fixed-risk deployment bound under calibrated risk scores.
- Include full tables for main results, hard aggregate, paired tests, ablations, stress, fixed-risk, negative cases, and prior-work threat map.
- Use bright boxed clickable citations via `hyperref`.
- Include references in `paper/references.bib`; citations must resolve and route to bibliography entries.
- Build a clean PDF and copy only to `C:/Users/wangz/Downloads/86.pdf`.
- Do not copy any PDF to the visible Desktop.

## Validation Requirements

The final validator must check:

- expected CSV row counts;
- required columns, splits, methods, metrics, and negative-case count;
- terminal decision tokens in `results/summary.txt`;
- `paper/main.log` has no unresolved citations/references or rerun warnings;
- `paper/main.pdf` has at least 25 pages;
- `C:/Users/wangz/Downloads/86.pdf` exists and matches the built PDF hash;
- `C:/Users/wangz/Desktop/86.pdf` does not exist;
- PDF text contains terminal decision and key gate evidence;
- bright boxed citation settings are present in `paper/main.tex`.

## Repository and Ledger Requirements

- Commit and push the expanded Paper 86 repo to the existing public GitHub repository.
- Update root ledgers:
  - `GLOBAL_POOL_STATUS.md`
  - `BATCH_STATUS.md`
  - `SUBMISSION_STATUS.md`
  - `MASTER_REPORT.md`
  - `MASTER_SUBMISSION_REPORT.md`
  - `SUBMISSION_AUDIT_MATRIX.csv`
- Advance the expanded-standard frontier from Papers 61-85 to Papers 61-86.
