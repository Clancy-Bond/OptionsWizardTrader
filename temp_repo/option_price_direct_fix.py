"""
Direct fix for the string formatting issue in discord_bot.py
"""

def fix_description_strings():
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Replace the problematic dollar change description
    content = content.replace(
        """embed.description = f"Your {ticker} ${closest_option['strike']:.2f} {info['option_type']}s expiring {expiration_date_formatted} would be worth approximately **${estimated_price:.2f}** if the stock went {change_direction} ${abs(price_change):.2f} (to ${target_price:.2f}) by {target_date.strftime('%B %d, %Y')}.

**Current option price:** ${closest_option['lastPrice']:.2f}"""",
        """embed.description = f"Your {ticker} ${closest_option['strike']:.2f} {info['option_type']}s expiring {expiration_date_formatted} would be worth approximately **${estimated_price:.2f}** if the stock went {change_direction} ${abs(price_change):.2f} (to ${target_price:.2f}) by {target_date.strftime('%B %d, %Y')}\\n\\n**Current option price:** ${closest_option['lastPrice']:.2f}\""""
    )
    
    # Replace the problematic percent change description
    content = content.replace(
        """embed.description = f"Your {ticker} ${closest_option['strike']:.2f} {info['option_type']}s expiring {expiration_date_formatted} would be worth approximately **${estimated_price:.2f}** if the stock went {change_direction} {abs(pct_change):.1f}% (to ${target_price:.2f}) by {target_date.strftime('%B %d, %Y')}.

**Current option price:** ${closest_option['lastPrice']:.2f}"""",
        """embed.description = f"Your {ticker} ${closest_option['strike']:.2f} {info['option_type']}s expiring {expiration_date_formatted} would be worth approximately **${estimated_price:.2f}** if the stock went {change_direction} {abs(pct_change):.1f}% (to ${target_price:.2f}) by {target_date.strftime('%B %d, %Y')}\\n\\n**Current option price:** ${closest_option['lastPrice']:.2f}\""""
    )
    
    with open('discord_bot.py', 'w') as file:
        file.write(content)
    
    print("Fixed the string formatting issues in discord_bot.py")

if __name__ == "__main__":
    fix_description_strings()