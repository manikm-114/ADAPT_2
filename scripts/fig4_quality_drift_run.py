# =========================
# Fix import path FIRST
# =========================
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

# =========================
# Standard imports
# =========================
import argparse
import yaml
import numpy as np
import pandas as pd

from adapt.core.rng import seed_all
from adapt.core.types import State, Policy
from adapt.mechanisms.governance import adapt_policy


def load_yaml(p):
    return yaml.safe_load(Path(p).read_text())


def run(cfg):
    seed_all(cfg["run"]["seed"])

    out_root = Path(cfg["run"]["out_dir"])
    out_root.mkdir(parents=True, exist_ok=True)

    run_dir = out_root / "quality_drift_run"
    run_dir.mkdir(exist_ok=True)

    T = cfg["sim"]["T"]

    # -----------------------------
    # Initial state & policy
    # -----------------------------
    state = State()
    state.policy = Policy(
        ai_fraction=cfg["review_process"]["ai_fraction_target"],
        triage_threshold=cfg["triage"]["threshold"],
        escalation_enabled=False,
    )

    backlog = 0
    quality = cfg["submissions"]["quality_mean"]

    rows = []

    for t in range(T):
        # ---- Quality drift (core stress) ----
        quality = max(0.35, quality - 0.01)

        submitted = int(np.random.poisson(cfg["submissions"]["mean_per_timestep"]))
        processed = int(
            cfg["capacity"]["max_reviews_per_timestep"]
            * (1.0 - state.policy.triage_threshold)
            / cfg["review_process"]["k_reviewers"]
        )

        backlog = max(0, backlog + submitted - processed)

        # disagreement rises as quality degrades
        mean_disagreement = float(
            0.6 + (0.7 - quality) * 2.0 + np.random.normal(0, 0.05)
        )

        # ---- ADAPT update (REQUIRES both metrics) ----
        adapt_policy(
            state=state,
            cfg=cfg,
            metrics={
                "backlog": backlog,
                "mean_disagreement": mean_disagreement,
            },
        )

        rows.append({
            "t": t,
            "submitted": submitted,
            "backlog": backlog,
            "mean_quality": quality,
            "mean_disagreement": mean_disagreement,
            "ai_fraction_policy": state.policy.ai_fraction,
            "triage_threshold": state.policy.triage_threshold,
        })

    df = pd.DataFrame(rows)
    df.to_csv(run_dir / "metrics.csv", index=False)

    print(f"[OK] Quality drift run complete: {run_dir}")
    return run_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    run(cfg)


if __name__ == "__main__":
    main()
