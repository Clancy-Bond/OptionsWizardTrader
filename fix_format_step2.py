#!/usr/bin/env python3
"""
Step 2: Fix the strike price format to show the actual price value
"""

def fix_format_step2():
    """Apply specific change to fix strike price format"""
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # Extract the strike price from contract_parts[0] and convert it to float
    # We need to add code to parse the strike price correctly
    
    bullish_section_start = "if overall_sentiment == \"bullish\":"
    bullish_section_end = "elif overall_sentiment == \"bearish\":"
    
    bullish_start_pos = content.find(bullish_section_start)
    bullish_end_pos = content.find(bullish_section_end, bullish_start_pos)
    
    if bullish_start_pos > 0 and bullish_end_pos > bullish_start_pos:
        bullish_section = content[bullish_start_pos:bullish_end_pos]
        
        # Add code to extract the strike price near where contract_parts is defined
        strike_price_code = """
            # Extract strike price from the option symbol or contract parts
            strike_price = 0.0
            try:
                if 'symbol' in main_contract:
                    # Try to extract from symbol (more reliable)
                    symbol = main_contract['symbol']
                    if 'C' in symbol or 'P' in symbol:
                        # Parse the last part of symbols like O:TSLA250417C00245000
                        strike_part = symbol.split('C' if 'C' in symbol else 'P')[1]
                        if strike_part.startswith('00'):
                            strike_price = float(strike_part) / 1000  # Convert from format like 00245000 to 245.00
                
                # Fallback to contract_parts if needed
                if strike_price == 0.0 and len(contract_parts) >= 1:
                    strike_price = float(contract_parts[0])
            except (ValueError, IndexError):
                # If conversion fails, use a default value
                strike_price = 0.0
            """
        
        # Find the place where main_contract and contract_parts are defined
        insert_pos = bullish_section.find("contract_parts = main_contract.get('contract', '').split()")
        if insert_pos > 0:
            insert_pos = bullish_section.find('\n', insert_pos) + 1
            
            # Insert our strike price extraction code
            updated_bullish = bullish_section[:insert_pos] + strike_price_code + bullish_section[insert_pos:]
            
            # Now update the format string to use strike_price variable instead of contract_parts[0]
            old_format = 'summary += f"in-the-money (${contract_parts[0]}) options expiring on {expiry_date}.'
            new_format = 'summary += f"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}.'
            
            updated_bullish = updated_bullish.replace(old_format, new_format)
            
            # Same for "expiring soon" format
            old_soon_format = 'summary += f"in-the-money (${contract_parts[0]}) options expiring soon.'
            new_soon_format = 'summary += f"in-the-money (${strike_price:.2f}) options expiring soon.'
            
            updated_bullish = updated_bullish.replace(old_soon_format, new_soon_format)
            
            # Update the content with our modified bullish section
            content = content.replace(bullish_section, updated_bullish)
    
    # Now do the same for the bearish section
    bearish_section_start = "elif overall_sentiment == \"bearish\":"
    bearish_section_end = "else:"
    
    bearish_start_pos = content.find(bearish_section_start)
    bearish_end_pos = content.find(bearish_section_end, bearish_start_pos)
    
    if bearish_start_pos > 0 and bearish_end_pos > bearish_start_pos:
        bearish_section = content[bearish_start_pos:bearish_end_pos]
        
        # Add code to extract the strike price near where contract_parts is defined
        strike_price_code = """
            # Extract strike price from the option symbol or contract parts
            strike_price = 0.0
            try:
                if 'symbol' in main_contract:
                    # Try to extract from symbol (more reliable)
                    symbol = main_contract['symbol']
                    if 'C' in symbol or 'P' in symbol:
                        # Parse the last part of symbols like O:TSLA250417C00245000
                        strike_part = symbol.split('C' if 'C' in symbol else 'P')[1]
                        if strike_part.startswith('00'):
                            strike_price = float(strike_part) / 1000  # Convert from format like 00245000 to 245.00
                
                # Fallback to contract_parts if needed
                if strike_price == 0.0 and len(contract_parts) >= 1:
                    strike_price = float(contract_parts[0])
            except (ValueError, IndexError):
                # If conversion fails, use a default value
                strike_price = 0.0
            """
        
        # Find the place where main_contract and contract_parts are defined
        insert_pos = bearish_section.find("contract_parts = main_contract.get('contract', '').split()")
        if insert_pos > 0:
            insert_pos = bearish_section.find('\n', insert_pos) + 1
            
            # Insert our strike price extraction code
            updated_bearish = bearish_section[:insert_pos] + strike_price_code + bearish_section[insert_pos:]
            
            # Now update the format string to use strike_price variable instead of contract_parts[0]
            old_format = 'summary += f"in-the-money (${contract_parts[0]}) options expiring on {expiry_date}.'
            new_format = 'summary += f"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}.'
            
            updated_bearish = updated_bearish.replace(old_format, new_format)
            
            # Same for "expiring soon" format
            old_soon_format = 'summary += f"in-the-money (${contract_parts[0]}) options expiring soon.'
            new_soon_format = 'summary += f"in-the-money (${strike_price:.2f}) options expiring soon.'
            
            updated_bearish = updated_bearish.replace(old_soon_format, new_soon_format)
            
            # Update the content with our modified bearish section
            content = content.replace(bearish_section, updated_bearish)
    
    # Save the changes
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Step 2 complete: Fixed strike price format to show actual price values")

if __name__ == "__main__":
    fix_format_step2()