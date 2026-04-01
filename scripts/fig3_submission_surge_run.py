from __future__ import annotations

from pathlib import Path
import argparse
import yaml
import numpy as np
import pandas as pd

# =========================
# Utilities
# =========================
def load_yaml(path: str | Path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def seed_all(seed: int):
    np.random.seed(seed)


# =========================
# Main simulation
# =========================
def run(cfg: dict) -> Path:
    seed_all(int(cfg["run"]["seed"]))

    # --- output dir ---
    out_root = Path(cfg["run"]["out_dir"])
    out_root.mkdir(parents=True, exist_ok=True)

    run_name = cfg["run"].get("run_name", "submission_surge")
    run_dir = out_root / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    # --- parameters ---
    T = int(cfg["sim"]["T"])
    base_lambda = float(cfg["submissions"]["mean_per_timestep"])

    backlog = []
    rows = []

    backlog_queue = 0

    ai_frac = float(cfg["review_process"]["ai_fraction_target"])
    triage = float(cfg["triage"]["threshold"])

    ai_min = cfg["governance"]["ai_min"]
    ai_max = cfg["governance"]["ai_max"]
    ai_step = cfg["governance"]["ai_step"]

    triage_step = cfg["governance"]["triage_step"]
    triage_max = cfg["governance"]["triage_max"]

    backlog_high = cfg["governance"]["backlog_high"]
    backlog_low = cfg["governance"]["backlog_low"]

    base_capacity = int(cfg["capacity"]["max_reviews_per_timestep"])

    # =========================
    # Time loop
    # =========================
    for t in range(T):

        # ---- submission surge ----
        if 5 <= t <= 12:
            lam = base_lambda * 3.0
        else:
            lam = base_lambda

        submitted = int(np.random.poisson(lam))

        backlog_queue += submitted

        # ---- recovery capacity (KEY FIX) ----
        capacity_multiplier = 1.0
        if backlog_queue > backlog_high:
            capacity_multiplier = 2.5
        elif backlog_queue < backlog_low:
            capacity_multiplier = 1.0

        effective_capacity = int(min(base_capacity * capacity_multiplier, base_capacity * 1.8))


        processed = min(backlog_queue, effective_capacity)
        backlog_queue -= processed

        # ---- governance response ----
        if backlog_queue > backlog_high:
            ai_frac = min(ai_frac + ai_step, ai_max)
            triage = min(triage + triage_step, triage_max)
        elif backlog_queue < backlog_low:
            ai_frac = max(ai_frac - ai_step, ai_min)
            triage = max(triage - triage_step, cfg["triage"]["threshold"])

        backlog.append(backlog_queue)

        rows.append({
            "t": t,
            "submitted": submitted,
            "backlog": backlog_queue,
            "ai_fraction_policy": round(ai_frac, 3),
            "triage_threshold": round(triage, 3),
        })

    # =========================
    # Save metrics
    # =========================
    df = pd.DataFrame(rows)
    df.to_csv(run_dir / "metrics.csv", index=False)

    return run_dir


# =========================
# CLI
# =========================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    run_dir = run(cfg)

    print(f"[OK] Submission surge recovery run complete: {run_dir}")


if __name__ == "__main__":
    main()
