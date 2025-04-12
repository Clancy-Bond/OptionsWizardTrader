import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

# Test getting option trades data with timestamps
def get_option_trades(option_symbol, limit=10):
    """
    Get recent trades for a specific option contract
    """
    endpoint = f'https://api.polygon.io/v3/trades/{option_symbol}?limit={limit}&apiKey={POLYGON_API_KEY}'
    print(f"Calling endpoint: {endpoint}")
    
    response = requests.get(endpoint)
    
    if response.status_code != 200:
        print(f"Error: Status code {response.status_code}")
        return None
    
    data = response.json()
    return data.get('results', [])

# Convert nanosecond timestamp to readable date
def format_timestamp(timestamp_ns):
    if not timestamp_ns:
        return "N/A"
    
    # Convert nanoseconds to seconds and then to datetime
    dt = datetime.fromtimestamp(timestamp_ns / 1e9)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# Test with an AAPL option
option_symbol = "O:AAPL250417C00100000"  # AAPL Call, Strike $100, Expiry 2025-04-17
trades = get_option_trades(option_symbol)

if trades:
    print(f"\nFound {len(trades)} trades for {option_symbol}")
    print("\nMost recent trades:")
    
    for i, trade in enumerate(trades[:5], 1):
        price = trade.get('price', 'N/A')
        size = trade.get('size', 'N/A')
        
        # Get the timestamp (prefer participant_timestamp if available, fall back to sip_timestamp)
        timestamp = trade.get('participant_timestamp') or trade.get('sip_timestamp')
        date_str = format_timestamp(timestamp)
        
        print(f"Trade {i}: Price=${price}, Size={size}, Date={date_str}")
        print(f"Raw data: {json.dumps(trade, indent=2)}")
        print("-" * 40)
else:
    print(f"No trades found for {option_symbol}")