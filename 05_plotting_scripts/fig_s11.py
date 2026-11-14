"""S11: published experimental symbols and the saved RTA reference states.

Curve interpolation matches the original comparison: PCHIP in log(T), log(kappa),
without extrapolation. Digitization uncertainty is not a measurement error bar.
"""
import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator
from si_common import plt, table, finish, MAIN_DATA, TRANSPORT, COLORS


def main():
    observations = table(TRANSPORT, "experimental_reference_points.csv")
    calculations = table(MAIN_DATA, "rta_five_state_contributions.csv")
    assert len(observations) == 141 and observations.observation_id.is_unique
    assert observations.temperature_K.notna().all()
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 8.3))

    def curves(ax, material, states, low=100, high=800):
        z = calculations[calculations.material == material].sort_values("T")
        x = np.linspace(max(low, z["T"].min()), min(high, z["T"].max()), 500)
        for state, style in zip(states, ["-", "--", ":", "-."]):
            interpolation = PchipInterpolator(np.log(z["T"]), np.log(z[state]))
            ax.plot(x, np.exp(interpolation(np.log(x))), color=COLORS[state],
                    ls=style, lw=1.4, label=f"${state}$")

    def points(ax, material, group, reference, label, marker, errors=True):
        z = observations[(observations.material == material) &
                         (observations.group == group) &
                         (observations.reference == reference)].sort_values("temperature_K")
        assert len(z), (material, group, reference)
        ax.plot(z.temperature_K, z.kappa_W_mK, marker, ls="none", ms=4,
                mfc="white", mec="#12a2dd", label=label)
        if errors:
            error = z.measurement_uncertainty_abs_W_mK
            valid = error.notna() & (error > 0)
            ax.errorbar(z.loc[valid, "temperature_K"], z.loc[valid, "kappa_W_mK"],
                        yerr=error[valid], fmt="none", ecolor="#12a2dd", capsize=2)

    a, b, c, d = axes.ravel()
    curves(a, "GaAs", ["H"], 100, 300)
    points(a, "GaAs", "enriched71", "Inyushkin2003", "Inyushkin et al.", "D", False)
    curves(b, "GaN", ["H"], 150, 600)
    points(b, "GaN", "enriched71_c", "Zheng2019", "Zheng et al.", "^")
    curves(c, "GaAs", ["L", "U", "H", "D"])
    points(c, "GaAs", "natural", "Inyushkin2003", "Inyushkin et al.", "o", False)
    points(c, "GaAs", "conventional_pending", "Holland1964", "Holland et al.*", "s", False)
    points(c, "GaAs", "conventional_pending", "Amith1965", "Amith et al.*", "^", False)
    curves(d, "GaN", ["L", "U", "H", "D"])
    points(d, "GaN", "natural_c", "Zheng2019", "Zheng et al.", "^")
    points(d, "GaN", "conventional_c", "Shibata2007", "Shibata et al.", "o")
    points(d, "GaN", "conventional_abstract", "Jezowski2003_SSC", "Jezowski et al., SSC*", "v", False)
    points(d, "GaN", "conventional_abstract", "Jezowski2003_PSSB", "Jezowski et al., PSSB*", "p", False)
    for ax, title, xlim, ylim in [
            (a, "(a) GaAs: enriched 71Ga", (90, 320), (43, 265)),
            (b, "(b) GaN: enriched 71Ga, c axis", (140, 625), (65, 800)),
            (c, "(c) GaAs: natural / conventional", (80, 855), (14, 280)),
            (d, "(d) GaN: natural / conventional", (30, 880), (40, 4500))]:
        ax.set_yscale("log")
        ax.set(xlim=xlim, ylim=ylim, xlabel="Temperature (K)",
               ylabel=r"$\kappa$ (W m$^{-1}$ K$^{-1}$)")
        ax.set_title(title, loc="left", fontsize=10)
        ax.legend(loc="upper right", frameon=False, fontsize=7.2)
    for ax in [c, d]:
        ax.text(.04, .04, "Composition unmatched: reference only", transform=ax.transAxes,
                fontsize=8, color="0.3")
    finish(fig, "FigS11")


if __name__ == "__main__":
    main()
