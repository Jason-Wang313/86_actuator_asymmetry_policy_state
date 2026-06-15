        # Hostile Reviewer Response

        Paper: 86 Actuator Asymmetry as Policy State

        ## Strongest Technical Threats
        - Maximum principle for stochastic optimal control problem of finite state forward-backward stochastic difference systems (2022)
- Nonlinear Model Predictive Control with Enhanced Actuator Model for Multi-Rotor Aerial Vehicles with Generic Designs (2020)
- Fast, Safe and Robust Motion Planning for Autonomous Vehicles Based on Robust Control Invariant Tubes (2025)
- Adaptive State Tracking Control with Actuator Nonlinearities and Failures (2020)
- Observer-based robust control for flexible-joint robot manipulators: A state-dependent Riccati equation-based approach (2020)
- Asymmetry in Skipping Enhances Viability Against Control Input Noise (2026)
- Multimodal AI: PaLM-E's Role in Vision-Language-Robotics & the Future of Efficient Fine-Tuning (2026)
- Rollover Prevention for Mobile Robots With Control Barrier Functions: Differentiator-Based Adaptation and Projection-to-State Safety (2024)

        ## ICLR Main Response
        A hostile ICLR reviewer would be correct to reject this as a main-conference submission. The v4 paper has reproducible synthetic evidence and careful limitations, but it does not contain the real robot, high-fidelity simulator, learned controller, or manual related-work depth needed for the ICLR main track. The 2026-06-15 rerun shows a real local success/tracking gain, but hard-split safety does not decisively beat online system ID.

        ## Honest Action
        The paper is marked `KILL_ARCHIVE`. This avoids converting a generated workshop-style idea into an overstated main-conference claim.

        ## What Would Be Needed To Revive
        - Real robot or high-fidelity benchmark experiments.
        - Implemented model and baselines, not synthetic probability tables.
        - Manual full-paper related-work audit.
        - Paper-specific writing and figures.
        - Evidence that the core mechanism is learned and useful under deployment shift.
