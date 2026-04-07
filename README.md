# Algo Bot (Beginner Framework)

A clean, beginner-friendly algorithmic trading framework built around one shared flow:

`data -> strategy -> risk -> execution -> logging`

This version is intentionally simple and runs in **paper mode** only (no live orders).

## What it includes

- Historical data download with `yfinance`
- A simple moving-average strategy that returns `BUY`, `SELL`, or `HOLD`
- Basic risk checks (`can_trade`)
- Fixed position sizing
- Simulated paper broker execution
- Portfolio state and an append-only trade log on disk

## Project layout

Core package lives in `src/algo_bot`:

- `runners.py` — orchestration for CLI modes (backtest / paper / status)
- `main.py` — optional entry; same behavior as `paper` mode
- `config/settings.py` — env-based configuration
- `data/` — market data + features
- `strategies/` — strategy interfaces + implementations
- `risk/` — risk checks and position sizing
- `execution/` — broker interface + paper broker
- `portfolio/` — positions and portfolio state
- `persistence/` — JSON state for paper mode
- `backtest/` — backtest loop and metrics
- `monitoring/` — logger setup

## Setup

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Create your environment file from the example:

```bash
copy .env.example .env
```

3. Optional: edit `.env` (symbol, trade size, cash, state file path, etc.).

## Main commands (recommended)

From the repo root, **no `PYTHONPATH` needed** — `scripts/run.py` adds `src/` for you:

```bash
python scripts/run.py backtest
python scripts/run.py paper
python scripts/run.py status
```

### What each mode means

| Mode | What it does |
|------|----------------|
| **backtest** | Replays **past** prices: loads settings, downloads history, builds features, runs the backtest engine, prints metrics (return, win rate, etc.). Uses the **same** strategy + feature pipeline as paper mode. |
| **paper** | One **live-style** cycle on **current** data: loads persisted state, fetches recent prices, builds features, gets a signal, runs risk checks, simulates a fill, updates portfolio, saves JSON state, logs the result. Does not send real orders. |
| **status** | **Read-only**: loads `paper_state.json` and prints cash, open positions, and trade history (audit trail). |

If you run `python scripts/run.py` with no arguments, or an unknown mode, you get a short usage message.

### Alternative entry (same as `paper`)

If you prefer module style:

```powershell
$env:PYTHONPATH="src"
python -m algo_bot.main
```

Legacy thin wrappers still work: `scripts/run_backtest.py`, `scripts/run_paper.py`.

## Notes

- This project does not place real live orders.
- API keys are read from environment variables and are optional in paper mode.
- Paper portfolio state defaults to `data/state/paper_state.json` (cash, positions, `trades` log).
