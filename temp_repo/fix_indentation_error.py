"""
Fix the indentation errors in the technical_analysis.py file 
that were introduced by the dynamic stop loss buffer implementation.
"""

def fix_indentation_errors():
    """
    Fix indentation errors in the technical_analysis.py file.
    """
    # Read the current file
    with open('technical_analysis.py', 'r') as file:
        lines = file.readlines()
    
    fixed_lines = []
    in_fix_section = False
    
    for line in lines:
        # Check for problematic indentation in swing trade call section
        if "# Add a buffer based on ATR (less tight than scalp" in line:
            in_fix_section = True
            fixed_lines.append(line)
        elif in_fix_section and "# Calculate dynamic buffer based on days to expiration" in line:
            # This line is correctly indented
            fixed_lines.append(line)
        elif in_fix_section and "min_percentage = 0.95  # Default 5% max buffer" in line:
            # This line has extra indentation - remove one level
            fixed_lines.append("                min_percentage = 0.95  # Default 5% max buffer\n")
        elif in_fix_section and "buffer_factor = 0.5    # Default ATR factor" in line:
            # This line has extra indentation - remove one level
            fixed_lines.append("                buffer_factor = 0.5    # Default ATR factor\n")
            in_fix_section = False
        elif "# Adjust buffer based on days to expiration if available" in line:
            # Just make sure this line is properly indented in all sections
            if "                    # Adjust buffer" in line:
                # This is in the swing call section and has one too many indentation levels
                fixed_lines.append("                # Adjust buffer based on days to expiration if available\n")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Write the fixed content back to the file
    with open('technical_analysis.py', 'w') as file:
        file.writelines(fixed_lines)

    # Now do a more precise fix for all the sections with systematic checking
    with open('technical_analysis.py', 'r') as file:
        content = file.read()
    
    # Fix the CALL option in SWING trade section - this is where the error was detected
    content = content.replace(
        """                # Add a buffer based on ATR (less tight than scalp, but still respects recent price action)
                # Calculate dynamic buffer based on days to expiration
                    min_percentage = 0.95  # Default 5% max buffer
                    buffer_factor = 0.5    # Default ATR factor
                    
                    # Adjust buffer based on days to expiration if available""",
        
        """                # Add a buffer based on ATR (less tight than scalp, but still respects recent price action)
                # Calculate dynamic buffer based on days to expiration
                min_percentage = 0.95  # Default 5% max buffer
                buffer_factor = 0.5    # Default ATR factor
                
                # Adjust buffer based on days to expiration if available"""
    )
    
    # Write the fixed content back to the file
    with open('technical_analysis.py', 'w') as file:
        file.write(content)
    
    print("Fixed indentation errors in technical_analysis.py")

if __name__ == "__main__":
    fix_indentation_errors()