from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Plot style (consistent)
# =========================
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
    ap.add_argument("--out_dir", default="../paper_assets/figures")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(run_dir / "metrics.csv")

    fig, axs = plt.subplots(2, 1, figsize=(7, 6), sharex=True)

    # =====================================================
    # Panel 1 — Mean disagreement + escalation window
    # =====================================================
    axs[0].plot(df["t"], df["mean_disagreement"], label="Mean disagreement")

    esc = df["escalation_enabled"].astype(bool)
    if esc.any():
        t0 = df.loc[esc, "t"].min()
        t1 = df.loc[esc, "t"].max()
        axs[0].axvspan(
            t0, t1,
            color="red", alpha=0.12,
            label="Escalation active"
        )

    axs[0].set_ylabel("Disagreement")
    axs[0].legend(loc="upper left")

    # =====================================================
    # Panel 2 — AI fraction + triage threshold (merged)
    # =====================================================
    ax = axs[1]
    ax2 = ax.twinx()

    l1 = ax.plot(
        df["t"],
        df["ai_fraction_policy"],
        color="tab:green",
        label="AI reviewer fraction"
    )

    l2 = ax2.plot(
        df["t"],
        df["triage_threshold"],
        color="tab:orange",
        linestyle="--",
        label="Triage threshold"
    )

    ax.set_ylabel("AI fraction")
    ax2.set_ylabel("Triage threshold")
    ax.set_xlabel("Timestep")

    # Combined legend
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc="upper left")

    fig.tight_layout()
    fig.savefig(out_dir / "fig6_disagreement_response.png")
    plt.close(fig)

    print(f"[OK] Figure 6 saved to {out_dir / 'fig6_disagreement_response.png'}")


if __name__ == "__main__":
    main()
