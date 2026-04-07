"""Compatibility entry point: delegates to the same paper flow as `python scripts/run.py paper`."""

from __future__ import annotations

from algo_bot.runners import run_paper_mode


def main() -> None:
    run_paper_mode()


if __name__ == "__main__":
    main()
