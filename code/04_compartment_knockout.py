#!/usr/bin/env python3
"""E3 — knock each compartment out and see what the loop loses.

Four compartments share two waste streams, so their contributions are not
independent. Each arm is either a single compartment, all four, or all-but-one,
which separates what a compartment adds from what it adds *given the others*.
"""
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from lfstyle import setup, save, DATA, TABLES, INK, SOFT, ACCENT, GOOD, WARN

setup()
df = pd.read_csv(DATA / "e3_knockout.csv")
g = df.groupby("arm").agg(
    co2_floor=("co2_floor", "mean"), co2_mean=("co2_mean", "mean"),
    ls_share=("ls_share_mean", "mean"), waste=("waste_processed", "mean"),
    service=("service_total", "mean"), harvests=("harvests", "mean")).reset_index()
g.to_csv(TABLES / "e3_knockout_summary.csv", index=False)

base = g[g.arm == "none"].iloc[0]
allf = g[g.arm == "all"].iloc[0]
COMP = ["worms", "nitrifier", "digester", "reef"]
NICE = {"worms": "mealworm tier", "nitrifier": "nitrifying\nbioreactor",
        "digester": "anaerobic\ndigester", "reef": "reef microcosm"}

rows = []
for c in COMP:
    alone = g[g.arm == "only_" + c].iloc[0]
    without = g[g.arm == "without_" + c].iloc[0]
    rows.append({
        "compartment": NICE[c],
        "co2_alone": alone.co2_mean - base.co2_mean,       # what it adds on its own
        "co2_marginal": allf.co2_mean - without.co2_mean,  # what it adds given the rest
        "service_alone": alone.service - base.service,
        "waste_alone": alone.waste,
    })
k = pd.DataFrame(rows)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.0))
x = np.arange(len(k)); w = 0.38
ax1.bar(x - w/2, k["co2_alone"], w, color=ACCENT, label="added on its own")
ax1.bar(x + w/2, k["co2_marginal"], w, color=SOFT, label="added given the other three")
ax1.axhline(0, color=SOFT, lw=0.8)
ax1.set_xticks(x); ax1.set_xticklabels(k["compartment"], fontsize=8)
ax1.set_ylabel("change in mean CO$_2$ buffer (kg)")
ax1.set_title("Carbon: one compartment does the work", loc="left", color=INK)
ax1.legend(loc="upper left"); ax1.grid(axis="y"); ax1.set_axisbelow(True)

ax2.bar(x, k["service_alone"], 0.55, color=GOOD)
ax2.set_xticks(x); ax2.set_xticklabels(k["compartment"], fontsize=8)
ax2.set_ylabel("extra earned from the station over 260 days (credits)")
ax2.set_title("Income: a different compartment does that", loc="left", color=INK)
ax2.grid(axis="y"); ax2.set_axisbelow(True)
for i, v in enumerate(k["waste_alone"]):
    if v > 0:
        ax2.text(i, k["service_alone"].iloc[i] + 400, f"{v:.0f} waste\nprocessed",
                 ha="center", fontsize=7, color=SOFT)

fig.tight_layout()
save(fig, "fig3_compartment_knockout.png")
print(g.round(2).to_string(index=False))
print("\nmarginal contributions:\n", k.round(1).to_string(index=False))
