# Minimal consortium — milestone 1 findings

Taxon inventory (72 rows) built from real sequencing output, one explicitly-flagged
illustrative-model source, and one real genome-scale metabolic model (GEM), plus a
sanity check on that GEM. Reproducible via `code/01_build_taxon_inventory.py` and
`code/02_gem_sanity_check.py`.

## 1. The real taxonomic signal across 8 OSDR studies matches known contamination reference lists more often than not — now checked, not guessed

`Microbiome_of_seedlings_in_space`'s UpSet input is real MetaPhlAn output — actual
sequencing reads processed against real reads, not illustrative data — spanning
19 study/genotype/condition columns across OSDR-37, OSDR-120, OSDR-522 and OSD-217
(Arabidopsis ecotypes Col-0/Cvi-0/WS-2/Ler-0/PhyD, flight vs. ground, light vs. dark).

`code/03_contamination_filter.py` checks each of the 51 real detected species
against three actual cited reference lists (full sources and caveats in
[`data/CONTAMINATION_SOURCES.md`](data/CONTAMINATION_SOURCES.md)) instead of the
genus-level literature guesses this finding originally relied on:

1. **Salter et al. 2014** (*BMC Biology*, doi:10.1186/s12915-014-0087-z) — the
   standard 90-genus reagent/DNA-extraction-kit contamination reference (the
   "kitome").
2. **Bashir et al. 2016** (*Frontiers in Microbiology*, doi:10.3389/fmicb.2016.01321)
   — real NASA spacecraft-assembly-cleanroom metagenomics; used narrowly for the
   3 genera (*Acinetobacter*, *Escherichia*, *Legionella*) that paper's own
   headline finding actually supports.
3. **Dewhirst et al. 2010** (*J Bacteriol*, doi:10.1128/JB.00542-10 / HOMD) —
   core human oral microbiome genera, flagged separately because it implies a
   different contamination mechanism (handling/breath, not reagent background).

**Result: 29 of 51 real detected species (57%) match at least one reference
list.** Of the 10 most recurrent species (detected in the most study/condition
columns, i.e. the strongest apparent signal), **8 are flagged**: *Cutibacterium
acnes* (15/19 columns, kitome), *Herbaspirillum huttiense* (9/19, kitome),
*Ralstonia pickettii* (8/19, kitome), *Pseudomonas chengduensis* and
*P. fluorescens* (8/19 each, kitome), *Curvibacter gracilis* (8/19, kitome),
*Escherichia coli* (7/19, kitome **and** independently the dominant real
NASA-cleanroom genus per Bashir et al.), *Acidovorax temperans* (7/19, kitome).
The strongest apparent signal in the dataset is, on the current evidence, more
consistent with reagent/handling contamination than with real plant
colonization — a real and useful negative result, not a data-quality failure
to route around.

Full per-taxon flags: [`data/taxon_inventory_filtered.csv`](data/taxon_inventory_filtered.csv).

## 2. Two named species survive the filter — one thematically apt, one a real crop-risk pathogen, neither yet a validated consortium member

Only 22 of 51 real species carry no reference-list flag, and 20 of those are
singleton detections (1/19 columns) with too little recurrence to weigh
either way. The two exceptions:

- ***Cloacibacterium caeni*** (8/19 columns, unflagged) — a genus first
  described from wastewater/anaerobic-digester sludge. It's the single
  strongest surviving real signal in the whole inventory, and it happens to
  map thematically onto the game's digester compartment. That's suggestive,
  not confirmed — a name matching a compartment is not the same as a
  metabolic-capability match, and this is genus-level, not strain-level.
- ***Agrobacterium tumefaciens*** (7/19 columns, unflagged by these three
  lists) — a real phytopathogen (crown gall disease); this belongs on a
  "must exclude or monitor" list, not a candidate-member list, despite
  passing the contamination filter.

*Bradyrhizobium viridifuturi* (3/19) and *Ralstonia pickettii*/*insidiosa*
(8+3/19) — flagged here as genuine diazotrophic and phytopathogenic genera
respectively in the previous version of this finding — are **both also on
the Salter kitome list**, which is itself informative: real
environmental/plant-associated organisms and reagent contaminants overlap
heavily by genus, because extraction kits are manufactured using
environmental water sources. A genus's real biological capability (e.g.
nitrogen fixation) does not clear it of a contamination flag; the two
questions are independent, and both matter before treating a detection as
a candidate consortium member.

All of these calls remain genus-level, not strain/ASV-level — see
`osdr-plant-microbiome`'s own stated caveat about needing that resolution;
the same limitation applies here, and a real negative-control comparison
from the same OSDR studies (not attempted here) is the only way to actually
resolve it rather than screen for it.

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

Both milestone-1 prerequisites are now resolved:

1. ~~Narrow the real taxon list with an actual contamination filter~~ —
   done: 29 of 51 real species (57%) flagged against three cited reference
   lists (finding 1); only *Cloacibacterium caeni* and *Agrobacterium
   tumefaciens* survive with any real recurrence, and the latter is a
   pathogen risk, not a candidate.
2. ~~Fix the `_medium` GEM variants in `Myco_tissue_RNAseq`~~ — resolved:
   there was nothing to fix; use `*_gapfilled.xml` directly (finding 4).

But resolving the prerequisites surfaced a harder problem than either one
individually: **there is currently one (1) real, non-pathogen, non-flagged
bacterial candidate with meaningful recurrence** (*C. caeni*), and **one**
real fungal partner with a working GEM (*P. ostreatus*, from a physical
mycoponic culture system, not a spaceflight sample at all). That is not
enough real, trustworthy taxa to run a meaningful flux-balance co-culture
screen — milestone 3 as originally scoped (screen a real multi-taxon pool
for a minimal viable consortium) would currently be screening a pool of
essentially one bacterium and one fungus, which answers a different,
smaller question than "what's the minimal consortium."

Revised options for milestone 3, in place of the original scope:

- **(a) Narrow scope honestly**: run the flux-balance pairing of just
  *C. caeni* + *P. ostreatus* as a two-organism proof of concept, reporting
  it as exactly that rather than a "minimal consortium."
- **(b) Get a real negative control**: the actual fix for finding 1's
  genus-level uncertainty is a real negative-control comparison from the
  same OSDR studies (an extraction blank run through the same MetaPhlAn
  pipeline) — not attempted here, and the only way to move species currently
  sitting in "uncertain" back into "candidate" with confidence.
- **(c) Widen the real-data search**: `osdr-plant-microbiome`'s "Ingest real
  OSDR feature tables" item is still on that repo's own roadmap
  (finding 3) — if that ships, it would be a second real bacterial source
  independent of `Microbiome_of_seedlings_in_space`, worth re-running this
  filter against.

No consortium composition claim is made at this milestone.
