"""
Debug script for option trades
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
print(f"API Key: {POLYGON_API_KEY}")

# Test with AAPL option
# Try different combinations of popular stocks and strike prices
test_options = [
    {"ticker": "AAPL", "strike": 100, "expiry": "2025-04-17"},
    {"ticker": "AAPL", "strike": 150, "expiry": "2025-04-17"},
    {"ticker": "AAPL", "strike": 180, "expiry": "2025-04-17"},
    {"ticker": "AAPL", "strike": 200, "expiry": "2025-04-17"},
    {"ticker": "TSLA", "strike": 150, "expiry": "2025-04-17"},
    {"ticker": "MSFT", "strike": 400, "expiry": "2025-04-17"},
    {"ticker": "SPY", "strike": 500, "expiry": "2025-04-17"},
]

# Start with first option
ticker = test_options[0]["ticker"]
strike = test_options[0]["strike"]
expiry = test_options[0]["expiry"]

# Format option symbol
strike_price_padded = f"{strike:08.0f}"
option_date = datetime.strptime(expiry, '%Y-%m-%d')
option_date_str = option_date.strftime('%y%m%d')
option_symbol = f"O:{ticker}{option_date_str}C{strike_price_padded}"

print(f"Testing option symbol: {option_symbol}")

# Direct API call
BASE_URL = "https://api.polygon.io"
endpoint = f'{BASE_URL}/v3/trades/{option_symbol}?limit=10&apiKey={POLYGON_API_KEY}'
print(f"Calling API: {endpoint}")

try:
    response = requests.get(endpoint, timeout=10)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        trades = data.get('results', [])
        print(f"Found {len(trades)} trades")
        
        if trades:
            for i, trade in enumerate(trades[:3]):
                print(f"Trade {i+1}: Price=${trade.get('price')}, Size={trade.get('size')}")
                # Get timestamp
                timestamp = trade.get('participant_timestamp') or trade.get('sip_timestamp')
                if timestamp:
                    # Convert nanoseconds to seconds and then to datetime
                    trade_date = datetime.fromtimestamp(timestamp / 1e9)
                    date_str = trade_date.strftime("%m/%d/%y")
                    print(f"  Date: {date_str}")
        else:
            print("No trades found")
    else:
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()