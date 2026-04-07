"""Data layer: download and normalize historical OHLCV for strategies."""

from __future__ import annotations

import pandas as pd
import yfinance as yf


class MarketDataClient:
    """Fetch historical OHLCV market data via yfinance."""

    def get_history(self, symbol: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
        """Return clean price history for the given symbol."""
        if not symbol:
            return pd.DataFrame()

        data = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=False)
        if data is None or data.empty:
            return pd.DataFrame()

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]

        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        for column in required_columns:
            if column not in data.columns:
                data[column] = pd.NA

        data = data[required_columns].dropna(subset=["Close"]).copy()
        return data
