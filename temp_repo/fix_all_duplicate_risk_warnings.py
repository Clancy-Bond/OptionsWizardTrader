"""
A comprehensive fix for ALL duplicate risk warnings in discord_bot.py.
This script identifies and removes duplicate risk warning additions throughout the file.

The problem:
1. There are multiple places where risk warnings are added in each trade type section
2. Each trade type section adds a risk warning and then does field reordering which adds another one
3. This results in duplicate risk warnings appearing in responses

The solution:
1. Identify all empty embed.add_field calls
2. Remove all redundant risk warning fields, keeping only the ones in the field reordering section
"""

def fix_duplicate_risk_warnings():
    """
    Find and remove all duplicate risk warning field additions
    """
    # Read the current file content
    with open("discord_bot.py", "r") as file:
        lines = file.readlines()
    
    # Process the file line by line and identify blocks to remove
    i = 0
    removed_blocks = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for add_field calls that add a risk warning BEFORE field reordering
        if "embed.add_field(" in line and "name=\"⚠️ RISK WARNING\"" in "".join(lines[i:i+10]):
            # Check if this is BEFORE a field reordering section by looking ahead
            lookAhead = "".join(lines[i:i+50])
            if "# Ensure risk warning is the very last field" in lookAhead and "# Use Discord.py's proper API methods" in lookAhead:
                # This is a duplicate risk warning - find where it ends
                start_idx = i
                end_idx = i
                
                # Find where this add_field call ends
                parenthesis_count = line.count("(") - line.count(")")
                j = i + 1
                while j < len(lines) and parenthesis_count > 0:
                    end_idx = j
                    parenthesis_count += lines[j].count("(") - lines[j].count(")")
                    j += 1
                
                # Remove this block
                print(f"Removing duplicate risk warning at lines {start_idx+1}-{end_idx+1}")
                del lines[start_idx:end_idx+1]
                removed_blocks += 1
                
                # Don't increment i since we've deleted lines
                continue
        
        # Look for redundant field reordering sections
        elif "# Remove any existing risk warning by adding fields" in line:
            # This is a redundant field reordering section - find where it starts and ends
            start_idx = i
            
            # Find where this section ends - usually ends with re-adding the risk warning
            j = i
            while j < len(lines) and "embed.add_field(" not in lines[j] or "name=\"⚠️ RISK WARNING\"" not in "".join(lines[j:j+10]):
                j += 1
            
            # If we found the end, remove this block
            if j < len(lines):
                # Find where the add_field call ends
                end_idx = j
                parenthesis_count = lines[j].count("(") - lines[j].count(")")
                k = j + 1
                while k < len(lines) and parenthesis_count > 0:
                    end_idx = k
                    parenthesis_count += lines[k].count("(") - lines[k].count(")")
                    k += 1
                
                print(f"Removing redundant field reordering section at lines {start_idx+1}-{end_idx+1}")
                del lines[start_idx:end_idx+1]
                removed_blocks += 1
                
                # Don't increment i since we've deleted lines
                continue
        
        i += 1
    
    # Write the modified content back to the file
    with open("discord_bot.py", "w") as file:
        file.writelines(lines)
    
    print(f"Successfully removed {removed_blocks} duplicate risk warning blocks from discord_bot.py")

if __name__ == "__main__":
    fix_duplicate_risk_warnings()