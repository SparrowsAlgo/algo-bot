import os
from dotenv import load_dotenv
from alpaca_trade_api.rest import REST

def execute_test_trade():
    # 1. Load the secret keys
    load_dotenv()
    
    API_KEY = os.getenv('ALPACA_API_KEY')
    SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
    BASE_URL = 'https://paper-api.alpaca.markets' # This is your paper endpoint

    # Safety Check
    if not API_KEY or not SECRET_KEY:
        print("🛑 STOP: Python cannot find your API keys in the .env file!")
        return 

    # 2. Connect to the Broker
    print("Keys loaded! Connecting to Alpaca Paper Market...")
    api = REST(key_id=API_KEY, secret_key=SECRET_KEY, base_url=BASE_URL)

    # 3. Execute the Trade
    try:
        order = api.submit_order(
            symbol='AAPL',
            qty=1,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        print(f"✅ SUCCESS! Live paper order submitted: Bought 1 share of {order.symbol}.")
        
    except Exception as e:
        print(f"❌ ERROR: Trade failed. Details: {e}")