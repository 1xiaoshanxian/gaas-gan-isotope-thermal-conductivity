"""Shared helpers for supplementary figures drawn from the public tables."""
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import figsty
from plot_config import MAIN_DATA, SUPPLEMENTARY_DATA
from plot_output import save_figure

figsty.apply()
COLORS = {"L": "#2466a8", "U": "#d18326", "D": "#b42c48", "H": "#309479"}
MECHANISMS = SUPPLEMENTARY_DATA / "S12-S21_phonon_mechanisms"
VALIDATION = SUPPLEMENTARY_DATA / "S03-S08_validation"
TRANSPORT = SUPPLEMENTARY_DATA / "S09-S11_transport_comparisons"
BETA = SUPPLEMENTARY_DATA / "S22-S25_beta-Ga2O3"


def table(directory, name):
    return pd.read_csv(directory / name)


def gap(ax):
    ax.axvspan(9.708756932239803, 14.956285787709312, color="0.92", zorder=0)


def finish(fig, name, rect=None):
    fig.tight_layout(pad=1.3, rect=rect)
    save_figure(fig, name, dpi=300)


def dispatch(functions):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figures", nargs="+", choices=tuple(functions),
                        help="Figure IDs to generate; default: all in this script.")
    args = parser.parse_args()
    for name in args.figures or functions:
        functions[name]()
        print("Generated " + name, flush=True)
