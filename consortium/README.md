# Minimal consortium module

Challenge 7 from [genai-spacebio-roadmap](https://github.com/dr-richard-barker/genai-spacebio-roadmap):
predict the minimal plant + fungal + microbial taxon set that sustains closed-loop
nutrient cycling, then check the prediction against this repo's own measured
closed-loop findings (see `../manuscript_chapter.md`).

This module lives inside `LunarFarm-BLSS` rather than as its own repo because the
four findings it has to be checked against are here. It pulls real data from
three sibling repos — same convention this repo already uses for `LunarSims`:

```
../../osdr-plant-microbiome
../../Microbiome_of_seedlings_in_space
../../Myco_tissue_RNAseq
```

## Status: milestone 1 done, milestone 3 rescoped

1. **Taxon inventory** (done — see [`FINDINGS.md`](FINDINGS.md)) — what real or
   candidate organisms exist across the sibling repos, honestly tagged by
   evidence tier.
2. **GEM fitness for use** (done — see [`FINDINGS.md`](FINDINGS.md)) — does the
   one real genome-scale metabolic model already in the portfolio actually run.
   No upstream bug; `*_gapfilled.xml` is the model to use.
3. **Contamination filter** (done — see [`FINDINGS.md`](FINDINGS.md)) — checked
   every real detected species against 3 cited reference lists (Salter 2014
   kitome, Bashir 2016 NASA cleanroom, Dewhirst 2010 human oral) instead of
   genus-level guesses. Result: 57% flagged, and the strongest apparent
   signal in the data is mostly contamination — only 1 real bacterium
   (*Cloacibacterium caeni*) survives with meaningful recurrence.
4. **Flux-balance co-culture screen** (rescoped, not started) — the original
   "minimal consortium" scope needs more real, trustworthy taxa than
   currently exist in this inventory. See `FINDINGS.md`'s revised options.

No consortium composition claim is made yet. This is infrastructure and an
honesty check on the input data, not a result.

## Layout

```
code/01_build_taxon_inventory.py     real taxon inventory from the 3 sibling repos
     02_gem_sanity_check.py          FBA sanity check on the existing P. ostreatus GEMs
     03_contamination_filter.py      checks real taxa against 3 cited reference lists
data/taxon_inventory.csv             output of (1) — 72 rows, each tagged with evidence tier
data/gem_sanity_check.csv            output of (2)
data/ref_salter2014_kitome_genera.csv  reference list used by (3)
data/CONTAMINATION_SOURCES.md        the 3 reference sources, citations + caveats
data/taxon_inventory_filtered.csv    output of (3) — inventory + contamination_flags + consortium_candidate
FINDINGS.md                          milestone 1 write-up
```

## Reproducing

```bash
pip install cobra
cd code
python3 01_build_taxon_inventory.py
python3 02_gem_sanity_check.py
python3 03_contamination_filter.py
```
