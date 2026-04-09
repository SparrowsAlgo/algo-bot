"""Portfolio layer: cash, open positions, and trade log for paper accounting."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from algo_bot.portfolio.positions import Position, has_position
from algo_bot.trading.trade_plan import TradePlan


class PortfolioManager:
    """Track cash and positions with simple exposure limits."""

    def __init__(self, starting_cash: float) -> None:
        self.cash = float(starting_cash)
        self.daily_pnl = 0.0
        self.positions: dict[str, Position] = {}
        self.last_trade_time: str | None = None
        self.trades: list[dict[str, Any]] = []
        self.realized_pnl: float = 0.0
        self.last_action: str | None = None

    def has_position(self, symbol: str) -> bool:
        return has_position(self.positions, symbol)

    def can_open_position(self, price: float, quantity: int) -> bool:
        return price > 0 and quantity > 0 and (price * quantity) <= self.cash

    def apply_fill(self, symbol: str, side: str, quantity: int, price: float) -> None:
        """Update cash and positions after a fill (legacy helper)."""
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
            self.realized_pnl += realized
            current.quantity -= sell_qty
            if current.quantity == 0:
                self.positions.pop(symbol, None)
        else:
            return

        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self.last_trade_time = now
        self.last_action = f"{side}:{symbol}"

    def open_from_plan(self, plan: TradePlan, fill: dict[str, Any]) -> None:
        """Open/update a position based on a TradePlan and a broker fill."""
        if fill.get("status") != "filled":
            return
        symbol = plan.symbol
        qty = int(fill.get("quantity") or 0)
        price = float(fill.get("price") or 0.0)
        if qty <= 0 or price <= 0:
            return

        cost = qty * price
        if cost > self.cash:
            return

        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self.cash -= cost

        current = self.positions.get(symbol, Position(symbol=symbol))
        new_qty = current.quantity + qty
        if new_qty > 0:
            current.avg_price = ((current.avg_price * current.quantity) + cost) / new_qty
        current.quantity = new_qty
        current.stop_loss = float(plan.stop_loss)
        current.take_profit = float(plan.take_profit)
        current.opened_at = current.opened_at or now
        current.last_updated = now
        self.positions[symbol] = current

        self.last_trade_time = now
        self.last_action = f"OPEN:{symbol}"

    def close_position(self, symbol: str, fill: dict[str, Any], reason: str) -> float:
        """Close a position and return realized PnL."""
        if fill.get("status") != "filled":
            return 0.0

        current = self.positions.get(symbol)
        if current is None or current.quantity <= 0:
            return 0.0

        qty = int(fill.get("quantity") or 0)
        price = float(fill.get("price") or 0.0)
        if qty <= 0 or price <= 0:
            return 0.0

        sell_qty = min(qty, current.quantity)
        proceeds = sell_qty * price
        pnl = (price - current.avg_price) * sell_qty

        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self.cash += proceeds
        self.daily_pnl += pnl
        self.realized_pnl += pnl

        current.quantity -= sell_qty
        current.realized_pnl += pnl
        current.last_updated = now
        if current.quantity == 0:
            self.positions.pop(symbol, None)
        else:
            self.positions[symbol] = current

        self.last_trade_time = now
        self.last_action = f"CLOSE:{symbol}:{reason}"
        return float(pnl)

    def append_trade(self, trade: dict[str, Any]) -> None:
        """Append one trade to the event log (audit trail)."""
        self.trades.append(trade)

    @classmethod
    def from_state(cls, state: dict[str, Any], starting_cash: float) -> "PortfolioManager":
        """Build a portfolio manager from persisted JSON state."""
        portfolio = cls(starting_cash=starting_cash)
        portfolio.cash = float(state.get("cash", starting_cash))
        portfolio.last_trade_time = state.get("last_trade_time")
        portfolio.realized_pnl = float(state.get("realized_pnl", 0.0))
        portfolio.last_action = state.get("last_action")

        raw_positions = state.get("positions", {})
        if isinstance(raw_positions, dict):
            for symbol, payload in raw_positions.items():
                if not isinstance(payload, dict):
                    continue
                portfolio.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=int(payload.get("quantity", 0)),
                    avg_price=float(payload.get("avg_price", 0.0)),
                    stop_loss=(float(payload["stop_loss"]) if payload.get("stop_loss") is not None else None),
                    take_profit=(float(payload["take_profit"]) if payload.get("take_profit") is not None else None),
                    opened_at=payload.get("opened_at"),
                    last_updated=payload.get("last_updated"),
                    realized_pnl=float(payload.get("realized_pnl", 0.0)),
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
                symbol: {
                    "quantity": pos.quantity,
                    "avg_price": pos.avg_price,
                    "stop_loss": pos.stop_loss,
                    "take_profit": pos.take_profit,
                    "opened_at": pos.opened_at,
                    "last_updated": pos.last_updated,
                    "realized_pnl": pos.realized_pnl,
                }
                for symbol, pos in self.positions.items()
                if pos.quantity > 0
            },
            "last_trade_time": self.last_trade_time,
            "trades": list(self.trades),
            "realized_pnl": self.realized_pnl,
            "last_action": self.last_action,
        }
