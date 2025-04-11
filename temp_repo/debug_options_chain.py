"""
Debug script to investigate why the bot is having issues with options data
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
import sys

def debug_stop_loss_query(ticker_symbol, strike_price, option_type, expiration_date):
    """
    Debug the specific query that's failing in the Discord bot
    """
    print(f"\n===== Debugging Options Chain for {ticker_symbol} {option_type.upper()} ${strike_price} expiring {expiration_date} =====")
    
    try:
        # Get the ticker object
        print(f"Creating ticker object for {ticker_symbol}...")
        ticker = yf.Ticker(ticker_symbol)
        
        # Print available expirations
        print(f"Available expirations for {ticker_symbol}: {ticker.options}")
        
        if expiration_date not in ticker.options:
            print(f"WARNING: Expiration date {expiration_date} not in available options!")
            # Find closest expiration date
            date_obj = datetime.strptime(expiration_date, '%Y-%m-%d')
            closest_date = None
            closest_diff = float('inf')
            
            for exp in ticker.options:
                exp_obj = datetime.strptime(exp, '%Y-%m-%d')
                diff = abs((exp_obj - date_obj).days)
                if diff < closest_diff:
                    closest_diff = diff
                    closest_date = exp
            
            print(f"Closest available expiration: {closest_date} ({closest_diff} days different)")
            print(f"Updating expiration_date to {closest_date}")
            expiration_date = closest_date
        
        # Try to get the option chain
        print(f"Retrieving option chain for {expiration_date}...")
        try:
            options = ticker.option_chain(expiration_date)
            
            if option_type.lower() == 'call':
                chain = options.calls
                print(f"Successfully retrieved call options chain: {len(chain)} options")
            else:
                chain = options.puts
                print(f"Successfully retrieved put options chain: {len(chain)} options")
            
            # Check if the strike price exists
            strike_prices = sorted(chain['strike'].unique().tolist())
            print(f"Available strike prices: {strike_prices}")
            
            if strike_price not in strike_prices:
                print(f"WARNING: Strike price ${strike_price} not in available strikes!")
                # Find closest strike price
                closest_strike = min(strike_prices, key=lambda x: abs(x - strike_price))
                print(f"Closest available strike: ${closest_strike}")
                print(f"Updating strike_price to {closest_strike}")
                strike_price = closest_strike
            
            # Get the specific option
            option_data = chain[chain['strike'] == strike_price]
            print(f"Found option data: {not option_data.empty}")
            if not option_data.empty:
                print("\nOption details:")
                print(option_data[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']].to_string())
                
                # Try to calculate other values based on this data
                current_price = ticker.history(period='1d')['Close'].iloc[-1]
                print(f"\nCurrent stock price: ${current_price:.2f}")
                
                # Extract option price and IV
                current_option_price = option_data['lastPrice'].iloc[0]
                iv = option_data['impliedVolatility'].iloc[0]
                
                print(f"Current option price: ${current_option_price:.2f}")
                print(f"Implied volatility: {iv*100:.2f}%")
            else:
                print(f"ERROR: Could not find option with strike ${strike_price}")
        except Exception as option_error:
            print(f"ERROR retrieving option chain: {str(option_error)}")
            # Try with a different approach
            print("Attempting alternative approach...")
            
            # See if we can access any option data at all
            try:
                all_calls = []
                all_puts = []
                for exp in ticker.options[:3]:  # Try first few expirations
                    try:
                        opt = ticker.option_chain(exp)
                        all_calls.append(len(opt.calls))
                        all_puts.append(len(opt.puts))
                        print(f"  • Successfully retrieved {len(opt.calls)} calls and {len(opt.puts)} puts for {exp}")
                    except Exception as e:
                        print(f"  • Failed to retrieve options for {exp}: {str(e)}")
                
                if all_calls or all_puts:
                    print(f"Some option data is available. Retrieved {sum(all_calls)} calls and {sum(all_puts)} puts total.")
                else:
                    print("Could not retrieve any option data.")
            except Exception as alt_error:
                print(f"Alternative approach failed: {str(alt_error)}")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    
    print("\n===== Debug Complete =====")

def main():
    """
    Main debug function
    """
    # TSLA $270 calls expiring Apr 4th 2025
    debug_stop_loss_query('TSLA', 270.0, 'call', '2025-04-04')
    
    # Test with AAPL to compare
    debug_stop_loss_query('AAPL', 230.0, 'call', '2025-04-11')
    
    # Also test the specific example that comes up in the error
    if len(sys.argv) > 1:
        parts = sys.argv[1].split(',')
        if len(parts) >= 4:
            debug_stop_loss_query(parts[0], float(parts[1]), parts[2], parts[3])

if __name__ == "__main__":
    main()