"""
This script moves the risk warning from the top of the embed to the bottom
in the handle_stop_loss_request function in discord_bot.py
"""

def move_risk_warning_to_bottom():
    """
    Reads discord_bot.py, removes the risk warning from its current position
    at the top of the embed, and adds it at the bottom after all other fields.
    """
    with open('discord_bot.py', 'r', encoding='utf-8') as file:
        content = file.read()

    # Find the section where we add the risk warning (at the top)
    top_risk_warning = """            # Add Risk Warning field
            embed.add_field(
                name="⚠️ RISK WARNING",
                value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                inline=False
            )"""

    # Delete this section (we'll add it back at the bottom)
    content = content.replace(top_risk_warning, "            # Risk warning moved to bottom")

    # Now find places where we need to add the risk warning at the bottom
    # For scalp trades (right before the return statement)
    scalp_return = """                    # Add the response content to the embed's description
                    embed.description = response
                    
                    return embed"""
    
    scalp_with_warning = """                    # Add the response content to the embed's description
                    embed.description = response
                    
                    # Add Risk Warning at the bottom
                    embed.add_field(
                        name="⚠️ RISK WARNING",
                        value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                        inline=False
                    )
                    
                    return embed"""
    
    content = content.replace(scalp_return, scalp_with_warning)
    
    # For swing trades (before returning the embed)
    swing_return = """                    # Add the response content to the embed's description
                    embed.description = response

                    # Add theta decay warning field at the bottom if applicable
                    if theta_decay_warning:
                        embed.add_field(
                            name="⚠️ THETA DECAY PROJECTION TO (" + info["expiration"] + ") ⚠️",
                            value=theta_decay_warning.replace("⚠️ **THETA DECAY PROJECTION TO EXPIRY", "⚠️ **THETA DECAY PROJECTION TO").replace("** ⚠️", "** ⚠️"),
                            inline=False
                        )
                    
                    return embed"""
    
    swing_with_warning = """                    # Add the response content to the embed's description
                    embed.description = response

                    # Add theta decay warning field at the bottom if applicable
                    if theta_decay_warning:
                        embed.add_field(
                            name="⚠️ THETA DECAY PROJECTION TO (" + info["expiration"] + ") ⚠️",
                            value=theta_decay_warning.replace("⚠️ **THETA DECAY PROJECTION TO EXPIRY", "⚠️ **THETA DECAY PROJECTION TO").replace("** ⚠️", "** ⚠️"),
                            inline=False
                        )
                    
                    # Add Risk Warning at the bottom
                    embed.add_field(
                        name="⚠️ RISK WARNING",
                        value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                        inline=False
                    )
                    
                    return embed"""
    
    content = content.replace(swing_return, swing_with_warning)
    
    # For long-term trades (before returning the embed)
    longterm_return = """                    # Add the response content to the embed's description
                    embed.description = response
                    
                    # Add theta decay warning field if applicable (place at bottom after other content)
                    if theta_decay_warning:
                        embed.add_field(
                            name="⚠️ THETA DECAY PROJECTION TO (" + info["expiration"] + ") ⚠️",
                            value=theta_decay_warning.replace("⚠️ **THETA DECAY PROJECTION TO EXPIRY", "⚠️ **THETA DECAY PROJECTION TO").replace("** ⚠️", "** ⚠️"),
                            inline=False
                        )
                    
                    return embed"""
    
    longterm_with_warning = """                    # Add the response content to the embed's description
                    embed.description = response
                    
                    # Add theta decay warning field if applicable (place at bottom after other content)
                    if theta_decay_warning:
                        embed.add_field(
                            name="⚠️ THETA DECAY PROJECTION TO (" + info["expiration"] + ") ⚠️",
                            value=theta_decay_warning.replace("⚠️ **THETA DECAY PROJECTION TO EXPIRY", "⚠️ **THETA DECAY PROJECTION TO").replace("** ⚠️", "** ⚠️"),
                            inline=False
                        )
                    
                    # Add Risk Warning at the bottom
                    embed.add_field(
                        name="⚠️ RISK WARNING",
                        value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                        inline=False
                    )
                    
                    return embed"""
    
    content = content.replace(longterm_return, longterm_with_warning)
    
    # For default/unknown trade types (before returning the embed)
    default_return = """                # Add remaining fields and return the embed
                if technical_basis:
                    embed.description = response
                    
                    # Add theta decay warning field if applicable (place at bottom after other content)
                    if theta_decay_warning:
                        embed.add_field(
                            name="⚠️ THETA DECAY PROJECTION TO (" + info["expiration"] + ") ⚠️",
                            value=theta_decay_warning.replace("⚠️ **THETA DECAY PROJECTION TO EXPIRY", "⚠️ **THETA DECAY PROJECTION TO").replace("** ⚠️", "** ⚠️"),
                            inline=False
                        )
                    
                    return embed"""
    
    default_with_warning = """                # Add remaining fields and return the embed
                if technical_basis:
                    embed.description = response
                    
                    # Add theta decay warning field if applicable (place at bottom after other content)
                    if theta_decay_warning:
                        embed.add_field(
                            name="⚠️ THETA DECAY PROJECTION TO (" + info["expiration"] + ") ⚠️",
                            value=theta_decay_warning.replace("⚠️ **THETA DECAY PROJECTION TO EXPIRY", "⚠️ **THETA DECAY PROJECTION TO").replace("** ⚠️", "** ⚠️"),
                            inline=False
                        )
                    
                    # Add Risk Warning at the bottom
                    embed.add_field(
                        name="⚠️ RISK WARNING",
                        value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                        inline=False
                    )
                    
                    return embed"""
    
    content = content.replace(default_return, default_with_warning)
    
    # Also handle the generic fallback return
    fallback_return = """                # Default return an empty embed if something goes wrong
                return discord.Embed(
                    title=f"Stop Loss Recommendation for {ticker}",
                    description="Sorry, I couldn't generate a stop loss recommendation due to missing data.",
                    color=0xFF0000
                )"""
    
    fallback_with_warning = """                # Create a fallback embed with the risk warning
                fallback_embed = discord.Embed(
                    title=f"Stop Loss Recommendation for {ticker}",
                    description="Sorry, I couldn't generate a stop loss recommendation due to missing data.",
                    color=0xFF0000
                )
                
                # Add Risk Warning at the bottom even in fallback case
                fallback_embed.add_field(
                    name="⚠️ RISK WARNING",
                    value="Stop losses do not guarantee execution at the specified price in fast-moving markets.",
                    inline=False
                )
                
                return fallback_embed"""
    
    content = content.replace(fallback_return, fallback_with_warning)
    
    # Write the modified content back to the file
    with open('discord_bot.py', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Moved the Risk Warning to the bottom of the embed in discord_bot.py")

if __name__ == "__main__":
    move_risk_warning_to_bottom()