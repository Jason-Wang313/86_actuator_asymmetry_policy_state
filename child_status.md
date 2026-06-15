# Child Status 86

Current stage: ICLR main v4 evidence audit terminal
Last update: 2026-06-15 09:52:18 +01:00
PDF: C:/Users/wangz/Downloads/86.pdf
GitHub: https://github.com/Jason-Wang313/86_actuator_asymmetry_policy_state
Submission-hardening version: v4
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Reason: the 2026-06-15 full rerun regenerated 40,320 main rollouts, 7,056 ablation rollouts, and 100,800 stress rollouts. The latent-asymmetry policy has a real local success gain over online system ID (`0.05159 +/- 0.02483`) and improves tracking/asymmetry error, but hard-split safety does not decisively beat online system ID (`0.18730` vs `0.18396`) and no robot hardware or accepted high-fidelity simulator validation is available.
