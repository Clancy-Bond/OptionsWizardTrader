#!/usr/bin/env python3
"""
Simple, targeted fix for the ($TICKER.00) formatting issue
"""
import re

def fix_format():
    """Apply a minimal, targeted fix to format options correctly"""
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # Find the in-the-money formatting pattern - this is what shows ($TSLA.00) instead of the correct strike price
    money_pattern1 = r'summary \+= f"in-the-money \(\${ticker}\.00\) options expiring on {expiry_date}\.\\n\\n"'
    money_pattern2 = r'summary \+= f"in-the-money \(\${ticker}\.00\) options expiring soon\.\\n\\n"'
    
    # Replace with actual strike price formatting
    replacement1 = r'summary += f"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}.\\n\\n"'
    replacement2 = r'summary += f"in-the-money (${strike_price:.2f}) options expiring soon.\\n\\n"'
    
    # Add the strike_price extraction just before the in-the-money lines
    # First, locate the processing blocks
    bullish_section = re.search(r'if overall_sentiment == "bullish":(.*?)elif overall_sentiment == "bearish":', content, re.DOTALL)
    bearish_section = re.search(r'elif overall_sentiment == "bearish":(.*?)else:', content, re.DOTALL)
    
    # Only make the replacements if we found the sections
    if bullish_section:
        bullish_text = bullish_section.group(1)
        
        # Add strike_price extraction to bullish section
        bullish_fixed = bullish_text.replace(
            'if len(contract_parts) >= 3:',
            '''# Get the strike price from the option symbol
            strike_price = 0.0
            if 'symbol' in main_contract:
                symbol = main_contract['symbol']
                if symbol.startswith('O:'):
                    # Format: O:TSLA250417C00250000 (strike = 250.00)
                    match = re.search(r'[CP](\\d{8})$', symbol)
                    if match:
                        strike_price = float(match.group(1)) / 1000
                        print(f"Extracted strike price {strike_price} from {symbol}")
            
            if len(contract_parts) >= 3:'''
        )
        
        # Replace with fixed version
        content = content.replace(bullish_text, bullish_fixed)
    
    if bearish_section:
        bearish_text = bearish_section.group(1)
        
        # Add strike_price extraction to bearish section
        bearish_fixed = bearish_text.replace(
            'if len(contract_parts) >= 3:',
            '''# Get the strike price from the option symbol
            strike_price = 0.0
            if 'symbol' in main_contract:
                symbol = main_contract['symbol']
                if symbol.startswith('O:'):
                    # Format: O:TSLA250417C00250000 (strike = 250.00)
                    match = re.search(r'[CP](\\d{8})$', symbol)
                    if match:
                        strike_price = float(match.group(1)) / 1000
                        print(f"Extracted strike price {strike_price} from {symbol}")
            
            if len(contract_parts) >= 3:'''
        )
        
        # Replace with fixed version
        content = content.replace(bearish_text, bearish_fixed)
    
    # Now replace the specific ticker formatting issue
    content = content.replace('(${ticker}.00)', '(${strike_price:.2f})')
    
    # Add re import at the top if needed
    if 're.search' in content and 'import re' not in content:
        content = content.replace('import math', 'import math\nimport re')
    
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Fixed the in-the-money formatting issue")

if __name__ == "__main__":
    fix_format()