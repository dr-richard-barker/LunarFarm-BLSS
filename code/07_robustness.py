#!/usr/bin/env python3
"""E6-E8 — E1, E3 and E4 again with the event deck live.

Same arms, same measurements, same twelve seeds; the only change is the policy.
A conclusion drawn from a single deterministic trajectory that does not survive
twelve noisy operators was a property of the manager, not of the loop.

Food is held non-limiting in these arms, as it is in their deterministic
counterparts. That control becomes load-bearing once the deck is live: the
broker's resupply offer sells the larder down to a twelve-day reserve, which
would reintroduce exactly the starvation confound the deep pantry removes.
"""
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from scipy import stats
from lfstyle import setup, save, DATA, TABLES, INK, SOFT, ACCENT, GOOD, WARN, GRID

setup()
d6 = pd.read_csv(DATA / "e6_carbon_stochastic.csv")
d1 = pd.read_csv(DATA / "e1_carbon.csv")
d7 = pd.read_csv(DATA / "e7_knockout_stochastic.csv")
d8 = pd.read_csv(DATA / "e8_night_stochastic.csv")
d4 = pd.read_csv(DATA / "e4_night.csv")

LABEL = {"none": "no compartment", "nitrifier": "nitrifier", "worms": "mealworm",
         "digester": "digester", "all_four": "all four",
         "fungal_rotation": "fungal rotation", "algal_rotation": "algal rotation"}
ORDER = ["none", "nitrifier", "worms", "algal_rotation", "all_four", "fungal_rotation", "digester"]

fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(14.6, 4.2))

# ---------- A: does the digester still lift the floor ----------
gs = d6.groupby("arm")["co2_floor"].agg(["mean", "std"]).reindex(ORDER)
gd = d1.groupby("arm")["co2_floor"].mean().reindex(ORDER)
x = np.arange(len(ORDER)); w = 0.38
axA.bar(x - w/2, gd.values, w, color=SOFT, label="deterministic (E1)")
axA.bar(x + w/2, gs["mean"].values, w, color=ACCENT, yerr=gs["std"].values,
        error_kw=dict(ecolor="#7a8fa4", lw=0.9, capsize=2.5), label="stochastic (E6, 12 seeds)")
axA.axhline(14, color=WARN, lw=0.9, ls="--")
axA.set_xticks(x); axA.set_xticklabels([LABEL[a] for a in ORDER], rotation=32, ha="right", fontsize=7.6)
axA.set_ylabel("lowest CO$_2$ buffer reached (kg)")
axA.set_title("A — the carbon floor result holds", loc="left", color=INK)
axA.legend(loc="upper left"); axA.grid(axis="y"); axA.set_axisbelow(True)
dig, non = d6[d6.arm == "digester"]["co2_floor"], d6[d6.arm == "none"]["co2_floor"]
t, p = stats.ttest_ind(dig, non, equal_var=False)
axA.text(0.04, 0.62, f"digester ×{dig.mean()/non.mean():.1f}\nWelch p = {p:.0e}",
         transform=axA.transAxes, fontsize=7.4, color=ACCENT)

# ---------- B: are the marginal contributions real ----------
COMP = ["digester", "reef", "worms", "nitrifier"]
NICE = {"worms": "mealworm", "nitrifier": "nitrifier", "digester": "digester", "reef": "reef"}
allf = d7[d7.arm == "all"]["co2_mean"]
marg, err, ps = [], [], []
for c in COMP:
    without = d7[d7.arm == "without_" + c]["co2_mean"]
    marg.append(allf.mean() - without.mean())
    err.append(np.hypot(allf.std(), without.std()) / np.sqrt(len(allf)))
    ps.append(stats.ttest_ind(allf, without, equal_var=False)[1])
cols = [GOOD if m > 0 else WARN for m in marg]
cols = [c if pp < 0.05 else SOFT for c, pp in zip(cols, ps)]
y = np.arange(len(COMP))
axB.barh(y, marg, 0.6, color=cols, xerr=err,
         error_kw=dict(ecolor="#7a8fa4", lw=0.9, capsize=2.5))
axB.axvline(0, color=SOFT, lw=0.8)
axB.set_yticks(y); axB.set_yticklabels([NICE[c] for c in COMP], fontsize=8.5)
axB.set_xlabel("marginal change in mean CO$_2$ buffer, given the other three (kg)")
axB.set_title("B — the negative interaction is real", loc="left", color=INK)
axB.grid(axis="x"); axB.set_axisbelow(True)
for i, (m, pp) in enumerate(zip(marg, ps)):
    lab = f"p = {pp:.0e}" if pp < 0.05 else f"n.s. (p = {pp:.2f})"
    # clear the error-bar cap as well as the bar end
    off = err[i] + 6
    axB.text(m + (off if m > 0 else -off), i, lab, va="center",
             ha="left" if m > 0 else "right", fontsize=7.2,
             color=INK if pp < 0.05 else SOFT)
axB.set_xlim(min(marg) * 1.55, max(marg) * 1.75)

# ---------- C: is the oxygen cliff robust ----------
s8 = d8.groupby("dark_frac")["survived"].mean()
s4 = d4.groupby("dark_frac")["survived"].mean()
axC.plot(s4.index * 100, s4.values * 100, color=SOFT, ls="--", marker="s", ms=4,
         lw=1.6, label="deterministic (E4, 5 seeds)")
axC.plot(s8.index * 100, s8.values * 100, color=ACCENT, marker="o", ms=4.5,
         lw=1.8, label="stochastic (E8, 12 seeds)")
axC.axvspan(50, 102, color=WARN, alpha=0.10)
axC.set_xlabel("share of the farm grown in the dark (%)")
axC.set_ylabel("runs surviving 200 days (%)")
axC.set_title("C — the cliff sits in the same place", loc="left", color=INK)
axC.legend(loc="lower left"); axC.grid(axis="y"); axC.set_axisbelow(True)
axC.set_ylim(-5, 108)
oxy = (d8[(d8.dark_frac >= 0.6) & (d8.survived == 0)]["failure"]
       .str.contains("Oxygen").mean())
axC.text(52, 66, f"{oxy:.0%} of failures here\nare oxygen exhaustion;\nthe rest are the deck",
         fontsize=7.4, color=WARN,
         bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=GRID, lw=0.7))

fig.tight_layout()
save(fig, "fig6_robustness.png")

# ---------- tables ----------
tabA = pd.DataFrame({"arm": ORDER, "det_floor": gd.values,
                     "stoch_floor": gs["mean"].values, "stoch_sd": gs["std"].values})
tabA.to_csv(TABLES / "e6_carbon_stochastic.csv", index=False)
pd.DataFrame({"compartment": COMP, "marginal_co2": marg, "sem": err, "p": ps}) \
  .to_csv(TABLES / "e7_marginals_stochastic.csv", index=False)
pd.DataFrame({"dark_frac": s8.index, "stoch_survival": s8.values,
              "det_survival": s4.reindex(s8.index).values}) \
  .to_csv(TABLES / "e8_night_stochastic.csv", index=False)

print(tabA.round(1).to_string(index=False))
print(f"\ndigester floor: {non.mean():.1f} -> {dig.mean():.1f} kg "
      f"(x{dig.mean()/non.mean():.1f}), Welch p = {p:.2e}")
print("\nmarginal contributions given the other three:")
for c, m, e, pp in zip(COMP, marg, err, ps):
    print(f"  {NICE[c]:<10} {m:+7.1f} +/- {e:4.1f} kg   p = {pp:.3g}"
          f"   {'significant' if pp < 0.05 else 'NOT SIGNIFICANT'}")
print("\nsurvival by dark fraction (stochastic vs deterministic):")
for k in s8.index:
    print(f"  {k*100:5.0f}%   {s8[k]:.2f}   vs   {s4.get(k, float('nan')):.2f}")
print(f"\noxygen share of failures at >=60% dark: {oxy:.0%}")
