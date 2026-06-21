# Claims

- Mechanism claim retained: actuator asymmetry can be represented as latent policy state rather than compressed into scalar calibration.
- Evidence claim retained: the v5 synthetic benchmark tests gain asymmetry, deadzone/saturation, latency, thermal drift, intermittent faults, payload/contact shift, stress sweeps, fixed-risk acceptance, and ablations against strong adaptive/control-barrier/fault-observer baselines.
- Positive local result retained: `latent_asymmetry_belief_policy_v5` improves hard-aggregate task success over v4 with paired lower95 `0.00502`.
- Negative result retained: the same method worsens hard-aggregate tracking and safety relative to v4, fails the mechanism gate, and has zero fixed-risk coverage at budget `0.05`.
- Scope claim: results support mechanism plausibility only; they do not support real-robot deployment.
- Unsupported claims explicitly avoided: no SOTA robot performance, no safety dominance, no ICLR-main readiness, no hardware validation, and no accepted high-fidelity benchmark claim.
