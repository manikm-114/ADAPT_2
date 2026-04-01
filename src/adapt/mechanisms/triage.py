from __future__ import annotations
from typing import List, Tuple
import numpy as np

from adapt.core.types import Manuscript, Policy


def triage_score(m: Manuscript) -> float:
    """
    Cheap, noisy proxy of manuscript promise (NOT true quality).
    Higher is better.
    """
    noise = np.random.normal(0.0, 0.15)
    score = 0.6 * m.quality_true + 0.4 * (1.0 - m.complexity) + noise
    return float(np.clip(score, 0.0, 1.0))


def triage_select(
    manuscripts: List[Manuscript],
    policy: Policy,
    max_to_keep: int,
) -> Tuple[List[Manuscript], List[Tuple[int, float]]]:
    """
    Returns:
      - selected manuscripts to process now
      - (mid, triage_score) for logging/debug
    """
    scored = [(triage_score(m), m) for m in manuscripts]
    scored.sort(key=lambda x: x[0], reverse=True)

    # Apply threshold
    kept = [(s, m) for (s, m) in scored if s >= policy.triage_threshold]

    selected = [m for (s, m) in kept[:max_to_keep]]
    score_pairs = [(m.mid, float(s)) for (s, m) in kept[:max_to_keep]]
    return selected, score_pairs
