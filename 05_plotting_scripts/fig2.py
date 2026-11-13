# -*- coding: utf-8 -*-
"""Plot the mean GaAs SHC spectra at 150 K and 300 K.

The shaded mean-spectrum difference at 150 K highlights the main loss range.
The integrated difference at 300 K is statistically unresolved. Inputs are the
archived mean spectra of the selected GaAs runs."""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from figure_layout import FIGSIZE, MAIN_RECT, SECOND_RECT

from plot_config import MAIN_DATA
from plot_output import save_figure

spectrum = pd.read_csv(MAIN_DATA / "gaas_shc_spectra_150_300K.csv")

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9.5,
                     'axes.labelsize': 9.5, 'axes.titlesize': 9.5,
                     'xtick.labelsize': 8.5, 'ytick.labelsize': 8.5,
                     'legend.fontsize': 8, 'axes.linewidth': .8,
                     'svg.fonttype': 'none', 'pdf.fonttype': 42})
CU, CD, LOSS = '#D18326', '#B42C48', '#B42C48'

fig = plt.figure(figsize=FIGSIZE)
axs = [fig.add_axes(MAIN_RECT), fig.add_axes(SECOND_RECT)]
y_limits = {150: 46.0, 300: 22.0}
for j, temp in enumerate([150, 300]):
    ax = axs[j]
    z = {}
    for state in ('U', 'D'):
        s = spectrum[(spectrum.material == 'GaAs') & (spectrum['T'] == temp) &
                     (spectrum.state == state)].sort_values('nu_THz')
        assert int(s.n.iloc[0]) == {'U': 3, 'D': 5}[state]
        z[state] = s
    x = z['U'].nu_THz.to_numpy()
    yU = z['U'].spectral_mean_WmK_THz.to_numpy()
    yD = z['D'].spectral_mean_WmK_THz.to_numpy()
    selected = x <= 10
    # Shading shows the mean-spectrum difference. Pointwise confidence intervals are stored separately.
    if temp == 150:
        ax.fill_between(x[selected], yD[selected], yU[selected], color=LOSS, alpha=.16, lw=0, zorder=1)
    ax.plot(x, yU, color=CU, lw=1.5, zorder=4, label=r'$U$')
    ax.plot(x, yD, color=CD, lw=1.5, zorder=4, label=r'$D$')
    ax.axvline(3, color='black', ls=':', lw=.8, zorder=2)
    ax.text(3.18, y_limits[temp]*.90, '3 THz', color='black', fontsize=8.5,
            va='top', ha='left')
    ax.text(.75, .28, f'{temp} K', transform=ax.transAxes, color='black',
            fontsize=11, va='center', ha='center')
    # The integrated loss is resolved at 150 K. The arrow marks the main spectral difference.
    if temp == 150:
        k = int(np.argmax((yU-yD)[selected]))
        ax.annotate('disorder loss', xy=(x[k], (yU[k]+yD[k])/2),
                    xytext=(x[k]+2.6, y_limits[temp]*.52), fontsize=8.5, color=LOSS,
                    arrowprops=dict(arrowstyle='-', color=LOSS, lw=.8,
                                    shrinkA=0, shrinkB=1))
    ax.set_title(f'({chr(97+j)})', loc='left', pad=8)
    ax.set_xlim(0, 10); ax.set_xticks([0, 3, 6, 9]); ax.set_xlabel('Frequency (THz)')
    ax.set_ylim(-1, y_limits[temp])
    ax.set_ylabel(r'Spectral $\kappa$ (W m$^{-1}$ K$^{-1}$ THz$^{-1}$)')
    ax.tick_params(direction='in', top=True, right=True, length=3, width=.7)
    ax.grid(False)
    ax.legend(frameon=False, loc='upper right', bbox_to_anchor=(.95,.96),
              fontsize=9.5, handlelength=1.4, handletextpad=.5, borderaxespad=.3)
save_figure(fig, "Fig2")
