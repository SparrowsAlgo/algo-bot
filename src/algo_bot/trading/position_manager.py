"""Trading layer: manage open positions and decide when to exit (stop/target)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExitDecision:
    """A simple decision about closing an open position."""

    should_exit: bool
    reason: str


def should_exit_long(
    current_price: float,
    stop_loss: float | None,
    take_profit: float | None,
) -> ExitDecision:
    """Return whether a long position should be closed based on stop/target."""
    if current_price <= 0:
        return ExitDecision(False, "invalid price")
    if stop_loss is not None and current_price <= float(stop_loss):
        return ExitDecision(True, "stop_loss_hit")
    if take_profit is not None and current_price >= float(take_profit):
        return ExitDecision(True, "take_profit_hit")
    return ExitDecision(False, "hold")

