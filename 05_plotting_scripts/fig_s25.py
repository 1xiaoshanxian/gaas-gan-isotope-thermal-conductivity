"""Plot the archived same-cell phonon dispersion and DOS."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import AutoMinorLocator, MaxNLocator
import numpy as np

from plot_config import SUPPLEMENTARY_DATA
from plot_output import save_figure


def main():
    source = SUPPLEMENTARY_DATA / "S22-S25_beta-Ga2O3" / "Ga2O3_same_cell_plot_data.npz"
    with np.load(source, allow_pickle=False) as data:
        x = data["x"]
        fd, fn = data["dft_frequencies_THz"], data["nep_frequencies_THz"]
        densities = data["dft_dos"], data["nep_dos"]
        slices = [slice(start, stop) for start, stop in zip(data["segment_start"], data["segment_stop"])]

    plt.rcParams.update({"font.family": "Arial", "font.size": 22,
                         "axes.linewidth": 1.4, "axes.unicode_minus": False,
                         "xtick.direction": "in", "ytick.direction": "in",
                         "xtick.top": True, "ytick.right": True,
                         "xtick.major.size": 7, "ytick.major.size": 7,
                         "xtick.minor.size": 3.5, "ytick.minor.size": 3.5,
                         "svg.fonttype": "none"})
    blue, red, grey = "#1f4e99", "#c0394b", "#b3b6bc"
    fig = plt.figure(figsize=(15.5, 7.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[3.15, 1], wspace=0.055,
                          left=0.069, right=0.985, bottom=0.135, top=0.965)
    ax = fig.add_subplot(gs[0, 0])
    dos_ax = fig.add_subplot(gs[0, 1], sharey=ax)
    ticks = [x[0], x[slices[0].stop - 1], x[slices[1].stop - 1], x[-1]]
    tick_labels = ["Γ", r"C | C$_2$", r"Y$_2$", "Γ"]
    for tick in ticks[1:-1]:
        ax.axvline(tick, color=grey, lw=1.0, zorder=0)
    for frequencies, color, linestyle, width in [
            (fd, blue, "-", 1.7), (fn, red, (0, (5, 3)), 1.45)]:
        # Draw each recommended segment independently: never draw C -> C2.
        for segment in slices:
            for band in range(30):
                ax.plot(x[segment], frequencies[segment, band], color=color,
                        ls=linestyle, lw=width, solid_capstyle="round")
    for axis in [ax, dos_ax]:
        axis.set_ylim(-0.35, 23.8)
        axis.set_yticks(np.arange(0, 25, 4))
        axis.axhline(0, color="#9aa1ab", lw=1.0, ls=(0, (5, 4)), zorder=0)
        axis.yaxis.set_minor_locator(AutoMinorLocator(4))
        axis.xaxis.set_minor_locator(AutoMinorLocator(4))
    ax.set_xlim(0, x[-1])
    ax.set_xticks(ticks, tick_labels)
    ax.set_xlabel("Wave vector", labelpad=12)
    ax.set_ylabel("Frequency (THz)", labelpad=10)
    ax.legend(handles=[Line2D([], [], color=blue, lw=2.5, label="DFT"),
                       Line2D([], [], color=red, lw=2.3, ls=(0, (5, 3)), label="NEP")],
              loc="upper center", ncol=2, frameon=True, framealpha=0.96,
              edgecolor="#cbd0d7", fontsize=20, borderpad=0.35, handlelength=2.3)
    for density, color, linestyle in [(densities[0], blue, "-"),
                                       (densities[1], red, (0, (5, 3)))]:
        if color == blue:
            dos_ax.fill_betweenx(density[:, 0], 0, density[:, 1], color=color, alpha=0.12)
        dos_ax.plot(density[:, 1], density[:, 0], color=color, lw=2.0, ls=linestyle)
    dos_ax.set_xlim(0, 1.1 * max(np.max(d[:, 1]) for d in densities))
    dos_ax.xaxis.set_major_locator(MaxNLocator(nbins=3))
    dos_ax.tick_params(axis="y", labelleft=False)
    dos_ax.set_xlabel("DOS (states/THz)", labelpad=12)
    ax.text(0.015, 0.955, "(a)", transform=ax.transAxes, va="top", fontsize=24)
    dos_ax.text(0.06, 0.955, "(b)", transform=dos_ax.transAxes, va="top", fontsize=24)
    save_figure(fig, "FigS25", dpi=450)


if __name__ == "__main__":
    main()
