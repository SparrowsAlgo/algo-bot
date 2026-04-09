"""Reporting layer: format and save market scan results."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from algo_bot.scanner.scanner import ScanResult


def format_scan_report(results: list[ScanResult], ranked: bool = True) -> str:
    """Create a beginner-friendly report string for console output."""
    if not results:
        return "No scan results."

    lines: list[str] = []
    lines.append("=== Market Scan Report ===")
    lines.append(f"Symbols scanned: {len(results)}")
    lines.append("")

    for idx, r in enumerate(results, start=1):
        price = f"{r.current_price:.2f}" if isinstance(r.current_price, (int, float)) else "n/a"
        sl = f"{r.stop_loss:.2f}" if isinstance(r.stop_loss, (int, float)) else "n/a"
        tp = f"{r.take_profit:.2f}" if isinstance(r.take_profit, (int, float)) else "n/a"
        vol = f"{r.volatility:.2%}" if isinstance(r.volatility, (int, float)) else "n/a"
        trend = r.trend or "n/a"

        lines.append(f"{idx:>2}. {r.symbol:>5} | action={r.action:<4} | score={r.score:>5.2f} | price={price}")
        lines.append(f"    trend={trend} | vol={vol} | stop={sl} | take={tp}")
        if r.reasons:
            lines.append("    reasons:")
            for reason in r.reasons[:6]:
                lines.append(f"      - {reason}")
        lines.append("")

    return "\n".join(lines).rstrip()


def save_scan_report(results: list[ScanResult], directory: str = "data/reports") -> Path:
    """Save scan results to a timestamped JSON file and return its path."""
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y%m%dT%H%M%SZ")
    path = output_dir / f"scan_{timestamp}.json"
    payload = [asdict(r) for r in results]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path

