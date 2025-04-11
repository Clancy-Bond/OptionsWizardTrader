"""
This script provides a simpler fix for the duplicate risk warning issue in discord_bot.py.
It ensures there's only one risk warning at the end of the embed by only keeping
the risk warnings that appear in field reordering sections.
"""

import re

def fix_duplicate_risk_warning():
    """
    Simple fix for duplicate risk warnings in discord_bot.py
    """
    with open("discord_bot.py", "r") as file:
        lines = file.readlines()
    
    print("Scanning discord_bot.py for risk warning patterns...")
    
    # Keep track of which lines to keep
    keep_lines = []
    skip_risk_warning = False
    in_field_reordering = False
    skipped_count = 0
    
    for line in lines:
        # Check if we're entering a field reordering section
        if "# Ensure risk warning is the very last field" in line:
            in_field_reordering = True
        
        # Check if we have a risk warning field addition
        if 'name="⚠️ RISK WARNING"' in line:
            # Keep it if it's in a field reordering section
            if in_field_reordering:
                keep_lines.append(line)
            else:
                # Otherwise comment it out
                skipped_count += 1
                keep_lines.append(f"# REMOVED DUPLICATE: {line}")
                skip_risk_warning = True
        elif skip_risk_warning and ('value="Stop losses do not guarantee' in line or 'inline=False' in line):
            # This is part of the risk warning field addition we're skipping
            keep_lines.append(f"# REMOVED DUPLICATE: {line}")
        else:
            # This is not a risk warning line, just include it
            keep_lines.append(line)
            # Reset our skip flag if we see a closing parenthesis
            if skip_risk_warning and ')' in line:
                skip_risk_warning = False

        # Check if we're exiting a field reordering section (after return or at least 10 lines after)
        if in_field_reordering and "return" in line:
            in_field_reordering = False
    
    # Write the updated content back to the file
    with open("discord_bot.py", "w") as file:
        file.writelines(keep_lines)
    
    print(f"Successfully removed {skipped_count} duplicate risk warning fields from discord_bot.py")
    print("The risk warning will now appear exactly once at the bottom of embed responses")

if __name__ == "__main__":
    fix_duplicate_risk_warning()