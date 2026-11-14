# -*- coding: utf-8 -*-
"""SI Fig. S22 (redraw): beta-Ga2O3 isotope response under the L/U/D protocol."""
import csv
import numpy as np
import matplotlib.pyplot as plt
import figsty as S

from plot_config import SUPPLEMENTARY_DATA
from plot_output import save_figure

RES = SUPPLEMENTARY_DATA / "S22-S25_beta-Ga2O3"

COL = {"L": "#0072ff", "U": "#8a8f98", "D": "#ff3d00",
       "tot": "#20242b", "am": "#00a05a", "dis": "#ff3d00",
       "xx": "#20242b", "yy": "#0072ff", "zz": "#ff3d00", "avg": "#8a8f98"}

tens = list(csv.DictReader(open(RES / "Ga2O3_kappa_tensor.csv", encoding="utf-8-sig")))
deco = list(csv.DictReader(open(RES / "Ga2O3_isotope_decomposition.csv", encoding="utf-8-sig")))
for r in tens:
    for k, v in list(r.items()):
        if k not in ("state",):
            r[k] = float(v)
for r in deco:
    for k, v in list(r.items()):
        if k != "direction":
            r[k] = float(v)

T = sorted({r["T_K"] for r in tens})


def kt(Tv, st, comp):
    for r in tens:
        if abs(r["T_K"] - Tv) < 1e-6 and r["state"] == st:
            return r["k_" + comp]
    raise KeyError((Tv, st, comp))


def dc(Tv, d, col):
    for r in deco:
        if abs(r["T_K"] - Tv) < 1e-6 and r["direction"] == d:
            return r[col]
    raise KeyError((Tv, d, col))


S.apply()
fig, axes = plt.subplots(2, 2, figsize=(S.W, 5.3))
fig.subplots_adjust(left=0.105, right=0.985, top=0.905, bottom=0.115, wspace=0.30, hspace=0.46)

# (a) L-state diagonal components
ax = axes[0, 0]
for comp, lab in (("xx", r"$\kappa_{xx}$"), ("yy", r"$\kappa_{yy}$"), ("zz", r"$\kappa_{zz}$")):
    ax.semilogy(T, [kt(t, "L", comp) for t in T], "-o", ms=2.6, lw=1.4, color=COL[comp], label=lab)
ax.semilogy(T, [kt(t, "L", "avg") for t in T], "--s", ms=2.6, lw=1.3, mfc="white",
            color=COL["avg"], label=r"$\kappa_{\rm avg}$")
ax.set_xlim(50, 870)
ax.set_ylim(4.5, 150)
ax.set_yticks([5, 10, 20, 50, 100])
ax.set_yticklabels(["5", "10", "20", "50", "100"])
ax.set_xlabel("Temperature (K)", labelpad=1.5)
ax.set_ylabel(r"$\kappa$ (W m$^{-1}$ K$^{-1}$)", labelpad=2)
ax.set_title("(a) state L", pad=3, loc="left")
ax.legend(frameon=False, loc="upper right", handlelength=1.6, fontsize=7.8)

# (b) 300 K components for L, U, D
ax = axes[0, 1]
xc = np.arange(4)
wid = 0.25
comps = ["xx", "yy", "zz", "avg"]
for n, st in enumerate(("L", "U", "D")):
    ax.bar(xc + (n - 1) * wid, [kt(300.0, st, c) for c in comps], wid,
           color=COL[st], edgecolor="white", lw=0.5, label=st)
for k, comp in enumerate(comps):
    red = (kt(300.0, "L", comp) - kt(300.0, "D", comp)) / kt(300.0, "L", comp) * 100
    ax.text(xc[k], 22.4, "-%.1f%%" % red, ha="center", va="bottom", fontsize=7.4)
ax.set_xticks(xc)
ax.set_xticklabels([r"$\kappa_{xx}$", r"$\kappa_{yy}$", r"$\kappa_{zz}$", r"$\kappa_{\rm avg}$"], fontsize=8.4)
ax.set_ylim(0, 30.5)
ax.set_yticks([0, 5, 10, 15, 20])
ax.set_ylabel(r"$\kappa$ at 300 K (W m$^{-1}$ K$^{-1}$)", labelpad=2)
ax.set_title("(b) 300 K", pad=3, loc="left")
ax.legend(frameon=False, loc="upper center", ncol=3, handlelength=1.1, columnspacing=1.0,
          handletextpad=0.35, fontsize=7.8, bbox_to_anchor=(0.5, 1.02))

# (c) contributions vs T (orientation average)
ax = axes[1, 0]
ax.plot(T, [dc(t, "avg", "total_reduction_pct") for t in T], "-o", ms=2.6, lw=1.5, color=COL["tot"], label="total")
ax.plot(T, [dc(t, "avg", "average_mass_pp") for t in T], "-s", ms=2.6, lw=1.4, color=COL["am"], label="average mass")
ax.plot(T, [dc(t, "avg", "disorder_pp") for t in T], "-^", ms=2.6, lw=1.4, color=COL["dis"], label="disorder")
ax.set_xlim(50, 870)
ax.set_ylim(-0.25, 7.6)
ax.set_xlabel("Temperature (K)", labelpad=1.5)
ax.set_ylabel("Contribution (%)", labelpad=2)
ax.set_title("(c) orientation average", pad=3, loc="left")
ax.legend(frameon=False, loc="upper right", handlelength=1.6, fontsize=7.8)

# (d) decomposition per direction at 300 K
ax = axes[1, 1]
amv = [dc(300.0, d, "average_mass_pp") for d in comps]
div = [dc(300.0, d, "disorder_pp") for d in comps]
ax.bar(xc, amv, 0.55, color=COL["am"], edgecolor="white", lw=0.5, label="average mass")
ax.bar(xc, div, 0.55, bottom=amv, color=COL["dis"], edgecolor="white", lw=0.5, label="disorder")
for k in range(4):
    ax.text(xc[k], amv[k] + div[k] + 0.04, "%.2f" % (amv[k] + div[k]), ha="center", va="bottom", fontsize=7.6)
ax.set_xticks(xc)
ax.set_xticklabels([r"$\kappa_{xx}$", r"$\kappa_{yy}$", r"$\kappa_{zz}$", r"$\kappa_{\rm avg}$"], fontsize=8.4)
ax.set_ylim(0, 2.35)
ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
ax.set_ylabel("Contribution at 300 K (%)", labelpad=2)
ax.set_title("(d) 300 K", pad=3, loc="left")
ax.legend(frameon=False, loc="upper left", handlelength=1.1, fontsize=7.6)

save_figure(fig, "FigS22", dpi=600)
