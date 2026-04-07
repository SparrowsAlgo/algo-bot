#!/usr/bin/env python3
"""Single entry point: backtest | paper | status."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from algo_bot.runners import run_backtest_mode, run_paper_mode, run_status_mode

USAGE = """
Algo Bot - choose a mode:

  python scripts/run.py backtest   Run a historical backtest and print metrics
  python scripts/run.py paper      Run one simulated paper-trading cycle
  python scripts/run.py status     Show cash, positions, and trade history

Examples:
  python scripts/run.py backtest
  python scripts/run.py paper
  python scripts/run.py status
""".strip()


def main() -> None:
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    mode = sys.argv[1].strip().lower()
    if mode == "backtest":
        run_backtest_mode()
    elif mode == "paper":
        run_paper_mode()
    elif mode == "status":
        run_status_mode()
    else:
        print(f"Unknown mode: {sys.argv[1]!r}\n")
        print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
