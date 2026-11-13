import re
import matplotlib.pyplot as plt

from plot_config import OUT


def change_labels(fig, stem):
    if stem == "Fig1":
        for ax in fig.axes[1:]:
            # User's final wording: Average-mass, not Average-mass difference.
            p = ax.get_position()
            ax.set_position([p.x0 + .02, p.y0, p.width - .02, p.height])
            ax.set_yticks([0, 1, 2], ["Total", "Disorder", "Average-mass"])
            ax.tick_params(axis="y", labelsize=8)
    elif stem == "Fig4":
        for ax in fig.axes[:2]:
            p = ax.get_position()
            dx = .16 / fig.get_figwidth()
            ax.set_position([p.x0 + dx, p.y0, p.width - dx, p.height])
        for ax in fig.axes:
            if ax.get_ylabel() == "Mean mass (pp)":
                ax.set_ylabel("Average-mass\ncontribution (pp)")
    elif stem == "Fig6":
        for ax in (fig.axes[0], fig.axes[2]):
            p = ax.get_position()
            dx = .10 / fig.get_figwidth()
            ax.set_position([p.x0 + dx, p.y0, p.width - dx, p.height])
        for ax in fig.axes:
            if ax.get_ylabel() == "Mass response (pp)":
                ax.set_ylabel("Average-mass\nresponse (pp)")
                ax.yaxis.label.set_fontsize(9)
    elif stem == "FigS13":
        ax = fig.axes[2]
        ax.set_title("(c) Three-phonon and isotope half-linewidths", loc="left", pad=3, fontsize=9.0)
        ax.set_ylabel("$q$-weighted median\nhalf-linewidth (THz)", labelpad=2)
        ax.lines[0].set_label("Three-phonon (U/D)")
        ax.lines[1].set_label("Isotope (D)")
        ax.legend(frameon=False, loc="lower right", handlelength=1.8)
    elif stem == "FigS22":
        a, b, c, d = fig.axes
        for line, text in zip(c.lines, ["Total reduction (%)", "Average-mass contribution (pp)", "Disorder contribution (pp)"]):
            line.set_label(text)
        c.set_ylabel("Total reduction (%) /\ncontribution (pp)", labelpad=2, fontsize=8.8)
        c.legend(frameon=False, loc="upper right", handlelength=1.6, fontsize=7.5)
        for container, text in zip(d.containers, ["Average-mass contribution", "Disorder contribution"]):
            container.set_label(text)
        d.set_ylabel("Contribution at 300 K (pp)", labelpad=2)
        d.legend(frameon=False, loc="upper left", handlelength=1.1, fontsize=7.4)
        for text in d.texts:
            if re.fullmatch(r"\d+\.\d{2}", text.get_text()):
                text.set_text(text.get_text() + "%")
        # Make the meaning of the retained negative labels explicit without changing their values.
        b.text(.5, .855, r"$100(\kappa_D-\kappa_L)/\kappa_L$ (%)",
               transform=b.transAxes, ha="center", va="center", fontsize=7.0)

def save_figure(fig, stem, dpi=450):
    change_labels(fig, stem)
    OUT.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "svg"):
        fig.savefig(OUT / f"{stem}.{suffix}", dpi=dpi, facecolor="white")
    plt.close(fig)
