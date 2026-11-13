# -*- coding: utf-8 -*-
"""Shared plotting style for the redrawn SI figures (larger fonts, 14.65 cm print width)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, MaxNLocator

# final printed width is 14.65 cm = 5.77 in
W = 5.77

RC = {
    "font.family": "DejaVu Sans",
    "font.size": 9.5,
    "axes.labelsize": 9.5,
    "axes.titlesize": 9.5,
    "xtick.labelsize": 8.8,
    "ytick.labelsize": 8.8,
    "legend.fontsize": 8.4,
    "axes.linewidth": 0.9,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "xtick.major.size": 3.6,
    "xtick.major.width": 0.85,
    "ytick.major.size": 3.6,
    "ytick.major.width": 0.85,
    "xtick.minor.size": 2.0,
    "ytick.minor.size": 2.0,
    "xtick.minor.visible": True,
    "ytick.minor.visible": True,
    "axes.unicode_minus": False,
    "savefig.dpi": 600,
    "figure.dpi": 110,
}


def apply():
    plt.rcParams.update(RC)


def panel(ax, letter, dx=0.028, dy=0.955):
    ax.text(dx, dy, f"({letter})", transform=ax.transAxes, ha="left", va="top",
            fontsize=9.5, fontweight="bold")
