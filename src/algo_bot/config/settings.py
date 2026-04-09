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


def _parse_watchlist(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return list(default)
    parts = [p.strip().upper() for p in value.split(",")]
    symbols = [p for p in parts if p]
    return symbols or list(default)


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for the trading app."""

    symbol: str
    watchlist: list[str]
    lookback_period: str
    interval: str
    paper_mode: bool
    trade_size: int
    max_daily_loss: float
    starting_cash: float
    broker_name: str
    broker_api_key: str
    broker_secret_key: str
    risk_per_trade_pct: float
    risk_reward: float


def load_settings() -> Settings:
    """Load settings from environment variables with safe defaults."""
    default_watchlist = ["AAPL", "MSFT", "NVDA", "SPY", "QQQ"]
    return Settings(
        symbol=os.getenv("SYMBOL", "AAPL"),
        watchlist=_parse_watchlist(os.getenv("WATCHLIST"), default_watchlist),
        lookback_period=os.getenv("LOOKBACK_PERIOD", "3mo"),
        interval=os.getenv("INTERVAL", "1d"),
        paper_mode=_to_bool(os.getenv("PAPER_MODE"), True),
        trade_size=int(os.getenv("TRADE_SIZE", "1")),
        max_daily_loss=float(os.getenv("MAX_DAILY_LOSS", "500.0")),
        starting_cash=float(os.getenv("STARTING_CASH", "10000.0")),
        broker_name=os.getenv("BROKER_NAME", "paper"),
        broker_api_key=os.getenv("BROKER_API_KEY", ""),
        broker_secret_key=os.getenv("BROKER_SECRET_KEY", ""),
        risk_per_trade_pct=float(os.getenv("RISK_PER_TRADE_PCT", "0.01")),
        risk_reward=float(os.getenv("RISK_REWARD", "2.0")),
    )


SETTINGS = load_settings()
