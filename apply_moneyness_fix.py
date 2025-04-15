"""
Apply moneyness fixes to polygon_integration.py
This script edits polygon_integration.py to use determine_moneyness()
"""

import re
import shutil

def apply_moneyness_fix():
    # Back up the current file first
    try:
        shutil.copy('polygon_integration.py', 'polygon_integration.py.backup')
        print("Backed up polygon_integration.py to polygon_integration.py.backup")
    except Exception as e:
        print(f"Warning: Failed to create backup: {e}")
    
    try:
        with open('polygon_integration.py', 'r') as file:
            content = file.read()
            
        # First make sure the determine_moneyness function is defined
        if "def determine_moneyness(" not in content:
            print("Adding determine_moneyness function...")
            moneyness_func = '''
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
'''
            
            # Find the appropriate place to add the function
            if "def extract_strike_from_symbol(" in content:
                # Add after this function
                pattern = r"def extract_strike_from_symbol\(.*?\):.*?return None\s*"
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    insert_pos = match.end()
                    content = content[:insert_pos] + "\n" + moneyness_func + "\n" + content[insert_pos:]
                else:
                    # If we can't find the end of extract_strike_from_symbol, add before get_simplified_unusual_activity_summary
                    if "def get_simplified_unusual_activity_summary(" in content:
                        insert_pos = content.find("def get_simplified_unusual_activity_summary(")
                        content = content[:insert_pos] + moneyness_func + "\n\n" + content[insert_pos:]
            else:
                # If we can't find extract_strike_from_symbol, add before get_simplified_unusual_activity_summary
                if "def get_simplified_unusual_activity_summary(" in content:
                    insert_pos = content.find("def get_simplified_unusual_activity_summary(")
                    content = content[:insert_pos] + moneyness_func + "\n\n" + content[insert_pos:]
                
        print("Fixing moneyness in string formats...")
        
        # Define the different patterns that need to be fixed
        # Pattern 1: Fix moneyness with strike price from symbol extraction in f-strings
        pattern1 = r'summary \+= f"in-the-money \({(strike_price)}\) options expiring {(expiry_date)}, purchased {(timestamp_str if timestamp_str else \'[^\']+\')}\.'
        replacement1 = r'summary += f"{determine_moneyness(\1, result_with_metadata.get(\'current_stock_price\', 0), \'call\')} ({\1}) options expiring {\2}, purchased {\3}.\n\n"'
        
        content = re.sub(pattern1, replacement1, content)
        
        # Pattern 2: Fix moneyness with strike price from contract_parts in f-strings for call options
        pattern2 = r'summary \+= f"in-the-money \({contract_parts\[1\]}\) options expiring {(expiry_date)}, purchased {(timestamp_str if timestamp_str else \'[^\']+\')}\.'
        replacement2 = r'summary += f"{determine_moneyness(contract_parts[1], result_with_metadata.get(\'current_stock_price\', 0), \'call\')} ({contract_parts[1]}) options expiring {\1}, purchased {\2}.\n\n"'
        
        content = re.sub(pattern2, replacement2, content)
        
        # Pattern 3: Fix moneyness with strike price from contract_parts for soon-expiring options
        pattern3 = r'summary \+= f"in-the-money \({contract_parts\[1\]}\) options expiring soon, purchased {(timestamp_str if timestamp_str else \'[^\']+\')}\.'
        replacement3 = r'summary += f"{determine_moneyness(contract_parts[1], result_with_metadata.get(\'current_stock_price\', 0), \'call\')} ({contract_parts[1]}) options expiring soon, purchased {\1}.\n\n"'
        
        content = re.sub(pattern3, replacement3, content)

        # Same patterns for put options
        pattern4 = r'summary \+= f"in-the-money \({(strike_price)}\) options expiring {(expiry_date)}, purchased {(timestamp_str if timestamp_str else \'[^\']+\')}\.'
        replacement4 = r'summary += f"{determine_moneyness(\1, result_with_metadata.get(\'current_stock_price\', 0), \'put\')} ({\1}) options expiring {\2}, purchased {\3}.\n\n"'
        
        content = re.sub(pattern4, replacement4, content)
        
        pattern5 = r'summary \+= f"in-the-money \({contract_parts\[1\]}\) options expiring {(expiry_date)}, purchased {(timestamp_str if timestamp_str else \'[^\']+\')}\.'
        replacement5 = r'summary += f"{determine_moneyness(contract_parts[1], result_with_metadata.get(\'current_stock_price\', 0), \'put\')} ({contract_parts[1]}) options expiring {\1}, purchased {\2}.\n\n"'
        
        content = re.sub(pattern5, replacement5, content)
        
        pattern6 = r'summary \+= f"in-the-money \({contract_parts\[1\]}\) options expiring soon, purchased {(timestamp_str if timestamp_str else \'[^\']+\')}\.'
        replacement6 = r'summary += f"{determine_moneyness(contract_parts[1], result_with_metadata.get(\'current_stock_price\', 0), \'put\')} ({contract_parts[1]}) options expiring soon, purchased {\1}.\n\n"'
        
        content = re.sub(pattern6, replacement6, content)
        
        # Ensure current_stock_price is included in the metadata
        if "'current_stock_price': stock_price" not in content:
            pattern = "'all_options_analyzed': len(all_options)"
            replacement = "'all_options_analyzed': len(all_options),\n            'current_stock_price': stock_price"
            content = content.replace(pattern, replacement)
        
        # Check if we actually made any changes
        if "determine_moneyness(" not in content:
            print("Warning: No moneyness calls were replaced. Check the pattern matching.")
        
        # Write the modified content back to the file
        with open('polygon_integration.py', 'w') as file:
            file.write(content)
            
        print("Moneyness fix applied successfully!")
        return True
    except Exception as e:
        print(f"Error applying moneyness fix: {e}")
        return False

if __name__ == "__main__":
    apply_moneyness_fix()