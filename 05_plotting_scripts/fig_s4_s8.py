"""S4 and table-based S5/S7/S8 panel redraws; coverage is listed in README."""
import numpy as np
from si_common import plt, table, finish, dispatch, VALIDATION


def size_convergence():
    data = table(VALIDATION, "md_size_convergence.csv").sort_values("atoms")
    fig, ax = plt.subplots(figsize=(6.2, 3.7))
    ax.errorbar(data.atoms, data["mean"], yerr=data.sem_gpumdkit,
                fmt="o-", color="#2466a8", capsize=3)
    ax.axhline(37.4, color="0.4", ls="--", label="37.4 W/(m K)")
    ax.set_xscale("log")
    ax.set_xticks(data.atoms, [f"{n:,}" for n in data.atoms])
    ax.tick_params(axis="x", labelrotation=25)
    ax.set(xlabel="Number of atoms", ylabel=r"$\kappa$ (W m$^{-1}$ K$^{-1}$)",
           title="GaAs, L state, 300 K")
    ax.legend(frameon=False)
    finish(fig, "FigS4")


def field_summary():
    data = table(VALIDATION, "field_checks.csv")
    fig, axes = plt.subplots(1, 2, figsize=(8.3, 3.5))
    for ax, temperature, letter in zip(axes, [300, 150], ["a", "b"]):
        z = data[data.T_K == temperature].sort_values("field_Ainv")
        ax.errorbar(z.field_Ainv * 1e5, z["mean"], yerr=z.block1ns_SE,
                    fmt="o-", capsize=3, color="#2466a8", label="Full run")
        ax.plot(z.field_Ainv * 1e5, z.tail50_mean, "s--", color="#b42c48",
                label="Last 50% of run")
        ax.set(xlabel=r"Driving field ($10^{-5}$ $\AA^{-1}$)",
               ylabel=r"$\kappa$ (W m$^{-1}$ K$^{-1}$)")
        ax.set_title(f"({letter}) {temperature} K", loc="left")
        ax.legend(frameon=False, fontsize=8)
    finish(fig, "FigS5_summary")


def gan_validation():
    thermal = table(VALIDATION, "thermal_comparison.csv")
    dos = table(VALIDATION, "dos_smooth_data.csv")
    lifetime = table(VALIDATION, "lifetime_binned_300K.csv")
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.5))
    for prefix, color, label in [("DFT", "#2466a8", "DFT"),
                                  ("NEP 1", "#b42c48", "NEP")]:
        axes[0].semilogy(thermal.T_K, thermal[prefix + "_LBTE_zz"],
                         "o-", ms=3, color=color, label=label)
    axes[0].set(xlabel="Temperature (K)", ylabel=r"$\kappa_{zz}$ (W m$^{-1}$ K$^{-1}$)")
    for prefix, color, label in [("DFT", "#2466a8", "DFT"),
                                  ("NEP1", "#b42c48", "NEP")]:
        axes[1].plot(dos.frequency_thz, dos[prefix + "_smooth_DOS"],
                     color=color, label=label)
        # The archived lifetime table contains log10(tau/ps) quartiles.
        lo, med, hi = [10**lifetime[prefix + "_logtau_" + suffix]
                       for suffix in ["p25", "median", "p75"]]
        axes[2].semilogy(lifetime.frequency_thz, med, color=color, label=label)
        axes[2].fill_between(lifetime.frequency_thz, lo, hi, color=color, alpha=.12)
    axes[1].set(xlabel="Frequency (THz)", ylabel=r"Normalized DOS (THz$^{-1}$)")
    axes[2].set(xlabel="Frequency (THz)", ylabel="Lifetime (ps)")
    for ax, panel in zip(axes, ["a", "b", "d"]):
        ax.set_title(f"({panel}) GaN" + (", LBTE" if panel == "a" else ""), loc="left")
        ax.legend(frameon=False)
    finish(fig, "FigS7_abd")


def gan_dispersion():
    data = table(VALIDATION, "phonon_GMKGA_matched222_frequencies.csv")
    fig, ax = plt.subplots(figsize=(7.3, 4.1))
    ticks = []
    for segment, z in data.groupby("segment_index", sort=True):
        z = z.sort_values("point_index")
        x = float(segment) + np.linspace(0, 1, len(z))
        ticks.append(float(segment))
        for branch in range(1, 13):
            ax.plot(x, z[f"DFT_b{branch}"], color="#2466a8", lw=.9,
                    label="DFT" if segment == 0 and branch == 1 else None)
            ax.plot(x, z[f"NEP1_b{branch}"], color="#b42c48", lw=.9, ls="--",
                    label="NEP" if segment == 0 and branch == 1 else None)
    ticks.append(float(data.segment_index.max()+1))
    for x in ticks[1:-1]:
        ax.axvline(x, color="0.8", lw=.6)
    ax.set_xticks(ticks, [r"$\Gamma$", "M", "K", r"$\Gamma$", "A"])
    ax.set(xlim=(ticks[0], ticks[-1]), xlabel="Wave vector",
           ylabel="Frequency (THz)", title="(b) GaN")
    ax.legend(frameon=False)
    finish(fig, "FigS8b")


if __name__ == "__main__":
    dispatch({"S4": size_convergence, "S5": field_summary,
              "S7": gan_validation, "S8": gan_dispersion})
