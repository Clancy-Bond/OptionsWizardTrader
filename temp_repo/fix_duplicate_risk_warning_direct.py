"""
A direct, simple fix for the duplicate risk warning in discord_bot.py.
This fix ONLY addresses the duplicate risk warning and doesn't touch anything else.

The problem:
1. There are two "⚠️ RISK WARNING" sections showing at the bottom of responses
2. We need to make sure there's only ONE risk warning at the bottom

The solution:
1. Find all instances where a risk warning is added
2. Add a flag to track if we've already added a risk warning
3. Only add the risk warning if we haven't added one already
"""

def fix_duplicate_risk_warning():
    """
    Direct fix to prevent duplicate risk warnings
    """
    # Read the current file content
    with open("discord_bot.py", "r") as file:
        content = file.read()
    
    # Count how many risk warnings are currently in the code
    risk_warning_count = content.count('name="⚠️ RISK WARNING"')
    print(f"Found {risk_warning_count} risk warning additions in the code")
    
    # The fix is to add a tracking variable at the beginning of the handle_stop_loss_request method
    # This variable will ensure we only add the risk warning once
    
    # Find the beginning of the handle_stop_loss_request method
    method_start = 'async def handle_stop_loss_request(self, message, info):'
    if method_start not in content:
        print("ERROR: Couldn't find the handle_stop_loss_request method!")
        return
    
    # Add the tracking variable after the method definition
    tracking_var = """
        # Track if we've added a risk warning to prevent duplicates
        risk_warning_added = False
"""
    
    # Replace the method start with method start + tracking variable
    content = content.replace(
        method_start,
        method_start + tracking_var
    )
    
    # Now, modify each place where a risk warning is added to check our tracking variable
    check_before_add = """
                    # Only add risk warning if we haven't already added one
                    if not risk_warning_added:
                        embed.add_field(
                            name="⚠️ RISK WARNING",
                            value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                            inline=False
                        )
                        risk_warning_added = True
"""
    
    # Find each risk warning addition and replace it with our conditional version
    risk_pattern = """                    embed.add_field(
                        name="⚠️ RISK WARNING",
                        value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                        inline=False
                    )"""
    
    # Update every risk warning addition with our conditional version
    content = content.replace(risk_pattern, check_before_add)
    
    # Write back to the file
    with open("discord_bot.py", "w") as file:
        file.write(content)
    
    print("Successfully updated discord_bot.py to prevent duplicate risk warnings")
    print("- Added tracking variable: risk_warning_added")
    print("- Modified risk warning additions to check if one was already added")
    print("- Bot will still show exactly one risk warning at the bottom of responses")

if __name__ == "__main__":
    fix_duplicate_risk_warning()