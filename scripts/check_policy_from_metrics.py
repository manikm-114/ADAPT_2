import sys
from pathlib import Path
import pandas as pd

run_dir = Path(sys.argv[1])
df = pd.read_csv(run_dir / "metrics.csv").sort_values("t")

col = "ai_fraction_policy"
print(f"RUN: {run_dir}")
print(f"{col}: first={df[col].iloc[0]:.3f}, last={df[col].iloc[-1]:.3f}, min={df[col].min():.3f}, max={df[col].max():.3f}")

col2 = "triage_threshold"
print(f"{col2}: first={df[col2].iloc[0]:.3f}, last={df[col2].iloc[-1]:.3f}, min={df[col2].min():.3f}, max={df[col2].max():.3f}")

if "concentration" in df.columns:
    print(f"concentration: max={df['concentration'].max():.3f}, last={df['concentration'].iloc[-1]:.3f}")
