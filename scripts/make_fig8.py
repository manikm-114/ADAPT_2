import argparse
import pandas as pd
import matplotlib.pyplot as plt


def main(csv_path, out_path):
    df = pd.read_csv(csv_path)

    t = df["t"]

    fig, axes = plt.subplots(
        3, 1,
        figsize=(10, 9),
        sharex=True
    )

    # ==================================================
    # Panel 1: Post-publication signal (lagged)
    # ==================================================
    axes[0].plot(
        t,
        df["postpub_signal_lag"],
        linewidth=2,
        label="Lagged post-publication signal"
    )

    axes[0].set_ylabel("Signal")
    axes[0].legend(loc="upper left")
    axes[0].set_title("Figure 8: Long-term governance adaptation")

    # ==================================================
    # Panel 2: Institutional state (quality + trust)
    # ==================================================
    axes[1].plot(
        t,
        df["quality_lag"],
        linewidth=2,
        label="Lagged quality"
    )

    axes[1].plot(
        t,
        df["trust_lag"],
        linestyle="--",
        linewidth=2,
        label="Lagged trust"
    )

    axes[1].set_ylabel("Institutional state")
    axes[1].legend(loc="center right")

    # ==================================================
    # Panel 3: Governance policy (dual axis)
    # ==================================================
    axes[2].plot(
        t,
        df["ai_fraction_policy"],
        linewidth=2,
        label="AI reviewer fraction"
    )

    ax2 = axes[2].twinx()
    ax2.plot(
        t,
        df["triage_threshold"],
        linestyle=":",
        linewidth=2,
        label="Triage threshold"
    )

    axes[2].set_ylabel("AI fraction")
    ax2.set_ylabel("Triage threshold")
    axes[2].set_xlabel("Timestep")

    # Combined legend (same trick as Fig 6)
    lines1, labels1 = axes[2].get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    axes[2].legend(
        lines1 + lines2,
        labels1 + labels2,
        loc="upper left"
    )

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()

    print(f"[OK] Figure 8 saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv",
        type=str,
        required=True,
        help="Path to metrics CSV for Figure 8"
    )
    parser.add_argument(
        "--out",
        type=str,
        default="figures/fig8_longterm_governance.png",
        help="Output figure path"
    )

    args = parser.parse_args()
    main(args.csv, args.out)
