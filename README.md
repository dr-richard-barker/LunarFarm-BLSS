# Lunar Farm — BLSS Economics

**What a playable closed loop teaches about closing one.**

A reproducible study of a human-in-the-loop bioregenerative life support model. The instrument is
[Lunar Farm](https://github.com/dr-richard-barker/LunarSims), a tile-based lunar agriculture
simulation with coupled carbon, oxygen, water and nitrogen budgets, an explicit power budget with
load shedding, and a fully specified economy. This repository asks what the model shows once a
decision-maker is inside the loop.

Read the write-up: **[`manuscript_chapter.md`](manuscript_chapter.md)**.

## New: minimal consortium module (in progress)

[`consortium/`](consortium/) asks a different question than the four findings below: not what
the *game* shows, but what a *real* minimal plant+fungal+microbial consortium would need to be to
back a closed loop like this one. Milestone 1 is done — real taxon inventory, a GEM sanity check,
and a contamination filter against 3 cited reference lists. Result so far: the strongest apparent
taxonomic signal in the real data is mostly reagent/handling contamination, not plant
colonization — see [`consortium/FINDINGS.md`](consortium/FINDINGS.md). No consortium composition
claim yet.

## The four findings

1. **Only an anaerobic digester lifts the carbon floor.** Across eight seeded runs per arm, with
   starvation timing and substrate quality controlled out, the digester raises the minimum CO₂
   buffer from 5.1 kg to 79.4 kg — a factor of 15.6. A mealworm tier, a nitrifying bioreactor and
   fungal crops in rotation raise the *mean* buffer while leaving the *minimum* untouched, so they
   still spend part of every lunar cycle in carbon limitation.
2. **Biodiversity can be made to pay, separably.** A broadcast mechanic that prices subject
   novelty produces revenue scaling with rotation breadth (r = 0.989, p = 7.4 × 10⁻⁸, 2.94× from
   one crop to ten). A life-support contract that prices closure is flat against breadth
   (r = −0.584, p = 0.076). Two incentives, one farm, no interference.
3. **Two waste compartments compete, and the better earner is the worse citizen.** Adding a
   nitrifying bioreactor *reduces* the system's mean carbon buffer by 60.6 kg when a digester is
   present, because both draw on the same waste stream — while earning more than twice as much.
   A player optimising income alone degrades the loop they are paid to close.
4. **There is an optimum dark-grown fraction, near 20%.** Load shedding falls monotonically as
   more of the farm is grown in the dark, but every run at or above 60% fails — on **oxygen**, not
   food, with a saturated carbon buffer and 700+ days of stores untouched. Heterotrophs are a
   supplement, never a substitute.
5. **Every conclusion survives a worse operator — and two secondary ones change.** Re-run with the event deck live and the
   manager's thresholds jittered per run, the ratio is **2.93×** against 2.94× deterministic
   (r = 0.967, p = 5.5 × 10⁻⁷², 120 runs), and survival is flat at 58% across every rotation
   breadth — so run length is not driving it. The variance decomposition is the new part: the
   coefficient of variation of total earnings is 34–38%, but of the *earning rate* only 1–8%. The
   noise decides whether a farm survives, not how well it trades once it does.

   All four experiments were re-run this way. The digester's carbon floor holds at 15.1× against
   15.6× (p = 7 × 10⁻²¹); the negative nitrifier interaction gets *larger* at −86.0 ± 8.7 kg
   (p = 6 × 10⁻⁸); the oxygen cliff sits at the same 40–60% boundary, with 75% of failures above
   it being oxygen exhaustion. Two secondary readings change once there is a spread attached:
   a **mealworm tier has no detectable carbon effect at all** (−4.2 ± 11.7 kg, p = 0.73, where the
   deterministic run implied a small negative), and a **fungal rotation's carbon floor is both far
   higher and far more variable** than one trajectory suggested (31.3 ± 20.5 kg against 6.2). The
   deterministic arms were not wrong so much as unquantified.

## Two notes on method

**The controls mattered.** Our first, uncontrolled comparison gave a confidently wrong answer. A plants-only farm failed in
3 of 3 runs while a mushroom rotation survived in 3 of 3, which looked like proof that a respiring
compartment rescues the carbon loop. It was not: a photosynthetic control survived too, and once
starvation timing and raw-regolith growth were controlled, the mushroom rotation turned out to
raise the mean buffer and not its floor. The effect was harvest cadence, not respiration.

**So did the shape of the noise.** Our first stochastic policy answered the event deck uniformly
at random, and every one of 120 runs died — most inside a month. A coin toss never patches a hull,
so pressure walks to the abort limit, and it takes the broker's offer to sell the larder down to a
twelve-day reserve. That would have supported the conclusion that the economy is fragile; it was
the policy that was fragile. Adding noise is not the same as modelling a worse operator.

Both failures are documented in the manuscript rather than quietly corrected, because they are the
most transferable things here.

## Layout

```
code/01_sweep.js               drives the game's own sim.js — writes data/*.csv
    lfstyle.py                 shared figure style
    02_carbon_stability.py     E1 — what stabilises the carbon loop
    03_diversity_economics.py  E2 — does variety pay, and which stream pays for it
    04_compartment_knockout.py E3 — each compartment alone and given the others
    05_night_resilience.py     E4 — how far a farm can lean on dark-grown crops
    06_stochastic_policy.py    E5 — does the diversity result hold with the deck live
    07_robustness.py           E6-E8 — E1, E3 and E4 again, with the deck live
data/                          raw sweep output, committed
results/figures/  tables/      every figure and table, all generated
manuscript_chapter.md          the write-up
docs/                          GitHub Pages summary
consortium/                    minimal-consortium module (see consortium/README.md) — in progress
```

## Reproducing

Requires Node 18+, Python 3.9+ with pandas, matplotlib and scipy, and a checkout of
[LunarSims](https://github.com/dr-richard-barker/LunarSims) beside this repository.

```bash
node code/01_sweep.js
python3 code/02_carbon_stability.py
python3 code/03_diversity_economics.py
python3 code/04_compartment_knockout.py
python3 code/05_night_resilience.py
python3 code/06_stochastic_policy.py
python3 code/07_robustness.py
```

`01_sweep.js` resolves the game with `LUNARFARM_DIR`, defaulting to `../LunarSims/farm`. It loads
`data.js` and `sim.js` directly and seeds `Math.random`, so **the analysis measures the code that
ships** and cannot drift from it.

## Parameter provenance

Compartment ratios are taken from the Lunar Palace 1 ("Yuegong-1") 105-day multi-crew closed
experiment of February–May 2014, the most completely instrumented integrated BLSS run with
published element budgets. The ratios are theirs; the throughputs they are applied to are scaled
for play.

- Li L *et al.* (2015) *Life Sci Space Res* 7:9–14 — *Tenebrio molitor*: 8.13% bioconversion,
  78.43% frass, essential amino acids 41.30% of total.
  [doi:10.1016/j.lssr.2015.08.002](https://doi.org/10.1016/j.lssr.2015.08.002)
- Fu Y *et al.* (2016) *Astrobiology* 16(12):925–936 — 21 plant species, 20.5% nitrogen recovery
  from urine, 41% solid waste degradation, 55% of food regenerated.
  [doi:10.1089/ast.2016.1477](https://doi.org/10.1089/ast.2016.1477)
- Dong C *et al.* (2017) *Astrobiology* 17(1):78–86 — 247 g d⁻¹ carbon imported inside stored
  food; >99% of water lost through leaf transpiration.
  [doi:10.1089/ast.2016.1466](https://doi.org/10.1089/ast.2016.1466)

**The reef microcosm compartment is speculative** and labelled as such everywhere it appears. No
marine calcifying system has been flown, and calcification is a local carbon dioxide source rather
than a sink.

## Limitations

The model is a game; its constants are balanced for play, and nothing here is a measurement of a
physical life support system. E1–E4 are deterministic by construction — their scripted policy
suppresses the event deck, the model's only stochastic element — so those seeds test
reproducibility rather than robustness. E5–E8 re-run all four stochastically and every headline
conclusion reproduces; where the two disagree, the stochastic figure is the one with an interval
attached. The stochastic operator model (0.75 remedial) is itself chosen, not measured. No human
players were involved in any of these measurements. See §6 of the manuscript.

## Licence

MIT. See [LICENSE](LICENSE).
