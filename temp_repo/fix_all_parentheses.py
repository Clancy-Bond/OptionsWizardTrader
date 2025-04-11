"""
This script fixes all the missing closing parentheses in the discord_bot.py file.
It's more aggressive than the previous script and will fix all instances of missing parentheses.
"""

def fix_all_parentheses():
    """
    Identify all function calls that are missing closing parentheses and fix them.
    Also fix any add_field calls that are missing closing parentheses.
    """
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Check and fix for the specific missing parenthesis in calculate_theta_decay calls
    missing_patterns = [
        (
            "theta_decay = calculate_theta_decay(\n"
            "                                    current_option_price=current_option_price,\n"
            "                                    theta=option_greeks['theta'],\n"
            "                                    days_ahead=5,\n"
            "                                    hours_ahead=0\n"
            "                                \n"
            "                                # Save the warning",
            "theta_decay = calculate_theta_decay(\n"
            "                                    current_option_price=current_option_price,\n"
            "                                    theta=option_greeks['theta'],\n"
            "                                    days_ahead=5,\n"
            "                                    hours_ahead=0\n"
            "                                )\n"
            "                                \n"
            "                                # Save the warning"
        ),
        (
            "theta_decay = calculate_theta_decay(\n"
            "                                    current_option_price=current_option_price,\n"
            "                                    theta=option_greeks['theta'],\n"
            "                                    days_ahead=2,\n"
            "                                    hours_ahead=0\n"
            "                                \n"
            "                                # Store warning",
            "theta_decay = calculate_theta_decay(\n"
            "                                    current_option_price=current_option_price,\n"
            "                                    theta=option_greeks['theta'],\n"
            "                                    days_ahead=2,\n"
            "                                    hours_ahead=0\n"
            "                                )\n"
            "                                \n"
            "                                # Store warning"
        ),
        (
            "theta_decay = calculate_expiry_theta_decay(\n"
            "                                current_option_price=current_option_price,\n"
            "                                theta=option_greeks['theta'],\n"
            "                                expiration_date=info['expiration'],\n"
            "                                max_days=5,  # Show up to 5 days for general options\n"
            "                                interval=1   # Daily intervals for general options\n"
            "                            \n"
            "                            # Store warning",
            "theta_decay = calculate_expiry_theta_decay(\n"
            "                                current_option_price=current_option_price,\n"
            "                                theta=option_greeks['theta'],\n"
            "                                expiration_date=info['expiration'],\n"
            "                                max_days=5,  # Show up to 5 days for general options\n"
            "                                interval=1   # Daily intervals for general options\n"
            "                            )\n"
            "                            \n"
            "                            # Store warning"
        ),
        (
            "embed.add_field(\n"
            "                        name=\"⚠️ General Risk Note\",\n"
            "                        value=\"Options typically show 2-3x leverage compared to stocks. Use proper position sizing to manage risk with larger percentage swings. Adjust stop losses as time decay impacts option pricing.\",\n"
            "                        inline=False\n"
            "                    \n"
            "                    # Add theta decay warning",
            "embed.add_field(\n"
            "                        name=\"⚠️ General Risk Note\",\n"
            "                        value=\"Options typically show 2-3x leverage compared to stocks. Use proper position sizing to manage risk with larger percentage swings. Adjust stop losses as time decay impacts option pricing.\",\n"
            "                        inline=False\n"
            "                    )\n"
            "                    \n"
            "                    # Add theta decay warning"
        ),
        (
            "embed.add_field(\n"
            "                            name=\"⚠️ THETA DECAY PROJECTION ⚠️\",\n"
            "                            value=formatted_value,\n"
            "                            inline=False\n"
            "                    \n"
            "                    # Add footer",
            "embed.add_field(\n"
            "                            name=\"⚠️ THETA DECAY PROJECTION ⚠️\",\n"
            "                            value=formatted_value,\n"
            "                            inline=False\n"
            "                    )\n"
            "                    \n"
            "                    # Add footer"
        )
    ]
    
    # Fix embedded errors
    for pattern, replacement in missing_patterns:
        content = content.replace(pattern, replacement)
    
    # Also fix single-line errors with add_field
    content = content.replace(
        "                    inline=False\n                \n                # Add footer",
        "                    inline=False\n                )\n                \n                # Add footer"
    )
    
    # Missing parenthesis in error embed
    content = content.replace(
        "                    color=0xFF0000  # Red color for error\n                return error_embed",
        "                    color=0xFF0000  # Red color for error\n                )\n                return error_embed"
    )
    
    # Missing parenthesis in mock_embed.set_footer
    content = content.replace(
        "                mock_embed.set_footer(text=\"Data as of \" + datetime.now().strftime(\"%Y-%m-%d %H:%M\")\n",
        "                mock_embed.set_footer(text=\"Data as of \" + datetime.now().strftime(\"%Y-%m-%d %H:%M\"))\n"
    )
    
    # Missing parenthesis in error_message
    content = content.replace(
        "                    f\"Please try again with a different ticker or option details.\"\n",
        "                    f\"Please try again with a different ticker or option details.\")\n"
    )
    
    # Missing parenthesis in mock_embed
    content = content.replace(
        "                    color=0xFF0000\n",
        "                    color=0xFF0000)\n"
    )
    
    # Fix add_field calls missing closing parentheses
    content = content.replace(
        "                    inline=False\n                \n                # Import here",
        "                    inline=False\n                )\n                \n                # Import here"
    )
    
    # Write back the fixed content
    with open('discord_bot.py', 'w') as file:
        file.write(content)
    
    print("Fixed all missing parentheses in discord_bot.py")

if __name__ == "__main__":
    fix_all_parentheses()