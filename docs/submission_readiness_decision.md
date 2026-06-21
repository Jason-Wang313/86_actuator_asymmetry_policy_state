# Submission Readiness Decision

Decision: KILL_ARCHIVE

Last update: 2026-06-22 00:42 +08:00

ICLR main-conference readiness: NO.

Reason: The v5 expanded rerun confirms a promising but non-submission-ready result. The belief-state method improves predefined hard-aggregate task success over v4 (`0.14566 +/- 0.01168` vs `0.12413 +/- 0.00938`, paired success lower95 `0.00502`), and it survives maximum combined-stress Pareto domination. However, hard-aggregate tracking is worse (`0.70018` vs `0.68686`), hard-aggregate safety violation is worse (`0.30466` vs `0.28271`), the mechanism gate fails, fixed-risk budget `0.05` has zero accepted coverage, absolute success remains low, and the evidence still lacks real-robot or accepted high-fidelity simulator validation.

Honest terminal action: archive/kill for ICLR main. Do not submit this paper to ICLR main in its current form.

Revival condition: rebuild as a real empirical robotics paper with robot or accepted high-fidelity actuator-fault/asymmetry data, implemented learned controllers, strong adaptive/control-barrier/MPC/fault-observer baselines, manual related work, decisive success/tracking gains, no safety regression against v4 or fault observers, calibrated nonzero fixed-risk coverage, and an external benchmark story that survives hostile review.
