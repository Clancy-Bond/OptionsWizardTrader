"""
Debug script for handle_stop_loss_request - directly adds enhanced debugging statements
to track where the method is failing to return properly
"""
import re

def add_debugging():
    """Add enhanced debugging to track the execution flow in handle_stop_loss_request"""
    with open('discord_bot.py', 'r') as file:
        content = file.read()

    # 1. Find the start line of the method
    method_start_match = re.search(r'async def handle_stop_loss_request\(self, message, info\):', content)
    if not method_start_match:
        print("ERROR: Could not find handle_stop_loss_request method")
        return

    # Position of the method start
    method_start_pos = method_start_match.start()
    
    # 2. Find the start of the try block and add detailed debugging
    try_match = re.search(r'\s+try:', content[method_start_pos:])
    if not try_match:
        print("ERROR: Could not find try block in handle_stop_loss_request")
        return
    
    try_pos = method_start_pos + try_match.end()
    
    # Insert detailed debugging after the try block
    debug_code = """
            # Enhanced debugging for stop loss function
            print("DEBUG: Enhanced debugging enabled for stop_loss_request")
            import inspect
            frame = inspect.currentframe()
            print(f"DEBUG: Current method at line {frame.f_lineno}")
    """
    
    content = content[:try_pos] + debug_code + content[try_pos:]
    
    # 3. Add debugging to return statements for swing trade section
    swing_trade_pattern = r'elif trade_type == "Swing Trade":(.*?)(?=elif trade_type|else:)'
    swing_match = re.search(swing_trade_pattern, content, re.DOTALL)
    
    if swing_match:
        swing_section = swing_match.group(0)
        
        # Add a return statement with debugging if needed
        if 'return embed' not in swing_section:
            if 'embed.description = response' in swing_section:
                updated_swing = swing_section.replace(
                    'embed.description = response',
                    'embed.description = response\n                    print("DEBUG: Returning embed from swing trade section")\n                    return embed'
                )
                content = content.replace(swing_section, updated_swing)
                print("Added return statement with debugging to swing trade section")
    
    # 4. Add debugging before all existing return statements
    return_pattern = r'return\s+embed'
    content = re.sub(
        return_pattern,
        'print("DEBUG: About to return embed")\n                    return embed',
        content
    )
    
    # 5. Add additional debug logging for important if blocks
    trade_horizon_pattern = r'if trade_horizon == (\w+)'
    content = re.sub(
        trade_horizon_pattern,
        r'print(f"DEBUG: Checking trade_horizon == \1")\n            if trade_horizon == \1',
        content
    )
    
    # 6. Write the modified content back to the file
    with open('discord_bot.py', 'w') as file:
        file.write(content)
    
    print("Added enhanced debugging to handle_stop_loss_request method")

if __name__ == "__main__":
    add_debugging()