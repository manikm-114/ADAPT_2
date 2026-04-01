from __future__ import annotations
from typing import Dict

from adapt.core.types import State


def adapt_policy(state: State, cfg: Dict, metrics: Dict) -> None:
    backlog = metrics["backlog"]
    disagreement = metrics["mean_disagreement"]
    gov = cfg["governance"]

    # Ablation/diagnostic toggles (default: False, preserves current behavior)
    disable_escalation = gov.get("disable_escalation", False)
    no_hysteresis = gov.get("no_hysteresis", False)
    no_bounds = gov.get("no_bounds", False)

    # Safe fallbacks
    triage_step = gov.get("triage_step", 0.02)
    triage_cap = gov.get("triage_max", cfg["triage"]["threshold"] + 0.15)
    ai_min = gov.get("ai_min", state.policy.ai_fraction)
    ai_max = gov.get("ai_max", state.policy.ai_fraction)
    ai_step = gov.get("ai_step", 0.01)

    def _triage_up(x: float) -> float:
        x = x + triage_step
        return x if no_bounds else min(triage_cap, x)

    def _ai_up(x: float) -> float:
        x = x + ai_step
        return x if no_bounds else min(ai_max, x)

    def _ai_down(x: float) -> float:
        x = x - ai_step
        return x if no_bounds else max(ai_min, x)

    # ==============================
    # DISAGREEMENT REGIME
    # ==============================
    if no_hysteresis:
        # Single-threshold behavior (intentionally more reactive)
        if disagreement >= gov["disagreement_high"]:
            state.policy.escalation_enabled = (not disable_escalation)
            state.policy.triage_threshold = _triage_up(state.policy.triage_threshold)

            # keep ai_fraction within bounds unless no_bounds
            if not no_bounds:
                state.policy.ai_fraction = max(ai_min, min(state.policy.ai_fraction, ai_max))
        else:
            state.policy.escalation_enabled = False
    else:
        if disagreement >= gov["disagreement_high"]:
            state.policy.escalation_enabled = (not disable_escalation)

            state.policy.triage_threshold = _triage_up(state.policy.triage_threshold)

            # keep ai_fraction within bounds unless no_bounds
            if not no_bounds:
                state.policy.ai_fraction = max(ai_min, min(state.policy.ai_fraction, ai_max))
            return

        if disagreement <= gov["disagreement_low"]:
            state.policy.escalation_enabled = False

    # ==============================
    # BACKLOG REGIME + RECOVERY
    # ==============================
    cooldown = gov.get("escalation_cooldown", 0)
    recovery_steps = gov.get("recovery_steps", 0)
    last_t = getattr(state, "last_escalation_t", -10**9)

    in_recovery = 0 < (state.t - last_t) <= recovery_steps

    if in_recovery:
        boost = gov.get("recovery_triage_boost", 0.05)
        state.policy.triage_threshold = (state.policy.triage_threshold + boost) if no_bounds else min(triage_cap, state.policy.triage_threshold + boost)

    elif backlog > gov["backlog_high"] and (state.t - last_t) > cooldown:
        state.policy.ai_fraction = _ai_up(state.policy.ai_fraction)
        state.policy.triage_threshold = _triage_up(state.policy.triage_threshold)

    elif backlog < gov["backlog_low"]:
        state.policy.ai_fraction = _ai_down(state.policy.ai_fraction)
