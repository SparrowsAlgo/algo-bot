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
- A beginner-friendly market scanner that ranks a watchlist

## Project layout

Core package lives in `src/algo_bot`:

- `runners.py` — orchestration for CLI modes (backtest / paper / status / scan)
- `main.py` — optional entry; same behavior as `paper` mode
- `config/settings.py` — env-based configuration
- `data/` — market data + features
- `strategies/` — strategy interfaces + implementations
- `risk/` — risk checks and position sizing
- `execution/` — broker interface + paper broker
- `portfolio/` — positions and portfolio state
- `persistence/` — JSON state for paper mode
- `scanner/` — scan watchlists and rank opportunities (no trading)
- `reporting/` — format and save scan reports
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
python scripts/run.py scan
python scripts/run.py monitor
```

### What each mode means

| Mode | What it does |
|------|----------------|
| **backtest** | Replays **past** prices: loads settings, downloads history, builds features, runs the backtest engine, prints metrics (return, win rate, etc.). Uses the **same** decision-scoring logic as scan/paper. |
| **paper** | One **live-style** cycle: loads persisted state, scans the watchlist, prints+saves a scan report, chooses the best BUY candidate, runs risk checks, simulates a fill, updates portfolio, saves JSON state + trade log. Does not send real orders. |
| **status** | **Read-only**: loads `paper_state.json` and prints cash, open positions, and trade history (audit trail). |
| **scan** | Scan the watchlist, rank symbols, print a report, and save it under `data/reports/`. Does **not** place trades. |
| **monitor** | Read-only for entries: checks existing open positions against latest prices and closes them if stop-loss or take-profit is hit. |

If you run `python scripts/run.py` with no arguments, or an unknown mode, you get a short usage message.

### Alternative entry (same as `paper`)

If you prefer module style:

```powershell
$env:PYTHONPATH="src"
python -m algo_bot.main
```

Legacy thin wrappers still work: `scripts/run_backtest.py`, `scripts/run_paper.py`.

## How market scanning works

### Watchlist

The **watchlist** is just a list of symbols the bot evaluates every run.

- Set it in `.env` like:
  - `WATCHLIST=AAPL,MSFT,NVDA,SPY,QQQ`
- If you don’t set it, the bot uses a safe default list.

### Scan mode (`python scripts/run.py scan`)

Scan mode is **evaluation only**:

1. **watchlist**: read the watchlist from settings
2. **fetch data**: download recent history per symbol
3. **build features**: compute indicators (moving averages, returns)
4. **score decision**: strategy creates a structured decision with:
   - action (`BUY` / `SELL` / `HOLD`)
   - score
   - reasons (plain-English explanation)
   - stop-loss / take-profit suggestion
5. **rank**: BUY candidates first, then by score
6. **report**: print a clean report and save JSON to `data/reports/`

### Paper mode (`python scripts/run.py paper`)

Paper mode starts with the **same scan** as scan mode, then:

1. **load paper state**: cash + positions + trades from `paper_state.json`
2. **manage exits first**: if you already hold a symbol, check stop-loss / take-profit and exit if hit
3. **pick a candidate**: if flat, choose the best BUY that isn’t already held
4. **plan the trade**: create a TradePlan (entry/stop/target/size) using risk budget + stop distance
5. **risk check**: block unsafe trades (bad signal, missing data, not enough cash, etc.)
6. **execute (paper)**: simulate a fill (no real broker)
7. **persist**: update cash/positions + append trade history + save state

### Scan vs paper (difference)

- **scan**: “What looks good right now?” (no trades)
- **paper**: “Scan + pick + simulate one trade + save everything”

## How Phase 3 trading works

Phase 3 turns scanner output into a **real trade lifecycle** (still paper-only):

1. **scanner** finds candidates across a watchlist and explains *why* each symbol is strong/weak
2. **planner** converts the best BUY candidate into a **TradePlan**:
   - entry price, stop-loss, take-profit
   - quantity sized from risk budget and stop distance
3. **risk** approves or rejects the plan (cash, daily loss limit, etc.)
4. **execution (paper)** opens/closes positions instantly (simulated fills)
5. **portfolio** updates cash/positions, tracks realized PnL, and keeps trade history append-only
6. **position manager** monitors open positions and exits on stop-loss or take-profit
7. **reporting** prints and saves scan reports and trade plan/lifecycle events under `data/reports/`

Key idea: **scan is evaluation**, **paper is evaluation + one lifecycle action (exit or entry)**, and **monitor is exit-only**.

## Notes

- This project does not place real live orders.
- API keys are read from environment variables and are optional in paper mode.
- Paper portfolio state defaults to `data/state/paper_state.json` (cash, positions, `trades` log).
