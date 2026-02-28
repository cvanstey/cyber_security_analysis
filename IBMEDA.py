"""
IBM Cost of a Data Breach 2025 — Analysis & Visualisation
==========================================================
Reads from IBM_Cost_Data_Breach_2025.xlsx (must be in same folder).
Produces 7 matplotlib charts saved as PNG files.

Requires: pandas, numpy, matplotlib, scikit-learn, openpyxl
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from sklearn.preprocessing import MinMaxScaler

XLS = "IBM_Cost_Data_Breach_2025.xlsx"

# ── Load ──────────────────────────────────────────────────────────────────────
df_country = pd.read_excel(XLS, sheet_name="by_country", header=1)
df_country.columns = ["rank","country","cost_2025","cost_2024","yoy_pct"]
df_country = df_country.dropna(subset=["country"]).copy()
df_country_sorted = df_country.sort_values("cost_2025", ascending=False).reset_index(drop=True)

df_industry = pd.read_excel(XLS, sheet_name="by_industry", header=1)
df_industry.columns = ["rank","industry","cost_2025","cost_2024","yoy_pct"]
df_industry = df_industry.dropna(subset=["industry"]).copy()

df_vector = pd.read_excel(XLS, sheet_name="attack_vectors", header=1)
df_vector.columns = ["rank","attack_vector","pct_of_breaches","avg_cost_m","notes"]
df_vector = df_vector.dropna(subset=["attack_vector"]).copy()
df_vector["attack_vector"] = df_vector["attack_vector"].str.strip()
# ── Clean string-formatted numbers ────────────────────────────────────────────
df_vector["pct_of_breaches"] = (
    df_vector["pct_of_breaches"]
    .astype(str).str.replace("%","",regex=False).str.strip()
    .astype(float)
)
df_vector["avg_cost_m"] = (
    df_vector["avg_cost_m"]
    .astype(str).str.replace("$","",regex=False).str.replace("M","",regex=False).str.strip()
    .astype(float)
)

# ── Verify all 9 rows loaded cleanly ─────────────────────────────────────────
print(df_vector[["attack_vector","pct_of_breaches","avg_cost_m"]])

df_factors = pd.read_excel(XLS, sheet_name="Cost_Factors", header=1)
df_factors.columns = ["rank","factor","cost_diff_usd","direction"]
df_factors = df_factors.dropna(subset=["factor"]).copy()

_ai = pd.read_excel(XLS, sheet_name="Security_AI", header=None)
df_ai_cost = _ai.iloc[8:13].copy()
df_ai_cost.columns = ["rank","level","avg_cost","vs_global","savings"]
df_ai_cost["avg_cost"] = pd.to_numeric(df_ai_cost["avg_cost"], errors="coerce")
df_ai_cost = df_ai_cost.dropna(subset=["avg_cost"]).reset_index(drop=True)

df_ai_time = _ai.iloc[15:19].copy()
df_ai_time.columns = ["rank","level","mtti","mttc","total"]
df_ai_time[["mtti","mttc","total"]] = df_ai_time[["mtti","mttc","total"]].apply(pd.to_numeric, errors="coerce")
df_ai_time = df_ai_time.reset_index(drop=True)

# ── Derived metrics ───────────────────────────────────────────────────────────
scaler = MinMaxScaler()
df_vector[["cost_norm","freq_norm"]] = scaler.fit_transform(df_vector[["avg_cost_m","pct_of_breaches"]])
df_vector["risk_score"] = df_vector["avg_cost_m"] * df_vector["pct_of_breaches"]
med_cost = df_vector["avg_cost_m"].median()
med_freq = df_vector["pct_of_breaches"].median()
df_vector["risk_cat"] = np.select(
    [(df_vector["avg_cost_m"]>=med_cost)&(df_vector["pct_of_breaches"]>=med_freq),
     (df_vector["avg_cost_m"]>=med_cost),
     (df_vector["pct_of_breaches"]>=med_freq)],
    ["Critical","Catastrophic","Chronic"], default="Low"
)

df_reducers   = df_factors[df_factors["cost_diff_usd"] < 0].sort_values("cost_diff_usd")
df_amplifiers = df_factors[df_factors["cost_diff_usd"] > 0].sort_values("cost_diff_usd")

# Strip whitespace and convert to lowercase
df_ai_cost["level_clean"] = df_ai_cost["level"].str.strip().str.lower()
print(df_ai_cost["level_clean"].tolist())
ai_none      = df_ai_cost.loc[df_ai_cost["level_clean"]=="no use", "avg_cost"].values[0]
ai_extensive = df_ai_cost.loc[df_ai_cost["level_clean"]=="extensive use", "avg_cost"].values[0]
ai_savings   = ai_none - ai_extensive
roi_pct      = ai_savings / ai_none * 100
top3_share   = df_country_sorted.head(3)["cost_2025"].sum() / df_country["cost_2025"].sum()

# ── Style ─────────────────────────────────────────────────────────────────────
IBM_BLUE = "#1F3864"; IBM_MID = "#2F5496"; RED = "#C00000"
GREEN = "#375623";    GOLD = "#E8A838";    LGREY = "#DCE6F1"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "axes.spines.top": False,
    "axes.spines.right": False,   "axes.titlesize": 11,
    "axes.titleweight": "bold",   "axes.labelsize": 9,
    "xtick.labelsize": 8,         "ytick.labelsize": 8,
    "figure.facecolor": "white",
})

# ── Plot 1: Country costs ─────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 8))
colors = [RED if v > 0 else GREEN for v in df_country_sorted["yoy_pct"]]
bars = ax.barh(range(len(df_country_sorted)), df_country_sorted["cost_2025"],
               color=colors, edgecolor="white", height=0.65)
ax.set_yticks(range(len(df_country_sorted)))
ax.set_yticklabels(df_country_sorted["country"], fontsize=9)
for bar, row in zip(bars, df_country_sorted.itertuples()):
    w = bar.get_width()
    sign = "▲" if row.yoy_pct > 0 else "▼"
    ax.text(w - 0.08, bar.get_y() + bar.get_height()/2,
            f"${w:.2f}M", va="center", ha="right", fontsize=8.5, color="white", fontweight="bold")
    ax.text(w + 0.12, bar.get_y() + bar.get_height()/2,
            f"{sign} {abs(row.yoy_pct)*100:.1f}%", va="center", ha="left",
            fontsize=8, color=RED if row.yoy_pct > 0 else GREEN)
ax.invert_yaxis()
ax.set_xlabel("Average Breach Cost (USD Millions)")
ax.set_title("Average Data Breach Cost by Country — 2025\n(Green = decreased vs 2024, Red = increased)")
ax.set_xlim(0, 14)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x:.0f}M"))
ax.legend(handles=[Patch(color=RED,label="Increased vs 2024"), Patch(color=GREEN,label="Decreased vs 2024")],
          loc="lower right", fontsize=9)
plt.tight_layout()
plt.savefig("plot1_country_costs.png", dpi=150, bbox_inches="tight")
plt.show()

# ── Plot 2: Industry 2024 vs 2025 ────────────────────────────────────────────
df_ind = df_industry.sort_values("cost_2025", ascending=True).reset_index(drop=True)
y = np.arange(len(df_ind)); h = 0.38
fig, ax = plt.subplots(figsize=(12, 9))
b25 = ax.barh(y+h/2, df_ind["cost_2025"], h, color=IBM_BLUE, label="2025")
b24 = ax.barh(y-h/2, df_ind["cost_2024"], h, color=LGREY, label="2024", edgecolor=IBM_MID, linewidth=0.5)
for bar, val in zip(b25, df_ind["cost_2025"]):
    ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2,
            f"${val:.2f}M", va="center", ha="left", fontsize=8, color=IBM_BLUE, fontweight="bold")
for bar, val in zip(b24, df_ind["cost_2024"]):
    ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2,
            f"${val:.2f}M", va="center", ha="left", fontsize=7.5, color="#666666")
ax.set_yticks(y); ax.set_yticklabels(df_ind["industry"])
ax.set_xlabel("Average Breach Cost (USD Millions)")
ax.set_title("Average Data Breach Cost by Industry — 2024 vs 2025")
ax.set_xlim(0, 13)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x:.0f}M"))
ax.legend(loc="lower right", fontsize=9)
plt.tight_layout(); plt.savefig("plot2_industry_costs.png", dpi=150, bbox_inches="tight"); plt.show()

# ── Plot 3: Attack vector bubble ──────────────────────────────────────────────
cat_colors = {"Critical":RED,"Catastrophic":GOLD,"Chronic":"#F7D060","Low":"#5BC0DE"}
fig, ax = plt.subplots(figsize=(12, 7))
for _, row in df_vector.iterrows():
    ax.scatter(row["pct_of_breaches"]*100, row["avg_cost_m"], s=row["risk_score"]*2000,
               color=cat_colors[row["risk_cat"]], alpha=0.85, edgecolors="white", linewidths=1.5, zorder=3)
    ax.annotate(row["attack_vector"], (row["pct_of_breaches"]*100, row["avg_cost_m"]),
                xytext=(7, 5), textcoords="offset points", fontsize=8.5, color="#222222",
                arrowprops=dict(arrowstyle="-", color="#AAAAAA", lw=0.5))
ax.axhline(med_cost, color="#CCCCCC", linestyle="--", linewidth=0.8)
ax.axvline(med_freq*100, color="#CCCCCC", linestyle="--", linewidth=0.8)
legend_els = [Line2D([0],[0],marker='o',color='w',markerfacecolor=c,markersize=9,label=k)
              for k,c in cat_colors.items()]
ax.legend(handles=legend_els, title="Risk Category", loc="lower right", fontsize=9)
ax.set_xlabel("Frequency — % of All Breaches")
ax.set_ylabel("Average Breach Cost (USD Millions)")
ax.set_title("Attack Vectors: Frequency vs Cost\n(bubble size = risk score = cost × frequency)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:.0f}%"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x:.2f}M"))
ax.set_xlim(4, 20); ax.set_ylim(3.3, 5.2)
plt.tight_layout(); plt.savefig("plot3_attack_vectors.png", dpi=150, bbox_inches="tight"); plt.show()

# ── Plot 4: Cost factors diverging bar ───────────────────────────────────────
df_div = df_factors.sort_values("cost_diff_usd").reset_index(drop=True)
vals_k = df_div["cost_diff_usd"] / 1000
colors_div = [GREEN if v < 0 else RED for v in df_div["cost_diff_usd"]]
fig, ax = plt.subplots(figsize=(13, 11))
bars = ax.barh(range(len(df_div)), vals_k, color=colors_div, edgecolor="white", height=0.72)
ax.set_yticks(range(len(df_div))); ax.set_yticklabels(df_div["factor"], fontsize=8.5)
for bar, val_usd in zip(bars, df_div["cost_diff_usd"]):
    w = bar.get_width()
    lbl = f"−${abs(val_usd/1000):.0f}K" if val_usd < 0 else f"+${val_usd/1000:.0f}K"
    ha  = "right" if val_usd < 0 else "left"
    off = -1.5 if val_usd < 0 else 1.5
    ax.text(w + off, bar.get_y()+bar.get_height()/2, lbl, va="center", ha=ha,
            fontsize=8, color=GREEN if val_usd < 0 else RED)
ax.axvline(0, color="black", linewidth=0.9); ax.invert_yaxis()
ax.set_xlabel("Cost Difference vs Global Average (USD Thousands)")
ax.set_title("Factors That Increase or Decrease Breach Cost\n(baseline: $4.88M global average)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x:+.0f}K"))
ax.legend(handles=[Patch(color=GREEN,label="Reduces cost"), Patch(color=RED,label="Increases cost")],
          loc="lower right", fontsize=9)
plt.tight_layout(); plt.savefig("plot4_cost_factors.png", dpi=150, bbox_inches="tight"); plt.show()

# ── Plot 5: AI impact — cost + time ──────────────────────────────────────────
level_order = ["No use","Limited use","Extensive use"]
ai_cost_plot = df_ai_cost[df_ai_cost["level"].isin(level_order)].set_index("level").loc[level_order]
ai_time_plot = df_ai_time.set_index("level").loc[level_order]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
b = ax1.bar(level_order, ai_cost_plot["avg_cost"], color=[RED,GOLD,GREEN], width=0.5, edgecolor="white")
for bar, val in zip(b, ai_cost_plot["avg_cost"]):
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.06,
             f"${val:.2f}M", ha="center", va="bottom", fontweight="bold", fontsize=11)
ax1.axhline(4.44, color=IBM_MID, linestyle="--", linewidth=1.2, label="Global avg $4.44M")
ax1.set_ylim(0, 7); ax1.set_ylabel("Avg Breach Cost (USD Millions)")
ax1.set_title("Breach Cost by AI Adoption Level")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x:.1f}M"))
ax1.legend(fontsize=9); ax1.set_xticklabels(level_order, fontsize=9)
mtti = ai_time_plot["mtti"].values.astype(int)
mttc = ai_time_plot["mttc"].values.astype(int)
x = np.arange(3)
ax2.bar(x, mtti, 0.5, color=IBM_BLUE, label="MTTI (identify)")
ax2.bar(x, mttc, 0.5, bottom=mtti, color=IBM_MID, label="MTTC (contain)")
for i, (m1, m2) in enumerate(zip(mtti, mttc)):
    ax2.text(i, m1/2,    str(m1), ha="center", va="center", color="white", fontsize=10, fontweight="bold")
    ax2.text(i, m1+m2/2, str(m2), ha="center", va="center", color="white", fontsize=10, fontweight="bold")
    ax2.text(i, m1+m2+4, f"{m1+m2}d", ha="center", va="bottom", fontsize=10, fontweight="bold")
ax2.set_xticks(x); ax2.set_xticklabels(level_order, fontsize=9)
ax2.set_ylabel("Days"); ax2.set_ylim(0, 340)
ax2.set_title("Detection + Containment Time\nby AI Adoption Level")
ax2.legend(loc="upper right", fontsize=9)
time_saved = int(ai_time_plot.loc["No use","total"] - ai_time_plot.loc["Extensive use","total"])
fig.suptitle(f"Extensive AI adoption saves ${ai_savings:.2f}M per breach ({roi_pct:.1f}%) and {time_saved} days",
             fontsize=12, fontweight="bold", y=1.01)
plt.tight_layout(); plt.savefig("plot5_ai_impact.png", dpi=150, bbox_inches="tight"); plt.show()

# ── Plot 6: Industry YoY dot plot ────────────────────────────────────────────
df_ind_yoy = df_industry.sort_values("yoy_pct").reset_index(drop=True)
fig, ax = plt.subplots(figsize=(10, 8))
for i, row in df_ind_yoy.iterrows():
    col = RED if row.yoy_pct > 0 else GREEN
    ax.hlines(i, 0, row.yoy_pct*100, color="#DDDDDD", linewidth=1.5, zorder=1)
    ax.scatter(row.yoy_pct*100, i, color=col, s=80, zorder=3)
    ax.text(row.yoy_pct*100 + (0.4 if row.yoy_pct>=0 else -0.4), i,
            f"{row.yoy_pct*100:+.1f}%", va="center",
            ha="left" if row.yoy_pct>=0 else "right", fontsize=8.5, color=col)
ax.set_yticks(range(len(df_ind_yoy))); ax.set_yticklabels(df_ind_yoy["industry"], fontsize=9)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Year-over-Year Change (%)"); ax.set_title("Industry Breach Cost: YoY Change 2024 → 2025")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:+.0f}%"))
ax.set_xlim(-30, 20)
ax.legend(handles=[Patch(color=GREEN,label="Cost decreased"), Patch(color=RED,label="Cost increased")],
          loc="lower right", fontsize=9)
plt.tight_layout(); plt.savefig("plot6_industry_yoy.png", dpi=150, bbox_inches="tight"); plt.show()

# ── Plot 7: Reducers vs amplifiers side by side ───────────────────────────────
df_amp_sorted = df_amplifiers.sort_values("cost_diff_usd", ascending=True).reset_index(drop=True)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))
for bar, val in zip(
    ax1.barh(range(len(df_reducers)), df_reducers["cost_diff_usd"]/1000,
             color=GREEN, edgecolor="white", height=0.7),
    df_reducers["cost_diff_usd"]
):
    ax1.text(bar.get_width()-1, bar.get_y()+bar.get_height()/2,
             f"−${abs(val/1000):.0f}K", va="center", ha="right", color="white", fontsize=8, fontweight="bold")
ax1.set_yticks(range(len(df_reducers))); ax1.set_yticklabels(df_reducers["factor"], fontsize=8.5)
ax1.invert_yaxis(); ax1.set_xlabel("Cost Reduction (USD Thousands)")
ax1.set_title("Factors That REDUCE Breach Cost", color=GREEN, fontweight="bold")
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x:.0f}K"))
for bar, val in zip(
    ax2.barh(range(len(df_amp_sorted)), df_amp_sorted["cost_diff_usd"]/1000,
             color=RED, edgecolor="white", height=0.7),
    df_amp_sorted["cost_diff_usd"]
):
    ax2.text(bar.get_width()-1, bar.get_y()+bar.get_height()/2,
             f"+${val/1000:.0f}K", va="center", ha="right", color="white", fontsize=8.5, fontweight="bold")
ax2.set_yticks(range(len(df_amp_sorted))); ax2.set_yticklabels(df_amp_sorted["factor"], fontsize=8.5)
ax2.invert_yaxis(); ax2.set_xlabel("Cost Increase (USD Thousands)")
ax2.set_title("Factors That INCREASE Breach Cost", color=RED, fontweight="bold")
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"${x:.0f}K"))
plt.suptitle("IBM Cost of a Data Breach 2025 — Cost Factor Analysis", fontsize=13, fontweight="bold")
plt.tight_layout(); plt.savefig("plot7_factors_split.png", dpi=150, bbox_inches="tight"); plt.show()

# ── Summary ───────────────────────────────────────────────────────────────────
top_country = df_country_sorted.iloc[0]
top_vector  = df_vector.iloc[0]
top_reducer = df_reducers.iloc[0]
top_amp     = df_amplifiers.sort_values("cost_diff_usd",ascending=False).iloc[0]
print(f"""
╔══════════════════════════════════════════════════════╗
║     IBM Cost of a Data Breach 2025 — Key Numbers     ║
╠══════════════════════════════════════════════════════╣
  Global average breach cost : $4.44M
  US breach cost (record)    : $10.22M
  Highest cost country       : {top_country['country']} (${top_country['cost_2025']:.2f}M)
  Top 3 countries share      : {top3_share:.1%} of all breach costs
  Highest risk attack vector : {top_vector['attack_vector']}
    → Frequency : {top_vector['pct_of_breaches']:.0%} of breaches
    → Avg cost  : ${top_vector['avg_cost_m']:.2f}M
    → Risk score: {top_vector['risk_score']:.3f}
  Biggest cost reducer       : {top_reducer['factor']} (${top_reducer['cost_diff_usd']/1000:.0f}K)
  Biggest cost amplifier     : {top_amp['factor']} (+${top_amp['cost_diff_usd']/1000:.0f}K)
  AI adoption ROI            : ${ai_savings:.2f}M saved per breach ({roi_pct:.1f}%)
    No use    → ${ai_none:.2f}M avg
    Extensive → ${ai_extensive:.2f}M avg
╚══════════════════════════════════════════════════════╝
""")