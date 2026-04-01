from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def load_yaml(path: str | Path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def run(cfg: dict) -> Path:
    np.random.seed(int(cfg["run"]["seed"]))

    out_root = Path(cfg["run"]["out_dir"])
    out_root.mkdir(parents=True, exist_ok=True)

    run_name = cfg["run"].get("run_name", "fig7_postpub_credit")
    run_dir = out_root / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    T = int(cfg["sim"]["T"])

    a_cfg = cfg["authors"]
    r_cfg = cfg["reviewers"]

    high_credit = float(a_cfg.get("initial_credit", 0.0))
    low_credit = float(a_cfg.get("initial_credit", 0.0))
    insightful_credit = float(r_cfg.get("initial_credit", 0.0))
    noisy_credit = float(r_cfg.get("initial_credit", 0.0))

    rows = []

    for t in range(T):
        high_mean = float(a_cfg["high_quality_base_impact"]) + float(a_cfg["impact_drift_per_t"]) * t
        low_mean = float(a_cfg["low_quality_base_impact"]) + 0.4 * float(a_cfg["impact_drift_per_t"]) * t

        high_impact = max(
            0.0,
            np.random.poisson(max(0.1, high_mean)) + np.random.normal(0.0, float(a_cfg["impact_noise_std"]))
        )
        low_impact = max(
            0.0,
            np.random.poisson(max(0.1, low_mean)) + np.random.normal(0.0, float(a_cfg["impact_noise_std"]))
        )

        expected_impact = float(a_cfg["expected_impact"])
        alpha_a = float(a_cfg["alpha"])
        alpha_r = float(r_cfg["alpha"])

        high_credit += alpha_a * (high_impact - expected_impact)
        low_credit += alpha_a * (low_impact - expected_impact)

        insightful_alignment = clamp(
            float(r_cfg["insightful_alignment"]) + np.random.normal(0.0, float(r_cfg["noise_std"])),
            -1.0, 1.0
        )
        noisy_alignment = clamp(
            float(r_cfg["noisy_alignment"]) + np.random.normal(0.0, float(r_cfg["noise_std"])),
            -1.0, 1.0
        )

        insightful_credit += alpha_r * insightful_alignment
        noisy_credit += alpha_r * noisy_alignment

        rows.append({
            "time": t,
            "credit_high_quality_author": high_credit,
            "credit_low_quality_author": low_credit,
            "credit_insightful_reviewer": insightful_credit,
            "credit_noisy_reviewer": noisy_credit,
            "impact_high_quality_author": high_impact,
            "impact_low_quality_author": low_impact,
        })

    df = pd.DataFrame(rows)
    df.to_csv(run_dir / "postpub_metrics.csv", index=False)
    (run_dir / "config_resolved.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    (run_dir / "summary.json").write_text(json.dumps({
        "T": T,
        "final_high_quality_author_credit": float(df["credit_high_quality_author"].iloc[-1]),
        "final_low_quality_author_credit": float(df["credit_low_quality_author"].iloc[-1]),
        "final_insightful_reviewer_credit": float(df["credit_insightful_reviewer"].iloc[-1]),
        "final_noisy_reviewer_credit": float(df["credit_noisy_reviewer"].iloc[-1]),
    }, indent=2), encoding="utf-8")

    print(f"[OK] Post-publication credit run complete: {run_dir}")
    return run_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    run(cfg)


if __name__ == "__main__":
    main()
