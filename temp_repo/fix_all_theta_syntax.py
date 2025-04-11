"""
A comprehensive fix for all theta decay formatting issues in discord_bot.py
"""

def fix_all_theta_syntax():
    """
    Completely rewrites all the theta decay sections to ensure proper formatting
    and no syntax errors.
    """
    with open('discord_bot.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find all occurrences of the theta decay section
    theta_sections_start = '# Add theta decay warning as a field at the bottom if available'
    theta_sections_end = 'inline=False'
    
    # Split the file by the theta sections
    parts = content.split(theta_sections_start)
    
    if len(parts) == 1:
        print("No theta sections found!")
        return
    
    # Keep the beginning of the file
    new_content = parts[0]
    
    # For each section, replace with the corrected version
    for i in range(1, len(parts)):
        # Find the end of the current theta section
        end_idx = parts[i].find(theta_sections_end)
        if end_idx == -1:
            # If we can't find the end, just append the part as is
            new_content += theta_sections_start + parts[i]
            continue
            
        # Get the part after the section
        after_section = parts[i][end_idx + len(theta_sections_end):]
        
        # Insert the corrected theta section
        new_content += '''# Add theta decay warning as a field at the bottom if available
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
                        )''' + after_section
    
    # Write the updated content back to the file
    with open('discord_bot.py', 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("Fixed all theta decay sections in discord_bot.py")

if __name__ == "__main__":
    fix_all_theta_syntax()