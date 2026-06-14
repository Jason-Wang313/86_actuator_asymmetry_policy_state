# Paper 86 Rebuild Plan

Last update: 2026-06-14 11:47:42 +01:00

## Target Claim

Actuator asymmetry should be represented as latent policy state rather than treated as calibration noise. A policy that carries an explicit asymmetry state should adapt faster and safer under asymmetric gain, deadzone, saturation, latency, and drift than nominal policies, robust controllers, scalar system identification, or online residual compensation.

## Evidence To Build

Replace the v3 template scaffold with a deterministic local actuator-asymmetry benchmark for mobile and manipulation control.

### Splits

- `balanced_nominal`: mild actuator mismatch.
- `left_right_gain_shift`: asymmetric left/right or joint-pair gain.
- `deadzone_saturation_shift`: sign-dependent deadzone and saturation.
- `thermal_drift_shift`: asymmetry evolves during rollout.
- `combined_hard_shift`: gain, deadzone, saturation, latency, and drift together.

### Tasks

- differential-drive corridor tracking.
- two-wheel pivot alignment.
- two-joint reach.
- gripper slide insertion.

### Methods

- `nominal_policy`
- `domain_randomized_policy`
- `scalar_gain_calibration`
- `online_system_id`
- `adaptive_mpc`
- `robust_tube_mpc`
- `latent_asymmetry_policy_state` (proposed)
- `oracle_asymmetry_state`

### Main Metrics

- trajectory/task success.
- tracking error.
- safety violation rate.
- actuator energy.
- adaptation regret.
- asymmetry estimation error.
- calibration error.
- paired seed-level differences versus strongest baselines.

### Ablations

- full latent-asymmetry policy state.
- minus persistent latent memory.
- minus sign-specific asymmetry.
- minus deadzone/saturation state.
- minus online residual update.
- scalar-only latent gain.
- no safety-aware action clipping.

### Stress Tests

- gain asymmetry.
- deadzone/saturation.
- latency.
- thermal drift.
- combined stress.

### Terminal Gate

Mark `STRONG_REVISE` only if the proposed model beats the strongest non-oracle baseline on combined hard-shift task success, tracking error, and safety, while ablations degrade the mechanism. Otherwise mark `KILL_ARCHIVE`.

Even a `STRONG_REVISE` result is not ICLR-main ready without robot hardware or accepted high-fidelity benchmark validation.
