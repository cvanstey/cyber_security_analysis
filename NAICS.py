"""
NAIC Cybersecurity Insurance 2025 — Visualisation
==================================================
Reads from NAIC_2025_Cybersecurity_Insurance.xlsx (must be in same folder).
Produces 6 charts saved as PNG files.

Requires: pandas, numpy, matplotlib, openpyxl
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch, Patch
from matplotlib.lines import Line2D

XLS = "NAIC_2025_Cybersecurity_Insurance.xlsx"

# ── Load ──────────────────────────────────────────────────────────────────────
df_mgrowth = pd.read_excel(XLS, sheet_name="market_growth", header=0)
df_mgrowth.columns = ["sheet", "year", "metric", "value", "unit", "notes"]
df_mgrowth = df_mgrowth.dropna(subset=["metric"]).copy()

df_mstructure = pd.read_excel(XLS, sheet_name="market_structure", header=0)
df_mstructure.columns = ["sheet", "category", "metric", "value", "unit", "notes"]
df_mstructure = df_mstructure.dropna(subset=["metric"]).copy()

df_insurers = pd.read_excel(XLS, sheet_name="top_insurers", header=0)
df_insurers.columns = ["rank_2024", "rank_2023", "group_name", "dwp",
                       "loss_ratio_with_dcc", "market_share", "cumulative_market_share"]
df_insurers = df_insurers.dropna(subset=["group_name"]).copy()

df_states = pd.read_excel(XLS, sheet_name="state_dwp", header=0)
df_states.columns = ["sheet", "rank", "state", "dwp", "market_share"]
df_states = df_states.dropna(subset=["state"]).copy()
df_states["state"] = df_states["state"].str.strip()

df_threat = pd.read_excel(XLS, sheet_name="threat_metrics", header=0)
df_threat.columns = ["metric", "value", "unit", "notes"]
df_threat = df_threat.dropna(subset=["metric"]).copy()

# ── Subsets ───────────────────────────────────────────────────────────────────
df_yoy_total    = df_mgrowth[df_mgrowth["metric"] == "yoy_pct_change_total"].copy()
df_yoy_domestic = df_mgrowth[df_mgrowth["metric"] == "yoy_pct_change_domestic"].copy()
df_policy_dwp   = df_mstructure[df_mstructure["sheet"] == "policy_structure_dwp"].copy()
df_policy_pif   = df_mstructure[df_mstructure["sheet"] == "policy_structure_pif"].copy()
df_claims       = df_mstructure[df_mstructure["sheet"] == "claims_closed"].copy()

# ── Style ─────────────────────────────────────────────────────────────────────
RED   = "#C00000"
BLUE  = "#1F3864"
MID   = "#2F5496"
GOLD  = "#E8A838"
GREEN = "#375623"
LGREY = "#DCE6F1"
INK   = "#222222"

SOURCE = "Source: NAIC Report on the Cybersecurity Insurance Market 2025"

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
    "axes.facecolor":     "white",
})

# ── Plot 1: YoY % Change — Diverging Bar ─────────────────────────────────────
years   = df_yoy_total["year"].astype(int).tolist()
yoy_tot = (df_yoy_total["value"] * 100).tolist()
yoy_dom = (df_yoy_domestic["value"] * 100).tolist()

x = np.arange(len(years))
w = 0.35

fig, ax = plt.subplots(figsize=(11, 5))
bars_tot = ax.bar(x - w/2, yoy_tot, w,
                  color=[RED if v < 0 else BLUE for v in yoy_tot],
                  label="Total (incl. alien surplus)", edgecolor="white")
bars_dom = ax.bar(x + w/2, yoy_dom, w,
                  color=[RED if v < 0 else MID for v in yoy_dom],
                  label="Domestic only", edgecolor="white", alpha=0.8)

for bar, val in zip(bars_tot, yoy_tot):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + (1 if val >= 0 else -2.5),
            f"{val:+.1f}%", ha="center",
            va="bottom" if val >= 0 else "top",
            fontsize=8, color=RED if val < 0 else BLUE, fontweight="bold")
for bar, val in zip(bars_dom, yoy_dom):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + (1 if val >= 0 else -2.5),
            f"{val:+.1f}%", ha="center",
            va="bottom" if val >= 0 else "top",
            fontsize=8, color=RED if val < 0 else MID)

ax.axhline(0, color=INK, linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(years)
ax.set_ylabel("Year-over-Year Change (%)")
ax.set_title("Cyber Insurance DWP — Year-over-Year % Change\n(Red = decline, Blue = growth)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:+.0f}%"))
ax.legend(fontsize=9, frameon=False)
fig.text(0.12, -0.02, SOURCE, fontsize=7, color="#888888")
plt.tight_layout()
plt.savefig("naic_plot1_yoy.png", dpi=150, bbox_inches="tight")
plt.show()

# ── Plot 2: Policy Structure — Donut Charts ───────────────────────────────────
types        = ["Primary", "Excess", "Endorsement"]
donut_colors = [BLUE, GOLD, RED]
dwp_vals     = [df_policy_dwp[df_policy_dwp["category"] == t]["value"].values[0] for t in types]
pif_vals     = [df_policy_pif[df_policy_pif["category"] == t]["value"].values[0] for t in types]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
fig.suptitle("Policy Structure: Premium vs Policy Count (2024)",
             fontsize=12, fontweight="bold")

for ax, vals, title in zip([ax1, ax2],
                            [dwp_vals, pif_vals],
                            ["Share of Direct Written Premium",
                             "Share of Policies in Force"]):
    wedges, texts, autotexts = ax.pie(
        vals, labels=types, colors=donut_colors,
        autopct="%1.1f%%", startangle=90,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
        pctdistance=0.75
    )
    for t in texts:
        t.set_fontsize(10)
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color("white")
        at.set_fontweight("bold")
    ax.set_title(title, fontsize=10, pad=15)

fig.text(0.5, -0.02,
         "Key insight: Endorsement = 55% of policies but only 4% of premium  ·  "
         "Excess = 3% of policies but 31% of premium",
         ha="center", fontsize=8, color="#555555")
fig.text(0.12, -0.06, SOURCE, fontsize=7, color="#888888")
plt.tight_layout()
plt.savefig("naic_plot2_policy_structure.png", dpi=150, bbox_inches="tight")
plt.show()

# ── Plot 3: Top 20 Insurers — DWP bar + Loss Ratio scatter ───────────────────
df_ins = df_insurers.sort_values("dwp", ascending=True).reset_index(drop=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))
fig.suptitle("Top 20 Cyber Insurers (2024)", fontsize=13, fontweight="bold")

# Left: horizontal bar for DWP
bar_colors = [RED if i == df_ins["dwp"].idxmax() else BLUE for i in df_ins.index]
bars = ax1.barh(range(len(df_ins)), df_ins["dwp"] / 1e6,
                color=bar_colors, edgecolor="white", height=0.65)
for bar, val in zip(bars, df_ins["dwp"] / 1e6):
    ax1.text(bar.get_width() + 3, bar.get_y() + bar.get_height()/2,
             f"${val:.0f}M", va="center", ha="left", fontsize=8, color=INK)
ax1.set_yticks(range(len(df_ins)))
ax1.set_yticklabels(df_ins["group_name"], fontsize=8.5)
ax1.set_xlabel("Direct Written Premium (USD Millions)")
ax1.set_title("DWP by Insurer Group", fontsize=10)
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:.0f}M"))
ax1.set_xlim(0, df_ins["dwp"].max() / 1e6 * 1.3)

# Right: scatter loss ratio — color coded by profitability
lr_colors = [RED if v > 0.75 else GOLD if v > 0.50 else GREEN
             for v in df_ins["loss_ratio_with_dcc"]]
ax2.scatter(
    df_ins["loss_ratio_with_dcc"] * 100,
    range(len(df_ins)),
    s=df_ins["market_share"] * 5000,
    c=lr_colors, alpha=0.85, edgecolors="white", linewidths=1.5, zorder=3
)
for i, row in df_ins.iterrows():
    ax2.text(row["loss_ratio_with_dcc"] * 100 + 1, i,
             f"{row['loss_ratio_with_dcc']*100:.1f}%",
             va="center", fontsize=7.5,
             color=RED if row["loss_ratio_with_dcc"] > 0.75 else INK)
ax2.axvline(100, color=RED,  linewidth=0.8, linestyle="--")
ax2.axvline(70,  color=GOLD, linewidth=0.8, linestyle=":")
ax2.set_yticks(range(len(df_ins)))
ax2.set_yticklabels(df_ins["group_name"], fontsize=8.5)
ax2.set_xlabel("Loss Ratio with DCC (%)")
ax2.set_title("Loss Ratio  (bubble size = market share)", fontsize=10)
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax2.legend(handles=[
    Patch(color=RED,   label=">75% — High risk"),
    Patch(color=GOLD,  label="50–75% — Moderate"),
    Patch(color=GREEN, label="<50% — Profitable"),
    Line2D([0],[0], color=RED,  linestyle="--", label="100% breakeven"),
    Line2D([0],[0], color=GOLD, linestyle=":",  label="70% market avg"),
], fontsize=8, frameon=False, loc="lower right")

fig.text(0.12, -0.01, SOURCE, fontsize=7, color="#888888")
plt.tight_layout()
plt.savefig("naic_plot3_insurers.png", dpi=150, bbox_inches="tight")
plt.show()

# ── Plot 4: State Market Share — Horizontal Bar ───────────────────────────────
df_st    = df_states.sort_values("market_share", ascending=True).reset_index(drop=True)
top5_min = df_st.nlargest(5, "market_share")["market_share"].min()

fig, ax = plt.subplots(figsize=(11, 9))
bar_colors_st = [RED if v >= top5_min else BLUE for v in df_st["market_share"]]
bars = ax.barh(range(len(df_st)), df_st["market_share"] * 100,
               color=bar_colors_st, edgecolor="white", height=0.65)
for bar, row in zip(bars, df_st.itertuples()):
    w = bar.get_width()
    ax.text(w + 0.1, bar.get_y() + bar.get_height()/2,
            f"{w:.2f}%  (${row.dwp/1e6:.0f}M)",
            va="center", ha="left", fontsize=8,
            color=RED if row.market_share >= top5_min else INK)
ax.set_yticks(range(len(df_st)))
ax.set_yticklabels(df_st["state"], fontsize=9)
ax.set_xlabel("Market Share of Total DWP")
ax.set_title("State Distribution of Cyber Insurance DWP (2024)\n"
             "Top 5 states account for 64.5% of total market")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.set_xlim(0, df_st["market_share"].max() * 100 * 1.35)
ax.legend(handles=[Patch(color=RED,  label="Top 5 states (64.5% combined)"),
                   Patch(color=BLUE, label="Other states")],
          fontsize=9, loc="lower right")
fig.text(0.12, -0.01, SOURCE, fontsize=7, color="#888888")
plt.tight_layout()
plt.savefig("naic_plot4_states.png", dpi=150, bbox_inches="tight")
plt.show()

# ── Plot 5: Claims Paid vs Unpaid — Grouped Bar ───────────────────────────────
claim_types = ["Primary", "Excess", "Endorsement", "Total"]
paid   = [df_claims[(df_claims["category"]==t) &
                    (df_claims["metric"]=="closed_with_payment")]["value"].values[0]
          for t in claim_types]
unpaid = [df_claims[(df_claims["category"]==t) &
                    (df_claims["metric"]=="closed_without_payment")]["value"].values[0]
          for t in claim_types]

x = np.arange(len(claim_types))
w = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
b1 = ax.bar(x - w/2, paid,   w, label="Closed with payment",    color=BLUE,  edgecolor="white")
b2 = ax.bar(x + w/2, unpaid, w, label="Closed without payment", color=LGREY,
            edgecolor=MID, linewidth=0.5)

for bar, val in zip(b1, paid):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 150,
            f"{val:,}", ha="center", va="bottom", fontsize=8.5,
            color=BLUE, fontweight="bold")
for bar, val in zip(b2, unpaid):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 150,
            f"{val:,}", ha="center", va="bottom", fontsize=8.5, color=INK)

ax.set_xticks(x)
ax.set_xticklabels(claim_types)
ax.set_ylabel("Number of Claims")
ax.set_title("Claims Closed With vs Without Payment by Policy Type (2024)\n"
             "Claims without payment outnumber paid claims nearly 3:1 overall")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.legend(fontsize=9)
fig.text(0.12, -0.01,
         SOURCE + "  |  Excludes alien surplus lines", fontsize=7, color="#888888")
plt.tight_layout()
plt.savefig("naic_plot5_claims.png", dpi=150, bbox_inches="tight")
plt.show()

# ── Plot 6: Threat Metrics — Card Dashboard ───────────────────────────────────
key_metrics = [
    {"label": "Ransomware in Breaches",         "value": "44%",    "color": RED},
    {"label": "Human Element in Breaches",      "value": "60%",    "color": RED},
    {"label": "Third-Party Breach Share",       "value": "35.5%",  "color": RED},
    {"label": "BEC Losses 2024",                "value": "$2.77B", "color": RED},
    {"label": "Organizations Refusing Ransom",  "value": "64%",    "color": GREEN},
    {"label": "Avg Ransom Drop 2024",           "value": "−77%",   "color": GREEN},
    {"label": "Cyber Rate Decline Q4 2024",     "value": "−5%",    "color": GREEN},
    {"label": "U.S. DWP Decline 2024",          "value": "−7.1%",  "color": RED},
    {"label": "Claims Rise 2024",               "value": "~40%",   "color": RED},
    {"label": "Top 5 Reinsurers Share",         "value": "62%",    "color": BLUE},
    {"label": "Vishing Surge 2024",             "value": "+442%",  "color": RED},
    {"label": "Stolen Credential Rise H1 2025", "value": "+800%",  "color": RED},
]

cols  = 4
rows  = (len(key_metrics) + cols - 1) // cols   # = 3

# Size the figure to exactly fit the grid
card_w_in = 2.2    # card width  in inches
card_h_in = 1.6    # card height in inches
gap_in    = 0.18   # gap between cards in inches
margin_in = 0.35   # outer margin

fig_w = cols * card_w_in + (cols - 1) * gap_in + 2 * margin_in    # ~10.1"
fig_h = rows * card_h_in + (rows - 1) * gap_in + 2 * margin_in    # ~5.7"

fig = plt.figure(figsize=(fig_w, fig_h))
fig.patch.set_facecolor("white")

# Reserve top margin for title
title_frac = 0.10
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, fig_w)
ax.set_ylim(0, fig_h)
ax.axis("off")

fig.suptitle("NAIC 2025 — Cyber Threat & Market Snapshot",
             fontsize=12, fontweight="bold", y=0.97)

# Place cards bottom-up so row 0 = top row
usable_h = fig_h - margin_in - (margin_in + title_frac * fig_h)

for idx, m in enumerate(key_metrics):
    col_i = idx % cols
    row_i = idx // cols

    x = margin_in + col_i * (card_w_in + gap_in)
    # y starts from top; invert row direction
    y = fig_h - margin_in - title_frac * fig_h - (row_i + 1) * card_h_in - row_i * gap_in

    fancy = FancyBboxPatch(
        (x, y), card_w_in, card_h_in,
        boxstyle="round,pad=0.08",
        facecolor=m["color"], edgecolor="white", linewidth=1.5,
        transform=ax.transData, zorder=2
    )
    ax.add_patch(fancy)

    # Big value text — 62% down from top of card
    ax.text(x + card_w_in / 2, y + card_h_in * 0.58,
            m["value"],
            ha="center", va="center",
            fontsize=20, fontweight="bold", color="white",
            transform=ax.transData)

    # Label text — 22% up from bottom of card
    ax.text(x + card_w_in / 2, y + card_h_in * 0.22,
            m["label"],
            ha="center", va="center",
            fontsize=7.5, color="white", alpha=0.92,
            wrap=True, transform=ax.transData)

fig.text(0.02, 0.01, SOURCE, fontsize=7, color="#888888")
plt.savefig("naic_plot6_threat_dashboard.png", dpi=150, bbox_inches="tight")
plt.show()

# ── Summary ───────────────────────────────────────────────────────────────────
top_insurer  = df_insurers.sort_values("dwp", ascending=False).iloc[0]
top_state    = df_states.sort_values("market_share", ascending=False).iloc[0]
total_dwp    = df_insurers["dwp"].sum()
top5_share   = df_insurers.sort_values("dwp", ascending=False).head(5)["market_share"].sum()

yoy_latest   = df_yoy_total.sort_values("year").iloc[-1]
yoy_dom_latest = df_yoy_domestic.sort_values("year").iloc[-1]

avg_lr       = df_insurers["loss_ratio_with_dcc"].mean()
unprofitable = (df_insurers["loss_ratio_with_dcc"] > 0.75).sum()

print(f"""
╔══════════════════════════════════════════════════════════════╗
║    NAIC Cybersecurity Insurance 2025 — Key Findings          ║
╠══════════════════════════════════════════════════════════════╣
  Market size (top 20 DWP)   : ${total_dwp/1e9:.2f}B
  Latest YoY change (total)  : {yoy_latest['value']*100:+.1f}% ({int(yoy_latest['year'])})
  Latest YoY change (domestic): {yoy_dom_latest['value']*100:+.1f}%

  Top insurer                : {top_insurer['group_name']}
    → DWP                    : ${top_insurer['dwp']/1e6:.0f}M
    → Market share           : {top_insurer['market_share']:.1%}
    → Loss ratio             : {top_insurer['loss_ratio_with_dcc']:.1%}

  Top 5 insurers share       : {top5_share:.1%} of market
  Avg loss ratio (top 20)    : {avg_lr:.1%}
  Insurers loss ratio >75%   : {unprofitable} of {len(df_insurers)}

  Top state by DWP           : {top_state['state']}
    → Market share           : {top_state['market_share']:.1%}
    → DWP                    : ${top_state['dwp']/1e6:.0f}M

  Ransomware in breaches     : 44%
  Human element factor       : 60%
  Vishing surge 2024         : +442%
  Stolen credential rise     : +800% (H1 2025)
╚══════════════════════════════════════════════════════════════╝
""")