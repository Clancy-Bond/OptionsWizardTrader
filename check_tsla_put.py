"""
Check details of the TSLA 260 April 25, 2025 PUT trade
"""
import os
import requests
import json
from datetime import datetime
from polygon_integration import get_headers, throttled_api_call

# Load Polygon API key from environment
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
BASE_URL = "https://api.polygon.io"

def examine_option_trades(option_symbol):
    """
    Get detailed information about trades for a specific option
    """
    print(f"\nExamining trades for {option_symbol}\n")
    
    # Get trades for this option
    trades_endpoint = f"{BASE_URL}/v3/trades/{option_symbol}?limit=50&order=desc&apiKey={POLYGON_API_KEY}"
    trades_response = throttled_api_call(trades_endpoint, headers=get_headers())
    
    if trades_response.status_code != 200:
        print(f"Error fetching trades: {trades_response.status_code}")
        return
    
    trades_data = trades_response.json()
    trades = trades_data.get('results', [])
    
    if not trades:
        print("No trades found for this option")
        return
    
    print(f"Found {len(trades)} trades\n")
    
    # Get option details
    option_endpoint = f"{BASE_URL}/v3/reference/options/contracts/{option_symbol}?apiKey={POLYGON_API_KEY}"
    option_response = throttled_api_call(option_endpoint, headers=get_headers())
    
    if option_response.status_code != 200:
        print(f"Error fetching option data: {option_response.status_code}")
        return
    
    option_data = option_response.json()
    option = option_data.get('results', {})
    
    # Print option details
    print(f"TSLA {option.get('strike_price')} {option.get('expiration_date')} {option.get('contract_type', '').upper()}")
    print(f"Open Interest: {option.get('open_interest', 'N/A')}")
    print(f"Current Option Price: ${option.get('close_price', 'N/A')}")
    print(f"Current Implied Volatility: {option.get('implied_volatility', 'N/A')}\n")
    
    # Sort trades by size to find the largest trades
    sorted_trades = sorted(trades, key=lambda x: x.get('size', 0), reverse=True)
    
    # Print the top 5 largest trades
    print("LARGEST TRADES:")
    for i, trade in enumerate(sorted_trades[:5]):
        trade_size = trade.get('size', 0)
        trade_price = trade.get('price', 0)
        total_premium = trade_size * 100 * trade_price
        
        # Format the timestamp
        timestamp_ns = trade.get('sip_timestamp', 0)
        timestamp_s = timestamp_ns / 1_000_000_000
        trade_time = datetime.fromtimestamp(timestamp_s).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"Trade #{i+1}:")
        print(f"  Size: {trade_size} contracts")
        print(f"  Price: ${trade_price:.2f} per contract")
        print(f"  Total Premium: ${total_premium:,.2f}")
        print(f"  Time: {trade_time}")
        print(f"  Exchange: {trade.get('exchange', 'N/A')}")
        print()
    
    # Calculate total volume and premium
    total_volume = sum(t.get('size', 0) for t in trades)
    total_premium = sum(t.get('size', 0) * 100 * t.get('price', 0) for t in trades)
    
    print(f"SUMMARY:")
    print(f"  Total Volume: {total_volume} contracts")
    print(f"  Total Premium: ${total_premium:,.2f}")
    print(f"  Average Price: ${total_premium / (total_volume * 100):.2f} per contract")
    
    # Calculate volume/open interest ratio
    open_interest = option.get('open_interest', 0)
    if open_interest > 0:
        vol_oi_ratio = total_volume / open_interest
        print(f"  Volume/Open Interest Ratio: {vol_oi_ratio:.2f}")

if __name__ == "__main__":
    examine_option_trades("O:TSLA250425P00260000")