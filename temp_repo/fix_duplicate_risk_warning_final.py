"""
A direct, focused fix for the duplicate risk warning issue in discord_bot.py.
This script specifically targets the exact issue causing duplicate risk warnings.

The problem:
1. In handle_stop_loss_request, there are two add_field calls that are both adding risk warnings
2. The first one at lines ~1933-1961 has the content commented out but the add_field() call is still active
3. This creates an empty field followed by the actual risk warning field

The solution:
1. Completely remove the first, empty add_field() call
2. Keep only the proper risk warning add_field() call at the end
"""

def fix_duplicate_risk_warning():
    """
    Direct fix to remove the empty add_field call that's causing the duplicate risk warning
    """
    # Read the current file content
    with open("discord_bot.py", "r") as file:
        lines = file.readlines()
    
    # Find the problematic section (empty add_field that needs to be removed)
    empty_field_start = None
    empty_field_end = None
    
    # Find the section with comments about removed duplicate
    for i, line in enumerate(lines):
        if "REMOVED DUPLICATE:" in line and "⚠️ RISK WARNING" in line:
            # Found the starting point of the empty add_field
            # Now backtrack to find the 'embed.add_field(' line
            for j in range(i-1, max(0, i-20), -1):
                if "embed.add_field(" in lines[j]:
                    empty_field_start = j
                    break
            
            # Now find the closing parenthesis for this add_field call
            if empty_field_start is not None:
                for j in range(i+1, min(len(lines), i+30)):
                    if "))" in lines[j] or ") )" in lines[j]:  # End of the method
                        break
                    if ")" in lines[j] and lines[j].strip() == ")":
                        empty_field_end = j
                        break
            
            # Only need to find the first occurrence
            break
    
    if empty_field_start is not None and empty_field_end is not None:
        print(f"Found empty add_field call at lines {empty_field_start+1}-{empty_field_end+1}")
        
        # Remove the empty add_field call
        del lines[empty_field_start:empty_field_end+1]
        
        # Write the modified content back to the file
        with open("discord_bot.py", "w") as file:
            file.writelines(lines)
        
        print("Successfully removed the empty add_field call that was causing duplicate risk warnings")
    else:
        print("Could not find the empty add_field call. Please check the file manually.")

if __name__ == "__main__":
    fix_duplicate_risk_warning()