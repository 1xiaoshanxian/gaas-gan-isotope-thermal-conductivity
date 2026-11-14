"""Supplementary lifetime, channel, mass and boundary plots from saved tables.

The scripts plot stored results. They do not evaluate FC3, regenerate force
constants, or infer full-zone channel contributions from selected modes.
"""
import numpy as np
from si_common import (plt, table, finish, dispatch, gap, MECHANISMS, COLORS)


def lifetimes():
    data = table(MECHANISMS, "LUD_lifetimes_300K.csv")
    fig, axes = plt.subplots(3, 2, figsize=(9.0, 8.7))
    keys = ["tau_qweighted_median_ps", "tau_eff_fixed_Cv2_U_ps",
            "kappaU_weighted_mode_tau_ratio"]
    labels = ["q-weighted median lifetime (ps)",
              "Effective lifetime, fixed U weights (ps)",
              r"$\langle\tau_s/\tau_U\rangle_{\kappa_U}$"]
    for col, material in enumerate(["GaN", "GaAs"]):
        for row, (key, ylabel) in enumerate(zip(keys, labels)):
            ax = axes[row, col]
            for state in ["L", "U", "D"]:
                z = data[(data.material == material) & (data.state == state)].sort_values("f_lo")
                x = (z.f_lo + z.f_hi) / 2
                ax.plot(x, z[key], color=COLORS[state], label=state)
            if row < 2:
                ax.set_yscale("log")
            else:
                ax.axhline(1, color="0.5", ls=":", lw=.7)
            if material == "GaN":
                gap(ax)
            ax.set(xlim=(0, 21.5 if material == "GaN" else 10),
                   xlabel="Reference U frequency (THz)", ylabel=ylabel)
            ax.set_title(f"({chr(97+row*2+col)}) {material}, 300 K", loc="left")
            ax.legend(frameon=False)
    finish(fig, "FigS12")


def branches():
    data = table(MECHANISMS, "branch_contributions_adopted_convention_all_T.csv")
    fig, axes = plt.subplots(1, 2, figsize=(8.1, 3.8))
    for ax, material, letter in zip(axes, ["GaN", "GaAs"], ["a", "b"]):
        z = data[(data.material == material) & (data.T_K == 300)].set_index("branch_group")
        bottom = np.zeros(2)
        for branch, color in [("acoustic", "#2466a8"), ("optical", "#b42c48")]:
            y = z.loc[branch, ["kappaU_share_pct", "isotope_loss_share_pct"]].to_numpy(float)
            ax.bar([0, 1], y, bottom=bottom, color=color, label=branch.capitalize())
            bottom += y
        np.testing.assert_allclose(bottom, [100, 100], atol=1e-8)
        ax.set_xticks([0, 1], [r"$\kappa_U$", r"$\kappa_U-\kappa_D$"])
        ax.set(ylim=(0, 105), ylabel="Share (%)")
        ax.set_title(f"({letter}) {material}, 300 K", loc="left")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False)
    finish(fig, "FigS14", rect=[0, 0, 1, .90])


def phase_space():
    data = table(MECHANISMS, "GaN_P3_frequency.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.7))
    for ax, process, letter in zip(axes, ["dec", "abs"], ["a", "b"]):
        for group, color in [("LL", "#2466a8"), ("LH", "#d18326"), ("HH", "#b42c48")]:
            y = data[f"P3{process}_{group}"].where(data.n_ir_modes > 0)
            ax.plot(data.f_THz, y, color=color, label=group)
        gap(ax)
        ax.set(xlabel="Initial-mode frequency (THz)", ylabel=r"$P_3$ (THz$^{-1}$)", xlim=(0, 21.5))
        ax.set_title(f"({letter}) " + ("Decay" if process == "dec" else "Absorption"), loc="left")
        ax.legend(frameon=False)
    finish(fig, "FigS15")


def gap_edges():
    data = table(MECHANISMS, "GaN_gap_edge_modes.csv")
    channels = [f"P3{process}_{group}" for process in ["dec", "abs"] for group in ["LL", "LH", "HH"]]
    fig = plt.figure(figsize=(10.2, 7.5))
    grid = fig.add_gridspec(2, 2, height_ratios=[1, 1.0])
    axes = [fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1]), fig.add_subplot(grid[1, :])]
    floor = 1e-6
    for ax, group, letter in zip(axes[:2], ["low", "high"], ["a", "b"]):
        z = data[data.group == group]
        for process, marker in [("dec", "o"), ("abs", "s")]:
            for partner, color in [("LL", "#2466a8"), ("LH", "#d18326"), ("HH", "#b42c48")]:
                y = z[f"P3{process}_{partner}"].to_numpy(float)
                ax.scatter(z.f_THz, np.maximum(y, floor), s=13, marker=marker,
                           facecolors=color if process == "dec" else "none",
                           edgecolors=color, linewidths=.7, label=f"{process} {partner}")
        ax.axhline(1e-3, color="0.4", ls="--", lw=.8)
        ax.set_yscale("log")
        ax.set(xlabel="Initial-mode frequency (THz)", ylabel=r"$P_3$ (THz$^{-1}$)", ylim=(floor*.7, None))
        ax.set_title(f"({letter}) {group}-group edge, n={len(z)}", loc="left")
        ax.legend(frameon=False, fontsize=7, ncol=2)
    ax = axes[2]
    x = np.arange(6)
    for group, offset, color in [("low", -.19, "#2466a8"), ("high", .19, "#a9c5e2")]:
        z = data[data.group == group]
        assert len(z) == {"low": 97, "high": 55}[group]
        counts = np.array([(z[key] > 1e-3).sum() for key in channels])
        fractions = counts / len(z)
        ax.bar(x+offset, fractions, width=.36, color=color, label=f"{group} edge")
        for xi, count, fraction, key in zip(x+offset, counts, fractions, channels):
            ax.text(xi, fraction+.025, f"{count}/{len(z)}", ha="center", fontsize=7)
            if not count:
                ax.plot([xi-.13, xi+.13], [.012, .012], color="0.2",
                        ls="-" if (z[key] == 0).all() else "--", lw=1.2)
    ax.set_xticks(x, [c.replace("P3", "").replace("_", " ") for c in channels])
    ax.set(ylim=(0, 1.22), ylabel=r"Fraction above $10^{-3}$ THz$^{-1}$")
    ax.set_title("(c) Detection fractions; exact zeros shown at the lower limit above", loc="left", fontsize=9)
    ax.legend(frameon=False, ncol=2, loc="upper right")
    finish(fig, "FigS16")


def channel_rates():
    data = table(MECHANISMS, "selected_clusters_channels.csv")
    fig, axes = plt.subplots(4, 2, figsize=(9.5, 11.5))
    for row, gp in enumerate([2129, 3369, 3391, 3799]):
        state = {s: data[(data.state == s) & (data.gp == gp)].sort_values("T_K") for s in ["L", "U"]}
        for process, color in [("total", "0.15"), ("dec", "#2466a8"), ("abs", "#d18326")]:
            rates = {}
            for s, z in state.items():
                rates[s] = z.gamma_native_THz.to_numpy() if process == "total" else z[
                    [f"{process}_{group}_gamma_THz" for group in ["LL", "LH", "HH"]]].sum(axis=1).to_numpy()
            x = state["U"].T_K
            axes[row, 0].semilogy(x, rates["U"], "o-", ms=3, color=color, label=process)
            ratio = np.divide(rates["L"], rates["U"], out=np.full_like(rates["U"], np.nan), where=rates["U"] > 1e-15)
            axes[row, 1].plot(x, 100*(ratio-1), "o-", ms=3, color=color, label=process)
        for col in [0, 1]:
            axes[row, col].set_xlabel("Temperature (K)")
            axes[row, col].set_title(f"({chr(97+row*2+col)}) gp={gp}, b={state['U'].branches_0based.iloc[0]}", loc="left")
            axes[row, col].legend(frameon=False, fontsize=8)
        axes[row, 0].set_ylabel("U-state half-linewidth (THz)")
        axes[row, 1].set_ylabel(r"$100(\gamma_L/\gamma_U-1)$ (%)")
        axes[row, 1].axhline(0, color="0.6", lw=.7)
    finish(fig, "FigS17")


def channel_shares():
    data = table(MECHANISMS, "selected_clusters_channels.csv")
    channels = [f"{p}_{g}" for p in ["dec", "abs"] for g in ["LL", "LH", "HH"]]
    colors = ["#2466a8", "#53a3cf", "#a5d3e7", "#b42c48", "#e0807b", "#f1bdb5"]
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 6.3))
    for ax, state in zip(axes, ["U", "L"]):
        z = data[(data.state == state) & (data.T_K == 300) & data.gp.isin([0, 3799])].sort_values(["gp", "branch_0based"])
        left = np.zeros(len(z))
        for key, color in zip(channels, colors):
            values = z[key+"_share_pct"].to_numpy()
            ax.barh(np.arange(len(z)), values, left=left, color=color, label=key.replace("_", " "))
            left += values
        np.testing.assert_allclose(left, np.full(len(z), 100), atol=1e-8)
        labels = [f"g{int(row.gp)}/b{row.branches_0based}\n{row.f_THz:.3f} THz, d={int(row.dimension)}" for row in z.itertuples()]
        ax.set_yticks(np.arange(len(z)), labels, fontsize=8)
        ax.invert_yaxis()
        ax.set(xlim=(0, 100), xlabel="Share of total half-linewidth (%)", title=state+", 300 K")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=6, frameon=False, fontsize=8)
    finish(fig, "FigS18", rect=[0, 0, 1, .94])


def mass_scaling():
    shifts = table(MECHANISMS, "GaN_mass_frequency_shifts.csv")
    edges = table(MECHANISMS, "GaN_gap_edges_LUH.csv").set_index("state").loc[["L", "U", "H"]]
    data = table(MECHANISMS, "GaN_mass_scaling_decomposition.csv")
    fig, axes = plt.subplots(2, 2, figsize=(9.4, 6.8))
    for state, color in [("L", COLORS["L"]), ("H", COLORS["H"])]:
        axes[0, 0].scatter(shifts.frequency_U_THz, shifts[f"shift_{state}_minus_U_THz"], s=2,
                           alpha=.4, color=color, label=state+" - U", rasterized=True)
    axes[0, 0].set(xlabel="U-state frequency (THz)", ylabel="Frequency shift (THz)")
    axes[0, 0].legend(frameon=False)
    axes[0, 1].bar(edges.index, edges.gap_THz, color=[COLORS[s] for s in edges.index])
    axes[0, 1].set(ylim=(5.1, 5.35), ylabel="Sampled frequency-group gap (THz)")
    for state in ["U", "H"]:
        axes[1, 0].plot(data.T_K, data["kappa_"+state]/data.kappa_L, "o-", ms=3, label=state+"/L")
    axes[1, 0].set(xlabel="Temperature (K)", ylabel="RTA conductivity ratio (zz)")
    axes[1, 0].legend(frameon=False)
    for key, label, color in [("term_Cv", "C", "0.4"), ("term_v2_star", "k-star geometry", "#d18326"), ("term_tau", "Lifetime", "#b42c48")]:
        axes[1, 1].plot(data.T_K, data[key], label=label, color=color)
    axes[1, 1].plot(data.T_K, data.log_ratio, "k.", label="Total log ratio")
    axes[1, 1].set(xlabel="Temperature (K)", ylabel="Sequential logarithmic terms")
    axes[1, 1].legend(frameon=False, fontsize=8)
    for i, ax in enumerate(axes.ravel()):
        ax.set_title(f"({chr(97+i)})", loc="left")
    finish(fig, "FigS19")


def boundary_sensitivity():
    cumulative = table(MECHANISMS, "mfp_cumulative.csv")
    boundary = table(MECHANISMS, "boundary_sensitivity.csv")
    fig, axes = plt.subplots(2, 2, figsize=(9.0, 6.8))
    for col, material in enumerate(["GaAs", "GaN"]):
        for state in ["U", "D"]:
            z = cumulative[(cumulative.material == material) & (cumulative.state == state)].sort_values("mfp_upper_um")
            axes[0, col].semilogx(z.mfp_upper_um, 100*z.cumulative_fraction, color=COLORS[state], label=state)
        z = boundary[(boundary.material == material) & (boundary.T_K == 300) & np.isfinite(boundary.boundary_length_um)].sort_values("boundary_length_um")
        axes[1, col].semilogx(z.boundary_length_um, 100*z.disorder_suppression_fraction_U, "o-", ms=3, label=r"$U\rightarrow D$, normalized by $\kappa_U$")
        axes[1, col].semilogx(z.boundary_length_um, 100*z.total_loss_fraction_L, "s--", ms=3, label=r"$L\rightarrow D$, normalized by $\kappa_L$")
        axes[0, col].set(xlabel="Mean free path (micrometers)", ylabel="Cumulative conductivity (%)", ylim=(0, 103))
        axes[1, col].set(xlabel="Assumed boundary length (micrometers)", ylabel="Conductivity reduction (%)")
        for row in [0, 1]:
            axes[row, col].set_title(f"({chr(97+row*2+col)}) {material}, 300 K", loc="left")
            axes[row, col].legend(frameon=False, fontsize=7.5)
    finish(fig, "FigS20")


def low_frequency():
    modes = table(MECHANISMS, "low_frequency_isotope_modes.csv")
    fits = table(MECHANISMS, "low_frequency_isotope_rate_fits.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.8))
    for ax, material in zip(axes, ["GaN", "GaAs"]):
        z = modes[modes.material == material]
        f, g, w = z.frequency_THz.to_numpy(), z.gamma_isotope_THz.to_numpy(), z.q_weight.to_numpy()
        ax.loglog(f, g, ".", ms=2, color="0.6", alpha=.4, rasterized=True)
        for (_, row), color in zip(fits[fits.material == material].iterrows(), ["#2466a8", "#d18326", "#b42c48"]):
            valid = (f >= row.f_lo_THz) & (f <= row.f_hi_THz)
            x, y, weight = np.log(f[valid]), np.log(g[valid]), w[valid]
            xc, yc = np.average(x, weights=weight), np.average(y, weights=weight)
            slope = np.sum(weight*(x-xc)*(y-yc))/np.sum(weight*(x-xc)**2)
            np.testing.assert_allclose(slope, row.log_slope, atol=1e-9)
            assert valid.sum() == int(row.n_ir_modes)
            xx = np.geomspace(row.f_lo_THz, row.f_hi_THz, 100)
            ax.loglog(xx, np.exp(yc-slope*xc)*xx**slope, color=color,
                      label=f"{row.f_lo_THz:g}-{row.f_hi_THz:g} THz: {slope:.2f}, n={valid.sum()}")
        anchor = (f > .5) & (f < 1.5)
        coefficient = np.exp(np.average(np.log(g[anchor]/f[anchor]**4), weights=w[anchor]))
        xx = np.geomspace(.3, 3, 100)
        ax.loglog(xx, coefficient*xx**4, "k--", lw=.8, label=r"Scaled $f^4$ guide")
        ax.set(xlim=(.2, 3), xlabel="Frequency (THz)", ylabel="Isotope half-linewidth (THz)")
        ax.set_title(material, loc="left")
        ax.legend(frameon=False, fontsize=6.8)
    finish(fig, "FigS21")


if __name__ == "__main__":
    dispatch({"S12": lifetimes, "S14": branches, "S15": phase_space,
              "S16": gap_edges, "S17": channel_rates, "S18": channel_shares,
              "S19": mass_scaling, "S20": boundary_sensitivity, "S21": low_frequency})
