"""
This script will fix the display formatting for the theta decay information
in the Discord bot to match the screenshot format.
"""

import re

def fix_theta_decay_display():
    """
    Updates the discord_bot.py file to format the theta decay warning display correctly.
    """
    with open('discord_bot.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Define the replacement pattern
    old_pattern = r'# Add theta decay warning as a field at the bottom if available\s+if theta_decay_warning:\s+embed\.add_field\(\s+name="⚠️ THETA DECAY PROJECTION ⚠️",\s+value=theta_decay_warning\.replace\("⚠️ \*\*THETA DECAY PROJECTION TO EXPIRY", ""\)\.replace\("⚠️", ""\),\s+inline=False\s+\)'
    
    new_code = '''# Add theta decay warning as a field at the bottom if available
                    if theta_decay_warning:
                        # Extract date if available
                        date_part = ""
                        cleaned_text = theta_decay_warning
                        
                        if "EXPIRY (" in cleaned_text and ")" in cleaned_text:
                            start_idx = cleaned_text.find("EXPIRY (") + 7
                            end_idx = cleaned_text.find(")", start_idx)
                            if start_idx > 0 and end_idx > start_idx:
                                date_part = cleaned_text[start_idx:end_idx+1]
                        
                        # Clean up the text by removing the header 
                        cleaned_text = cleaned_text.replace("⚠️ **THETA DECAY PROJECTION TO EXPIRY", "").replace("**", "")
                        
                        # Remove closing warning emoji if present
                        if "** ⚠️" in cleaned_text:
                            cleaned_text = cleaned_text.replace("** ⚠️", "")
                        elif " ⚠️" in cleaned_text:
                            cleaned_text = cleaned_text.replace(" ⚠️", "")
                        
                        if date_part:
                            cleaned_text = cleaned_text.replace(date_part, "")
                        
                        # Formatting the value to match the screenshot
                        formatted_value = f"⚠️ THETA DECAY PROJECTION ⚠️\\n{date_part}\\nYour option is projected to decay over the next 5 weeks:\\n{cleaned_text}"
                        
                        # Clean up any double newlines or extra spaces
                        formatted_value = formatted_value.replace("\\n\\n\\n", "\\n\\n").strip()
                        
                        embed.add_field(
                            name="⚠️ THETA DECAY PROJECTION ⚠️",
                            value=formatted_value,
                            inline=False
                        )'''
                        
    # Replace all occurrences
    updated_content = re.sub(old_pattern, new_code, content)
    
    # Check if any replacements were made
    if content == updated_content:
        print("No replacements made. Trying a more direct approach.")
        
        # Try a more direct approach
        theta_decay_sections = []
        
        for match in re.finditer(r'# Add theta decay warning as a field at the bottom if available.*?inline=False\s+\)', content, re.DOTALL):
            theta_decay_sections.append(match.group(0))
        
        if not theta_decay_sections:
            print("No sections found that match the pattern.")
            return
        
        print(f"Found {len(theta_decay_sections)} sections to replace.")
        
        # Replace each section individually
        for section in theta_decay_sections:
            updated_content = content.replace(section, new_code)
            
            # Check if replacement worked
            if content != updated_content:
                content = updated_content
                print("Replacement successful.")
            else:
                print(f"Failed to replace section: {section[:100]}...")
    
    # Write the updated content back to the file
    with open('discord_bot.py', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("Theta decay display formatting has been updated.")

if __name__ == "__main__":
    fix_theta_decay_display()