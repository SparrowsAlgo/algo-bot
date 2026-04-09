"""Strategy layer: shared decision object with score and explanations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Decision:
    """A structured strategy decision for one symbol at one point in time."""

    symbol: str
    action: str  # BUY / SELL / HOLD
    score: float
    reasons: list[str] = field(default_factory=list)
    current_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    trend: str | None = None
    volatility: float | None = None

