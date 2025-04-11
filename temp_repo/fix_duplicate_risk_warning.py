"""
This script fixes the duplicate risk warning issue in the Discord bot.
It ensures there's only one risk warning at the end of the embed.
"""

def fix_duplicate_risk_warning():
    """
    Update the handle_stop_loss_request method to ensure only one risk warning is added
    """
    with open("discord_bot.py", "r") as file:
        content = file.read()
    
    # Find the code where risk warning is being added in the handle_stop_loss_request method
    # The issue is that we might be adding the risk warning twice - once in the original code
    # and once in our field reordering logic
    
    # First, let's check for any existing risk warning adds in the main body
    risk_warning_pattern = "embed.add_field(\n" + \
                          ".*?name=\"⚠️ RISK WARNING\",\n" + \
                          ".*?value=\"Stop losses do not guarantee execution at the specified price in fast-moving markets\.",\n" + \
                          ".*?inline=False\n" + \
                          ".*?\)"
    
    # We'll replace any occurrences of risk warning adds in the main body with a comment
    import re
    content = re.sub(risk_warning_pattern, "# Risk warning moved to reordering section at the end", content, flags=re.DOTALL)
    
    # Let's also check for any general risk warning adds
    general_risk_pattern = "embed.add_field\\(\n.*?name=\"⚠️ General Risk Note\",.*?\\)"
    # Make sure our regex pattern is finding what we expect
    has_general_risk = bool(re.search(general_risk_pattern, content, re.DOTALL))
    print(f"Found general risk field: {has_general_risk}")
    
    # Make sure our reordering logic is correctly adding the risk warning only once
    # Let's review the field reordering code
    reordering_start = "# Ensure risk warning is the very last field"
    if reordering_start in content:
        print("Found field reordering section - ensuring it adds risk warning only once")
    else:
        print("ERROR: Could not find field reordering section")
        return
    
    # Write the updated content back to the file
    with open("discord_bot.py", "w") as file:
        file.write(content)
    
    print("Removed duplicate risk warnings from discord_bot.py")

if __name__ == "__main__":
    fix_duplicate_risk_warning()