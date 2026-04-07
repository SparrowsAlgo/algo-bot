"""Persistence layer: load/save paper portfolio and trade history as JSON."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class JsonStateStore:
    """Read/write paper trading state on disk."""

    def __init__(self, path: str = "data/state/paper_state.json") -> None:
        self.path = Path(path)

    def load(self, default_cash: float) -> dict[str, Any]:
        """Load persisted state or return a safe default."""
        default_state = {
            "cash": float(default_cash),
            "positions": {},
            "last_trade_time": None,
            "trades": [],
            "last_updated": self._now_iso(),
        }
        if not self.path.exists():
            return default_state

        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return default_state

        if not isinstance(payload, dict):
            return default_state

        raw_trades = payload.get("trades", [])
        trades = raw_trades if isinstance(raw_trades, list) else []

        return {
            "cash": float(payload.get("cash", default_cash)),
            "positions": payload.get("positions", {}),
            "last_trade_time": payload.get("last_trade_time"),
            "trades": trades,
            "last_updated": payload.get("last_updated", self._now_iso()),
        }

    def save(self, state: dict[str, Any]) -> None:
        """Persist state to disk, creating parent folders when needed."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        raw_trades = state.get("trades", [])
        trades = raw_trades if isinstance(raw_trades, list) else []

        payload = {
            "cash": float(state.get("cash", 0.0)),
            "positions": state.get("positions", {}),
            "last_trade_time": state.get("last_trade_time"),
            "trades": trades,
            "last_updated": self._now_iso(),
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
