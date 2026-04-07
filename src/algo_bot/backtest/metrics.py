"""Backtest layer: summarize equity curve and trade statistics."""

from __future__ import annotations

from typing import Any


def compute_metrics(trade_pnls: list[float], final_equity: float, starting_equity: float) -> dict[str, Any]:
    """Compute simple metrics from trade-level PnL."""
    total_return = 0.0
    if starting_equity > 0:
        total_return = (final_equity - starting_equity) / starting_equity

    wins = sum(1 for pnl in trade_pnls if pnl > 0)
    total_trades = len(trade_pnls)
    win_rate = (wins / total_trades) if total_trades > 0 else 0.0

    return {
        "starting_equity": starting_equity,
        "final_equity": final_equity,
        "total_return": total_return,
        "total_trades": total_trades,
        "win_rate": win_rate,
    }
