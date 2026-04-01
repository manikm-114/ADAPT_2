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

    df = pd.read_csv(run_dir / "metrics.csv")

    fig, axs = plt.subplots(3, 1, figsize=(8, 7), sharex=True)

    axs[0].plot(df["t"], df["mean_disagreement"], label="Mean disagreement")
    axs[0].set_ylabel("Disagreement")
    axs[0].legend(loc="upper left")
    axs[0].grid(alpha=0.3)

    if "escalations" in df.columns:
        axs[1].plot(df["t"], df["escalations"], label="Escalations")
        axs[1].set_ylabel("Escalations")
        axs[1].legend(loc="upper left")
        axs[1].grid(alpha=0.3)
    else:
        axs[1].plot(df["t"], df["escalation_enabled"].astype(int), label="Escalation enabled")
        axs[1].set_ylabel("Escalation")
        axs[1].legend(loc="upper left")
        axs[1].grid(alpha=0.3)

    ax = axs[2]
    ax2 = ax.twinx()
    l1 = ax.plot(df["t"], df["ai_fraction_policy"], label="AI reviewer fraction")
    l2 = ax2.plot(df["t"], df["triage_threshold"], linestyle="--", label="Triage threshold")
    ax.set_ylabel("AI fraction")
    ax2.set_ylabel("Triage threshold")
    ax.set_xlabel("Timestep")
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc="upper left")
    ax.grid(alpha=0.3)

    plt.tight_layout()
    out_path = out_dir / "fig5_disagreement_spike.png"
    plt.savefig(out_path, dpi=300)
    plt.close()

    print(f"[OK] Saved {out_path}")

if __name__ == "__main__":
    main()
