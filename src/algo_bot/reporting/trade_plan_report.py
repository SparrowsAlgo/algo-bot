"""Reporting layer: format and save trade plans and lifecycle events."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from algo_bot.trading.trade_plan import TradePlan


def format_trade_plan(plan: TradePlan) -> str:
    """Human-readable trade plan output."""
    lines: list[str] = []
    lines.append("=== Trade Plan ===")
    lines.append(f"symbol: {plan.symbol}")
    lines.append(f"action: {plan.action}")
    lines.append(f"entry:  {plan.entry_price:.2f}")
    lines.append(f"stop:   {plan.stop_loss:.2f}")
    lines.append(f"target: {plan.take_profit:.2f}")
    lines.append(f"qty:    {plan.quantity}")
    lines.append("")
    lines.append(f"risk/share: {plan.risk_per_share:.2f}")
    lines.append(f"total risk: {plan.total_risk:.2f}")
    lines.append(f"exp reward: {plan.expected_reward:.2f}")
    lines.append(f"R:R ratio:  {plan.risk_reward_ratio:.2f}")
    lines.append("")
    lines.append(f"score: {plan.score:.2f}")
    if plan.reasons:
        lines.append("reasons:")
        for r in plan.reasons[:8]:
            lines.append(f"  - {r}")
    return "\n".join(lines)


def save_trade_event(
    plan: TradePlan,
    event: str,
    extra: dict[str, Any] | None = None,
    directory: str = "data/reports",
) -> Path:
    """Save a timestamped JSON record for this trade plan event."""
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y%m%dT%H%M%SZ")
    path = output_dir / f"trade_{plan.symbol}_{event}_{ts}.json"
    payload: dict[str, Any] = {"event": event, "plan": asdict(plan), "timestamp": ts}
    if extra:
        payload["extra"] = extra
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path

