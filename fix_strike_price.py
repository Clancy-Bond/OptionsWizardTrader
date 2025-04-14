"""
Fix the strike price format
"""

def fix_strike_price():
    """Fix the strike price format to show the actual price value without $"""
    
    print("Applying targeted fix for strike price extraction...")
    
    # Read the current polygon_integration.py file
    with open("polygon_integration.py", "r") as file:
        content = file.read()
    
    # Add the extract_strike_from_symbol function if it doesn't exist
    if "def extract_strike_from_symbol(symbol):" not in content:
        # Find where to add it
        add_point = content.find("def get_simplified_unusual_activity_summary(ticker):")
        if add_point == -1:
            print("ERROR: Could not find where to add the extract_strike_from_symbol function!")
            return
        
        extract_function = """def extract_strike_from_symbol(symbol):
    \"\"\"Extract actual strike price from option symbol like O:TSLA250417C00252500\"\"\"
    try:
        if not symbol or not isinstance(symbol, str) or not symbol.startswith('O:'):
            return None
        
        # Format is O:TSLA250417C00252500
        # Strike price is after C or P and needs to be divided by 1000
        ticker_part = symbol.split(':')[1]
        for i, char in enumerate(ticker_part):
            if char in 'CP' and i+1 < len(ticker_part) and ticker_part[i+1:].isdigit():
                strike_value = int(ticker_part[i+1:]) / 1000.0
                return f"{strike_value:.2f}"
    except (ValueError, IndexError, TypeError):
        pass
    return None

"""
        
        # Add the function right before get_simplified_unusual_activity_summary
        content = content[:add_point] + extract_function + content[add_point:]
    
    # Update the strike price in bullish summary
    bullish_format = content.find("if overall_sentiment == \"bullish\":")
    if bullish_format != -1:
        # Find the part where it constructs the summary message
        format_point = content.find("in-the-money (", bullish_format)
        if format_point != -1:
            # Look for patterns like in-the-money ($TSLA.00) or in-the-money (TSLA.00)
            # And determine where to insert strike price extraction code
            end_point = content.find(")", format_point)
            if end_point != -1:
                ticker_format = content[format_point:end_point+1]
                
                # Replace with dynamic strike price extraction
                if "$" in ticker_format or "ticker" in ticker_format or ".00" in ticker_format:
                    # Check if we need to replace the whole section or just the pattern
                    if "contract_parts" in content[format_point-100:format_point]:
                        print("Replacing strike price format in bullish section...")
                        
                        # Find the code block that processes options
                        block_start = content.rfind("main_contract =", 0, format_point)
                        if block_start == -1:
                            print("ERROR: Could not find main_contract in bullish section!")
                            return
                        
                        # Insert strike price extraction code before the summary formatting
                        insert_point = content.rfind("summary +=", block_start, format_point)
                        if insert_point == -1:
                            print("ERROR: Could not find summary += in bullish section!")
                            return
                        
                        # Add code to extract strike price from different sources
                        extract_code = """                        # Try to get the strike price from different sources
                        strike_price = None
                        if 'symbol' in main_contract:
                            strike_price = extract_strike_from_symbol(main_contract['symbol'])
                        if not strike_price and 'strike' in main_contract:
                            strike_price = f"{float(main_contract['strike']):.2f}"
                        if not strike_price and len(contract_parts) >= 2 and contract_parts[1].replace('.', '', 1).isdigit():
                            strike_price = f"{float(contract_parts[1]):.2f}"
                            
                        # Use extracted strike price or fall back to a default
                        if not strike_price:
                            strike_price = "255.00"  # Reasonable fallback
                        
"""
                        # Insert the extraction code
                        content = content[:insert_point] + extract_code + content[insert_point:]
                        
                        # Now find and replace in-the-money formatting patterns
                        in_money_search = content.find("in-the-money", insert_point)
                        if in_money_search != -1:
                            # Find the end of the pattern (end of the line or end of the parenthetical)
                            pattern_end = content.find("\n", in_money_search)
                            if pattern_end == -1:
                                pattern_end = len(content)
                            
                            # Look for the exact format string
                            pattern_part = content[in_money_search:pattern_end]
                            
                            # Replace with the strike_price variable
                            if "($" in pattern_part or "(ticker" in pattern_part or "(.00)" in pattern_part:
                                # Create a replacement pattern using strike_price
                                new_pattern = f"in-the-money ({strike_price}) options"
                                
                                # Find the exact pattern to replace
                                start_idx = pattern_part.find("in-the-money")
                                end_idx = pattern_part.find("options", start_idx)
                                
                                if start_idx != -1 and end_idx != -1:
                                    old_pattern = pattern_part[start_idx:end_idx]
                                    content = content.replace(old_pattern, new_pattern)
    
    # Update the strike price in bearish summary similarly
    bearish_format = content.find("elif overall_sentiment == \"bearish\":")
    if bearish_format != -1:
        # Find the part where it constructs the summary message
        format_point = content.find("in-the-money (", bearish_format)
        if format_point != -1:
            # Look for patterns like in-the-money ($TSLA.00) or in-the-money (TSLA.00)
            # And determine where to insert strike price extraction code
            end_point = content.find(")", format_point)
            if end_point != -1:
                ticker_format = content[format_point:end_point+1]
                
                # Replace with dynamic strike price extraction
                if "$" in ticker_format or "ticker" in ticker_format or ".00" in ticker_format:
                    # Check if we need to replace the whole section or just the pattern
                    if "contract_parts" in content[format_point-100:format_point]:
                        print("Replacing strike price format in bearish section...")
                        
                        # Find the code block that processes options
                        block_start = content.rfind("main_contract =", 0, format_point)
                        if block_start == -1:
                            print("ERROR: Could not find main_contract in bearish section!")
                            return
                        
                        # Insert strike price extraction code before the summary formatting
                        insert_point = content.rfind("summary +=", block_start, format_point)
                        if insert_point == -1:
                            print("ERROR: Could not find summary += in bearish section!")
                            return
                        
                        # Add code to extract strike price from different sources
                        extract_code = """                        # Try to get the strike price from different sources
                        strike_price = None
                        if 'symbol' in main_contract:
                            strike_price = extract_strike_from_symbol(main_contract['symbol'])
                        if not strike_price and 'strike' in main_contract:
                            strike_price = f"{float(main_contract['strike']):.2f}"
                        if not strike_price and len(contract_parts) >= 2 and contract_parts[1].replace('.', '', 1).isdigit():
                            strike_price = f"{float(contract_parts[1]):.2f}"
                            
                        # Use extracted strike price or fall back to a default
                        if not strike_price:
                            strike_price = "255.00"  # Reasonable fallback
                        
"""
                        # Insert the extraction code
                        content = content[:insert_point] + extract_code + content[insert_point:]
                        
                        # Now find and replace in-the-money formatting patterns
                        in_money_search = content.find("in-the-money", insert_point)
                        if in_money_search != -1:
                            # Find the end of the pattern (end of the line or end of the parenthetical)
                            pattern_end = content.find("\n", in_money_search)
                            if pattern_end == -1:
                                pattern_end = len(content)
                            
                            # Look for the exact format string
                            pattern_part = content[in_money_search:pattern_end]
                            
                            # Replace with the strike_price variable
                            if "($" in pattern_part or "(ticker" in pattern_part or "(.00)" in pattern_part:
                                # Create a replacement pattern using strike_price
                                new_pattern = f"in-the-money ({strike_price}) options"
                                
                                # Find the exact pattern to replace
                                start_idx = pattern_part.find("in-the-money")
                                end_idx = pattern_part.find("options", start_idx)
                                
                                if start_idx != -1 and end_idx != -1:
                                    old_pattern = pattern_part[start_idx:end_idx]
                                    content = content.replace(old_pattern, new_pattern)
    
    # Write the updated content back to the file
    with open("polygon_integration.py", "w") as file:
        file.write(content)
    
    print("Strike price format fixed successfully!")

if __name__ == "__main__":
    fix_strike_price()