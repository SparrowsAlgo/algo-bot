import yfinance as yf
import pandas as pd
import warnings
warnings.filterwarnings('ignore') # Hides annoying pandas math warnings

def run_backtest(symbol='AAPL'):
    print(f"⏳ Booting up the Time Machine for {symbol}...\n")

    # 1. Download 2 years of historical data
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="2y") 
    
    # 2. THE NEW MATH (Trend Following / Momentum)
    df['10_Day_Avg'] = df['Close'].rolling(window=10).mean()
    df['50_Day_Avg'] = df['Close'].rolling(window=50).mean()
    
    # 3. THE NEW LOGIC
    # If the fast average is higher than the slow average, momentum is UP. Buy/Hold.
    # We use .fillna(0) to handle the first 50 days where there isn't enough data yet.
    df['Signal'] = (df['10_Day_Avg'] > df['50_Day_Avg']).astype(int)
    
    # Shift the signal by 1 day! (Trade tomorrow based on today's signal)
    df['Position'] = df['Signal'].shift(1).fillna(0)
    
    # 4. CALCULATE PROFITS
    df['Market_Return'] = df['Close'].pct_change()
    df['Strategy_Return'] = df['Market_Return'] * df['Position']
    
    # 5. THE FINAL SCORE
    total_market_return = (1 + df['Market_Return']).prod() - 1
    total_strategy_return = (1 + df['Strategy_Return']).prod() - 1

    # --- PRINT THE REPORT ---
    print("📊 --- BACKTEST RESULTS (Last 2 Years) ---")
    print(f"Strategy: Trend Following (10 SMA vs 50 SMA)")
    print(f"If a human just bought and held {symbol}:  {total_market_return * 100:.2f}% profit")
    print(f"If you used our 'Momentum' Bot: {total_strategy_return * 100:.2f}% profit")
    
    if total_strategy_return > total_market_return:
        print("\n🏆 CONCLUSION: The bot beat the market! The math works.")
    else:
        print("\n💀 CONCLUSION: The bot lost to the market. Back to the drawing board.")

if __name__ == "__main__":
    run_backtest()