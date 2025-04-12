#!/usr/bin/env python3
"""
Fix the in-the-money strike price formatting by directly examining the option symbols
"""
import re

def fix_strike_price():
    """
    Extract the real strike price from the option symbol
    """
    with open('polygon_integration.py', 'r') as file:
        content = file.readlines()
    
    # We need to modify two sections - the bullish and bearish parts
    
    # First, find the lines with the bullish formatting for in-the-money options
    bullish_format_line = None
    bearish_format_line = None
    
    for i, line in enumerate(content):
        if "in-the-money" in line and "expiring on {expiry_date}" in line:
            bullish_format_line = i
        if "in-the-money" in line and "expiring soon" in line and bullish_format_line is not None:
            bearish_format_line = i
            break
    
    # Bullish section - Add code to extract the real strike price
    if bullish_format_line is not None:
        # We need to insert code before this line to extract the strike price
        bullish_insert_code = [
            "                # Extract strike price directly from the option symbol\n",
            "                strike_price = 0.0\n",
            "                if 'symbol' in main_contract:\n",
            "                    option_symbol = main_contract['symbol']\n",
            "                    # Format: O:TSLA250417C00250000 (strike = 250.00)\n",
            "                    if option_symbol.startswith('O:'):\n",
            "                        # Find the C or P in the symbol, then extract the strike\n",
            "                        match = re.search(r'[CP](\d{8})$', option_symbol)\n",
            "                        if match:\n",
            "                            # Convert to float and divide by 1000 to get actual strike\n",
            "                            strike_price = float(match.group(1)) / 1000\n",
            "                            print(f\"Extracted strike price {strike_price} from {option_symbol}\")\n"
        ]
        
        # Insert the code before the in-the-money line
        content[bullish_format_line-1:bullish_format_line-1] = bullish_insert_code
        
        # Update the line with the correct format (use strike_price instead of contract_parts[0])
        content[bullish_format_line + len(bullish_insert_code)] = content[bullish_format_line + len(bullish_insert_code)].replace(
            "in-the-money (${contract_parts[0]}.00)",
            "in-the-money (${strike_price:.2f})"
        )
    
    # Bearish section - Add code to extract the real strike price 
    # (adjusted for the inserted lines above)
    bearish_format_line += len(bullish_insert_code)
    if bearish_format_line is not None:
        # We need to insert code before this line to extract the strike price
        bearish_insert_code = [
            "                # Extract strike price directly from the option symbol\n",
            "                strike_price = 0.0\n",
            "                if 'symbol' in main_contract:\n",
            "                    option_symbol = main_contract['symbol']\n",
            "                    # Format: O:TSLA250417C00250000 (strike = 250.00)\n",
            "                    if option_symbol.startswith('O:'):\n",
            "                        # Find the C or P in the symbol, then extract the strike\n",
            "                        match = re.search(r'[CP](\d{8})$', option_symbol)\n",
            "                        if match:\n",
            "                            # Convert to float and divide by 1000 to get actual strike\n",
            "                            strike_price = float(match.group(1)) / 1000\n",
            "                            print(f\"Extracted strike price {strike_price} from {option_symbol}\")\n"
        ]
        
        # Insert the code before the in-the-money line
        content[bearish_format_line-1:bearish_format_line-1] = bearish_insert_code
        
        # Update the line with the correct format (use strike_price instead of contract_parts[0])
        content[bearish_format_line + len(bearish_insert_code)] = content[bearish_format_line + len(bearish_insert_code)].replace(
            "in-the-money (${contract_parts[0]}.00)",
            "in-the-money (${strike_price:.2f})"
        )
    
    # Find also the identical code blocks in the bearish section
    bearish_section_start = None
    for i, line in enumerate(content):
        if "elif overall_sentiment == \"bearish\":" in line:
            bearish_section_start = i
            break
    
    if bearish_section_start is not None:
        # Find the next two occurrences of in-the-money formatting in the bearish section
        bearish_format_lines = []
        for i in range(bearish_section_start, len(content)):
            if "in-the-money" in content[i]:
                bearish_format_lines.append(i)
                if len(bearish_format_lines) == 2:
                    break
        
        # For the first bearish in-the-money line
        if len(bearish_format_lines) > 0:
            # We need to insert code before this line to extract the strike price
            bearish_insert_code1 = [
                "                # Extract strike price directly from the option symbol\n",
                "                strike_price = 0.0\n",
                "                if 'symbol' in main_contract:\n",
                "                    option_symbol = main_contract['symbol']\n",
                "                    # Format: O:TSLA250417C00250000 (strike = 250.00)\n",
                "                    if option_symbol.startswith('O:'):\n",
                "                        # Find the C or P in the symbol, then extract the strike\n",
                "                        match = re.search(r'[CP](\d{8})$', option_symbol)\n",
                "                        if match:\n",
                "                            # Convert to float and divide by 1000 to get actual strike\n",
                "                            strike_price = float(match.group(1)) / 1000\n",
                "                            print(f\"Extracted strike price {strike_price} from {option_symbol}\")\n"
            ]
            
            # Insert the code before the in-the-money line
            content[bearish_format_lines[0]-1:bearish_format_lines[0]-1] = bearish_insert_code1
            
            # Update all subsequent line indices due to insertion
            bearish_format_lines[1] += len(bearish_insert_code1)
            
            # Update the line with the correct format (use strike_price instead of contract_parts[0])
            content[bearish_format_lines[0] + len(bearish_insert_code1)] = content[bearish_format_lines[0] + len(bearish_insert_code1)].replace(
                "in-the-money (${contract_parts[0]}.00)",
                "in-the-money (${strike_price:.2f})"
            )
        
        # For the second bearish in-the-money line
        if len(bearish_format_lines) > 1:
            # We need to insert code before this line to extract the strike price
            bearish_insert_code2 = [
                "                # Extract strike price directly from the option symbol\n",
                "                strike_price = 0.0\n",
                "                if 'symbol' in main_contract:\n",
                "                    option_symbol = main_contract['symbol']\n",
                "                    # Format: O:TSLA250417C00250000 (strike = 250.00)\n",
                "                    if option_symbol.startswith('O:'):\n",
                "                        # Find the C or P in the symbol, then extract the strike\n",
                "                        match = re.search(r'[CP](\d{8})$', option_symbol)\n",
                "                        if match:\n",
                "                            # Convert to float and divide by 1000 to get actual strike\n",
                "                            strike_price = float(match.group(1)) / 1000\n",
                "                            print(f\"Extracted strike price {strike_price} from {option_symbol}\")\n"
            ]
            
            # Insert the code before the in-the-money line
            content[bearish_format_lines[1]-1:bearish_format_lines[1]-1] = bearish_insert_code2
            
            # Update the line with the correct format (use strike_price instead of contract_parts[0])
            content[bearish_format_lines[1] + len(bearish_insert_code2)] = content[bearish_format_lines[1] + len(bearish_insert_code2)].replace(
                "in-the-money (${contract_parts[0]}.00)",
                "in-the-money (${strike_price:.2f})"
            )
    
    # Write the updated content back to the file
    with open('polygon_integration.py', 'w') as file:
        file.writelines(content)
    
    print("Fixed the strike price formatting in polygon_integration.py")

if __name__ == "__main__":
    fix_strike_price()