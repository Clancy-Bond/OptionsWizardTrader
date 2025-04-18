"""
Functions for accessing options trade data from Polygon.io
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')
BASE_URL = "https://api.polygon.io"

def format_timestamp(timestamp_ns):
    """
    Format a nanosecond timestamp to a human-readable date and time
    
    Args:
        timestamp_ns: Timestamp in nanoseconds
        
    Returns:
        Formatted date and time string in ISO format (YYYY-MM-DD)
    """
    if not timestamp_ns:
        return None
        
    # Convert nanoseconds to seconds
    timestamp_sec = timestamp_ns / 1e9
    # Format in ISO format (YYYY-MM-DD)
    return datetime.fromtimestamp(timestamp_sec).strftime("%Y-%m-%d")

def get_option_trade_data(option_symbol, min_size=5, min_date="2025-04-07"):
    """
    Get the most recent significant trade for a specific option contract
    
    Args:
        option_symbol: Option symbol in Polygon format (O:AAPL250417C00100000)
        min_size: Minimum trade size to consider significant
        min_date: Minimum date string in YYYY-MM-DD format (e.g., '2025-04-07')
        
    Returns:
        Dictionary with trade data including date, price, size, and exchange if available
        Returns a dict with just price if the option exists but has no trade history
        Returns None if the option doesn't exist or there was an error
    """
    try:
        # Use a larger limit to find a significant trade
        limit = 50
        endpoint = f'{BASE_URL}/v3/trades/{option_symbol}?limit={limit}&apiKey={POLYGON_API_KEY}'
        
        response = requests.get(endpoint, timeout=5)
        
        if response.status_code != 200:
            print(f"Error fetching option trades: {response.status_code}")
            return None
        
        data = response.json()
        trades = data.get('results', [])
        
        # If there are trades available, filter by date and get the most significant one
        if trades:
            print(f"Found {len(trades)} trades for {option_symbol}")
            
            # Filter trades by date if min_date is provided
            if min_date:
                try:
                    min_date_obj = datetime.strptime(min_date, '%Y-%m-%d').date()
                    filtered_trades = []
                    
                    for trade in trades:
                        # Get timestamp from trade
                        timestamp = trade.get('participant_timestamp') or trade.get('sip_timestamp')
                        if timestamp:
                            # Convert nanoseconds to datetime
                            trade_date = datetime.fromtimestamp(timestamp / 1e9).date()
                            # Include only trades on or after min_date
                            if trade_date >= min_date_obj:
                                filtered_trades.append(trade)
                    
                    trades = filtered_trades
                    print(f"Filtered to {len(trades)} trades after {min_date}")
                except Exception as e:
                    print(f"Error filtering trades by date: {e}")
            
            # Skip if no trades after filtering
            if not trades:
                print(f"No trades found after {min_date} for {option_symbol}")
                return {}
                
            # Look for a significant trade (by size)
            significant_trade = None
            for trade in trades:
                size = trade.get('size', 0)
                if size >= min_size:
                    significant_trade = trade
                    print(f"Found significant trade with size {size} for {option_symbol}")
                    break
                    
            # If no significant trade found, use the most recent one
            if not significant_trade:
                significant_trade = trades[0]
                print(f"No significant trade found, using most recent one for {option_symbol}")
            
            # Get timestamp (prefer participant_timestamp for more accurate timing when available)
            timestamp = significant_trade.get('participant_timestamp') or significant_trade.get('sip_timestamp')
            exchange = significant_trade.get('exchange')
            
            if timestamp:
                # Format timestamp for display and store exact time
                date_str = format_timestamp(timestamp)
                
                return {
                    'date': date_str,
                    'price': significant_trade.get('price'),
                    'size': significant_trade.get('size'),
                    'exchange': exchange,
                    'timestamp': timestamp,  # Store raw timestamp for sorting/precision
                    'timestamp_human': date_str  # Human readable version
                }
            
            # If we have a trade but no timestamp (unlikely), just return price and size
            return {
                'price': significant_trade.get('price'),
                'size': significant_trade.get('size'),
                'exchange': exchange
            }
        else:
            print(f"No trades found for {option_symbol}")
            
            # For future-dated options or those without trade history,
            # we return an empty dict which indicates the option exists
            # but we don't have historical trades
            return {}
    
    except Exception as e:
        print(f"Error getting option trade data for {option_symbol}: {str(e)}")
        # Print traceback for debugging
        import traceback
        traceback.print_exc()
    
    return None