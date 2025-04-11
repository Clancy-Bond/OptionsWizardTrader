"""
This script modifies the Discord bot to move the theta decay warning from
being part of the embed description to being a separate field that appears
at the bottom of the embed after the "General Risk Note" field.
"""

def apply_fix():
    """
    Update the Discord bot to move the theta decay warnings to the bottom
    """
    # Read in the current discord_bot.py file
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Find and replace each instance of theta decay warning placement
    
    # Pattern 1: Swing Trade Position
    swing_trade_old = """                    # Add the response content to the embed's description
                    embed.description = response
                    
                    # Main content is set without theta decay warning since we'll add it as a field at the bottom
                    
                    # Add general risk disclaimer to the embed
                    embed.add_field(
                        name="⚠️ General Risk Note",
                        value="Options typically show 2-3x leverage compared to stocks. Use proper position sizing to manage risk with larger percentage swings. Adjust stop losses as time decay impacts option pricing.",
                        inline=False
                    )"""
    
    swing_trade_new = """                    # Add the response content to the embed's description
                    embed.description = response
                    
                    # Add general risk disclaimer to the embed
                    embed.add_field(
                        name="⚠️ General Risk Note",
                        value="Options typically show 2-3x leverage compared to stocks. Use proper position sizing to manage risk with larger percentage swings. Adjust stop losses as time decay impacts option pricing.",
                        inline=False
                    )
                    
                    # Add theta decay warning as a field at the bottom if available
                    if theta_decay_warning:
                        embed.add_field(
                            name="⚠️ THETA DECAY PROJECTION ⚠️",
                            value=theta_decay_warning.replace("⚠️ **THETA DECAY PROJECTION TO EXPIRY", "").replace("⚠️", ""),
                            inline=False
                        )"""
    
    content = content.replace(swing_trade_old, swing_trade_new)
    
    # Pattern 2: Long-Term Position
    longterm_old = """                    # Add the response content to the embed's description
                    embed.description = response
                    
                    # Now that the main content is set, add the theta decay warning at the bottom if available
                    if theta_decay_warning:
                        embed.description += f"\\n\\n{theta_decay_warning}"
                    
                    return embed"""
    
    longterm_new = """                    # Add the response content to the embed's description
                    embed.description = response
                    
                    # Add general risk disclaimer to the embed
                    embed.add_field(
                        name="⚠️ General Risk Note",
                        value="Options typically show 2-3x leverage compared to stocks. Use proper position sizing to manage risk with larger percentage swings. Adjust stop losses as time decay impacts option pricing.",
                        inline=False
                    )
                    
                    # Add theta decay warning as a field at the bottom if available
                    if theta_decay_warning:
                        embed.add_field(
                            name="⚠️ THETA DECAY PROJECTION ⚠️",
                            value=theta_decay_warning.replace("⚠️ **THETA DECAY PROJECTION TO EXPIRY", "").replace("⚠️", ""),
                            inline=False
                        )
                    
                    # Add footer to the embed
                    from datetime import datetime
                    embed.set_footer(text=f"Data as of {datetime.now().strftime('%Y-%m-%d %H:%M')} | Prices may change quickly during market hours")
                    
                    return embed"""
    
    # Find the first specific instance to replace (for long-term trades)
    longterm_section = """                elif trade_type == "Long-Term Position/LEAP":
                    # Use regular text (not bold) for the stop loss recommendation 
                    response += f"🔍 LONG-TERM STOP LOSS (Weekly chart) 🔍\\n"
                    response += f"• For long-dated options (3+ months expiry)\\n" 
                    response += f"• Technical Basis: Major support level with extended volatility buffer\\n\\n"
                    """
    
    section_end = """                    # Add the response content to the embed's description
                    embed.description = response
                    
                    # Now that the main content is set, add the theta decay warning at the bottom if available
                    if theta_decay_warning:
                        embed.description += f"\\n\\n{theta_decay_warning}"
                    
                    return embed"""
    
    full_longterm_section = longterm_section
    
    # Find the full section that includes the end part we want to replace
    section_index = content.find(longterm_section)
    if section_index != -1:
        # Find where this section ends (where it returns the embed)
        section_end_index = content.find(section_end, section_index)
        if section_end_index != -1:
            section_end_index += len(section_end)
            full_longterm_section = content[section_index:section_end_index]
            
            # Create the replacement with our modification
            replacement = full_longterm_section.replace(section_end, longterm_new)
            
            # Replace just this specific instance
            content = content.replace(full_longterm_section, replacement)
    
    # Pattern 3: General Options
    general_old = """                    # Add the response content to the embed's description
                    embed.description = response
                    
                    # Now that the main content is set, add the theta decay warning at the bottom if available
                    if theta_decay_warning:
                        embed.description += f"\\n\\n{theta_decay_warning}"
                    
                    return embed"""
    
    general_new = """                    # Add the response content to the embed's description
                    embed.description = response
                    
                    # Add general risk disclaimer to the embed
                    embed.add_field(
                        name="⚠️ General Risk Note",
                        value="Options typically show 2-3x leverage compared to stocks. Use proper position sizing to manage risk with larger percentage swings. Adjust stop losses as time decay impacts option pricing.",
                        inline=False
                    )
                    
                    # Add theta decay warning as a field at the bottom if available
                    if theta_decay_warning:
                        embed.add_field(
                            name="⚠️ THETA DECAY PROJECTION ⚠️",
                            value=theta_decay_warning.replace("⚠️ **THETA DECAY PROJECTION TO EXPIRY", "").replace("⚠️", ""),
                            inline=False
                        )
                    
                    # Add footer to the embed
                    from datetime import datetime
                    embed.set_footer(text=f"Data as of {datetime.now().strftime('%Y-%m-%d %H:%M')} | Prices may change quickly during market hours")
                    
                    return embed"""
    
    # Find the general section
    general_section = """                else:
                    response += f"🔍 GENERAL STOP LOSS RECOMMENDATION 🔍\\n"
                    response += f"• For any option timeframe\\n"
                    response += f"• Technical Basis: Default 5% buffer from current price\\n\\n"
                    response += f"⚠️ Options typically lose 50-70% of value when the stock hits stop level if you continue to hold the position.\\n"
                    """
                    
    section_end = """                    # Add the response content to the embed's description
                    embed.description = response
                    
                    # Now that the main content is set, add the theta decay warning at the bottom if available
                    if theta_decay_warning:
                        embed.description += f"\\n\\n{theta_decay_warning}"
                    
                    return embed"""
                    
    full_general_section = general_section
    
    # Find the full section that includes the end part we want to replace
    section_index = content.find(general_section)
    if section_index != -1:
        # Find where this section ends (where it returns the embed)
        section_end_index = content.find(section_end, section_index)
        if section_end_index != -1:
            section_end_index += len(section_end)
            full_general_section = content[section_index:section_end_index]
            
            # Create the replacement with our modification
            replacement = full_general_section.replace(section_end, general_new)
            
            # Replace just this specific instance
            content = content.replace(full_general_section, replacement)
    
    # Write the updated content back to the file
    with open('discord_bot.py', 'w') as file:
        file.write(content)
    
    print("Successfully updated the theta decay placement in discord_bot.py")

if __name__ == "__main__":
    apply_fix()