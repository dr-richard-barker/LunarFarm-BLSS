# Minimal consortium — milestone 1 findings

Taxon inventory (73 rows) built from real sequencing output, one explicitly-flagged
illustrative-model source, and one real genome-scale metabolic model (GEM), plus a
sanity check on that GEM. Reproducible via `code/01_build_taxon_inventory.py` and
`code/02_gem_sanity_check.py`.

## 1. The real taxonomic signal across 8 OSDR studies is dominated by human-associated genera, not confirmed plant endophytes

`Microbiome_of_seedlings_in_space`'s UpSet input is real MetaPhlAn output — actual
sequencing reads processed against real reads, not illustrative data — spanning
19 study/genotype/condition columns across OSDR-37, OSDR-120, OSDR-522 and OSD-217
(Arabidopsis ecotypes Col-0/Cvi-0/WS-2/Ler-0/PhyD, flight vs. ground, light vs. dark).
Of 52 unique species, the single most recurrent is *Cutibacterium acnes*
(15 of 19 columns) — a human skin commensal. *E. coli*, *Streptococcus*,
*Veillonella*, *Rothia*, *Neisseria*, *Porphyromonas*, *Granulicatella* and
*Actinomyces* show the same pattern. 9 of the ~20 recurring genera are tagged
`uncertain` in the inventory for exactly this reason: a genuine plant-endophyte
signal has to be separated from handling/cleanroom contamination before any of
this can inform a consortium design, and this milestone does not attempt that
separation — it flags the need honestly instead of guessing.

## 2. A smaller set of taxa are plausible genuine spaceflight plant commensals or pathogens, by established genus-level biology

*Herbaspirillum huttiense* (9/19 columns) and *Bradyrhizobium viridifuturi*
(3/19) are real diazotrophic (nitrogen-fixing) genera — plausible genuine
members of a nitrogen-cycling compartment. *Agrobacterium tumefaciens* (7/19),
*Ralstonia pickettii*/*insidiosa* (8+3/19) and *Rhodococcus fascians* (2/19)
all include real phytopathogenic species — a crop-risk list, not a
candidate-member list. These calls are genus-level literature reads, not
strain-level confirmation (see `osdr-plant-microbiome`'s own stated caveat
about needing ASV/strain resolution — the same limitation applies here).

## 3. `osdr-plant-microbiome`'s own genus/guild data is explicitly a placeholder, not yet real

That repo's own docs (`data/processed/GUILD_METHOD.md`,
`docs/DATA_DICTIONARY.md`) flag every abundance value as
`data_provenance = illustrative_model` — "a deterministic ecological model
(demo; replace with real data)" — pending real OSDR feature-table ingestion,
still an open item on that repo's own roadmap. It's kept in this inventory for
the guild-classification *method*, which is real and reusable, but every row
from it is tagged `illustrative_model` and should not be read as confirmed
spaceflight microbiome composition.

## 4. The one real GEM in the portfolio grows under its unconstrained variant; its medium-constrained variant is broken, not merely restrictive

FBA on all four existing GEM files (`Myco_tissue_RNAseq/models/*.xml`,
*Pleurotus ostreatus*):

| model | reactions | has biomass reaction | objective | growth flux |
|---|---|---|---|---|
| PC9.15_gapfilled | 5,414 | yes | `BIOMASS_fungal` | 125 (uncalibrated) |
| PC9.15_medium | 5,410 | **no** | none (`0`) | not meaningful |
| BOM_ss5_gapfilled | 5,247 | yes | `BIOMASS_fungal` | 125 (uncalibrated) |
| BOM_ss5_medium | 5,243 | **no** | none (`0`) | not meaningful |

Both `_gapfilled` variants carry an intact objective — the biomass reaction
itself is self-labeled `"Coarse fungal biomass (uncurated)"` in the model, so
125 is not yet a calibrated growth rate, just a nonzero feasible flux. Both
`_medium` variants are **missing the biomass reaction/objective link
entirely** — cobrapy reports "No objective coefficients in model" and finds
zero reactions matching `biomass` by name. This is a model-building defect in
how the medium-constrained variant was derived from the gapfilled one (4–5
reactions were dropped, apparently including the objective), not a biological
"doesn't grow in this medium" result. It needs a fix in `Myco_tissue_RNAseq`
itself before any co-culture screen can use the medium-constrained model.

## What this means for milestone 3

The real, usable evidence right now is thinner than the roadmap doc assumed:
one real GEM (only half-usable as shipped), and a taxon list where more
entries are "uncertain / likely contamination" than "candidate consortium
member." Two prerequisites before the flux-balance co-culture screen:

1. Fix the `_medium` GEM variants in `Myco_tissue_RNAseq` (restore the
   biomass objective link).
2. Narrow the real taxon list with an actual contamination filter (e.g.
   comparison against a reagent/cleanroom contaminant reference list) instead
   of genus-level literature guesses.

No consortium composition claim is made at this milestone.
