"""Generate every figure supported by this public package."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

SCRIPTS = ["fig1.py", "fig2.py", "fig3_4.py", "fig5_6.py",
           "fig_s1.py", "fig_s4_s8.py", "fig_s9_s10.py", "fig_s11.py",
           "fig_s12_s21.py", "fig_s13.py", "fig_s22.py", "fig_s23_s24.py", "fig_s25.py"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Output directory; default: package figures/.")
    parser.add_argument("--list", action="store_true", help="List entry scripts without executing them.")
    args = parser.parse_args()
    if args.list:
        print("\n".join(SCRIPTS))
        return
    environment = os.environ.copy()
    environment["MPLBACKEND"] = "Agg"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    if args.output:
        environment["PLOT_OUTPUT_DIR"] = str(args.output.resolve())
    directory = Path(__file__).resolve().parent
    for name in SCRIPTS:
        print("Running " + name, flush=True)
        subprocess.run([sys.executable, "-B", str(directory / name)],
                       env=environment, check=True)
    print("All public figure scripts completed.", flush=True)


if __name__ == "__main__":
    main()
