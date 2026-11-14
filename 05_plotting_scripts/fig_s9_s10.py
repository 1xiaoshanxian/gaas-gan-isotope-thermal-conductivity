"""S9-S10: reference-state diagnostics and the saved LBTE/RTA differences."""
from si_common import plt, table, finish, dispatch, MAIN_DATA, TRANSPORT


def reference_states():
    data = table(MAIN_DATA, "rta_five_state_contributions.csv")
    fig, axes = plt.subplots(1, 2, figsize=(8.3, 3.5))
    for ax, material, letter in zip(axes, ["GaAs", "GaN"], ["a", "b"]):
        z = data[data.material == material].sort_values("T")
        ax.plot(z["T"], z.endpoint_bias_pp, "o-", ms=3, label="Endpoint deviation E")
        ax.plot(z["T"], z.path_difference_pp, "s--", ms=3, label="Background difference B")
        ax.axhline(0, color="0.6", lw=.7)
        ax.set(xlabel="Temperature (K)", ylabel="Difference (pp)")
        ax.set_title(f"({letter}) {material}", loc="left")
        ax.legend(frameon=False, fontsize=8)
    finish(fig, "FigS9")


def solver_comparison():
    data = table(TRANSPORT, "lbte_rta_comparison.csv")
    fig, axes = plt.subplots(2, 2, figsize=(8.3, 6.3))
    for col, material in enumerate(["GaAs", "GaN"]):
        z = data[data.material == material].sort_values("temperature_K")
        for row, quantity in enumerate(["mass", "disorder"]):
            ax = axes[row, col]
            for method, style in [("LBTE", "o-"), ("RTA", "s--")]:
                ax.plot(z.temperature_K, z[f"{quantity}_{method}_W_mK"],
                        style, ms=3, label=method)
            if row:
                ax.set_yscale("log")
            ax.axhline(0, color="0.7", lw=.6) if not row else None
            ax.set(xlabel="Temperature (K)",
                   ylabel=(r"$\kappa_L-\kappa_U$" if row == 0 else r"$\kappa_U-\kappa_D$")
                   + r" (W m$^{-1}$ K$^{-1}$)")
            ax.set_title(f"({chr(97+row*2+col)}) {material}", loc="left")
            ax.legend(frameon=False)
    finish(fig, "FigS10")


if __name__ == "__main__":
    dispatch({"S9": reference_states, "S10": solver_comparison})
