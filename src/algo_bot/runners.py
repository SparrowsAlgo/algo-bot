"""CLI-oriented orchestration for backtest, paper trading, and status (no strategy/risk rules here)."""

from __future__ import annotations

import json
import os
from typing import Any

from algo_bot.backtest.engine import BacktestEngine
from algo_bot.config.settings import SETTINGS
from algo_bot.data.features import add_basic_features
from algo_bot.data.market_data import MarketDataClient
from algo_bot.execution.paper_broker import PaperBroker
from algo_bot.monitoring.logger import get_logger
from algo_bot.persistence.json_state_store import JsonStateStore
from algo_bot.portfolio.portfolio_manager import PortfolioManager
from algo_bot.risk.checks import can_trade
from algo_bot.risk.position_sizing import fixed_position_size
from algo_bot.strategies.simple_ma import SimpleMAStrategy
from algo_bot.utils.trade_record import trade_record_from_broker_order


def run_backtest_mode() -> None:
    """Load data, run backtest engine, print metrics."""
    print("[backtest] Loading settings...")
    settings = SETTINGS

    print("[backtest] Fetching historical data...")
    data_client = MarketDataClient()
    raw_data = data_client.get_history(settings.symbol, settings.lookback_period, settings.interval)

    print("[backtest] Building features...")
    features = add_basic_features(raw_data)

    print("[backtest] Running backtest...")
    strategy = SimpleMAStrategy()
    engine = BacktestEngine()
    metrics = engine.run(
        data=features,
        strategy=strategy,
        quantity=fixed_position_size(settings.trade_size),
        starting_cash=settings.starting_cash,
        max_daily_loss=settings.max_daily_loss,
    )

    print("[backtest] Metrics:")
    print(json.dumps(metrics, indent=2))


def run_paper_mode() -> None:
    """One paper cycle: data → signal → risk → execution → persist → log."""
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

    print("[paper] Fetching market data...")
    data_client = MarketDataClient()
    raw_data = data_client.get_history(settings.symbol, settings.lookback_period, settings.interval)

    print("[paper] Building features...")
    features = add_basic_features(raw_data)

    if features.empty:
        logger.warning("No market data for %s. Stopping.", settings.symbol)
        return

    print("[paper] Generating signal (strategy)...")
    strategy = SimpleMAStrategy()
    signal = strategy.generate_signal(features)

    print("[paper] Sizing position...")
    quantity = fixed_position_size(settings.trade_size)

    print("[paper] Applying position guard (avoid duplicate buy / sell flat)...")
    has_open_position = portfolio.has_position(settings.symbol)
    side = signal
    if signal == "BUY" and has_open_position:
        side = "HOLD"
    elif signal == "SELL" and not has_open_position:
        side = "HOLD"

    last_price = float(features["Close"].iloc[-1])
    estimated_cost = last_price * quantity

    print("[paper] Risk check...")
    allowed, reason = can_trade(
        signal=side,
        has_data=not features.empty,
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

    print("[paper] Simulating paper execution...")
    broker = PaperBroker()
    order = broker.submit_order(settings.symbol, side, quantity, last_price)

    if order["status"] == "filled":
        print("[paper] Updating portfolio and saving state...")
        portfolio.apply_fill(settings.symbol, side, quantity, last_price)
        portfolio.append_trade(trade_record_from_broker_order(order))
        state_store.save(portfolio.to_state())
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

    print("\n--- Cash ---")
    print(state.get("cash"))

    print("\n--- Positions ---")
    positions = state.get("positions") or {}
    if not positions:
        print("(none)")
    else:
        print(json.dumps(positions, indent=2))

    print("\n--- Trade history ---")
    trades = state.get("trades") or []
    if not trades:
        print("(no trades recorded yet)")
    else:
        print(json.dumps(trades, indent=2))

    print(f"\n--- Last trade time ---\n{state.get('last_trade_time')}")
    print(f"\n--- File last updated ---\n{state.get('last_updated')}")
