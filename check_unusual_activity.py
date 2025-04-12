"""
Check how unusual options activity is detected and where transaction dates come from
"""
import os
import requests
import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
BASE_URL = "https://api.polygon.io"

def get_unusual_options_activity_direct(ticker):
    """
    Directly query Polygon API for options activity data
    """
    print(f"Checking unusual options activity for {ticker} directly from Polygon")
    
    # Get current price first for strike price reference
    price_endpoint = f"{BASE_URL}/v2/aggs/ticker/{ticker}/prev?apiKey={POLYGON_API_KEY}"
    price_response = requests.get(price_endpoint, timeout=10)
    current_price = 0
    
    if price_response.status_code == 200:
        price_data = price_response.json()
        if 'results' in price_data and price_data['results']:
            current_price = price_data['results'][0]['c']
            print(f"\nCurrent price for {ticker}: ${current_price}")
    else:
        print(f"Error getting current price: {price_response.status_code}")
    
    # Get available option expiration dates
    expiry_endpoint = f"{BASE_URL}/v3/reference/options/contracts?underlying_ticker={ticker}&apiKey={POLYGON_API_KEY}"
    expiry_response = requests.get(expiry_endpoint, timeout=10)
    
    expiry_dates = set()
    if expiry_response.status_code == 200:
        contracts = expiry_response.json().get('results', [])
        for contract in contracts:
            if 'expiration_date' in contract:
                expiry_dates.add(contract['expiration_date'])
        
        print(f"\nFound {len(expiry_dates)} expiration dates")
    else:
        print(f"Error getting expiration dates: {expiry_response.status_code}")
    
    # Sort dates and take the next few expirations
    sorted_dates = sorted(list(expiry_dates))
    target_dates = sorted_dates[:min(5, len(sorted_dates))]
    
    print(f"\nAnalyzing options for expiry dates: {', '.join(target_dates)}")
    
    # Get and analyze options for each expiry date
    unusual_activity = []
    
    for expiry in target_dates:
        print(f"\nChecking options for {expiry}")
        
        # Get option chain for this expiry
        chain_endpoint = f"{BASE_URL}/v3/reference/options/contracts?underlying_ticker={ticker}&expiration_date={expiry}&apiKey={POLYGON_API_KEY}"
        chain_response = requests.get(chain_endpoint, timeout=10)
        
        if chain_response.status_code == 200:
            contracts = chain_response.json().get('results', [])
            print(f"Found {len(contracts)} contracts for {expiry}")
            
            # Process each contract
            call_activity = []
            put_activity = []
            
            # Request snapshot data for all options of this ticker
            snapshot_endpoint = f"{BASE_URL}/v3/snapshot/options/{ticker}?expiration_date={expiry}&apiKey={POLYGON_API_KEY}"
            snapshot_response = requests.get(snapshot_endpoint, timeout=10)
            
            if snapshot_response.status_code == 200:
                snapshot_data = snapshot_response.json().get('results', [])
                print(f"Found {len(snapshot_data)} contracts with snapshot data")
                
                # Create a map of ticker to snapshot data for quick lookup
                snapshot_map = {contract['ticker']: contract for contract in snapshot_data}
                
                # Process each contract with available data
                for contract in contracts:
                    ticker_symbol = contract.get('ticker')
                    snapshot = snapshot_map.get(ticker_symbol)
                    
                    if snapshot:
                        # Get key data
                        strike = contract.get('strike_price', 0)
                        contract_type = contract.get('contract_type', '').lower()
                        day_data = snapshot.get('day', {})
                        open_interest = snapshot.get('open_interest', 0)
                        volume = day_data.get('volume', 0)
                        vwap = day_data.get('vwap', 0)
                        
                        # Option value (rough estimate)
                        option_price = vwap if vwap else 0
                        
                        # Calculate volume to OI ratio and dollar amount
                        volume_oi_ratio = volume / max(open_interest, 1)
                        dollar_amount = volume * option_price * 100  # 100 shares per contract
                        
                        # Only process if we have meaningful data
                        if volume > 0 and dollar_amount > 0:
                            # Create activity entry
                            activity = {
                                'ticker': ticker_symbol,
                                'strike': strike,
                                'expiry': expiry,
                                'volume': volume,
                                'open_interest': open_interest,
                                'volume_oi_ratio': volume_oi_ratio,
                                'option_price': option_price,
                                'amount': dollar_amount,
                                'distance_from_current': abs(current_price - strike) / current_price if current_price else 0
                            }
                            
                            # Add to appropriate list
                            if contract_type == 'call':
                                call_activity.append(activity)
                            elif contract_type == 'put':
                                put_activity.append(activity)
                    
                # Sort by dollar amount (descending)
                call_activity.sort(key=lambda x: x['amount'], reverse=True)
                put_activity.sort(key=lambda x: x['amount'], reverse=True)
                
                # Take top activities
                top_calls = call_activity[:3]
                top_puts = put_activity[:3]
                
                # Print summary
                print(f"\nTop Call Activity for {expiry}:")
                for activity in top_calls:
                    strike = activity['strike']
                    volume = activity['volume']
                    amount = activity['amount']
                    print(f"  ${strike} calls: {volume} contracts, ${amount:,.2f} premium")
                    
                    # Check for trade data
                    option_symbol = activity['ticker']
                    trade_endpoint = f"{BASE_URL}/v3/trades/{option_symbol}?limit=10&apiKey={POLYGON_API_KEY}"
                    trade_response = requests.get(trade_endpoint, timeout=10)
                    
                    if trade_response.status_code == 200:
                        trades = trade_response.json().get('results', [])
                        if trades:
                            # Get most recent trade
                            latest_trade = trades[0]
                            timestamp = latest_trade.get('sip_timestamp', 0)
                            if timestamp:
                                trade_date = datetime.datetime.fromtimestamp(timestamp / 1e9)
                                date_str = trade_date.strftime("%m/%d/%y %H:%M:%S")
                                print(f"    Latest trade: {date_str}, ${latest_trade.get('price')}, size: {latest_trade.get('size')}")
                        else:
                            print("    No trade data available")
                    else:
                        print(f"    Error getting trade data: {trade_response.status_code}")
                
                print(f"\nTop Put Activity for {expiry}:")
                for activity in top_puts:
                    strike = activity['strike']
                    volume = activity['volume']
                    amount = activity['amount']
                    print(f"  ${strike} puts: {volume} contracts, ${amount:,.2f} premium")
                    
                    # Check for trade data
                    option_symbol = activity['ticker']
                    trade_endpoint = f"{BASE_URL}/v3/trades/{option_symbol}?limit=10&apiKey={POLYGON_API_KEY}"
                    trade_response = requests.get(trade_endpoint, timeout=10)
                    
                    if trade_response.status_code == 200:
                        trades = trade_response.json().get('results', [])
                        if trades:
                            # Get most recent trade
                            latest_trade = trades[0]
                            timestamp = latest_trade.get('sip_timestamp', 0)
                            if timestamp:
                                trade_date = datetime.datetime.fromtimestamp(timestamp / 1e9)
                                date_str = trade_date.strftime("%m/%d/%y %H:%M:%S")
                                print(f"    Latest trade: {date_str}, ${latest_trade.get('price')}, size: {latest_trade.get('size')}")
                        else:
                            print("    No trade data available")
                    else:
                        print(f"    Error getting trade data: {trade_response.status_code}")
                        
                # Combine all activities
                unusual_activity.extend(top_calls)
                unusual_activity.extend(top_puts)
            else:
                print(f"Error getting snapshot data: {snapshot_response.status_code}")
        else:
            print(f"Error getting option chain: {chain_response.status_code}")
    
    # Overall summary - find the largest flow
    if unusual_activity:
        # Sort by amount (descending)
        unusual_activity.sort(key=lambda x: x['amount'], reverse=True)
        
        largest_flow = unusual_activity[0]
        strike = largest_flow['strike']
        expiry = largest_flow['expiry']
        amount = largest_flow['amount']
        option_symbol = largest_flow['ticker']
        
        is_call = 'C' in option_symbol
        sentiment = "bullish" if is_call else "bearish"
        
        print(f"\nLargest flow: ${amount:,.2f} million {sentiment} bet with {'out-of-the-money' if (is_call and strike > current_price) or (not is_call and strike < current_price) else 'in-the-money'} (${strike}) options expiring on {expiry}")
        
        # Check for trade data
        trade_endpoint = f"{BASE_URL}/v3/trades/{option_symbol}?limit=10&apiKey={POLYGON_API_KEY}"
        trade_response = requests.get(trade_endpoint, timeout=10)
        
        if trade_response.status_code == 200:
            trades = trade_response.json().get('results', [])
            if trades:
                print("\nMost recent trades for largest flow:")
                for i, trade in enumerate(trades[:5]):
                    timestamp = trade.get('sip_timestamp', 0)
                    if timestamp:
                        trade_date = datetime.datetime.fromtimestamp(timestamp / 1e9)
                        date_str = trade_date.strftime("%m/%d/%y %H:%M:%S")
                        print(f"  {i+1}. {date_str}: ${trade.get('price')}, size: {trade.get('size')}")
            else:
                print("\nNo trade data available for largest flow")
        else:
            print(f"\nError getting trade data for largest flow: {trade_response.status_code}")
    else:
        print("\nNo unusual activity detected")

# Test with SPY and TSLA
get_unusual_options_activity_direct("SPY")
print("\n" + "="*80 + "\n")
get_unusual_options_activity_direct("TSLA")