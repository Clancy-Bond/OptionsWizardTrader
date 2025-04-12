"""
Debug script to troubleshoot unusual options activity detection
"""

import os
import polygon_integration as polygon
from polygon_integration import get_option_chain, get_current_price, throttled_api_call, get_headers, BASE_URL, POLYGON_API_KEY
from polygon_trades import get_option_trade_data

def debug_unusual_activity(ticker):
    """
    Detailed debugging of unusual options activity detection
    """
    if not ticker:
        print("No ticker provided")
        return
    
    ticker = ticker.upper()
    print(f"\n=== DEBUGGING UNUSUAL OPTIONS ACTIVITY FOR {ticker} ===\n")
    
    # Check API key
    api_key = os.getenv('POLYGON_API_KEY')
    print(f"Polygon API Key available: {api_key is not None}")
    
    # Get stock price
    print("\n--- STOCK PRICE DATA ---")
    stock_price = get_current_price(ticker)
    print(f"Current stock price for {ticker}: {stock_price}")
    
    # Get options chain
    print("\n--- OPTIONS CHAIN DATA ---")
    chain = get_option_chain(ticker)
    if not chain:
        print(f"No option chain found for {ticker}")
        return
    
    print(f"Options chain contains {len(chain)} options")
    
    # Count near-the-money options
    near_money_count = 0
    if stock_price:
        near_money_count = sum(1 for option in chain if 'strike_price' in option and abs(option['strike_price'] - stock_price) / stock_price <= 0.1)
    print(f"Options near the money (within 10%): {near_money_count}")
    
    # Sample some options to check
    sample_size = min(5, len(chain))
    print(f"\n--- SAMPLING {sample_size} OPTIONS FOR DETAILED ANALYSIS ---")
    
    for i in range(sample_size):
        option = chain[i]
        option_symbol = option.get('ticker')
        strike = option.get('strike_price')
        expiry = option.get('expiration_date')
        contract_type = option.get('contract_type', '').lower()
        
        print(f"\nOption: {ticker} {strike} {expiry} {contract_type.upper()} ({option_symbol})")
        
        # Skip if missing key info
        if not strike or not expiry or not contract_type:
            print("  Missing key information (strike, expiry, or type)")
            continue
        
        # Check if near the money
        if stock_price:
            pct_diff = abs(strike - stock_price) / stock_price
            print(f"  Strike % from current price: {pct_diff:.2%} (threshold: 10%)")
            if pct_diff > 0.1:
                print("  SKIPPED: Not near the money")
                continue
        
        # Get trades for this option
        print(f"  Checking trades for {option_symbol}...")
        endpoint = f"{BASE_URL}/v3/trades/{option_symbol}?limit=50&order=desc&apiKey={POLYGON_API_KEY}"
        response = throttled_api_call(endpoint, headers=get_headers())
        
        if response.status_code != 200:
            print(f"  ERROR: API returned status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            continue
        
        data = response.json()
        trades = data.get('results', [])
        print(f"  Total trades found: {len(trades)}")
        
        # Look for large size trades (>20 contracts)
        large_trades = [t for t in trades if t.get('size', 0) > 20]
        print(f"  Large trades (>20 contracts): {len(large_trades)}")
        
        if large_trades:
            # Calculate some metrics
            total_volume = sum(t.get('size', 0) for t in large_trades)
            avg_price = sum(t.get('price', 0) * t.get('size', 0) for t in large_trades) / total_volume if total_volume > 0 else 0
            total_premium = total_volume * 100 * avg_price  # Each contract is 100 shares
            
            print(f"  Total volume: {total_volume} contracts")
            print(f"  Average price: ${avg_price:.2f} per contract")
            print(f"  Total premium: ${total_premium:.2f}")
            
            # Only include if premium is significant (>$10,000)
            if total_premium > 10000:
                print(f"  FOUND UNUSUAL ACTIVITY: Premium (${total_premium:.2f}) exceeds $10,000 threshold")
                
                # Get detailed trade info from our trade data function
                try:
                    trade_info = get_option_trade_data(option_symbol)
                    if trade_info:
                        print(f"  Trade data available: {trade_info}")
                    else:
                        print("  No detailed trade data available")
                except Exception as e:
                    print(f"  Error getting trade data: {str(e)}")
            else:
                print(f"  Not unusual: Premium (${total_premium:.2f}) below $10,000 threshold")
        else:
            print("  No large trades found")
    
    # Now run the actual unusual activity function
    print("\n--- RUNNING PRODUCTION UNUSUAL ACTIVITY DETECTION ---")
    activity = polygon.get_unusual_options_activity(ticker)
    
    print(f"Unusual activity detection returned: {activity}")
    print(f"Found {len(activity) if activity else 0} unusual activity items")

if __name__ == "__main__":
    ticker = input("Enter ticker to debug (e.g., AAPL): ").strip().upper()
    debug_unusual_activity(ticker)