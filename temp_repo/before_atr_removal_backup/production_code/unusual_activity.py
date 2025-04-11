import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import random
from dateutil.parser import parse

def get_unusual_options_activity(ticker):
    """
    Identify unusual options activity for a given ticker.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        List of unusual options activity with sentiment
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get all available expiration dates
        expirations = stock.options
        
        if not expirations:
            return []
        
        unusual_activity = []
        
        # Process recent expirations (limit to 3 to avoid too many API calls)
        for expiry in expirations[:3]:
            # Get option chains
            options = stock.option_chain(expiry)
            calls = options.calls
            puts = options.puts
            
            # Check for unusual volume in calls
            if not calls.empty:
                # Calculate volume to open interest ratio
                calls['volume_oi_ratio'] = calls['volume'] / calls['openInterest'].replace(0, 1)
                
                # Filter for unusual activity
                unusual_calls = calls[
                    (calls['volume'] > 100) &  # Minimum volume
                    (calls['volume_oi_ratio'] > 2)  # Volume is more than 2x open interest
                ].copy()
                
                if not unusual_calls.empty:
                    unusual_calls['sentiment'] = 'bullish'
                    unusual_calls['amount'] = unusual_calls['volume'] * unusual_calls['lastPrice'] * 100  # Contract size
                    
                    # Sort by amount (descending)
                    unusual_calls = unusual_calls.sort_values('amount', ascending=False)
                    
                    # Take top 2 unusual call activities
                    for _, row in unusual_calls.head(2).iterrows():
                        unusual_activity.append({
                            'expiry': expiry,
                            'strike': row['strike'],
                            'volume': row['volume'],
                            'open_interest': row['openInterest'],
                            'amount': row['amount'],
                            'volume_oi_ratio': row['volume_oi_ratio'],
                            'sentiment': 'bullish'
                        })
            
            # Check for unusual volume in puts
            if not puts.empty:
                # Calculate volume to open interest ratio
                puts['volume_oi_ratio'] = puts['volume'] / puts['openInterest'].replace(0, 1)
                
                # Filter for unusual activity
                unusual_puts = puts[
                    (puts['volume'] > 100) &  # Minimum volume
                    (puts['volume_oi_ratio'] > 2)  # Volume is more than 2x open interest
                ].copy()
                
                if not unusual_puts.empty:
                    unusual_puts['sentiment'] = 'bearish'
                    unusual_puts['amount'] = unusual_puts['volume'] * unusual_puts['lastPrice'] * 100  # Contract size
                    
                    # Sort by amount (descending)
                    unusual_puts = unusual_puts.sort_values('amount', ascending=False)
                    
                    # Take top 2 unusual put activities
                    for _, row in unusual_puts.head(2).iterrows():
                        unusual_activity.append({
                            'expiry': expiry,
                            'strike': row['strike'],
                            'volume': row['volume'],
                            'open_interest': row['openInterest'],
                            'amount': row['amount'],
                            'volume_oi_ratio': row['volume_oi_ratio'],
                            'sentiment': 'bearish'
                        })
        
        # If no unusual activity is found, check for highest volume options as an alternative
        if not unusual_activity:
            # Get the most active options
            for expiry in expirations[:2]:
                options = stock.option_chain(expiry)
                calls = options.calls
                puts = options.puts
                
                # Check calls
                if not calls.empty:
                    # Sort by volume (descending)
                    high_volume_calls = calls.sort_values('volume', ascending=False)
                    
                    # Take top high volume call
                    if high_volume_calls.iloc[0]['volume'] > 50:
                        row = high_volume_calls.iloc[0]
                        # Calculate volume to open interest ratio
                        volume_oi_ratio = row['volume'] / row['openInterest'] if row['openInterest'] > 0 else 1.0
                        unusual_activity.append({
                            'expiry': expiry,
                            'strike': row['strike'],
                            'volume': row['volume'],
                            'open_interest': row['openInterest'],
                            'amount': row['volume'] * row['lastPrice'] * 100,
                            'volume_oi_ratio': volume_oi_ratio,
                            'sentiment': 'bullish'
                        })
                
                # Check puts
                if not puts.empty:
                    # Sort by volume (descending)
                    high_volume_puts = puts.sort_values('volume', ascending=False)
                    
                    # Take top high volume put
                    if high_volume_puts.iloc[0]['volume'] > 50:
                        row = high_volume_puts.iloc[0]
                        # Calculate volume to open interest ratio
                        volume_oi_ratio = row['volume'] / row['openInterest'] if row['openInterest'] > 0 else 1.0
                        unusual_activity.append({
                            'expiry': expiry,
                            'strike': row['strike'],
                            'volume': row['volume'],
                            'open_interest': row['openInterest'],
                            'amount': row['volume'] * row['lastPrice'] * 100,
                            'volume_oi_ratio': volume_oi_ratio,
                            'sentiment': 'bearish'
                        })
        
        return unusual_activity
    except Exception as e:
        print(f"Error fetching unusual options activity: {str(e)}")
        return []

def get_simplified_unusual_activity_summary(ticker):
    """
    Create a simplified, conversational summary of unusual options activity.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        A string with a conversational summary of unusual options activity
    """
    try:
        stock = yf.Ticker(ticker)
        ticker_data = stock.history(period="1d")
        current_price = ticker_data['Close'].iloc[-1] if not ticker_data.empty else 0
        
        # Get unusual options activity
        unusual_activity = get_unusual_options_activity(ticker)
        
        if not unusual_activity:
            return f"I'm not seeing any unusual options activity for {ticker} right now."
        
        # Get stock info
        info = stock.info
        company_name = info.get('shortName', ticker)
        
        # Separate bullish and bearish activity
        bullish_activity = [a for a in unusual_activity if a['sentiment'] == 'bullish']
        bearish_activity = [a for a in unusual_activity if a['sentiment'] == 'bearish']
        
        # Find the biggest money flow
        all_activity = sorted(unusual_activity, key=lambda x: x['amount'], reverse=True)
        biggest_bet = all_activity[0] if all_activity else None
        
        # Determine overall sentiment
        bullish_amount = sum(a['amount'] for a in bullish_activity)
        bearish_amount = sum(a['amount'] for a in bearish_activity)
        
        overall_sentiment = ""
        if bullish_amount > bearish_amount * 1.5:
            overall_sentiment = "strongly bullish"
        elif bullish_amount > bearish_amount:
            overall_sentiment = "mildly bullish"
        elif bearish_amount > bullish_amount * 1.5:
            overall_sentiment = "strongly bearish"
        elif bearish_amount > bullish_amount:
            overall_sentiment = "mildly bearish"
        else:
            overall_sentiment = "neutral with mixed signals"
        
        # Create a conversational response
        response = f"📊 **{ticker} Unusual Options Activity** 📊\n\n"
        
        # Add creative elements based on sentiment
        traders = ["institutional investors", "large traders", "market makers", "big money players", "option whales"]
        bullish_phrases = ["betting on a rally", "expecting upside", "positioning for gains", "optimistic about growth"]
        bearish_phrases = ["hedging downside risk", "betting on a decline", "expecting weakness", "positioning defensively"]
        
        if biggest_bet:
            # Format the date
            expiry_date = parse(biggest_bet['expiry'])
            date_str = expiry_date.strftime("%B %d")
            
            # Format the dollar amount
            amount_millions = biggest_bet['amount'] / 1000000
            
            trader_type = random.choice(traders)
            action_phrase = random.choice(bullish_phrases if biggest_bet['sentiment'] == 'bullish' else bearish_phrases)
            
            response += f"I'm seeing {overall_sentiment} activity for {company_name}. "
            
            if amount_millions >= 1:
                response += f"The largest flow is a **${amount_millions:.1f} million {biggest_bet['sentiment']}** bet "
            else:
                amount_thousands = biggest_bet['amount'] / 1000
                response += f"The largest flow is a **${amount_thousands:.0f}K {biggest_bet['sentiment']}** bet "
            
            strike_vs_current = (biggest_bet['strike'] / current_price - 1) * 100
            strike_description = ""
            
            if biggest_bet['sentiment'] == 'bullish':
                if strike_vs_current > 10:
                    strike_description = f"far out-of-the-money (${biggest_bet['strike']:.2f}, about {abs(strike_vs_current):.0f}% above current price)"
                elif strike_vs_current > 0:
                    strike_description = f"out-of-the-money (${biggest_bet['strike']:.2f})"
                else:
                    strike_description = f"in-the-money (${biggest_bet['strike']:.2f})"
            else:  # bearish
                if strike_vs_current < -10:
                    strike_description = f"far out-of-the-money (${biggest_bet['strike']:.2f}, about {abs(strike_vs_current):.0f}% below current price)"
                elif strike_vs_current < 0:
                    strike_description = f"out-of-the-money (${biggest_bet['strike']:.2f})"
                else:
                    strike_description = f"in-the-money (${biggest_bet['strike']:.2f})"
            
            response += f"with {strike_description} options expiring on {date_str}.\n\n"
            
            # Add some color about what this might mean
            response += f"{trader_type.title()} are {action_phrase} "
            
            if biggest_bet['sentiment'] == 'bullish':
                response += f"with call options volume {biggest_bet['volume_oi_ratio']:.1f}x the open interest.\n\n"
            else:
                response += f"with put options volume {biggest_bet['volume_oi_ratio']:.1f}x the open interest.\n\n"
                
            # Add overall flow summary
            total_flow = bullish_amount + bearish_amount
            bullish_percentage = (bullish_amount / total_flow) * 100 if total_flow > 0 else 0
            bearish_percentage = (bearish_amount / total_flow) * 100 if total_flow > 0 else 0
            
            response += f"**Overall flow:** {bullish_percentage:.0f}% bullish / {bearish_percentage:.0f}% bearish"
            
        else:
            response += f"I don't see any significant unusual options activity for {company_name} right now."
            
        return response
        
    except Exception as e:
        print(f"Error generating simplified unusual activity summary: {str(e)}")
        return f"I couldn't analyze unusual options activity for {ticker} right now. There might be an issue with the data source."
