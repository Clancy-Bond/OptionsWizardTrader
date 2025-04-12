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
        List of unusual options activity with sentiment, or empty list if Polygon.io API key is not available
    """
    # Only proceed if Polygon API key is available
    if not os.getenv('POLYGON_API_KEY'):
        print(f"No Polygon API key available for getting unusual options activity")
        return []
        
    try:
        # Use polygon integration to get unusual activity
        unusual_activity_data = polygon.get_unusual_options_activity(ticker)
        
        # If we got data from polygon, return it
        if unusual_activity_data:
            print(f"Retrieved unusual activity data from Polygon for {ticker}")
            return unusual_activity_data
            
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

def detect_unusual_options_flow(options_data):
    """
    Analyze options data to detect unusual flow patterns
    
    Args:
        options_data (DataFrame): Options chain data
    
    Returns:
        dict: Unusual activity indicators
    """
    # Skip rows with zero open interest to avoid division by zero
    valid_data = options_data[options_data['openInterest'] > 0].copy()
    
    if valid_data.empty:
        return {
            'unusual_detected': False,
            'activity_level': 'None',
            'volume_oi_ratio': 0,
            'sentiment': 'Neutral',
            'large_trades': []
        }
    
    # Calculate volume to open interest ratio
    valid_data['volume_oi_ratio'] = valid_data['volume'] / valid_data['openInterest']
    
    # Find strikes with unusual volume
    unusual_threshold = 3.0  # Volume at least 3x open interest
    unusual_strikes = valid_data[valid_data['volume_oi_ratio'] >= unusual_threshold]
    
    # Determine if there's unusual activity
    if unusual_strikes.empty or unusual_strikes['volume'].sum() < 100:
        return {
            'unusual_detected': False,
            'activity_level': 'Low',
            'volume_oi_ratio': valid_data['volume_oi_ratio'].mean(),
            'sentiment': 'Neutral',
            'large_trades': []
        }
    
    # Calculate highest volume/OI ratio
    max_vol_oi = unusual_strikes['volume_oi_ratio'].max()
    
    # Determine activity level
    activity_level = 'Moderate'
    if max_vol_oi >= 10.0:
        activity_level = 'High'
    if max_vol_oi >= 20.0:
        activity_level = 'Very High'
    
    # Determine sentiment
    # Check if unusual strikes are mostly ITM or OTM
    current_price = options_data['lastPrice'].iloc[0]  # Approximate current price
    
    # For calls, ITM if strike < price. For puts, ITM if strike > price
    # Determine if the options are calls or puts based on contractSymbol
    sample_symbol = options_data['contractSymbol'].iloc[0]
    is_call = 'C' in sample_symbol
    
    if is_call:
        itm_strikes = unusual_strikes[unusual_strikes['strike'] < current_price]
        otm_strikes = unusual_strikes[unusual_strikes['strike'] >= current_price]
    else:
        itm_strikes = unusual_strikes[unusual_strikes['strike'] > current_price]
        otm_strikes = unusual_strikes[unusual_strikes['strike'] <= current_price]
    
    itm_volume = itm_strikes['volume'].sum() if not itm_strikes.empty else 0
    otm_volume = otm_strikes['volume'].sum() if not otm_strikes.empty else 0
    
    if is_call:
        if otm_volume > itm_volume * 2:
            sentiment = 'Strongly Bullish'
        elif otm_volume > itm_volume:
            sentiment = 'Bullish'
        elif itm_volume > otm_volume * 2:
            sentiment = 'Cautiously Bullish'
        else:
            sentiment = 'Slightly Bullish'
    else:
        if otm_volume > itm_volume * 2:
            sentiment = 'Strongly Bearish'
        elif otm_volume > itm_volume:
            sentiment = 'Bearish'
        elif itm_volume > otm_volume * 2:
            sentiment = 'Cautiously Bearish'
        else:
            sentiment = 'Slightly Bearish'
    
    # Identify largest trades
    # Sort by volume to identify the largest trades
    top_trades = unusual_strikes.nlargest(3, 'volume')
    large_trades = []
    
    for _, trade in top_trades.iterrows():
        strike = trade['strike']
        expiry = trade['contractSymbol'].split(options_data['contractSymbol'].iloc[0].split('C')[0])[-1]
        volume = trade['volume']
        open_interest = trade['openInterest']
        
        trade_str = f"Strike: ${strike:.2f}, Exp: {expiry}, Vol: {volume} ({volume/open_interest:.1f}x OI)"
        large_trades.append(trade_str)
    
    return {
        'unusual_detected': True,
        'activity_level': activity_level,
        'volume_oi_ratio': max_vol_oi,
        'sentiment': sentiment,
        'large_trades': large_trades
    }