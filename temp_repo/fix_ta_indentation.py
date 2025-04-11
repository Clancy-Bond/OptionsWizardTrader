"""
Fix all indentation issues in technical_analysis.py that were introduced
during the integration of the enhanced ATR-based stop loss system.
"""

import re

def fix_indentation():
    """Fix indentation issues in technical_analysis.py"""
    with open("technical_analysis.py", "r") as file:
        content = file.read()
    
    # Fix indentation in the swing trade section
    content = content.replace(
        """        elif trade_horizon == "swing":
                result["primary"] = swing_recommendation
            
            # Create a completely integrated stop loss message""",
        """        elif trade_horizon == "swing":
                result["primary"] = swing_recommendation
                
                # Create a completely integrated stop loss message"""
    )
    
    # Fix indentation in the longterm section
    content = content.replace(
        """        elif trade_horizon == "longterm":
            result["primary"] = longterm_recommendation
            
            # Create a completely integrated stop loss message""",
        """        elif trade_horizon == "longterm":
                result["primary"] = longterm_recommendation
                
                # Create a completely integrated stop loss message"""
    )
    
    # Fix indentation in the rest of the longterm section
    orig_lines = content.split('\n')
    fixed_lines = []
    in_longterm_section = False
    longterm_end = False
    
    for line in orig_lines:
        if "elif trade_horizon == \"longterm\":" in line:
            in_longterm_section = True
            fixed_lines.append(line)
        elif in_longterm_section and "else:  # unknown trade horizon" in line:
            in_longterm_section = False
            longterm_end = True
            fixed_lines.append(line)
        elif in_longterm_section and not line.strip().startswith("elif") and not line.strip().startswith("#"):
            # Add proper indentation (4 spaces) to the longterm section
            if line.strip() and not line.startswith("                "):
                fixed_lines.append("    " + line)
            else:
                fixed_lines.append(line)
        elif longterm_end and line.strip().startswith("result[\"primary\"]"):
            # Fix indentation for the unknown trade horizon section
            fixed_lines.append("            " + line.lstrip())
            longterm_end = False
        else:
            fixed_lines.append(line)
    
    # Write the fixed content back to the file
    with open("technical_analysis.py", "w") as file:
        file.write('\n'.join(fixed_lines))

if __name__ == "__main__":
    fix_indentation()