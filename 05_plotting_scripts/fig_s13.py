# -*- coding: utf-8 -*-
"""SI Fig. S13 (redraw): frequency-resolved U/D conductivity, isotope loss and half-widths, GaN zz 300 K."""
import csv
import numpy as np
import matplotlib.pyplot as plt
import figsty as S

from plot_config import SUPPLEMENTARY_DATA
from plot_output import save_figure

SRC = SUPPLEMENTARY_DATA / "S12-S21_phonon_mechanisms/GaN_spectral_isotope_300K.csv"
GAP = (9.708756932239803, 14.956285787709312)

rows = [r for r in csv.DictReader(open(SRC, encoding="utf-8-sig")) if r["direction"] == "zz"]
for r in rows:
    for k in ("f_lo", "f_hi", "kappaU", "kappaD", "dkappa",
              "gamma3ph_qweighted_median", "gamma_iso_qweighted_median"):
        r[k] = float(r[k])
    r["n_modes"] = int(r["n_modes"])
rows.sort(key=lambda r: r["f_lo"])
f = np.array([(r["f_lo"] + r["f_hi"]) / 2 for r in rows])
kU = np.array([r["kappaU"] for r in rows])
kD = np.array([r["kappaD"] for r in rows])
dk = kU - kD
g3 = np.array([r["gamma3ph_qweighted_median"] for r in rows])
gi = np.array([r["gamma_iso_qweighted_median"] for r in rows])
ok = np.array([r["n_modes"] > 0 for r in rows])

cum = np.cumsum(np.where(ok, dk, 0.0)) / dk[ok].sum()

S.apply()
fig, axes = plt.subplots(3, 1, figsize=(S.W, 6.2))
fig.subplots_adjust(left=0.155, right=0.875, top=0.945, bottom=0.085, hspace=0.42)

ax = axes[0]
ax.step(f, np.where(ok, kU, np.nan), where="mid", color="#1f77b4", lw=1.4, label=r"$\kappa_{U,\ zz}$")
ax.step(f, np.where(ok, kD, np.nan), where="mid", color="#ff7f0e", lw=1.4, label=r"$\kappa_{D,\ zz}$")
ax.set_ylabel(r"Conductivity per 0.5 THz" + "\n" + r"(W m$^{-1}$ K$^{-1}$)", labelpad=2)
ax.legend(frameon=False, loc="upper right", handlelength=1.8)
ax.set_title("(a) GaN, zz, 300 K", pad=3, loc="left")

ax = axes[1]
ax.bar(f, dk, width=0.42, color="0.45", edgecolor="none", label=r"$\kappa_U-\kappa_D$ per bin")
ax.set_ylabel(r"Disorder loss per bin" + "\n" + r"(W m$^{-1}$ K$^{-1}$)", labelpad=2)
ax2 = ax.twinx()
ax2.plot(f, cum, "-o", ms=2.6, lw=1.4, color="#d62728", label="cumulative fraction")
ax2.set_ylim(-0.02, 1.08)
ax2.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax2.set_ylabel("Cumulative loss fraction", color="#d62728", labelpad=3)
ax2.tick_params(axis="y", colors="#d62728")
ax2.spines["right"].set_color("#d62728")
ax.set_title("(b) cumulative loss from low frequency", pad=3, loc="left")

ax = axes[2]
m = ok
ax.semilogy(f[m], g3[m], "-o", ms=2.4, lw=1.3, color="#1f77b4", label="three-phonon")
mi = m & np.isfinite(gi) & (gi > 0)
ax.semilogy(f[mi], gi[mi], "-s", ms=2.4, lw=1.3, color="#2ca02c", label="isotope")
ax.set_ylabel("$q$-weighted median\nhalf-width (THz)", labelpad=2)
ax.legend(frameon=False, loc="upper left", handlelength=1.8)
ax.set_title("(c) U-state half-widths", pad=3, loc="left")

for i, ax in enumerate(axes):
    ax.axvspan(GAP[0], GAP[1], color="0.90", zorder=0)
    ax.set_xlim(0, 21.5)
    ax.set_xlabel("Frequency (THz)", labelpad=1.5)

save_figure(fig, "FigS13", dpi=600)
