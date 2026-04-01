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
    ap.add_argument("--run_dir", required=True, help="Path to run directory containing metrics.csv")
    ap.add_argument("--out_dir", default="../paper_assets/figures")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(run_dir / "metrics.csv")

    fig, axs = plt.subplots(3, 1, figsize=(7, 8), sharex=True)

    # --- Panel 1: Quality + Disagreement ---
    axs[0].plot(df["t"], df["mean_quality"], label="Mean quality")
    axs[0].plot(df["t"], df["mean_disagreement"], label="Mean disagreement")
    axs[0].set_ylabel("Quality / Disagreement")
    axs[0].legend()

    # --- Panel 2: Triage response ---
    axs[1].plot(df["t"], df["triage_threshold"], color="tab:orange")
    axs[1].set_ylabel("Triage threshold")

    # --- Panel 3: Backlog ---
    axs[2].plot(df["t"], df["backlog"], color="tab:green")
    axs[2].set_ylabel("Backlog")
    axs[2].set_xlabel("Timestep")

    fig.tight_layout()
    fig.savefig(out_dir / "fig4_quality_drift.png")
    plt.close(fig)

    print(f"[OK] Figure 4 saved to {out_dir}")


if __name__ == "__main__":
    main()
