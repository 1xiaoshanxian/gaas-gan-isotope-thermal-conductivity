"""S23-S24: beta-Ga2O3 spectral response and q-mesh sensitivity."""
import numpy as np
from si_common import plt, table, finish, dispatch, BETA


def spectrum_and_mesh():
    spectral = table(BETA, "Ga2O3_spectral.csv")
    mesh = table(BETA, "Ga2O3_mesh_convergence.csv")
    fig, axes = plt.subplots(2, 2, figsize=(9.4, 6.9))
    colors = {"xx": "#2466a8", "yy": "#b42c48", "zz": "#309479", "avg": "0.3"}
    for direction in ["xx", "yy", "zz"]:
        z = spectral[(spectral.T_K == 300) & (spectral.direction == direction)].sort_values("E_THz")
        for state, style in [("U", "-"), ("D", "--")]:
            axes[0, 0].plot(z.E_THz, z[f"kappa_{state}_bin"], style,
                            color=colors[direction], label=direction+" "+state)
        axes[0, 1].plot(z.E_THz, z.relative_reduction_pct, color=colors[direction], label=direction)
        axes[1, 0].plot(z.E_THz, 100*z.cumulative_fraction, color=colors[direction], label=direction)
    for direction in ["xx", "yy", "zz", "avg"]:
        z = mesh[mesh.T_K == 300].sort_values("mesh")
        axes[1, 1].plot(z.mesh, z["k_"+direction], "o-", ms=3, color=colors[direction], label=direction)
    axes[0, 0].set(xlabel="Frequency (THz)", ylabel=r"$\kappa$ per 0.5 THz (W m$^{-1}$ K$^{-1}$)")
    axes[0, 1].set(xlabel="Frequency (THz)", ylabel="Relative disorder reduction (%)")
    axes[1, 0].set(xlabel="Frequency (THz)", ylabel="Cumulative disorder loss (%)")
    axes[1, 1].set(xlabel="q-mesh dimension", ylabel=r"$\kappa_L$ (W m$^{-1}$ K$^{-1}$)", xticks=[10, 11, 12, 13, 14])
    for i, ax in enumerate(axes.ravel()):
        ax.set_title(f"({chr(97+i)}) 300 K", loc="left")
        ax.legend(frameon=False, fontsize=7.5, ncol=2 if i == 0 else 1)
    finish(fig, "FigS23")


def difference_mesh():
    data = table(BETA, "Ga2O3_LUD_12mesh_difference_convergence.csv")
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.8))
    for mesh, color in [(12, "#2466a8"), (14, "#b42c48")]:
        for direction, style in [("avg", "-"), ("yy", "--")]:
            z = data[data.direction == direction].sort_values("T_K")
            axes[0].plot(z.T_K, z[f"d_dis_{mesh}"], style, color=color, label=f"{mesh} cubed, {direction}")
    for direction, color in [("avg", "0.2"), ("xx", "#2466a8"), ("yy", "#b42c48"), ("zz", "#309479")]:
        z = data[data.direction == direction].sort_values("T_K")
        axes[1].plot(z.T_K, z.rel_dis_pct, color=color, label=direction)
    axes[1].axhspan(-10, 10, color="0.92", zorder=0)
    z = data[data.direction == "avg"].sort_values("T_K")
    for key, label, color in [("pp_mass", "Average-mass", "#d18326"), ("pp_dis", "Disorder", "#2466a8"), ("pp_total", "Total", "#b42c48")]:
        axes[2].plot(z.T_K, z[key], "o-", ms=2.5, color=color, label=label)
    axes[0].set_ylabel(r"$\kappa_U-\kappa_D$ (W m$^{-1}$ K$^{-1}$)")
    axes[1].set_ylabel("Relative disorder difference (%)")
    axes[2].set_ylabel(r"Difference (pp of $\kappa_L$ on 14 cubed)")
    for i, ax in enumerate(axes):
        ax.set_xlabel("Temperature (K)")
        ax.set_title(f"({chr(97+i)})", loc="left")
        ax.legend(frameon=False, fontsize=7)
        if i:
            ax.axhline(0, color="0.6", lw=.7)
    finish(fig, "FigS24")


if __name__ == "__main__":
    dispatch({"S23": spectrum_and_mesh, "S24": difference_mesh})
