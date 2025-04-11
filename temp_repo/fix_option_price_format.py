"""
This script modifies the handle_option_price_request method in discord_bot.py
to use a simpler, more conversational response format when users ask about price changes.
"""

import re

def apply_fix():
    """
    Updates the dollar_change and percent_change sections to use a simplified,
    conversation-style response format.
    """
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Find the sections for dollar change and percent change
    dollar_change_pattern = re.compile(
        r'(# Calculate target stock price and estimated option price if dollar change specified.*?'
        r'# Add the price projection to the embed\n\s+embed\.add_field\(\n\s+name=f"Projected Value on {target_date\.strftime\(\'%Y-%m-%d\'\)}",\n\s+value=f"\*\*If {target_description}:\*\*\\n"\n\s+f"\*\*Estimated Option Price:\*\* \${estimated_price:.2f} \({price_diff_sign}{price_diff_pct:.1f}%\)\\n"\n\s+f"\*\*Total Value:\*\* \${total_value:.2f}\\n"\n\s+f"\*\*Per Contract:\*\* \${estimated_price \* 100:.2f}",\n\s+inline=False\n\s+\))',
        re.DOTALL
    )
    
    percent_change_pattern = re.compile(
        r'(# Calculate target stock price and estimated option price if percentage change specified.*?'
        r'# Add the price projection to the embed\n\s+embed\.add_field\(\n\s+name=f"Projected Value on {target_date\.strftime\(\'%Y-%m-%d\'\)}",\n\s+value=f"\*\*If {target_description}:\*\*\\n"\n\s+f"\*\*Estimated Option Price:\*\* \${estimated_price:.2f} \({price_diff_sign}{price_diff_pct:.1f}%\)\\n"\n\s+f"\*\*Total Value:\*\* \${total_value:.2f}\\n"\n\s+f"\*\*Per Contract:\*\* \${estimated_price \* 100:.2f}",\n\s+inline=False\n\s+\))',
        re.DOTALL
    )
    
    # Define the replacements
    dollar_change_replacement = (
        '# Calculate target stock price and estimated option price if dollar change specified\n'
        '                        if \'dollar_change\' in info and target_date:\n'
        '                            price_change = info[\'dollar_change\']\n'
        '                            target_price = current_price + price_change\n'
        '                            change_direction = "up" if price_change > 0 else "down"\n'
        '                            target_description = f"stock went {change_direction} ${abs(price_change):.2f} (to ${target_price:.2f})"\n'
        '                            \n'
        '                            # Calculate days between now and target date\n'
        '                            days_to_target = (target_date - datetime.now()).days\n'
        '                            days_to_target = max(0, days_to_target)  # Ensure non-negative\n'
        '                            \n'
        '                            # Calculate option price at target stock price using delta approximation\n'
        '                            if option_greeks and \'delta\' in option_greeks:\n'
        '                                from option_price_calculator import delta_approximation\n'
        '                                \n'
        '                                estimated_price = delta_approximation(\n'
        '                                    closest_option[\'lastPrice\'],\n'
        '                                    current_price,\n'
        '                                    target_price,\n'
        '                                    option_greeks[\'delta\'],\n'
        '                                    info[\'option_type\']\n'
        '                                )\n'
        '                                \n'
        '                                # Factor in theta decay if we have theta\n'
        '                                if \'theta\' in option_greeks:\n'
        '                                    theta_decay = option_greeks[\'theta\'] * days_to_target\n'
        '                                    estimated_price = max(0.01, estimated_price - theta_decay)\n'
        '                                \n'
        '                                # Format the price change\n'
        '                                price_diff = estimated_price - closest_option[\'lastPrice\']\n'
        '                                price_diff_pct = (price_diff / closest_option[\'lastPrice\']) * 100\n'
        '                                price_diff_sign = "+" if price_diff >= 0 else ""\n'
        '                                \n'
        '                                # Calculate total value\n'
        '                                total_value = estimated_price * 100 * num_contracts\n'
        '                                \n'
        '                                # Set up a conversational response\n'
        '                                # Clear any existing fields\n'
        '                                embed.clear_fields()\n'
        '                                \n'
        '                                # Update the title to be more descriptive\n'
        '                                embed.title = f"{ticker} {info[\'option_type\'].upper()} ${closest_option[\'strike\']:.2f} Price Projection"\n'
        '                                \n'
        '                                # Format the expiration date in a more readable format\n'
        '                                expiration_date_formatted = datetime.strptime(selected_expiration, "%Y-%m-%d").strftime("%B %d, %Y")\n'
        '                                \n'
        '                                # Create a conversational description\n'
        '                                embed.description = f"Your {ticker} ${closest_option[\'strike\']:.2f} {info[\'option_type\']}s expiring {expiration_date_formatted} would be worth approximately **${estimated_price:.2f}** if the stock went {change_direction} ${abs(price_change):.2f} (to ${target_price:.2f}) by {target_date.strftime(\'%B %d, %Y\')}.\n\n**Current option price:** ${closest_option[\'lastPrice\']:.2f}"\n'
        '                                \n'
        '                                # Add detailed projection info\n'
        '                                embed.add_field(\n'
        '                                    name="Detailed Projection",\n'
        '                                    value=f"**Price Change:** {price_diff_sign}${abs(price_diff):.2f} ({price_diff_sign}{price_diff_pct:.1f}%)\n"\n'
        '                                         f"**Total Value ({num_contracts} contract{\'s\' if num_contracts > 1 else \'\'}):** ${total_value:.2f}",\n'
        '                                    inline=False\n'
        '                                )'
    )
    
    percent_change_replacement = (
        '# Calculate target stock price and estimated option price if percentage change specified\n'
        '                        elif \'percent_change\' in info and target_date:\n'
        '                            pct_change = info[\'percent_change\']\n'
        '                            target_price = current_price * (1 + pct_change/100)\n'
        '                            change_direction = "up" if pct_change > 0 else "down"\n'
        '                            target_description = f"stock went {change_direction} {abs(pct_change):.1f}% (to ${target_price:.2f})"\n'
        '                            \n'
        '                            # Calculate days between now and target date\n'
        '                            days_to_target = (target_date - datetime.now()).days\n'
        '                            days_to_target = max(0, days_to_target)  # Ensure non-negative\n'
        '                            \n'
        '                            # Calculate option price at target stock price using delta approximation\n'
        '                            if option_greeks and \'delta\' in option_greeks:\n'
        '                                from option_price_calculator import delta_approximation\n'
        '                                \n'
        '                                estimated_price = delta_approximation(\n'
        '                                    closest_option[\'lastPrice\'],\n'
        '                                    current_price,\n'
        '                                    target_price,\n'
        '                                    option_greeks[\'delta\'],\n'
        '                                    info[\'option_type\']\n'
        '                                )\n'
        '                                \n'
        '                                # Factor in theta decay if we have theta\n'
        '                                if \'theta\' in option_greeks:\n'
        '                                    theta_decay = option_greeks[\'theta\'] * days_to_target\n'
        '                                    estimated_price = max(0.01, estimated_price - theta_decay)\n'
        '                                \n'
        '                                # Format the price change\n'
        '                                price_diff = estimated_price - closest_option[\'lastPrice\']\n'
        '                                price_diff_pct = (price_diff / closest_option[\'lastPrice\']) * 100\n'
        '                                price_diff_sign = "+" if price_diff >= 0 else ""\n'
        '                                \n'
        '                                # Calculate total value\n'
        '                                total_value = estimated_price * 100 * num_contracts\n'
        '                                \n'
        '                                # Set up a conversational response\n'
        '                                # Clear any existing fields\n'
        '                                embed.clear_fields()\n'
        '                                \n'
        '                                # Update the title to be more descriptive\n'
        '                                embed.title = f"{ticker} {info[\'option_type\'].upper()} ${closest_option[\'strike\']:.2f} Price Projection"\n'
        '                                \n'
        '                                # Format the expiration date in a more readable format\n'
        '                                expiration_date_formatted = datetime.strptime(selected_expiration, "%Y-%m-%d").strftime("%B %d, %Y")\n'
        '                                \n'
        '                                # Create a conversational description\n'
        '                                embed.description = f"Your {ticker} ${closest_option[\'strike\']:.2f} {info[\'option_type\']}s expiring {expiration_date_formatted} would be worth approximately **${estimated_price:.2f}** if the stock went {change_direction} {abs(pct_change):.1f}% (to ${target_price:.2f}) by {target_date.strftime(\'%B %d, %Y\')}.\n\n**Current option price:** ${closest_option[\'lastPrice\']:.2f}"\n'
        '                                \n'
        '                                # Add detailed projection info\n'
        '                                embed.add_field(\n'
        '                                    name="Detailed Projection",\n'
        '                                    value=f"**Price Change:** {price_diff_sign}${abs(price_diff):.2f} ({price_diff_sign}{price_diff_pct:.1f}%)\n"\n'
        '                                         f"**Total Value ({num_contracts} contract{\'s\' if num_contracts > 1 else \'\'}):** ${total_value:.2f}",\n'
        '                                    inline=False\n'
        '                                )'
    )
    
    # Apply the replacements
    new_content = dollar_change_pattern.sub(dollar_change_replacement, content)
    new_content = percent_change_pattern.sub(percent_change_replacement, new_content)
    
    # Write the updated content back to the file
    with open('discord_bot.py', 'w') as file:
        file.write(new_content)
    
    print("Option price response format has been updated to a more conversational style.")

if __name__ == "__main__":
    apply_fix()