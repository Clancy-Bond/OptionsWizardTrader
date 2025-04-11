"""
Simplified direct fix by creating a backup and then writing the entire file
with our edits after fixing the string formatting.
"""

import os
import shutil

def apply_simplified_fix():
    # Create a backup first
    shutil.copy('discord_bot.py', 'discord_bot.py.bak')
    
    # Read the original file
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # The most direct way - search and replace the specific problematic sections
    content = content.replace(
        '''                                # Create a conversational description
                                embed.description = f"Your {ticker} ${closest_option['strike']:.2f} {info['option_type']}s expiring {expiration_date_formatted} would be worth approximately **${estimated_price:.2f}** if the stock went {change_direction} ${abs(price_change):.2f} (to ${target_price:.2f}) by {target_date.strftime('%B %d, %Y')}

**Current option price:** ${closest_option['lastPrice']:.2f}"''',
        '''                                # Create a conversational description
                                embed.description = f"Your {ticker} ${closest_option['strike']:.2f} {info['option_type']}s expiring {expiration_date_formatted} would be worth approximately **${estimated_price:.2f}** if the stock went {change_direction} ${abs(price_change):.2f} (to ${target_price:.2f}) by {target_date.strftime('%B %d, %Y')}\\n\\n**Current option price:** ${closest_option['lastPrice']:.2f}"'''
    )
    
    content = content.replace(
        '''                                # Add detailed projection info
                                embed.add_field(
                                    name="Detailed Projection",
                                    value=f"**Price Change:** {price_diff_sign}${abs(price_diff):.2f} ({price_diff_sign}{price_diff_pct:.1f}%)
                                         f"**Total Value ({num_contracts} contract{'s' if num_contracts > 1 else ''}):** ${total_value:.2f}",
                                    inline=False
                                )''',
        '''                                # Add detailed projection info
                                embed.add_field(
                                    name="Detailed Projection",
                                    value=f"**Price Change:** {price_diff_sign}${abs(price_diff):.2f} ({price_diff_sign}{price_diff_pct:.1f}%)\\n"
                                         f"**Total Value ({num_contracts} contract{'s' if num_contracts > 1 else ''}):** ${total_value:.2f}",
                                    inline=False
                                )'''
    )
    
    content = content.replace(
        '''                                # Create a conversational description
                                embed.description = f"Your {ticker} ${closest_option['strike']:.2f} {info['option_type']}s expiring {expiration_date_formatted} would be worth approximately **${estimated_price:.2f}** if the stock went {change_direction} {abs(pct_change):.1f}% (to ${target_price:.2f}) by {target_date.strftime('%B %d, %Y')}

**Current option price:** ${closest_option['lastPrice']:.2f}"''',
        '''                                # Create a conversational description
                                embed.description = f"Your {ticker} ${closest_option['strike']:.2f} {info['option_type']}s expiring {expiration_date_formatted} would be worth approximately **${estimated_price:.2f}** if the stock went {change_direction} {abs(pct_change):.1f}% (to ${target_price:.2f}) by {target_date.strftime('%B %d, %Y')}\\n\\n**Current option price:** ${closest_option['lastPrice']:.2f}"'''
    )
    
    content = content.replace(
        '''                                # Add detailed projection info
                                embed.add_field(
                                    name="Detailed Projection",
                                    value=f"**Price Change:** {price_diff_sign}${abs(price_diff):.2f} ({price_diff_sign}{price_diff_pct:.1f}%)
                                         f"**Total Value ({num_contracts} contract{'s' if num_contracts > 1 else ''}):** ${total_value:.2f}",
                                    inline=False
                                )''',
        '''                                # Add detailed projection info
                                embed.add_field(
                                    name="Detailed Projection",
                                    value=f"**Price Change:** {price_diff_sign}${abs(price_diff):.2f} ({price_diff_sign}{price_diff_pct:.1f}%)\\n"
                                         f"**Total Value ({num_contracts} contract{'s' if num_contracts > 1 else ''}):** ${total_value:.2f}",
                                    inline=False
                                )'''
    )
    
    # Write the fixed content back
    with open('discord_bot.py', 'w') as file:
        file.write(content)
    
    print("Applied fixes to discord_bot.py")

if __name__ == "__main__":
    apply_simplified_fix()