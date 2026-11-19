"""
Generates high-resolution publication-grade Pareto Chart for Stage 8 TQM Artefacts.
Based on empirical defects recorded in docs/defect-log.md.
"""

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "pareto_chart.png"


def generate_pareto():
    # 1. Defect Categories and empirical frequencies from docs/defect-log.md
    categories = [
        "Interface &\nContract Mismatch",
        "Input Validation &\nConstraint Handling",
        "Dependency &\nVersion Conflict",
        "Concurrency &\nDatabase Locking",
        "Environment &\nHarness Boundary",
    ]
    counts = np.array([3, 2, 1, 1, 1])
    total_defects = counts.sum()

    # Calculate cumulative percentages
    cum_counts = np.cumsum(counts)
    cum_percentages = (cum_counts / total_defects) * 100

    # 2. Styling configuration
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#cbd5e1"
    plt.rcParams["axes.linewidth"] = 1.2

    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=300)

    # 3. Bar chart (Primary Y-Axis: Defect Frequency)
    bar_colors = ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe"]
    bars = ax1.bar(
        categories,
        counts,
        color=bar_colors,
        width=0.55,
        edgecolor="#1e40af",
        linewidth=1.2,
        zorder=3,
    )
    ax1.set_ylabel("Defect Frequency (Count)", color="#1e293b", fontsize=12, fontweight="bold", labelpad=10)
    ax1.set_ylim(0, 4)
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax1.tick_params(axis="y", labelsize=10, colors="#1e293b")
    ax1.tick_params(axis="x", labelsize=9.5, colors="#1e293b")
    ax1.grid(axis="y", linestyle="--", alpha=0.5, zorder=0)

    # Add count labels above bars
    for bar in bars:
        yval = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + 0.1,
            f"{int(yval)} ({yval/total_defects*100:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color="#1e3a8a",
        )

    # 4. Cumulative Percentage Line (Secondary Y-Axis)
    ax2 = ax1.twinx()
    ax2.plot(
        categories,
        cum_percentages,
        color="#dc2626",
        marker="o",
        linewidth=2.4,
        markersize=7,
        zorder=4,
        label="Cumulative Percentage",
    )
    ax2.set_ylabel("Cumulative Percentage (%)", color="#991b1b", fontsize=12, fontweight="bold", labelpad=10)
    ax2.set_ylim(0, 110)
    ax2.yaxis.set_major_formatter(ticker.PercentFormatter())
    ax2.tick_params(axis="y", labelsize=10, colors="#991b1b")

    # Add 80% Pareto Reference Cutoff Line
    ax2.axhline(80, color="#f59e0b", linestyle=":", linewidth=2, zorder=2, label="80% Cutoff (Vital Few)")
    ax2.text(
        len(categories) - 0.6,
        82,
        "80% Cutoff",
        color="#b45309",
        fontweight="bold",
        fontsize=9,
        ha="right",
    )

    # Data callout for top 2 categories
    ax2.annotate(
        f"Top 2 Categories = {cum_percentages[1]:.1f}%\n(Vital Few)",
        xy=(1, cum_percentages[1]),
        xytext=(1.4, 48),
        arrowprops=dict(facecolor="#dc2626", shrink=0.08, width=1.5, headwidth=6),
        fontsize=9.5,
        fontweight="bold",
        color="#991b1b",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#fee2e2", edgecolor="#ef4444", alpha=0.9),
    )

    # Title & Subtitle
    plt.title(
        "Pareto Analysis of Software Defects (BBAT104 Baseline No. 9)",
        fontsize=14,
        fontweight="bold",
        pad=18,
        color="#0f172a",
    )

    fig.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300)
    print(f"Pareto chart successfully generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_pareto()
