"""
Simple moneyness implementation to replace the existing incorrect logic
that always shows options as "in-the-money" regardless of actual status.
"""

def determine_moneyness(strike_price, stock_price, option_type):
    """
    Determine if an option is in-the-money or out-of-the-money
    
    Args:
        strike_price: Option strike price (as float or string)
        stock_price: Current stock price
        option_type: 'call' or 'put'
        
    Returns:
        String: 'in-the-money' or 'out-of-the-money'
    """
    try:
        # Convert strike price to float if it's a string
        if isinstance(strike_price, str):
            strike_price = float(strike_price)
            
        # For call options: in-the-money if strike < stock price
        if option_type.lower() == 'call':
            return 'in-the-money' if strike_price < stock_price else 'out-of-the-money'
        # For put options: in-the-money if strike > stock price
        elif option_type.lower() == 'put':
            return 'in-the-money' if strike_price > stock_price else 'out-of-the-money'
        else:
            return 'in-the-money'  # Default to in-the-money if we can't determine
    except (ValueError, TypeError):
        return 'in-the-money'  # Default to in-the-money if conversion fails