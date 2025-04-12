"""
Test script for Polygon.io options trade data
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
print(f"API Key: {POLYGON_API_KEY}")

def get_option_trades(option_symbol, limit=10):
    """
    Get recent trades for a specific option contract
    """
    BASE_URL = "https://api.polygon.io"
    endpoint = f'{BASE_URL}/v3/trades/{option_symbol}?limit={limit}&apiKey={POLYGON_API_KEY}'
    print(f"Calling API: {endpoint}")
    
    try:
        response = requests.get(endpoint, timeout=10)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def format_timestamp(timestamp_ns):
    # Convert nanoseconds to seconds and then to datetime
    trade_date = datetime.fromtimestamp(timestamp_ns / 1e9)
    return trade_date.strftime("%Y-%m-%d %H:%M:%S")

# Test with some current options (that would be expiring very soon)
print("\n===== Looking at active options for the current date =====")

# Try options from 2023 and 2024 which definitely had trading activity
options_to_test = [
    # 2023 options (historical)
    "O:AAPL230616C00160000",  # AAPL Jun 16 2023 Call $160
    "O:AAPL230616P00160000",  # AAPL Jun 16 2023 Put $160
    "O:SPY230616C00410000",   # SPY Jun 16 2023 Call $410
    "O:SPY230616P00410000",   # SPY Jun 16 2023 Put $410
    
    # 2024 options (recent past)
    "O:AAPL240119C00170000",  # AAPL Jan 19 2024 Call $170
    "O:AAPL240119P00170000",  # AAPL Jan 19 2024 Put $170
    "O:SPY240119C00450000",   # SPY Jan 19 2024 Call $450
    "O:SPY240119P00450000",   # SPY Jan 19 2024 Put $450
    
    # Near-term options
    "O:AAPL240621C00170000",  # AAPL Jun 21 2024 Call $170
    "O:AAPL240621P00170000",  # AAPL Jun 21 2024 Put $170
    
    # 2025 options (future)
    "O:AAPL250418C00170000",  # AAPL Apr 18 2025 Call $170
    "O:AAPL250117C00170000",  # AAPL Jan 17 2025 Call $170
]

found_trades = False

for symbol in options_to_test:
    print(f"\nChecking trades for {symbol}")
    trades = get_option_trades(symbol, 20)
    
    if trades:
        found_trades = True
        print(f"Found {len(trades)} trades")
        for i, trade in enumerate(trades[:3]):
            price = trade.get('price')
            size = trade.get('size')
            timestamp = trade.get('participant_timestamp') or trade.get('sip_timestamp')
            date_str = format_timestamp(timestamp) if timestamp else "Unknown"
            print(f"Trade {i+1}: Price=${price}, Size={size}, Date: {date_str}")
    else:
        print("No trades found")

if not found_trades:
    print("\n===== Trying with some different date format variations =====")
    
    # Try different expiration date formatting to see if that makes a difference
    alt_format_options = [
        "O:AAPL250418C00000170",  # Pad with leading zeros
        "O:AAPL2504C00170000",    # Without day
        "O:AAPL25C00170000",      # Without day and month
        "O:AAPL2504C00170",       # Different strike format
    ]
    
    for symbol in alt_format_options:
        print(f"\nChecking trades for {symbol}")
        trades = get_option_trades(symbol, 20)
        
        if trades:
            print(f"Found {len(trades)} trades")
            for i, trade in enumerate(trades[:3]):
                price = trade.get('price')
                size = trade.get('size')
                timestamp = trade.get('participant_timestamp') or trade.get('sip_timestamp')
                date_str = format_timestamp(timestamp) if timestamp else "Unknown"
                print(f"Trade {i+1}: Price=${price}, Size={size}, Date: {date_str}")
        else:
            print("No trades found")