"""
Verizon DBIR 2025 — Analysis & Visualisation
=============================================
Reads from DBIR_2025_Companion_For_Verizon.xlsx (must be in same folder).
Produces 5 matplotlib charts saved as PNG files.

Requires: pandas, numpy, matplotlib
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
from matplotlib.patches import FancyBboxPatch

XLS = "DBIR_2025_Companion_For_Verizon.xlsx"

# ── Load all sheets ───────────────────────────────────────────────────────────
df_pattern  = pd.read_excel(XLS, sheet_name="Pattern_By_Region")
df_action   = pd.read_excel(XLS, sheet_name="Action_By_Region")
df_asset    = pd.read_excel(XLS, sheet_name="Asset_By_Region")
df_action_g = pd.read_excel(XLS, sheet_name="Action_Global_Percent")
df_risk     = pd.read_excel(XLS, sheet_name="Risk_Metrics")

# ── Clean ─────────────────────────────────────────────────────────────────────
# Replace NaN region with "NA/Global" for labelling
for df in [df_pattern, df_action, df_asset]:
    df["region"] = df["region"].fillna("NA/Global")

# Derived: breach rate (breaches / incidents)
for df in [df_pattern, df_action, df_asset]:
    df["breach_rate"] = df["breaches"] / df["incidents"]

# Global totals per pattern/action/asset (sum across regions)
df_pattern_global = (
    df_pattern.groupby("pattern")[["incidents","breaches"]].sum().reset_index()
)
df_action_global = (
    df_action.groupby("action")[["incidents","breaches"]].sum().reset_index()
)
df_asset_global = (
    df_asset.groupby("asset")[["incidents","breaches"]].sum().reset_index()
)

# ── Style ─────────────────────────────────────────────────────────────────────
VZ_RED   = "#CD040B"   # Verizon red
VZ_DARK  = "#1A1A2E"   # dark navy
VZ_MID   = "#4A4A8A"   # mid purple
VZ_LIGHT = "#E8E8F0"   # off-white
GOLD     = "#E8A838"
GREEN    = "#2E7D32"
LGREY    = "#D0D0D0"

REGIONS       = ["APAC", "EMEA", "LAC", "NA/Global"]
REGION_COLORS = [VZ_RED, VZ_MID, GOLD, GREEN]

plt.rcParams.update({
    "font.family":        "DejaVu Sans",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.titlesize":     11,
    "axes.titleweight":   "bold",
    "axes.labelsize":     9,
    "xtick.labelsize":    8,
    "ytick.labelsize":    8,
    "figure.facecolor":   "white",
})

# ── Plot 1: Attack Patterns — Incidents & Breaches by Region ─────────────────
patterns = df_pattern["pattern"].unique()
regions  = ["APAC", "EMEA", "LAC", "NA/Global"]

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

for ax, metric, title in zip(
    axes,
    ["incidents", "breaches"],
    ["Incidents by Region", "Breaches by Region"]
):
    x     = np.arange(len(patterns))
    width = 0.2
    for i, (region, color) in enumerate(zip(regions, REGION_COLORS)):
        sub  = df_pattern[df_pattern["region"] == region].set_index("pattern")
        vals = [sub.loc[p, metric] if p in sub.index else 0 for p in patterns]
        bars = ax.bar(x + i * width, vals, width, label=region, color=color,
                      edgecolor="white", linewidth=0.5)
        for bar, val in zip(bars, vals):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 30,
                        f"{val:,}", ha="center", va="bottom",
                        fontsize=6.5, rotation=90, color="#333333")
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(patterns, rotation=15, ha="right", fontsize=8)
    ax.set_title(title)
    ax.set_ylabel(metric.capitalize())
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.legend(fontsize=8)

fig.suptitle("Verizon DBIR 2025 — Attack Patterns by Region",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("dbir_plot1_patterns_region.png", dpi=150, bbox_inches="tight")
plt.show()

# ── Plot 2: Threat Actions — Global Breach % + Regional Breakdown ─────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Left: global breach percentage horizontal bar
df_ag_sorted = df_action_g.sort_values("breach_percent", ascending=True)
colors_ag    = [VZ_RED if v >= df_action_g["breach_percent"].median()
                else VZ_MID for v in df_ag_sorted["breach_percent"]]
bars = ax1.barh(df_ag_sorted["action"], df_ag_sorted["breach_percent"] * 100,
                color=colors_ag, edgecolor="white", height=0.55)
for bar, val in zip(bars, df_ag_sorted["breach_percent"]):
    ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
             f"{val*100:.0f}%", va="center", ha="left",
             fontsize=9, fontweight="bold",
             color=VZ_RED if val >= df_action_g["breach_percent"].median() else VZ_MID)
ax1.set_xlabel("% of Breaches Involving This Action")
ax1.set_title("Threat Actions — Global Breach Involvement")
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
ax1.set_xlim(0, 70)
ax1.legend(handles=[Patch(color=VZ_RED, label="Above median"),
                    Patch(color=VZ_MID, label="Below median")],
           fontsize=8, loc="lower right")

# Right: stacked bar of breaches by action & region
actions = df_action["action"].unique()
x       = np.arange(len(actions))
bottom  = np.zeros(len(actions))
for region, color in zip(regions, REGION_COLORS):
    sub  = df_action[df_action["region"] == region].set_index("action")
    vals = np.array([sub.loc[a, "breaches"] if a in sub.index else 0
                     for a in actions], dtype=float)
    ax2.bar(x, vals, bottom=bottom, label=region, color=color,
            edgecolor="white", linewidth=0.5)
    bottom += vals
ax2.set_xticks(x)
ax2.set_xticklabels(actions, rotation=15, ha="right", fontsize=8)
ax2.set_ylabel("Total Breaches")
ax2.set_title("Breaches by Action Type & Region (Stacked)")
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
ax2.legend(fontsize=8)

fig.suptitle("Verizon DBIR 2025 — Threat Action Analysis",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("dbir_plot2_actions.png", dpi=150, bbox_inches="tight")
plt.show()

# ── Plot 3: Breach Rate Heatmap (action × region) ────────────────────────────
pivot = df_action.pivot_table(
    index="action", columns="region", values="breach_rate", aggfunc="mean"
)
# reorder columns
cols_present = [c for c in regions if c in pivot.columns]
pivot        = pivot[cols_present]

fig, ax = plt.subplots(figsize=(10, 5))
im = ax.imshow(pivot.values, cmap="RdYlGn_r", aspect="auto",
               vmin=0.4, vmax=0.7)
ax.set_xticks(range(len(cols_present)))
ax.set_xticklabels(cols_present, fontsize=9)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index, fontsize=9)
for i in range(len(pivot.index)):
    for j in range(len(cols_present)):
        val = pivot.values[i, j]
        ax.text(j, i, f"{val:.1%}", ha="center", va="center",
                fontsize=10, fontweight="bold",
                color="white" if val > 0.58 else "#222222")
plt.colorbar(im, ax=ax, label="Breach Rate (breaches / incidents)",
             format=mticker.FuncFormatter(lambda x, _: f"{x:.0%}"))
ax.set_title("Breach Rate by Action Type & Region\n(darker = higher conversion from incident to breach)",
             fontweight="bold")
plt.tight_layout()
plt.savefig("dbir_plot3_breach_rate_heatmap.png", dpi=150, bbox_inches="tight")
plt.show()

# ── Plot 4: Asset Targeting — Incidents & Breach Rate ────────────────────────
df_asset_g = df_asset_global.copy()
df_asset_g["breach_rate"] = df_asset_g["breaches"] / df_asset_g["incidents"]
df_asset_g = df_asset_g.sort_values("incidents", ascending=False)

fig, ax1 = plt.subplots(figsize=(10, 5))
ax2_twin = ax1.twinx()

x     = np.arange(len(df_asset_g))
bars  = ax1.bar(x, df_asset_g["incidents"], color=VZ_MID,
                width=0.5, label="Incidents", edgecolor="white")
ax2_twin.plot(x, df_asset_g["breach_rate"] * 100, "o-",
              color=VZ_RED, linewidth=2, markersize=7, label="Breach Rate %")

for bar, val in zip(bars, df_asset_g["incidents"]):
    ax1.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 50, f"{val:,}",
             ha="center", va="bottom", fontsize=8.5, color=VZ_MID, fontweight="bold")
for xi, br in zip(x, df_asset_g["breach_rate"]):
    ax2_twin.text(xi, br * 100 + 1.5, f"{br:.0%}",
                  ha="center", va="bottom", fontsize=8, color=VZ_RED)

ax1.set_xticks(x)
ax1.set_xticklabels(df_asset_g["asset"], fontsize=9)
ax1.set_ylabel("Total Incidents", color=VZ_MID)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
ax2_twin.set_ylabel("Breach Rate (%)", color=VZ_RED)
ax2_twin.set_ylim(0, 100)
ax2_twin.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2_twin.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc="upper right")
ax1.set_title("Asset Targeting — Global Incidents & Breach Conversion Rate",
              fontweight="bold")
plt.tight_layout()
plt.savefig("dbir_plot4_assets.png", dpi=150, bbox_inches="tight")
plt.show()


# ── Plot 5: Key Risk Metrics Dashboard ───────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
ax.axis("off")

# Separate pct metrics from USD
pct_metrics = df_risk[df_risk["unit"] == "percent"].copy()
usd_metrics = df_risk[df_risk["unit"] == "USD"].copy()

pct_metrics["display"] = pct_metrics["value"].apply(lambda v: f"{v:.0%}")
usd_metrics["display"] = usd_metrics["value"].apply(lambda v: f"${v:,.0f}")
all_metrics = pd.concat([pct_metrics, usd_metrics], ignore_index=True)

n      = len(all_metrics)
cols   = 3
rows   = (n + cols - 1) // cols
card_w = 0.28
card_h = 0.35
gap_x  = 0.06
gap_y  = 0.12

card_colors = [VZ_RED, VZ_MID, VZ_DARK, VZ_RED, GOLD, VZ_MID]

for idx, (_, row) in enumerate(all_metrics.iterrows()):
    col_i  = idx % cols
    row_i  = idx // cols
    x_pos  = 0.05 + col_i * (card_w + gap_x)
    y_pos  = 0.75 - row_i * (card_h + gap_y)
    color  = card_colors[idx % len(card_colors)]

    fancy = FancyBboxPatch(
        (x_pos, y_pos), card_w, card_h,
        boxstyle="round,pad=0.02",
        facecolor=color, edgecolor="white", linewidth=1.5,
        transform=ax.transAxes, zorder=2
    )
    ax.add_patch(fancy)

    ax.text(x_pos + card_w / 2, y_pos + card_h * 0.62,
            row["display"],
            ha="center", va="center",
            fontsize=26, fontweight="bold", color="white",
            transform=ax.transAxes, zorder=3)
    ax.text(x_pos + card_w / 2, y_pos + card_h * 0.22,
            row["metric"],
            ha="center", va="center",
            fontsize=7.5, color="white", alpha=0.9,
            transform=ax.transAxes, zorder=3,
            wrap=True)

ax.set_title("Verizon DBIR 2025 — Key Risk Metrics at a Glance",
             fontsize=13, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig("dbir_plot5_risk_metrics.png", dpi=150, bbox_inches="tight")
plt.show()

# ── Summary ───────────────────────────────────────────────────────────────────
top_pattern = df_pattern_global.sort_values("breaches", ascending=False).iloc[0]
top_action  = df_action_global.sort_values("breaches", ascending=False).iloc[0]
top_action_g= df_action_g.sort_values("breach_percent", ascending=False).iloc[0]
top_asset   = df_asset_global.sort_values("incidents", ascending=False).iloc[0]
ransom_row  = df_risk[df_risk["metric"].str.contains("ansom", case=False)].iloc[0]
human_row   = df_risk[df_risk["metric"].str.contains("uman", case=False)].iloc[0]

print(f"""
╔══════════════════════════════════════════════════════════╗
║    Verizon DBIR 2025 — Key Findings Summary              ║
╠══════════════════════════════════════════════════════════╣
  Top breach pattern    : {top_pattern['pattern']}
    → Total breaches    : {top_pattern['breaches']:,}
  Top action (breaches) : {top_action['action']}
    → Total breaches    : {top_action['breaches']:,}
  Most common action    : {top_action_g['action']}
    → % of all breaches : {top_action_g['breach_percent']:.0%}
  Most targeted asset   : {top_asset['asset']}
    → Total incidents   : {top_asset['incidents']:,}
  Ransomware involvement: {ransom_row['value']:.0%} of breaches
  Human element factor  : {human_row['value']:.0%} of breaches
╚══════════════════════════════════════════════════════════╝
""")