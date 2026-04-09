"""CLI-oriented orchestration for backtest, paper trading, scanning, and status."""

from __future__ import annotations

import json
import os
from typing import Any

from algo_bot.backtest.engine import BacktestEngine
from algo_bot.config.settings import SETTINGS
from algo_bot.execution.paper_broker import PaperBroker
from algo_bot.monitoring.logger import get_logger
from algo_bot.persistence.json_state_store import JsonStateStore
from algo_bot.portfolio.portfolio_manager import PortfolioManager
from algo_bot.reporting.scan_report import format_scan_report, save_scan_report
from algo_bot.reporting.trade_plan_report import format_trade_plan, save_trade_event
from algo_bot.risk.checks import can_trade
from algo_bot.risk.position_sizing import fixed_position_size
from algo_bot.scanner.ranking import rank_scan_results, top_candidates
from algo_bot.scanner.scanner import scan_watchlist
from algo_bot.trading.planner import build_trade_plan
from algo_bot.trading.position_manager import should_exit_long
from algo_bot.utils.trade_record import trade_record_from_broker_order


def run_backtest_mode() -> None:
    """Load data, run backtest engine, print metrics."""
    print("[backtest] Loading settings...")
    settings = SETTINGS

    print("[backtest] Fetching historical data...")
    results = scan_watchlist([settings.symbol], settings.lookback_period, settings.interval)
    features_symbol = results[0].symbol  # for clarity: same symbol

    print("[backtest] Running backtest...")
    engine = BacktestEngine()
    # Re-fetch features via scanner pipeline to keep paper/backtest aligned
    # (BacktestEngine still needs a DataFrame, so we fetch it directly again.)
    from algo_bot.data.market_data import MarketDataClient
    from algo_bot.data.features import add_basic_features
    from algo_bot.strategies.simple_ma import SimpleMAStrategy

    data_client = MarketDataClient()
    raw_data = data_client.get_history(features_symbol, settings.lookback_period, settings.interval)
    features = add_basic_features(raw_data)
    strategy = SimpleMAStrategy()
    metrics = engine.run(
        symbol=features_symbol,
        data=features,
        strategy=strategy,
        quantity=fixed_position_size(settings.trade_size),
        starting_cash=settings.starting_cash,
        max_daily_loss=settings.max_daily_loss,
    )

    print("[backtest] Metrics:")
    print(json.dumps(metrics, indent=2))

def run_scan_mode() -> None:
    """Scan watchlist, rank symbols, print and save a report (no trading)."""
    print("[scan] Loading settings...")
    settings = SETTINGS

    print(f"[scan] Watchlist: {', '.join(settings.watchlist)}")
    print("[scan] Scanning symbols...")
    results = scan_watchlist(settings.watchlist, settings.lookback_period, settings.interval)
    ranked = rank_scan_results(results)

    report = format_scan_report(ranked)
    print(report)

    path = save_scan_report(ranked)
    print(f"\n[scan] Saved report: {path.as_posix()}")


def run_paper_mode() -> None:
    """One paper cycle: manage exits → scan → plan → risk → open → persist."""
    logger = get_logger()
    print("[paper] Loading settings...")
    settings = SETTINGS

    if not settings.paper_mode:
        logger.error("Only paper mode is supported in this starter framework.")
        return

    print("[paper] Loading persisted state...")
    state_path = os.getenv("PAPER_STATE_PATH", "data/state/paper_state.json")
    print(f"[paper] State file: {state_path}")
    state_store = JsonStateStore(path=state_path)
    initial_state = state_store.load(default_cash=settings.starting_cash)
    portfolio = PortfolioManager.from_state(initial_state, starting_cash=settings.starting_cash)

    # 1) Manage open positions first (stop/target exits)
    if portfolio.positions:
        print("[paper] Managing open positions...")
        from algo_bot.data.market_data import MarketDataClient

        data_client = MarketDataClient()
        broker = PaperBroker()

        for symbol, pos in list(portfolio.positions.items()):
            raw = data_client.get_history(symbol, period="5d", interval=settings.interval)
            if raw is None or raw.empty or "Close" not in raw.columns:
                print(f"[paper] {symbol}: no fresh data, skipping exit check.")
                continue

            current_price = float(raw["Close"].iloc[-1])
            exit_decision = should_exit_long(current_price, pos.stop_loss, pos.take_profit)
            if not exit_decision.should_exit:
                print(f"[paper] {symbol}: holding (price={current_price:.2f})")
                continue

            print(f"[paper] {symbol}: exiting due to {exit_decision.reason} at {current_price:.2f}")
            fill = broker.close_trade(symbol, pos.quantity, current_price, exit_decision.reason)
            realized = portfolio.close_position(symbol, fill, exit_decision.reason)
            portfolio.append_trade(trade_record_from_broker_order(fill))
            state_store.save(portfolio.to_state())
            logger.info("Closed %s (%s) realized_pnl=%.2f", symbol, exit_decision.reason, realized)

        # After managing, stop here to keep the loop beginner-simple (one action per run).
        print("[paper] Exit management complete. Run again to look for new entries.")
        return

    print("[paper] Scanning watchlist (no trades yet)...")
    results = scan_watchlist(settings.watchlist, settings.lookback_period, settings.interval)
    ranked = rank_scan_results(results)

    print("[paper] Market scan report:")
    print(format_scan_report(ranked))
    report_path = save_scan_report(ranked)
    print(f"[paper] Saved scan report: {report_path.as_posix()}")

    print("[paper] Choosing best candidate...")
    candidates = top_candidates(ranked, limit=3)
    candidates = [c for c in candidates if not portfolio.has_position(c.symbol)]
    if not candidates:
        print("[paper] No BUY candidates right now. No trade.")
        return

    pick = candidates[0]
    print(f"[paper] Selected candidate: {pick.symbol} (score {pick.score:.2f})")

    # 2) Build trade plan (entry/stop/target/size)
    plan = build_trade_plan(
        decision={
            "symbol": pick.symbol,
            "action": pick.action,
            "score": pick.score,
            "reasons": pick.reasons,
            "current_price": pick.current_price,
            "stop_loss": pick.stop_loss,
            "take_profit": pick.take_profit,
            "volatility": pick.volatility,
        },
        cash_available=portfolio.cash,
        risk_per_trade_pct=settings.risk_per_trade_pct,
        risk_reward=settings.risk_reward,
    )
    if plan is None:
        print("[paper] No valid trade plan could be built (likely size/risk too small).")
        return

    print(format_trade_plan(plan))
    save_trade_event(plan, event="planned")

    symbol = plan.symbol
    side = plan.action
    quantity = plan.quantity
    last_price = float(plan.entry_price)
    estimated_cost = last_price * quantity

    print("[paper] Risk check...")
    allowed, reason = can_trade(
        signal=side,
        has_data=(last_price > 0),
        quantity=quantity,
        estimated_cost=estimated_cost,
        cash_available=portfolio.cash,
        daily_pnl=portfolio.daily_pnl,
        max_daily_loss=settings.max_daily_loss,
    )

    if not allowed:
        print(f"[paper] No execution: {reason}")
        logger.info("Trade blocked: %s", reason)
        return

    print("[paper] Opening paper position...")
    broker = PaperBroker()
    order = broker.open_trade(plan)

    if order["status"] == "filled":
        print("[paper] Updating portfolio and saving state...")
        portfolio.open_from_plan(plan, order)
        portfolio.append_trade(trade_record_from_broker_order(order))
        state_store.save(portfolio.to_state())
        save_trade_event(plan, event="opened", extra={"fill": order})
        logger.info("Order filled: %s", order)
        logger.info("Cash remaining: %.2f", portfolio.cash)
        print("[paper] Done.")
    else:
        logger.warning("Order not filled: %s", order)
        print("[paper] Order not filled (see log).")


def run_status_mode() -> None:
    """Print cash, positions, and trade history from disk."""
    print("[status] Loading settings...")
    settings = SETTINGS

    state_path = os.getenv("PAPER_STATE_PATH", "data/state/paper_state.json")
    print(f"[status] Reading state: {state_path}")

    state_store = JsonStateStore(path=state_path)
    state: dict[str, Any] = state_store.load(default_cash=settings.starting_cash)
    portfolio = PortfolioManager.from_state(state, starting_cash=settings.starting_cash)

    print("\n--- Cash ---")
    print(f"{portfolio.cash:.2f}")

    print("\n--- Realized PnL ---")
    print(f"{portfolio.realized_pnl:.2f}")

    print("\n--- Last action ---")
    print(portfolio.last_action)

    print("\n--- Positions ---")
    if not portfolio.positions:
        print("(none)")
    else:
        for symbol, pos in portfolio.positions.items():
            sl = f"{pos.stop_loss:.2f}" if pos.stop_loss is not None else "n/a"
            tp = f"{pos.take_profit:.2f}" if pos.take_profit is not None else "n/a"
            print(
                f"- {symbol}: qty={pos.quantity} avg={pos.avg_price:.2f} "
                f"stop={sl} target={tp} opened_at={pos.opened_at or 'n/a'}"
            )

    print("\n--- Trade history ---")
    if not portfolio.trades:
        print("(no trades recorded yet)")
    else:
        print(f"total trades: {len(portfolio.trades)}")
        for t in portfolio.trades[-10:]:
            print(
                f"- {t.get('filled_at') or t.get('submitted_at')} "
                f"{t.get('symbol')} {t.get('side')} qty={t.get('quantity')} price={t.get('price')} status={t.get('status')}"
            )

    print(f"\n--- Last trade time ---\n{state.get('last_trade_time')}")
    print(f"\n--- File last updated ---\n{state.get('last_updated')}")


def run_monitor_mode() -> None:
    """Monitor only: manage open positions (stop/target) and exit if needed."""
    logger = get_logger()
    print("[monitor] Loading settings...")
    settings = SETTINGS

    print("[monitor] Loading persisted state...")
    state_path = os.getenv("PAPER_STATE_PATH", "data/state/paper_state.json")
    print(f"[monitor] State file: {state_path}")
    state_store = JsonStateStore(path=state_path)
    initial_state = state_store.load(default_cash=settings.starting_cash)
    portfolio = PortfolioManager.from_state(initial_state, starting_cash=settings.starting_cash)

    if not portfolio.positions:
        print("[monitor] No open positions.")
        return

    from algo_bot.data.market_data import MarketDataClient

    data_client = MarketDataClient()
    broker = PaperBroker()

    print("[monitor] Checking exits...")
    for symbol, pos in list(portfolio.positions.items()):
        raw = data_client.get_history(symbol, period="5d", interval=settings.interval)
        if raw is None or raw.empty or "Close" not in raw.columns:
            print(f"[monitor] {symbol}: no fresh data, skipping.")
            continue

        current_price = float(raw["Close"].iloc[-1])
        exit_decision = should_exit_long(current_price, pos.stop_loss, pos.take_profit)
        if not exit_decision.should_exit:
            print(f"[monitor] {symbol}: holding (price={current_price:.2f})")
            continue

        print(f"[monitor] {symbol}: exiting due to {exit_decision.reason} at {current_price:.2f}")
        fill = broker.close_trade(symbol, pos.quantity, current_price, exit_decision.reason)
        realized = portfolio.close_position(symbol, fill, exit_decision.reason)
        portfolio.append_trade(trade_record_from_broker_order(fill))
        state_store.save(portfolio.to_state())
        logger.info("Closed %s (%s) realized_pnl=%.2f", symbol, exit_decision.reason, realized)
