import yfinance as yf
import pandas as pd

def check_buy_condition(symbol='AAPL'):
    print(f"🧠 Brain activated. Analyzing {symbol}...")
    
    # 1. Download the last 5 days of stock data quietly
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="5d")
    
    # 2. Get the math
    latest_close = hist['Close'].iloc[-1]
    avg_close = hist['Close'].mean()
    
    print(f"📊 {symbol} Latest Price: ${latest_close:.2f}")
    print(f"📈 {symbol} 5-Day Average: ${avg_close:.2f}")
    
    # 3. The Decision Logic
    if latest_close < avg_close:
        print("💡 SIGNAL: BUY (Price has dipped below the average)")
        return "BUY"
    else:
        print("💡 SIGNAL: HOLD (Price is currently too high)")
        return "HOLD"