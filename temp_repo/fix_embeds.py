"""
This script fixes all the Discord.Embed and add_field instances that are missing closing parentheses
"""

def fix_all_embeds():
    """
    Fix Discord.Embed constructor calls and add_field calls missing closing parentheses
    """
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Fix embed declarations
    embed_patterns = [
        (
            "error_embed = discord.Embed(\n"
            "                    title=f\"No Options Available\",\n"
            "                    description=f\"No options data found for {ticker}.\",\n"
            "                    color=0xFF0000  # Red for errors\n"
            "                error_embed.set_footer",
            "error_embed = discord.Embed(\n"
            "                    title=f\"No Options Available\",\n"
            "                    description=f\"No options data found for {ticker}.\",\n"
            "                    color=0xFF0000  # Red for errors\n"
            "                )\n"
            "                error_embed.set_footer"
        ),
        (
            "options_embed = discord.Embed(\n"
            "                title=f\"📈 Options Available for {ticker}\",\n"
            "                description=f\"**Current Stock Price:** ${current_price:.2f}\",\n"
            "                color=0x1ABC9C  # Teal for brand consistency\n"
            "            \n"
            "            # Create a list",
            "options_embed = discord.Embed(\n"
            "                title=f\"📈 Options Available for {ticker}\",\n"
            "                description=f\"**Current Stock Price:** ${current_price:.2f}\",\n"
            "                color=0x1ABC9C  # Teal for brand consistency\n"
            "            )\n"
            "            \n"
            "            # Create a list"
        ),
        (
            "options_embed.add_field(\n"
            "                name=\"Available Expiration Dates\",\n"
            "                value=expiry_text,\n"
            "                inline=False\n"
            "            \n"
            "            # For the nearest",
            "options_embed.add_field(\n"
            "                name=\"Available Expiration Dates\",\n"
            "                value=expiry_text,\n"
            "                inline=False\n"
            "            )\n"
            "            \n"
            "            # For the nearest"
        ),
        (
            "options_embed.add_field(\n"
            "                    name=f\"Sample Calls for {nearest_expiry}\",\n"
            "                    value=calls_text,\n"
            "                    inline=False\n"
            "                \n"
            "                options_embed.add_field",
            "options_embed.add_field(\n"
            "                    name=f\"Sample Calls for {nearest_expiry}\",\n"
            "                    value=calls_text,\n"
            "                    inline=False\n"
            "                )\n"
            "                \n"
            "                options_embed.add_field"
        ),
        (
            "options_embed.add_field(\n"
            "                    name=f\"Sample Puts for {nearest_expiry}\",\n"
            "                    value=puts_text,\n"
            "                    inline=False\n"
            "            \n"
            "            # Add",
            "options_embed.add_field(\n"
            "                    name=f\"Sample Puts for {nearest_expiry}\",\n"
            "                    value=puts_text,\n"
            "                    inline=False\n"
            "            )\n"
            "            \n"
            "            # Add"
        ),
        (
            "error_embed = discord.Embed(\n"
            "                title=f\"Error Getting Options Data for {ticker}\",\n"
            "                description=f\"Sorry, I encountered an error: {str(e)}\",\n"
            "                color=0xFF0000  # Red for errors\n"
            "            \n"
            "            error_embed.add_field",
            "error_embed = discord.Embed(\n"
            "                title=f\"Error Getting Options Data for {ticker}\",\n"
            "                description=f\"Sorry, I encountered an error: {str(e)}\",\n"
            "                color=0xFF0000  # Red for errors\n"
            "            )\n"
            "            \n"
            "            error_embed.add_field"
        ),
        (
            "error_embed.add_field(\n"
            "                name=\"Troubleshooting\",\n"
            "                value=\"• Check that the ticker symbol is correct\\n\"\n"
            "                      \"• Verify that options are available for this stock\\n\"\n"
            "                      \"• Try again in a few moments\",\n"
            "                inline=False\n"
            "            \n"
            "            error_embed.set_footer",
            "error_embed.add_field(\n"
            "                name=\"Troubleshooting\",\n"
            "                value=\"• Check that the ticker symbol is correct\\n\"\n"
            "                      \"• Verify that options are available for this stock\\n\"\n"
            "                      \"• Try again in a few moments\",\n"
            "                inline=False\n"
            "            )\n"
            "            \n"
            "            error_embed.set_footer"
        ),
        (
            "embed = discord.Embed(\n"
            "                title=f\"🔍 Unusual Options Activity: {ticker.upper()}\",\n"
            "                description=activity_summary,\n"
            "                color=embed_color\n"
            "            \n"
            "            # Add footer",
            "embed = discord.Embed(\n"
            "                title=f\"🔍 Unusual Options Activity: {ticker.upper()}\",\n"
            "                description=activity_summary,\n"
            "                color=embed_color\n"
            "            )\n"
            "            \n"
            "            # Add footer"
        ),
        # Fix for missing closed parenthesis in strikes list
        (
            "strikes = sorted(list(set(calls['strike'].tolist())\n"
            "                \n"
            "                # Find",
            "strikes = sorted(list(set(calls['strike'].tolist())))\n"
            "                \n"
            "                # Find"
        ),
        # Fix for missing closed parenthesis in closest_strike_idx
        (
            "closest_strike_idx = min(range(len(strikes), \n"
            "                                      key=lambda i: abs(strikes[i] - current_price)\n"
            "                \n"
            "                # Show",
            "closest_strike_idx = min(range(len(strikes)), \n"
            "                                      key=lambda i: abs(strikes[i] - current_price))\n"
            "                \n"
            "                # Show"
        )
    ]
    
    # Apply all the fixes
    for old, new in embed_patterns:
        content = content.replace(old, new)
    
    # Write back the fixed content
    with open('discord_bot.py', 'w') as file:
        file.write(content)
    
    print("Fixed all missing parentheses for Discord.Embed and add_field calls in discord_bot.py")

if __name__ == "__main__":
    fix_all_embeds()