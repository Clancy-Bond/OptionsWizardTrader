"""
Test script to debug how the Discord bot parses messages and handles stop loss requests
"""
import re
from datetime import datetime, timedelta
import sys
import yfinance as yf

# Import the option calculator functions
from option_calculator import get_option_chain, get_option_greeks, calculate_option_at_stop_loss

def debug_message_parsing(query):
    """
    Debug how the Discord bot parses and processes a specific query
    """
    print(f"\n===== Debugging Message: '{query}' =====")
    
    # This is a simplified version of the OptionsBotNLP.parse_query method
    # Define regex patterns - let's improve these based on the exact query format
    ticker_pattern = r'\b(?:for|my)?\s*([A-Z]{1,5})\b'  # Ticker pattern that works with various formats
    option_type_pattern = r'\b(call|put|calls|puts)\b'
    
    # Modified strike price pattern to account for dollar signs
    strike_pattern = r'\$?(\d+(?:\.\d+)?)'
    
    # More comprehensive expiration date pattern to match various formats
    expiration_pattern = r'(?:expir(?:ing|e|es|ation)?(?:\s+(?:on|at|in))?\s+)?((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?(?:\s+\d{4})?)'
    
    # Pattern for number of contracts
    contracts_pattern = r'(\d+)\s*(?:contract|contracts)'
    
    # Extract data with regex
    print("Extracting information from query...")
    
    # Find the ticker symbol
    ticker_match = re.search(ticker_pattern, query.upper())
    ticker = ticker_match.group(1) if ticker_match else None
    print(f"Ticker: {ticker}")
    
    # Find the option type
    option_type_match = re.search(option_type_pattern, query.lower())
    option_type = option_type_match.group(1) if option_type_match else None
    if option_type in ['calls', 'puts']:
        option_type = option_type[:-1]  # Convert 'calls' to 'call', 'puts' to 'put'
    print(f"Option type: {option_type}")
    
    # Find the strike price
    strike_match = re.search(strike_pattern, query)
    strike = None
    if strike_match:
        strike = strike_match.group(1)
        strike = float(strike)
    print(f"Strike price: {strike}")
    
    # Find expiration date
    expiration_match = re.search(expiration_pattern, query, re.IGNORECASE)
    expiration = None
    expiration_date_obj = None
    
    if expiration_match:
        expiration_raw = expiration_match.group(1)
        print(f"Raw expiration: {expiration_raw}")
        
        # Try to parse the date string into a standard format
        try:
            # If already in YYYY-MM-DD format
            if re.match(r'\d{4}-\d{2}-\d{2}', expiration_raw):
                expiration = expiration_raw
                expiration_date_obj = datetime.strptime(expiration, '%Y-%m-%d')
            else:
                # Try various date formats
                date_formats = [
                    '%b %d %Y',     # Apr 15 2025
                    '%B %d %Y',     # April 15 2025
                    '%b %dst %Y',   # Apr 1st 2025
                    '%b %dnd %Y',   # Apr 2nd 2025
                    '%b %drd %Y',   # Apr 3rd 2025
                    '%b %dth %Y',   # Apr 4th 2025
                    '%B %dst %Y',   # April 1st 2025
                    '%B %dnd %Y',   # April 2nd 2025
                    '%B %drd %Y',   # April 3rd 2025
                    '%B %dth %Y',   # April 4th 2025
                    '%d %b %Y',     # 15 Apr 2025
                    '%d %B %Y',     # 15 April 2025
                    '%dst %b %Y',   # 1st Apr 2025
                    '%dnd %b %Y',   # 2nd Apr 2025
                    '%drd %b %Y',   # 3rd Apr 2025
                    '%dth %b %Y',   # 4th Apr 2025
                    '%dst %B %Y',   # 1st April 2025
                    '%dnd %B %Y',   # 2nd April 2025
                    '%drd %B %Y',   # 3rd April 2025
                    '%dth %B %Y',   # 4th April 2025
                ]
                
                # If no year specified, add current year
                if re.search(r'\d{4}', expiration_raw) is None:
                    # Add current year to the string
                    current_year = datetime.now().year
                    expiration_raw = f"{expiration_raw} {current_year}"
                    print(f"Added year: {expiration_raw}")
                    
                    # Update date formats to try
                    date_formats = [
                        '%b %d %Y',     # Apr 15 2025
                        '%B %d %Y',     # April 15 2025
                        '%b %dst %Y',   # Apr 1st 2025
                        '%b %dnd %Y',   # Apr 2nd 2025
                        '%b %drd %Y',   # Apr 3rd 2025
                        '%b %dth %Y',   # Apr 4th 2025
                        '%B %dst %Y',   # April 1st 2025
                        '%B %dnd %Y',   # April 2nd 2025
                        '%B %drd %Y',   # April 3rd 2025
                        '%B %dth %Y',   # April 4th 2025
                    ]
                
                # Try each format
                for fmt in date_formats:
                    try:
                        expiration_date_obj = datetime.strptime(expiration_raw, fmt)
                        print(f"Matched format: {fmt}")
                        break
                    except ValueError:
                        continue
        except Exception as e:
            print(f"Error parsing date: {str(e)}")
        
        if expiration_date_obj:
            expiration = expiration_date_obj.strftime('%Y-%m-%d')
    
    print(f"Parsed expiration date: {expiration}")
    
    # Find number of contracts
    contracts_match = re.search(contracts_pattern, query)
    num_contracts = int(contracts_match.group(1)) if contracts_match else 1
    print(f"Number of contracts: {num_contracts}")
    
    # Check if we have all the necessary information for a stop loss request
    if all([ticker, option_type, strike, expiration]):
        print("\nAll required information is available! Let's process the stop loss request.")
        
        try:
            # Get the ticker data
            ticker_obj = yf.Ticker(ticker)
            
            # Check if the expiration date is available
            if expiration not in ticker_obj.options:
                print(f"WARNING: Expiration date {expiration} not in available options!")
                print(f"Available expirations: {ticker_obj.options}")
                
                # Find closest expiration date
                if ticker_obj.options:
                    closest_date = min(ticker_obj.options, key=lambda x: abs((datetime.strptime(x, '%Y-%m-%d') - expiration_date_obj).days))
                    print(f"Closest available expiration: {closest_date}")
                    expiration = closest_date
                else:
                    print("No available expiration dates.")
                    return
            
            # Get option chain
            print(f"Getting option chain for {ticker} {option_type} expiring {expiration}")
            try:
                option_chain = get_option_chain(ticker_obj, expiration, option_type)
                if option_chain is None or option_chain.empty:
                    print(f"No option chain available for {ticker} {option_type} expiring {expiration}")
                    return
                
                # Check if the strike price exists
                available_strikes = option_chain['strike'].unique().tolist()
                print(f"Available strikes: {sorted(available_strikes)}")
                
                if strike not in available_strikes:
                    print(f"WARNING: Strike price ${strike} not in available strikes!")
                    closest_strike = min(available_strikes, key=lambda x: abs(x - strike))
                    print(f"Closest available strike: ${closest_strike}")
                    strike = closest_strike
                
                # Get current stock price
                current_price = ticker_obj.history(period='1d')['Close'].iloc[-1]
                print(f"Current stock price: ${current_price:.2f}")
                
                # Get current option price
                option_data = option_chain[option_chain['strike'] == strike]
                current_option_price = option_data['lastPrice'].iloc[0] if not option_data.empty else None
                print(f"Current option price: ${current_option_price:.2f}" if current_option_price else "Option price data not available")
                
                # Try to get option Greeks
                try:
                    greeks = get_option_greeks(ticker_obj, expiration, strike, option_type)
                    print(f"Option Greeks: {greeks}")
                    
                    # Calculate what the option would be worth at a stop loss level (10% below current price for example)
                    stop_loss_price = current_price * 0.9 if option_type == 'call' else current_price * 1.1
                    print(f"Example stop loss price: ${stop_loss_price:.2f}")
                    
                    stop_loss_option = calculate_option_at_stop_loss(
                        current_price, stop_loss_price, strike, current_option_price, expiration, option_type
                    )
                    
                    print(f"Option price at stop loss: ${stop_loss_option['price']:.2f}")
                    print(f"Percent change: {stop_loss_option['percent_change']:.2f}%")
                except Exception as e:
                    print(f"Error calculating Greeks or stop loss: {str(e)}")
            except Exception as e:
                print(f"Error retrieving option chain: {str(e)}")
        except Exception as e:
            print(f"Error processing ticker data: {str(e)}")
    else:
        print("\nMissing required information for stop loss request:")
        if not ticker:
            print("- No ticker symbol found")
        if not option_type:
            print("- No option type (call/put) found")
        if not strike:
            print("- No strike price found")
        if not expiration:
            print("- No expiration date found")
    
    print("\n===== Debug Complete =====")

def main():
    """
    Main function to test different message formats
    """
    # Test the exact query format that's failing
    test_query = "Recommend stop loss for TSLA $270 calls expiring Apr 4th 2025"
    debug_message_parsing(test_query)
    
    # Try alternative formats as well
    debug_message_parsing("What's a good stop loss for my AAPL $190 calls expiring April 11?")
    
    # Test with user-provided query if any
    if len(sys.argv) > 1:
        debug_message_parsing(sys.argv[1])

if __name__ == "__main__":
    main()