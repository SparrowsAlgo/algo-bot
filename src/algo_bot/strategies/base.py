"""Strategy layer: abstract BUY/SELL/HOLD signal from market data."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from algo_bot.strategies.decision import Decision


class StrategyBase(ABC):
    """Interface for trading strategies."""

    @abstractmethod
    def decide(self, symbol: str, data: pd.DataFrame) -> Decision:
        """Return a structured decision (action, score, reasons)."""

    def generate_signal(self, symbol: str, data: pd.DataFrame) -> str:
        """Compatibility helper: return only BUY/SELL/HOLD."""
        return self.decide(symbol, data).action
