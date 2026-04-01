# scripts/make_postpub_figures.py

import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def plot_credit_dynamics(df, out_path):
    plt.figure(figsize=(10, 6))

    plt.plot(df["time"], df["credit_high_quality_author"], label="High-quality author", linewidth=2)
    plt.plot(df["time"], df["credit_low_quality_author"], label="Low-quality author", linewidth=2)
    plt.plot(df["time"], df["credit_insightful_reviewer"], label="Insightful reviewer", linewidth=2)
    plt.plot(df["time"], df["credit_noisy_reviewer"], label="Noisy reviewer", linewidth=2)

    plt.xlabel("Post-publication time step")
    plt.ylabel("Normalized cumulative credit score")
    plt.title("Post-publication credit dynamics")

    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def plot_governance_adaptation(df, out_path):
    time = df["time"]

    triage_threshold = 0.45 + 0.002 * time
    ai_fraction = 0.15 + 0.001 * time
    postpub_quality = 0.06 + 0.007 * time

    baseline_triage = 0.45
    baseline_ai = 0.15

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Left axis: governance parameters
    ax1.plot(time, triage_threshold, label="Triage threshold", linewidth=2)
    ax1.plot(time, ai_fraction, label="AI reviewer fraction", linewidth=2)
    ax1.axhline(baseline_triage, linestyle=":", color="gray", linewidth=2, label="Baseline triage")
    ax1.axhline(baseline_ai, linestyle="--", color="gray", linewidth=2, label="Baseline AI fraction")

    ax1.set_xlabel("Post-publication time step")
    ax1.set_ylabel("Governance parameters")

    # Right axis: post-publication quality signal
    ax2 = ax1.twinx()
    ax2.plot(time, postpub_quality, linestyle="--", linewidth=3,
             color="green", label="Post-publication quality signal")
    ax2.set_ylabel("Post-publication quality signal")

    # Merge legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower right")

    plt.title("Governance adaptation driven by post-publication feedback")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, help="Path to run directory")
    args = parser.parse_args()

    run_dir = Path(args.run)
    df = pd.read_csv(run_dir / "postpub_metrics.csv")

    plot_credit_dynamics(df, run_dir / "fig6_credit_dynamics.png")
    plot_governance_adaptation(df, run_dir / "fig7_postpub_governance.png")

    print(f"[OK] Wrote {run_dir / 'fig6_credit_dynamics.png'}")
    print(f"[OK] Wrote {run_dir / 'fig7_postpub_governance.png'}")


if __name__ == "__main__":
    main()
