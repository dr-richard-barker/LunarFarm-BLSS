"""
Milestone 1 of the minimal-consortium module (see ../README.md): inventory every
real or candidate taxon for the game's compartments (digester, nitrifying
bioreactor, fungal crop rotation, mealworm tier) from sibling repos, and flag
each row's evidence tier honestly rather than treating all sources as equal.

Requires sibling checkouts, same convention as the game itself:
    ../../osdr-plant-microbiome
    ../../Microbiome_of_seedlings_in_space
    ../../Myco_tissue_RNAseq

Evidence tiers (see FINDINGS.md for the reasoning behind each call):
    real_sequencing     - detected by an actual sequencing/tool run against
                          real reads (MetaPhlAn output, UpSet taxon matrix)
    illustrative_model  - osdr-plant-microbiome's own `data_provenance` flag;
                          a deterministic demo standing in for real feature
                          tables that have not been ingested yet (see that
                          repo's docs/DATA_DICTIONARY.md and
                          data/processed/GUILD_METHOD.md)
    real_gem            - a real, already-built genome-scale metabolic model
                          exists for this organism
"""
import csv
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent  # .../Documents
OUT = HERE.parent / "data" / "taxon_inventory.csv"

MICROBIOME_SEEDLINGS = ROOT / "Microbiome_of_seedlings_in_space"
OSDR_PLANT_MICROBIOME = ROOT / "osdr-plant-microbiome"
MYCO_TISSUE = ROOT / "Myco_tissue_RNAseq"

# Genus-level functional read, from established literature, used only to
# propose a candidate compartment / guild -- NOT a claim of strain-level
# confirmation. Flag stays "literature_genus_role" wherever this is the only
# evidence for the call.
GENUS_ROLE = {
    "Cutibacterium": ("uncertain", "human skin commensal; likely handling/cleanroom signal, not a plant colonizer"),
    "Escherichia": ("uncertain", "human/animal gut commensal; likely handling signal"),
    "Streptococcus": ("uncertain", "human oral/skin commensal; likely handling signal"),
    "Veillonella": ("uncertain", "human oral commensal; likely handling signal"),
    "Rothia": ("uncertain", "human oral commensal; likely handling signal"),
    "Neisseria": ("uncertain", "human oral commensal; likely handling signal"),
    "Porphyromonas": ("uncertain", "human oral commensal; likely handling signal"),
    "Granulicatella": ("uncertain", "human oral commensal; likely handling signal"),
    "Actinomyces": ("uncertain", "human oral commensal; likely handling signal"),
    "Herbaspirillum": ("nitrifying_bioreactor", "genuine diazotrophic plant endophyte genus (real N2-fixing capability)"),
    "Bradyrhizobium": ("nitrifying_bioreactor", "genuine diazotrophic rhizobial genus (real N2-fixing capability)"),
    "Rhizobium": ("nitrifying_bioreactor", "genuine diazotrophic rhizobial genus (real N2-fixing capability)"),
    "Agrobacterium": ("plant_host_risk", "contains real phytopathogenic species (e.g. crown gall); crop risk"),
    "Rhodococcus": ("plant_host_risk", "R. fascians causes real fasciation disease in plants; crop risk"),
    "Ralstonia": ("plant_host_risk", "contains real phytopathogenic species; also a known ultrapure-water/lab contaminant genus"),
    "Pseudomonas": ("digester_or_nitrifying", "metabolically versatile genus; some species genuine plant-growth-promoters, others opportunists"),
    "Acidovorax": ("digester_or_nitrifying", "environmental/freshwater genus, denitrification-capable in some species"),
    "Curvibacter": ("digester_or_nitrifying", "environmental freshwater genus"),
    "Cloacibacterium": ("digester_or_nitrifying", "genus first described from wastewater/anaerobic digester sludge"),
    "Cupriavidus": ("digester_or_nitrifying", "metabolically versatile, some species used industrially for bioplastic/waste processing"),
    "Acinetobacter": ("uncertain", "environmental genus, some species opportunistic human pathogens"),
}


def load_real_upsettr_taxa():
    """Real per-study/condition species presence from actual MetaPhlAn-derived
    UpSet input. Returns list of (species, n_studies_or_conditions_detected_in)."""
    path = MICROBIOME_SEEDLINGS / "Plants in space microbiome - upsettr.csv"
    alt = MICROBIOME_SEEDLINGS / "Plants_in_space_microbiome - upsettr.csv"
    target = path if path.exists() else alt
    if not target.exists():
        return []
    counts = Counter()
    with open(target, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            for v in row:
                # source file mixes "Genus species" and "Genus_species" for
                # the same taxon across columns -- normalize before counting,
                # otherwise the same species can land on both sides of the
                # contamination filter under two different spellings.
                v = " ".join(v.replace("_", " ").split())
                if v:
                    counts[v] += 1
    return counts.most_common()


def genus_of(species_name):
    return species_name.split()[0] if species_name else ""


def main():
    rows = []

    # --- Tier 1: real sequencing-derived detections -----------------------
    for species, n in load_real_upsettr_taxa():
        genus = genus_of(species)
        role, note = GENUS_ROLE.get(genus, ("uncertain", "no genus-level literature read applied yet"))
        rows.append({
            "taxon": species,
            "level": "species",
            "source_repo": "Microbiome_of_seedlings_in_space",
            "source_detail": "real MetaPhlAn taxonomic profiling, UpSet input across OSDR-37/120/522/OSD-217",
            "data_provenance": "real_sequencing",
            "n_study_conditions_detected": n,
            "candidate_compartment": role,
            "note": note,
        })

    # --- Tier 2: osdr-plant-microbiome's own illustrative-model genera ----
    # Explicitly NOT treated as confirmed real detections -- see that repo's
    # data/processed/GUILD_METHOD.md: "Scores here are illustrative until
    # primary feature tables are ingested."
    guild_csv = OSDR_PLANT_MICROBIOME / "data" / "processed" / "guild_scores.csv"
    if guild_csv.exists():
        with open(guild_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                genus = row["genus"]
                role, note = GENUS_ROLE.get(genus, (row.get("guild_call", "uncertain"), "osdr-plant-microbiome guild-inference call"))
                rows.append({
                    "taxon": genus,
                    "level": "genus",
                    "source_repo": "osdr-plant-microbiome",
                    "source_detail": f"guild_call={row.get('guild_call')}, confidence={row.get('confidence')}",
                    "data_provenance": "illustrative_model",
                    "n_study_conditions_detected": "",
                    "candidate_compartment": role,
                    "note": note + " -- PLACEHOLDER DATA, not yet a real ingested OSDR feature table",
                })

    # --- Tier 3: real GEM already built ------------------------------------
    rows.append({
        "taxon": "Pleurotus ostreatus (cv. Harbor Blue P01)",
        "level": "species",
        "source_repo": "Myco_tissue_RNAseq",
        "source_detail": "real mycoponic ceramic-tube culture (Porterfield et al. 2026); real tissue RNA-seq; real GEM (PC9.15/BOM_ss5, gapfilled + medium-constrained)",
        "data_provenance": "real_gem",
        "n_study_conditions_detected": "",
        "candidate_compartment": "fungal_crop_rotation",
        "note": "the only organism in this inventory with both a real physical BLSS-relevant culture system and a runnable metabolic model",
    })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["taxon", "level", "source_repo", "source_detail", "data_provenance",
                  "n_study_conditions_detected", "candidate_compartment", "note"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
