"""
Milestone 1, part 2: does the one real genome-scale metabolic model already in
the portfolio (Myco_tissue_RNAseq's Pleurotus ostreatus GEM) actually grow?

This is a sanity check, not a consortium screen -- it has to pass before any
co-culture flux-balance work (milestone 3) is worth attempting. Requires
`pip install cobra` and a sibling checkout of Myco_tissue_RNAseq.

Note: the two *_medium.xml files are EXPECTED to report no biomass reaction
and no objective -- that's not a defect, it's a pipeline intermediate (see
Myco_tissue_RNAseq/models/README.md). Use *_gapfilled.xml for anything that
needs a working objective; it already carries the same medium constraints.
"""
import csv
import warnings
from pathlib import Path

import cobra

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent  # .../Documents
MODELS_DIR = ROOT / "Myco_tissue_RNAseq" / "models"
OUT = HERE.parent / "data" / "gem_sanity_check.csv"

MODEL_FILES = ["PC9.15_gapfilled", "PC9.15_medium", "BOM_ss5_gapfilled", "BOM_ss5_medium"]


def main():
    rows = []
    for name in MODEL_FILES:
        path = MODELS_DIR / f"{name}.xml"
        if not path.exists():
            rows.append({"model": name, "status": "FILE_NOT_FOUND"})
            continue
        model = cobra.io.read_sbml_model(str(path))
        biomass_rxns = [r for r in model.reactions if "biomass" in r.id.lower()]
        has_biomass = len(biomass_rxns) > 0
        # cobrapy warns "No objective coefficients in model" when the fbc
        # objective link is missing/broken; solution.objective_value is not
        # meaningful in that case even when solver status says "optimal".
        solution = model.optimize()
        rows.append({
            "model": name,
            "reactions": len(model.reactions),
            "metabolites": len(model.metabolites),
            "genes": len(model.genes),
            "has_biomass_reaction": has_biomass,
            "objective_expression": str(model.objective.expression),
            "fba_status": solution.status,
            "growth_flux": round(solution.objective_value, 6) if solution.objective_value is not None else "",
            "growth_flux_meaningful": has_biomass and str(model.objective.expression) != "0",
        })
        print(f"{name}: {rows[-1]}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["model", "reactions", "metabolites", "genes", "has_biomass_reaction",
                  "objective_expression", "fba_status", "growth_flux", "growth_flux_meaningful"]
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nwrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
