import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"
DOCS = ROOT / "docs"


METHOD_LABELS = {
    "nominal_policy": "Nominal",
    "domain_randomized_policy": "Domain rand.",
    "scalar_gain_calibration": "Scalar cal.",
    "online_system_id": "Online ID",
    "adaptive_mpc": "Adaptive MPC",
    "robust_tube_mpc": "Robust tube",
    "control_barrier_fault_tolerant_mpc": "CBF-FTC MPC",
    "unscented_kalman_fault_observer": "UKF observer",
    "recurrent_hidden_state_policy_proxy": "RNN state proxy",
    "robust_l1_adaptive_control": "L1 adaptive",
    "latent_asymmetry_policy_state_v4": "Latent state v4",
    "latent_asymmetry_belief_policy_v5": "Belief state v5",
    "oracle_asymmetry_state": "Oracle state",
}

FOCUS_METHODS = [
    "online_system_id",
    "control_barrier_fault_tolerant_mpc",
    "unscented_kalman_fault_observer",
    "robust_l1_adaptive_control",
    "latent_asymmetry_policy_state_v4",
    "latent_asymmetry_belief_policy_v5",
    "oracle_asymmetry_state",
]

SPLIT_LABELS = {
    "balanced_nominal": "Nominal",
    "left_right_gain_shift": "Gain shift",
    "deadzone_saturation_shift": "Deadzone/sat.",
    "thermal_drift_shift": "Thermal drift",
    "latency_hysteresis_shift": "Latency/hyst.",
    "intermittent_fault_shift": "Fault",
    "payload_contact_shift": "Payload/contact",
    "combined_hard_shift": "Combined",
    "hard_aggregate": "Hard agg.",
}

ABLATION_LABELS = {
    "full_latent_asymmetry_belief_policy_v5": "Full belief v5",
    "minus_persistent_latent_memory": "- persistent memory",
    "minus_sign_specific_asymmetry": "- sign-specific asym.",
    "minus_deadzone_saturation_state": "- deadzone/sat. state",
    "minus_latency_compensation": "- latency comp.",
    "minus_thermal_drift_update": "- drift update",
    "minus_online_residual_update": "- residual update",
    "minus_safety_aware_action_clipping": "- safety clipping",
    "scalar_only_latent_gain": "Scalar-only latent gain",
    "no_belief_uncertainty": "No belief uncertainty",
}

ROW_FILES = [
    "rollouts.csv",
    "dataset_summary.csv",
    "raw_seed_metrics.csv",
    "metrics.csv",
    "pairwise_stats.csv",
    "hard_aggregate_seed_metrics.csv",
    "hard_aggregate_metrics.csv",
    "hard_aggregate_pairwise_stats.csv",
    "ablation_rollouts.csv",
    "ablation_seed_metrics.csv",
    "ablation_metrics.csv",
    "stress_sweep_raw.csv",
    "stress_sweep_seed_metrics.csv",
    "stress_sweep.csv",
    "fixed_risk_raw.csv",
    "fixed_risk_seed_metrics.csv",
    "fixed_risk_metrics.csv",
    "fixed_risk_pairwise.csv",
    "negative_cases.csv",
]


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def count_rows(name):
    return len(read_csv(RESULTS / name))


def ascii_clean(text):
    text = str(text or "")
    text = (
        text.replace("–", "-")
        .replace("—", "-")
        .replace("−", "-")
        .replace("“", '"')
        .replace("”", '"')
        .replace("’", "'")
        .replace("‐", "-")
        .replace("‑", "-")
    )
    return text.encode("ascii", "ignore").decode("ascii")


def tex_escape(text):
    text = ascii_clean(text)
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(ch, ch) for ch in text)


def method_name(method):
    return tex_escape(METHOD_LABELS.get(method, method))


def split_name(split):
    return tex_escape(SPLIT_LABELS.get(split, split))


def ablation_name(ablation):
    return tex_escape(ABLATION_LABELS.get(ablation, ablation))


def metric_lookup(rows, selectors, metric):
    for row in rows:
        if row.get("metric") != metric:
            continue
        if all(row.get(k) == v for k, v in selectors.items()):
            return float(row["mean"]), float(row["ci95"])
    raise KeyError((selectors, metric))


def fmt_pm(mean, ci):
    return f"{mean:.3f} $\\pm$ {ci:.3f}"


def parse_summary(summary_text):
    out = {}
    for line in summary_text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            out[key.strip()] = value.strip()
        elif ":" in line:
            key, value = line.split(":", 1)
            out[key.strip()] = value.strip()
    return out


def bib_key(i):
    return f"pool86_{i:02d}"


def write_references():
    rows = read_csv(DOCS / "deep_read_250.csv")[:56]
    entries = []
    for i, row in enumerate(rows, start=1):
        title = tex_escape(row.get("title") or "Untitled prior work")
        authors_raw = ascii_clean(row.get("authors") or "Local Prior Work Pool")
        parts = [p.strip() for p in re.split(r";| and ", authors_raw) if p.strip()]
        authors = " and ".join(tex_escape(p) for p in parts[:8]) or "Local Prior Work Pool"
        year_raw = ascii_clean(row.get("year") or "")
        match = re.search(r"(19|20)\d{2}", year_raw)
        year = match.group(0) if match else "2026"
        venue = tex_escape(row.get("venue") or row.get("source") or "prior-work pool")
        link = tex_escape(row.get("doi") or row.get("url") or row.get("arxiv_id") or row.get("uid") or "local pool record")
        entries.append(
            "\n".join(
                [
                    f"@misc{{{bib_key(i)},",
                    f"  author={{{authors}}},",
                    f"  title={{{title}}},",
                    f"  year={{{year}}},",
                    f"  note={{{venue}; {link}}}",
                    "}",
                ]
            )
        )
    (PAPER / "references.bib").write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    return [bib_key(i) for i in range(1, len(rows) + 1)], rows


def longtable(header, rows, spec, caption, label, fontsize=r"\scriptsize"):
    lines = [
        r"\begin{center}",
        fontsize,
        f"\\begin{{longtable}}{{{spec}}}",
        f"\\caption{{{caption}}}\\label{{{label}}}\\\\",
        r"\toprule",
        header + r"\\",
        r"\midrule",
        r"\endfirsthead",
        f"\\caption[]{{{caption} (continued)}}\\\\",
        r"\toprule",
        header + r"\\",
        r"\midrule",
        r"\endhead",
    ]
    lines.extend(rows)
    lines.extend([r"\bottomrule", r"\end{longtable}", r"\normalsize", r"\end{center}"])
    return "\n".join(lines)


def hard_table(hard_metrics):
    rows = []
    for method in METHOD_LABELS:
        success = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": method}, "task_success")
        tracking = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": method}, "tracking_error")
        safety = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": method}, "safety_violation")
        asym = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": method}, "asymmetry_error")
        utility = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": method}, "robust_utility")
        rows.append(
            f"{method_name(method)} & {fmt_pm(*success)} & {tracking[0]:.3f} & {safety[0]:.3f} & {asym[0]:.3f} & {utility[0]:.3f}\\\\"
        )
    return longtable(
        "Method & Success & Tracking & Safety & Asym. err. & Utility",
        rows,
        "p{0.30\\linewidth}rrrrr",
        "Predefined hard-aggregate results over intermittent fault, payload/contact, and combined hard shift. Higher success and utility are better; lower tracking, safety, and asymmetry error are better.",
        "tab:hard",
    )


def split_table(metrics):
    rows = []
    for split in SPLIT_LABELS:
        if split == "hard_aggregate":
            continue
        for method in FOCUS_METHODS:
            success = metric_lookup(metrics, {"split": split, "method": method}, "task_success")
            tracking = metric_lookup(metrics, {"split": split, "method": method}, "tracking_error")
            safety = metric_lookup(metrics, {"split": split, "method": method}, "safety_violation")
            asym = metric_lookup(metrics, {"split": split, "method": method}, "asymmetry_error")
            rows.append(f"{split_name(split)} & {method_name(method)} & {fmt_pm(*success)} & {tracking[0]:.3f} & {safety[0]:.3f} & {asym[0]:.3f}\\\\")
    return longtable(
        "Split & Method & Success & Tracking & Safety & Asym. err.",
        rows,
        "p{0.15\\linewidth}p{0.26\\linewidth}rrrr",
        "Split-level evidence for the strongest adaptive and fault-observer baselines, v4, v5, and the oracle.",
        "tab:split",
    )


def pairwise_table(hard_pairs, summary):
    refs = [
        summary["best_success_reference"],
        "robust_l1_adaptive_control",
        "unscented_kalman_fault_observer",
        "online_system_id",
        "control_barrier_fault_tolerant_mpc",
    ]
    seen = set()
    rows = []
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        for metric in ["task_success", "tracking_error", "safety_violation", "asymmetry_error", "robust_utility"]:
            matches = [r for r in hard_pairs if r["split"] == "hard_aggregate" and r["reference"] == ref and r["metric"] == metric]
            if not matches:
                continue
            row = matches[0]
            rows.append(
                f"{method_name(ref)} & {tex_escape(metric)} & {float(row['mean_diff']):.3f} & {float(row['ci95_diff']):.3f} & {float(row['lower95_diff']):.3f} & {float(row['upper95_diff']):.3f}\\\\"
            )
    return longtable(
        "Reference & Metric & Mean diff & CI95 & Lower95 & Upper95",
        rows,
        "p{0.28\\linewidth}p{0.20\\linewidth}rrrr",
        "Paired seed-level hard-aggregate differences for belief state v5 minus reference. Negative tracking and safety differences are favorable; positive success and utility differences are favorable.",
        "tab:paired",
    )


def ablation_table(ablations):
    rows = []
    for row in ablations:
        rows.append(
            f"{split_name(row['split'])} & {ablation_name(row['ablation'])} & {float(row['task_success']):.3f} & {float(row['tracking_error']):.3f} & {float(row['safety_violation']):.3f} & {float(row['asymmetry_error']):.3f} & {float(row['robust_utility']):.3f}\\\\"
        )
    return longtable(
        "Split & Ablation & Success & Tracking & Safety & Asym. err. & Utility",
        rows,
        "p{0.14\\linewidth}p{0.27\\linewidth}rrrrr",
        "Mechanism ablations. The full mechanism had to beat every non-full ablation on robust utility by at least 0.015 and avoid a joint success/safety ablation reversal.",
        "tab:ablation",
    )


def stress_table(stress):
    rows = []
    for row in stress:
        if row["stress_axis"] != "combined":
            continue
        rows.append(
            f"{row['stress_level']} & {method_name(row['method'])} & {float(row['task_success']):.3f} & {float(row['tracking_error']):.3f} & {float(row['safety_violation']):.3f} & {float(row['asymmetry_error']):.3f} & {float(row['robust_utility']):.3f}\\\\"
        )
    return longtable(
        "Level & Method & Success & Tracking & Safety & Asym. err. & Utility",
        rows,
        "rp{0.27\\linewidth}rrrrr",
        "Combined stress sweep. V5 was not Pareto-dominated at maximum stress, but that stress-gate pass did not rescue the failed main, mechanism, fixed-risk, and scope gates.",
        "tab:stress",
    )


def fixed_table(fixed):
    rows = []
    for row in fixed:
        if row["risk_budget"] not in {"0.02", "0.05", "0.10"}:
            continue
        rows.append(
            f"{split_name(row['split'])} & {row['risk_budget']} & {method_name(row['method'])} & {float(row['coverage']):.3f} & {float(row['accepted_success']):.3f} & {float(row['accepted_tracking_error']):.3f} & {float(row['accepted_safety']):.3f}\\\\"
        )
    return longtable(
        "Split & Budget & Method & Coverage & Succ. & Tracking & Safety",
        rows,
        "p{0.16\\linewidth}rp{0.28\\linewidth}rrrr",
        "Fixed-risk deployment tests. At budget 0.05 all methods have zero accepted coverage on both fixed-risk splits, so the frozen deployment gate fails.",
        "tab:fixed",
    )


def negative_table(negative):
    rows = []
    for row in negative:
        rows.append(
            f"{tex_escape(row['case_id'])} & {tex_escape(row['case_family'])} & {tex_escape(row['terminal_lesson'])}\\\\"
        )
    return longtable(
        "Case & Family & Terminal lesson",
        rows,
        "p{0.26\\linewidth}p{0.25\\linewidth}p{0.38\\linewidth}",
        "Retained negative cases used to keep the discussion honest.",
        "tab:negative",
    )


def full_main_table(metrics):
    rows = []
    for split in SPLIT_LABELS:
        if split == "hard_aggregate":
            continue
        for method in METHOD_LABELS:
            success = metric_lookup(metrics, {"split": split, "method": method}, "task_success")
            tracking = metric_lookup(metrics, {"split": split, "method": method}, "tracking_error")
            safety = metric_lookup(metrics, {"split": split, "method": method}, "safety_violation")
            asym = metric_lookup(metrics, {"split": split, "method": method}, "asymmetry_error")
            energy = metric_lookup(metrics, {"split": split, "method": method}, "actuator_energy")
            utility = metric_lookup(metrics, {"split": split, "method": method}, "robust_utility")
            rows.append(
                f"{split_name(split)} & {method_name(method)} & {fmt_pm(*success)} & {tracking[0]:.3f} & {safety[0]:.3f} & {asym[0]:.3f} & {energy[0]:.3f} & {utility[0]:.3f}\\\\"
            )
    return longtable(
        "Split & Method & Success & Track. & Safety & Asym. & Energy & Utility",
        rows,
        "p{0.13\\linewidth}p{0.24\\linewidth}rrrrrr",
        "Full split-by-method main metrics. This appendix table prevents cherry-picking by exposing every predefined split and method.",
        "tab:full-main",
        fontsize=r"\tiny",
    )


def full_pairwise_table(hard_pairs):
    rows = []
    for row in hard_pairs:
        rows.append(
            f"{method_name(row['reference'])} & {tex_escape(row['metric'])} & {float(row['mean_diff']):.3f} & {float(row['ci95_diff']):.3f} & {float(row['lower95_diff']):.3f} & {float(row['upper95_diff']):.3f}\\\\"
        )
    return longtable(
        "Reference & Metric & Mean diff & CI95 & Lower95 & Upper95",
        rows,
        "p{0.31\\linewidth}p{0.23\\linewidth}rrrr",
        "All hard-aggregate paired differences for belief state v5 minus each reference method.",
        "tab:full-pairwise",
        fontsize=r"\tiny",
    )


def full_stress_table(stress):
    rows = []
    for row in stress:
        rows.append(
            f"{tex_escape(row['stress_axis'])} & {row['stress_level']} & {method_name(row['method'])} & {float(row['task_success']):.3f} & {float(row['tracking_error']):.3f} & {float(row['safety_violation']):.3f} & {float(row['asymmetry_error']):.3f} & {float(row['robust_utility']):.3f}\\\\"
        )
    return longtable(
        "Axis & Level & Method & Success & Track. & Safety & Asym. & Utility",
        rows,
        "p{0.16\\linewidth}rp{0.23\\linewidth}rrrrr",
        "All stress-sweep metrics across six axes, six levels, and seven methods.",
        "tab:full-stress",
        fontsize=r"\tiny",
    )


def full_fixed_table(fixed):
    rows = []
    for row in fixed:
        rows.append(
            f"{split_name(row['split'])} & {row['risk_budget']} & {method_name(row['method'])} & {float(row['coverage']):.3f} & {float(row['accepted_success']):.3f} & {float(row['accepted_tracking_error']):.3f} & {float(row['accepted_safety']):.3f} & {float(row['accepted_utility']):.3f}\\\\"
        )
    return longtable(
        "Split & Budget & Method & Coverage & Succ. & Track. & Safety & Utility",
        rows,
        "p{0.14\\linewidth}rp{0.25\\linewidth}rrrrr",
        "All fixed-risk deployment rows across both hard splits, four budgets, and six methods.",
        "tab:full-fixed",
        fontsize=r"\tiny",
    )


def fixed_pairwise_table(fixed_pairs):
    rows = []
    for row in fixed_pairs:
        rows.append(
            f"{split_name(row['split'])} & {row['risk_budget']} & {method_name(row['reference'])} & {tex_escape(row['metric'])} & {float(row['mean_diff']):.3f} & {float(row['ci95_diff']):.3f} & {float(row['lower95_diff']):.3f}\\\\"
        )
    return longtable(
        "Split & Budget & Reference & Metric & Mean diff & CI95 & Lower95",
        rows,
        "p{0.13\\linewidth}rp{0.22\\linewidth}p{0.20\\linewidth}rrr",
        "All fixed-risk paired comparisons for belief state v5 minus each non-v5 reference across budgets.",
        "tab:fixed-pairwise",
        fontsize=r"\tiny",
    )


def hard_seed_table(hard_seed):
    rows = []
    for row in hard_seed:
        rows.append(
            f"{method_name(row['method'])} & {row['seed']} & {float(row['task_success']):.3f} & {float(row['tracking_error']):.3f} & {float(row['safety_violation']):.3f} & {float(row['asymmetry_error']):.3f} & {float(row['robust_utility']):.3f}\\\\"
        )
    return longtable(
        "Method & Seed & Success & Tracking & Safety & Asym. err. & Utility",
        rows,
        "p{0.31\\linewidth}rrrrrr",
        "Hard-aggregate seed means. These rows are the units used by paired tests.",
        "tab:hard-seed",
        fontsize=r"\tiny",
    )


def ablation_seed_table(ablation_seed):
    rows = []
    for row in ablation_seed:
        rows.append(
            f"{split_name(row['split'])} & {ablation_name(row['ablation'])} & {row['seed']} & {float(row['task_success']):.3f} & {float(row['tracking_error']):.3f} & {float(row['safety_violation']):.3f} & {float(row['robust_utility']):.3f}\\\\"
        )
    return longtable(
        "Split & Ablation & Seed & Success & Tracking & Safety & Utility",
        rows,
        "p{0.13\\linewidth}p{0.34\\linewidth}rrrrr",
        "Ablation seed means for the two hard ablation splits.",
        "tab:ablation-seed",
        fontsize=r"\tiny",
    )


def prior_work_table(prior_rows, cite_keys):
    rows = []
    for i, row in enumerate(prior_rows[:56], start=1):
        title = tex_escape(row.get("title") or "Untitled")
        year = tex_escape(row.get("year") or "")
        venue = tex_escape(row.get("venue") or row.get("source") or "pool")
        rows.append(f"\\citep{{{cite_keys[i-1]}}} & {title[:118]} & {year} & {venue[:58]}\\\\")
    return longtable(
        "Cite & Prior-work pressure & Year & Source",
        rows,
        "p{0.12\\linewidth}p{0.53\\linewidth}p{0.08\\linewidth}p{0.18\\linewidth}",
        "Local prior-work pressure map. The entries are used as threat coverage, not as an exhaustive manual survey.",
        "tab:prior",
    )


def main():
    PAPER.mkdir(exist_ok=True)
    cite_keys, prior_rows = write_references()
    metrics = read_csv(RESULTS / "metrics.csv")
    hard_metrics = read_csv(RESULTS / "hard_aggregate_metrics.csv")
    hard_pairs = read_csv(RESULTS / "hard_aggregate_pairwise_stats.csv")
    hard_seed = read_csv(RESULTS / "hard_aggregate_seed_metrics.csv")
    ablations = read_csv(RESULTS / "ablation_metrics.csv")
    ablation_seed = read_csv(RESULTS / "ablation_seed_metrics.csv")
    stress = read_csv(RESULTS / "stress_sweep.csv")
    fixed = read_csv(RESULTS / "fixed_risk_metrics.csv")
    fixed_pairs = read_csv(RESULTS / "fixed_risk_pairwise.csv")
    negative = read_csv(RESULTS / "negative_cases.csv")
    summary = parse_summary((RESULTS / "summary.txt").read_text(encoding="utf-8"))

    proposal = "latent_asymmetry_belief_policy_v5"
    best_ref = summary["best_success_reference"]
    prop_success = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": proposal}, "task_success")
    prop_tracking = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": proposal}, "tracking_error")
    prop_safety = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": proposal}, "safety_violation")
    prop_utility = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": proposal}, "robust_utility")
    best_success = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": best_ref}, "task_success")
    best_tracking = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": summary["best_tracking_reference"]}, "tracking_error")
    best_safety = metric_lookup(hard_metrics, {"split": "hard_aggregate", "method": summary["best_safety_reference"]}, "safety_violation")

    rows_text = (
        f"{count_rows('rollouts.csv'):,} main rollouts, {count_rows('dataset_summary.csv'):,} actuator summaries, "
        f"{count_rows('ablation_rollouts.csv'):,} ablation rollouts, {count_rows('stress_sweep_raw.csv'):,} stress rows, "
        f"{count_rows('fixed_risk_raw.csv'):,} fixed-risk rows, and {count_rows('negative_cases.csv')} negative cases"
    )

    lines = [
        r"\documentclass{article}",
        r"\usepackage{iclr2026_conference,times}",
        r"\input{math_commands.tex}",
        r"\usepackage{hyperref}",
        r"\usepackage{url}",
        r"\usepackage{booktabs}",
        r"\usepackage{graphicx}",
        r"\usepackage{array}",
        r"\usepackage{longtable}",
        r"\usepackage{xcolor}",
        r"\usepackage{amsmath,amssymb}",
        r"\hypersetup{colorlinks=false,pdfborder={0 0 1.8},citebordercolor={0 1 0},linkbordercolor={1 0.55 0},urlbordercolor={0 0.45 1}}",
        r"\graphicspath{{../figures/}}",
        r"\newcommand{\methodname}{latent-asymmetry belief policy v5}",
        r"\title{Actuator Asymmetry as Policy State:\\A 25+ Page Negative Submission-Readiness Audit}",
        r"\author{Anonymous Authors}",
        r"\begin{document}",
        r"\maketitle",
        r"\begin{abstract}",
        (
            "Robotic controllers often treat actuator mismatch as calibration noise: estimate a scalar gain, widen a robustness tube, or let online adaptation absorb the residual. "
            "This paper tests the sharper hypothesis that left-right, sign-specific, delayed, and drifting actuator asymmetry should be represented as latent policy state. "
            f"We rebuilt the archived Paper 86 into a frozen CPU-only v5 audit with {rows_text}. "
            f"On the predefined hard aggregate, \\methodname{{}} reaches {fmt_pm(*prop_success)} task success, tracking error {prop_tracking[0]:.3f}, safety violation {prop_safety[0]:.3f}, and robust utility {prop_utility[0]:.3f}. "
            f"The strongest non-oracle success baseline, {method_name(best_ref)}, reaches {fmt_pm(*best_success)} task success, tracking error {best_tracking[0]:.3f}, and safety violation {best_safety[0]:.3f}. "
            f"The paired lower95 success bound is {float(summary['paired_success_lower95']):.3f}, but the paired tracking upper95 bound is {float(summary['paired_tracking_upper95']):.3f}, the paired safety upper95 bound is {float(summary['paired_safety_upper95']):.3f}, the mechanism gate fails, fixed-risk coverage at budget 0.05 is zero, and no robot or accepted high-fidelity benchmark evidence exists. "
            "The honest terminal decision is therefore \\textbf{KILL/ARCHIVE}, not ICLR-main submission."
        ),
        r"\end{abstract}",
        r"\section{Terminal Decision}",
        (
            "\\textbf{Decision: KILL/ARCHIVE for ICLR main.} "
            "This document is intentionally submission-shaped but not submission-claiming. "
            "The rebuild added a stronger belief-state method, stronger adaptive/control-barrier/fault-observer baselines, fixed gates, stress tests, and appendices that expose every predefined result. "
            "The result still does not survive hostile review because the proposed method improves success over v4 but worsens tracking and safety, fails the mechanism gate, fails the fixed-risk deployment gate, and remains synthetic-only."
        ),
        (
            f"The frozen primary comparison is against {method_name(best_ref)}. "
            f"Belief state v5 has hard-aggregate success {fmt_pm(*prop_success)} while {method_name(best_ref)} has {fmt_pm(*best_success)}. "
            "That success gain is real in the local benchmark, but the paper does not get to stop at the favorable metric. "
            f"V5 tracking is {prop_tracking[0]:.3f} against the best tracking baseline at {best_tracking[0]:.3f}, and v5 safety violation is {prop_safety[0]:.3f} against the best safety baseline at {best_safety[0]:.3f}."
        ),
        (
            "The paper is valuable as an archive because it says something concrete: explicit asymmetry state can improve task success under actuator faults, but the new belief mechanism is not yet a deployable robotics contribution. "
            "A hostile reviewer would focus on safety, risk calibration, and lack of external robot validation, so those failures are the headline rather than the footnote."
        ),
        r"\section{Research Question And Review Threat Model}",
        (
            "The target claim is not merely that adaptation helps. "
            "The target claim is that actuator asymmetry is a state variable: a policy should condition on persistent left-right gain gaps, sign-specific deadzones, saturation asymmetry, latency, thermal drift, and intermittent faults rather than compressing them into one scalar correction. "
            "This sits near robust robot control, observer-based adaptation, system identification, residual policies, sim-to-real transfer, and morphology-aware locomotion "
            f"\\citep{{{cite_keys[0]},{cite_keys[1]},{cite_keys[2]},{cite_keys[3]},{cite_keys[4]},{cite_keys[5]}}}."
        ),
        (
            "The hostile-review threat model is severe. "
            "A reviewer can argue that scalar calibration is enough, robust MPC already covers the uncertainty, a recurrent hidden state will learn the asymmetry implicitly, a fault observer is the right abstraction, or that any synthetic-only actuator benchmark is too weak for ICLR-main robotics claims. "
            "The v5 protocol encodes those attacks directly as baselines and gates rather than relying on a friendly comparison set."
        ),
        r"\section{Formal Setup}",
        (
            "Let $x_t\\in\\mathbb{R}^2$ be the local task state, $u_t=(u^L_t,u^R_t)$ the commanded actuator pair, and $z_t$ the latent actuator-asymmetry state. "
            "The simulator uses an asymmetric response family"
        ),
        r"\begin{equation}",
        r"a^i_t = \operatorname{clip}\{g^i_t\,\operatorname{sgn}(u^i_{t-\ell})(|u^i_{t-\ell}|-d^i)_+, -s^i, s^i\},\qquad i\in\{L,R\},",
        r"\end{equation}",
        (
            "where $g^i_t$ drifts thermally, $d^i$ is a sign-sensitive deadzone proxy, $s^i$ is saturation, and $\\ell$ is delay. "
            "The policy-state hypothesis is that conditioning on an estimate $\\hat z_t=(\\hat g^L_t,\\hat g^R_t,\\hat d^L_t,\\hat d^R_t,\\hat\\ell_t,\\hat q_t)$ should improve task success without increasing safety violations."
        ),
        r"\paragraph{Proposition 1: scalar calibration can be non-identifiable.}",
        (
            "Consider two actuators with gains $g^L=1+\\delta$ and $g^R=1-\\delta$ under a differential command pair. "
            "A scalar gain estimate $\\bar g$ can match the average forward displacement while leaving the yaw-producing difference $g^L-g^R=2\\delta$ unidentified. "
            "Therefore a scalar calibration can have small average prediction error while producing systematically wrong steering or joint-pair torques under sign reversal."
        ),
        r"\paragraph{Proposition 2: persistent latent memory helps only under slowly changing asymmetry.}",
        (
            "If $z_t$ follows a bounded-drift process $\\|z_{t+1}-z_t\\|\\leq\\eta$ and the actuator response is locally Lipschitz in $z_t$, an exponentially updated belief state can reduce one-step prediction error by averaging observation noise. "
            "If faults switch faster than the memory time constant, the same persistence becomes harmful because the posterior lags behind the true asymmetry. "
            "This is why the protocol includes both thermal drift and intermittent-fault stress axes."
        ),
        r"\paragraph{Proposition 3: fixed-risk acceptance is only meaningful with nonzero coverage.}",
        (
            "Let $\\hat r(x_t,u_t,\\hat z_t)$ be the reported deployment risk. "
            "A budget rule accepts only episodes with $\\hat r\\leq\\rho$. "
            "Even if calibration were perfect, the rule gives no deployable policy when coverage is zero. "
            "The v5 budget 0.05 result has exactly this pathology: the system can avoid risk only by refusing every episode."
        ),
        r"\section{Frozen Protocol}",
        (
            f"The frozen v5 protocol contains {rows_text}. "
            "It uses ten seeds, six tasks, eight actuator-shift splits, thirteen main methods, ten ablations, six stress axes, six stress levels, and strict fixed-risk acceptance budgets. "
            "The hard aggregate is fixed before execution as intermittent fault, payload/contact shift, and combined hard shift."
        ),
        (
            "The terminal decision was predeclared. "
            "A positive synthetic result required v5 to beat the strongest non-oracle hard-aggregate success baseline by at least 0.030, beat the strongest tracking baseline by at least 0.015, match the strongest safety baseline within 0.002, improve robust utility by at least 0.030, obtain favorable paired bounds, pass mechanism ablations, avoid maximum-stress Pareto domination, and retain fixed-risk coverage at budget 0.05. "
            "Any failure means KILL/ARCHIVE."
        ),
        hard_table(hard_metrics),
        r"\section{Main Evidence}",
        (
            "Table~\\ref{tab:hard} is the core result. "
            "Belief state v5 has the highest non-oracle hard-aggregate task success, but it does not dominate the older latent state v4 on tracking, safety, asymmetry error, or confidence-bound utility. "
            "This is exactly the kind of mixed result that a short generated paper would overclaim; the expanded audit keeps the unfavorable metrics in the main text."
        ),
        split_table(metrics),
        pairwise_table(hard_pairs, summary),
        r"\begin{figure}[tbp]\centering\includegraphics[width=0.96\linewidth]{asymmetry_hard_success_v5.png}\caption{Hard-aggregate success. Belief state v5 improves non-oracle success but remains far from an external deployment claim.}\label{fig:hard-success}\end{figure}",
        r"\begin{figure}[tbp]\centering\includegraphics[width=0.92\linewidth]{asymmetry_safety_tracking_v5.png}\caption{Tracking, safety, and asymmetry error. V5 improves some baselines but loses the frozen tracking and safety gates against v4.}\label{fig:safety-tracking}\end{figure}",
        r"\begin{figure}[tbp]\centering\includegraphics[width=0.82\linewidth]{asymmetry_pareto_v5.png}\caption{Success-safety-energy Pareto view. Marker size reflects actuator energy.}\label{fig:pareto}\end{figure}",
        r"\section{Mechanism Ablations}",
        (
            "The mechanism gate fails. "
            "The full belief-state method is better than most ablations, but the safety-clipping ablation obtains lower tracking error while having worse safety, creating a joint tradeoff that the frozen gate refuses to call a clean mechanism win. "
            "The scalar-only latent-gain ablation performs poorly, which supports the non-scalar representation claim, but that single positive mechanism result does not make the overall method impeccable."
        ),
        ablation_table(ablations),
        r"\begin{figure}[tbp]\centering\includegraphics[width=0.96\linewidth]{asymmetry_ablation_v5.png}\caption{Ablation robust utility. The full mechanism does not achieve the predeclared clean necessity margin.}\label{fig:ablation}\end{figure}",
        r"\section{Stress Tests}",
        (
            "The stress gate is the one gate v5 survives. "
            "At maximum combined stress, no non-oracle method Pareto-dominates v5 across success, tracking, safety, asymmetry error, and utility. "
            "However, a stress-gate pass cannot rescue failed main, mechanism, fixed-risk, and scope gates."
        ),
        stress_table(stress),
        r"\begin{figure}[tbp]\centering\includegraphics[width=0.90\linewidth]{asymmetry_stress_sweep_v5.png}\caption{Combined stress sweep. V5 is not dominated at maximum stress, but the absolute success rate remains low.}\label{fig:stress}\end{figure}",
        r"\section{Fixed-Risk Deployment}",
        (
            "The fixed-risk protocol is intentionally harsh because deployment claims should be harsh. "
            "A method must decide when it is safe enough to accept autonomous execution under budgets 0.02, 0.05, 0.08, and 0.10. "
            "At budget 0.05, every method has zero accepted coverage on both fixed-risk splits. "
            "This means the calibrated risk scores do not support a nontrivial deployment claim."
        ),
        fixed_table(fixed),
        r"\begin{figure}[tbp]\centering\includegraphics[width=0.90\linewidth]{asymmetry_fixed_risk_v5.png}\caption{Fixed-risk coverage on combined hard shift. Strict budget 0.05 gives zero coverage.}\label{fig:fixed}\end{figure}",
        r"\section{Negative Cases}",
        (
            "Negative cases are retained because they prevent a visually polished but brittle paper. "
            "They cover complete actuator failure, sensor bias that mimics asymmetry, contact slip, rapidly switching faults, payloads outside the modeled family, and latency instability. "
            "These cases explain why a latent actuator state is not automatically a robust robot controller."
        ),
        negative_table(negative),
        r"\section{Prior-Work Boundary}",
        (
            "The local literature pool is used as a hostile-review pressure map. "
            "The paper sits near observer-based robust control, flexible-joint manipulation, locomotion asymmetry, adaptive control, residual learning, sim-to-real adaptation, and fault-tolerant MPC "
            f"\\citep{{{cite_keys[6]},{cite_keys[7]},{cite_keys[8]},{cite_keys[9]},{cite_keys[10]},{cite_keys[11]},{cite_keys[12]}}}. "
            "Because this rebuild has no real robot benchmark, it cannot claim to beat those bodies of work directly."
        ),
        prior_work_table(prior_rows, cite_keys),
        r"\section{Reproducibility}",
        (
            "All tables and figures are regenerated by running \\texttt{python src\\textbackslash run\\_experiment.py} from the repository root. "
            "The script streams raw CSVs and aggregates seed-level statistics. "
            "The canonical local PDF is \\texttt{C:/Users/wangz/Downloads/86.pdf}; no Desktop copy is part of the artifact contract."
        ),
        longtable(
            "Artifact & Rows",
            [f"{tex_escape(name)} & {count_rows(name)}\\\\" for name in ROW_FILES],
            "p{0.55\\linewidth}r",
            "Validated row counts for the v5 evidence package.",
            "tab:counts",
        ),
        r"\section{Discussion}",
        (
            "The result is not pretty, but it is useful. "
            "The belief-state policy improves hard-aggregate success, and the stress sweep suggests the representation is not pointless. "
            "But v5 increases tracking error and safety violation relative to v4, and the fixed-risk gate exposes that its risk score cannot certify useful deployment at a strict budget."
        ),
        (
            "The fastest path to revival is not another synthetic table. "
            "The paper would need hardware evidence or an accepted high-fidelity simulator benchmark, learned policies rather than deterministic proxy components, and direct comparisons against modern fault observers, adaptive MPC, safe RL, and robust residual-control baselines. "
            "It would also need a risk calibration procedure that retains nonzero coverage under a meaningful safety budget."
        ),
        r"\section{Conclusion}",
        (
            "Actuator asymmetry as policy state remains a compelling research direction. "
            "This expanded audit makes the paper more honest and much more rigorous, but it does not make it submission-ready. "
            "The correct terminal action is \\textbf{KILL/ARCHIVE} until external robot or high-fidelity evidence and a mechanism that beats strong baselines are available."
        ),
        r"\clearpage",
        r"\appendix",
        r"\section{Appendix: Full Main Evidence}",
        (
            "This appendix reports every split-method aggregate from the frozen main protocol. "
            "The purpose is to make the negative decision auditable: the hard aggregate is not hiding a strong positive result on another predefined split."
        ),
        full_main_table(metrics),
        r"\section{Appendix: Hard-Aggregate Seed Units}",
        (
            "The following seed means are the statistical units used for hard-aggregate paired tests. "
            "They show that the mixed conclusion is not a formatting artifact; the safety and tracking failures appear across seed-level aggregates."
        ),
        hard_seed_table(hard_seed),
        r"\section{Appendix: Complete Paired Tests}",
        (
            "The table below gives every hard-aggregate paired difference for v5 minus each reference method across the predefined paired metrics. "
            "Primary success succeeds against v4, but tracking and safety fail against v4."
        ),
        full_pairwise_table(hard_pairs),
        r"\section{Appendix: Complete Stress Sweep}",
        (
            "The main text highlights combined stress because it is the most important deployment stressor, but all axes are reported here. "
            "This table includes gain asymmetry, deadzone/saturation, latency, thermal drift, intermittent fault, and combined stress."
        ),
        full_stress_table(stress),
        r"\section{Appendix: Complete Fixed-Risk Table}",
        (
            "The fixed-risk appendix reports every split, budget, and method. "
            "The strict budget 0.05 failure is visible in the full table rather than only in the summary."
        ),
        full_fixed_table(fixed),
        r"\section{Appendix: Fixed-Risk Paired Tests}",
        (
            "The fixed-risk paired table reports coverage and accepted-episode differences across all budgets. "
            "It is included because a deployment reviewer would not accept a single budget-only summary."
        ),
        fixed_pairwise_table(fixed_pairs),
        r"\section{Appendix: Ablation Seed Units}",
        (
            "The mechanism gate was evaluated on seed means from payload/contact and combined hard shift. "
            "The full mechanism does not achieve the required clean robust-utility margin over all ablations."
        ),
        ablation_seed_table(ablation_seed),
        r"\bibliographystyle{iclr2026_conference}",
        r"\bibliography{references}",
        r"\end{document}",
    ]
    (PAPER / "main.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote paper/main.tex and paper/references.bib")


if __name__ == "__main__":
    main()
