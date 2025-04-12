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
# Include both long-dated and shorter-dated options
from datetime import datetime, timedelta

# Current date for reference
today = datetime.now()
# Get this Friday's date
days_to_friday = (4 - today.weekday()) % 7
this_friday = today + timedelta(days=days_to_friday)
friday_date = this_friday.strftime('%Y-%m-%d')

# Get next month's expiration (third Friday)
next_month = today.replace(day=1) + timedelta(days=32)
first_day_next_month = next_month.replace(day=1)
days_to_third_friday = ((4 - first_day_next_month.weekday()) % 7) + 14
third_friday = first_day_next_month + timedelta(days=days_to_third_friday)
next_month_date = third_friday.strftime('%Y-%m-%d')

print(f"Testing options for this Friday: {friday_date}")
print(f"Testing options for next month: {next_month_date}")

# Since we're in a simulated 2025 environment, we need to try options from 2024
# These would be the options that likely have recorded trades
test_options = [
    # Popular contracts from 2024
    {"ticker": "AAPL", "strike": 170, "expiry": "2024-04-19"},
    {"ticker": "AAPL", "strike": 170, "expiry": "2024-05-17"},
    {"ticker": "AAPL", "strike": 170, "expiry": "2024-06-21"},
    {"ticker": "AAPL", "strike": 180, "expiry": "2024-04-19"},
    
    {"ticker": "TSLA", "strike": 160, "expiry": "2024-04-19"},
    {"ticker": "TSLA", "strike": 160, "expiry": "2024-05-17"},
    {"ticker": "TSLA", "strike": 160, "expiry": "2024-06-21"},
    
    {"ticker": "SPY", "strike": 500, "expiry": "2024-04-19"},
    {"ticker": "SPY", "strike": 500, "expiry": "2024-05-17"},
    {"ticker": "SPY", "strike": 500, "expiry": "2024-06-21"},
    
    # Weekly options - pick this week in 2024
    {"ticker": "SPY", "strike": 475, "expiry": "2024-04-12"},
    {"ticker": "QQQ", "strike": 400, "expiry": "2024-04-12"},
]

# Try both call and put options for each configuration
for option in test_options:
    ticker = option["ticker"]
    strike = option["strike"]
    expiry = option["expiry"]
    
    # Process expiration date
    option_date = datetime.strptime(expiry, '%Y-%m-%d')
    option_date_str = option_date.strftime('%y%m%d')
    strike_price_padded = f"{strike:08.0f}"
    
    # Test both call and put
    for option_type in ['C', 'P']:
        option_symbol = f"O:{ticker}{option_date_str}{option_type}{strike_price_padded}"
        print(f"\n===== Testing {ticker} {option_type} @ ${strike} exp {expiry} =====")
        print(f"Option symbol: {option_symbol}")
        
        # Use different date ranges to look for trades
        BASE_URL = "https://api.polygon.io"
        endpoint = f'{BASE_URL}/v3/trades/{option_symbol}?limit=20&apiKey={POLYGON_API_KEY}'
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