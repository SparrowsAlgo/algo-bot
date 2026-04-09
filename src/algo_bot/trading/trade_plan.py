"""Trading layer: a TradePlan represents a complete trade idea before execution."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TradePlan:
    """A full trade idea before execution (entry, stop, target, size, and rationale)."""

    symbol: str
    action: str  # BUY / SELL / HOLD
    entry_price: float
    stop_loss: float
    take_profit: float
    quantity: int

    risk_per_share: float
    total_risk: float
    expected_reward: float
    risk_reward_ratio: float

    score: float
    reasons: list[str] = field(default_factory=list)
    timestamp: str | None = None

