from __future__ import annotations

def compute_performance(trades: list[dict]) -> dict:
    closed = [t for t in trades if t.get("status") == "closed" and t.get("pnl") is not None]

    if not closed:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "total_pnl": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "max_win": 0.0,
            "max_loss": 0.0,
            "avg_holding_time": 0.0,
            "win_count": 0,
            "loss_count": 0,
        }

    pnls = [float(t["pnl"]) for t in closed]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    holding_times = [t.get("holding_seconds", 0) or 0 for t in closed]

    total_trades = len(closed)
    win_count = len(wins)
    loss_count = len(losses)
    total_pnl = sum(pnls)

    return {
        "total_trades": total_trades,
        "win_rate": win_count / total_trades if total_trades else 0.0,
        "total_pnl": total_pnl,
        "avg_win": sum(wins) / len(wins) if wins else 0.0,
        "avg_loss": sum(losses) / len(losses) if losses else 0.0,
        "max_win": max(wins) if wins else 0.0,
        "max_loss": min(losses) if losses else 0.0,
        "avg_holding_time": sum(holding_times) / len(holding_times) if holding_times else 0.0,
        "win_count": win_count,
        "loss_count": loss_count,
    }