"""
Test scoring for a specific option symbol
"""
import os
import requests
import json
from datetime import datetime
from polygon_integration import calculate_unusualness_score, get_headers, throttled_api_call

# Load Polygon API key from environment
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
BASE_URL = "https://api.polygon.io"

def test_option_scoring(option_symbol, ticker="TSLA"):
    """
    Test the scoring system on a specific option symbol
    """
    print(f"\nScoring unusual activity for {option_symbol}\n")
    
    # First get the current stock price
    price_endpoint = f"{BASE_URL}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}?apiKey={POLYGON_API_KEY}"
    price_response = throttled_api_call(price_endpoint, headers=get_headers())
    
    if price_response.status_code != 200:
        print(f"Error fetching price: {price_response.status_code}")
        return
    
    price_data = price_response.json()
    stock_price = price_data.get('ticker', {}).get('day', {}).get('c', 0)
    
    if not stock_price:
        print("Could not get current stock price")
        return
    
    print(f"Current {ticker} price: ${stock_price}")
    
    # Now get the option data
    option_endpoint = f"{BASE_URL}/v3/reference/options/contracts/{option_symbol}?apiKey={POLYGON_API_KEY}"
    option_response = throttled_api_call(option_endpoint, headers=get_headers())
    
    if option_response.status_code != 200:
        print(f"Error fetching option data: {option_response.status_code}")
        return
    
    option_data = option_response.json()
    option = option_data.get('results', {})
    
    if not option:
        print("No option data found")
        return
    
    print(f"Option type: {option.get('contract_type')}")
    print(f"Strike price: ${option.get('strike_price')}")
    print(f"Expiration: {option.get('expiration_date')}")
    
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
    
    print(f"Found {len(trades)} trades")
    
    # Calculate unusualness score
    score, breakdown = calculate_unusualness_score(option, trades, stock_price)
    
    print(f"\nUnusualness Score: {score}/100\n")
    print("Score breakdown:")
    
    for category, points in breakdown.items():
        if category not in ['total_volume', 'total_premium', 'largest_trade', 'vol_oi_ratio']:
            print(f"  {category}: {points} points")
    
    print("\nAdditional metrics:")
    print(f"  Total Volume: {breakdown.get('total_volume', 'N/A')}")
    print(f"  Total Premium: ${breakdown.get('total_premium', 0):,.2f}")
    print(f"  Largest Trade: {breakdown.get('largest_trade', 'N/A')} contracts")
    if 'vol_oi_ratio' in breakdown:
        print(f"  Volume/OI Ratio: {breakdown.get('vol_oi_ratio')}")

if __name__ == "__main__":
    # Test with the TSLA option that had the highest score from our logs
    test_option_scoring("O:TSLA250425P00260000")