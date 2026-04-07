"""Risk layer: decide if a proposed trade is allowed before execution."""

from __future__ import annotations

from typing import Tuple


VALID_SIGNALS = {"BUY", "SELL", "HOLD"}


def can_trade(
    signal: str,
    has_data: bool,
    quantity: int,
    estimated_cost: float,
    cash_available: float,
    daily_pnl: float,
    max_daily_loss: float,
) -> Tuple[bool, str]:
    """Return whether a trade is allowed and why."""
    if signal not in VALID_SIGNALS:
        return False, f"Invalid signal: {signal}"
    if signal == "HOLD":
        return False, "No trade: HOLD signal"
    if not has_data:
        return False, "Missing market data"
    if quantity <= 0:
        return False, "Quantity must be positive"
    if estimated_cost <= 0:
        return False, "Estimated cost must be positive"
    if signal == "BUY" and estimated_cost > cash_available:
        return False, "Not enough cash"
    if daily_pnl <= -abs(max_daily_loss):
        return False, "Daily loss limit reached"
    return True, "Trade approved"
