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


def read_metrics(run_dir: Path) -> pd.DataFrame:
    p = run_dir / "metrics.csv"
    if not p.exists():
        raise FileNotFoundError(f"metrics.csv not found in: {run_dir}")
    return pd.read_csv(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True, help="Path to a single baseline run directory")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    df = read_metrics(run_dir)

    outdir = Path("paper_assets/figures")
    outdir.mkdir(parents=True, exist_ok=True)

    t = df["t"]

    # =========================
    # Figure 2: Baseline stability
    # =========================
    fig, axs = plt.subplots(
        2, 1,
        figsize=(7.2, 6.5),
        sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.4]}
    )

    # ---------
    # (a) Backlog dynamics
    # ---------
    axs[0].plot(t, df["backlog"], color="#1f77b4", label="Backlog size")
    axs[0].set_ylabel("Backlog size")
    axs[0].set_title("Baseline Stability (No Stress Regime)")
    axs[0].grid(alpha=0.3)
    axs[0].legend(loc="upper left")

    # ---------
    # (b) Governance control signals
    # ---------
    ax_left = axs[1]
    ax_right = ax_left.twinx()

    l1, = ax_left.plot(
        t,
        df["ai_fraction_policy"],
        color="#ff7f0e",
        label="AI reviewer fraction"
    )
    ax_left.set_ylabel("AI fraction")

    l2, = ax_right.plot(
        t,
        df["triage_threshold"],
        color="#2ca02c",
        linestyle="--",
        label="Triage threshold"
    )
    ax_right.set_ylabel("Triage threshold")

    ax_left.grid(alpha=0.3)
    axs[1].set_xlabel("Time step")

    # Combined legend
    lines = [l1, l2]
    labels = [l.get_label() for l in lines]
    axs[1].legend(lines, labels, loc="upper left")

    fig.tight_layout()
    fig.savefig(outdir / "fig2_baseline_stability.png")
    plt.close(fig)

    print(f"[OK] Figure 2 saved to: {outdir / 'fig2_baseline_stability.png'}")


if __name__ == "__main__":
    main()
