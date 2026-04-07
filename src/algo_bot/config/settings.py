"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for the trading app."""

    symbol: str
    lookback_period: str
    interval: str
    paper_mode: bool
    trade_size: int
    max_daily_loss: float
    starting_cash: float
    broker_name: str
    broker_api_key: str
    broker_secret_key: str


def load_settings() -> Settings:
    """Load settings from environment variables with safe defaults."""
    return Settings(
        symbol=os.getenv("SYMBOL", "AAPL"),
        lookback_period=os.getenv("LOOKBACK_PERIOD", "3mo"),
        interval=os.getenv("INTERVAL", "1d"),
        paper_mode=_to_bool(os.getenv("PAPER_MODE"), True),
        trade_size=int(os.getenv("TRADE_SIZE", "1")),
        max_daily_loss=float(os.getenv("MAX_DAILY_LOSS", "500.0")),
        starting_cash=float(os.getenv("STARTING_CASH", "10000.0")),
        broker_name=os.getenv("BROKER_NAME", "paper"),
        broker_api_key=os.getenv("BROKER_API_KEY", ""),
        broker_secret_key=os.getenv("BROKER_SECRET_KEY", ""),
    )


SETTINGS = load_settings()
