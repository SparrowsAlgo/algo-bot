"""Strategy layer: abstract BUY/SELL/HOLD signal from market data."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class StrategyBase(ABC):
    """Interface for trading strategies."""

    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Return one of BUY, SELL, or HOLD."""
