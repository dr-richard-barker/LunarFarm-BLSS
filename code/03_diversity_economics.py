#!/usr/bin/env python3
"""E2 — does variety actually pay, and which income stream pays for it.

The farm has two income streams by design. The broadcast studio prices novelty,
so it should reward a wide rotation; the life-support service contract prices
closure, so it should be indifferent to what is grown. This tests whether the
two behave as designed and separably.
"""
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from scipy import stats
from lfstyle import setup, save, DATA, TABLES, INK, SOFT, ACCENT, GOOD, WARN

setup()
df = pd.read_csv(DATA / "e2_diversity.csv")
on = df[df.studio == 1].groupby("breadth").agg(
    media=("media_total", "mean"), media_sd=("media_total", "std"),
    service=("service_total", "mean"), service_sd=("service_total", "std"),
    credits=("credits_end", "mean"), kinds=("kinds", "mean")).reset_index()
off = df[df.studio == 0].groupby("breadth").agg(
    credits=("credits_end", "mean"), service=("service_total", "mean")).reset_index()
on.to_csv(TABLES / "e2_diversity_summary.csv", index=False)

# how strongly does each stream track rotation breadth?
r_media, p_media = stats.pearsonr(on["breadth"], on["media"])
r_serv, p_serv = stats.pearsonr(on["breadth"], on["service"])
ratio = on.loc[on.breadth == on.breadth.max(), "media"].iloc[0] / on.loc[on.breadth == 1, "media"].iloc[0]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.0))

ax1.errorbar(on["breadth"], on["media"], yerr=on["media_sd"], color=ACCENT,
             marker="o", ms=4.5, lw=1.6, capsize=2.5, label="broadcast (prices novelty)")
ax1.errorbar(on["breadth"], on["service"], yerr=on["service_sd"], color=GOOD,
             marker="s", ms=4.2, lw=1.6, capsize=2.5, ls="--",
             label="life-support contract (prices closure)")
ax1.set_xlabel("crops in the rotation")
ax1.set_ylabel("earned over 240 days (credits)")
ax1.set_title("Two income streams, one of them diversity-priced", loc="left", color=INK)
ax1.legend(loc="center left")
ax1.grid(axis="y"); ax1.set_axisbelow(True)
ax1.annotate(f"×{ratio:.2f} from one crop to ten\nr = {r_media:.3f}, p = {p_media:.1e}",
             xy=(on["breadth"].iloc[-1], on["media"].iloc[-1]),
             xytext=(5.2, on["media"].max() * 0.62), fontsize=7.6, color=ACCENT)
ax1.annotate(f"flat: r = {r_serv:.2f}, p = {p_serv:.2f}",
             xy=(6, on["service"].iloc[5]), xytext=(5.6, on["service"].iloc[5] * 0.45),
             fontsize=7.6, color=GOOD)

w = 0.38
x = np.arange(len(on))
ax2.bar(x - w/2, on["credits"], w, color=ACCENT, label="with a studio")
ax2.bar(x + w/2, off["credits"], w, color=SOFT, label="without one")
ax2.set_xticks(x); ax2.set_xticklabels(on["breadth"])
ax2.set_xlabel("crops in the rotation"); ax2.set_ylabel("credits held at day 240")
ax2.set_title("What the farm is worth at the end", loc="left", color=INK)
ax2.legend(loc="upper left")
ax2.grid(axis="y"); ax2.set_axisbelow(True)

fig.tight_layout()
save(fig, "fig2_diversity_economics.png")
print(on.round(0).to_string(index=False))
print(f"\nbroadcast vs breadth: r={r_media:.3f} p={p_media:.2e} | ratio 1->10 crops = {ratio:.2f}x")
print(f"service   vs breadth: r={r_serv:.3f} p={p_serv:.3f}")
