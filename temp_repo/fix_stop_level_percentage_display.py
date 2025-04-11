"""
Fix script to ensure the stock price stop level shows the percentage difference from current price.

This addresses the issue where the stop loss level is shown without the percentage difference,
which should display dynamically based on days to expiration.
"""

def fix_stop_level_percentage_display():
    """Fix the missing percentage display for stock price stop level in Discord responses."""
    
    # Read the discord_bot.py file
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Find the line in main stop loss display (line 1410) and update it
    line_1410 = 'value=f"• Current Stock Price: ${current_price:.2f}\n• Current Option Price: ${option_price:.2f}\n• Stock Price Stop Level: ${stop_loss:.2f}\n• Option Price at Stop Recommendation Level: ${option_stop_price:.2f} (a {abs(loss_percentage):.1f}% loss)",'
    
    updated_line_1410 = 'value=f"• Current Stock Price: ${current_price:.2f}\n• Current Option Price: ${option_price:.2f}\n• Stock Price Stop Level: ${stop_loss:.2f} ({abs((stop_loss - current_price) / current_price * 100):.1f}% {\'below\' if option_type.lower() == \'call\' else \'above\'} current price)\n• Option Price at Stop Recommendation Level: ${option_stop_price:.2f} (a {abs(loss_percentage):.1f}% loss)",'
    
    # Apply the update
    updated_content = content.replace(line_1410, updated_line_1410)
    
    # Check if we made any changes for the main section
    if updated_content == content:
        print("Could not find the main target line to replace. Manual check needed.")
        return False
    
    # Write the updated content back to the file
    with open('discord_bot.py', 'w') as file:
        file.write(updated_content)
    
    print("Successfully updated stop level percentage display.")
    return True

if __name__ == "__main__":
    fix_stop_level_percentage_display()