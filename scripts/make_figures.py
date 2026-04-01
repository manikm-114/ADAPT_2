from pathlib import Path
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# =========================
# Global plotting defaults
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


# =========================
# Utilities
# =========================
def read_metrics(run_dir: Path) -> pd.DataFrame:
    p = run_dir / "metrics.csv"
    if not p.exists():
        raise FileNotFoundError(f"metrics.csv not found in: {run_dir}")
    return pd.read_csv(p)


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


# =========================
# Figure 1: ADAPT architecture
# =========================
def fig_architecture(outdir: Path):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("off")

    boxes = {
        "Submission": (0.02, 0.55, 0.18, 0.3, "Submission\nStream"),
        "Triage": (0.26, 0.55, 0.22, 0.3, "Triage\n(Policy-controlled)"),
        "Review": (0.54, 0.55, 0.24, 0.3, "Review Pool\n(Human + AI)"),
        "Meta": (0.82, 0.55, 0.26, 0.3, "Meta-review &\nAggregation"),
        "Decision": (1.12, 0.55, 0.26, 0.3, "Final Decision\n(Human authority preserved)"),
        "Policy": (0.45, 0.05, 0.45, 0.3, "Policy / Governance\n(ADAPT controller)"),
    }

    for x, y, w, h, text in boxes.values():
        ax.add_patch(patches.Rectangle((x, y), w, h, fill=False, linewidth=2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center")

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", lw=1.8))

    arrow(0.20, 0.70, 0.26, 0.70)
    arrow(0.48, 0.70, 0.54, 0.70)
    arrow(0.78, 0.70, 0.82, 0.70)
    arrow(1.08, 0.70, 1.12, 0.70)

    arrow(0.37, 0.55, 0.55, 0.35)
    arrow(0.66, 0.55, 0.66, 0.35)
    arrow(0.95, 0.55, 0.75, 0.35)

    ax.text(0.66, 0.42, "System signals:\nbacklog, disagreement",
            ha="center", va="center", fontsize=9)

    ax.set_xlim(0, 1.42)
    ax.set_ylim(0, 1)

    fig.tight_layout()
    fig.savefig(outdir / "fig1_adapt_architecture.png")
    plt.close(fig)


# =========================
# Figure 2: Baseline stability
# =========================
def fig_baseline(df: pd.DataFrame, outdir: Path):
    fig, axs = plt.subplots(3, 1, figsize=(7, 7), sharex=True)

    T = df["t"].max()

    axs[0].plot(df["t"], df["backlog"])
    axs[0].axvspan(0, T, color="gray", alpha=0.08,
                   label="Stable regime (no ADAPT intervention)")
    axs[0].set_ylabel("Backlog")
    axs[0].legend()

    axs[1].plot(df["t"], df["ai_fraction_policy"])
    axs[1].set_ylabel("AI fraction")

    axs[2].plot(df["t"], df["triage_threshold"])
    axs[2].set_ylabel("Triage threshold")
    axs[2].set_xlabel("Timestep")

    fig.tight_layout()
    fig.savefig(outdir / "fig2_baseline_stability.png")
    plt.close(fig)


# =========================
# Figure 3: Submission surge
# =========================
def fig_submission_surge(df: pd.DataFrame, outdir: Path):
    fig, axs = plt.subplots(3, 1, figsize=(7, 7), sharex=True)

    axs[0].plot(df["t"], df["submitted"], label="Submitted")
    axs[0].plot(df["t"], df["backlog"], label="Backlog")
    axs[0].set_ylabel("Manuscripts per timestep")
    axs[0].legend()

    axs[1].plot(df["t"], df["ai_fraction_policy"])
    axs[1].set_ylabel("AI fraction")

    axs[2].plot(df["t"], df["triage_threshold"])
    axs[2].set_ylabel("Triage threshold")
    axs[2].set_xlabel("Timestep")

    fig.tight_layout()
    fig.savefig(outdir / "fig3_submission_surge.png")
    plt.close(fig)


# =========================
# Figure 4: Quality drift
# =========================
def fig_quality_drift(df: pd.DataFrame, outdir: Path):
    fig, axs = plt.subplots(3, 1, figsize=(7, 7), sharex=True)

    initial_triage = df["triage_threshold"].iloc[0]

    axs[0].plot(df["t"], df["accept"] / df["decided"].replace(0, np.nan))
    axs[0].plot(df["t"], df["reject"] / df["decided"].replace(0, np.nan))
    axs[0].set_ylabel("Decision rate")

    axs[1].plot(df["t"], df["triage_threshold"])
    axs[1].axhline(initial_triage, linestyle="--",
                    color="gray", alpha=0.6, label="Baseline threshold")
    axs[1].set_ylabel("Triage threshold")
    axs[1].legend()

    axs[2].plot(df["t"], df["backlog"])
    axs[2].set_ylabel("Backlog")
    axs[2].set_xlabel("Timestep")

    fig.tight_layout()
    fig.savefig(outdir / "fig4_quality_drift.png")
    plt.close(fig)


# =========================
# Figure 5a: Disagreement & escalation
# =========================
def fig_disagreement_escalation(df: pd.DataFrame, outdir: Path):
    fig, axs = plt.subplots(3, 1, figsize=(7, 7), sharex=True)

    axs[0].plot(df["t"], df["mean_disagreement"])
    axs[0].set_ylabel("Mean disagreement")

    axs[1].plot(df["t"], df["escalations"])
    axs[1].set_ylabel("Escalations")

    axs[2].step(df["t"], df["escalation_enabled"].astype(int), where="post")
    axs[2].set_yticks([0, 1])
    axs[2].set_yticklabels(["OFF", "ON"])
    axs[2].set_ylabel("Escalation")
    axs[2].set_xlabel("Timestep")

    fig.tight_layout()
    fig.savefig(outdir / "fig5a_disagreement_escalation.png")
    plt.close(fig)


# =========================
# Figure 5b: Governance response
# =========================
def fig_governance_response(df: pd.DataFrame, outdir: Path):
    fig, axs = plt.subplots(3, 1, figsize=(7, 7), sharex=True)

    axs[0].plot(df["t"], df["ai_fraction_policy"])
    axs[0].set_ylabel("AI fraction")

    axs[1].plot(df["t"], df["triage_threshold"])
    axs[1].set_ylabel("Triage threshold")

    axs[2].plot(df["t"], df["backlog"])
    axs[2].set_ylabel("Backlog")
    axs[2].set_xlabel("Timestep")

    fig.tight_layout()
    fig.savefig(outdir / "fig5b_governance_response.png")
    plt.close(fig)


# =========================
# Main
# =========================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--surge", required=True)
    ap.add_argument("--drift", required=True)
    ap.add_argument("--spike", required=True)
    args = ap.parse_args()

    outdir = Path("paper_assets/figures")
    ensure_dir(outdir)

    df_base = read_metrics(Path(args.baseline))
    df_surge = read_metrics(Path(args.surge))
    df_drift = read_metrics(Path(args.drift))
    df_spike = read_metrics(Path(args.spike))

    fig_architecture(outdir)
    fig_baseline(df_base, outdir)
    fig_submission_surge(df_surge, outdir)
    fig_quality_drift(df_drift, outdir)
    fig_disagreement_escalation(df_spike, outdir)
    fig_governance_response(df_spike, outdir)

    print(f"[OK] Figures saved to: {outdir}")


if __name__ == "__main__":
    main()
