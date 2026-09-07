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

## 4. Correction: the one real GEM in the portfolio is not broken — `_medium.xml` is a superseded intermediate, and `_gapfilled.xml` is the real medium-constrained model

The original version of this finding claimed the `*_medium.xml` files were
missing their biomass objective due to a build defect. That was a
misdiagnosis on this module's part, caught after reading
`Myco_tissue_RNAseq/NOTES.md` §10b and §14 and its pipeline scripts directly
rather than just probing the SBML files. The real story:

`16_gem_medium.py` builds `*_medium.xml` as a **connectivity diagnostic
only** — its own docstring says so explicitly: "It does NOT claim a
validated growth prediction. There is still no curated biomass objective."
`26_gem_gapfill_targeted.py` then reads `*_medium.xml` as *input*
(`--model` defaults to it), gapfills the remaining blocked cofactor
precursors, constructs a fresh `BIOMASS_fungal` reaction, sets it as the
objective, and writes `*_gapfilled.xml` — which is therefore the medium
constraint *and* a working objective, not a separate unconstrained variant.
`*_medium.xml` was never meant to carry flux on its own; it's a pipeline
stage, not a deliverable.

FBA on all four files, corrected reading:

| model | reactions | has biomass reaction | objective | growth flux |
|---|---|---|---|---|
| PC9.15_gapfilled | 5,414 | yes | `BIOMASS_fungal` | 125 (uncalibrated, on MNM v3 medium) |
| PC9.15_medium | 5,410 | no (by design — pipeline input, not a deliverable) | none (`0`) | not applicable |
| BOM_ss5_gapfilled | 5,247 | yes | `BIOMASS_fungal` | 125 (uncalibrated, on MNM v3 medium) |
| BOM_ss5_medium | 5,243 | no (by design — pipeline input, not a deliverable) | none (`0`) | not applicable |

The growth flux of 125.0 for both references is not a new result — it
independently reproduces `Myco_tissue_RNAseq/NOTES.md` §14c's own reported
number exactly, which is a genuine (if small) cross-validation rather than a
new finding. `Myco_tissue_RNAseq`'s README and a new `models/README.md` have
since been updated upstream to make this explicit, so the next reader
doesn't repeat this mistake.

## What this means for milestone 3

The real, usable evidence is better than the corrected finding above implies
for the GEM side — `*_gapfilled.xml` is a working, medium-constrained model,
no upstream fix needed — but the taxon side still has the real problem from
findings 1–3: more entries are "uncertain / likely contamination" than
"candidate consortium member." One prerequisite remains before the
flux-balance co-culture screen:

1. Narrow the real taxon list with an actual contamination filter (e.g.
   comparison against a reagent/cleanroom contaminant reference list) instead
   of genus-level literature guesses.
2. ~~Fix the `_medium` GEM variants in `Myco_tissue_RNAseq`~~ — resolved:
   there was nothing to fix; use `*_gapfilled.xml` directly.

No consortium composition claim is made at this milestone.
