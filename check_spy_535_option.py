"""
Check specific SPY option data and trades
"""
import os
import json
import requests
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
BASE_URL = "https://api.polygon.io"

def check_strikes(underlying, expiration):
    """Get all available strikes for a given expiration"""
    
    chains_endpoint = f"{BASE_URL}/v3/reference/options/contracts?underlying_ticker={underlying}&expiration_date={expiration}&apiKey={POLYGON_API_KEY}"
    response = requests.get(chains_endpoint, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        contracts = data.get('results', [])
        
        call_strikes = []
        put_strikes = []
        
        for contract in contracts:
            strike = contract.get('strike_price')
            contract_type = contract.get('contract_type')
            
            if contract_type == 'call':
                call_strikes.append(strike)
            elif contract_type == 'put':
                put_strikes.append(strike)
        
        call_strikes.sort()
        put_strikes.sort()
        
        return {
            'calls': call_strikes,
            'puts': put_strikes
        }
    else:
        print(f"Error: {response.status_code}")
        return None

def check_option_for_trade_data(symbol, strike, expiration, option_type='call'):
    """Check if trade data exists for a specific option"""
    
    # Format the option symbol to match Polygon standard
    option_date = datetime.datetime.strptime(expiration, '%Y-%m-%d')
    option_date_str = option_date.strftime('%y%m%d')
    strike_price_padded = f"{strike:08.0f}"
    option_type_char = 'C' if option_type.lower() == 'call' else 'P'
    option_symbol = f"O:{symbol}{option_date_str}{option_type_char}{strike_price_padded}"
    
    print(f"Checking trades for {option_type} option: {option_symbol}")
    
    # Get option trades
    trades_endpoint = f"{BASE_URL}/v3/trades/{option_symbol}?limit=3&apiKey={POLYGON_API_KEY}"
    response = requests.get(trades_endpoint, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        trades = data.get('results', [])
        
        if trades:
            print(f"Found {len(trades)} trades")
            for i, trade in enumerate(trades):
                price = trade.get('price', 0)
                size = trade.get('size', 0)
                timestamp = trade.get('sip_timestamp', 0)
                
                if timestamp:
                    trade_date = datetime.datetime.fromtimestamp(timestamp / 1e9)
                    date_str = trade_date.strftime('%Y-%m-%d %H:%M:%S.%f')
                    print(f"  Trade {i+1}: {date_str} - Price: ${price}, Size: {size}")
                else:
                    print(f"  Trade {i+1}: Price: ${price}, Size: {size}")
                
            # Calculate total premium for a large trade scenario
            est_premium_per_contract = trades[0].get('price', 0)
            est_total_premium = est_premium_per_contract * 1000 * 100  # 1000 contracts * 100 shares
            print(f"\nEstimated premium for 1000 contracts: ${est_total_premium:,.2f}")
            
            # Check if this matches our target premium of ~$26.4 million
            target_contracts = 26400000 / (est_premium_per_contract * 100)
            print(f"Contracts needed for $26.4M premium: {int(target_contracts)}")
        else:
            print("No trades found")
    else:
        print(f"Error: {response.status_code}")

# Check available strikes for SPY on April 14, 2025
strikes = check_strikes("SPY", "2025-04-14")

if strikes:
    # Print available strikes
    print(f"\nAvailable call strikes for SPY April 14, 2025:")
    print(", ".join([str(x) for x in strikes['calls']]))
    
    # If 535 is in the list, check it specifically
    if 535 in strikes['calls']:
        print("\nChecking 535 strike:")
        check_option_for_trade_data("SPY", 535, "2025-04-14", "call")
    else:
        print("\n535 strike not found. Checking the closest strikes:")
        # Find the closest strikes to 535
        closest_strikes = sorted(strikes['calls'], key=lambda x: abs(x - 535))[:5]
        for strike in closest_strikes:
            print(f"\nChecking {strike} strike:")
            check_option_for_trade_data("SPY", strike, "2025-04-14", "call")