#!/usr/bin/env python3
"""E4 — how much of the farm should grow in the dark.

A dark-grown crop is immune to the fortnight of lunar night, when lit halls are
shed one at a time for want of power. That argues for growing more of them. It
is also a heterotroph: it burns oxygen and returns carbon dioxide. This sweeps
the dark-grown fraction to find where the trade turns.
"""
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from lfstyle import setup, save, DATA, TABLES, INK, SOFT, ACCENT, GOOD, WARN

setup()
df = pd.read_csv(DATA / "e4_night.csv")
g = df.groupby(["batteries", "dark_frac"]).agg(
    shed=("shed_mean", "mean"), harvests=("harvests", "mean"),
    survived=("survived", "mean"), co2=("co2_mean", "mean"),
    end_day=("end_day", "mean")).reset_index()
g.to_csv(TABLES / "e4_night_summary.csv", index=False)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.0))

for b, col, ls in [(0, SOFT, "--"), (3, ACCENT, "-")]:
    s = g[g.batteries == b]
    ax1.plot(s["dark_frac"] * 100, s["shed"] * 100, color=col, ls=ls, marker="o", ms=4,
             lw=1.6, label=f"{b} extra battery banks")
ax1.set_xlabel("share of the farm grown in the dark (%)")
ax1.set_ylabel("mean load shedding while lights are called for (%)")
ax1.set_title("Dark-grown crops are never shed", loc="left", color=INK)
ax1.legend(); ax1.grid(axis="y"); ax1.set_axisbelow(True)

s = g[g.batteries == 3]
ax2.plot(s["dark_frac"] * 100, s["harvests"], color=GOOD, marker="o", ms=4, lw=1.6)
ax2.set_xlabel("share of the farm grown in the dark (%)")
ax2.set_ylabel("harvests in 200 days", color=GOOD)
ax2.tick_params(axis="y", colors=GOOD)
ax2.set_title("but they cannot make the oxygen", loc="left", color=INK)
dead = s[s.survived < 1]
if len(dead):
    x0 = dead["dark_frac"].min() * 100
    ax2.axvspan(x0 - 2, 102, color=WARN, alpha=0.10)
    ax2.text(x0 + 2, s["harvests"].max() * 0.62,
             "every run here ends on\noxygen, not on food:\nno photoautotroph left\nto replace what the crew\nand the fungi burn",
             fontsize=7.4, color=WARN, va="top")
ax2.grid(axis="y"); ax2.set_axisbelow(True)

fig.tight_layout()
save(fig, "fig4_night_resilience.png")
print(g.round(3).to_string(index=False))
