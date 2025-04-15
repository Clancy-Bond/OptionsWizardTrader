import random  # For generating demo data only
import datetime
import os
from dateutil.parser import parse
import polygon_integration as polygon
from polygon_trades import get_option_trade_data

def detect_unusual_activity(ticker, option_type):
    """
    Detect unusual options activity for a given ticker and option type
    using only Polygon.io data
    
    Args:
        ticker (str): The ticker symbol
        option_type (str): 'call' or 'put'
    
    Returns:
        dict: Information about unusual options activity
    """
    # Initialize response
    response = {
        'ticker': ticker,
        'option_type': option_type,
        'unusual_activity_detected': False
    }
    
    # Only proceed if Polygon API key is available
    if not os.getenv('POLYGON_API_KEY'):
        return {
            **response,
            'error': "Polygon.io API key is not available. Please provide a valid API key to view unusual options activity."
        }
    
    # Get option chain data
    try:
        # Retrieve unusual options activity from Polygon via our integration module
        unusual_activity_data = polygon.get_unusual_options_activity(ticker)
        
        # Filter for specific option type if requested
        if unusual_activity_data:
            filtered_activity = []
            for item in unusual_activity_data:
                # Check if this is the requested option type
                if option_type.lower() == 'call' and item.get('sentiment') == 'bullish':
                    filtered_activity.append(item)
                elif option_type.lower() == 'put' and item.get('sentiment') == 'bearish':
                    filtered_activity.append(item)
            
            if filtered_activity:
                # We have unusual activity for the requested option type
                max_premium_item = max(filtered_activity, key=lambda x: x.get('premium', 0))
                
                response.update({
                    'unusual_activity_detected': True,
                    'activity_level': 'High' if max_premium_item.get('premium', 0) > 1000000 else 'Moderate',
                    'volume': max_premium_item.get('volume', 0),
                    'premium': max_premium_item.get('premium', 0),
                    'sentiment': 'Bullish' if option_type.lower() == 'call' else 'Bearish',
                    'contract': max_premium_item.get('contract', '')
                })
                
                # Add transaction date if available
                if 'transaction_date' in max_premium_item:
                    response['transaction_date'] = max_premium_item['transaction_date']
                
                return response
        
        # If we get here, no unusual activity was found for the requested option type
        return {
            **response,
            'message': f"No unusual {option_type} options activity detected for {ticker} in Polygon.io data."
        }
        
    except Exception as e:
        return {
            **response,
            'error': f"Error analyzing options activity: {str(e)}"
        }

def get_unusual_options_activity(ticker):
    """
    Identify unusual options activity for a given ticker using only Polygon.io data.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Data structure with unusual options information and overall market sentiment counts,
        or empty list if Polygon.io API key is not available
    """
    # Only proceed if Polygon API key is available
    if not os.getenv('POLYGON_API_KEY'):
        print(f"No Polygon API key available for getting unusual options activity")
        return []
        
    try:
        # Use polygon integration to get unusual activity
        result_with_metadata = polygon.get_unusual_options_activity(ticker)
        
        # If we got data from polygon, return it
        if result_with_metadata:
            print(f"Retrieved unusual activity data from Polygon for {ticker}")
            
            # Handle both new format (with metadata) and old format
            if isinstance(result_with_metadata, dict) and 'unusual_options' in result_with_metadata:
                options_count = len(result_with_metadata.get('unusual_options', []))
                bullish = result_with_metadata.get('total_bullish_count', 0)
                bearish = result_with_metadata.get('total_bearish_count', 0)
                print(f"Found {options_count} unusual options with {bullish} bullish and {bearish} bearish overall")
            else:
                print(f"Found {len(result_with_metadata)} unusual options in legacy format")
                
            return result_with_metadata
            
        # If polygon returned empty data, return empty list
        return []
        
    except Exception as e:
        print(f"Error fetching unusual options activity from Polygon: {str(e)}")
        return []

def get_simplified_unusual_activity_summary(ticker):
    """
    Create a simplified, conversational summary of unusual options activity.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        A string with a conversational summary of unusual options activity
    """
    # Only use Polygon.io API as requested
    if os.getenv('POLYGON_API_KEY'):
        try:
            polygon_summary = polygon.get_simplified_unusual_activity_summary(ticker)
            if polygon_summary and len(polygon_summary) > 20:  # Check for a valid response
                print(f"Using Polygon.io data for unusual activity summary for {ticker}")
                return polygon_summary
            else:
                return f"📊 No significant unusual options activity detected for {ticker} in Polygon.io data.\n\nThis could indicate normal trading patterns or low options volume."
        except Exception as e:
            print(f"Error with Polygon unusual activity summary: {str(e)}")
            return f"📊 Unable to retrieve unusual options activity for {ticker} from Polygon.io.\n\nError: {str(e)}"
    else:
        return f"📊 Polygon.io API key is not available. Please provide a valid API key to view unusual options activity."

def detect_unusual_options_flow(option_symbols):
    """
    This function is kept for backward compatibility with any code that might call it,
    but now it simply returns a message indicating we're now using Polygon.io's API
    for unusual options activity detection.
    
    Args:
        option_symbols: List of option symbols or options data (not used)
    
    Returns:
        dict: A message indicating we now use Polygon.io
    """
    return {
        'unusual_detected': False,
        'activity_level': 'None',
        'volume_oi_ratio': 0,
        'sentiment': 'Neutral',
        'large_trades': [],
        'message': 'This function is deprecated. The system now uses Polygon.io API exclusively for unusual options activity detection.'
    }