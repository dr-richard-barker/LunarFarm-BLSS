# Lunar Farm — BLSS Economics

**What a playable closed loop teaches about closing one.**

A reproducible study of a human-in-the-loop bioregenerative life support model. The instrument is
[Lunar Farm](https://github.com/dr-richard-barker/LunarSims), a tile-based lunar agriculture
simulation with coupled carbon, oxygen, water and nitrogen budgets, an explicit power budget with
load shedding, and a fully specified economy. This repository asks what the model shows once a
decision-maker is inside the loop.

Read the write-up: **[`manuscript_chapter.md`](manuscript_chapter.md)**.

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

## A note on method

Our first, uncontrolled comparison gave a confidently wrong answer. A plants-only farm failed in
3 of 3 runs while a mushroom rotation survived in 3 of 3, which looked like proof that a respiring
compartment rescues the carbon loop. It was not: a photosynthetic control survived too, and once
starvation timing and raw-regolith growth were controlled, the mushroom rotation turned out to
raise the mean buffer and not its floor. The effect was harvest cadence, not respiration.

That failure is documented in §3 of the manuscript rather than quietly corrected, because it is
the most transferable thing here.

## Layout

```
code/01_sweep.js               drives the game's own sim.js — writes data/*.csv
    lfstyle.py                 shared figure style
    02_carbon_stability.py     E1 — what stabilises the carbon loop
    03_diversity_economics.py  E2 — does variety pay, and which stream pays for it
    04_compartment_knockout.py E3 — each compartment alone and given the others
    05_night_resilience.py     E4 — how far a farm can lean on dark-grown crops
data/                          raw sweep output, committed
results/figures/  tables/      every figure and table, all generated
manuscript_chapter.md          the write-up
docs/                          GitHub Pages summary
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
physical life support system. Between-seed variance in E2 is exactly zero because the scripted
policy suppresses the event deck, the model's only stochastic element — the seeds test
reproducibility, not robustness. All arms share one management policy, and no human players were
involved in these measurements. See §6 of the manuscript.

## Licence

MIT. See [LICENSE](LICENSE).
