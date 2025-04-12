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

def get_option_trade_data(option_symbol, min_size=5):
    """
    Get the most recent significant trade for a specific option contract
    
    Args:
        option_symbol: Option symbol in Polygon format (O:AAPL250417C00100000)
        min_size: Minimum trade size to consider significant
        
    Returns:
        Dictionary with trade data including date, price, and size
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
        
        if not trades:
            return None
            
        # Look for a significant trade (by size)
        significant_trade = None
        for trade in trades:
            size = trade.get('size', 0)
            if size >= min_size:
                significant_trade = trade
                break
                
        # If no significant trade found, use the most recent one
        if not significant_trade and trades:
            significant_trade = trades[0]
            
        if significant_trade:
            # Get timestamp (prefer participant_timestamp if available)
            timestamp = significant_trade.get('participant_timestamp') or significant_trade.get('sip_timestamp')
            
            if timestamp:
                # Convert nanoseconds to seconds and then to datetime
                trade_date = datetime.fromtimestamp(timestamp / 1e9)
                date_str = trade_date.strftime("%m/%d/%y")
                
                return {
                    'date': date_str,
                    'price': significant_trade.get('price'),
                    'size': significant_trade.get('size')
                }
    
    except Exception as e:
        print(f"Error getting option trade data for {option_symbol}: {str(e)}")
        # Print traceback for debugging
        import traceback
        traceback.print_exc()
    
    return None