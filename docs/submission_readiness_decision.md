# Submission Readiness Decision

Decision: KILL_ARCHIVE

Last update: 2026-06-15 09:52:18 +01:00

ICLR main-conference readiness: NO.

Reason: The 2026-06-15 v4 rerun confirms a promising but non-submission-ready result. The latent-asymmetry policy improves combined hard-shift task success over online system ID (`0.15079` vs `0.09921`, paired gain `0.05159 +/- 0.02483`) and improves tracking/asymmetry error, with ablations supporting persistent non-scalar asymmetry state. However, hard-split safety does not decisively beat online system ID (`0.18730` vs `0.18396` safety violation), absolute hard-shift success remains low, and the evidence still lacks real-robot or accepted high-fidelity simulator validation.

Honest terminal action: archive/kill for ICLR main. Do not submit this paper to ICLR main in its current form.

Revival condition: rebuild as a real empirical robotics paper with robot or accepted high-fidelity actuator-fault/asymmetry data, implemented learned controllers, strong adaptive/control-barrier/MPC baselines, manual related work, decisive success/tracking gains, and no safety regression against online system identification.
