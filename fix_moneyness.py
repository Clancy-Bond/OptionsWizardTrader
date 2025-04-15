"""
Fix for polygon_integration.py to update all occurrences of hardcoded "in-the-money"
to use dynamic moneyness detection based on current stock price and option details.
"""

import re

def replace_moneyness_text():
    """Apply the moneyness detection fix to polygon_integration.py"""
    try:
        # Read the entire file content
        with open('polygon_integration.py', 'r') as file:
            content = file.read()
        
        # First replace for bullish section (assuming calls)
        bullish_pattern = r'(\s+if strike_price:\s+summary \+= f)"in-the-money \(\{strike_price\}\)(.*?)"\s*'
        bullish_replacement = r'\1"{moneyness} ({strike_price})\2"\n            # Get proper moneyness classification\n            stock_price = get_current_price(ticker)\n            moneyness = get_option_moneyness(main_contract["symbol"], strike_price, stock_price, "bullish")\n            '
        
        # Apply first replacement for bullish section
        content = re.sub(bullish_pattern, bullish_replacement, content)
        
        # Second replace for bearish section (assuming puts)
        bearish_pattern = r'(\s+if strike_price:\s+summary \+= f)"in-the-money \(\{strike_price\}\)(.*?)"\s*'
        bearish_replacement = r'\1"{moneyness} ({strike_price})\2"\n            # Get proper moneyness classification\n            stock_price = get_current_price(ticker)\n            moneyness = get_option_moneyness(main_contract["symbol"], strike_price, stock_price, "bearish")\n            '
        
        # Apply second replacement for bearish section
        content = re.sub(bearish_pattern, bearish_replacement, content)
        
        # Now handle the other in-the-money occurrences that use contract_parts
        contract_pattern = r'(\s+)(summary \+= f)"in-the-money \(\{contract_parts\[1\]\}\)(.*?)"\s*'
        contract_replacement = r'\1# Get proper moneyness classification\n\1stock_price = get_current_price(ticker)\n\1try:\n\1    strike_value = float(contract_parts[1])\n\1    # Determine moneyness based on section (bullish = call, bearish = put)\n\1    if "bullish" in summary.lower():\n\1        moneyness = "in-the-money" if stock_price > strike_value else "out-of-the-money"\n\1    else:  # bearish\n\1        moneyness = "in-the-money" if stock_price < strike_value else "out-of-the-money"\n\1except:\n\1    moneyness = "in-the-money"  # Fallback\n\n\1\2"{moneyness} ({contract_parts[1]})\3"\n'
        
        # Apply replacements for contract_parts
        content = re.sub(contract_pattern, contract_replacement, content)
        
        # Write the modified content back to the file
        with open('polygon_integration.py', 'w') as file:
            file.write(content)
            
        print("Successfully applied moneyness detection fixes to polygon_integration.py")
        return True
    except Exception as e:
        print(f"Error applying moneyness detection fixes: {str(e)}")
        return False

if __name__ == "__main__":
    print("Applying moneyness detection fixes...")
    success = replace_moneyness_text()
    print(f"Fixes completed: {'Successfully' if success else 'Failed'}")