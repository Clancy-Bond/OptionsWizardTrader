"""
Fix the contract parsing to correctly extract strike prices
"""

def fix_contract_parsing():
    print("Fixing contract parsing to extract strike prices correctly...")
    
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # Add a helper function to extract strike price from option symbols
    add_after = "def get_simplified_unusual_activity_summary(ticker):"
    helper_function = """
    def get_simplified_unusual_activity_summary(ticker):
        \"\"\"
        Create a simplified, conversational summary of unusual options activity
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            A string with a conversational summary of unusual options activity
        \"\"\"
        
        # Helper function to extract strike price from option symbol
        def extract_strike_from_symbol(symbol):
            \"\"\"Extract actual strike price from option symbol like O:TSLA250417C00252500\"\"\"
            if not symbol or not symbol.startswith('O:'):
                return None
                
            try:
                # Format is O:TSLA250417C00252500 where last 8 digits are strike * 1000
                strike_part = symbol.split('C')[-1] if 'C' in symbol else symbol.split('P')[-1]
                if strike_part and len(strike_part) >= 8:
                    strike_value = int(strike_part) / 1000.0
                    return f"{strike_value:.2f}"
                return None
            except (ValueError, IndexError):
                return None
    """
    
    # Replace the function definition with our updated version that includes the helper
    content = content.replace(add_after, helper_function)
    
    # Update bullish section to use this helper function
    bullish_section = """            # Add strike price and expiration
            if len(contract_parts) >= 3:
                # If we have a properly parsed expiration date
                if expiry_date:
                    # Try to extract the real strike price from the option symbol
                    if 'symbol' in main_contract:
                        strike_price = extract_strike_from_symbol(main_contract['symbol'])
                        if strike_price:
                            summary += f"in-the-money ({strike_price}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '04/11/25'}.\\n\\n"
                        else:
                            summary += f"in-the-money ({contract_parts[0]}.00) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '04/11/25'}.\\n\\n"
                    else:
                        summary += f"in-the-money ({contract_parts[0]}.00) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '04/11/25'}.\\n\\n"
                else:
                    # Fallback to just the second part if we couldn't parse a proper date
                    summary += f"in-the-money ({contract_parts[0]}.00) options expiring soon, purchased {timestamp_str if timestamp_str else '04/11/25'}.\\n\\n"
            else:
                summary += f"options from the largest unusual activity.\\n\\n\""""
    
    # Find and replace the bullish section
    old_bullish_section = """            # Add strike price and expiration
            if len(contract_parts) >= 3:
                # If we have a properly parsed expiration date
                if expiry_date:
                    summary += f"in-the-money ({contract_parts[0]}.00) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '04/11/25'}.\\n\\n"
                else:
                    # Fallback to just the second part if we couldn't parse a proper date
                    summary += f"in-the-money ({contract_parts[0]}.00) options expiring soon, purchased {timestamp_str if timestamp_str else '04/11/25'}.\\n\\n"
            else:
                summary += f"options from the largest unusual activity.\\n\\n\""""
    
    content = content.replace(old_bullish_section, bullish_section)
    
    # Update bearish section similarly
    bearish_section = """            # Add strike price and expiration
            if len(contract_parts) >= 3:
                # If we have a properly parsed expiration date
                if expiry_date:
                    # Try to extract the real strike price from the option symbol
                    if 'symbol' in main_contract:
                        strike_price = extract_strike_from_symbol(main_contract['symbol'])
                        if strike_price:
                            summary += f"in-the-money ({strike_price}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '04/11/25'}.\\n\\n"
                        else:
                            summary += f"in-the-money ({contract_parts[0]}.00) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '04/11/25'}.\\n\\n"
                    else:
                        summary += f"in-the-money ({contract_parts[0]}.00) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '04/11/25'}.\\n\\n"
                else:
                    # Fallback to just the second part if we couldn't parse a proper date
                    summary += f"in-the-money ({contract_parts[0]}.00) options expiring soon, purchased {timestamp_str if timestamp_str else '04/11/25'}.\\n\\n"
            else:
                summary += f"options from the largest unusual activity.\\n\\n\""""
    
    # Find and replace the bearish section
    old_bearish_section = """            # Add strike price and expiration
            if len(contract_parts) >= 3:
                # If we have a properly parsed expiration date
                if expiry_date:
                    summary += f"in-the-money ({contract_parts[0]}.00) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else '04/11/25'}.\\n\\n"
                else:
                    # Fallback to just the second part if we couldn't parse a proper date
                    summary += f"in-the-money ({contract_parts[0]}.00) options expiring soon, purchased {timestamp_str if timestamp_str else '04/11/25'}.\\n\\n"
            else:
                summary += f"options from the largest unusual activity.\\n\\n\""""
    
    content = content.replace(old_bearish_section, bearish_section)
    
    # Write the fixed content back to the file
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Contract parsing fixed!")

if __name__ == "__main__":
    fix_contract_parsing()