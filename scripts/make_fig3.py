from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Global plotting defaults
# =========================
plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "font.size": 11,
    "axes.labelsize": 11,
    "axes.titlesize": 13,
    "legend.fontsize": 10,
    "lines.linewidth": 2.2,
})

# =========================
# Main plotting function
# =========================
def plot_figure3(run_dir: Path, out_dir: Path):
    df = pd.read_csv(run_dir / "metrics.csv")

    fig, axs = plt.subplots(
        2, 1, figsize=(7.5, 6.5), sharex=True,
        gridspec_kw={"height_ratios": [2, 1]}
    )

    # -------------------------------------------------
    # Top panel: submission surge and backlog
    # -------------------------------------------------
    axs[0].plot(df["t"], df["submitted"], label="Submitted", color="#1f77b4")
    axs[0].plot(df["t"], df["backlog"], label="Backlog", color="#ff7f0e")

    axs[0].set_ylabel("Manuscripts per timestep")
    axs[0].legend(loc="upper left")
    axs[0].set_title("Adaptive Response to Submission Surge")

    # Highlight surge window (visual aid, optional but recommended)
    axs[0].axvspan(5, 9, color="gray", alpha=0.15, label="Surge window")

    # -------------------------------------------------
    # Bottom panel: governance response
    # -------------------------------------------------
    ax2 = axs[1]
    ax3 = ax2.twinx()

    ax2.plot(
        df["t"], df["ai_fraction_policy"],
        color="#2ca02c", label="AI reviewer fraction"
    )
    ax3.plot(
        df["t"], df["triage_threshold"],
        color="#d62728", linestyle="--", label="Triage threshold"
    )

    ax2.set_ylabel("AI fraction")
    ax3.set_ylabel("Triage threshold")

    ax2.set_xlabel("Timestep")

    # Combined legend
    lines = ax2.get_lines() + ax3.get_lines()
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc="upper left")

    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / "fig3_submission_surge_recovery.png")
    plt.close(fig)


# =========================
# CLI
# =========================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True, help="Path to run directory containing metrics.csv")
    ap.add_argument(
        "--out_dir",
        default="../paper_assets/figures",
        help="Output directory for figures"
    )
    args = ap.parse_args()

    plot_figure3(Path(args.run_dir), Path(args.out_dir))
    print("[OK] Figure 3 saved successfully.")


if __name__ == "__main__":
    main()
