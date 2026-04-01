from pathlib import Path
import pandas as pd

# ============================================================
# Paths
# ============================================================
ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "outputs" / "runs"
OUT_DIR = ROOT / "paper_assets" / "tables"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# Scenarios corresponding to Figures 2--6
# ============================================================
SCENARIOS = {
    "Baseline": RUNS / "fig2_baseline" / "metrics.csv",
    "Submission surge": RUNS / "fig3_submission_surge_recovery" / "metrics.csv",
    "Quality drift": RUNS / "fig4_quality_drift_run" / "metrics.csv",
    "Disagreement spike": RUNS / "fig6_disagreement" / "metrics.csv",
}

# ============================================================
# Build Table 2
# ============================================================
rows = []

for scenario_name, csv_path in SCENARIOS.items():
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing CSV file: {csv_path}")

    df = pd.read_csv(csv_path)

    # --------------------------------------------------------
    # Steady-state definition
    # Last 20% of timesteps
    # --------------------------------------------------------
    T = len(df)
    if T < 10:
        raise ValueError(f"Run too short for steady-state analysis: {csv_path}")

    W = max(1, int(0.2 * T))
    steady_df = df.iloc[-W:]

    # --------------------------------------------------------
    # Policy variables: mean over steady-state window
    # --------------------------------------------------------
    ai_fraction_ss = steady_df["ai_fraction_policy"].mean()
    triage_threshold_ss = steady_df["triage_threshold"].mean()

    # --------------------------------------------------------
    # Backlog: median over steady-state window
    # (robust, matches visual interpretation)
    # --------------------------------------------------------
    backlog_ss = steady_df["backlog"].median()

    # --------------------------------------------------------
    # Escalation: whether active at any point in steady window
    # --------------------------------------------------------
    if "escalation_enabled" in steady_df.columns:
        escalation_active = bool(steady_df["escalation_enabled"].any())
    else:
        escalation_active = False

    rows.append({
        "Scenario": scenario_name,
        "AI fraction": round(ai_fraction_ss, 2),
        "Triage threshold": round(triage_threshold_ss, 2),
        "Escalation active": "Yes" if escalation_active else "No",
        "Final backlog": int(round(backlog_ss)),
    })

# ============================================================
# Export Table 2
# ============================================================
table2 = pd.DataFrame(rows)

tex_path = OUT_DIR / "table2_final_states.tex"
table2.to_latex(tex_path, index=False)

print("\n[OK] Table 2 regenerated using steady-state window (last 20%)")
print(table2)
print(f"\nSaved to: {tex_path}")
