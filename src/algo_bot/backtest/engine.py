"""Backtest layer: replay history using the same strategy and risk rules as paper mode."""

from __future__ import annotations

import pandas as pd

from algo_bot.backtest.metrics import compute_metrics
from algo_bot.risk.checks import can_trade
from algo_bot.trading.position_manager import should_exit_long


class BacktestEngine:
    """Run a basic single-symbol backtest."""

    def run(
        self,
        symbol: str,
        data: pd.DataFrame,
        strategy,
        quantity: int,
        starting_cash: float,
        max_daily_loss: float,
    ) -> dict:
        if data is None or data.empty or "Close" not in data.columns:
            return compute_metrics([], starting_cash, starting_cash)

        cash = float(starting_cash)
        held_qty = 0
        entry_price = 0.0
        stop_loss: float | None = None
        take_profit: float | None = None
        trade_pnls: list[float] = []
        daily_pnl = 0.0

        for i in range(2, len(data)):
            window = data.iloc[: i + 1]
            price = float(window["Close"].iloc[-1])

            # If holding, exit on stop/target first.
            if held_qty > 0:
                exit_decision = should_exit_long(price, stop_loss, take_profit)
                if exit_decision.should_exit:
                    cash += price * held_qty
                    pnl = (price - entry_price) * held_qty
                    trade_pnls.append(pnl)
                    daily_pnl += pnl
                    held_qty = 0
                    entry_price = 0.0
                    stop_loss = None
                    take_profit = None
                    continue

            decision = strategy.decide(symbol, window)
            signal = decision.action

            side = "HOLD"
            if signal == "BUY" and held_qty == 0:
                side = "BUY"
            elif signal == "SELL" and held_qty > 0:
                side = "SELL"

            allowed, _ = can_trade(
                signal=side,
                has_data=True,
                quantity=quantity,
                estimated_cost=price * quantity,
                cash_available=cash,
                daily_pnl=daily_pnl,
                max_daily_loss=max_daily_loss,
            )
            if not allowed:
                continue

            if side == "BUY":
                cash -= price * quantity
                held_qty = quantity
                entry_price = price
                stop_loss = decision.stop_loss
                take_profit = decision.take_profit
            elif side == "SELL":
                cash += price * held_qty
                pnl = (price - entry_price) * held_qty
                trade_pnls.append(pnl)
                daily_pnl += pnl
                held_qty = 0
                stop_loss = None
                take_profit = None

        final_price = float(data["Close"].iloc[-1])
        final_equity = cash + (held_qty * final_price)
        return compute_metrics(trade_pnls, final_equity, starting_cash)
