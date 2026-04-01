from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "font.size": 11,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "legend.fontsize": 10,
    "lines.linewidth": 2.0,
})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True)
    ap.add_argument("--out_dir", default="simulator_web/_generated")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(run_dir / "postpub_metrics.csv")

    plt.figure(figsize=(8, 5.5))
    plt.plot(df["time"], df["credit_high_quality_author"], label="High-quality author")
    plt.plot(df["time"], df["credit_low_quality_author"], label="Low-quality author")
    plt.plot(df["time"], df["credit_insightful_reviewer"], label="Insightful reviewer")
    plt.plot(df["time"], df["credit_noisy_reviewer"], label="Noisy reviewer")
    plt.xlabel("Post-publication time step")
    plt.ylabel("Cumulative credit")
    plt.title("Post-publication credit dynamics")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    out_path = out_dir / "fig7_postpub_credit_dynamics.png"
    plt.savefig(out_path, dpi=300)
    plt.close()

    print(f"[OK] Saved {out_path}")

if __name__ == "__main__":
    main()
