"""Portfolio layer: small types and helpers for open positions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Position:
    """Simple equity position state."""

    symbol: str
    quantity: int = 0
    avg_price: float = 0.0


def has_position(positions: dict[str, Position], symbol: str) -> bool:
    """Return True if a symbol is currently held."""
    position = positions.get(symbol)
    return bool(position and position.quantity > 0)
