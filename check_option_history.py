"""
Script to check option history from Polygon API
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
BASE_URL = "https://api.polygon.io"

def check_option_data(option_symbol):
    """
    Check various Polygon.io endpoints for option data
    """
    print(f"Checking data for option: {option_symbol}")
    
    # 1. Check option details
    details = {}  # Initialize details dictionary
    details_endpoint = f"{BASE_URL}/v3/reference/options/contracts/{option_symbol}?apiKey={POLYGON_API_KEY}"
    details_response = requests.get(details_endpoint, timeout=10)
    
    if details_response.status_code == 200:
        details = details_response.json().get('results', {})
        print(f"\nOption Details:")
        print(f"  Underlying: {details.get('underlying_ticker')}")
        print(f"  Strike Price: ${details.get('strike_price')}")
        print(f"  Expiration: {details.get('expiration_date')}")
        print(f"  Type: {details.get('contract_type')}")
        print(f"  Exercise Style: {details.get('exercise_style')}")
        print(f"  Shares Per Contract: {details.get('shares_per_contract')}")
        print(f"  Primary Exchange: {details.get('primary_exchange')}")
        
        # Check creation date or effective date if available
        if details.get('effective_date'):
            print(f"  Effective Date: {details.get('effective_date')}")
    else:
        print(f"Error getting option details: {details_response.status_code}")
    
    # 2. Get historical aggregates (OHLC data)
    # Try to get all historical data for this option
    aggs_endpoint = f"{BASE_URL}/v2/aggs/ticker/{option_symbol}/range/1/day/2023-01-01/{datetime.now().strftime('%Y-%m-%d')}?apiKey={POLYGON_API_KEY}"
    aggs_response = requests.get(aggs_endpoint, timeout=10)
    
    if aggs_response.status_code == 200:
        aggs_data = aggs_response.json().get('results', [])
        if aggs_data:
            earliest_data = min(aggs_data, key=lambda x: x['t'])
            latest_data = max(aggs_data, key=lambda x: x['t'])
            
            earliest_date = datetime.fromtimestamp(earliest_data['t']/1000).strftime('%Y-%m-%d')
            latest_date = datetime.fromtimestamp(latest_data['t']/1000).strftime('%Y-%m-%d')
            
            print(f"\nHistorical Data:")
            print(f"  Earliest Trading Date: {earliest_date}")
            print(f"  Latest Trading Date: {latest_date}")
            print(f"  Total Days with Data: {len(aggs_data)}")
            
            print(f"\nEarliest Trading Data:")
            print(f"  Date: {earliest_date}")
            print(f"  Open: ${earliest_data['o']}")
            print(f"  High: ${earliest_data['h']}")
            print(f"  Low: ${earliest_data['l']}")
            print(f"  Close: ${earliest_data['c']}")
            print(f"  Volume: {earliest_data['v']}")
        else:
            print("\nNo historical aggregate data found")
    else:
        print(f"Error getting historical data: {aggs_response.status_code}")
    
    # 3. Check today's quotes
    today = datetime.now().strftime('%Y-%m-%d')
    quotes_endpoint = f"{BASE_URL}/v3/quotes/{option_symbol}?timestamp.gte={today}&limit=100&apiKey={POLYGON_API_KEY}"
    quotes_response = requests.get(quotes_endpoint, timeout=10)
    
    if quotes_response.status_code == 200:
        quotes = quotes_response.json().get('results', [])
        if quotes:
            print(f"\nToday's Quotes:")
            print(f"  Quote Count: {len(quotes)}")
            first_quote = quotes[0]
            if first_quote:
                quote_time = datetime.fromtimestamp(first_quote.get('sip_timestamp', 0)/1000000000).strftime('%Y-%m-%d %H:%M:%S')
                print(f"  Latest Quote Time: {quote_time}")
                print(f"  Ask: ${first_quote.get('ask_price')}")
                print(f"  Bid: ${first_quote.get('bid_price')}")
        else:
            print("\nNo quotes found today")
    else:
        print(f"Error getting quotes: {quotes_response.status_code}")
    
    # 4. Try the snapshots API
    snapshot_endpoint = f"{BASE_URL}/v3/snapshot/options/{details.get('underlying_ticker', 'SPY')}?apiKey={POLYGON_API_KEY}"
    snapshot_response = requests.get(snapshot_endpoint, timeout=10)
    
    if snapshot_response.status_code == 200:
        data = snapshot_response.json()
        matching_contract = None
        
        for contract in data.get('results', []):
            if contract.get('ticker') == option_symbol:
                matching_contract = contract
                break
        
        if matching_contract:
            print(f"\nOption Snapshot:")
            print(f"  Open Interest: {matching_contract.get('open_interest')}")
            print(f"  Implied Volatility: {matching_contract.get('implied_volatility')}")
            print(f"  Delta: {matching_contract.get('greeks', {}).get('delta')}")
            print(f"  Volume: {matching_contract.get('day', {}).get('volume')}")
            print(f"  VWAP: ${matching_contract.get('day', {}).get('vwap')}")
        else:
            print("\nNo matching contract found in snapshot data")
    else:
        print(f"Error getting snapshot: {snapshot_response.status_code}")

# Test with the SPY option from the unusual activity
check_option_data('O:SPY250414C00000535')

# Try with a couple of other examples
print("\n" + "="*50 + "\n")
check_option_data('O:SPY250117C00000500')  # Longer dated option

print("\n" + "="*50 + "\n")
check_option_data('O:AAPL250117C00000200')  # AAPL option