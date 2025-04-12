"""
Test the options endpoint with a limit parameter
"""

import requests
import os
import time
from datetime import datetime

# Setup Polygon.io API access
BASE_URL = "https://api.polygon.io"
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

def get_headers():
    """Get authenticated headers for Polygon API requests"""
    return {
        'Authorization': f'Bearer {POLYGON_API_KEY}'
    }

def test_options_endpoint(ticker, limit=1000):
    """Test the options endpoint with different limit values"""
    if not ticker:
        return None
    
    ticker = ticker.upper()
    print(f"\n=== TESTING OPTIONS ENDPOINT FOR {ticker} WITH LIMIT={limit} ===\n")
    
    try:
        # Build the API endpoint with limit
        endpoint = f"{BASE_URL}/v3/reference/options/contracts?underlying_ticker={ticker}&limit={limit}&apiKey={POLYGON_API_KEY}"
        
        # Make the API call
        print(f"Calling endpoint: {endpoint}")
        start_time = time.time()
        response = requests.get(endpoint, headers=get_headers())
        elapsed = time.time() - start_time
        
        print(f"API call completed in {elapsed:.2f} seconds with status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error: {response.text}")
            return
        
        # Process the response
        data = response.json()
        results = data.get('results', [])
        
        print(f"Total options returned: {len(results)}")
        
        # Check for near-the-money options
        # First get current stock price
        price_endpoint = f"{BASE_URL}/v2/last/trade/{ticker}?apiKey={POLYGON_API_KEY}"
        price_response = requests.get(price_endpoint, headers=get_headers())
        
        current_price = None
        if price_response.status_code == 200:
            price_data = price_response.json()
            if 'results' in price_data and 'p' in price_data['results']:
                current_price = price_data['results']['p']
        
        print(f"Current stock price: {current_price}")
        
        if current_price:
            # Count options near the money
            near_money_options = [
                option for option in results 
                if 'strike_price' in option 
                and abs(option['strike_price'] - current_price) / current_price <= 0.1
            ]
            
            print(f"Options near the money (within 10%): {len(near_money_options)}")
            
            # List first 5 near-the-money options
            print("\nSample of near-the-money options:")
            for i, option in enumerate(near_money_options[:5]):
                strike = option.get('strike_price')
                expiry = option.get('expiration_date')
                contract_type = option.get('contract_type', '').upper()
                option_symbol = option.get('ticker')
                
                print(f"{i+1}. {ticker} {strike} {expiry} {contract_type} ({option_symbol})")
                print(f"   Strike % from current price: {abs(strike - current_price) / current_price:.2%}")
        
        # Group by expiration date
        expirations = {}
        for option in results:
            exp_date = option.get('expiration_date')
            if exp_date:
                if exp_date not in expirations:
                    expirations[exp_date] = []
                expirations[exp_date].append(option)
        
        print(f"\nOptions grouped by expiration date:")
        for date, options in sorted(expirations.items()):
            print(f"{date}: {len(options)} options")
        
        # Count calls vs puts
        calls = sum(1 for option in results if option.get('contract_type', '').lower() == 'call')
        puts = sum(1 for option in results if option.get('contract_type', '').lower() == 'put')
        
        print(f"\nOptions by type:")
        print(f"Calls: {calls}")
        print(f"Puts: {puts}")
        
        return results
        
    except Exception as e:
        print(f"Error testing options endpoint: {str(e)}")
        return None

if __name__ == "__main__":
    ticker = input("Enter ticker to test (e.g., AAPL): ").strip().upper()
    test_options_endpoint(ticker)