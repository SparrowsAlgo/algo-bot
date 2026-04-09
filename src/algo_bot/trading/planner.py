"""Trading layer: create a TradePlan from a scan decision (rule-based, beginner-friendly)."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from algo_bot.trading.trade_plan import TradePlan


def build_trade_plan(
    decision: dict[str, Any],
    cash_available: float,
    risk_per_trade_pct: float = 0.01,
    risk_reward: float = 2.0,
) -> TradePlan | None:
    """Build a TradePlan from a decision-like dict.

    Expected keys: symbol, action, score, reasons, current_price, stop_loss, take_profit, volatility.
    Returns None for non-BUY actions or if required fields are missing.
    """
    action = str(decision.get("action", "HOLD")).upper()
    if action != "BUY":
        return None

    symbol = str(decision.get("symbol", "")).upper()
    price = decision.get("current_price")
    if price is None:
        return None
    entry_price = float(price)
    if entry_price <= 0:
        return None

    # Stop loss: prefer strategy-provided stop; otherwise use a simple fallback.
    stop = decision.get("stop_loss")
    vol = float(decision.get("volatility") or 0.0)
    if stop is None:
        stop_loss = entry_price * (1.0 - max(0.02, 2.0 * vol))
    else:
        stop_loss = float(stop)

    risk_per_share = max(0.0, entry_price - stop_loss)
    if risk_per_share <= 0:
        return None

    # Take profit: prefer strategy-provided target; otherwise set by risk-reward.
    tp = decision.get("take_profit")
    if tp is None:
        take_profit = entry_price + (risk_reward * risk_per_share)
    else:
        take_profit = float(tp)

    # Quantity: risk budget / stop distance, also limited by cash.
    risk_budget = max(0.0, float(cash_available) * float(risk_per_trade_pct))
    qty_by_risk = int(risk_budget // risk_per_share) if risk_per_share > 0 else 0
    qty_by_cash = int(float(cash_available) // entry_price) if entry_price > 0 else 0
    quantity = max(0, min(qty_by_risk, qty_by_cash))
    if quantity <= 0:
        return None

    total_risk = risk_per_share * quantity
    expected_reward = max(0.0, (take_profit - entry_price) * quantity)
    rr = (expected_reward / total_risk) if total_risk > 0 else 0.0

    reasons = decision.get("reasons") or []
    if not isinstance(reasons, list):
        reasons = [str(reasons)]

    return TradePlan(
        symbol=symbol,
        action="BUY",
        entry_price=entry_price,
        stop_loss=float(stop_loss),
        take_profit=float(take_profit),
        quantity=int(quantity),
        risk_per_share=float(risk_per_share),
        total_risk=float(total_risk),
        expected_reward=float(expected_reward),
        risk_reward_ratio=float(rr),
        score=float(decision.get("score") or 0.0),
        reasons=[str(r) for r in reasons],
        timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    )

