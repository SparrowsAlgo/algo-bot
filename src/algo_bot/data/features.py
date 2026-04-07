"""Data layer: derive indicators and returns from price series."""

from __future__ import annotations

import pandas as pd


def add_basic_features(data: pd.DataFrame, short_window: int = 5, long_window: int = 20) -> pd.DataFrame:
    """Add simple moving averages and returns.

    The function is defensive and returns an empty frame for invalid input.
    """
    if data is None or data.empty:
        return pd.DataFrame()

    features = data.copy()
    if "Close" not in features.columns:
        return pd.DataFrame()

    features["returns"] = features["Close"].pct_change().fillna(0.0)
    features["ma_short"] = features["Close"].rolling(window=short_window, min_periods=1).mean()
    features["ma_long"] = features["Close"].rolling(window=long_window, min_periods=1).mean()
    return features.dropna(how="all")
