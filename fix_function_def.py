"""
Fix the function definition in polygon_integration.py
"""

def fix_function_def():
    print("Fixing the function definition...")
    
    with open('polygon_integration.py', 'r') as file:
        content = file.readlines()
    
    # Find the function definition we need to restore
    function_start = None
    extract_func_defined = False
    
    for i, line in enumerate(content):
        if 'def get_simplified_unusual_activity_summary(ticker):' in line and function_start is None:
            function_start = i
        if 'def extract_strike_from_symbol(' in line:
            extract_func_defined = True
    
    # If we couldn't find the function start, something is wrong
    if function_start is None:
        print("ERROR: Could not find function definition!")
        return
    
    # Add the extract_strike_from_symbol function if it's not already defined
    if not extract_func_defined:
        helper_function = """
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
        # Find the function before get_simplified_unusual_activity_summary
        previous_function_end = None
        for i in range(function_start - 1, 0, -1):
            if content[i].strip() == "":
                previous_function_end = i
                break
        
        if previous_function_end:
            # Insert the helper function after the previous function
            content.insert(previous_function_end, helper_function)
            function_start += len(helper_function.split('\n'))  # Update function_start index
    
    # Fix the function definition
    fixed_function_def = """def get_simplified_unusual_activity_summary(ticker):
    \"\"\"
    Create a simplified, conversational summary of unusual options activity
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        A string with a conversational summary of unusual options activity
    \"\"\"
"""
    
    # Replace the function definition line
    content[function_start] = fixed_function_def
    
    # Write the fixed content back to the file
    with open('polygon_integration.py', 'w') as file:
        file.writelines(content)
    
    print("Function definition fixed!")

if __name__ == "__main__":
    fix_function_def()