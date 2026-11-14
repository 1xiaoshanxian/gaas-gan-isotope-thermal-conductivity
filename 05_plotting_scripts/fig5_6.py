# -*- coding: utf-8 -*-
"""Plot RTA disorder spectra and average-mass factor contributions.

Figures 5 and 6 use a 7.1 by 3.22 inch canvas. Export at 450 dpi produces
3195 by 1449 pixels. DejaVu Sans fonts, inward ticks, fixed panel geometry,
and editable SVG text follow the other main figures. Figure 5 has six
panels. Figure 6 has two material rows, cumulative mass responses in the left
column, and heat-capacity, squared-velocity, and lifetime contributions in
the right column. Legends are placed inside their panels.

Input tables are read from 03_main_data. Run python fig5_6.py to generate
both figures in the package output directory."""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import (FixedLocator, LogLocator, MultipleLocator,
                               NullFormatter, NullLocator)

# Physical geometry shared with Figures 1 to 4, in inches.
FIG = (7.1, 3.22)
COL2_X = (0.55, 4.15)          # Figure 6 uses the same two-column positions as Figures 1 and 3.
COL2_W = 2.80
COL3_X = (0.68, 2.952, 5.224)   # Figure 5 has three columns with space for logarithmic ticks and y labels.
COL3_W = 1.727

F5_H, F5_BOT, F5_GAP = 0.965, 0.46, 0.62
F6_H, F6_BOT, F6_GAP = 1.02, 0.46, 0.50

INK = '#20242b'
GREY0 = '#8a9099'
COL = {'L': '#2466A8', 'U': '#D18326', 'D': '#B42C48',
       'mass': '#2466A8', 'dis': '#B42C48', 'total': '#303A44'}
TEMPERATURES = {100: ('#2466A8', '-'), 300: ('#B42C48', '--'), 600: ('#309479', ':')}
FACTORS = [('C_loss_pp', 'Heat capacity', '#885AA8'),
           ('v2_loss_pp', 'Squared velocity', '#2466A8'),
           ('tau_loss_pp', 'Lifetime', '#B42C48')]
# The Figure 6 legends use the factor symbols defined in the manuscript.
FACTOR_LABELS = {'symbol': ['$C$', '$v^2$', '$\\tau$', 'Net response'],
                 'short': ['Capacity', 'Velocity$^2$', 'Lifetime', 'Net'],
                 'full': ['Heat capacity', 'Squared velocity', 'Lifetime',
                          'Net response']}

# Label alternating logarithmic decades, with three GaAs ticks and four GaN ticks.
F5_LOG_TICKS = ([1e1, 1e-1, 1e-3], [1e2, 1e0, 1e-2, 1e-4])

# Use explicit limits and ticks on the Figure 6 y axes.
F6_CUM = {'GaAs': ((-0.06, 0.62), [0.0, 0.2, 0.4, 0.6]),
          'GaN': ((-3.0, 1.5), [-2, -1, 0, 1])}
F6_BAR = {'GaAs': ((-0.45, 1.35), [0.0, 0.5, 1.0]),
          'GaN': ((-4.2, 4.0), [-4, -2, 0, 2])}

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 9.5, 'axes.labelsize': 9.5,
    'xtick.labelsize': 8.5, 'ytick.labelsize': 8.5, 'legend.fontsize': 8.5,
    'axes.linewidth': 0.9, 'axes.edgecolor': INK, 'axes.unicode_minus': False,
    'lines.linewidth': 1.5, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
})


from plot_config import MAIN_DATA
from plot_output import save_figure


def rect(x, bottom, height, width):
    """Convert inch coordinates to figure fractions while preserving panel size."""
    return [x / FIG[0], bottom / FIG[1], width / FIG[0], height / FIG[1]]


def tidy(ax, minor=False):
    ax.tick_params(direction='in', top=True, right=True, length=3.2, width=0.8)
    if minor:
        ax.tick_params(which='minor', direction='in', top=True, right=True,
                       length=1.9, width=0.7)


def panel_title(ax, text, pad=6, fs=9.5):
    """Place the panel title just outside the upper-left corner."""
    ax.set_title(text, loc='left', pad=pad, fontsize=fs, color=INK)


def inch_bbox(artist, fig):
    """Return the artist bounding box in inches."""
    return artist.get_window_extent().transformed(fig.dpi_scale_trans.inverted())


def check_legends(fig, legs, tag):
    """Check that legends stay inside the canvas and do not overlap each other."""
    boxes = []
    for leg in legs:
        bb = inch_bbox(leg, fig)
        boxes.append(bb)
        assert bb.x0 > 0.02 and bb.x1 < FIG[0] - 0.02, f'{tag}: legend exceeds the horizontal canvas bounds {bb}'
        assert bb.y0 > 0.02 and bb.y1 < FIG[1] - 0.02, f'{tag}: legend exceeds the vertical canvas bounds {bb}'
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            assert (a.x1 < b.x0 or b.x1 < a.x0 or a.y1 < b.y0 or b.y1 < a.y0), \
                f'{tag}: two legend boxes overlap {a} / {b}'
    for bb in boxes:
        print(f'  {tag} legend position: x {bb.x0:.2f}--{bb.x1:.2f} in, '
              f'y {bb.y0:.2f}--{bb.y1:.2f} in, height {bb.height:.2f} in')
    return boxes


def proxy_temp():
    """Create legend handles for the temperature series."""
    return [Line2D([], [], color=c, ls=ls, lw=1.7, label=f'{t} K')
            for t, (c, ls) in TEMPERATURES.items()]


def proxy_factor(labels):
    """Create handles for the three factors and the net-response diamond."""
    h = [Patch(facecolor=c, edgecolor='white', lw=.5, label=lab)
         for (_, _, c), lab in zip(FACTORS, labels[:3])]
    h.append(Line2D([], [], marker='D', ls='', ms=4.2, mfc='white',
                    mec=COL['total'], mew=1, label=labels[3]))
    return h


def check_in_axes(fig, ax, leg, tag):
    """Check pixel coordinates to keep an in-panel legend inside its axes."""
    fig.canvas.draw()
    ab, lb = ax.get_window_extent(), leg.get_window_extent()
    inside = (lb.x0 >= ab.x0 - 1 and lb.x1 <= ab.x1 + 1
              and lb.y0 >= ab.y0 - 1 and lb.y1 <= ab.y1 + 1)
    bb = inch_bbox(leg, fig)
    print(f'  {tag} in-panel legend: {bb.width:.2f} x {bb.height:.2f} in '
          f'(panel coverage {100 * bb.width / (ab.width / fig.dpi):.0f}% x '
          f'{100 * bb.height / (ab.height / fig.dpi):.0f}%), inside axes={inside}')
    assert inside, f'{tag}: legend exceeds its axes'
    return lb


def assert_legend_clear(fig, ax, leg, points, tag):
    """Check that a legend box contains no plotted curve or bar points."""
    lb = check_in_axes(fig, ax, leg, tag)
    inv = ax.transData.inverted()
    (x0, y0), (x1, y1) = inv.transform([(lb.x0, lb.y0), (lb.x1, lb.y1)])
    bad = [(round(float(x), 3), float(y)) for x, y in points
           if x0 <= x <= x1 and y0 <= y <= y1]
    print(f'    legend covers data range x {x0:.2f}--{x1:.2f}, y {y0:.4g}--{y1:.4g}, '
          f'covered points {len(bad)}')
    assert not bad, f'{tag}: legend covers {len(bad)} data points, including {bad[:3]}'


def align_y_labels(fig, columns, base_pad_pt=3.5, labelpad_pt=4.0):
    """Align y labels between material rows while retaining a fixed tick-label gap.

Increase the tick padding in the row with narrower tick labels until both
rows have the same tick-label left edge. Matplotlib then positions the axis
labels along a shared vertical line with the requested label padding."""
    fig.canvas.draw()
    for axes in columns:
        for ax in axes:
            ax.tick_params(axis='y', pad=base_pad_pt)
            ax.yaxis.labelpad = labelpad_pt
        fig.canvas.draw()
        widths = [max((t.get_window_extent().width for t in ax.get_yticklabels()
                       if t.get_text()), default=0.0) for ax in axes]
        target = max(widths)
        for ax, w in zip(axes, widths):
            ax.tick_params(axis='y',
                           pad=base_pad_pt + (target - w) * 72 / fig.dpi)
    fig.canvas.draw()

    labelpad_in = labelpad_pt / 72
    for axes in columns:
        boxes = [inch_bbox(ax.yaxis.label, fig) for ax in axes]
        tag = '/'.join(ax.get_ylabel().replace('\n', ' ') for ax in axes)
        print('  y-label alignment ' + tag + ': x0 = '
              + ', '.join(f'{b.x0:.3f}' for b in boxes) + ' in')
        assert max(b.x0 for b in boxes) - min(b.x0 for b in boxes) < 2e-3, \
            f'{tag}: y labels in the same column are misaligned'
        assert min(b.x0 for b in boxes) > 0.004, f'{tag}: y label is clipped by the canvas'
        for ax, b in zip(axes, boxes):
            ticks = [t.get_window_extent() for t in ax.get_yticklabels()
                     if t.get_text()]
            if not ticks:
                continue
            left = min(t.x0 for t in ticks) / fig.dpi
            gap = left - b.x1
            print(f'    gap to tick labels {gap:.3f} in (expected {labelpad_in:.3f})')
            assert abs(gap - labelpad_in) < 5e-3, f'{tag}: y label is too far from its tick labels'


def stair_points(edges, values):
    """Return step-curve corners for checking legend overlap."""
    pts = []
    for lo, hi, v in zip(edges[:-1], edges[1:], values):
        pts += [(float(lo), float(v)), (float(hi), float(v))]
    return pts


def place_legends(fig, legs, y_in, centers_in=None, gap_in=0.34):
    """Place legends along the canvas bottom, centered when centers_in is None."""
    fig.canvas.draw()
    if centers_in is None:
        widths = [inch_bbox(leg, fig).width for leg in legs]
        x0 = (FIG[0] - (sum(widths) + gap_in * (len(legs) - 1))) / 2
        centers_in, cursor = [], x0
        for w in widths:
            centers_in.append(cursor + w / 2)
            cursor += w + gap_in
    for leg, cx in zip(legs, centers_in):
        leg.set_bbox_to_anchor((cx / FIG[0], y_in / FIG[1]), transform=fig.transFigure)
    fig.canvas.draw()
    return centers_in




# Figure 5 RTA disorder-loss spectra.
def draw_fig5(sp):
    """Plot bin conductivities, relative suppression, and cumulative loss for both materials."""
    fig = plt.figure(figsize=FIG)
    col_axes = ([], [], [])
    for row, (material, bw, xmax) in enumerate(((u'GaAs', .25, 10.0),
                                                (u'GaN', .5, 21.0))):
        zb = F5_BOT + (1 - row) * (F5_H + F5_GAP)
        a, b, c = [fig.add_axes(rect(x, zb, F5_H, COL3_W)) for x in COL3_X]
        for col, ax in zip(col_axes, (a, b, c)):
            col.append(ax)
        z = sp[(sp.material == material) & np.isclose(sp.bin_width_THz, bw)]
        r = z[z['T'] == 300]
        edges = np.r_[r.f_low.to_numpy(float), float(r.f_high.iloc[-1])]

        a.stairs(r.U_bin.to_numpy(float), edges, color=COL['L'], lw=1.5,
                 label='$U$ heat')
        a.stairs(r.loss_bin.to_numpy(float), edges, color=COL['D'], lw=1.5,
                 ls=(0, (6.4, 2.6)), label='$U-D$ loss')
        a.set_yscale('log')
        a.set_ylim(1e-4, 15.0 if row == 0 else 100.0)
        # Label alternating decades and omit minor ticks.
        a.yaxis.set_major_locator(FixedLocator(F5_LOG_TICKS[row]))
        a.yaxis.set_minor_locator(NullLocator())
        a.set_ylabel(r'$\kappa$ (W m$^{-1}$ K$^{-1}$)')   # Match the Figure 3 notation and fit the label within the canvas.
        if row == 0:
            # Both rows share the same curve labels. Show a compact, opaque legend in the first row.
            # Place it in the empty region near x above 6.4 THz and y above 0.6.
            leg = a.legend(loc='upper right', fontsize=6.8, handlelength=1.1,
                           handletextpad=.4, labelspacing=.1, borderpad=.18,
                           borderaxespad=.3, frameon=True, framealpha=1,
                           facecolor='white', edgecolor='#c3c8d0')
            fig.canvas.draw()
            assert_legend_clear(fig, a, leg,
                                stair_points(edges, r.U_bin.to_numpy(float))
                                + stair_points(edges, r.loss_bin.to_numpy(float)),
                                'fig5a')

        b.plot(r.f.to_numpy(float), r.suppression_pct.to_numpy(float),
               color=COL['D'], marker='o', ms=2.2, lw=1.5)
        b.set_ylim(0, 25 if row == 0 else 100)
        b.set_yticks([0, 10, 20] if row == 0 else [0, 50, 100])
        b.set_ylabel('Suppression (%)')

        for temp, (color, ls) in TEMPERATURES.items():
            s = z[z['T'] == temp]
            c.step(np.r_[0, s.f_high.to_numpy(float)],
                   np.r_[0, s.cumulative_loss_pct.to_numpy(float)],
                   where='post', color=color, ls=ls, lw=1.5, label=f'{temp} K')
        c.set_ylim(0, 105)
        c.set_yticks([0, 50, 100])
        c.set_ylabel('Cumulative loss (%)')
        c.legend(loc='lower right', frameon=False, fontsize=8, handlelength=1.8,
                 handletextpad=.5, labelspacing=.3, borderaxespad=.35)

        for ax, letter in zip((a, b, c), 'abcdef'[3 * row:3 * row + 3]):
            ax.set_xlim(0, xmax)
            ax.xaxis.set_major_locator(MultipleLocator(2 if row == 0 else 5))
            ax.set_xlabel('Frequency (THz)')
            tidy(ax)
            panel_title(ax, f'({letter})' + (f' {material}, 300 K' if ax is a else ''))
    align_y_labels(fig, col_axes)
    save_figure(fig, "Fig5")


# Figure 6 Average-mass responses and transport-factor allocation.
def draw_fig6(groups, factors, budget, labels='symbol'):
    """Plot cumulative mass responses and symmetric transport-factor allocations.

The GaAs panels are a and b. The GaN panels are c and d. Temperature
legends sit inside the cumulative-response panels and factor legends sit
above the bars inside the contribution panels."""
    fig = plt.figure(figsize=FIG)
    col_axes = ([], [])
    records = {'panels': {}, 'geometry': {'figsize_in': list(FIG),
                                          'columns_x_in': list(COL2_X),
                                          'panel_in': [COL2_W, F6_H],
                                          'bottom_in': F6_BOT, 'gap_in': F6_GAP,
                                          'legend_place': 'in-panel',
                                          'factor_legend_labels': FACTOR_LABELS[labels]}}
    for row, (material, direction, xmax) in enumerate(((u'GaAs', 'xx', 10.0),
                                                       (u'GaN', 'zz', 21.0))):
        zb = F6_BOT + (1 - row) * (F6_H + F6_GAP)
        a = fig.add_axes(rect(COL2_X[0], zb, F6_H, COL2_W))
        c = fig.add_axes(rect(COL2_X[1], zb, F6_H, COL2_W))
        col_axes[0].append(a)
        col_axes[1].append(c)
        tag_left, tag_right = chr(97 + 2 * row), chr(98 + 2 * row)

        z = groups[(groups.material == material) & (groups.direction == direction)
                   & np.isclose(groups.group_threshold, .05)]
        line_records = []
        cum_points = [(float(xi), 0.0) for xi in np.linspace(0, xmax, 80)]  # Include the zero reference line.
        for temp, (color, ls) in TEMPERATURES.items():
            s = z[z['T'] == temp]
            assert len(s) > 0 and s.f_edge.is_monotonic_increasing
            model = float(budget[(budget.material == material)
                                 & (budget['T'] == temp)].mass_pp.iloc[0])
            assert abs(float(s.cumulative_pp.iloc[-1]) - model) < 1e-9
            x = np.r_[0, s.f_edge.to_numpy(float)]
            y = np.r_[0, s.cumulative_pp.to_numpy(float)]
            a.step(x, y, where='post', color=color, ls=ls, lw=1.5, label=f'{temp} K')
            cum_points += stair_points(x, y)
            line_records.append({'T': temp, 'frequency_edges_THz': x.tolist(),
                                 'cumulative_pp': y.tolist(), 'RTA_mass_pp': model})
        a.axhline(0, color=GREY0, lw=.7)
        a.set_xlim(0, xmax)
        a.xaxis.set_major_locator(MultipleLocator(2 if row == 0 else 5))
        a.set_xlabel('Reference frequency (THz)')
        a.set_ylabel('Mass response (pp)')
        a.set_ylim(*F6_CUM[material][0])
        a.set_yticks(F6_CUM[material][1])
        # Place the GaAs temperature legend at center right below its curves.
        # Place the GaN legend in the lower-left space beside its negative response.
        leg_a = a.legend(loc=('center right' if row == 0 else 'lower left'),
                         bbox_to_anchor=((1.0, .42) if row == 0 else (.02, .03)),
                         ncol=1, frameon=False, fontsize=8.5, handlelength=1.6,
                         handletextpad=.6, labelspacing=.35, borderaxespad=.3)
        fig.canvas.draw()
        assert_legend_clear(fig, a, leg_a, cum_points, f'fig6{tag_left}')

        s = factors[(factors.material == material)
                    & np.isclose(factors.group_threshold_THz, .05)
                    & (factors.frequency_band == 'all')].sort_values('T')
        assert s['T'].tolist() == [100.0, 300.0, 600.0]
        x = np.arange(3)
        pos = np.zeros(3)
        neg = np.zeros(3)
        for column, lab, color in FACTORS:
            values = s[column].to_numpy(float)
            c.bar(x, values, bottom=np.where(values >= 0, pos, neg), width=.46,
                  color=color, edgecolor='white', lw=.5, label=lab, zorder=3)
            pos += np.maximum(values, 0)
            neg += np.minimum(values, 0)
        net = s.total_loss_pp.to_numpy(float)
        np.testing.assert_allclose(pos + neg, net, atol=1e-9, rtol=0)
        model = budget[(budget.material == material)
                       & budget['T'].isin([100, 300, 600])].sort_values('T')
        np.testing.assert_allclose(net, model.mass_pp, atol=1e-9, rtol=0)
        c.plot(x, net, 'D', color=COL['total'], ms=4.2, mfc='white', mew=1,
               label='Net response', zorder=4)
        c.axhline(0, color=GREY0, lw=.7)
        c.set_xticks(x, ['100', '300', '600'])
        c.set_xlim(-.55, 2.55)
        c.set_xlabel('Temperature (K)')
        c.set_ylabel('Contribution (pp)')
        c.set_ylim(*F6_BAR[material][0])
        c.set_yticks(F6_BAR[material][1])
        # Arrange factor labels in one row in the upper panel space.
        leg_c = c.legend(handles=proxy_factor(FACTOR_LABELS[labels]),
                         loc='upper right', ncol=4, frameon=False, fontsize=8,
                         handlelength=1.1, columnspacing=.9, handletextpad=.4,
                         borderaxespad=.3)
        bar_points = [(-.55, 0.0), (2.55, 0.0)]       # Include the zero reference line in overlap checks.
        bar_points += [(float(xi), float(v)) for xi in x
                       for v in (pos[xi], neg[xi], net[xi])]
        fig.canvas.draw()
        assert_legend_clear(fig, c, leg_c, bar_points, f'fig6{tag_right}')

        for ax, letter in ((a, tag_left), (c, tag_right)):
            tidy(ax)
            panel_title(ax, f'({letter}) {material}')
        records['panels'][tag_left] = {'material': material, 'kind': 'cumulative',
                                       'series': line_records}
        records['panels'][tag_right] = {'material': material, 'kind': 'factors',
                                        'rows': s.to_dict(orient='records')}

    align_y_labels(fig, col_axes)
    save_figure(fig, "Fig6")


def load():
    sp = pd.read_csv(MAIN_DATA / 'disorder_spectra_bin_width_sensitivity.csv')
    sp = sp[((sp.material == 'GaAs') & np.isclose(sp.bin_width_THz, .25))
            | ((sp.material == 'GaN') & np.isclose(sp.bin_width_THz, .5))].copy()
    sp = sp.rename(columns={'U_bin_W_mK': 'U_bin', 'loss_bin_W_mK': 'loss_bin'})
    sp['f'] = (sp.f_low + sp.f_high) / 2
    groups = pd.read_csv(MAIN_DATA / 'grouped_mass_response.csv')
    factors = pd.read_csv(MAIN_DATA / 'symmetric_mass_factor_decomposition.csv')
    budget = pd.read_csv(MAIN_DATA / 'rta_five_state_contributions.csv')
    return sp, groups, factors, budget



if __name__ == "__main__":
    spectra, groups, factors, budget = load()
    draw_fig5(spectra)
    draw_fig6(groups, factors, budget)
