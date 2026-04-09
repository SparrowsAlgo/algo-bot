"""Strategy layer: simple moving-average crossover implementation."""

from __future__ import annotations

import pandas as pd

from algo_bot.strategies.base import StrategyBase
from algo_bot.strategies.decision import Decision


class SimpleMAStrategy(StrategyBase):
    """Generate BUY/SELL/HOLD based on MA crossover."""

    def __init__(self, short_window: int = 5, long_window: int = 20) -> None:
        self.short_window = short_window
        self.long_window = long_window

    def decide(self, symbol: str, data: pd.DataFrame) -> Decision:
        """Score a symbol with simple, explainable rules."""
        if data is None or data.empty or "Close" not in data.columns:
            return Decision(symbol=symbol, action="HOLD", score=0.0, reasons=["missing close prices"])

        close = data["Close"].astype(float)
        price = float(close.iloc[-1])

        # Core indicators
        ma_short = close.rolling(window=self.short_window, min_periods=1).mean()
        ma_long = close.rolling(window=self.long_window, min_periods=1).mean()

        returns = close.pct_change().fillna(0.0)
        momentum_5 = float(returns.tail(5).sum())
        vol_20 = float(returns.tail(20).std()) if len(returns) >= 2 else 0.0

        score = 0.0
        reasons: list[str] = []

        # Trend direction (short MA vs long MA)
        if ma_short.iloc[-1] > ma_long.iloc[-1]:
            score += 2.0
            reasons.append("trend up: short MA above long MA")
            trend = "up"
        elif ma_short.iloc[-1] < ma_long.iloc[-1]:
            score -= 2.0
            reasons.append("trend down: short MA below long MA")
            trend = "down"
        else:
            trend = "flat"
            reasons.append("trend flat: short MA equals long MA")

        # Momentum
        if momentum_5 > 0:
            score += 1.0
            reasons.append(f"positive 5-bar momentum ({momentum_5:.2%})")
        elif momentum_5 < 0:
            score -= 1.0
            reasons.append(f"negative 5-bar momentum ({momentum_5:.2%})")

        # Volatility filter (beginner-friendly: avoid extreme chop)
        if vol_20 > 0.04:
            score -= 0.5
            reasons.append(f"high volatility (20-bar stdev {vol_20:.2%})")
        else:
            score += 0.25
            reasons.append(f"volatility ok (20-bar stdev {vol_20:.2%})")

        # Convert score to action
        if score >= 2.0:
            action = "BUY"
        elif score <= -2.0:
            action = "SELL"
        else:
            action = "HOLD"

        # Simple risk levels (not orders): based on volatility
        stop_loss = price * (1.0 - max(0.02, 2.0 * vol_20))
        take_profit = price * (1.0 + max(0.03, 3.0 * vol_20))

        return Decision(
            symbol=symbol,
            action=action,
            score=float(score),
            reasons=reasons,
            current_price=price,
            stop_loss=float(stop_loss),
            take_profit=float(take_profit),
            trend=trend,
            volatility=float(vol_20),
        )
