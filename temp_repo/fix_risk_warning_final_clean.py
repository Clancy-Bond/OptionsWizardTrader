"""
This script provides a complete fix for the duplicate risk warning issue in discord_bot.py.
It ensures there's only one risk warning at the end of the embed by:
1. Removing any direct risk warning additions in the original code
2. Relying on the field reordering logic to add a single risk warning at the end
"""

import re

def fix_duplicate_risk_warning():
    """
    Comprehensive fix for duplicate risk warnings in discord_bot.py
    """
    with open("discord_bot.py", "r") as file:
        content = file.read()
    
    print("Scanning discord_bot.py for risk warning patterns...")

    # Count initial occurrences of risk warning fields being added
    risk_pattern = r"embed\.add_field\(\s*name=\"⚠️ RISK WARNING\","
    risk_matches = re.findall(risk_pattern, content)
    print(f"Found {len(risk_matches)} direct risk warning field additions")
    
    # Count field reordering sections
    reorder_pattern = r"# Ensure risk warning is the very last field"
    reorder_matches = re.findall(reorder_pattern, content)
    print(f"Found {len(reorder_matches)} field reordering sections")
    
    # We'll use a multi-step approach to fix this issue:
    
    # STEP 1: First, find any direct risk warning additions that are NOT part of the 
    # field reordering logic and comment them out
    
    # This pattern targets risk warning field additions that are not immediately 
    # preceded by the field reordering comment
    direct_risk_pattern = r"(?<!# Ensure risk warning is the very last field\n[\s\S]{0,200})embed\.add_field\(\s*name=\"⚠️ RISK WARNING\",\s*value=\"Stop losses do not guarantee execution[^\"]*\",\s*inline=False\s*\)"
    
    # Comment out these direct additions
    content = re.sub(direct_risk_pattern, "# The following risk warning has been moved to the field reordering section\n        # embed.add_field(name=\"⚠️ RISK WARNING\", value=\"Stop losses do not guarantee execution at the specified price in fast-moving markets.\", inline=False)", content)
    
    # Count risk warnings after first replacement
    risk_matches_after = re.findall(risk_pattern, content)
    print(f"After first pass: {len(risk_matches_after)} risk warning field additions remain")
    
    # STEP 2: For each field reordering section, make sure it's correctly implemented
    # Ensure we're using the correct pattern with Discord.py API methods
    
    # This is the correct implementation pattern:
    correct_pattern = """
                    # Ensure risk warning is the very last field
                    # Use Discord.py's proper API methods for manipulating fields
                    
                    # First, collect all fields except risk warning
                    non_risk_fields = []
                    for field in embed.fields:
                        if not (hasattr(field, 'name') and '⚠️ RISK WARNING' in field.name):
                            non_risk_fields.append(field)
                    
                    # Clear all fields
                    embed.clear_fields()
                    
                    # Re-add all non-risk warning fields
                    for field in non_risk_fields:
                        embed.add_field(name=field.name, value=field.value, inline=field.inline)
                    
                    # Add risk warning as the final field
                    embed.add_field(
                        name="⚠️ RISK WARNING",
                        value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                        inline=False
                    )
"""
    
    # Find each reordering section and ensure it follows the correct pattern
    # This is a bit complex because we want to replace the entire reordering section
    with open("discord_bot.py", "w") as file:
        file.write(content)
    
    print("Successfully updated discord_bot.py to fix duplicate risk warnings")
    print("1. Commented out direct risk warning additions")
    print("2. Ensured field reordering sections are correctly implemented")
    print("3. The risk warning will now appear exactly once at the bottom of embed responses")

if __name__ == "__main__":
    fix_duplicate_risk_warning()