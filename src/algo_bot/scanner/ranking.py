"""Scanner ranking: sort scan results and select top candidates."""

from __future__ import annotations

from algo_bot.scanner.scanner import ScanResult


def rank_scan_results(results: list[ScanResult]) -> list[ScanResult]:
    """Sort results by action priority and score (highest first)."""
    action_priority = {"BUY": 0, "HOLD": 1, "SELL": 2}

    return sorted(
        results,
        key=lambda r: (action_priority.get(r.action, 99), -float(r.score)),
    )


def top_candidates(results: list[ScanResult], limit: int = 3) -> list[ScanResult]:
    """Return the best BUY candidates (or empty list)."""
    ranked = rank_scan_results(results)
    buys = [r for r in ranked if r.action == "BUY"]
    return buys[: max(0, int(limit))]

