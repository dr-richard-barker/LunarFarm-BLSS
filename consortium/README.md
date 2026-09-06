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

## Status: milestone 1 of 3

1. **Taxon inventory** (done — see [`FINDINGS.md`](FINDINGS.md)) — what real or
   candidate organisms exist across the sibling repos, honestly tagged by
   evidence tier.
2. **GEM fitness for use** (done — see [`FINDINGS.md`](FINDINGS.md)) — does the
   one real genome-scale metabolic model already in the portfolio actually run.
3. **Flux-balance co-culture screen** (not started — blocked on prerequisites
   found in milestone 2).

No consortium composition claim is made yet. This is infrastructure and an
honesty check on the input data, not a result.

## Layout

```
code/01_build_taxon_inventory.py   real taxon inventory from the 3 sibling repos
     02_gem_sanity_check.py        FBA sanity check on the existing P. ostreatus GEMs
data/taxon_inventory.csv           output of (1) — 73 rows, each tagged with evidence tier
data/gem_sanity_check.csv          output of (2)
FINDINGS.md                        milestone 1 write-up
```

## Reproducing

```bash
pip install cobra
cd code
python3 01_build_taxon_inventory.py
python3 02_gem_sanity_check.py
```
