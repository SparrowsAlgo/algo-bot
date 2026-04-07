"""Risk layer: map account settings to an order size (fixed shares here)."""

from __future__ import annotations


def fixed_position_size(trade_size: int) -> int:
    """Return a fixed number of shares, never negative."""
    return max(0, int(trade_size))
