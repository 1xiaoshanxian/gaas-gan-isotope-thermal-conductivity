# -*- coding: utf-8 -*-
"""Plot RTA thermal conductivities and isotope contributions in Figures 3 and 4.

The 7.1 by 3.22 inch canvas matches Figures 1 and 2. Panels use a width of
2.80 inches, column origins at 0.55 and 4.15 inches, and a 0.52 inch bottom
margin. Material labels sit above the curves. Figure 4 uses in-panel legends,
an optional pale fill between total and disorder contributions, and an
optional line glow. The data are read from rta_five_state_contributions.csv.

Run python fig3_4.py to generate both figures."""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, LogLocator, MultipleLocator, NullFormatter

FILL_BAND = True          # Shade between the total and disorder curves in Figure 4.
GLOW = True               # Add a soft glow around each curve.


from plot_config import MAIN_DATA
from plot_output import save_figure
from figure_layout import FIGSIZE, MAIN_RECT, SECOND_RECT

DATA = MAIN_DATA / "rta_five_state_contributions.csv"

COLUMN_X = (0.55, 4.15)
PANEL_W = 2.80


def rect(x, bottom, height, width=PANEL_W):
    return [x / FIGSIZE[0], bottom / FIGSIZE[1], width / FIGSIZE[0], height / FIGSIZE[1]]


COL = {'L': '#2466A8', 'U': '#D18326', 'D': '#B42C48',
       'total': '#303A44', 'disorder': '#B42C48', 'mass': '#2466A8'}
INK = '#20242b'
STYLE = {'L': dict(ls='-', marker='o'),
         'U': dict(ls=(0, (6.4, 2.6)), marker='s'),
         'D': dict(ls=(0, (7.0, 2.2, 1.5, 2.2)), marker='^')}
YLIM3 = {'GaAs': (15.0, 300.0), 'GaN': (60.0, 1600.0)}

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 9.5, 'axes.labelsize': 9.5,
    'xtick.labelsize': 8.5, 'ytick.labelsize': 8.5, 'legend.fontsize': 9.5,
    'axes.linewidth': 0.9, 'axes.edgecolor': INK, 'axes.unicode_minus': False,
    'lines.linewidth': 1.7, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
})


def tidy(ax, minor=True):
    ax.tick_params(direction='in', top=True, right=True, length=3.2, width=0.8)
    if minor:
        ax.tick_params(which='minor', direction='in', top=True, right=True,
                       length=1.9, width=0.7)


def curve(ax, x, y, color, ls='-', lw=1.7, marker=None, ms=4.4, markevery=None,
          label=None, zorder=4, glow_alpha=0.085, glow_lw=6.2):
    """Draw a rounded main line and an optional soft glow."""
    if GLOW:
        ax.plot(x, y, color=color, lw=glow_lw, alpha=glow_alpha, ls='-',
                solid_capstyle='round', zorder=zorder - 1)
    return ax.plot(x, y, color=color, lw=lw, ls=ls, marker=marker, ms=ms,
                   mfc='white', mec=color, mew=1.1, markevery=markevery,
                   label=label, dash_capstyle='round', solid_capstyle='round',
                   zorder=zorder, clip_on=True)


def label_xy(T, series, x=0.72, gap=0.055):
    """Place the label gap axes units above the highest curve at x."""
    t = float(np.interp(x, np.linspace(0, 1, len(T)), T))
    yk = max(float(np.interp(t, T, np.asarray(y, float))) for y in series)
    return t, yk


def material_label(ax, text, y, fs=12.5, x=0.55):
    """Place the material label above the curves in the central panel space."""
    ax.text(x, y, text, transform=ax.transAxes, ha='center', va='bottom',
            fontsize=fs, color=INK, zorder=9)


def panel_letter(ax, letter, pad=8, fs=9.5):
    """Place the panel letter just outside the upper-left corner."""
    ax.set_title(f'({letter})', loc='left', pad=pad, fontsize=fs, color=INK)


def frac_log(ax, y):
    lo, hi = ax.get_ylim()
    return (np.log10(y) - np.log10(lo)) / (np.log10(hi) - np.log10(lo))


def frac_lin(ax, y):
    lo, hi = ax.get_ylim()
    return (y - lo) / (hi - lo)




def load():
    df = pd.read_csv(DATA, encoding='utf-8-sig')
    assert set(df.material) == {'GaAs', 'GaN'} and set(df.solver) == {'RTA'}
    for material, z in df.groupby('material'):
        z = z.sort_values('T')
        assert np.allclose(z['T'], np.arange(100, 801, 50)), material
        assert np.allclose(z.mass_pp + z.disorder_pp, z.total_pct, atol=1e-9), material
    return df


def draw_fig3(df):
    fig = plt.figure(figsize=FIGSIZE)
    for j, (r, material) in enumerate(zip((MAIN_RECT, SECOND_RECT), ('GaAs', 'GaN'))):
        ax = fig.add_axes(r)
        z = df[df.material == material].sort_values('T')
        T = z['T'].to_numpy(float)
        handles = []
        for i, state in enumerate(('L', 'U', 'D')):
            st = STYLE[state]
            h, = curve(ax, T, z[state].to_numpy(float), COL[state], ls=st['ls'],
                       marker=st['marker'], ms=4.4,
                       markevery=list(range(i, len(T), 3)),
                       label=f'${state}$', zorder=4 + i,
                       glow_alpha=0.07, glow_lw=5.2)
            handles.append(h)
        ax.set_yscale('log')
        ax.set_xlim(75, 825)
        ax.xaxis.set_major_locator(FixedLocator([100, 300, 500, 700]))
        ax.xaxis.set_minor_locator(MultipleLocator(100))
        ax.set_ylim(*YLIM3[material])
        ax.yaxis.set_major_locator(LogLocator(base=10, subs=(1, 2, 5), numticks=12))
        ax.yaxis.set_minor_locator(LogLocator(base=10, subs=tuple(range(2, 10)), numticks=100))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_xlabel('Temperature (K)')
        ax.set_ylabel(r'$\kappa$ (W m$^{-1}$ K$^{-1}$)')
        tidy(ax)
        ax.legend(handles=handles, loc='upper right', frameon=False, numpoints=1,
                  handlelength=2.0, handletextpad=0.5, labelspacing=0.28,
                  borderaxespad=0.45)
        t615, yk = label_xy(T, [z[s].to_numpy(float) for s in ('L', 'U', 'D')], x=0.55)
        material_label(ax, material, frac_log(ax, yk) + 0.10)
        panel_letter(ax, chr(97 + j))
    save_figure(fig, "Fig3")


def draw_fig4(df):
    top_h, top_b = 1.33, 1.60
    bot_h, bot_b = 0.92, 0.52
    ylim_top = {'GaAs': (0.0, 15.0), 'GaN': (15.0, 50.0)}
    yticks_top = {'GaAs': [0, 5, 10, 15], 'GaN': [20, 30, 40, 50]}
    ylim_bot = {'GaAs': (0.47, 0.55), 'GaN': (-2.9, 0.8)}
    yticks_bot = {'GaAs': [0.48, 0.50, 0.52, 0.54], 'GaN': [-2, 0]}
    fig = plt.figure(figsize=FIGSIZE)
    left_top = left_bot = None
    for j, material in enumerate(('GaAs', 'GaN')):
        x0 = COLUMN_X[j]
        a = fig.add_axes(rect(x0, top_b, top_h))
        b = fig.add_axes(rect(x0, bot_b, bot_h))
        z = df[df.material == material].sort_values('T')
        T = z['T'].to_numpy(float)
        total = z.total_pct.to_numpy(float)
        dis = z.disorder_pp.to_numpy(float)
        a.set_xlim(75, 825)
        a.set_ylim(*ylim_top[material])
        if FILL_BAND:                        # The difference between the curves is the average-mass contribution.
            a.fill_between(T, total, dis, color=COL['mass'], alpha=0.10, lw=0,
                           zorder=1)
        h_total, = curve(a, T, total, COL['total'], ls='-', lw=1.6, marker='o',
                         ms=3.9, markevery=2, label='Total (%)', zorder=5)
        h_dis, = curve(a, T, dis, COL['disorder'], ls=(0, (6.4, 2.6)), lw=1.6,
                       marker='s', ms=3.9, markevery=2, label='Disorder (pp)',
                       zorder=6)
        curve(b, T, z.mass_pp.to_numpy(float), COL['mass'], ls='-', lw=1.6,
              marker='^', ms=3.9, markevery=2, zorder=5)
        b.axhline(0, color='#8a9099', lw=0.7, zorder=1)

        a.yaxis.set_major_locator(FixedLocator(yticks_top[material]))
        b.set_xlim(75, 825)
        b.set_ylim(*ylim_bot[material])
        b.yaxis.set_major_locator(FixedLocator(yticks_bot[material]))
        b.xaxis.set_major_locator(FixedLocator([100, 300, 500, 700]))
        b.xaxis.set_minor_locator(MultipleLocator(100))
        b.set_xlabel('Temperature (K)')
        a.tick_params(labelbottom=False)
        tidy(a)
        tidy(b, minor=False)
        _, yk = label_xy(T, [total, dis], x=0.55)
        material_label(a, material, frac_lin(a, yk) + 0.08, fs=11.5)
        panel_letter(a, chr(97 + j), pad=7)
        a.legend(handles=[h_total, h_dis], loc='upper right', frameon=False,
                 numpoints=1, handlelength=2.0, handletextpad=0.5,
                 labelspacing=0.3, borderaxespad=0.45)
        if j == 0:
            left_top, left_bot = a, b
    left_top.set_ylabel('Total / disorder')
    left_bot.set_ylabel('Mean mass (pp)')
    save_figure(fig, "Fig4")



if __name__ == "__main__":
    data = load()
    draw_fig3(data)
    draw_fig4(data)
