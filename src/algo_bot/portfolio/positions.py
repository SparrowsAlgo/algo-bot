"""Portfolio layer: small types and helpers for open positions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Position:
    """Simple equity position state (paper mode)."""

    symbol: str
    quantity: int = 0
    avg_price: float = 0.0
    stop_loss: float | None = None
    take_profit: float | None = None
    opened_at: str | None = None
    last_updated: str | None = None
    realized_pnl: float = 0.0


def has_position(positions: dict[str, Position], symbol: str) -> bool:
    """Return True if a symbol is currently held."""
    position = positions.get(symbol)
    return bool(position and position.quantity > 0)
