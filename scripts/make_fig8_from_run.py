import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True)
    ap.add_argument("--threshold", type=float, default=0.24)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    df = pd.read_csv(run_dir / "metrics.csv")

    out = Path(args.out) if args.out else (run_dir / "fig8_collusion_capture.png")

    fig, axes = plt.subplots(3, 1, figsize=(8, 7), sharex=True)

    axes[0].plot(df["concentration"].values, linewidth=2, label="Concentration")
    axes[0].axhline(args.threshold, linestyle="--", color="orange", label="Threshold")
    axes[0].set_ylabel("Concentration")
    axes[0].legend()

    axes[1].plot(df["within_cluster_share"].values, linewidth=2, label="Within-cluster share")
    axes[1].set_ylabel("Share")
    axes[1].legend()

    axes[2].step(range(len(df)), df["intervention_active"].astype(int).values, where="post", linewidth=2, label="Intervention")
    axes[2].set_ylabel("Intervention")
    axes[2].set_yticks([0, 1])
    axes[2].set_yticklabels(["OFF", "ON"])
    axes[2].set_xlabel("Timestep")
    axes[2].legend()

    plt.tight_layout()
    plt.savefig(out, dpi=300)
    print(f"[OK] Saved {out}")

if __name__ == "__main__":
    main()
