from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

def format_performance_report(metrics: dict) -> str:
    return f"""
===== PERFORMANCE REPORT =====

Total Trades: {metrics['total_trades']}
Win Rate: {metrics['win_rate'] * 100:.1f}%
Total PnL: {metrics['total_pnl']:+.2f}

Avg Win: {metrics['avg_win']:+.2f}
Avg Loss: {metrics['avg_loss']:+.2f}

Best Trade: {metrics['max_win']:+.2f}
Worst Trade: {metrics['max_loss']:+.2f}

Avg Holding Time: {metrics['avg_holding_time']:.0f} seconds
Win Count: {metrics['win_count']}
Loss Count: {metrics['loss_count']}
""".strip()

def save_performance_report(metrics: dict, report_dir: str = "data/reports") -> Path:
    path = Path(report_dir)
    path.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    file_path = path / f"performance_{stamp}.json"

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return file_path