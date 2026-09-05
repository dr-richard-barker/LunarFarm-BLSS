"""Shared plotting style. One ink colour, one accent, hairline rules — the
figures are meant to be read, not admired."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIGS = ROOT / "results" / "figures"
TABLES = ROOT / "results" / "tables"
FIGS.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

INK = "#1d2733"
SOFT = "#68788c"
ACCENT = "#2f6f9e"       # the compartment under test
WARN = "#b4652a"
GOOD = "#2f7a49"
GRID = "#d8e0e8"

def setup():
    plt.rcParams.update({
        "figure.dpi": 140, "savefig.dpi": 200, "savefig.bbox": "tight",
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 9, "axes.titlesize": 10.5, "axes.labelsize": 9,
        "axes.edgecolor": SOFT, "axes.linewidth": 0.7, "axes.labelcolor": INK,
        "axes.spines.top": False, "axes.spines.right": False,
        "text.color": INK, "xtick.color": SOFT, "ytick.color": SOFT,
        "xtick.labelsize": 8, "ytick.labelsize": 8,
        "grid.color": GRID, "grid.linewidth": 0.6,
        "legend.frameon": False, "legend.fontsize": 8,
        "figure.facecolor": "white", "axes.facecolor": "white",
    })

def save(fig, name):
    p = FIGS / name
    fig.savefig(p)
    plt.close(fig)
    print("  wrote results/figures/" + name)
