"""
This script modifies the handle_option_price_request method in discord_bot.py
to use a simpler, more conversational response format when users ask about price changes.
"""

def apply_fix():
    """
    Manually fixes the specific sections with formatting issues in discord_bot.py
    """
    with open('discord_bot.py', 'r') as file:
        lines = file.readlines()
    
    # Find the problematic sections and fix them manually
    in_dollar_change_section = False
    in_percent_change_section = False
    fix_line = False
    
    for i in range(len(lines)):
        # Detect the start of dollar change section
        if "# Calculate target stock price and estimated option price if dollar change specified" in lines[i]:
            in_dollar_change_section = True
            in_percent_change_section = False
        
        # Detect the start of percent change section
        elif "# Calculate target stock price and estimated option price if percentage change specified" in lines[i]:
            in_dollar_change_section = False
            in_percent_change_section = True
        
        # Detect the "Projected Value" field in dollar change section
        if in_dollar_change_section and 'name=f"Projected Value on {target_date.strftime' in lines[i]:
            # Found the field definition, set the flag to begin fixing
            fix_line = True
            
            # Replace the lines with our fixed version for dollar change
            lines[i] = '                                # Set up a conversational response\n'
            lines[i+1] = '                                # Clear any existing fields\n'
            lines[i+2] = '                                embed.clear_fields()\n'
            lines[i+3] = '                                \n'
            lines[i+4] = '                                # Update the title to be more descriptive\n'
            lines[i+5] = '                                embed.title = f"{ticker} {info[\'option_type\'].upper()} ${closest_option[\'strike\']:.2f} Price Projection"\n'
            lines[i+6] = '                                \n'
            lines[i+7] = '                                # Format the expiration date in a more readable format\n'
            lines[i+8] = '                                expiration_date_formatted = datetime.strptime(selected_expiration, "%Y-%m-%d").strftime("%B %d, %Y")\n'
            lines[i+9] = '                                \n'
            lines[i+10] = '                                # Create a conversational description\n'
            lines[i+11] = '                                embed.description = f"Your {ticker} ${closest_option[\'strike\']:.2f} {info[\'option_type\']}s expiring {expiration_date_formatted} would be worth approximately **${estimated_price:.2f}** if the stock went {change_direction} ${abs(price_change):.2f} (to ${target_price:.2f}) by {target_date.strftime(\'%B %d, %Y\')}\\n\\n**Current option price:** ${closest_option[\'lastPrice\']:.2f}"\n'
            lines[i+12] = '                                \n'
            lines[i+13] = '                                # Add detailed projection info\n'
            lines[i+14] = '                                embed.add_field(\n'
            lines[i+15] = '                                    name="Detailed Projection",\n'
            lines[i+16] = '                                    value=f"**Price Change:** {price_diff_sign}${abs(price_diff):.2f} ({price_diff_sign}{price_diff_pct:.1f}%)\\n"\n'
            lines[i+17] = '                                         f"**Total Value ({num_contracts} contract{\'s\' if num_contracts > 1 else \'\'}):** ${total_value:.2f}",\n'
            lines[i+18] = '                                    inline=False\n'
            lines[i+19] = '                                )\n'
            
            # Skip the next few lines that would have been part of the original field
            i += 19
            fix_line = False
            in_dollar_change_section = False
            
        # Detect the "Projected Value" field in percent change section
        elif in_percent_change_section and 'name=f"Projected Value on {target_date.strftime' in lines[i]:
            # Found the field definition, set the flag to begin fixing
            fix_line = True
            
            # Replace the lines with our fixed version for percent change
            lines[i] = '                                # Set up a conversational response\n'
            lines[i+1] = '                                # Clear any existing fields\n'
            lines[i+2] = '                                embed.clear_fields()\n'
            lines[i+3] = '                                \n'
            lines[i+4] = '                                # Update the title to be more descriptive\n'
            lines[i+5] = '                                embed.title = f"{ticker} {info[\'option_type\'].upper()} ${closest_option[\'strike\']:.2f} Price Projection"\n'
            lines[i+6] = '                                \n'
            lines[i+7] = '                                # Format the expiration date in a more readable format\n'
            lines[i+8] = '                                expiration_date_formatted = datetime.strptime(selected_expiration, "%Y-%m-%d").strftime("%B %d, %Y")\n'
            lines[i+9] = '                                \n'
            lines[i+10] = '                                # Create a conversational description\n'
            lines[i+11] = '                                embed.description = f"Your {ticker} ${closest_option[\'strike\']:.2f} {info[\'option_type\']}s expiring {expiration_date_formatted} would be worth approximately **${estimated_price:.2f}** if the stock went {change_direction} {abs(pct_change):.1f}% (to ${target_price:.2f}) by {target_date.strftime(\'%B %d, %Y\')}\\n\\n**Current option price:** ${closest_option[\'lastPrice\']:.2f}"\n'
            lines[i+12] = '                                \n'
            lines[i+13] = '                                # Add detailed projection info\n'
            lines[i+14] = '                                embed.add_field(\n'
            lines[i+15] = '                                    name="Detailed Projection",\n'
            lines[i+16] = '                                    value=f"**Price Change:** {price_diff_sign}${abs(price_diff):.2f} ({price_diff_sign}{price_diff_pct:.1f}%)\\n"\n'
            lines[i+17] = '                                         f"**Total Value ({num_contracts} contract{\'s\' if num_contracts > 1 else \'\'}):** ${total_value:.2f}",\n'
            lines[i+18] = '                                    inline=False\n'
            lines[i+19] = '                                )\n'
            
            # Skip the next few lines that would have been part of the original field
            i += 19
            fix_line = False
            in_percent_change_section = False
    
    # Write the fixed content back to the file
    with open('discord_bot.py', 'w') as file:
        file.writelines(lines)
    
    print("Option price response format has been updated with proper syntax for a more conversational style.")

if __name__ == "__main__":
    apply_fix()