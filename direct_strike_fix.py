#!/usr/bin/env python3
"""
Fix the strike price formatting with direct, targeted changes
"""

def fix_polygon_integration():
    """
    Directly modify the specific lines that need to be changed
    """
    # Read the original file
    with open('polygon_integration.py', 'r') as file:
        original_content = file.read()
    
    # Add the strike price extraction code to the bullish section
    bullish_insertion_point = "            main_contract = next((item for item in activity if item.get('sentiment') == 'bullish'), activity[0])\n            contract_parts = main_contract.get('contract', '').split()"
    
    bullish_extraction_code = """            main_contract = next((item for item in activity if item.get('sentiment') == 'bullish'), activity[0])
            contract_parts = main_contract.get('contract', '').split()
            
            # Extract strike price from option symbol
            strike_price = 0.0
            if 'symbol' in main_contract:
                symbol = main_contract['symbol']
                if symbol.startswith('O:'):
                    # Format: O:TSLA250417C00250000 (strike = 250.00)
                    import re
                    match = re.search(r'[CP](\d{8})$', symbol)
                    if match:
                        strike_price = float(match.group(1)) / 1000
                        print(f"Extracted strike price {strike_price} from {symbol}")
            
            # Fallback to contract_parts if needed
            if strike_price == 0.0 and len(contract_parts) >= 1:
                try:
                    strike_price = float(contract_parts[0])
                except (ValueError, TypeError):
                    # If conversion fails, keep the default
                    pass"""
    
    # Add the strike price extraction code to the bearish section
    bearish_insertion_point = "            main_contract = next((item for item in activity if item.get('sentiment') == 'bearish'), activity[0])\n            contract_parts = main_contract.get('contract', '').split()"
    
    bearish_extraction_code = """            main_contract = next((item for item in activity if item.get('sentiment') == 'bearish'), activity[0])
            contract_parts = main_contract.get('contract', '').split()
            
            # Extract strike price from option symbol
            strike_price = 0.0
            if 'symbol' in main_contract:
                symbol = main_contract['symbol']
                if symbol.startswith('O:'):
                    # Format: O:TSLA250417C00250000 (strike = 250.00)
                    import re
                    match = re.search(r'[CP](\d{8})$', symbol)
                    if match:
                        strike_price = float(match.group(1)) / 1000
                        print(f"Extracted strike price {strike_price} from {symbol}")
            
            # Fallback to contract_parts if needed
            if strike_price == 0.0 and len(contract_parts) >= 1:
                try:
                    strike_price = float(contract_parts[0])
                except (ValueError, TypeError):
                    # If conversion fails, keep the default
                    pass"""
    
    # Update the bullish and bearish sections
    content = original_content.replace(bullish_insertion_point, bullish_extraction_code)
    content = content.replace(bearish_insertion_point, bearish_extraction_code)
    
    # Now replace the in-the-money formatting to use strike_price instead of contract_parts[0]
    content = content.replace(
        'summary += f"in-the-money (${contract_parts[0]}.00) options expiring on {expiry_date}.\\n\\n"',
        'summary += f"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}.\\n\\n"'
    )
    
    content = content.replace(
        'summary += f"in-the-money (${contract_parts[0]}.00) options expiring soon.\\n\\n"',
        'summary += f"in-the-money (${strike_price:.2f}) options expiring soon.\\n\\n"'
    )
    
    # Write the modified content back to the file
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Fixed the strike price formatting in polygon_integration.py")

if __name__ == "__main__":
    fix_polygon_integration()