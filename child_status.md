# Child Status 86

Current stage: ICLR main v5 expanded submission-readiness audit terminal
Last update: 2026-06-22 00:42 +08:00
PDF: C:/Users/wangz/Downloads/86.pdf
PDF pages: 29
PDF SHA256: B9BCA5A27CD6F5B14032E146AEC84D75B035C245131D777057B44089495BF826
GitHub: https://github.com/Jason-Wang313/86_actuator_asymmetry_policy_state
Submission-hardening version: v5 expanded
Terminal decision: KILL_ARCHIVE
ICLR main ready: no

Reason: the v5 full rerun regenerated 199,680 main rollouts, 15,360 actuator summaries, 33,600 ablation rollouts, 302,400 stress rows, 69,120 fixed-risk rows, and 24 negative cases. The belief-state method has a real hard-aggregate success gain over v4 (`0.14566 +/- 0.01168` vs `0.12413 +/- 0.00938`, paired lower95 `0.00502`), but it fails tracking (`0.70018` vs `0.68686`), safety (`0.30466` vs `0.28271`), mechanism, fixed-risk, and scope gates. No robot hardware or accepted high-fidelity simulator validation is available.
