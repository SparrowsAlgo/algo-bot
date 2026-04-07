"""Execution layer: simulate order submission and fills without a live broker."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from algo_bot.execution.broker_base import BrokerBase


class PaperBroker(BrokerBase):
    """Simulate order execution for testing and learning."""

    def __init__(self) -> None:
        self.orders: List[dict[str, Any]] = []
        self._positions: Dict[str, int] = {}

    def submit_order(self, symbol: str, side: str, quantity: int, price: float) -> dict[str, Any]:
        filled_qty = quantity if side in {"BUY", "SELL"} and quantity > 0 else 0
        if side == "BUY":
            self._positions[symbol] = self._positions.get(symbol, 0) + filled_qty
        elif side == "SELL":
            self._positions[symbol] = max(0, self._positions.get(symbol, 0) - filled_qty)

        submitted_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        filled_at = submitted_at if filled_qty > 0 else ""

        order: dict[str, Any] = {
            "status": "filled" if filled_qty > 0 else "rejected",
            "symbol": symbol,
            "side": side,
            "quantity": filled_qty,
            "price": float(price),
            "submitted_at": submitted_at,
            "filled_at": filled_at,
        }
        self.orders.append(order)
        return order

    def get_positions(self) -> List[dict]:
        return [{"symbol": symbol, "quantity": qty} for symbol, qty in self._positions.items() if qty > 0]
