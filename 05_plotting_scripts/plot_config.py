from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
MAIN_DATA = ROOT / "03_main_data"
SUPPLEMENTARY_DATA = ROOT / "04_supplementary_data"
OUT = Path(os.environ.get("PLOT_OUTPUT_DIR", ROOT / "figures"))
