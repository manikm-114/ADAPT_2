from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
import time


Decision = Literal["ACCEPT", "REJECT", "DELIBERATE"]


@dataclass
class Manuscript:
    mid: int
    t_submitted: int
    quality_true: float          # latent "ground truth"
    complexity: float            # affects reviewer noise/effort
    domain: str = "general"
    coi_risk: bool = False


@dataclass
class Reviewer:
    rid: int
    kind: Literal["human", "ai"]
    reliability: float           # higher = less noise, more complete
    bias: float                  # systematic score shift
    max_load: int
    load: int = 0
    credit: float = 0.0
    # editor eligibility later
    editor_score: float = 0.0


@dataclass
class Review:
    mid: int
    rid: int
    score: float                 # 0..1 normalized
    confidence: float            # 0..1
    completeness: float          # 0..1 proxy for review quality
    time_cost: float             # proxy


@dataclass
class Policy:
    # adaptive knobs (we’ll expand later)
    ai_fraction: float
    triage_threshold: float
    escalation_enabled: bool


@dataclass
class State:
    t: int = 0
    next_mid: int = 0
    next_event_id: int = 0

    backlog: List[Manuscript] = field(default_factory=list)
    decided: Dict[int, Decision] = field(default_factory=dict)

    reviewers: List[Reviewer] = field(default_factory=list)

    # running counters (for summary)
    n_submitted: int = 0
    n_reviewed: int = 0
    n_escalations: int = 0
    n_accept: int = 0
    n_reject: int = 0
    n_deliberate: int = 0

    # policy state
    policy: Optional[Policy] = None

    created_at: float = field(default_factory=lambda: time.time())
