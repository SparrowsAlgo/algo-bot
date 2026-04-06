from strategies.simple_strategy import check_buy_condition
from execution.paper_trader import execute_test_trade

if __name__ == "__main__":
    print("🤖 Backstage engine initialized.")
    print("-" * 40)
    
    # 1. Ask the Brain what to do
    signal = check_buy_condition('AAPL')
    print("-" * 40)
    
    # 2. Tell the Muscle to act based on the signal
    if signal == "BUY":
        print("💪 Triggering the execution muscle...")
        execute_test_trade()
    else:
        print("💤 Brain says HOLD. No trades executed. Going back to sleep.")