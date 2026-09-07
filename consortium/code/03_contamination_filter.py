"""
Milestone 1, prerequisite fix: replace the ad hoc genus-level literature
guesses in 01_build_taxon_inventory.py's real_sequencing rows with an actual
matched reference list. See ../data/CONTAMINATION_SOURCES.md for the three
sources and their caveats -- this is a screen, not a proof; a genus match
means "known to behave as a contaminant somewhere," not "this detection was
definitely contamination."

Reads:  ../data/taxon_inventory.csv          (output of 01_)
        ../data/ref_salter2014_kitome_genera.csv
Writes: ../data/taxon_inventory_filtered.csv
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

INVENTORY_IN = DATA / "taxon_inventory.csv"
SALTER_CSV = DATA / "ref_salter2014_kitome_genera.csv"
OUT = DATA / "taxon_inventory_filtered.csv"

# Bashir et al. 2016 (spacecraft cleanroom) -- narrow, only what that paper's
# headline finding actually supports, not a general cleanroom catalog.
NASA_CLEANROOM_GENERA = {"Acinetobacter", "Escherichia", "Legionella"}

# Dewhirst et al. 2010 / HOMD -- core human oral genera.
ORAL_GENERA = {"Streptococcus", "Veillonella", "Neisseria", "Actinomyces",
               "Rothia", "Granulicatella", "Porphyromonas"}

# Post-2014 reclassifications: match the modern genus name used in our real
# data against the pre-2016 name Salter et al. used.
GENUS_SYNONYMS = {"Cutibacterium": "Propionibacterium"}


def load_salter_genera():
    genera = {}
    with open(SALTER_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            genera[row["genus"]] = row["taxon_group"]
    return genera


def genus_of(taxon_name):
    return taxon_name.split()[0] if taxon_name else ""


def classify(genus, salter_genera):
    lookup = GENUS_SYNONYMS.get(genus, genus)
    flags = []
    if lookup in salter_genera:
        flags.append(f"kitome_match(Salter2014:{salter_genera[lookup]})")
    if genus in NASA_CLEANROOM_GENERA:
        flags.append("nasa_cleanroom_match(Bashir2016)")
    if genus in ORAL_GENERA:
        flags.append("oral_commensal_match(Dewhirst2010)")
    return flags


def main():
    salter_genera = load_salter_genera()
    rows = list(csv.DictReader(open(INVENTORY_IN, newline="", encoding="utf-8")))

    out_rows = []
    n_real = n_flagged = n_candidate = 0
    for row in rows:
        row = dict(row)
        if row["data_provenance"] != "real_sequencing":
            # illustrative_model and real_gem rows pass through unfiltered --
            # this filter is specifically for the real detection events that
            # milestone 1 could not yet tell apart from contamination.
            row["contamination_flags"] = ""
            row["consortium_candidate"] = ""
            out_rows.append(row)
            continue

        n_real += 1
        genus = genus_of(row["taxon"])
        flags = classify(genus, salter_genera)
        row["contamination_flags"] = ";".join(flags) if flags else ""
        is_candidate = len(flags) == 0 and genus != ""
        row["consortium_candidate"] = str(is_candidate)
        if flags:
            n_flagged += 1
        if is_candidate:
            n_candidate += 1
        out_rows.append(row)

    fieldnames = list(rows[0].keys()) + ["contamination_flags", "consortium_candidate"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"real_sequencing taxa checked: {n_real}")
    print(f"flagged by >=1 reference source: {n_flagged} ({100*n_flagged/n_real:.0f}%)")
    print(f"surviving as consortium candidates (no flag, genus assignable): {n_candidate}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
