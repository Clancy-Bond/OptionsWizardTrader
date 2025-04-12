"""
Get options snapshot data to understand the structure
"""
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
BASE_URL = "https://api.polygon.io"

def check_options_snapshot(ticker, expiry_date=None):
    """Get and display options snapshot data"""
    
    url_params = f"?underlying_ticker={ticker}&apiKey={POLYGON_API_KEY}"
    if expiry_date:
        url_params += f"&expiration_date={expiry_date}"
    
    snapshot_endpoint = f"{BASE_URL}/v3/snapshot/options/{ticker}{url_params}"
    print(f"Fetching options snapshot from: {snapshot_endpoint}")
    
    response = requests.get(snapshot_endpoint, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print("\nResponse structure:")
        print(json.dumps(data, indent=2)[:2000] + "...(truncated)")
        
        results = data.get('results', [])
        print(f"\nFound {len(results)} contracts in snapshot")
        
        if results:
            # Print structure of the first result
            print("\nFirst contract structure:")
            print(json.dumps(results[0], indent=2))
            
            # Print basic summary of all contracts
            print("\nBasic summary:")
            for i, contract in enumerate(results[:5]):  # Show first 5 only
                details = contract.get('details', {})
                ticker_str = details.get('ticker', 'Unknown')
                strike = details.get('strike_price', 0)
                expiry = details.get('expiration_date', 'Unknown')
                contract_type = details.get('contract_type', 'Unknown')
                day_data = contract.get('day', {})
                open_interest = contract.get('open_interest', 0)
                volume = day_data.get('volume', 0)
                vwap = day_data.get('vwap', 0)
                
                print(f"{i+1}. {ticker_str}: ${strike} {contract_type.upper()} exp {expiry}")
                print(f"   Vol: {volume}, OI: {open_interest}, VWAP: ${vwap}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# Check SPY options snapshot
check_options_snapshot("SPY", "2025-04-14")

# Also check a specific option - try the one with volume
print("\n" + "="*80 + "\n")

# This option had volume according to the snapshot data
option_symbol = "O:SPY250414C00310000"
trades_endpoint = f"{BASE_URL}/v3/trades/{option_symbol}?limit=10&apiKey={POLYGON_API_KEY}"
print(f"Checking trades for {option_symbol} from: {trades_endpoint}")

trades_response = requests.get(trades_endpoint, timeout=10)
if trades_response.status_code == 200:
    trades_data = trades_response.json()
    print(json.dumps(trades_data, indent=2))
else:
    print(f"Error: {trades_response.status_code}")
    print(trades_response.text)

# Also check the original option mentioned ($535)
print("\n" + "="*80 + "\n")
option_symbol = "O:SPY250414C00535000"
trades_endpoint = f"{BASE_URL}/v3/trades/{option_symbol}?limit=10&apiKey={POLYGON_API_KEY}"
print(f"Checking trades for {option_symbol} from: {trades_endpoint}")

trades_response = requests.get(trades_endpoint, timeout=10)
if trades_response.status_code == 200:
    trades_data = trades_response.json()
    print(json.dumps(trades_data, indent=2))
else:
    print(f"Error: {trades_response.status_code}")
    print(trades_response.text)