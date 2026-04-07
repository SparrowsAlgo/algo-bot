"""Portfolio layer: cash, open positions, and trade log for paper accounting."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from algo_bot.portfolio.positions import Position, has_position


class PortfolioManager:
    """Track cash and positions with simple exposure limits."""

    def __init__(self, starting_cash: float) -> None:
        self.cash = float(starting_cash)
        self.daily_pnl = 0.0
        self.positions: dict[str, Position] = {}
        self.last_trade_time: str | None = None
        self.trades: list[dict[str, Any]] = []

    def has_position(self, symbol: str) -> bool:
        return has_position(self.positions, symbol)

    def can_open_position(self, price: float, quantity: int) -> bool:
        return price > 0 and quantity > 0 and (price * quantity) <= self.cash

    def apply_fill(self, symbol: str, side: str, quantity: int, price: float) -> None:
        """Update cash and positions after a fill."""
        if quantity <= 0 or price <= 0:
            return

        if side == "BUY":
            cost = quantity * price
            if cost > self.cash:
                return
            self.cash -= cost
            current = self.positions.get(symbol, Position(symbol=symbol))
            new_qty = current.quantity + quantity
            if new_qty > 0:
                current.avg_price = ((current.avg_price * current.quantity) + cost) / new_qty
            current.quantity = new_qty
            self.positions[symbol] = current
        elif side == "SELL":
            current = self.positions.get(symbol)
            if current is None or current.quantity <= 0:
                return
            sell_qty = min(quantity, current.quantity)
            proceeds = sell_qty * price
            realized = (price - current.avg_price) * sell_qty
            self.cash += proceeds
            self.daily_pnl += realized
            current.quantity -= sell_qty
            if current.quantity == 0:
                self.positions.pop(symbol, None)
        else:
            return

        self.last_trade_time = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def append_trade(self, trade: dict[str, Any]) -> None:
        """Append one trade to the event log (audit trail)."""
        self.trades.append(trade)

    @classmethod
    def from_state(cls, state: dict[str, Any], starting_cash: float) -> "PortfolioManager":
        """Build a portfolio manager from persisted JSON state."""
        portfolio = cls(starting_cash=starting_cash)
        portfolio.cash = float(state.get("cash", starting_cash))
        portfolio.last_trade_time = state.get("last_trade_time")

        raw_positions = state.get("positions", {})
        if isinstance(raw_positions, dict):
            for symbol, payload in raw_positions.items():
                if not isinstance(payload, dict):
                    continue
                portfolio.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=int(payload.get("quantity", 0)),
                    avg_price=float(payload.get("avg_price", 0.0)),
                )

        raw_trades = state.get("trades", [])
        if isinstance(raw_trades, list):
            portfolio.trades = [t for t in raw_trades if isinstance(t, dict)]

        return portfolio

    def to_state(self) -> dict[str, Any]:
        """Serialize portfolio state for disk storage."""
        return {
            "cash": self.cash,
            "positions": {
                symbol: {"quantity": pos.quantity, "avg_price": pos.avg_price}
                for symbol, pos in self.positions.items()
                if pos.quantity > 0
            },
            "last_trade_time": self.last_trade_time,
            "trades": list(self.trades),
        }
