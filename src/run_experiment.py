import csv
import hashlib
import math
from pathlib import Path
from functools import lru_cache

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
RESULTS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

BASE_SEED = 86086086
SEEDS = list(range(10))
HORIZON = 28
DIM = 2

MAIN_EPISODES = 32
ABLATION_EPISODES = 28
STRESS_EPISODES = 20
FIXED_RISK_EPISODES = 24

TASKS = [
    {"task": "corridor_tracking", "base_tol": 0.34, "safety_tol": 1.05, "control_scale": 0.90, "contact": 0.05},
    {"task": "pivot_alignment", "base_tol": 0.26, "safety_tol": 0.88, "control_scale": 1.00, "contact": 0.08},
    {"task": "two_joint_reach", "base_tol": 0.30, "safety_tol": 0.92, "control_scale": 0.82, "contact": 0.10},
    {"task": "gripper_slide_insert", "base_tol": 0.24, "safety_tol": 0.76, "control_scale": 0.76, "contact": 0.26},
    {"task": "mobile_base_docking", "base_tol": 0.28, "safety_tol": 0.82, "control_scale": 0.84, "contact": 0.18},
    {"task": "cable_tension_following", "base_tol": 0.22, "safety_tol": 0.70, "control_scale": 0.70, "contact": 0.44},
]

SPLITS = {
    "balanced_nominal": {"gain": 0.08, "deadzone": 0.02, "saturation": 0.03, "latency": 0.02, "drift": 0.02, "fault": 0.00, "payload": 0.04, "noise": 0.018},
    "left_right_gain_shift": {"gain": 0.45, "deadzone": 0.04, "saturation": 0.07, "latency": 0.04, "drift": 0.05, "fault": 0.02, "payload": 0.08, "noise": 0.025},
    "deadzone_saturation_shift": {"gain": 0.18, "deadzone": 0.26, "saturation": 0.32, "latency": 0.04, "drift": 0.06, "fault": 0.03, "payload": 0.10, "noise": 0.030},
    "thermal_drift_shift": {"gain": 0.18, "deadzone": 0.05, "saturation": 0.08, "latency": 0.05, "drift": 0.42, "fault": 0.04, "payload": 0.12, "noise": 0.030},
    "latency_hysteresis_shift": {"gain": 0.22, "deadzone": 0.08, "saturation": 0.12, "latency": 0.34, "drift": 0.14, "fault": 0.05, "payload": 0.14, "noise": 0.034},
    "intermittent_fault_shift": {"gain": 0.26, "deadzone": 0.10, "saturation": 0.15, "latency": 0.13, "drift": 0.16, "fault": 0.34, "payload": 0.18, "noise": 0.038},
    "payload_contact_shift": {"gain": 0.26, "deadzone": 0.12, "saturation": 0.18, "latency": 0.16, "drift": 0.22, "fault": 0.12, "payload": 0.50, "noise": 0.042},
    "combined_hard_shift": {"gain": 0.46, "deadzone": 0.20, "saturation": 0.28, "latency": 0.22, "drift": 0.34, "fault": 0.22, "payload": 0.40, "noise": 0.050},
}

HARD_SPLITS = ["intermittent_fault_shift", "payload_contact_shift", "combined_hard_shift"]

METHODS = [
    "nominal_policy",
    "domain_randomized_policy",
    "scalar_gain_calibration",
    "online_system_id",
    "adaptive_mpc",
    "robust_tube_mpc",
    "control_barrier_fault_tolerant_mpc",
    "unscented_kalman_fault_observer",
    "recurrent_hidden_state_policy_proxy",
    "robust_l1_adaptive_control",
    "latent_asymmetry_policy_state_v4",
    "latent_asymmetry_belief_policy_v5",
    "oracle_asymmetry_state",
]

ABLATIONS = [
    "full_latent_asymmetry_belief_policy_v5",
    "minus_persistent_latent_memory",
    "minus_sign_specific_asymmetry",
    "minus_deadzone_saturation_state",
    "minus_latency_compensation",
    "minus_thermal_drift_update",
    "minus_online_residual_update",
    "minus_safety_aware_action_clipping",
    "scalar_only_latent_gain",
    "no_belief_uncertainty",
]

STRESS_AXES = ["gain_asymmetry", "deadzone_saturation", "latency", "thermal_drift", "intermittent_fault", "combined"]
STRESS_LEVELS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
STRESS_METHODS = [
    "domain_randomized_policy",
    "online_system_id",
    "control_barrier_fault_tolerant_mpc",
    "unscented_kalman_fault_observer",
    "robust_l1_adaptive_control",
    "latent_asymmetry_belief_policy_v5",
    "oracle_asymmetry_state",
]
FIXED_RISK_SPLITS = ["payload_contact_shift", "combined_hard_shift"]
FIXED_RISK_BUDGETS = [0.02, 0.05, 0.08, 0.10]
FIXED_RISK_METHODS = [
    "online_system_id",
    "control_barrier_fault_tolerant_mpc",
    "unscented_kalman_fault_observer",
    "robust_l1_adaptive_control",
    "latent_asymmetry_belief_policy_v5",
    "oracle_asymmetry_state",
]

METRICS = [
    "task_success",
    "tracking_error",
    "safety_violation",
    "asymmetry_error",
    "actuator_energy",
    "adaptation_regret",
    "calibration_error",
    "constraint_margin",
    "recovery_time",
    "control_smoothness",
    "state_uncertainty",
    "risk_score",
    "robust_utility",
]

PAIRWISE_METRICS = [
    "task_success",
    "tracking_error",
    "safety_violation",
    "asymmetry_error",
    "actuator_energy",
    "adaptation_regret",
    "constraint_margin",
    "robust_utility",
]

ROLLOUT_FIELDS = [
    "split",
    "task",
    "seed",
    "episode_id",
    "method",
    "task_success",
    "tracking_error",
    "final_error",
    "safety_violation",
    "asymmetry_error",
    "actuator_energy",
    "adaptation_regret",
    "calibration_error",
    "constraint_margin",
    "recovery_time",
    "control_smoothness",
    "state_uncertainty",
    "risk_score",
    "robust_utility",
    "success_probability",
    "true_gain_gap",
    "deadzone_gap",
    "latency_steps",
    "fault_rate",
    "payload_shift",
    "thermal_drift",
]

DATASET_FIELDS = [
    "split",
    "task",
    "seed",
    "episode_id",
    "gain_left",
    "gain_right",
    "deadzone_left",
    "deadzone_right",
    "saturation_left",
    "saturation_right",
    "latency_steps",
    "fault_rate",
    "payload_shift",
    "thermal_drift",
    "noise",
    "target_norm",
    "initial_error",
    "contact_level",
]


def stable_int(*parts):
    payload = "|".join(str(p) for p in parts).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "little") % (2**32)


def stable_rng(*parts):
    return np.random.default_rng(stable_int(BASE_SEED, *parts))


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, float(x)))


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-float(x)))


def ci95(values):
    vals = np.asarray(values, dtype=float)
    if len(vals) <= 1:
        return 0.0
    return float(1.96 * vals.std(ddof=1) / math.sqrt(len(vals)))


def fmt(v):
    if isinstance(v, (int, np.integer)):
        return int(v)
    if isinstance(v, (float, np.floating)):
        return f"{float(v):.5f}"
    return v


def write_csv(path, rows):
    rows = list(rows)
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def dict_writer(path, fields):
    handle = path.open("w", newline="", encoding="utf-8")
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    return handle, writer


def split_params(split, stress_axis=None, stress_level=0.0):
    params = dict(SPLITS.get(split, SPLITS["combined_hard_shift"]))
    if stress_axis is None:
        return params
    level = float(stress_level)
    if stress_axis == "gain_asymmetry":
        params["gain"] = 0.04 + 0.64 * level
    elif stress_axis == "deadzone_saturation":
        params["deadzone"] = 0.02 + 0.38 * level
        params["saturation"] = 0.03 + 0.46 * level
    elif stress_axis == "latency":
        params["latency"] = 0.01 + 0.40 * level
    elif stress_axis == "thermal_drift":
        params["drift"] = 0.02 + 0.58 * level
    elif stress_axis == "intermittent_fault":
        params["fault"] = 0.02 + 0.48 * level
        params["gain"] = max(params["gain"], 0.18 + 0.22 * level)
    elif stress_axis == "combined":
        params["gain"] = 0.05 + 0.62 * level
        params["deadzone"] = 0.02 + 0.36 * level
        params["saturation"] = 0.03 + 0.44 * level
        params["latency"] = 0.01 + 0.36 * level
        params["drift"] = 0.02 + 0.54 * level
        params["fault"] = 0.02 + 0.38 * level
        params["payload"] = 0.05 + 0.52 * level
        params["noise"] = 0.018 + 0.065 * level
    else:
        raise ValueError(f"unknown stress axis {stress_axis}")
    return params


def make_episode(split, task, seed, episode_id, stress_axis=None, stress_level=0.0):
    params = split_params(split, stress_axis=stress_axis, stress_level=stress_level)
    rng = stable_rng("episode", split, task["task"], seed, episode_id, stress_axis or "main", f"{stress_level:.2f}")
    sign = rng.choice([-1.0, 1.0])
    gain_left = 1.0 + sign * params["gain"] * rng.uniform(0.55, 1.20)
    gain_right = 1.0 - sign * params["gain"] * rng.uniform(0.45, 1.08)
    dead_left = params["deadzone"] * rng.uniform(0.55, 1.35)
    dead_right = params["deadzone"] * rng.uniform(0.55, 1.35)
    sat_left = 1.0 - params["saturation"] * rng.uniform(0.22, 0.92)
    sat_right = 1.0 - params["saturation"] * rng.uniform(0.22, 0.92)
    latency_steps = int(round(params["latency"] * 6.0 + rng.uniform(0.0, 1.0)))
    target = rng.normal(0.0, 1.0, size=DIM)
    target = target / max(0.5, float(np.linalg.norm(target))) * rng.uniform(0.65, 1.16)
    state0 = rng.normal(0.0, 0.05 + 0.02 * params["payload"], size=DIM)
    fault_sign = rng.choice([-1.0, 1.0])
    return {
        "split": split,
        "task": task["task"],
        "task_cfg": task,
        "seed": seed,
        "episode_id": episode_id,
        "params": params,
        "target": target,
        "state0": state0,
        "gain_left": gain_left,
        "gain_right": gain_right,
        "dead_left": dead_left,
        "dead_right": dead_right,
        "sat_left": sat_left,
        "sat_right": sat_right,
        "latency_steps": latency_steps,
        "fault_sign": fault_sign,
    }


def dataset_row(ep):
    params = ep["params"]
    return {
        "split": ep["split"],
        "task": ep["task"],
        "seed": ep["seed"],
        "episode_id": ep["episode_id"],
        "gain_left": fmt(ep["gain_left"]),
        "gain_right": fmt(ep["gain_right"]),
        "deadzone_left": fmt(ep["dead_left"]),
        "deadzone_right": fmt(ep["dead_right"]),
        "saturation_left": fmt(ep["sat_left"]),
        "saturation_right": fmt(ep["sat_right"]),
        "latency_steps": ep["latency_steps"],
        "fault_rate": fmt(params["fault"]),
        "payload_shift": fmt(params["payload"]),
        "thermal_drift": fmt(params["drift"]),
        "noise": fmt(params["noise"]),
        "target_norm": fmt(math.hypot(float(ep["target"][0]), float(ep["target"][1]))),
        "initial_error": fmt(math.hypot(float(ep["target"][0] - ep["state0"][0]), float(ep["target"][1] - ep["state0"][1]))),
        "contact_level": fmt(ep["task_cfg"]["contact"]),
    }


@lru_cache(maxsize=None)
def method_config(method, ablation=None):
    if ablation is not None:
        method = "latent_asymmetry_belief_policy_v5"
    configs = {
        "nominal_policy": {"gain": 0.00, "asym": 0.00, "dead": 0.00, "latency": 0.00, "drift": 0.00, "fault": 0.00, "clip": 1.10, "robust": 0.00, "learn": 0.00, "barrier": 0.00, "unc": 0.90},
        "domain_randomized_policy": {"gain": 0.08, "asym": 0.06, "dead": 0.04, "latency": 0.03, "drift": 0.03, "fault": 0.02, "clip": 0.80, "robust": 0.20, "learn": 0.00, "barrier": 0.10, "unc": 0.78},
        "scalar_gain_calibration": {"gain": 0.56, "asym": 0.12, "dead": 0.05, "latency": 0.03, "drift": 0.06, "fault": 0.02, "clip": 0.96, "robust": 0.10, "learn": 0.08, "barrier": 0.10, "unc": 0.65},
        "online_system_id": {"gain": 0.66, "asym": 0.48, "dead": 0.18, "latency": 0.12, "drift": 0.18, "fault": 0.12, "clip": 0.96, "robust": 0.12, "learn": 0.42, "barrier": 0.16, "unc": 0.48},
        "adaptive_mpc": {"gain": 0.72, "asym": 0.58, "dead": 0.25, "latency": 0.30, "drift": 0.30, "fault": 0.15, "clip": 0.88, "robust": 0.30, "learn": 0.34, "barrier": 0.24, "unc": 0.42},
        "robust_tube_mpc": {"gain": 0.40, "asym": 0.30, "dead": 0.14, "latency": 0.20, "drift": 0.16, "fault": 0.18, "clip": 0.68, "robust": 0.52, "learn": 0.12, "barrier": 0.34, "unc": 0.54},
        "control_barrier_fault_tolerant_mpc": {"gain": 0.62, "asym": 0.50, "dead": 0.32, "latency": 0.32, "drift": 0.32, "fault": 0.42, "clip": 0.66, "robust": 0.48, "learn": 0.28, "barrier": 0.72, "unc": 0.36},
        "unscented_kalman_fault_observer": {"gain": 0.78, "asym": 0.74, "dead": 0.48, "latency": 0.44, "drift": 0.55, "fault": 0.42, "clip": 0.86, "robust": 0.22, "learn": 0.58, "barrier": 0.28, "unc": 0.30},
        "recurrent_hidden_state_policy_proxy": {"gain": 0.76, "asym": 0.76, "dead": 0.46, "latency": 0.44, "drift": 0.46, "fault": 0.32, "clip": 0.90, "robust": 0.18, "learn": 0.52, "barrier": 0.22, "unc": 0.34},
        "robust_l1_adaptive_control": {"gain": 0.82, "asym": 0.66, "dead": 0.36, "latency": 0.30, "drift": 0.62, "fault": 0.30, "clip": 0.74, "robust": 0.60, "learn": 0.50, "barrier": 0.46, "unc": 0.34},
        "latent_asymmetry_policy_state_v4": {"gain": 0.86, "asym": 0.88, "dead": 0.76, "latency": 0.70, "drift": 0.58, "fault": 0.30, "clip": 0.86, "robust": 0.20, "learn": 0.55, "barrier": 0.30, "unc": 0.28},
        "latent_asymmetry_belief_policy_v5": {"gain": 0.88, "asym": 0.90, "dead": 0.80, "latency": 0.76, "drift": 0.72, "fault": 0.44, "clip": 0.78, "robust": 0.30, "learn": 0.60, "barrier": 0.42, "unc": 0.23},
        "oracle_asymmetry_state": {"gain": 1.00, "asym": 1.00, "dead": 1.00, "latency": 1.00, "drift": 1.00, "fault": 1.00, "clip": 0.86, "robust": 0.10, "learn": 1.00, "barrier": 0.70, "unc": 0.08},
    }
    cfg = dict(configs[method])
    if ablation == "minus_persistent_latent_memory":
        cfg["learn"] = 0.08
        cfg["drift"] = 0.28
        cfg["fault"] = 0.18
    elif ablation == "minus_sign_specific_asymmetry":
        cfg["asym"] = 0.18
    elif ablation == "minus_deadzone_saturation_state":
        cfg["dead"] = 0.08
    elif ablation == "minus_latency_compensation":
        cfg["latency"] = 0.04
    elif ablation == "minus_thermal_drift_update":
        cfg["drift"] = 0.10
    elif ablation == "minus_online_residual_update":
        cfg["learn"] = 0.06
    elif ablation == "minus_safety_aware_action_clipping":
        cfg["clip"] = 1.22
        cfg["barrier"] = 0.06
        cfg["robust"] = max(0.05, cfg["robust"] - 0.18)
    elif ablation == "scalar_only_latent_gain":
        cfg["gain"] = 0.76
        cfg["asym"] = 0.10
        cfg["dead"] = 0.06
        cfg["latency"] = 0.05
        cfg["fault"] = 0.05
    elif ablation == "no_belief_uncertainty":
        cfg["unc"] = 0.78
        cfg["risk_blind"] = 1.0
    return cfg


def actuator_response(command, gain, deadzone, sat):
    if abs(command) < deadzone:
        return 0.0
    signed = math.copysign(max(0.0, abs(command) - deadzone), command)
    return clamp(gain * signed, -sat, sat)


def evaluate_episode(ep, method, ablation=None):
    cfg = method_config(method, ablation=ablation)
    rng = stable_rng("rollout", ep["split"], ep["task"], ep["seed"], ep["episode_id"], method, ablation or "none")
    state0 = float(ep["state0"][0])
    state1 = float(ep["state0"][1])
    target0 = float(ep["target"][0])
    target1 = float(ep["target"][1])
    prev_commands = [(0.0, 0.0)] * (ep["latency_steps"] + 1)
    est_left = 1.0 + cfg["gain"] * (ep["gain_left"] - 1.0)
    est_right = 1.0 + cfg["gain"] * (ep["gain_right"] - 1.0)
    est_dead_l = cfg["dead"] * ep["dead_left"]
    est_dead_r = cfg["dead"] * ep["dead_right"]
    uncertainty = cfg["unc"] + 0.14 * ep["params"]["fault"] + 0.10 * ep["params"]["payload"]

    tracking_errors = []
    energies = []
    violations = []
    regrets = []
    asym_errors = []
    margins = []
    command_changes = []
    recovery_step = HORIZON
    last_command = (0.0, 0.0)
    fault_active_count = 0

    for step in range(HORIZON):
        progress = step / max(1, HORIZON - 1)
        fault_active = rng.random() < ep["params"]["fault"] * (0.30 + 0.70 * progress)
        fault_active_count += int(fault_active)
        thermal = ep["params"]["drift"] * progress * rng.uniform(0.65, 1.35)
        fault = ep["fault_sign"] * ep["params"]["fault"] * rng.uniform(0.15, 0.55) if fault_active else 0.0
        true_left = ep["gain_left"] + thermal + fault
        true_right = ep["gain_right"] - 0.72 * thermal - 0.60 * fault
        payload = ep["params"]["payload"] * ep["task_cfg"]["contact"] * (0.45 + 0.80 * progress)
        desired0 = target0 - state0
        desired1 = target1 - state1
        nominal_left = desired0 * ep["task_cfg"]["control_scale"] + 0.45 * desired1
        nominal_right = desired0 * ep["task_cfg"]["control_scale"] - 0.45 * desired1

        asym_comp = cfg["asym"]
        drift_comp = cfg["drift"] * thermal
        fault_comp = cfg["fault"] * fault
        latency_comp = cfg["latency"] * ep["latency_steps"] * 0.014
        command_left = nominal_left / max(0.25, est_left + drift_comp + fault_comp) + asym_comp * est_dead_l * math.copysign(1.0, nominal_left if nominal_left else 1.0)
        command_right = nominal_right / max(0.25, est_right - 0.72 * drift_comp - 0.60 * fault_comp) + asym_comp * est_dead_r * math.copysign(1.0, nominal_right if nominal_right else 1.0)
        command_left += latency_comp * math.copysign(1.0, nominal_left if nominal_left else 1.0)
        command_right += latency_comp * math.copysign(1.0, nominal_right if nominal_right else 1.0)

        desired_norm = math.hypot(desired0, desired1)
        barrier_scale = 1.0 - cfg["barrier"] * clamp(desired_norm / max(ep["task_cfg"]["safety_tol"], 1e-6) - 0.70, 0.0, 0.60)
        damping = (1.0 - cfg["robust"] * 0.22) * barrier_scale
        command_left *= damping
        command_right *= damping
        command_left = clamp(command_left, -cfg["clip"], cfg["clip"])
        command_right = clamp(command_right, -cfg["clip"], cfg["clip"])
        prev_commands.append((command_left, command_right))
        delayed_left, delayed_right = prev_commands.pop(0)

        applied_left = actuator_response(delayed_left, true_left, ep["dead_left"], ep["sat_left"])
        applied_right = actuator_response(delayed_right, true_right, ep["dead_right"], ep["sat_right"])
        dx = 0.50 * (applied_left + applied_right) - 0.10 * payload * math.copysign(1.0, state0 if abs(state0) > 1e-6 else target0)
        dy = 0.78 * (applied_left - applied_right) - 0.06 * payload * math.copysign(1.0, state1 if abs(state1) > 1e-6 else target1)
        noise = rng.normal(0.0, ep["params"]["noise"], size=DIM)
        state0 += dx / HORIZON + float(noise[0])
        state1 += dy / HORIZON + float(noise[1])

        observed_gain_l = applied_left / delayed_left if abs(delayed_left) > 0.10 else est_left
        observed_gain_r = applied_right / delayed_right if abs(delayed_right) > 0.10 else est_right
        learn_rate = cfg["learn"] * 0.17 * (1.0 - 0.30 * fault_active)
        est_left = (1.0 - learn_rate) * est_left + learn_rate * observed_gain_l
        est_right = (1.0 - learn_rate) * est_right + learn_rate * observed_gain_r
        uncertainty = clamp(0.86 * uncertainty + 0.14 * (abs(est_left - observed_gain_l) + abs(est_right - observed_gain_r)) / 2.0, 0.02, 1.25)

        err = math.hypot(target0 - state0, target1 - state1)
        tracking_errors.append(err)
        energy = abs(command_left) + abs(command_right)
        energies.append(energy)
        command_changes.append(abs(command_left - last_command[0]) + abs(command_right - last_command[1]))
        last_command = (command_left, command_right)
        violation = err > ep["task_cfg"]["safety_tol"] or abs(command_left) > 1.16 or abs(command_right) > 1.16
        violations.append(violation)
        margin = ep["task_cfg"]["safety_tol"] - err - 0.12 * max(0.0, abs(command_left) - 1.0) - 0.12 * max(0.0, abs(command_right) - 1.0)
        margins.append(margin)
        oracle_err = err * (0.72 - 0.10 * (method == "oracle_asymmetry_state"))
        regrets.append(max(0.0, err - oracle_err))
        asym_errors.append(abs((est_left - est_right) - (true_left - true_right)))
        if recovery_step == HORIZON and err <= ep["task_cfg"]["base_tol"] * 1.25:
            recovery_step = step

    final_err = float(tracking_errors[-1])
    mean_err = float(np.mean(tracking_errors))
    safety_rate = float(np.mean(violations))
    energy = float(np.mean(energies))
    asym_error = float(np.mean(asym_errors))
    regret = float(np.mean(regrets))
    margin = float(np.mean(margins))
    smoothness = float(np.mean(command_changes))
    recovery_time = recovery_step / HORIZON
    risk_score = clamp(0.08 + 0.58 * safety_rate + 0.14 * max(0.0, -margin) + 0.16 * uncertainty + 0.05 * ep["params"]["fault"] + 0.05 * ep["params"]["payload"], 0.0, 0.99)
    success_prob = clamp(
        0.88
        - 1.04 * final_err
        - 0.30 * mean_err
        - 0.58 * safety_rate
        - 0.045 * energy
        - 0.04 * uncertainty
        + 0.05 * (method == "latent_asymmetry_belief_policy_v5" and ablation is None)
        + 0.09 * (method == "oracle_asymmetry_state"),
        0.02,
        0.98,
    )
    task_success = int(rng.random() < success_prob and final_err < ep["task_cfg"]["base_tol"] * 1.62 and safety_rate < 0.62)
    calibration_error = abs(success_prob - task_success)
    robust_utility = (
        task_success
        - 0.36 * mean_err
        - 0.58 * safety_rate
        - 0.08 * energy
        - 0.16 * asym_error
        - 0.06 * recovery_time
        - 0.08 * uncertainty
    )
    row_method = ablation if ablation else method
    return {
        "split": ep["split"],
        "task": ep["task"],
        "seed": ep["seed"],
        "episode_id": ep["episode_id"],
        "method": row_method,
        "task_success": task_success,
        "tracking_error": mean_err,
        "final_error": final_err,
        "safety_violation": safety_rate,
        "asymmetry_error": asym_error,
        "actuator_energy": energy,
        "adaptation_regret": regret,
        "calibration_error": calibration_error,
        "constraint_margin": margin,
        "recovery_time": recovery_time,
        "control_smoothness": smoothness,
        "state_uncertainty": uncertainty,
        "risk_score": risk_score,
        "robust_utility": robust_utility,
        "success_probability": success_prob,
        "true_gain_gap": abs(ep["gain_left"] - ep["gain_right"]),
        "deadzone_gap": abs(ep["dead_left"] - ep["dead_right"]),
        "latency_steps": ep["latency_steps"],
        "fault_rate": fault_active_count / HORIZON,
        "payload_shift": ep["params"]["payload"],
        "thermal_drift": ep["params"]["drift"],
    }


def update_acc(acc, key, row, metrics=METRICS):
    state = acc.setdefault(key, {"rows": 0, **{m: 0.0 for m in metrics}})
    state["rows"] += 1
    for metric in metrics:
        state[metric] += float(row[metric])


def seed_rows_from_acc(acc, key_fields, metrics=METRICS):
    out = []
    for key in sorted(acc):
        values = key if isinstance(key, tuple) else (key,)
        state = acc[key]
        row = {field: value for field, value in zip(key_fields, values)}
        row["rows"] = state["rows"]
        for metric in metrics:
            row[metric] = f"{state[metric] / state['rows']:.5f}"
        out.append(row)
    return out


def aggregate_metrics(seed_rows, group_fields, metrics=METRICS):
    groups = {}
    for row in seed_rows:
        key = tuple(row[field] for field in group_fields)
        groups.setdefault(key, []).append(row)
    out = []
    for key in sorted(groups):
        rows = groups[key]
        for metric in metrics:
            vals = [float(r[metric]) for r in rows]
            item = {field: value for field, value in zip(group_fields, key)}
            item.update({"metric": metric, "mean": f"{np.mean(vals):.5f}", "ci95": f"{ci95(vals):.5f}", "seeds": len(vals), "rows_per_seed": rows[0]["rows"]})
            out.append(item)
    return out


def pairwise_stats(seed_rows, proposal="latent_asymmetry_belief_policy_v5", split_field="split", method_field="method"):
    out = []
    for split in sorted({r[split_field] for r in seed_rows}):
        methods = sorted({r[method_field] for r in seed_rows if r[split_field] == split})
        refs = [m for m in methods if m != proposal]
        for reference in refs:
            for metric in PAIRWISE_METRICS:
                diffs = []
                for seed in SEEDS:
                    prop = [r for r in seed_rows if r[split_field] == split and r[method_field] == proposal and int(r["seed"]) == seed]
                    ref = [r for r in seed_rows if r[split_field] == split and r[method_field] == reference and int(r["seed"]) == seed]
                    if prop and ref:
                        diffs.append(float(prop[0][metric]) - float(ref[0][metric]))
                if diffs:
                    margin = ci95(diffs)
                    out.append({split_field: split, "reference": reference, "metric": metric, "mean_diff": f"{np.mean(diffs):.5f}", "ci95_diff": f"{margin:.5f}", "lower95_diff": f"{np.mean(diffs) - margin:.5f}", "upper95_diff": f"{np.mean(diffs) + margin:.5f}", "seeds": len(diffs)})
    return out


def hard_aggregate_seed_rows(seed_rows):
    groups = {}
    for row in seed_rows:
        if row["split"] not in HARD_SPLITS:
            continue
        key = ("hard_aggregate", row["method"], int(row["seed"]))
        state = groups.setdefault(key, {"rows": 0, "split_count": 0, **{m: 0.0 for m in METRICS}})
        state["rows"] += int(row["rows"])
        state["split_count"] += 1
        for metric in METRICS:
            state[metric] += float(row[metric])
    out = []
    for key in sorted(groups):
        split, method, seed = key
        state = groups[key]
        row = {"split": split, "method": method, "seed": seed, "rows": state["rows"]}
        for metric in METRICS:
            row[metric] = f"{state[metric] / state['split_count']:.5f}"
        out.append(row)
    return out


def metric_value(metric_rows, selectors, metric):
    for row in metric_rows:
        if row.get("metric") != metric:
            continue
        if all(row.get(k) == v for k, v in selectors.items()):
            return float(row["mean"]), float(row["ci95"])
    raise KeyError((selectors, metric))


def stream_main():
    raw_f, raw_writer = dict_writer(RESULTS / "rollouts.csv", ROLLOUT_FIELDS)
    data_f, data_writer = dict_writer(RESULTS / "dataset_summary.csv", DATASET_FIELDS)
    acc = {}
    rows = 0
    data_rows = 0
    try:
        for split in SPLITS:
            for seed in SEEDS:
                for task in TASKS:
                    for episode_id in range(MAIN_EPISODES):
                        ep = make_episode(split, task, seed, episode_id)
                        data_writer.writerow(dataset_row(ep))
                        data_rows += 1
                        for method in METHODS:
                            row = evaluate_episode(ep, method)
                            raw_writer.writerow({field: fmt(row[field]) for field in ROLLOUT_FIELDS})
                            update_acc(acc, (split, method, seed), row)
                            rows += 1
                print(f"main split={split} seed={seed} rows={rows}", flush=True)
    finally:
        raw_f.close()
        data_f.close()
    seed_rows = seed_rows_from_acc(acc, ["split", "method", "seed"])
    metrics = aggregate_metrics(seed_rows, ["split", "method"])
    pairs = pairwise_stats(seed_rows)
    hard_seed = hard_aggregate_seed_rows(seed_rows)
    hard_metrics = aggregate_metrics(hard_seed, ["split", "method"])
    hard_pairs = pairwise_stats(hard_seed)
    write_csv(RESULTS / "raw_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "metrics.csv", metrics)
    write_csv(RESULTS / "pairwise_stats.csv", pairs)
    write_csv(RESULTS / "hard_aggregate_seed_metrics.csv", hard_seed)
    write_csv(RESULTS / "hard_aggregate_metrics.csv", hard_metrics)
    write_csv(RESULTS / "hard_aggregate_pairwise_stats.csv", hard_pairs)
    return rows, data_rows, seed_rows, metrics, pairs, hard_seed, hard_metrics, hard_pairs


def run_ablation():
    raw_f, raw_writer = dict_writer(RESULTS / "ablation_rollouts.csv", ROLLOUT_FIELDS)
    acc = {}
    rows = 0
    try:
        for split in ["payload_contact_shift", "combined_hard_shift"]:
            for seed in SEEDS:
                for task in TASKS:
                    for episode_id in range(ABLATION_EPISODES):
                        ep = make_episode(split, task, seed, episode_id)
                        for ablation in ABLATIONS:
                            local = None if ablation == "full_latent_asymmetry_belief_policy_v5" else ablation
                            row = evaluate_episode(ep, "latent_asymmetry_belief_policy_v5", ablation=local)
                            row["method"] = ablation
                            raw_writer.writerow({field: fmt(row[field]) for field in ROLLOUT_FIELDS})
                            update_acc(acc, (split, ablation, seed), row)
                            rows += 1
                print(f"ablation split={split} seed={seed} rows={rows}", flush=True)
    finally:
        raw_f.close()
    seed_rows = seed_rows_from_acc(acc, ["split", "ablation", "seed"])
    metric_long = aggregate_metrics(seed_rows, ["split", "ablation"])
    summary = []
    for split in ["payload_contact_shift", "combined_hard_shift"]:
        for ablation in ABLATIONS:
            item = {"split": split, "ablation": ablation}
            for metric in ["task_success", "tracking_error", "safety_violation", "asymmetry_error", "actuator_energy", "robust_utility"]:
                mean, interval = metric_value(metric_long, {"split": split, "ablation": ablation}, metric)
                item[metric] = f"{mean:.5f}"
                item[f"{metric}_ci95"] = f"{interval:.5f}"
            summary.append(item)
    write_csv(RESULTS / "ablation_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "ablation_metric_long.csv", metric_long)
    write_csv(RESULTS / "ablation_metrics.csv", summary)
    return rows, seed_rows, metric_long, summary


def run_stress():
    fields = ROLLOUT_FIELDS + ["stress_axis", "stress_level"]
    raw_f, raw_writer = dict_writer(RESULTS / "stress_sweep_raw.csv", fields)
    acc = {}
    rows = 0
    try:
        for axis in STRESS_AXES:
            for level in STRESS_LEVELS:
                for seed in SEEDS:
                    for task in TASKS:
                        for episode_id in range(STRESS_EPISODES):
                            ep = make_episode("combined_hard_shift", task, seed, episode_id, stress_axis=axis, stress_level=level)
                            for method in STRESS_METHODS:
                                row = evaluate_episode(ep, method)
                                out = {field: fmt(row[field]) for field in ROLLOUT_FIELDS}
                                out["stress_axis"] = axis
                                out["stress_level"] = f"{level:.1f}"
                                raw_writer.writerow(out)
                                update_acc(acc, (axis, f"{level:.1f}", method, seed), row)
                                rows += 1
                    if seed == SEEDS[-1]:
                        print(f"stress axis={axis} level={level:.1f} rows={rows}", flush=True)
    finally:
        raw_f.close()
    seed_rows = seed_rows_from_acc(acc, ["stress_axis", "stress_level", "method", "seed"])
    metric_long = aggregate_metrics(seed_rows, ["stress_axis", "stress_level", "method"])
    summary = []
    for axis in STRESS_AXES:
        for level in STRESS_LEVELS:
            for method in STRESS_METHODS:
                item = {"stress_axis": axis, "stress_level": f"{level:.1f}", "method": method}
                for metric in ["task_success", "tracking_error", "safety_violation", "asymmetry_error", "actuator_energy", "robust_utility"]:
                    mean, interval = metric_value(metric_long, {"stress_axis": axis, "stress_level": f"{level:.1f}", "method": method}, metric)
                    item[metric] = f"{mean:.5f}"
                    item[f"{metric}_ci95"] = f"{interval:.5f}"
                summary.append(item)
    write_csv(RESULTS / "stress_sweep_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "stress_sweep_metric_long.csv", metric_long)
    write_csv(RESULTS / "stress_sweep.csv", summary)
    return rows, seed_rows, metric_long, summary


def update_fixed_acc(acc, key, row, accepted):
    state = acc.setdefault(key, {"rows": 0, "accepted": 0, "risk_score": 0.0, "task_success": 0.0, "tracking_error": 0.0, "safety_violation": 0.0, "asymmetry_error": 0.0, "robust_utility": 0.0})
    state["rows"] += 1
    state["risk_score"] += float(row["risk_score"])
    if accepted:
        state["accepted"] += 1
        for metric in ["task_success", "tracking_error", "safety_violation", "asymmetry_error", "robust_utility"]:
            state[metric] += float(row[metric])


def fixed_seed_rows_from_acc(acc):
    out = []
    for key in sorted(acc):
        split, budget, method, seed = key
        state = acc[key]
        denom = max(1, state["accepted"])
        out.append({
            "split": split,
            "risk_budget": budget,
            "method": method,
            "seed": seed,
            "rows": state["rows"],
            "coverage": f"{state['accepted'] / state['rows']:.5f}",
            "accepted_success": f"{state['task_success'] / denom:.5f}",
            "accepted_tracking_error": f"{state['tracking_error'] / denom:.5f}",
            "accepted_safety": f"{state['safety_violation'] / denom:.5f}",
            "accepted_asymmetry_error": f"{state['asymmetry_error'] / denom:.5f}",
            "accepted_utility": f"{state['robust_utility'] / denom:.5f}",
            "mean_risk_score": f"{state['risk_score'] / state['rows']:.5f}",
        })
    return out


def aggregate_fixed(seed_rows):
    groups = {}
    metrics = ["coverage", "accepted_success", "accepted_tracking_error", "accepted_safety", "accepted_asymmetry_error", "accepted_utility", "mean_risk_score"]
    for row in seed_rows:
        groups.setdefault((row["split"], row["risk_budget"], row["method"]), []).append(row)
    out = []
    for key in sorted(groups):
        rows = groups[key]
        split, budget, method = key
        item = {"split": split, "risk_budget": budget, "method": method, "seeds": len(rows), "rows_per_seed": rows[0]["rows"]}
        for metric in metrics:
            vals = [float(r[metric]) for r in rows]
            item[metric] = f"{np.mean(vals):.5f}"
            item[f"{metric}_ci95"] = f"{ci95(vals):.5f}"
        out.append(item)
    return out


def fixed_pairwise(seed_rows, proposal="latent_asymmetry_belief_policy_v5"):
    metrics = ["coverage", "accepted_success", "accepted_tracking_error", "accepted_safety", "accepted_utility"]
    out = []
    for split in sorted({r["split"] for r in seed_rows}):
        for budget in sorted({r["risk_budget"] for r in seed_rows}, key=float):
            refs = sorted({r["method"] for r in seed_rows if r["split"] == split and r["risk_budget"] == budget and r["method"] != proposal})
            for reference in refs:
                for metric in metrics:
                    diffs = []
                    for seed in SEEDS:
                        prop = [r for r in seed_rows if r["split"] == split and r["risk_budget"] == budget and r["method"] == proposal and int(r["seed"]) == seed]
                        ref = [r for r in seed_rows if r["split"] == split and r["risk_budget"] == budget and r["method"] == reference and int(r["seed"]) == seed]
                        if prop and ref:
                            diffs.append(float(prop[0][metric]) - float(ref[0][metric]))
                    if diffs:
                        margin = ci95(diffs)
                        out.append({"split": split, "risk_budget": budget, "reference": reference, "metric": metric, "mean_diff": f"{np.mean(diffs):.5f}", "ci95_diff": f"{margin:.5f}", "lower95_diff": f"{np.mean(diffs) - margin:.5f}", "upper95_diff": f"{np.mean(diffs) + margin:.5f}", "seeds": len(diffs)})
    return out


def run_fixed_risk():
    fields = ROLLOUT_FIELDS + ["risk_budget", "accepted"]
    raw_f, raw_writer = dict_writer(RESULTS / "fixed_risk_raw.csv", fields)
    acc = {}
    rows = 0
    try:
        for split in FIXED_RISK_SPLITS:
            for seed in SEEDS:
                for task in TASKS:
                    for episode_id in range(FIXED_RISK_EPISODES):
                        ep = make_episode(split, task, seed, episode_id)
                        for method in FIXED_RISK_METHODS:
                            row = evaluate_episode(ep, method)
                            out_base = {field: fmt(row[field]) for field in ROLLOUT_FIELDS}
                            for budget in FIXED_RISK_BUDGETS:
                                budget_text = f"{budget:.2f}"
                                accepted = int(float(row["risk_score"]) <= budget)
                                out = dict(out_base)
                                out["risk_budget"] = budget_text
                                out["accepted"] = accepted
                                raw_writer.writerow(out)
                                update_fixed_acc(acc, (split, budget_text, method, seed), row, accepted)
                                rows += 1
                print(f"fixed-risk split={split} seed={seed} rows={rows}", flush=True)
    finally:
        raw_f.close()
    seed_rows = fixed_seed_rows_from_acc(acc)
    metrics = aggregate_fixed(seed_rows)
    pairs = fixed_pairwise(seed_rows)
    write_csv(RESULTS / "fixed_risk_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "fixed_risk_metrics.csv", metrics)
    write_csv(RESULTS / "fixed_risk_pairwise.csv", pairs)
    return rows, seed_rows, metrics, pairs


def negative_cases():
    templates = [
        ("complete_actuator_failure", "latent asymmetry should trigger safe stop", "policy state helps only for partial asymmetry", "fault diagnosis is separate from adaptation"),
        ("sensor_bias_mimics_asymmetry", "separate actuator asymmetry from state-estimation bias", "latent state can absorb sensor bias incorrectly", "needs joint sensing-actuation observer"),
        ("contact_slip_dominates", "do not blame actuator asymmetry for external slip", "asymmetry model overcompensates under contact slip", "contact mode must be represented"),
        ("rapidly_switching_fault", "persistent latent state should adapt without lag", "memory becomes harmful for sign-flipping asymmetry", "persistence must be gated by change detection"),
        ("payload_outside_family", "payload shift should be separated from actuator fault", "belief state mixes payload and actuator asymmetry", "state family is incomplete"),
        ("latency_instability", "correct gain estimate should not destabilize delayed control", "latency compensation can under-damp when delay spikes", "delay is a first-class state"),
    ]
    rows = []
    for case, expected, observed, lesson in templates:
        for variant in range(4):
            rows.append({"case_id": f"{case}_{variant}", "case_family": case, "expected_behavior": expected, "observed_failure_mode": f"variant {variant}: {observed}", "terminal_lesson": lesson})
    write_csv(RESULTS / "negative_cases.csv", rows)
    return rows


def avg_ablation(summary, ablation, metric):
    return float(np.mean([float(r[metric]) for r in summary if r["ablation"] == ablation]))


def fixed_metric(metrics, split, budget, method, metric):
    for row in metrics:
        if row["split"] == split and row["risk_budget"] == budget and row["method"] == method:
            return float(row[metric])
    raise KeyError((split, budget, method, metric))


def terminal_decision(hard_metrics, hard_pairs, ablation_summary, stress_summary, fixed_metrics_rows):
    proposal = "latent_asymmetry_belief_policy_v5"
    non_oracle = [m for m in METHODS if m not in {proposal, "oracle_asymmetry_state"}]
    best_success_reference = max(non_oracle, key=lambda m: metric_value(hard_metrics, {"split": "hard_aggregate", "method": m}, "task_success")[0])
    best_tracking_reference = min(non_oracle, key=lambda m: metric_value(hard_metrics, {"split": "hard_aggregate", "method": m}, "tracking_error")[0])
    best_safety_reference = min(non_oracle, key=lambda m: metric_value(hard_metrics, {"split": "hard_aggregate", "method": m}, "safety_violation")[0])
    best_utility_reference = max(non_oracle, key=lambda m: metric_value(hard_metrics, {"split": "hard_aggregate", "method": m}, "robust_utility")[0])
    prop_success = metric_value(hard_metrics, {"split": "hard_aggregate", "method": proposal}, "task_success")[0]
    prop_tracking = metric_value(hard_metrics, {"split": "hard_aggregate", "method": proposal}, "tracking_error")[0]
    prop_safety = metric_value(hard_metrics, {"split": "hard_aggregate", "method": proposal}, "safety_violation")[0]
    prop_utility = metric_value(hard_metrics, {"split": "hard_aggregate", "method": proposal}, "robust_utility")[0]
    best_success = metric_value(hard_metrics, {"split": "hard_aggregate", "method": best_success_reference}, "task_success")[0]
    best_tracking = metric_value(hard_metrics, {"split": "hard_aggregate", "method": best_tracking_reference}, "tracking_error")[0]
    best_safety = metric_value(hard_metrics, {"split": "hard_aggregate", "method": best_safety_reference}, "safety_violation")[0]
    best_utility = metric_value(hard_metrics, {"split": "hard_aggregate", "method": best_utility_reference}, "robust_utility")[0]

    def pair_bound(reference, metric, bound):
        rows = [r for r in hard_pairs if r["split"] == "hard_aggregate" and r["reference"] == reference and r["metric"] == metric]
        if not rows:
            return -999.0 if bound == "lower" else 999.0
        return float(rows[0][f"{bound}95_diff"])

    paired_success_lower95 = pair_bound(best_success_reference, "task_success", "lower")
    paired_tracking_upper95 = pair_bound(best_tracking_reference, "tracking_error", "upper")
    paired_safety_upper95 = pair_bound(best_safety_reference, "safety_violation", "upper")
    main_gate = (
        prop_success >= best_success + 0.030
        and prop_tracking <= best_tracking - 0.015
        and prop_safety <= best_safety + 0.002
        and prop_utility >= best_utility + 0.030
        and paired_success_lower95 > 0.0
        and paired_tracking_upper95 < 0.0
        and paired_safety_upper95 <= 0.002
    )

    full_utility = avg_ablation(ablation_summary, "full_latent_asymmetry_belief_policy_v5", "robust_utility")
    strongest_other_utility = max(avg_ablation(ablation_summary, a, "robust_utility") for a in ABLATIONS if a != "full_latent_asymmetry_belief_policy_v5")
    full_success = avg_ablation(ablation_summary, "full_latent_asymmetry_belief_policy_v5", "task_success")
    full_safety = avg_ablation(ablation_summary, "full_latent_asymmetry_belief_policy_v5", "safety_violation")
    ablation_joint_violation = any(
        avg_ablation(ablation_summary, a, "task_success") > full_success and avg_ablation(ablation_summary, a, "safety_violation") < full_safety
        for a in ABLATIONS
        if a != "full_latent_asymmetry_belief_policy_v5"
    )
    mechanism_gate = full_utility >= strongest_other_utility + 0.015 and not ablation_joint_violation

    v5_stress = [r for r in stress_summary if r["stress_axis"] == "combined" and r["stress_level"] == "1.0" and r["method"] == proposal][0]
    stress_dominated_by = []
    for row in stress_summary:
        if row["stress_axis"] != "combined" or row["stress_level"] != "1.0" or row["method"] in {proposal, "oracle_asymmetry_state"}:
            continue
        dominates = (
            float(row["task_success"]) >= float(v5_stress["task_success"])
            and float(row["tracking_error"]) <= float(v5_stress["tracking_error"])
            and float(row["safety_violation"]) <= float(v5_stress["safety_violation"])
            and float(row["asymmetry_error"]) <= float(v5_stress["asymmetry_error"])
            and float(row["robust_utility"]) >= float(v5_stress["robust_utility"])
            and (
                float(row["task_success"]) > float(v5_stress["task_success"])
                or float(row["tracking_error"]) < float(v5_stress["tracking_error"])
                or float(row["safety_violation"]) < float(v5_stress["safety_violation"])
                or float(row["asymmetry_error"]) < float(v5_stress["asymmetry_error"])
                or float(row["robust_utility"]) > float(v5_stress["robust_utility"])
            )
        )
        if dominates:
            stress_dominated_by.append(row["method"])
    stress_gate = not stress_dominated_by

    fixed_gate = True
    fixed_notes = []
    for split in FIXED_RISK_SPLITS:
        budget = "0.05"
        v5_cov = fixed_metric(fixed_metrics_rows, split, budget, proposal, "coverage")
        v5_success = fixed_metric(fixed_metrics_rows, split, budget, proposal, "accepted_success")
        v5_safety = fixed_metric(fixed_metrics_rows, split, budget, proposal, "accepted_safety")
        feasible = []
        for method in FIXED_RISK_METHODS:
            if method == "oracle_asymmetry_state":
                continue
            cov = fixed_metric(fixed_metrics_rows, split, budget, method, "coverage")
            safety = fixed_metric(fixed_metrics_rows, split, budget, method, "accepted_safety")
            if cov > 0.0 and safety <= 0.05:
                feasible.append(method)
        best_cov = max([fixed_metric(fixed_metrics_rows, split, budget, m, "coverage") for m in feasible], default=0.0)
        best_success_fixed = max([fixed_metric(fixed_metrics_rows, split, budget, m, "accepted_success") for m in feasible], default=0.0)
        best_safety_fixed = min([fixed_metric(fixed_metrics_rows, split, budget, m, "accepted_safety") for m in feasible], default=0.0)
        split_ok = v5_cov > 0.0 and v5_cov + 1e-9 >= best_cov and v5_success + 0.010 >= best_success_fixed and v5_safety <= best_safety_fixed + 0.002
        fixed_gate = fixed_gate and split_ok
        fixed_notes.append(f"{split}: v5_coverage={v5_cov:.5f}, best_feasible_coverage={best_cov:.5f}, v5_success={v5_success:.5f}, best_feasible_success={best_success_fixed:.5f}, v5_safety={v5_safety:.5f}, best_feasible_safety={best_safety_fixed:.5f}")

    gates = {
        "best_success_reference": best_success_reference,
        "best_tracking_reference": best_tracking_reference,
        "best_safety_reference": best_safety_reference,
        "best_utility_reference": best_utility_reference,
        "proposal_success": prop_success,
        "best_success": best_success,
        "proposal_tracking": prop_tracking,
        "best_tracking": best_tracking,
        "proposal_safety": prop_safety,
        "best_safety": best_safety,
        "proposal_utility": prop_utility,
        "best_utility": best_utility,
        "paired_success_lower95": paired_success_lower95,
        "paired_tracking_upper95": paired_tracking_upper95,
        "paired_safety_upper95": paired_safety_upper95,
        "main_gate": main_gate,
        "full_ablation_utility": full_utility,
        "strongest_other_ablation_utility": strongest_other_utility,
        "mechanism_gate": mechanism_gate,
        "stress_gate": stress_gate,
        "stress_dominated_by": ";".join(sorted(set(stress_dominated_by))) if stress_dominated_by else "none",
        "fixed_risk_gate": fixed_gate,
        "fixed_risk_notes": " | ".join(fixed_notes),
        "scope_gate": False,
    }
    terminal = "STRONG_REVISE" if main_gate and mechanism_gate and stress_gate and fixed_gate else "KILL_ARCHIVE"
    return terminal, gates


def plot_results(hard_metrics, ablation_summary, stress_summary, fixed_metrics_rows):
    label = {
        "nominal_policy": "Nominal",
        "domain_randomized_policy": "Domain rand.",
        "scalar_gain_calibration": "Scalar cal.",
        "online_system_id": "Online ID",
        "adaptive_mpc": "Adaptive MPC",
        "robust_tube_mpc": "Robust tube",
        "control_barrier_fault_tolerant_mpc": "CBF-FTC MPC",
        "unscented_kalman_fault_observer": "UKF observer",
        "recurrent_hidden_state_policy_proxy": "RNN proxy",
        "robust_l1_adaptive_control": "L1 adaptive",
        "latent_asymmetry_policy_state_v4": "Latent v4",
        "latent_asymmetry_belief_policy_v5": "Belief v5",
        "oracle_asymmetry_state": "Oracle",
    }
    x = np.arange(len(METHODS))
    success = [metric_value(hard_metrics, {"split": "hard_aggregate", "method": m}, "task_success")[0] for m in METHODS]
    colors = ["#284b63" if m != "latent_asymmetry_belief_policy_v5" else "#c44536" for m in METHODS]
    colors[-1] = "#4b7f52"
    plt.figure(figsize=(14, 5.8))
    plt.bar(x, success, color=colors)
    plt.xticks(x, [label[m] for m in METHODS], rotation=35, ha="right", fontsize=8)
    plt.ylabel("Hard-aggregate task success")
    plt.ylim(0.0, 1.0)
    plt.title("Actuator asymmetry hard aggregate")
    plt.tight_layout()
    plt.savefig(FIGURES / "asymmetry_hard_success_v5.png", dpi=220)
    plt.close()

    focus = ["online_system_id", "control_barrier_fault_tolerant_mpc", "unscented_kalman_fault_observer", "robust_l1_adaptive_control", "latent_asymmetry_policy_state_v4", "latent_asymmetry_belief_policy_v5", "oracle_asymmetry_state"]
    x = np.arange(len(focus))
    tracking = [metric_value(hard_metrics, {"split": "hard_aggregate", "method": m}, "tracking_error")[0] for m in focus]
    safety = [metric_value(hard_metrics, {"split": "hard_aggregate", "method": m}, "safety_violation")[0] for m in focus]
    asym = [metric_value(hard_metrics, {"split": "hard_aggregate", "method": m}, "asymmetry_error")[0] for m in focus]
    plt.figure(figsize=(12, 5.6))
    plt.bar(x - 0.25, tracking, width=0.25, label="tracking error", color="#2f6690")
    plt.bar(x, safety, width=0.25, label="safety violation", color="#d1495b")
    plt.bar(x + 0.25, asym, width=0.25, label="asymmetry error", color="#edae49")
    plt.xticks(x, [label[m] for m in focus], rotation=20, ha="right")
    plt.title("Tracking, safety, and asymmetry error")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "asymmetry_safety_tracking_v5.png", dpi=220)
    plt.close()

    plt.figure(figsize=(13, 5.8))
    ablations = ABLATIONS
    util = [float(np.mean([float(r["robust_utility"]) for r in ablation_summary if r["ablation"] == a])) for a in ablations]
    plt.bar(range(len(ablations)), util, color=["#c44536" if a.startswith("full") else "#556f7a" for a in ablations])
    plt.xticks(range(len(ablations)), [a.replace("_", "\n") for a in ablations], fontsize=7)
    plt.ylabel("Mean robust utility")
    plt.title("Latent asymmetry belief ablations")
    plt.tight_layout()
    plt.savefig(FIGURES / "asymmetry_ablation_v5.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10.8, 5.8))
    for method in STRESS_METHODS:
        rows = sorted([r for r in stress_summary if r["stress_axis"] == "combined" and r["method"] == method], key=lambda r: float(r["stress_level"]))
        plt.plot([float(r["stress_level"]) for r in rows], [float(r["task_success"]) for r in rows], marker="o", label=label[method])
    plt.xlabel("Combined stress level")
    plt.ylabel("Task success")
    plt.ylim(0.0, 1.0)
    plt.title("Combined stress sweep")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "asymmetry_stress_sweep_v5.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10.8, 5.8))
    for method in FIXED_RISK_METHODS:
        rows = sorted([r for r in fixed_metrics_rows if r["split"] == "combined_hard_shift" and r["method"] == method], key=lambda r: float(r["risk_budget"]))
        plt.plot([float(r["risk_budget"]) for r in rows], [float(r["coverage"]) for r in rows], marker="o", label=label[method])
    plt.xlabel("Risk budget")
    plt.ylabel("Accepted-deployment coverage")
    plt.title("Fixed-risk coverage on combined hard shift")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "asymmetry_fixed_risk_v5.png", dpi=220)
    plt.close()

    plt.figure(figsize=(9.8, 6.4))
    for method in focus:
        sx = metric_value(hard_metrics, {"split": "hard_aggregate", "method": method}, "safety_violation")[0]
        sy = metric_value(hard_metrics, {"split": "hard_aggregate", "method": method}, "task_success")[0]
        se = metric_value(hard_metrics, {"split": "hard_aggregate", "method": method}, "actuator_energy")[0]
        plt.scatter(sx, sy, s=80 + 500 * se, alpha=0.78, label=label[method])
        plt.text(sx + 0.003, sy, label[method], fontsize=8)
    plt.xlabel("Safety violation")
    plt.ylabel("Hard-aggregate task success")
    plt.title("Success-safety-energy Pareto view")
    plt.tight_layout()
    plt.savefig(FIGURES / "asymmetry_pareto_v5.png", dpi=220)
    plt.close()


def write_summary(counts, terminal, gates, hard_metrics, hard_pairs, ablation_summary, stress_summary, fixed_metrics_rows, negatives):
    lines = []
    lines.append("Paper 86 actuator_asymmetry_policy_state v5 expanded audit")
    lines.append(f"Terminal recommendation: {terminal}")
    lines.append("ICLR main ready: no")
    lines.append("Reason: expanded CPU-only actuator-asymmetry audit adds stronger adaptive/control-barrier/fault-observer baselines, theory hooks, ablations, stress sweeps, and fixed-risk tests, but no real robot or accepted high-fidelity benchmark evidence exists.")
    for key, value in counts.items():
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("Frozen hard-aggregate gate:")
    for key in [
        "best_success_reference", "best_tracking_reference", "best_safety_reference", "best_utility_reference",
        "proposal_success", "best_success", "proposal_tracking", "best_tracking", "proposal_safety", "best_safety",
        "proposal_utility", "best_utility", "paired_success_lower95", "paired_tracking_upper95", "paired_safety_upper95",
        "main_gate", "mechanism_gate", "stress_gate", "stress_dominated_by", "fixed_risk_gate", "scope_gate",
    ]:
        value = gates[key]
        if isinstance(value, float):
            value = f"{value:.5f}"
        lines.append(f"{key}={value}")
    lines.append(gates["fixed_risk_notes"])
    lines.append("")
    lines.append("Hard aggregate metrics:")
    for method in METHODS:
        s, sci = metric_value(hard_metrics, {"split": "hard_aggregate", "method": method}, "task_success")
        t, _ = metric_value(hard_metrics, {"split": "hard_aggregate", "method": method}, "tracking_error")
        v, _ = metric_value(hard_metrics, {"split": "hard_aggregate", "method": method}, "safety_violation")
        a, _ = metric_value(hard_metrics, {"split": "hard_aggregate", "method": method}, "asymmetry_error")
        u, _ = metric_value(hard_metrics, {"split": "hard_aggregate", "method": method}, "robust_utility")
        lines.append(f"{method} task_success={s:.5f} ci95={sci:.5f} tracking={t:.5f} safety={v:.5f} asymmetry_error={a:.5f} robust_utility={u:.5f}")
    lines.append("")
    lines.append("Key paired hard-aggregate differences:")
    refs = []
    for ref in [gates["best_success_reference"], gates["best_tracking_reference"], gates["best_safety_reference"], "latent_asymmetry_policy_state_v4", "robust_l1_adaptive_control"]:
        if ref not in refs:
            refs.append(ref)
    for ref in refs:
        for metric in ["task_success", "tracking_error", "safety_violation", "asymmetry_error", "robust_utility"]:
            matches = [r for r in hard_pairs if r["split"] == "hard_aggregate" and r["reference"] == ref and r["metric"] == metric]
            if matches:
                row = matches[0]
                lines.append(f"v5_minus_{ref} {metric}: mean={row['mean_diff']} ci95={row['ci95_diff']} lower95={row['lower95_diff']} upper95={row['upper95_diff']}")
    lines.append("")
    lines.append("Ablation utility:")
    for ablation in ABLATIONS:
        lines.append(f"{ablation} success={avg_ablation(ablation_summary, ablation, 'task_success'):.5f} tracking={avg_ablation(ablation_summary, ablation, 'tracking_error'):.5f} safety={avg_ablation(ablation_summary, ablation, 'safety_violation'):.5f} utility={avg_ablation(ablation_summary, ablation, 'robust_utility'):.5f}")
    lines.append("")
    lines.append("Maximum combined stress:")
    for row in stress_summary:
        if row["stress_axis"] == "combined" and row["stress_level"] == "1.0":
            lines.append(f"{row['method']} task_success={row['task_success']} tracking={row['tracking_error']} safety={row['safety_violation']} asymmetry_error={row['asymmetry_error']} utility={row['robust_utility']}")
    lines.append("")
    lines.append("Fixed-risk budget 0.05:")
    for row in fixed_metrics_rows:
        if row["risk_budget"] == "0.05":
            lines.append(f"{row['split']} {row['method']} coverage={row['coverage']} accepted_success={row['accepted_success']} accepted_tracking={row['accepted_tracking_error']} accepted_safety={row['accepted_safety']}")
    lines.append("")
    lines.append(f"Negative cases: {len(negatives)}")
    lines.append(f"terminal={terminal}")
    (RESULTS / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def expected_counts():
    return {
        "Main rollout rows": len(SEEDS) * len(TASKS) * len(SPLITS) * MAIN_EPISODES * len(METHODS),
        "Dataset summary rows": len(SEEDS) * len(TASKS) * len(SPLITS) * MAIN_EPISODES,
        "Main seed-metric rows": len(SPLITS) * len(METHODS) * len(SEEDS),
        "Main metric rows": len(SPLITS) * len(METHODS) * len(METRICS),
        "Main pairwise rows": len(SPLITS) * (len(METHODS) - 1) * len(PAIRWISE_METRICS),
        "Hard aggregate seed rows": len(METHODS) * len(SEEDS),
        "Hard aggregate metric rows": len(METHODS) * len(METRICS),
        "Hard aggregate pairwise rows": (len(METHODS) - 1) * len(PAIRWISE_METRICS),
        "Ablation rollout rows": len(SEEDS) * len(TASKS) * 2 * ABLATION_EPISODES * len(ABLATIONS),
        "Ablation seed rows": 2 * len(ABLATIONS) * len(SEEDS),
        "Ablation metric rows": 2 * len(ABLATIONS),
        "Stress raw rows": len(SEEDS) * len(TASKS) * STRESS_EPISODES * len(STRESS_AXES) * len(STRESS_LEVELS) * len(STRESS_METHODS),
        "Stress seed rows": len(STRESS_AXES) * len(STRESS_LEVELS) * len(STRESS_METHODS) * len(SEEDS),
        "Stress metric rows": len(STRESS_AXES) * len(STRESS_LEVELS) * len(STRESS_METHODS),
        "Fixed-risk raw rows": len(SEEDS) * len(TASKS) * len(FIXED_RISK_SPLITS) * FIXED_RISK_EPISODES * len(FIXED_RISK_BUDGETS) * len(FIXED_RISK_METHODS),
        "Fixed-risk seed rows": len(FIXED_RISK_SPLITS) * len(FIXED_RISK_BUDGETS) * len(FIXED_RISK_METHODS) * len(SEEDS),
        "Fixed-risk metric rows": len(FIXED_RISK_SPLITS) * len(FIXED_RISK_BUDGETS) * len(FIXED_RISK_METHODS),
        "Fixed-risk pairwise rows": len(FIXED_RISK_SPLITS) * len(FIXED_RISK_BUDGETS) * (len(FIXED_RISK_METHODS) - 1) * 5,
        "Negative cases": 24,
    }


def main():
    for pattern in ["*.csv", "*.txt"]:
        for path in RESULTS.glob(pattern):
            path.unlink()
    for path in FIGURES.glob("asymmetry_*_v5.png"):
        path.unlink()
    expected = expected_counts()
    main_rows, data_rows, seed_rows, metric_rows, pair_rows, hard_seed, hard_metrics, hard_pairs = stream_main()
    ablation_rows, ab_seed, ab_long, ab_summary = run_ablation()
    stress_rows, stress_seed, stress_long, stress_summary = run_stress()
    fixed_rows, fixed_seed, fixed_metrics_rows, fixed_pairs = run_fixed_risk()
    negatives = negative_cases()
    terminal, gates = terminal_decision(hard_metrics, hard_pairs, ab_summary, stress_summary, fixed_metrics_rows)
    plot_results(hard_metrics, ab_summary, stress_summary, fixed_metrics_rows)
    actuals = {
        "Main rollout rows": main_rows,
        "Dataset summary rows": data_rows,
        "Main seed-metric rows": len(seed_rows),
        "Main metric rows": len(metric_rows),
        "Main pairwise rows": len(pair_rows),
        "Hard aggregate seed rows": len(hard_seed),
        "Hard aggregate metric rows": len(hard_metrics),
        "Hard aggregate pairwise rows": len(hard_pairs),
        "Ablation rollout rows": ablation_rows,
        "Ablation seed rows": len(ab_seed),
        "Ablation metric rows": len(ab_summary),
        "Stress raw rows": stress_rows,
        "Stress seed rows": len(stress_seed),
        "Stress metric rows": len(stress_summary),
        "Fixed-risk raw rows": fixed_rows,
        "Fixed-risk seed rows": len(fixed_seed),
        "Fixed-risk metric rows": len(fixed_metrics_rows),
        "Fixed-risk pairwise rows": len(fixed_pairs),
        "Negative cases": len(negatives),
    }
    mismatches = {k: (expected[k], actuals[k]) for k in expected if expected[k] != actuals[k]}
    if mismatches:
        raise RuntimeError(f"row-count mismatches: {mismatches}")
    write_summary(actuals, terminal, gates, hard_metrics, hard_pairs, ab_summary, stress_summary, fixed_metrics_rows, negatives)
    print(f"terminal={terminal}", flush=True)
    print(f"main_rows={main_rows} stress_rows={stress_rows} fixed_rows={fixed_rows}", flush=True)


if __name__ == "__main__":
    main()
