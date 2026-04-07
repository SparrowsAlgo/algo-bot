"""Thin wrapper: prefer `python scripts/run.py paper`."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from algo_bot.runners import run_paper_mode

if __name__ == "__main__":
    run_paper_mode()
