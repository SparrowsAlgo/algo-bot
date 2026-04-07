"""Strategy layer: simple moving-average crossover implementation."""

from __future__ import annotations

import pandas as pd

from algo_bot.strategies.base import StrategyBase


class SimpleMAStrategy(StrategyBase):
    """Generate BUY/SELL/HOLD based on MA crossover."""

    def __init__(self, short_window: int = 5, long_window: int = 20) -> None:
        self.short_window = short_window
        self.long_window = long_window

    def generate_signal(self, data: pd.DataFrame) -> str:
        """Generate a signal from closing prices."""
        if data is None or data.empty or "Close" not in data.columns:
            return "HOLD"
        if len(data) < 2:
            return "HOLD"

        close = data["Close"]
        ma_short = close.rolling(window=self.short_window, min_periods=1).mean()
        ma_long = close.rolling(window=self.long_window, min_periods=1).mean()

        if ma_short.iloc[-1] > ma_long.iloc[-1]:
            return "BUY"
        if ma_short.iloc[-1] < ma_long.iloc[-1]:
            return "SELL"
        return "HOLD"
