from pathlib import Path
import sys
import argparse

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from typing_ai.cli import run_cli
from typing_ai.gui import run_gui


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Typing AI Scratch")
    parser.add_argument("--gui", action="store_true", help="Run Tkinter GUI mode")
    parser.add_argument("--cli", action="store_true", help="Run terminal CLI mode")
    args = parser.parse_args()

    if args.gui and args.cli:
        print("Choose only one mode: --gui or --cli")
        raise SystemExit(2)

    if args.gui:
        run_gui()
    else:
        run_cli()
