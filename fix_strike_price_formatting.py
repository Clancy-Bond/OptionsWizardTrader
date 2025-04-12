#!/usr/bin/env python3
"""
Fix the in-the-money strike price formatting in polygon_integration.py
"""
import re

def fix_strike_price_formatting():
    """
    Fix the formatting of the in-the-money strike price display
    """
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # The issue is that we're showing ($TSLA.00) instead of the actual strike price
    # Find and replace the formatting for in-the-money options
    
    # Pattern 1: Replace in-the-money formatting for bullish options
    content = re.sub(
        r'(summary \+= f"in-the-money \(\$)({contract_parts\[0\]})(\.00\) options expiring on {expiry_date}\.\\n\\n")',
        r'\1{strike_price}\3',
        content
    )
    
    # Pattern 2: Replace in-the-money formatting for bearish options
    content = re.sub(
        r'(summary \+= f"in-the-money \(\$)({contract_parts\[0\]})(\.00\) options expiring soon\.\\n\\n")',
        r'\1{strike_price}\3',
        content
    )
    
    # Extract the strike price from the option symbol or contract data
    # Add code before line 1046 to extract and store strike_price
    bullish_fix = """            # Extract strike price from option symbol
            strike_price = None
            if 'symbol' in main_contract:
                symbol = main_contract['symbol']
                if symbol.startswith('O:'):
                    # Extract strike from symbol (e.g., O:TSLA250417C00252500 => 252.50)
                    match = re.search(r'[CP](\d{8})$', symbol)
                    if match:
                        strike_price = float(match.group(1)) / 1000
            
            # If we couldn't get strike from symbol, use contract_parts[0] if it's numeric
            if not strike_price and len(contract_parts) >= 1:
                if contract_parts[0].replace('.', '', 1).isdigit():
                    strike_price = float(contract_parts[0])
                else:
                    # Fallback to a default if we can't parse the strike
                    strike_price = 0.0
            """
    
    # Insert the strike price extraction code before the in-the-money formatting
    content = content.replace(
        "            # Add strike price and expiration",
        "            # Extract strike price\n" + bullish_fix + "\n            # Add strike price and expiration"
    )
    
    # Same for bearish section
    bearish_fix = """            # Extract strike price from option symbol
            strike_price = None
            if 'symbol' in main_contract:
                symbol = main_contract['symbol']
                if symbol.startswith('O:'):
                    # Extract strike from symbol (e.g., O:TSLA250417C00252500 => 252.50)
                    match = re.search(r'[CP](\d{8})$', symbol)
                    if match:
                        strike_price = float(match.group(1)) / 1000
            
            # If we couldn't get strike from symbol, use contract_parts[0] if it's numeric
            if not strike_price and len(contract_parts) >= 1:
                if contract_parts[0].replace('.', '', 1).isdigit():
                    strike_price = float(contract_parts[0])
                else:
                    # Fallback to a default if we can't parse the strike
                    strike_price = 0.0
            """
    
    # Insert the strike price extraction code for bearish section
    content = content.replace(
        "            # Add strike price and expiration",
        "            # Extract strike price\n" + bearish_fix + "\n            # Add strike price and expiration",
        2  # Replace the second occurrence (bearish section)
    )
    
    # Now update the actual formatting lines to use strike_price instead of contract_parts[0]
    content = content.replace(
        'summary += f"in-the-money (${contract_parts[0]}.00) options expiring on {expiry_date}.\\n\\n"',
        'summary += f"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}.\\n\\n"'
    )
    
    content = content.replace(
        'summary += f"in-the-money (${contract_parts[0]}.00) options expiring soon.\\n\\n"',
        'summary += f"in-the-money (${strike_price:.2f}) options expiring soon.\\n\\n"'
    )
    
    # Write the updated content back to the file
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Fixed strike price formatting for in-the-money options")

if __name__ == "__main__":
    fix_strike_price_formatting()