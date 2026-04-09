"""Scanner layer: loop through a watchlist and create per-symbol decisions (no trading)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from algo_bot.data.features import add_basic_features
from algo_bot.data.market_data import MarketDataClient
from algo_bot.strategies.decision import Decision
from algo_bot.strategies.simple_ma import SimpleMAStrategy


@dataclass(frozen=True)
class ScanResult:
    """One symbol evaluation from the scanner."""

    symbol: str
    action: str
    score: float
    reasons: list[str]
    current_price: float | None
    stop_loss: float | None
    take_profit: float | None
    trend: str | None
    volatility: float | None
    timestamp: str


def scan_symbol(
    symbol: str,
    data_client: MarketDataClient,
    strategy: SimpleMAStrategy,
    lookback_period: str,
    interval: str,
) -> ScanResult:
    """Fetch data, build features, and create one scan result."""
    raw = data_client.get_history(symbol, lookback_period, interval)
    features = add_basic_features(raw)
    decision: Decision = strategy.decide(symbol, features)

    return ScanResult(
        symbol=symbol,
        action=decision.action,
        score=float(decision.score),
        reasons=list(decision.reasons),
        current_price=decision.current_price,
        stop_loss=decision.stop_loss,
        take_profit=decision.take_profit,
        trend=decision.trend,
        volatility=decision.volatility,
        timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    )


def scan_watchlist(
    watchlist: list[str],
    lookback_period: str,
    interval: str,
) -> list[ScanResult]:
    """Scan all symbols and return results."""
    data_client = MarketDataClient()
    strategy = SimpleMAStrategy()

    results: list[ScanResult] = []
    for symbol in watchlist:
        try:
            results.append(scan_symbol(symbol, data_client, strategy, lookback_period, interval))
        except Exception as exc:
            results.append(
                ScanResult(
                    symbol=symbol,
                    action="HOLD",
                    score=0.0,
                    reasons=[f"scanner error: {exc}"],
                    current_price=None,
                    stop_loss=None,
                    take_profit=None,
                    trend=None,
                    volatility=None,
                    timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                )
            )
    return results

