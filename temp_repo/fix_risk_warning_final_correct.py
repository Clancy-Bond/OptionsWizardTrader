"""
This is the final, correct fix for the risk warning placement in discord_bot.py.
Instead of trying to modify the fields property (which doesn't have a setter),
we'll completely rewrite the stop_loss_request method to add the risk warning at the end.
"""

def fix_risk_warning_placement():
    """
    Update discord_bot.py to ensure risk warning is the absolute last field
    by rewriting the handle_stop_loss_request method.
    """
    with open("discord_bot.py", "r") as file:
        content = file.read()
    
    # Locate the handle_stop_loss_request method
    import re
    
    # Find the start of the method
    method_start_pattern = r"async def handle_stop_loss_request\(self, message, info\):"
    method_start_match = re.search(method_start_pattern, content)
    
    if not method_start_match:
        print("Error: Could not find the handle_stop_loss_request method.")
        return
    
    method_start_pos = method_start_match.start()
    
    # Find the end of the method (next async def or end of file)
    next_method_pattern = r"async def \w+"
    next_method_match = re.search(next_method_pattern, content[method_start_pos + 1:])
    
    if next_method_match:
        method_end_pos = method_start_pos + 1 + next_method_match.start()
    else:
        # If no next method, look for the end of the class
        end_class_pattern = r"# End of OptionsBot class"
        end_class_match = re.search(end_class_pattern, content[method_start_pos:])
        if end_class_match:
            method_end_pos = method_start_pos + end_class_match.start()
        else:
            print("Error: Could not determine the end of the handle_stop_loss_request method.")
            return
    
    # Extract the current method code
    current_method = content[method_start_pos:method_end_pos]
    
    # Create the updated method with risk warning added only at the end
    updated_method = current_method
    
    # Remove all existing risk warning field additions to avoid duplicates
    risk_warning_pattern = r"# Add Risk Warning.*?embed\.add_field\(\s*name=\"⚠️ RISK WARNING\".*?inline=False\s*\)"
    updated_method = re.sub(risk_warning_pattern, "# Risk warning will be added at the end", updated_method, flags=re.DOTALL)
    
    # Also remove any risk warning moved to bottom comments
    updated_method = updated_method.replace("# Risk warning moved to bottom", "# Risk warning will be added at the end")
    
    # Find all return statements in the method and ensure they don't have a risk warning
    # right before them (to avoid duplicates)
    return_pattern = r"(\s+)return embed(\s*)"
    
    # Function to add risk warning before return statements
    def add_risk_warning_before_return(match):
        indent = match.group(1)
        # Add the risk warning right before the return
        return f"{indent}# Add Risk Warning at the very end\n{indent}embed.add_field(\n{indent}    name=\"⚠️ RISK WARNING\",\n{indent}    value=\"Stop losses do not guarantee execution at the specified price in fast-moving markets.\",\n{indent}    inline=False\n{indent})\n{indent}return embed{match.group(2)}"
    
    updated_method = re.sub(return_pattern, add_risk_warning_before_return, updated_method)
    
    # Replace the original method with the updated one
    updated_content = content[:method_start_pos] + updated_method + content[method_end_pos:]
    
    # Write the updated content back to the file
    with open("discord_bot.py", "w") as file:
        file.write(updated_content)
    
    print("✅ Successfully fixed risk warning placement to ensure it always appears as the last field")

if __name__ == "__main__":
    fix_risk_warning_placement()