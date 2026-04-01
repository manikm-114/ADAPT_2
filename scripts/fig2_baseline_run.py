from __future__ import annotations

# ============================================================
# Figure 2 — Baseline stability run (clean + reproducible)
# ============================================================

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import argparse
import json

import numpy as np
import pandas as pd
import yaml

# ------------------------------------------------------------
# Make sure src/ is importable
# ------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from adapt.core.types import Manuscript, Reviewer, Review, Policy, State, Decision
from adapt.core.rng import seed_all
from adapt.core.logging import EventLogger
from adapt.mechanisms.triage import triage_select
from adapt.mechanisms.governance import adapt_policy


# ============================================================
# Utilities
# ============================================================

def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


# ============================================================
# Agent generation
# ============================================================

def make_reviewers(cfg: Dict[str, Any]) -> List[Reviewer]:
    n_h = int(cfg["reviewers"]["n_humans"])
    n_ai = int(cfg["reviewers"]["n_ai"])
    max_load = int(cfg["reviewers"]["max_load"])

    reviewers: List[Reviewer] = []

    for i in range(n_h):
        reliability = float(np.clip(np.random.normal(0.70, 0.12), 0.2, 0.98))
        bias = float(np.random.normal(0.0, 0.03))
        reviewers.append(
            Reviewer(i, "human", reliability, bias, max_load)
        )

    for j in range(n_ai):
        rid = n_h + j
        reliability = float(np.clip(np.random.normal(0.78, 0.10), 0.2, 0.99))
        bias = float(np.random.normal(0.0, 0.02))
        reviewers.append(
            Reviewer(rid, "ai", reliability, bias, max_load)
        )

    return reviewers


# ============================================================
# Submission + review mechanics (unchanged)
# ============================================================

def sample_submissions(cfg, t, state) -> List[Manuscript]:
    lam = cfg["submissions"]["mean_per_timestep"]
    n = int(np.random.poisson(lam))
    out = []

    for _ in range(n):
        q = float(np.clip(np.random.normal(
            cfg["submissions"]["quality_mean"],
            cfg["submissions"]["quality_std"]
        ), 0, 1))
        c = float(np.clip(np.random.normal(
            cfg["submissions"]["complexity_mean"],
            cfg["submissions"]["complexity_std"]
        ), 0, 1))

        mid = state.next_mid
        state.next_mid += 1
        out.append(Manuscript(mid, t, q, c))

    return out


def choose_reviewers(state: State, k: int) -> List[Reviewer]:
    available = [r for r in state.reviewers if r.load < r.max_load]
    if len(available) < k:
        available = list(state.reviewers)
    return list(np.random.choice(available, size=k, replace=False))


def generate_review(m: Manuscript, r: Reviewer) -> Review:
    noise = (0.18 + 0.22 * m.complexity) * (1.05 - r.reliability)
    score = clamp01(m.quality_true + r.bias + np.random.normal(0, noise))
    completeness = clamp01(0.4 + 0.6 * r.reliability - 0.3 * m.complexity)
    return Review(m.mid, r.rid, score, r.reliability, completeness, 1.0)


def meta_signals(reviews: List[Review]) -> Tuple[float, float]:
    scores = np.array([r.score for r in reviews])
    comps = np.array([r.completeness for r in reviews])
    return float(np.var(scores) * 10), float(np.mean(comps))


def decide(cfg, reviews) -> Decision:
    scores = np.array([r.score for r in reviews])
    mu = scores.mean()
    d = scores.var() * 10
    if d <= cfg["decision"]["disagreement_guard"] and mu >= cfg["decision"]["accept_threshold"]:
        return "ACCEPT"
    if d <= cfg["decision"]["disagreement_guard"] and mu <= cfg["decision"]["reject_threshold"]:
        return "REJECT"
    return "DELIBERATE"


# ============================================================
# Main simulation loop (baseline)
# ============================================================

def run_baseline(cfg: Dict[str, Any]) -> Path:
    seed_all(cfg["run"]["seed"])

    out_root = ROOT / cfg["run"]["out_dir"]
    out_root.mkdir(parents=True, exist_ok=True)

    from adapt.core.logging import now_tag
    run_dir = out_root / f"{now_tag()}_{cfg['run']['run_name']}"
    run_dir.mkdir()

    state = State()
    state.reviewers = make_reviewers(cfg)
    state.policy = Policy(
        ai_fraction=cfg["review_process"]["ai_fraction_target"],
        triage_threshold=cfg["triage"]["threshold"],
        escalation_enabled=cfg["review_process"]["escalation_enabled"],
    )

    rows = []

    for t in range(cfg["sim"]["T"]):
        state.t = t

        new_ms = sample_submissions(cfg, t, state)
        state.backlog.extend(new_ms)

        processed, _ = triage_select(
            state.backlog, state.policy,
            max_to_keep=cfg["capacity"]["max_reviews_per_timestep"] // cfg["review_process"]["k_reviewers"]
        )

        state.backlog = [m for m in state.backlog if m not in processed]

        disagreements = []

        for m in processed:
            reviews = []
            for r in choose_reviewers(state, cfg["review_process"]["k_reviewers"]):
                r.load += 1
                reviews.append(generate_review(m, r))

            d, _ = meta_signals(reviews)
            disagreements.append(d)

            dec = decide(cfg, reviews)
            state.decided[m.mid] = dec
            if dec == "ACCEPT":
                state.n_accept += 1
            elif dec == "REJECT":
                state.n_reject += 1
            else:
                state.n_deliberate += 1

        mean_dis = float(np.mean(disagreements)) if disagreements else 0.0

        # --- ADAPT policy update (unchanged, safe) ---
        adapt_policy(
            state,
            cfg,
            metrics={
                "backlog": len(state.backlog),
                "mean_disagreement": mean_dis,
            },
        )

        rows.append({
            "t": t,
            "submitted": len(new_ms),
            "processed": len(processed),
            "mean_disagreement": mean_dis,
            "backlog": len(state.backlog),
            "ai_fraction_policy": state.policy.ai_fraction,
            "triage_threshold": state.policy.triage_threshold,
        })

    df = pd.DataFrame(rows)
    df.to_csv(run_dir / "metrics.csv", index=False)

    return run_dir


# ============================================================
# Entry point
# ============================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = load_yaml(Path(args.config))
    run_dir = run_baseline(cfg)

    print(f"[OK] Baseline run complete: {run_dir}")


if __name__ == "__main__":
    main()
