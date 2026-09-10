#!/usr/bin/env python3
"""E5 — the economics result under a stochastic policy.

E2 reported zero between-seed variance, because the scripted manager suppressed
the event deck and the deck is the model's only stochastic element. Those seeds
tested reproducibility, not robustness. Here the deck is answered rather than
suppressed and the manager's own thresholds are jittered per run, so the seeds
finally disagree with each other — and the question is whether the diversity
result survives that.

A first attempt answered the deck uniformly at random. Every one of 120 runs
died, most inside a month: a coin toss never patches a hull, and it takes the
broker's offer to sell the larder down to a twelve-day reserve. That is recorded
in the manuscript rather than dropped, because "add noise" is not the same as
"model a worse operator".
"""
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from scipy import stats
from lfstyle import setup, save, DATA, TABLES, INK, SOFT, ACCENT, GOOD, WARN, GRID

setup()
d = pd.read_csv(DATA / "e5_diversity_stochastic.csv")
det = pd.read_csv(DATA / "e2_diversity.csv")
det = det[det.studio == 1]
d["rate"] = d["media_total"] / d["end_day"]

# Survival must not track breadth, or the revenue trend is just run length.
r_surv, p_surv = stats.pearsonr(d["breadth"], d["survived"])

g = d.groupby("breadth").agg(
    rate=("rate", "mean"), rate_sd=("rate", "std"),
    total=("media_total", "mean"), total_sd=("media_total", "std"),
    survived=("survived", "mean"), n=("seed", "count")).reset_index()
g["cv_total"] = g["total_sd"] / g["total"] * 100
g["cv_rate"] = g["rate_sd"] / g["rate"] * 100
g["det_total"] = det.groupby("breadth")["media_total"].mean().values
g.to_csv(TABLES / "e5_stochastic_summary.csv", index=False)

r_rate, p_rate = stats.pearsonr(d["breadth"], d["rate"])
surv = d[d.survived == 1]
r_tot, p_tot = stats.pearsonr(surv["breadth"], surv["media_total"])
lo, hi = surv[surv.breadth == 1]["media_total"], surv[surv.breadth == 10]["media_total"]
ratio = hi.mean() / lo.mean()
det_ratio = det[det.breadth == 10]["media_total"].mean() / det[det.breadth == 1]["media_total"].mean()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.0))

ax1.errorbar(g["breadth"], g["rate"], yerr=g["rate_sd"], color=ACCENT, marker="o",
             ms=4.5, lw=1.6, capsize=3, label="stochastic policy (12 seeds, ±1 s.d.)")
ax1.set_xlabel("crops in the rotation")
ax1.set_ylabel("broadcast revenue per day survived (credits)")
ax1.set_title("The diversity result survives a worse operator", loc="left", color=INK)
ax1.legend(loc="upper left")
ax1.grid(axis="y"); ax1.set_axisbelow(True)
ax1.annotate(f"r = {r_rate:.3f}, p = {p_rate:.0e}\n×{ratio:.2f} one crop to ten\n"
             f"(deterministic: ×{det_ratio:.2f})",
             xy=(6.0, g["rate"].min() * 1.25), fontsize=7.6, color=ACCENT)

# Where the variance actually lives: run length, not earning rate.
w = 0.38; x = np.arange(len(g))
ax2.bar(x - w/2, g["cv_total"], w, color=SOFT, label="total earned")
ax2.bar(x + w/2, g["cv_rate"], w, color=GOOD, label="earning rate")
ax2.set_xticks(x); ax2.set_xticklabels(g["breadth"])
ax2.set_xlabel("crops in the rotation")
ax2.set_ylabel("coefficient of variation across seeds (%)")
ax2.set_title("The noise decides whether you survive, not how well you earn",
              loc="left", color=INK)
ax2.legend(loc="upper left"); ax2.grid(axis="y"); ax2.set_axisbelow(True)
# a white-backed box, because the bars fill the panel and plain text is lost on them
ax2.text(0.5, g["cv_total"].max() * 0.63,
         f"survival is {g['survived'].mean():.0%} at every breadth\n"
         f"(r = {r_surv:.3f}, p = {p_surv:.2f}) — so run length\nis not what drives the trend",
         fontsize=7.4, color=INK, va="center",
         bbox=dict(boxstyle="round,pad=0.45", facecolor="white",
                   edgecolor=GRID, linewidth=0.7))

fig.tight_layout()
save(fig, "fig5_stochastic_policy.png")

print(g[["breadth", "rate", "rate_sd", "cv_total", "cv_rate", "survived", "n"]].round(1).to_string(index=False))
print(f"\nrate vs breadth, all {len(d)} runs:  r={r_rate:.3f} p={p_rate:.2e}")
print(f"total vs breadth, survivors n={len(surv)}: r={r_tot:.3f} p={p_tot:.2e}")
print(f"survival vs breadth:               r={r_surv:.3f} p={p_surv:.3f}")
print(f"ratio 1->10 crops: stochastic {ratio:.2f}x vs deterministic {det_ratio:.2f}x")
