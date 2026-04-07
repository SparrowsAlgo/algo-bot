"""Shared trade record shape for paper logs and (later) backtest logs."""

from __future__ import annotations

from typing import Any


def _as_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            return 0
    return 0


def _as_float(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def trade_record_from_broker_order(order: dict[str, Any]) -> dict[str, Any]:
    """Map a broker execution summary to the persisted trade log format."""
    side_raw = str(order.get("side", "")).upper()
    side_lower = {"BUY": "buy", "SELL": "sell", "HOLD": "hold"}.get(side_raw, side_raw.lower())

    quantity = _as_int(order.get("quantity", 0))
    price = _as_float(order.get("price", 0.0))

    submitted = order.get("submitted_at", "")
    filled = order.get("filled_at", submitted)

    return {
        "symbol": str(order.get("symbol", "")),
        "side": side_lower,
        "quantity": quantity,
        "price": price,
        "submitted_at": submitted,
        "filled_at": filled,
        "status": str(order.get("status", "unknown")),
    }
