import yfinance as yf
import pandas as pd
import warnings

# This hides the messy pandas math warnings from your terminal
warnings.filterwarnings('ignore')

def optimize_sma(symbol='AAPL'):
    print(f"🔍 Booting up The Grid Search Optimizer for {symbol}...\n")
    
    # 1. Download Data once to save time
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="2y")
    
    best_fast = 0
    best_slow = 0
    best_return = -999 # Start with a terrible number so anything beats it
    
    print("Testing hundreds of moving average combinations. Please wait...")
    
    # 2. THE LOOP (Test Fast SMAs from 5 to 20, and Slow SMAs from 20 to 60)
    for fast in range(5, 21):
        for slow in range(20, 61):
            if fast >= slow: 
                continue # The fast line must always be faster than the slow line
                
            # Create a temporary dataframe for this specific test
            temp_df = df.copy()
            temp_df['Fast_SMA'] = temp_df['Close'].rolling(window=fast).mean()
            temp_df['Slow_SMA'] = temp_df['Close'].rolling(window=slow).mean()
            
            # The Logic
            temp_df['Signal'] = (temp_df['Fast_SMA'] > temp_df['Slow_SMA']).astype(int)
            temp_df['Position'] = temp_df['Signal'].shift(1).fillna(0)
            
            # Calculate Profit
            temp_df['Market_Return'] = temp_df['Close'].pct_change()
            temp_df['Strategy_Return'] = temp_df['Market_Return'] * temp_df['Position']
            
            strategy_return = (1 + temp_df['Strategy_Return']).prod() - 1
            
            # If this combination is the best one so far, save it!
            if strategy_return > best_return:
                best_return = strategy_return
                best_fast = fast
                best_slow = slow

    # 3. Calculate what the human made just holding the stock
    market_return = (1 + df['Close'].pct_change()).prod() - 1

    # --- PRINT THE REPORT ---
    print("\n🏆 --- OPTIMIZATION COMPLETE ---")
    print(f"Human Buy & Hold Profit: {market_return * 100:.2f}%")
    print(f"Best Bot Profit:         {best_return * 100:.2f}%")
    print("-" * 30)
    print(f"🔥 The Magic Numbers for {symbol}:")
    print(f"Fast SMA: {best_fast} Days")
    print(f"Slow SMA: {best_slow} Days")

    if best_return > market_return:
        print("\n✅ The Optimizer beat the market! Go update your backtester with these numbers.")
    else:
        print("\n💀 Even the absolute best setup couldn't beat the market. AAPL trend is too strong.")

if __name__ == "__main__":
    optimize_sma()