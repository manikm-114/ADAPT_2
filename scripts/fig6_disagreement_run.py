from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import argparse
import numpy as np
import pandas as pd
import yaml

from adapt.core.rng import seed_all
from adapt.core.logging import EventLogger, now_tag
from adapt.core.types import Manuscript, Reviewer, Policy, State
from adapt.mechanisms.triage import triage_select
from adapt.mechanisms.governance import adapt_policy


def load_yaml(path: str | Path):
    return yaml.safe_load(Path(path).read_text())


def in_window(t: int, a: int, b: int) -> bool:
    return a <= t <= b


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def make_reviewers(cfg):
    rs = []
    for i in range(cfg["reviewers"]["n_humans"]):
        rs.append(
            Reviewer(
                rid=i,
                kind="human",
                reliability=np.clip(np.random.normal(0.70, 0.10), 0.2, 0.95),
                bias=np.random.normal(0.0, 0.03),
                max_load=cfg["reviewers"]["max_load"],
            )
        )
    base = len(rs)
    for j in range(cfg["reviewers"]["n_ai"]):
        rs.append(
            Reviewer(
                rid=base + j,
                kind="ai",
                reliability=np.clip(np.random.normal(0.78, 0.08), 0.3, 0.98),
                bias=np.random.normal(0.0, 0.02),
                max_load=cfg["reviewers"]["max_load"],
            )
        )
    return rs


def run(cfg):
    seed_all(cfg["run"]["seed"])
    out_root = Path(cfg["run"]["out_dir"])
    out_root.mkdir(parents=True, exist_ok=True)

    run_dir = out_root / f"{now_tag()}_fig6_disagreement"
    run_dir.mkdir()

    (run_dir / "config_resolved.yaml").write_text(
        yaml.safe_dump(cfg, sort_keys=False)
    )

    logger = EventLogger(run_dir / "events.jsonl")

    state = State()
    state.reviewers = make_reviewers(cfg)
    state.policy = Policy(
        ai_fraction=cfg["review_process"]["ai_fraction_target"],
        triage_threshold=cfg["triage"]["threshold"],
        escalation_enabled=False,
    )

    T = cfg["sim"]["T"]
    spike = cfg["scenario"]["disagreement_spike"]

    rows = []

    for t in range(T):
        state.t = t

        if not hasattr(state, "last_escalation_t"):
            state.last_escalation_t = -10**9

        # --- disagreement spike ---
        if in_window(t, spike["start_t"], spike["end_t"]):
            noise_multiplier = spike["noise_multiplier"]
            state.policy.escalation_enabled = True
            state.last_escalation_t = t
        else:
            noise_multiplier = 1.0
            state.policy.escalation_enabled = False

        # --- capacity with recovery boost ---
        base_capacity = cfg["capacity"]["max_reviews_per_timestep"]
        boost_steps = cfg["governance"].get("recovery_steps", 0)
        last_t = state.last_escalation_t

        if 0 < (t - last_t) <= boost_steps:
            max_reviews = int(base_capacity * 1.25)
        else:
            max_reviews = base_capacity

        # --- submissions ---
        lam = cfg["submissions"]["mean_per_timestep"]
        n_new = np.random.poisson(lam)
        for _ in range(n_new):
            state.backlog.append(
                Manuscript(
                    mid=state.next_mid,
                    t_submitted=t,
                    quality_true=np.clip(
                        np.random.normal(
                            cfg["submissions"]["quality_mean"],
                            cfg["submissions"]["quality_std"],
                        ),
                        0,
                        1,
                    ),
                    complexity=np.clip(
                        np.random.normal(
                            cfg["submissions"]["complexity_mean"],
                            cfg["submissions"]["complexity_std"],
                        ),
                        0,
                        1,
                    ),
                )
            )
            state.next_mid += 1

        # --- triage ---
        k = cfg["review_process"]["k_reviewers"]
        max_ms = max(1, max_reviews // k)

        selected, _ = triage_select(
            manuscripts=state.backlog,
            policy=state.policy,
            max_to_keep=max_ms,
        )

        processed_ids = {m.mid for m in selected}
        state.backlog = [m for m in state.backlog if m.mid not in processed_ids]

        # --- reviews ---
        disagreements = []
        for m in selected:
            scores = []
            for _ in range(k):
                s = clamp01(
                    m.quality_true
                    + np.random.normal(0, 0.15 * noise_multiplier)
                )
                scores.append(s)
            disagreements.append(np.var(scores) * 30.0)

        mean_disagreement = float(np.mean(disagreements)) if disagreements else 0.0

        # --- adapt policy ---
        adapt_policy(
            state=state,
            cfg=cfg,
            metrics={
                "backlog": len(state.backlog),
                "mean_disagreement": mean_disagreement,
            },
        )

        # --- record ---
        rows.append(
            {
                "t": t,
                "backlog": len(state.backlog),
                "mean_disagreement": mean_disagreement,
                "ai_fraction_policy": state.policy.ai_fraction,
                "triage_threshold": state.policy.triage_threshold,
                "escalation_enabled": state.policy.escalation_enabled,
                "noise_multiplier": noise_multiplier,
                "spike_start": spike["start_t"],
                "spike_end": spike["end_t"],
            }
        )

    pd.DataFrame(rows).to_csv(run_dir / "metrics.csv", index=False)
    logger.close()
    print(f"[OK] Figure 6 run complete: {run_dir}")
    return run_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = load_yaml(args.config)
    run(cfg)


if __name__ == "__main__":
    main()
