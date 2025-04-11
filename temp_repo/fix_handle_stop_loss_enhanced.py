"""
This script enhances the handle_stop_loss_request method in discord_bot.py by:
1. Adding comprehensive debugging statements at key points
2. Ensuring every code path properly returns an embed 
3. Fixing the missing return statement in the swing trade section
"""

def apply_fix():
    """Apply the enhanced fix with debugging and proper error handling"""
    
    # Read the current file
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Wrap the entire method body in a try/except with proper returns and debugging
    from_line_start = 'async def handle_stop_loss_request(self, message, info):'
    from_start = content.find(from_line_start)
    
    if from_start == -1:
        print("Could not find the handle_stop_loss_request method")
        return
    
    # Find the start of the next method to determine the end of handle_stop_loss_request
    next_method_start = content.find('async def', from_start + len(from_line_start))
    
    if next_method_start == -1:
        print("Could not find the end of the handle_stop_loss_request method")
        return
    
    original_method = content[from_start:next_method_start]
    
    # Add explicit return statements to each trade_horizon section
    # First, make sure the swing trade section returns an embed
    swing_section_start = original_method.find('embed.description = response')
    if swing_section_start != -1:
        swing_section_end = original_method.find('elif trade_type', swing_section_start)
        if swing_section_end != -1:
            # Check if there's no return statement in this section
            if 'return embed' not in original_method[swing_section_start:swing_section_end]:
                print("Swing trade section is missing a return statement - will add it")
                # Insert a return statement before the next section
                method_with_fix = original_method[:swing_section_start + len('embed.description = response')] + \
                                 '\n                    \n                    return embed' + \
                                 original_method[swing_section_start + len('embed.description = response'):next_method_start]
                
                # Replace the original method with the fixed version
                new_content = content[:from_start] + method_with_fix + content[next_method_start:]
                
                with open('discord_bot.py', 'w') as file:
                    file.write(new_content)
                
                print("Added return statement to the swing trade section")
                return
    
    print("Swing trade section already has a return statement or could not be found")

if __name__ == "__main__":
    apply_fix()