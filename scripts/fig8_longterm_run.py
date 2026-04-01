from __future__ import annotations
import sys
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def load_yaml(path: str | Path):
    return yaml.safe_load(Path(path).read_text())


def sigmoid(x, k=4.0):
    return 1 / (1 + np.exp(-k * x))


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def run(cfg):
    np.random.seed(cfg["run"]["seed"])

    out_root = Path(cfg["run"]["out_dir"])
    out_root.mkdir(parents=True, exist_ok=True)
    run_dir = out_root / "fig8_longterm"
    run_dir.mkdir(exist_ok=True)

    T = cfg["sim"]["T"]
    gov = cfg["governance"]

    # ------------------------------
    # initial policy state
    # ------------------------------
    ai = gov["ai_min"]
    triage = gov["triage_min"]

    # ------------------------------
    # lagged states
    # ------------------------------
    lag_signal = cfg["postpub_signal"]["base"]
    lag_quality = cfg["objectives"]["quality_base"]
    lag_trust = cfg["objectives"]["trust_base"]

    # ------------------------------
    # cumulative trust erosion
    # ------------------------------
    trust_deficit_cum = 0.0

    rows = []

    for t in range(T):

        # ------------------------------
        # exogenous post-pub signal
        # ------------------------------
        raw_signal = (
            cfg["postpub_signal"]["base"]
            + cfg["postpub_signal"]["drift_per_t"] * t
            + np.random.normal(0, cfg["postpub_signal"]["noise_std"])
        )

        lag_signal = (
            cfg["postpub_signal"]["lag_alpha"] * raw_signal
            + (1 - cfg["postpub_signal"]["lag_alpha"]) * lag_signal
        )

        # ------------------------------
        # synthetic objectives
        # ------------------------------
        quality = clamp(
            cfg["objectives"]["quality_base"]
            + cfg["objectives"]["quality_sensitivity"] * np.tanh(1 - ai),
            0, 1,
        )

        trust = clamp(
            cfg["objectives"]["trust_base"]
            - cfg["objectives"]["trust_sensitivity"] * ai,
            0, 1,
        )

        lag_quality = (
            cfg["objectives"]["lag_alpha"] * quality
            + (1 - cfg["objectives"]["lag_alpha"]) * lag_quality
        )
        lag_trust = (
            cfg["objectives"]["lag_alpha"] * trust
            + (1 - cfg["objectives"]["lag_alpha"]) * lag_trust
        )

        # ------------------------------
        # cumulative trust erosion (stock)
        # ------------------------------
        trust_baseline = gov.get("trust_baseline", cfg["objectives"]["trust_base"])
        gain = gov.get("trust_integrator_gain", 0.05)
        cap = gov.get("trust_integrator_cap", 6.0)

        trust_deficit = max(0.0, trust_baseline - lag_trust)
        trust_deficit_cum = min(cap, trust_deficit_cum + gain * trust_deficit)

        # ------------------------------
        # nonlinear structural control
        # ------------------------------
        push_signal = sigmoid((lag_signal - 0.35) * 2.5, gov["k_signal"])
        conflict = lag_quality - lag_trust
        push_conflict = sigmoid(conflict * 3.0, gov["k_conflict"])

        # --- AI responds to cumulative erosion ---
        ai_stock = sigmoid((trust_deficit_cum - 2.0), 2.0)
        ai_target = gov["ai_min"] + (gov["ai_max"] - gov["ai_min"]) * ai_stock

        ai = gov["inertia"] * ai + (1 - gov["inertia"]) * ai_target
        ai = clamp(ai, gov["ai_min"], gov["ai_max"])

        # --- triage responds weakly to post-pub pressure ---
        triage_target = triage + gov["triage_step"] * (push_signal - 0.5)
        triage = gov["inertia"] * triage + (1 - gov["inertia"]) * triage_target
        triage = clamp(triage, gov["triage_min"], gov["triage_max"])

        # ------------------------------
        # record
        # ------------------------------
        rows.append(
            {
                "t": t,
                "postpub_signal_raw": raw_signal,
                "postpub_signal_lag": lag_signal,
                "quality_lag": lag_quality,
                "trust_lag": lag_trust,
                "trust_deficit_cum": trust_deficit_cum,
                "ai_fraction_policy": ai,
                "triage_threshold": triage,
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(run_dir / "metrics.csv", index=False)
    print(f"[OK] Figure 8 run complete: {run_dir}/metrics.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    run(cfg)


if __name__ == "__main__":
    main()
