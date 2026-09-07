# Reference sources used by `03_contamination_filter.py`

Three real, cited reference sources, retrieved 2026-09-06, used to replace the
milestone-1 ad hoc "likely handling signal" literature guesses with an actual
matched reference list.

## 1. Reagent/lab contamination ("kitome") genera

Salter SJ, Cox MJ, Turek EM, et al. "Reagent and laboratory contamination can
critically impact sequence-based microbiome analyses." *BMC Biology*.
2014;12:87. [doi:10.1186/s12915-014-0087-z](https://doi.org/10.1186/s12915-014-0087-z)

90 genera identified as recurrent contaminants of DNA extraction kits and PCR
reagents in negative controls sequenced alongside real low-biomass samples —
the standard reference for this kind of filter. Full list in
[`ref_salter2014_kitome_genera.csv`](ref_salter2014_kitome_genera.csv),
extracted from the article (PMC4228153) on 2026-09-06. **Note:** the paper
predates the 2016 reclassification of *Propionibacterium acnes* to
*Cutibacterium acnes*; the filter script maps `Cutibacterium -> Propionibacterium`
for matching.

Caveat: this list is genus-level and was built from human/clinical-sample
studies. A genus match means "known to behave as a reagent contaminant
somewhere," not "this specific detection event in these plant samples was
contamination" — real environmental/plant-associated members of the same
genus do exist. Strain/ASV-level resolution against a real negative control
from the same OSDR studies would be the actual fix; this filter is a
screen, not a proof.

## 2. NASA spacecraft-assembly-cleanroom genera

Bashir M, Ahmed M, Weinmaier T, Ciobanu D, Ivanova N, Pieber TR, Vaishampayan P.
"Functional Metagenomics of Spacecraft Assembly Cleanrooms: Presence of
Virulence Factors Associated with Human Pathogens." *Frontiers in
Microbiology*. 2016;7:1321.
[doi:10.3389/fmicb.2016.01321](https://doi.org/10.3389/fmicb.2016.01321)

Reports *Acinetobacter* (specifically *A. baumannii*, *A. lwoffii*) as the
dominant genus (94-100% of the dominant family, Moraxellaceae) across real
NASA spacecraft assembly cleanroom samples, alongside *Escherichia coli* and
*Legionella pneumophila* present in all samples. Used narrowly here — only
these three genera are flagged as "NASA cleanroom match," not a full list,
because that's what this specific paper's headline finding actually
supports.

## 3. Human oral microbiome core genera

Dewhirst FE, Chen T, Izard J, et al. "The Human Oral Microbiome." *Journal of
Bacteriology*. 2010;192(19):5002-5017.
[doi:10.1128/JB.00542-10](https://doi.org/10.1128/JB.00542-10) — the source
behind the Human Oral Microbiome Database (HOMD).

*Streptococcus*, *Veillonella*, *Neisseria*, *Actinomyces*, *Rothia* and
*Granulicatella* are reported as core/abundant oral genera; *Porphyromonas*
is a well-established oral genus independent of this specific source (one of
the classic periodontal "red complex" taxa). Flagged separately from the
kitome list because it implies a different contamination *mechanism* —
human breath/saliva/skin during sample handling, not extraction-kit reagent
background — which matters for anyone trying to fix the actual lab protocol
later.
