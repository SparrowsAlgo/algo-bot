# 📈 Algo-Bot: Automated Quantitative Trading Engine

A modular, Python-based algorithmic trading system. This project includes live paper-trading execution, historical backtesting, and a strategy optimizer.

## 📂 Project Structure
* `main.py` - The central orchestrator that runs the bot.
* `backtester.py` - The "Time Machine" to test strategies against historical data.
* `optimizer.py` - A grid-search tool to find the most profitable moving average parameters.
* `strategies/` - Folder containing the mathematical decision-making logic.
* `execution/` - Folder containing the API connection to the broker.

## ⚙️ Setup Instructions for New Machines

**1. Install Python Dependencies**
Open your terminal and run:
```bash
python -m pip install -r requirements.txt
python -m pip install yfinance python-dotenv

2. Configure the API Keys (CRITICAL)
Do NOT upload your keys to GitHub.

Create a new file in the main folder and name it exactly .env

Add your Alpaca Paper Trading keys to the file like this:

Plaintext
ALPACA_API_KEY=YourKeyHere
ALPACA_SECRET_KEY=YourSecretHere
(Note: Ensure .env is listed inside your .gitignore file so it remains untracked).

🚀 How to Run the Tools
Run the Live Paper Trader: python main.py

Test the Strategy Historically: python backtester.py

Find the Best Strategy Parameters: python optimizer.py


### Step 3: Save to the Vault
Once you have run the optimizer and saved both files, it is time to push this massive upgrade to GitHub so your partner can see it.

Run these three commands in your terminal:
```bash
git add .
git commit -m "Added SMA Grid Search Optimizer and Project README"
git push