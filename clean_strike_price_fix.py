#!/usr/bin/env python3
"""
Clean fix for the strike price formatting issue in unusual options activity
"""
import re

def fix_polygon_integration():
    """
    Fix the polygon_integration.py file to properly show strike prices in the output
    """
    # Create the new file content with corrections
    with open('polygon_integration.py', 'r') as file:
        lines = file.readlines()
    
    # Find the specific patterns that need to be fixed
    bullish_in_money_pattern = r'f"in-the-money \(\${contract_parts\[0\]}\.00\) options expiring on {expiry_date}\.\\n\\n"'
    bullish_soon_pattern = r'f"in-the-money \(\${contract_parts\[0\]}\.00\) options expiring soon\.\\n\\n"'
    
    bearish_in_money_pattern = r'f"in-the-money \(\${contract_parts\[0\]}\.00\) options expiring on {expiry_date}\.\\n\\n"'
    bearish_soon_pattern = r'f"in-the-money \(\${contract_parts\[0\]}\.00\) options expiring soon\.\\n\\n"'
    
    # Process each line and apply fixes
    new_lines = []
    i = 0
    in_bullish_section = False
    in_bearish_section = False
    fixed_bullish = False
    fixed_bearish = False
    
    while i < len(lines):
        line = lines[i]
        
        # Track which section we're in
        if 'if overall_sentiment == "bullish":' in line:
            in_bullish_section = True
            in_bearish_section = False
        elif 'elif overall_sentiment == "bearish":' in line:
            in_bullish_section = False
            in_bearish_section = True
        
        # For the bullish section
        if in_bullish_section and not fixed_bullish and 'main_contract = next(' in line:
            # Add the strike extraction code after this line
            new_lines.append(line)
            i += 1  # Skip to the next line
            
            # Process lines until we find where to add our strike extraction code
            while i < len(lines) and 'contract_parts = main_contract.get' in lines[i]:
                new_lines.append(lines[i])
                i += 1
            
            # Add our strike extraction code here
            new_lines.append("""            # Extract the actual strike price from the option symbol
            strike_price = 0.0
            if 'symbol' in main_contract:
                symbol = main_contract['symbol']
                if symbol.startswith('O:'):
                    # Extract the strike price from the option symbol (e.g., O:TSLA250417C00252500 -> 252.50)
                    match = re.search(r'[CP](\d{8})$', symbol)
                    if match:
                        strike_price = float(match.group(1)) / 1000
            
            # If we couldn't get the strike from the symbol, try using contract_parts
            if strike_price == 0.0 and len(contract_parts) >= 1 and contract_parts[0].replace('.', '', 1).isdigit():
                strike_price = float(contract_parts[0])
            
""")
            fixed_bullish = True
            continue  # Skip to the next iteration of the loop
        
        # For the bearish section
        if in_bearish_section and not fixed_bearish and 'main_contract = next(' in line:
            # Add the strike extraction code after this line
            new_lines.append(line)
            i += 1  # Skip to the next line
            
            # Process lines until we find where to add our strike extraction code
            while i < len(lines) and 'contract_parts = main_contract.get' in lines[i]:
                new_lines.append(lines[i])
                i += 1
            
            # Add our strike extraction code here
            new_lines.append("""            # Extract the actual strike price from the option symbol
            strike_price = 0.0
            if 'symbol' in main_contract:
                symbol = main_contract['symbol']
                if symbol.startswith('O:'):
                    # Extract the strike price from the option symbol (e.g., O:TSLA250417C00252500 -> 252.50)
                    match = re.search(r'[CP](\d{8})$', symbol)
                    if match:
                        strike_price = float(match.group(1)) / 1000
            
            # If we couldn't get the strike from the symbol, try using contract_parts
            if strike_price == 0.0 and len(contract_parts) >= 1 and contract_parts[0].replace('.', '', 1).isdigit():
                strike_price = float(contract_parts[0])
            
""")
            fixed_bearish = True
            continue  # Skip to the next iteration of the loop
        
        # Fix the in-the-money formatting patterns
        if re.search(bullish_in_money_pattern, line) or re.search(bearish_in_money_pattern, line):
            line = line.replace('${contract_parts[0]}.00', '${strike_price:.2f}')
        
        if re.search(bullish_soon_pattern, line) or re.search(bearish_soon_pattern, line):
            line = line.replace('${contract_parts[0]}.00', '${strike_price:.2f}')
        
        new_lines.append(line)
        i += 1
    
    # Write the modified content back to the file
    with open('polygon_integration.py', 'w') as file:
        file.writelines(new_lines)
    
    print("Fixed the strike price formatting in polygon_integration.py")

if __name__ == "__main__":
    fix_polygon_integration()