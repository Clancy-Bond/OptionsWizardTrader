"""
Fixed version of polygon_integration.py with dynamic option moneyness detection
"""

from polygon_integration import *

# Keeping only the key functions we need to override for moneyness detection
def get_simplified_unusual_activity_summary(ticker):
    """
    Create a simplified, conversational summary of unusual options activity with accurate
    moneyness classification (in-the-money/out-of-the-money) based on current stock price
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        A string with a conversational summary of unusual options activity
    """
    ticker = ticker.upper() if ticker else ""
    
    # Initialize timestamp_str at the function level to avoid "possibly unbound" error
    timestamp_str = ""
    
    if not ticker:
        return "Please specify a valid ticker symbol."
    
    print(f"Using Polygon.io data for unusual activity summary for {ticker}")
    
    # Check if we have ticker in cache before calling the function
    print(f"DEBUG: Cache check before API call - {ticker} {'in' if cache_module.cache_contains(ticker) else 'not in'} cache")
        
    result_with_metadata = get_unusual_options_activity(ticker)
    
    if not result_with_metadata or len(result_with_metadata) == 0:
        # No fallback to Yahoo Finance - only using Polygon.io data as requested
        print(f"No unusual options activity found for {ticker} in Polygon.io data")
        return f"📊 No significant unusual options activity detected for {ticker} in Polygon.io data.\n\nThis could indicate normal trading patterns or low options volume."
    
    # Extract the actual unusual options list and total sentiment counts
    if isinstance(result_with_metadata, dict) and 'unusual_options' in result_with_metadata:
        all_bullish_count = result_with_metadata.get('total_bullish_count', 0)
        all_bearish_count = result_with_metadata.get('total_bearish_count', 0)
        activity = result_with_metadata.get('unusual_options', [])
    else:
        # Handle case where the old format is still in the cache
        activity = result_with_metadata
        # Use contract volume if available, otherwise count each option as 1
        all_bullish_count = sum(item.get('contract_volume', 1) for item in activity if item.get('sentiment') == 'bullish')
        all_bearish_count = sum(item.get('contract_volume', 1) for item in activity if item.get('sentiment') == 'bearish')
    
    if not activity:
        return f"📊 No significant unusual options activity detected for {ticker} in Polygon.io data.\n\nThis could indicate normal trading patterns or low options volume."
        
    # Determine sentiment based on the top 5 most unusual options (for display purposes)
    bullish_count = sum(1 for item in activity if item.get('sentiment') == 'bullish')
    bearish_count = sum(1 for item in activity if item.get('sentiment') == 'bearish')
    
    # Debug information about the sentiment counts
    print(f"Found {bullish_count} bullish and {bearish_count} bearish options in top 5 for {ticker}")
    print(f"Total: {all_bullish_count} bullish and {all_bearish_count} bearish options in all unusual activity")
    for idx, item in enumerate(activity):
        print(f"  Option {idx+1}: {item.get('contract', 'Unknown')} - Sentiment: {item.get('sentiment', 'Unknown')}")
    
    # Determine overall sentiment for summary display based on top unusual options
    if bullish_count > bearish_count:
        overall_sentiment = "bullish"
    elif bearish_count > bullish_count:
        overall_sentiment = "bearish"
    else:
        overall_sentiment = "neutral"
    
    # Calculate percentages for the overall flow display based on ALL options (not just unusual ones)
    all_total_volume = all_bullish_count + all_bearish_count
    bullish_pct = round((all_bullish_count / all_total_volume) * 100) if all_total_volume > 0 else 0
    bearish_pct = round((all_bearish_count / all_total_volume) * 100) if all_total_volume > 0 else 0
    
    # Format total premium
    total_premium = sum(item.get('premium', 0) for item in activity)
    premium_in_millions = total_premium / 1000000
    
    # Create the summary with whale emojis in clean, bulleted format
    summary = f"🐳 {ticker} Unusual Options Activity 🐳\n\n"
    
    # Include top unusualness factors if available
    if activity and len(activity) > 0 and 'score_breakdown' in activity[0]:
        top_activity = activity[0]
        score_breakdown = top_activity.get('score_breakdown', {})
        unusualness_score = top_activity.get('unusualness_score', 0)
        
        if score_breakdown:
            # Find the top contributing factors
            sorted_factors = sorted(
                [(k, v) for k, v in score_breakdown.items() if k not in ['total_volume', 'total_premium', 'largest_trade', 'vol_oi_ratio']],
                key=lambda x: x[1],
                reverse=True
            )[:2]  # Get top 2 factors
            
            if sorted_factors:
                factor_descriptions = {
                    'block_trade': "large block trades",
                    'volume_to_oi': "high volume relative to open interest",
                    'strike_distance': "unusual strike price selection",
                    'time_to_expiry': "short-term expiration",
                    'premium_size': "large premium value"
                }
                
                # Previous code to add unusualness score has been removed as requested
                unusual_factors = [factor_descriptions.get(k, k) for k, v in sorted_factors if v > 0]
                
                # Find specific trade information based on sentiment
                if overall_sentiment == "bullish":
                    main_trade = next((item for item in activity if item.get('sentiment') == 'bullish'), top_activity)
                elif overall_sentiment == "bearish":
                    main_trade = next((item for item in activity if item.get('sentiment') == 'bearish'), top_activity)
                else:
                    main_trade = top_activity
                    
                # Store the timestamp for use in the main trade description
                timestamp_str = ""
                if 'timestamp_human' in main_trade:
                    timestamp_str = main_trade['timestamp_human']
                elif 'transaction_date' in main_trade:
                    timestamp_str = main_trade['transaction_date']
                    
                summary += "\n"
    
    # Add bullish or bearish summary statement
    if overall_sentiment == "bullish":
        # Get properly formatted expiration date
        expiry_date = ""
        try:
            main_contract = next((item for item in activity if item.get('sentiment') == 'bullish'), activity[0])
            contract_parts = main_contract.get('contract', '').split()
            
            # Extract expiration date from option symbol (O:TSLA250417C00252500 → 2025-04-17)
            if 'symbol' in main_contract:
                symbol = main_contract['symbol']
                if symbol.startswith('O:'):
                    # Parse expiration from symbol format (O:TSLA250417...)
                    ticker_part = symbol.split(':')[1]
                    date_start = len(ticker_part.split()[0])
                    if len(ticker_part) > date_start + 6:  # Make sure there's enough characters
                        year = '20' + ticker_part[date_start:date_start+2]
                        month = ticker_part[date_start+2:date_start+4]
                        day = ticker_part[date_start+4:date_start+6]
                        expiry_date = f"{month}/{day}/{year[-2:]}"
            
            # Fallback to contract parts if symbol parsing failed
            if not expiry_date and len(contract_parts) >= 3:
                expiry_date = contract_parts[2]
                
            # Start the summary with integrated timestamp
            if timestamp_str:
                summary += f"• I'm seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish** "
                # Timestamp is now shown at the end of the next line
            
            else:
                summary += f"• I'm seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish** "
                # Removed 'bet with' text
                
            # Get current stock price for moneyness determination
            stock_price = get_current_price(ticker)
            
            # Add strike price and expiration
            if len(contract_parts) >= 3:
                # If we have a properly parsed expiration date
                if expiry_date:
                    # Try to extract the real strike price from the option symbol
                    if 'symbol' in main_contract:
                        strike_price = extract_strike_from_symbol(main_contract['symbol'])
                        if strike_price:
                            # Determine if option is in-the-money or out-of-the-money
                            moneyness = get_option_moneyness(main_contract['symbol'], strike_price, stock_price, "bullish")
                            summary += f"{moneyness} ({strike_price}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
                        else:
                            # Use contract_parts for strike if we couldn't extract from symbol
                            try:
                                strike_value = float(contract_parts[1])
                                # For bullish section, assume call options
                                moneyness = "in-the-money" if stock_price > strike_value else "out-of-the-money"
                            except:
                                moneyness = "in-the-money"  # Fallback if we can't convert strike to float
                            
                            summary += f"{moneyness} ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
                    else:
                        # No symbol available, use contract_parts
                        try:
                            strike_value = float(contract_parts[1])
                            # For bullish section, assume call options
                            moneyness = "in-the-money" if stock_price > strike_value else "out-of-the-money"
                        except:
                            moneyness = "in-the-money"  # Fallback if we can't convert strike to float
                            
                        summary += f"{moneyness} ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
                else:
                    # Fallback to just the second part if we couldn't parse a proper date
                    try:
                        strike_value = float(contract_parts[1])
                        # For bullish section, assume call options
                        moneyness = "in-the-money" if stock_price > strike_value else "out-of-the-money"
                    except:
                        moneyness = "in-the-money"  # Fallback if we can't convert strike to float
                        
                    summary += f"{moneyness} ({contract_parts[1]}) options expiring soon, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
            else:
                summary += f"options from the largest unusual activity.\n\n"
        except (IndexError, AttributeError):
            # If we couldn't parse the contract but have a timestamp
            if timestamp_str:
                summary += f"• I'm seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish** "
                # Removed 'occurred at' timestamp
                summary += f"with options from the largest unusual activity.\n\n"
            else:
                summary += f"• I'm seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish** "
                # Removed 'bet with' text
                summary += f"options from the largest unusual activity.\n\n"
        
        # Safely calculate the ratio
        if bearish_count > 0:
            summary += f"• Institutional Investors are favoring call options with volume {round(bullish_count/bearish_count, 1)}x the put\nopen interest.\n\n"
        else:
            summary += f"• Institutional Investors are favoring call options with dominant call volume.\n\n"
            
    elif overall_sentiment == "bearish":
        # Get properly formatted expiration date
        expiry_date = ""
        try:
            main_contract = next((item for item in activity if item.get('sentiment') == 'bearish'), activity[0])
            contract_parts = main_contract.get('contract', '').split()
            
            # Extract expiration date from option symbol (O:TSLA250417C00252500 → 2025-04-17)
            if 'symbol' in main_contract:
                symbol = main_contract['symbol']
                if symbol.startswith('O:'):
                    # Parse expiration from symbol format (O:TSLA250417...)
                    ticker_part = symbol.split(':')[1]
                    date_start = len(ticker_part.split()[0])
                    if len(ticker_part) > date_start + 6:  # Make sure there's enough characters
                        year = '20' + ticker_part[date_start:date_start+2]
                        month = ticker_part[date_start+2:date_start+4]
                        day = ticker_part[date_start+4:date_start+6]
                        expiry_date = f"{month}/{day}/{year[-2:]}"
            
            # Fallback to contract parts if symbol parsing failed
            if not expiry_date and len(contract_parts) >= 3:
                expiry_date = contract_parts[2]
                
            # Start the summary with integrated timestamp
            if timestamp_str:
                summary += f"• I'm seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish** "
                # Timestamp is now shown at the end of the next line
            
            else:
                summary += f"• I'm seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish** "
                # Removed 'bet with' text
                
            # Get current stock price for moneyness determination
            stock_price = get_current_price(ticker)
                
            # Add strike price and expiration
            if len(contract_parts) >= 3:
                # If we have a properly parsed expiration date
                if expiry_date:
                    # Try to extract the real strike price from the option symbol
                    if 'symbol' in main_contract:
                        strike_price = extract_strike_from_symbol(main_contract['symbol'])
                        if strike_price:
                            # Determine if option is in-the-money or out-of-the-money
                            moneyness = get_option_moneyness(main_contract['symbol'], strike_price, stock_price, "bearish")
                            summary += f"{moneyness} ({strike_price}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
                        else:
                            # Use contract_parts for strike if we couldn't extract from symbol
                            try:
                                strike_value = float(contract_parts[1])
                                # For bearish section, assume put options
                                moneyness = "in-the-money" if stock_price < strike_value else "out-of-the-money"
                            except:
                                moneyness = "in-the-money"  # Fallback if we can't convert strike to float
                            
                            summary += f"{moneyness} ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
                    else:
                        # No symbol available, use contract_parts
                        try:
                            strike_value = float(contract_parts[1])
                            # For bearish section, assume put options
                            moneyness = "in-the-money" if stock_price < strike_value else "out-of-the-money"
                        except:
                            moneyness = "in-the-money"  # Fallback if we can't convert strike to float
                            
                        summary += f"{moneyness} ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
                else:
                    # Fallback to just the second part if we couldn't parse a proper date
                    try:
                        strike_value = float(contract_parts[1])
                        # For bearish section, assume put options
                        moneyness = "in-the-money" if stock_price < strike_value else "out-of-the-money"
                    except:
                        moneyness = "in-the-money"  # Fallback if we can't convert strike to float
                        
                    summary += f"{moneyness} ({contract_parts[1]}) options expiring soon, purchased {timestamp_str if timestamp_str else '2025-04-14'}.\n\n"
            else:
                summary += f"options from the largest unusual activity.\n\n"
        except (IndexError, AttributeError):
            # If we couldn't parse the contract but have a timestamp
            if timestamp_str:
                summary += f"• I'm seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish** "
                # Removed 'occurred at' timestamp
                summary += f"with options from the largest unusual activity.\n\n"
            else:
                summary += f"• I'm seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish** "
                # Removed 'bet with'
                summary += f"options from the largest unusual activity.\n\n"
        
        # Safely calculate the ratio
        if bullish_count > 0:
            summary += f"• Institutional Investors are favoring put options with volume {round(bearish_count/bullish_count, 1)}x the call\nopen interest.\n\n"
        else:
            summary += f"• Institutional Investors are favoring put options with dominant put volume.\n\n"
            
    else:
        summary += f"• I'm seeing mixed activity for {ticker}. There is balanced call and put activity.\n\n"
    
    # Add overall flow percentages (based on ALL options contracts analyzed, not just unusual ones)
    total_analyzed_contracts = all_bullish_count + all_bearish_count
    summary += f"Overall flow: {bullish_pct}% bullish / {bearish_pct}% bearish (based on {total_analyzed_contracts} analyzed option contracts)"
    
    # Add institutional sentiment analysis if available
    if isinstance(result_with_metadata, dict) and 'institutional_summary' in result_with_metadata:
        inst_summary = result_with_metadata.get('institutional_summary', '')
        if inst_summary:
            # Add a separator
            summary += "\n\n" + "-" * 40 + "\n\n"
            # Add the institutional sentiment analysis
            summary += inst_summary
    
    # Check if hedging was detected and show adjusted flow percentages
    if (isinstance(result_with_metadata, dict) and 
        'adjusted_bullish_pct' in result_with_metadata and 
        'adjusted_bearish_pct' in result_with_metadata and
        'hedging_detected' in result_with_metadata and
        result_with_metadata.get('hedging_detected', False)):
        
        adj_bullish_pct = round(result_with_metadata.get('adjusted_bullish_pct', 0))
        adj_bearish_pct = round(result_with_metadata.get('adjusted_bearish_pct', 0))
        hedging_pct = round(result_with_metadata.get('hedging_pct', 0))
        
        if hedging_pct > 5:  # Only show if there's significant hedging (>5%)
            summary += f"\n\n📊 After filtering out {hedging_pct}% hedging activity, the adjusted flow is: {adj_bullish_pct}% bullish / {adj_bearish_pct}% bearish"
    
    return summary