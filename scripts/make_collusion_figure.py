#!/usr/bin/env python3
"""
Read <run_dir>/collusion_metrics.csv and generate a paper-ready PNG figure.

Outputs:
- <run_dir>/fig8_collusion_capture.png

Also copies into paper figures directory if --paper_fig_dir is provided.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=str, required=True, help="Run directory containing collusion_metrics.csv")
    ap.add_argument("--paper_fig_dir", type=str, default="", help="Optional: path to paper figures dir")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run)
    csv_path = run_dir / "collusion_metrics.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing: {csv_path}")

    df = pd.read_csv(csv_path)

    t = df["t"].to_numpy()
    share = df["within_cluster_share"].to_numpy()
    conc = df["concentration_metric"].to_numpy()
    thr = df["threshold"].to_numpy()
    intervention = df["intervention_on"].to_numpy()

    # Figure layout: 3 stacked panels (easy to interpret)
    plt.figure(figsize=(11, 7.5))

    # Panel 1: concentration metric + threshold
    ax1 = plt.subplot(3, 1, 1)
    ax1.plot(t, conc, linewidth=2, label="Concentration metric")
    ax1.plot(t, thr, linestyle="--", linewidth=2, label="Detection threshold")
    ax1.set_ylabel("Concentration")
    ax1.set_title("Collusion / cluster capture detection and mitigation")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper left")

    # Panel 2: within-cluster share (raw)
    ax2 = plt.subplot(3, 1, 2, sharex=ax1)
    ax2.plot(t, share, linewidth=2, label="Within-cluster co-review share")
    ax2.set_ylabel("Within-cluster share")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper left")

    # Panel 3: intervention ON/OFF
    ax3 = plt.subplot(3, 1, 3, sharex=ax1)
    ax3.step(t, intervention, where="post", linewidth=2, label="Intervention (decentralize/rotate)")
    ax3.set_xlabel("Timestep")
    ax3.set_ylabel("Intervention")
    ax3.set_yticks([0, 1])
    ax3.set_yticklabels(["OFF", "ON"])
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc="upper left")

    plt.tight_layout()

    out_png = run_dir / "fig8_collusion_capture.png"
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[OK] Wrote {out_png}")

    # Optional copy into paper figures directory
    if args.paper_fig_dir:
        paper_dir = Path(args.paper_fig_dir)
        paper_dir.mkdir(parents=True, exist_ok=True)
        dst = paper_dir / out_png.name
        dst.write_bytes(out_png.read_bytes())
        print(f"[OK] Copied to {dst}")


if __name__ == "__main__":
    main()
