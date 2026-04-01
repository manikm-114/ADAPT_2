import json
from pathlib import Path
import pandas as pd

def summarize(run_dir: Path):
    df = pd.read_csv(run_dir / "metrics.csv")

    # concentration stats
    max_conc = float(df["concentration"].max())
    final_conc = float(df["concentration"].iloc[-1])

    # first time intervention becomes True (if ever)
    inter = df["intervention_active"].astype(str).str.lower().isin(["true", "1", "yes"])
    t_first = int(df.loc[inter, "t"].iloc[0]) if inter.any() else None

    # optional helpful stats
    max_share = float(df["within_cluster_share"].max())
    final_backlog = int(df["backlog"].iloc[-1])

    return {
        "run_dir": str(run_dir),
        "max_concentration": max_conc,
        "final_concentration": final_conc,
        "t_intervention_first": t_first,
        "max_within_cluster_share": max_share,
        "final_backlog": final_backlog,
    }

mit = Path(r"outputs/runs/20260323_105410_collusion_attack")
nomit = Path(r"outputs/runs/20260323_105413_collusion_attack_no_mitigation")

out = {
    "mitigation_enabled": summarize(mit),
    "mitigation_disabled": summarize(nomit),
}

# Pretty print
print(json.dumps(out, indent=2))

# Also print a paper-friendly 2-line summary
m = out["mitigation_enabled"]
n = out["mitigation_disabled"]
print()
print("=== Paper-friendly summary ===")
print(f"Mitigation enabled:   max conc={m['max_concentration']:.3f}, final conc={m['final_concentration']:.3f}, intervention first t={m['t_intervention_first']}")
print(f"Mitigation disabled:  max conc={n['max_concentration']:.3f}, final conc={n['final_concentration']:.3f}, intervention first t={n['t_intervention_first']}")
