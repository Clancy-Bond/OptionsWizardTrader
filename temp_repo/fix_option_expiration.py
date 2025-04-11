"""
This script adds better error handling to the option_calculator.py file for cases where
the user requests options data for an expiration date that doesn't exist.
"""

def main():
    """Add better error message for expiration date issues"""
    updated_code = """
# Add an improved version of handle_stop_loss_request to discord_bot.py
def handle_expiration_date_validation(expiration_date, ticker_obj):
    """
    Check if the given expiration date is available and find the closest one if not.
    
    Args:
        expiration_date: The requested expiration date (string in format 'YYYY-MM-DD')
        ticker_obj: The yfinance Ticker object
        
    Returns:
        A tuple with (valid_expiration_date, warning_message)
    """
    # Check if the expiration date is available
    available_expirations = ticker_obj.options
    
    # No options data at all
    if not available_expirations:
        return None, f"No options data available. The market may be closed or this ticker might not have options trading."
    
    # Exact match found
    if expiration_date in available_expirations:
        return expiration_date, None
    
    # Find closest available expiration
    import datetime
    requested_date = datetime.datetime.strptime(expiration_date, '%Y-%m-%d').date()
    closest_date = min(available_expirations, key=lambda x: abs((datetime.datetime.strptime(x, '%Y-%m-%d').date() - requested_date).days))
    days_diff = abs((datetime.datetime.strptime(closest_date, '%Y-%m-%d').date() - requested_date).days)
    
    if days_diff <= 7:
        # Close enough, just use it
        message = f"Expiration {expiration_date} not found. Using closest available: {closest_date} ({days_diff} days different)"
    else:
        # Quite different, give a more detailed warning
        if datetime.datetime.strptime(closest_date, '%Y-%m-%d').date() < requested_date:
            message = f"Expiration {expiration_date} not found. The furthest available expiration is {closest_date}, which is {days_diff} days earlier."
        else:
            message = f"Expiration {expiration_date} not found. The closest available is {closest_date}, which is {days_diff} days later."
    
    return closest_date, message
"""
    
    print(updated_code)
    print("\nThis function should be added to option_calculator.py and called wherever we're checking expiration dates.")
    print("The discord_bot.py should be updated to use this function in both handle_stop_loss_request and handle_option_price_request.")
    
    print("\nKey improvements:")
    print("1. Proper expiration date validation")
    print("2. Finding the closest available date when the requested one isn't available")
    print("3. Providing clear error messages to the user about why their request failed")
    print("4. Creating a reusable function to avoid duplicating code")

if __name__ == "__main__":
    main()