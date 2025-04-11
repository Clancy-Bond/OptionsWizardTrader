"""
Debugging script to investigate why the specific query about TSLA stop loss is failing.
This script will trace through each step of the process to identify the failure point.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
from option_calculator import get_option_greeks, handle_expiration_date_validation
from technical_analysis import get_stop_loss_recommendation
from discord_bot import OptionsBotNLP 

def debug_stop_loss_request():
    """Debug the specific query that's failing: TSLA $270 calls expiring Apr 4th 2025"""
    print("=" * 50)
    print("DEBUGGING TSLA STOP LOSS REQUEST")
    print("=" * 50)
    
    # 1. Parse the query using our NLP processor
    nlp = OptionsBotNLP()
    query = "Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025"
    print(f"Query: {query}")
    
    info = nlp.extract_info(query)
    print(f"\nExtracted Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 2. Check if the required fields are extracted correctly
    required_fields = ['ticker', 'strike', 'option_type', 'expiration']
    missing_fields = [field for field in required_fields if not info.get(field)]
    
    if missing_fields:
        print(f"\n⚠️ Missing required fields: {', '.join(missing_fields)}")
        for field in missing_fields:
            print(f"  - {field} is missing or None")
    else:
        print("\n✅ All required fields extracted successfully")
    
    # 3. Try to get the stock data
    print("\nAttempting to fetch stock data...")
    try:
        ticker_obj = yf.Ticker(info['ticker'])
        current_price = ticker_obj.history(period="1d")['Close'].iloc[-1]
        print(f"✅ Successfully fetched stock data. Current price: ${current_price:.2f}")
    except Exception as e:
        print(f"❌ Error fetching stock data: {str(e)}")
        return
    
    # 4. Validate the expiration date
    if info['expiration']:
        print(f"\nValidating expiration date: {info['expiration']}")
        try:
            valid_expiration, warning = handle_expiration_date_validation(info['expiration'], ticker_obj)
            if warning:
                print(f"⚠️ Expiration date warning: {warning}")
            else:
                print(f"✅ Expiration date is valid: {valid_expiration}")
                
            # Check available expirations for reference
            available_expirations = ticker_obj.options
            print(f"\nAvailable expiration dates:")
            for i, exp in enumerate(available_expirations[:10]):  # Show first 10
                print(f"  {exp}")
            if len(available_expirations) > 10:
                print(f"  ... and {len(available_expirations) - 10} more")
        except Exception as e:
            print(f"❌ Error validating expiration date: {str(e)}")
    else:
        print("❌ No expiration date to validate")
    
    # 5. Check if the option chain for that expiration exists and if the strike price is available
    if info['expiration'] and info['strike'] and info['option_type']:
        print(f"\nChecking option chain for {info['expiration']}...")
        try:
            # Get valid expiration date (or closest available)
            valid_expiration, _ = handle_expiration_date_validation(info['expiration'], ticker_obj)
            
            if valid_expiration:
                # Get the option chain
                option_type = 'calls' if info['option_type'] == 'call' else 'puts'
                chain = ticker_obj.option_chain(valid_expiration)
                options_data = getattr(chain, option_type)
                
                print(f"✅ Successfully fetched option chain with {len(options_data)} {option_type}")
                
                # Check if strike price exists
                available_strikes = options_data['strike'].tolist()
                print(f"\nChecking if strike price ${info['strike']} exists in available strikes:")
                
                # Find the closest strike prices
                closest_strikes = sorted(available_strikes, key=lambda x: abs(x - info['strike']))[:5]
                print(f"  Closest available strikes: {', '.join(['$' + str(s) for s in closest_strikes])}")
                
                if info['strike'] in available_strikes:
                    print(f"✅ Strike price ${info['strike']} is available")
                    
                    # Try to get option data for this specific strike
                    option_row = options_data[options_data['strike'] == info['strike']]
                    if not option_row.empty:
                        option_price = option_row['lastPrice'].iloc[0]
                        print(f"✅ Option price: ${option_price:.2f}")
                        
                        # Try to calculate Greeks
                        try:
                            greeks = get_option_greeks(ticker_obj, valid_expiration, info['strike'], info['option_type'])
                            print(f"✅ Successfully calculated Greeks: {greeks}")
                        except Exception as e:
                            print(f"❌ Error calculating Greeks: {str(e)}")
                        
                        # Try to get stop loss recommendation
                        try:
                            stop_loss = get_stop_loss_recommendation(ticker_obj, current_price, info['option_type'], valid_expiration)
                            print(f"✅ Successfully calculated stop loss recommendation")
                        except Exception as e:
                            print(f"❌ Error calculating stop loss: {str(e)}")
                            import traceback
                            print(traceback.format_exc())
                    else:
                        print(f"❌ Strike price ${info['strike']} is in the list of available strikes, but couldn't fetch option data")
                else:
                    print(f"❌ Strike price ${info['strike']} is not available")
            else:
                print(f"❌ No valid expiration date available")
        except Exception as e:
            print(f"❌ Error checking option chain: {str(e)}")
            import traceback
            print(traceback.format_exc())
    else:
        print("❌ Missing required option information")
    
    print("\n" + "=" * 50)
    print("DEBUG SUMMARY")
    print("=" * 50)
    
    # Summarize the findings
    if missing_fields:
        print("1. NLP extraction issue: Failed to extract all required fields")
    elif not info['expiration']:
        print("2. Date parsing issue: Failed to parse the expiration date format")
    else:
        print("3. YFinance API issue: The requested option data might not be available")
    
    print("\nRecommended fixes:")
    if "expiration" in missing_fields:
        print("- Improve date parsing patterns to better handle ordinal suffixes with year")
    elif info['expiration'] and not valid_expiration:
        print("- Enhance expiration date validation to better handle cases where the exact date isn't available")
    elif info['strike'] and info['strike'] not in available_strikes:
        print("- Improve strike price handling to use the closest available strike when the exact one isn't available")
    else:
        print("- Add better error handling for YFinance API limitations")

if __name__ == "__main__":
    debug_stop_loss_request()