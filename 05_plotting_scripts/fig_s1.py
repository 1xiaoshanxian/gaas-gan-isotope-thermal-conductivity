"""S1: reevaluate the published GaAs NEP on its 207 training configurations."""
import shutil
import tempfile
from pathlib import Path
import numpy as np
from ase.io import iread
from calorine.calculators import CPUNEP
from plot_config import ROOT
from si_common import plt, finish


def main():
    reference = [[], [], []]
    prediction = [[], [], []]
    directory = ROOT / "01_nep_models" / "GaAs"
    # A temporary ASCII-named model file also supports Windows C++ readers.
    with tempfile.TemporaryDirectory(prefix="nep_plot_") as temporary:
        model = Path(temporary) / "nep.txt"
        shutil.copyfile(directory / "nep.txt", model)
        calculator = CPUNEP(str(model))
        count = 0
        for atoms in iread(directory / "train.xyz", index=":", format="extxyz"):
            n = len(atoms)
            energy = float(atoms.info["Energy"]) / n
            forces = atoms.arrays["force"].copy()
            stress = -np.asarray(atoms.info["Virial"]).reshape(3, 3) / atoms.get_volume()
            atoms.calc = calculator
            reference[0].append(energy)
            prediction[0].append(atoms.get_potential_energy() / n)
            reference[1].extend(forces.ravel())
            prediction[1].extend(atoms.get_forces().ravel())
            indices = np.triu_indices(3)
            reference[2].extend(stress[indices] * 160.21766208)
            prediction[2].extend(atoms.get_stress(voigt=False)[indices] * 160.21766208)
            count += 1
    assert count == 207
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.6))
    labels = ["Energy (eV/atom)", "Force (eV/angstrom)", "Stress (GPa)"]
    for i, (ax, label) in enumerate(zip(axes, labels)):
        x, y = np.asarray(reference[i]), np.asarray(prediction[i])
        assert np.isfinite(x).all() and np.isfinite(y).all()
        ax.scatter(x, y, s=2, color="#2466a8", alpha=.22, rasterized=True)
        lo, hi = min(x.min(), y.min()), max(x.max(), y.max())
        ax.plot([lo, hi], [lo, hi], "--", color="0.35", lw=.8)
        ax.set(xlabel="DFT " + label, ylabel="NEP " + label)
        ax.set_title(f"({chr(97+i)})", loc="left")
        residual = y-x
        inset = ax.inset_axes([.60, .10, .35, .26])
        inset.hist(residual, bins=35, color="#b42c48", alpha=.75)
        inset.set_title(f"RMSE={np.sqrt(np.mean(residual**2)):.3g}", fontsize=7)
        inset.tick_params(labelsize=6)
    finish(fig, "FigS1")


if __name__ == "__main__":
    main()
