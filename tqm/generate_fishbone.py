"""
Generates high-resolution publication-grade Ishikawa (Fishbone) Diagram for Stage 8 TQM.
Analyzes root causes of Duplicate Entries across the 6Ms.
"""

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = OUTPUT_DIR / "ishikawa_fishbone.png"


def generate_fishbone():
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"

    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    ax.set_xlim(-1, 13)
    ax.set_ylim(-1, 9)
    ax.axis("off")

    # Central Spine (Horizontal line from left to right)
    spine_x = [0.5, 9.8]
    spine_y = [4.0, 4.0]
    ax.plot(spine_x, spine_y, color="#1e3a8a", linewidth=4.5, zorder=2)

    # Fish Head (Problem Statement Box on the right)
    head_box = patches.FancyBboxPatch(
        (9.8, 2.7),
        2.8,
        2.6,
        boxstyle="round,pad=0.2",
        facecolor="#ef4444",
        edgecolor="#b91c1c",
        linewidth=2.5,
        zorder=3,
    )
    ax.add_patch(head_box)
    ax.text(
        11.2,
        4.0,
        "EFFECT:\nDuplicate Entries\nin Online\nAssessments",
        ha="center",
        va="center",
        color="#ffffff",
        fontsize=11.5,
        fontweight="bold",
        linespacing=1.3,
    )

    # 6 Branches (3 Top, 3 Bottom)
    # Format: (Branch Label, Branch Start (x,y), Rib End (x,y), Sub-causes [(text, sub_x, sub_y)])
    branches = [
        # TOP 3 BRANCHES
        {
            "name": "MAN (People)",
            "start": (2.2, 4.0),
            "end": (1.0, 7.5),
            "subcauses": [
                ("Double-clicking Submit", 1.4, 6.7),
                ("Multiple Browser Tabs", 1.8, 5.8),
                ("Accidental Copy-Paste", 2.1, 4.9),
            ],
            "color": "#2563eb",
            "y_offset": 0.4,
        },
        {
            "name": "METHOD (Process)",
            "start": (5.2, 4.0),
            "end": (4.0, 7.5),
            "subcauses": [
                ("Missing Search-Before-Add", 4.4, 6.7),
                ("Lack of Poka-Yoke Dialogs", 4.8, 5.8),
                ("Non-Idempotent APIs", 5.1, 4.9),
            ],
            "color": "#0284c7",
            "y_offset": 0.4,
        },
        {
            "name": "MACHINE (Technology)",
            "start": (8.2, 4.0),
            "end": (7.0, 7.5),
            "subcauses": [
                ("Network Latency Delays", 7.4, 6.7),
                ("Unthrottled Endpoints", 7.8, 5.8),
                ("No Atomic DB Isolation", 8.1, 4.9),
            ],
            "color": "#059669",
            "y_offset": 0.4,
        },
        # BOTTOM 3 BRANCHES
        {
            "name": "MATERIAL (Data)",
            "start": (2.2, 4.0),
            "end": (1.0, 0.5),
            "subcauses": [
                ("Untrimmed Whitespaces", 1.4, 1.3),
                ("Case Variations (A vs a)", 1.8, 2.2),
                ("Blank / Empty Payloads", 2.1, 3.1),
            ],
            "color": "#d97706",
            "y_offset": -0.4,
        },
        {
            "name": "MEASUREMENT (Testing)",
            "start": (5.2, 4.0),
            "end": (4.0, 0.5),
            "subcauses": [
                ("Missing Uniqueness Tests", 4.4, 1.3),
                ("Incomplete Schema Check", 4.8, 2.2),
                ("Single-Threaded Mocks", 5.1, 3.1),
            ],
            "color": "#7c3aed",
            "y_offset": -0.4,
        },
        {
            "name": "MILIEU (Environment)",
            "start": (8.2, 4.0),
            "end": (7.0, 0.5),
            "subcauses": [
                ("Simultaneous Exam Starts", 7.4, 1.3),
                ("Campus Wi-Fi Dropouts", 7.8, 2.2),
                ("Cross-Browser Form Quirks", 8.1, 3.1),
            ],
            "color": "#db2777",
            "y_offset": -0.4,
        },
    ]

    for b in branches:
        # Draw main diagonal branch line
        bx = [b["start"][0], b["end"][0]]
        by = [b["start"][1], b["end"][1]]
        ax.plot(bx, by, color=b["color"], linewidth=3, zorder=2)

        # Draw Branch Category Header Box
        header_patch = patches.FancyBboxPatch(
            (b["end"][0] - 0.9, b["end"][1] - 0.25 + b["y_offset"] * 0.4),
            1.8,
            0.55,
            boxstyle="round,pad=0.15",
            facecolor=b["color"],
            edgecolor="#0f172a",
            linewidth=1.2,
            zorder=4,
        )
        ax.add_patch(header_patch)
        ax.text(
            b["end"][0],
            b["end"][1] + b["y_offset"] * 0.4 + 0.02,
            b["name"],
            ha="center",
            va="center",
            color="#ffffff",
            fontsize=9.5,
            fontweight="bold",
        )

        # Draw horizontal sub-cause ribs and text
        for text, sx, sy in b["subcauses"]:
            rib_len = 1.3
            ax.plot([sx - rib_len, sx], [sy, sy], color=b["color"], linewidth=1.5, linestyle="--", zorder=2)
            ax.text(
                sx - rib_len - 0.05,
                sy,
                text,
                ha="right",
                va="center",
                fontsize=8.5,
                color="#1e293b",
                fontweight="bold",
            )

    # Title Banner
    plt.title(
        "Ishikawa (Fishbone) Cause-and-Effect Diagram: Root Causes of Duplicate Entries",
        fontsize=14,
        fontweight="bold",
        pad=15,
        color="#0f172a",
    )

    fig.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=300)
    print(f"Ishikawa fishbone diagram successfully generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_fishbone()
