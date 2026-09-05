#!/usr/bin/env python3
"""E1 — what actually stabilises the carbon loop.

A closed farm that exports food exports carbon with it, so the buffer runs down.
The naive way to test a fix is to compare a plants-only farm against one with a
heterotroph in it and see which survives; that comparison is confounded twice
over, by starvation timing and by raw-regolith growth. Both are removed here
(deep pantry, worked beds) so the carbon question is the only one being asked.
"""
import pandas as pd, matplotlib.pyplot as plt
from lfstyle import setup, save, DATA, TABLES, INK, SOFT, ACCENT, GOOD, WARN

setup()
df = pd.read_csv(DATA / "e1_carbon.csv")
tr = pd.read_csv(DATA / "e1_traces.csv")

LABEL = {
    "none": "no compartment", "composter_only": "oxidation loop only",
    "nitrifier": "nitrifying bioreactor", "worms": "mealworm tier",
    "digester": "anaerobic digester", "all_four": "all four compartments",
    "fungal_rotation": "mushrooms in the rotation",
    "algal_rotation": "spirulina in the rotation",
}
g = df.groupby("arm").agg(
    co2_floor=("co2_floor", "mean"), co2_floor_sd=("co2_floor", "std"),
    co2_mean=("co2_mean", "mean"), harvests=("harvests", "mean"),
    survived=("survived", "mean"), n=("seed", "count")).reset_index()
g["label"] = g["arm"].map(LABEL).fillna(g["arm"])
g = g.sort_values("co2_floor")
g.to_csv(TABLES / "e1_carbon_summary.csv", index=False)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.0),
                               gridspec_kw={"width_ratios": [1.15, 1]})

# --- left: the floor, which is the number that matters ---
cols = [ACCENT if a == "digester" else SOFT for a in g["arm"]]
ax1.barh(g["label"], g["co2_floor"], color=cols, height=0.62,
         xerr=g["co2_floor_sd"], error_kw=dict(ecolor="#9aa8b8", lw=0.8, capsize=2))
ax1.set_xlabel("lowest CO$_2$ buffer reached over 300 days (kg)")
ax1.set_title("Only the digester lifts the carbon floor", loc="left", color=INK)
ax1.axvline(14, color=WARN, lw=0.9, ls="--")
ax1.text(15.5, -0.42, "below 14 kg all photosynthesis\nruns at the 15% floor",
         fontsize=7.2, color=WARN, va="bottom")
ax1.grid(axis="x")
ax1.set_axisbelow(True)

# --- right: the trajectories that produce it ---
show = ["none", "worms", "fungal_rotation", "digester"]
style = {"none": (SOFT, "-"), "worms": ("#8a94a4", "--"),
         "fungal_rotation": (GOOD, "-."), "digester": (ACCENT, "-")}
for arm in show:
    s = tr[tr.arm == arm]
    c, ls = style[arm]
    ax2.plot(s["day"], s["co2"], color=c, ls=ls, lw=1.5, label=LABEL[arm])
ax2.axhline(14, color=WARN, lw=0.9, ls="--")
ax2.set_xlabel("day"); ax2.set_ylabel("CO$_2$ buffer (kg)")
ax2.set_title("A farm exports its carbon inside the food", loc="left", color=INK)
ax2.legend(loc="upper left")
ax2.grid(axis="y"); ax2.set_axisbelow(True)

fig.tight_layout()
save(fig, "fig1_carbon_stability.png")

print(g[["label", "co2_floor", "co2_mean", "harvests", "n"]].round(1).to_string(index=False))
