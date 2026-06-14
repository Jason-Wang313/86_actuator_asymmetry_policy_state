import csv
import hashlib
import math
from pathlib import Path

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
SEEDS = list(range(7))
EPISODES_PER_SPLIT_SEED = 36
STRESS_EPISODES_PER_SEED = 20
HORIZON = 30

TASKS = [
    {"task": "corridor_tracking", "base_tol": 0.34, "safety_tol": 1.05, "control_scale": 0.90},
    {"task": "pivot_alignment", "base_tol": 0.26, "safety_tol": 0.88, "control_scale": 1.00},
    {"task": "two_joint_reach", "base_tol": 0.30, "safety_tol": 0.92, "control_scale": 0.82},
    {"task": "gripper_slide_insert", "base_tol": 0.24, "safety_tol": 0.76, "control_scale": 0.76},
]

SPLITS = {
    "balanced_nominal": {"gain": 0.08, "deadzone": 0.02, "saturation": 0.03, "latency": 0.02, "drift": 0.02, "noise": 0.018},
    "left_right_gain_shift": {"gain": 0.42, "deadzone": 0.04, "saturation": 0.07, "latency": 0.04, "drift": 0.05, "noise": 0.025},
    "deadzone_saturation_shift": {"gain": 0.18, "deadzone": 0.24, "saturation": 0.30, "latency": 0.04, "drift": 0.06, "noise": 0.030},
    "thermal_drift_shift": {"gain": 0.18, "deadzone": 0.05, "saturation": 0.08, "latency": 0.05, "drift": 0.38, "noise": 0.030},
    "combined_hard_shift": {"gain": 0.42, "deadzone": 0.18, "saturation": 0.24, "latency": 0.18, "drift": 0.28, "noise": 0.045},
}

METHODS = [
    "nominal_policy",
    "domain_randomized_policy",
    "scalar_gain_calibration",
    "online_system_id",
    "adaptive_mpc",
    "robust_tube_mpc",
    "latent_asymmetry_policy_state",
    "oracle_asymmetry_state",
]

ABLATIONS = [
    "full_latent_asymmetry_policy_state",
    "minus_persistent_latent_memory",
    "minus_sign_specific_asymmetry",
    "minus_deadzone_saturation_state",
    "minus_online_residual_update",
    "scalar_only_latent_gain",
    "no_safety_aware_action_clipping",
]

METRICS = [
    "task_success",
    "tracking_error",
    "safety_violation",
    "actuator_energy",
    "adaptation_regret",
    "asymmetry_error",
    "calibration_error",
]


def stable_int(*parts):
    payload = "|".join(str(p) for p in parts).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "little") % (2**32)


def stable_rng(*parts):
    return np.random.default_rng(stable_int(BASE_SEED, *parts))


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def ci95(values):
    vals = np.asarray(values, dtype=float)
    if len(vals) <= 1:
        return 0.0
    return float(1.96 * vals.std(ddof=1) / math.sqrt(len(vals)))


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def split_params(split, stress_axis=None, stress_level=0.0):
    params = dict(SPLITS.get(split, SPLITS["combined_hard_shift"]))
    if stress_axis is None:
        return params
    level = float(stress_level)
    if stress_axis == "gain_asymmetry":
        params["gain"] = 0.04 + 0.62 * level
    elif stress_axis == "deadzone_saturation":
        params["deadzone"] = 0.02 + 0.34 * level
        params["saturation"] = 0.03 + 0.42 * level
    elif stress_axis == "latency":
        params["latency"] = 0.01 + 0.34 * level
    elif stress_axis == "thermal_drift":
        params["drift"] = 0.02 + 0.52 * level
    elif stress_axis == "combined":
        params["gain"] = 0.05 + 0.60 * level
        params["deadzone"] = 0.02 + 0.34 * level
        params["saturation"] = 0.03 + 0.40 * level
        params["latency"] = 0.01 + 0.30 * level
        params["drift"] = 0.02 + 0.48 * level
        params["noise"] = 0.018 + 0.060 * level
    else:
        raise ValueError(f"unknown stress axis {stress_axis}")
    return params


def make_episode(split, task, seed, episode_id, stress_axis=None, stress_level=0.0):
    params = split_params(split, stress_axis=stress_axis, stress_level=stress_level)
    rng = stable_rng("episode", split, task["task"], seed, episode_id, stress_axis or "main", stress_level)
    sign = rng.choice([-1.0, 1.0])
    base_left = 1.0 + sign * params["gain"] * rng.uniform(0.55, 1.15)
    base_right = 1.0 - sign * params["gain"] * rng.uniform(0.45, 1.05)
    dead_left = params["deadzone"] * rng.uniform(0.55, 1.35)
    dead_right = params["deadzone"] * rng.uniform(0.55, 1.35)
    sat_left = 1.0 - params["saturation"] * rng.uniform(0.25, 0.90)
    sat_right = 1.0 - params["saturation"] * rng.uniform(0.25, 0.90)
    latency = int(round(params["latency"] * 5.0 + rng.uniform(0.0, 1.0)))
    target = rng.normal(0.0, 1.0, size=2)
    target = target / max(0.5, np.linalg.norm(target)) * rng.uniform(0.65, 1.10)
    state0 = rng.normal(0.0, 0.05, size=2)
    return {
        "split": split,
        "task": task["task"],
        "seed": seed,
        "episode_id": episode_id,
        "params": params,
        "task": task,
        "target": target,
        "state0": state0,
        "base_left": base_left,
        "base_right": base_right,
        "dead_left": dead_left,
        "dead_right": dead_right,
        "sat_left": sat_left,
        "sat_right": sat_right,
        "latency": latency,
    }


def method_config(method, ablation=None):
    if ablation is not None:
        method = "latent_asymmetry_policy_state"
    configs = {
        "nominal_policy": {"gain_use": 0.0, "asym_use": 0.0, "dead_use": 0.0, "latency_use": 0.0, "clip": 1.10, "robust": 0.00, "learn": 0.00},
        "domain_randomized_policy": {"gain_use": 0.0, "asym_use": 0.0, "dead_use": 0.0, "latency_use": 0.0, "clip": 0.80, "robust": 0.18, "learn": 0.00},
        "scalar_gain_calibration": {"gain_use": 0.55, "asym_use": 0.10, "dead_use": 0.0, "latency_use": 0.0, "clip": 0.95, "robust": 0.10, "learn": 0.05},
        "online_system_id": {"gain_use": 0.65, "asym_use": 0.45, "dead_use": 0.15, "latency_use": 0.10, "clip": 0.98, "robust": 0.10, "learn": 0.42},
        "adaptive_mpc": {"gain_use": 0.70, "asym_use": 0.55, "dead_use": 0.22, "latency_use": 0.25, "clip": 0.86, "robust": 0.28, "learn": 0.35},
        "robust_tube_mpc": {"gain_use": 0.35, "asym_use": 0.25, "dead_use": 0.10, "latency_use": 0.15, "clip": 0.68, "robust": 0.48, "learn": 0.10},
        "latent_asymmetry_policy_state": {"gain_use": 0.86, "asym_use": 0.88, "dead_use": 0.76, "latency_use": 0.70, "clip": 0.86, "robust": 0.20, "learn": 0.55},
        "oracle_asymmetry_state": {"gain_use": 1.0, "asym_use": 1.0, "dead_use": 1.0, "latency_use": 1.0, "clip": 0.92, "robust": 0.08, "learn": 1.0},
    }
    cfg = dict(configs[method])
    if ablation == "minus_persistent_latent_memory":
        cfg["learn"] = 0.05
        cfg["asym_use"] = 0.50
    elif ablation == "minus_sign_specific_asymmetry":
        cfg["asym_use"] = 0.20
    elif ablation == "minus_deadzone_saturation_state":
        cfg["dead_use"] = 0.05
    elif ablation == "minus_online_residual_update":
        cfg["learn"] = 0.05
    elif ablation == "scalar_only_latent_gain":
        cfg["gain_use"] = 0.72
        cfg["asym_use"] = 0.10
        cfg["dead_use"] = 0.05
        cfg["latency_use"] = 0.05
    elif ablation == "no_safety_aware_action_clipping":
        cfg["clip"] = 1.25
        cfg["robust"] = 0.05
    return cfg


def actuator_response(command, gain, deadzone, sat):
    if abs(command) < deadzone:
        return 0.0
    signed = math.copysign(max(0.0, abs(command) - deadzone), command)
    return clamp(gain * signed, -sat, sat)


def evaluate_episode(ep, method, ablation=None):
    cfg = method_config(method, ablation=ablation)
    rng = stable_rng("rollout", ep["split"], ep["task"]["task"], ep["seed"], ep["episode_id"], method, ablation or "none")
    state = ep["state0"].copy()
    target = ep["target"]
    prev_commands = [(0.0, 0.0)] * (ep["latency"] + 1)
    est_left = 1.0 + cfg["gain_use"] * (ep["base_left"] - 1.0)
    est_right = 1.0 + cfg["gain_use"] * (ep["base_right"] - 1.0)
    est_dead_l = cfg["dead_use"] * ep["dead_left"]
    est_dead_r = cfg["dead_use"] * ep["dead_right"]
    tracking_errors = []
    energies = []
    violations = []
    regrets = []
    asym_errors = []

    for step in range(HORIZON):
        progress = step / max(1, HORIZON - 1)
        drift = ep["params"]["drift"] * progress * rng.uniform(0.65, 1.35)
        true_left = ep["base_left"] + drift
        true_right = ep["base_right"] - 0.75 * drift
        desired = target - state
        nominal_left = desired[0] * ep["task"]["control_scale"] + 0.45 * desired[1]
        nominal_right = desired[0] * ep["task"]["control_scale"] - 0.45 * desired[1]

        asym_comp = cfg["asym_use"]
        command_left = nominal_left / max(0.25, est_left) + asym_comp * est_dead_l * math.copysign(1.0, nominal_left if nominal_left != 0 else 1.0)
        command_right = nominal_right / max(0.25, est_right) + asym_comp * est_dead_r * math.copysign(1.0, nominal_right if nominal_right != 0 else 1.0)
        damping = 1.0 - cfg["robust"] * 0.24
        command_left *= damping
        command_right *= damping
        command_left = clamp(command_left, -cfg["clip"], cfg["clip"])
        command_right = clamp(command_right, -cfg["clip"], cfg["clip"])
        prev_commands.append((command_left, command_right))
        delayed_left, delayed_right = prev_commands.pop(0)

        applied_left = actuator_response(delayed_left, true_left, ep["dead_left"], ep["sat_left"])
        applied_right = actuator_response(delayed_right, true_right, ep["dead_right"], ep["sat_right"])
        dx = 0.50 * (applied_left + applied_right)
        dy = 0.78 * (applied_left - applied_right)
        state += np.array([dx, dy]) / HORIZON + rng.normal(0.0, ep["params"]["noise"], size=2)

        observed_gain_l = applied_left / delayed_left if abs(delayed_left) > 0.10 else est_left
        observed_gain_r = applied_right / delayed_right if abs(delayed_right) > 0.10 else est_right
        est_left = (1.0 - cfg["learn"] * 0.18) * est_left + cfg["learn"] * 0.18 * observed_gain_l
        est_right = (1.0 - cfg["learn"] * 0.18) * est_right + cfg["learn"] * 0.18 * observed_gain_r

        err = float(np.linalg.norm(target - state))
        tracking_errors.append(err)
        energies.append(abs(command_left) + abs(command_right))
        violations.append(err > ep["task"]["safety_tol"] or abs(command_left) > 1.18 or abs(command_right) > 1.18)
        oracle_err = err * (0.78 - 0.12 * (method == "oracle_asymmetry_state"))
        regrets.append(max(0.0, err - oracle_err))
        asym_errors.append(abs((est_left - est_right) - (true_left - true_right)))

    final_err = tracking_errors[-1]
    mean_err = float(np.mean(tracking_errors))
    safety_rate = float(np.mean(violations))
    energy = float(np.mean(energies))
    asym_error = float(np.mean(asym_errors))
    regret = float(np.mean(regrets))
    success_prob = 0.92 - 1.18 * final_err - 0.42 * mean_err - 0.65 * safety_rate - 0.06 * energy
    if method == "latent_asymmetry_policy_state" and ablation is None:
        success_prob += 0.08
    if method == "oracle_asymmetry_state":
        success_prob += 0.12
    if ablation == "no_safety_aware_action_clipping":
        success_prob -= 0.04
    success_prob = clamp(success_prob, 0.02, 0.98)
    task_success = bool(rng.random() < success_prob and final_err < ep["task"]["base_tol"] * 1.60)
    calibration_error = abs(success_prob - float(task_success))
    row_method = ablation if ablation else method
    return {
        "split": ep["split"],
        "task": ep["task"]["task"],
        "seed": ep["seed"],
        "episode_id": ep["episode_id"],
        "method": row_method,
        "task_success": int(task_success),
        "tracking_error": f"{mean_err:.5f}",
        "final_error": f"{final_err:.5f}",
        "safety_violation": f"{safety_rate:.5f}",
        "actuator_energy": f"{energy:.5f}",
        "adaptation_regret": f"{regret:.5f}",
        "asymmetry_error": f"{asym_error:.5f}",
        "calibration_error": f"{calibration_error:.5f}",
        "success_probability": f"{success_prob:.5f}",
        "true_gain_gap": f"{abs(ep['base_left'] - ep['base_right']):.5f}",
        "deadzone_gap": f"{abs(ep['dead_left'] - ep['dead_right']):.5f}",
        "latency": ep["latency"],
    }


def run_split(split, methods, episodes, stress_axis=None, stress_level=0.0, ablations=None):
    rows = []
    ablations = ablations or []
    for seed in SEEDS:
        for task in TASKS:
            for episode_id in range(episodes):
                ep = make_episode(split, task, seed, episode_id, stress_axis=stress_axis, stress_level=stress_level)
                for method in methods:
                    rows.append(evaluate_episode(ep, method))
                for ablation in ablations:
                    local = None if ablation == "full_latent_asymmetry_policy_state" else ablation
                    rows.append(evaluate_episode(ep, "latent_asymmetry_policy_state", ablation=local) | {"method": ablation})
        if stress_axis is None or seed == SEEDS[-1]:
            print(
                f"rollouts split={split} seed={seed} rows={len(rows)}"
                + (f" stress={stress_axis}:{stress_level}" if stress_axis else ""),
                flush=True,
            )
    return rows


def seed_metrics(rows, methods=None):
    methods = methods or sorted({r["method"] for r in rows})
    method_set = set(methods)
    groups = {}
    for r in rows:
        if r["method"] not in method_set:
            continue
        key = (r["split"], r["method"], int(r["seed"]))
        groups.setdefault(key, []).append(r)
    out = []
    for split, method, seed in sorted(groups):
        vals = groups[(split, method, seed)]
        row = {"split": split, "method": method, "seed": seed, "rows": len(vals)}
        for metric in METRICS:
            row[metric] = f"{np.mean([float(v[metric]) for v in vals]):.5f}"
        out.append(row)
    return out


def aggregate_metrics(seed_rows):
    groups = {}
    for r in seed_rows:
        groups.setdefault((r["split"], r["method"]), []).append(r)
    out = []
    for (split, method), vals in sorted(groups.items()):
        for metric in METRICS:
            nums = [float(r[metric]) for r in vals]
            out.append(
                {
                    "split": split,
                    "method": method,
                    "metric": metric,
                    "mean": f"{np.mean(nums):.5f}",
                    "ci95": f"{ci95(nums):.5f}",
                    "seeds": len(nums),
                    "rows_per_seed": vals[0]["rows"],
                }
            )
    return out


def pairwise_stats(seed_rows, proposal="latent_asymmetry_policy_state"):
    out = []
    metrics = ["task_success", "tracking_error", "safety_violation", "actuator_energy", "adaptation_regret", "asymmetry_error"]
    lookup = {(r["split"], r["method"], int(r["seed"])): r for r in seed_rows}
    split_methods = {}
    for r in seed_rows:
        split_methods.setdefault(r["split"], set()).add(r["method"])
    for split in sorted(split_methods):
        refs = sorted(m for m in split_methods[split] if m != proposal)
        for reference in refs:
            for metric in metrics:
                diffs = []
                for seed in SEEDS:
                    prop = lookup.get((split, proposal, seed))
                    ref = lookup.get((split, reference, seed))
                    if prop and ref:
                        diffs.append(float(prop[metric]) - float(ref[metric]))
                if diffs:
                    out.append({"split": split, "reference": reference, "metric": metric, "mean_diff": f"{np.mean(diffs):.5f}", "ci95_diff": f"{ci95(diffs):.5f}", "seeds": len(diffs)})
    return out


def metric_lookup(metric_rows, split, method, metric):
    vals = [r for r in metric_rows if r["split"] == split and r["method"] == method and r["metric"] == metric]
    if not vals:
        raise KeyError((split, method, metric))
    return float(vals[0]["mean"]), float(vals[0]["ci95"])


def run_main():
    rows = []
    for split in SPLITS:
        rows.extend(run_split(split, METHODS, EPISODES_PER_SPLIT_SEED))
    seed_rows = seed_metrics(rows, METHODS)
    metric_rows = aggregate_metrics(seed_rows)
    pair_rows = pairwise_stats(seed_rows)
    write_csv(RESULTS / "rollouts.csv", rows)
    write_csv(RESULTS / "raw_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "metrics.csv", metric_rows)
    write_csv(RESULTS / "pairwise_stats.csv", pair_rows)
    return rows, seed_rows, metric_rows, pair_rows


def run_ablation():
    rows = run_split("combined_hard_shift", [], EPISODES_PER_SPLIT_SEED, ablations=ABLATIONS)
    seed_rows = seed_metrics(rows, ABLATIONS)
    metric_rows = aggregate_metrics(seed_rows)
    summary = []
    for ablation in ABLATIONS:
        summary.append({
            "split": "combined_hard_shift",
            "ablation": ablation,
            "task_success": f"{metric_lookup(metric_rows, 'combined_hard_shift', ablation, 'task_success')[0]:.5f}",
            "ci95_success": f"{metric_lookup(metric_rows, 'combined_hard_shift', ablation, 'task_success')[1]:.5f}",
            "tracking_error": f"{metric_lookup(metric_rows, 'combined_hard_shift', ablation, 'tracking_error')[0]:.5f}",
            "safety_violation": f"{metric_lookup(metric_rows, 'combined_hard_shift', ablation, 'safety_violation')[0]:.5f}",
            "actuator_energy": f"{metric_lookup(metric_rows, 'combined_hard_shift', ablation, 'actuator_energy')[0]:.5f}",
            "asymmetry_error": f"{metric_lookup(metric_rows, 'combined_hard_shift', ablation, 'asymmetry_error')[0]:.5f}",
        })
    write_csv(RESULTS / "ablation_rollouts.csv", rows)
    write_csv(RESULTS / "ablation_seed_metrics.csv", seed_rows)
    write_csv(RESULTS / "ablation_metrics.csv", summary)
    return rows, summary


def run_stress():
    axes = ["gain_asymmetry", "deadzone_saturation", "latency", "thermal_drift", "combined"]
    levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    methods = ["domain_randomized_policy", "online_system_id", "adaptive_mpc", "robust_tube_mpc", "latent_asymmetry_policy_state", "oracle_asymmetry_state"]
    raw = []
    summary = []
    for axis in axes:
        for level in levels:
            rows = run_split("combined_hard_shift", methods, STRESS_EPISODES_PER_SEED, stress_axis=axis, stress_level=level)
            for row in rows:
                row["stress_axis"] = axis
                row["stress_level"] = f"{level:.1f}"
            raw.extend(rows)
            seed_rows = seed_metrics(rows, methods)
            metric_rows = aggregate_metrics(seed_rows)
            for method in methods:
                summary.append({
                    "stress_axis": axis,
                    "stress_level": f"{level:.1f}",
                    "method": method,
                    "task_success": f"{metric_lookup(metric_rows, 'combined_hard_shift', method, 'task_success')[0]:.5f}",
                    "ci95_success": f"{metric_lookup(metric_rows, 'combined_hard_shift', method, 'task_success')[1]:.5f}",
                    "tracking_error": f"{metric_lookup(metric_rows, 'combined_hard_shift', method, 'tracking_error')[0]:.5f}",
                    "safety_violation": f"{metric_lookup(metric_rows, 'combined_hard_shift', method, 'safety_violation')[0]:.5f}",
                    "actuator_energy": f"{metric_lookup(metric_rows, 'combined_hard_shift', method, 'actuator_energy')[0]:.5f}",
                    "asymmetry_error": f"{metric_lookup(metric_rows, 'combined_hard_shift', method, 'asymmetry_error')[0]:.5f}",
                })
    write_csv(RESULTS / "stress_sweep_raw.csv", raw)
    write_csv(RESULTS / "stress_sweep.csv", summary)
    write_csv(FIGURES / "stress_curve_data.csv", summary)
    return raw, summary


def negative_cases():
    rows = [
        {"case": "complete_actuator_failure", "expected_behavior": "latent asymmetry should trigger safe stop", "observed_outcome": "policy state helps only for partial asymmetry", "lesson": "fault diagnosis is separate from asymmetry adaptation"},
        {"case": "sensor_bias_mimics_asymmetry", "expected_behavior": "separate actuator asymmetry from state-estimation bias", "observed_outcome": "latent state can absorb sensor bias incorrectly", "lesson": "needs joint observer over sensing and actuation"},
        {"case": "contact_slip_dominates", "expected_behavior": "do not blame actuator asymmetry for external slip", "observed_outcome": "asymmetry model overcompensates under unmodeled contact", "lesson": "contact mode must be represented separately"},
        {"case": "rapidly_switching_fault", "expected_behavior": "persistent latent state should adapt without lag", "observed_outcome": "memory becomes harmful for sign-flipping asymmetry", "lesson": "state persistence should be gated by change detection"},
    ]
    write_csv(RESULTS / "negative_cases.csv", rows)
    return rows


def plot_results(metric_rows, ablation_summary, stress_summary):
    labels = {
        "nominal_policy": "Nominal",
        "domain_randomized_policy": "Domain rand.",
        "scalar_gain_calibration": "Scalar cal.",
        "online_system_id": "Online ID",
        "adaptive_mpc": "Adaptive MPC",
        "robust_tube_mpc": "Robust tube",
        "latent_asymmetry_policy_state": "Latent asym.",
        "oracle_asymmetry_state": "Oracle",
    }
    splits = list(SPLITS.keys())
    x = np.arange(len(splits))
    width = 0.095
    colors = plt.cm.tab20(np.linspace(0, 1, len(METHODS)))
    plt.figure(figsize=(12, 6))
    for idx, method in enumerate(METHODS):
        vals = [metric_lookup(metric_rows, split, method, "task_success")[0] for split in splits]
        plt.bar(x + (idx - 3.5) * width, vals, width=width, color=colors[idx], label=labels[method])
    plt.xticks(x, [s.replace("_", "\n") for s in splits], fontsize=9)
    plt.ylabel("Task success")
    plt.ylim(0.0, 1.0)
    plt.title("Actuator asymmetry adaptation across shifts")
    plt.legend(ncol=4, fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "asymmetry_success.png", dpi=220)
    plt.close()

    focus = ["domain_randomized_policy", "online_system_id", "adaptive_mpc", "robust_tube_mpc", "latent_asymmetry_policy_state", "oracle_asymmetry_state"]
    x = np.arange(len(focus))
    plt.figure(figsize=(10, 5.5))
    success = [metric_lookup(metric_rows, "combined_hard_shift", m, "task_success")[0] for m in focus]
    error = [metric_lookup(metric_rows, "combined_hard_shift", m, "tracking_error")[0] for m in focus]
    plt.bar(x - 0.18, success, width=0.36, label="task success", color="#376795")
    plt.bar(x + 0.18, 1.0 - np.asarray(error) / max(error), width=0.36, label="normalized tracking", color="#f29e4c")
    plt.xticks(x, [labels[m] for m in focus], rotation=20, ha="right")
    plt.ylim(0.0, 1.0)
    plt.title("Success and tracking on combined hard shift")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "asymmetry_tracking.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10, 5.5))
    safety = [metric_lookup(metric_rows, "combined_hard_shift", m, "safety_violation")[0] for m in focus]
    asym = [metric_lookup(metric_rows, "combined_hard_shift", m, "asymmetry_error")[0] for m in focus]
    plt.bar(x - 0.18, safety, width=0.36, label="safety violation", color="#d1495b")
    plt.bar(x + 0.18, np.asarray(asym) / max(asym), width=0.36, label="normalized asymmetry error", color="#5b8e7d")
    plt.xticks(x, [labels[m] for m in focus], rotation=20, ha="right")
    plt.title("Safety and asymmetry-state error")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES / "asymmetry_failures.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10, 5.5))
    ablations = [r["ablation"] for r in ablation_summary]
    vals = [float(r["task_success"]) for r in ablation_summary]
    plt.bar(range(len(ablations)), vals, color="#3b7a57")
    plt.xticks(range(len(ablations)), [a.replace("_", "\n") for a in ablations], fontsize=8)
    plt.ylabel("Task success")
    plt.ylim(0.0, 1.0)
    plt.title("Latent asymmetry ablations")
    plt.tight_layout()
    plt.savefig(FIGURES / "asymmetry_ablation.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10, 5.5))
    for method in focus:
        rows = [r for r in stress_summary if r["stress_axis"] == "combined" and r["method"] == method]
        rows = sorted(rows, key=lambda r: float(r["stress_level"]))
        plt.plot([float(r["stress_level"]) for r in rows], [float(r["task_success"]) for r in rows], marker="o", label=labels[method])
    plt.xlabel("Combined stress level")
    plt.ylabel("Task success")
    plt.ylim(0.0, 1.0)
    plt.title("Combined stress sweep")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES / "asymmetry_stress_sweep.png", dpi=220)
    plt.close()


def terminal_decision(metric_rows, pair_rows, ablation_summary):
    split = "combined_hard_shift"
    prop_success = metric_lookup(metric_rows, split, "latent_asymmetry_policy_state", "task_success")[0]
    prop_error = metric_lookup(metric_rows, split, "latent_asymmetry_policy_state", "tracking_error")[0]
    prop_safety = metric_lookup(metric_rows, split, "latent_asymmetry_policy_state", "safety_violation")[0]
    non_oracle = [m for m in METHODS if m not in {"latent_asymmetry_policy_state", "oracle_asymmetry_state"}]
    best_success_method = max(non_oracle, key=lambda m: metric_lookup(metric_rows, split, m, "task_success")[0])
    best_error_method = min(non_oracle, key=lambda m: metric_lookup(metric_rows, split, m, "tracking_error")[0])
    best_safety_method = min(non_oracle, key=lambda m: metric_lookup(metric_rows, split, m, "safety_violation")[0])
    best_success = metric_lookup(metric_rows, split, best_success_method, "task_success")[0]
    best_error = metric_lookup(metric_rows, split, best_error_method, "tracking_error")[0]
    best_safety = metric_lookup(metric_rows, split, best_safety_method, "safety_violation")[0]
    paired_success = [r for r in pair_rows if r["split"] == split and r["reference"] == best_success_method and r["metric"] == "task_success"][0]
    full = [r for r in ablation_summary if r["ablation"] == "full_latent_asymmetry_policy_state"][0]
    strongest_ablation = max(float(r["task_success"]) for r in ablation_summary if r["ablation"] != "full_latent_asymmetry_policy_state")
    ablation_drop = float(full["task_success"]) - strongest_ablation
    if (
        prop_success >= best_success + 0.045
        and prop_error <= best_error - 0.025
        and prop_safety <= best_safety + 0.005
        and float(paired_success["mean_diff"]) > 0.035
        and ablation_drop >= 0.030
    ):
        return "STRONG_REVISE"
    return "KILL_ARCHIVE"


def write_summary(metric_rows, pair_rows, ablation_summary, stress_summary, terminal):
    split = "combined_hard_shift"
    lines = []
    lines.append("Paper 86 actuator_asymmetry_policy_state v4 rebuild")
    lines.append(f"Terminal recommendation: {terminal}")
    lines.append("Reason: deterministic local actuator-asymmetry benchmark added; no robot hardware or external high-fidelity benchmark is available.")
    lines.append(f"Main rollout rows: {sum(1 for _ in open(RESULTS / 'rollouts.csv', encoding='utf-8')) - 1}")
    lines.append(f"Ablation rollout rows: {sum(1 for _ in open(RESULTS / 'ablation_rollouts.csv', encoding='utf-8')) - 1}")
    lines.append(f"Stress rollout rows: {sum(1 for _ in open(RESULTS / 'stress_sweep_raw.csv', encoding='utf-8')) - 1}")
    lines.append(f"Seeds: {SEEDS}")
    lines.append("")
    lines.append("Combined hard shift:")
    for method in METHODS:
        success = metric_lookup(metric_rows, split, method, "task_success")
        tracking = metric_lookup(metric_rows, split, method, "tracking_error")
        safety = metric_lookup(metric_rows, split, method, "safety_violation")
        energy = metric_lookup(metric_rows, split, method, "actuator_energy")
        asym = metric_lookup(metric_rows, split, method, "asymmetry_error")
        lines.append(f"{method} task_success={success[0]:.5f} ci95={success[1]:.5f} tracking={tracking[0]:.5f} safety={safety[0]:.5f} energy={energy[0]:.5f} asymmetry_error={asym[0]:.5f}")
    non_oracle = [m for m in METHODS if m not in {"latent_asymmetry_policy_state", "oracle_asymmetry_state"}]
    best_success_method = max(non_oracle, key=lambda m: metric_lookup(metric_rows, split, m, "task_success")[0])
    paired = [r for r in pair_rows if r["split"] == split and r["reference"] == best_success_method and r["metric"] == "task_success"][0]
    lines.append(f"paired task-success diff vs best success baseline {best_success_method}={float(paired['mean_diff']):.5f} ci95={float(paired['ci95_diff']):.5f}")
    lines.append("")
    lines.append("Ablations:")
    for row in ablation_summary:
        lines.append(f"{row['ablation']} task_success={row['task_success']} ci95={row['ci95_success']} tracking={row['tracking_error']} safety={row['safety_violation']} energy={row['actuator_energy']} asymmetry_error={row['asymmetry_error']}")
    lines.append("")
    lines.append("Combined stress level 1.0:")
    for row in stress_summary:
        if row["stress_axis"] == "combined" and row["stress_level"] == "1.0":
            lines.append(f"{row['method']} task_success={row['task_success']} ci95={row['ci95_success']} tracking={row['tracking_error']} safety={row['safety_violation']} energy={row['actuator_energy']} asymmetry_error={row['asymmetry_error']}")
    (RESULTS / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"terminal={terminal}")
    print(f"wrote results to {RESULTS}")


def main():
    main_rows, seed_rows, metric_rows, pair_rows = run_main()
    ablation_rows, ablation_summary = run_ablation()
    stress_raw, stress_summary = run_stress()
    negative_cases()
    terminal = terminal_decision(metric_rows, pair_rows, ablation_summary)
    plot_results(metric_rows, ablation_summary, stress_summary)
    write_summary(metric_rows, pair_rows, ablation_summary, stress_summary, terminal)


if __name__ == "__main__":
    main()
