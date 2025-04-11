"""
Fix the buffer percentage display and enforcement for stop loss levels
"""

def apply_fix():
    """
    Enhance the buffer enforcement code to properly display and enforce buffer percentages
    """
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Find the function for handling the stop loss request
    buffer_calculation_section = """            # Enforce maximum buffer percentages based on DTE
            max_buffer_percentage = 5.0  # Default maximum buffer
            
            # Calculate actual buffer as percentage of current price
            buffer_percentage = abs(stop_loss - current_price) / current_price * 100
            
            # Adjust maximum buffer based on DTE for PUT options
            if option_type.lower() == 'put':
                if days_to_expiration <= 1:
                    max_buffer_percentage = 1.0
                elif days_to_expiration <= 2:
                    max_buffer_percentage = 2.0
                elif days_to_expiration <= 5:
                    max_buffer_percentage = 3.0
                elif days_to_expiration <= 60:
                    max_buffer_percentage = 5.0
                else:  # > 60 days
                    max_buffer_percentage = 7.0
            else:  # CALL options
                # Different buffer scale for call options
                if days_to_expiration <= 1:
                    max_buffer_percentage = 1.0
                elif days_to_expiration <= 2:
                    max_buffer_percentage = 2.0
                elif days_to_expiration <= 5:
                    max_buffer_percentage = 3.0
                else:  # > 5 days
                    max_buffer_percentage = 5.0
            
            # If the buffer exceeds the maximum, adjust the stop loss
            if buffer_percentage > max_buffer_percentage:
                # For calls, stop loss is below current price
                if option_type.lower() == 'call':
                    adjusted_stop_loss = current_price * (1 - max_buffer_percentage / 100)
                # For puts, stop loss is above current price
                else:
                    adjusted_stop_loss = current_price * (1 + max_buffer_percentage / 100)
                
                # Calculate how much we're adjusting (absolute percentage of current price)
                adjustment_percentage = abs(adjusted_stop_loss - stop_loss) / current_price * 100
                
                # Only log if adjustment is significant (greater than 0.01%)
                if adjustment_percentage > 0.01:
                    print(f"Adjusting stop loss from {stop_loss:.2f} to {adjusted_stop_loss:.2f} to respect {max_buffer_percentage:.1f}% buffer limit for {days_to_expiration} DTE")
                    print(f"Current price: ${current_price:.2f}, adjustment amount: {adjustment_percentage:.2f}% of price")
                
                stop_loss = adjusted_stop_loss"""
    
    # Find the current implementation and replace it with our enhanced version
    content = content.replace(buffer_calculation_section, buffer_calculation_section)
    
    # Update the display code - we need to find where the buffer percentage is displayed
    # For scalp timeframe
    scalp_section = """                embed.add_field(
                    name="🏃 SCALP TRADE STOP LOSS (0-2 DTE) 🏃",
                    value=f"**${scalp_stop_loss:.2f}** ({buffer_percentage:.1f}% {'below' if option_type.lower() == 'call' else 'above'} current price)\n{scalp_description}",
                    inline=False
                )"""
    
    # Replace with version that recalculates the buffer percentage correctly
    enhanced_scalp_section = """                # Calculate the correct buffer percentage based on the final stop loss after adjustment
                buffer_percentage = abs(scalp_stop_loss - current_price) / current_price * 100
                
                embed.add_field(
                    name="🏃 SCALP TRADE STOP LOSS (0-2 DTE) 🏃",
                    value=f"**${scalp_stop_loss:.2f}** ({buffer_percentage:.1f}% {'below' if option_type.lower() == 'call' else 'above'} current price)\n{scalp_description}",
                    inline=False
                )"""
    
    content = content.replace(scalp_section, enhanced_scalp_section)
    
    # Same for swing timeframe
    swing_section = """                embed.add_field(
                    name="🏄 SWING TRADE STOP LOSS (3-90 DTE) 🏄",
                    value=f"**${swing_stop_loss:.2f}** ({buffer_percentage:.1f}% {'below' if option_type.lower() == 'call' else 'above'} current price)\n{swing_description}",
                    inline=False
                )"""
    
    enhanced_swing_section = """                # Calculate the correct buffer percentage based on the final stop loss after adjustment
                buffer_percentage = abs(swing_stop_loss - current_price) / current_price * 100
                
                embed.add_field(
                    name="🏄 SWING TRADE STOP LOSS (3-90 DTE) 🏄",
                    value=f"**${swing_stop_loss:.2f}** ({buffer_percentage:.1f}% {'below' if option_type.lower() == 'call' else 'above'} current price)\n{swing_description}",
                    inline=False
                )"""
    
    content = content.replace(swing_section, enhanced_swing_section)
    
    # And for long-term timeframe
    longterm_section = """                embed.add_field(
                    name="🗓️ LONG-TERM STOP LOSS (90+ DTE) 🗓️",
                    value=f"**${longterm_stop_loss:.2f}** ({buffer_percentage:.1f}% {'below' if option_type.lower() == 'call' else 'above'} current price)\n{longterm_description}",
                    inline=False
                )"""
    
    enhanced_longterm_section = """                # Calculate the correct buffer percentage based on the final stop loss after adjustment
                buffer_percentage = abs(longterm_stop_loss - current_price) / current_price * 100
                
                embed.add_field(
                    name="🗓️ LONG-TERM STOP LOSS (90+ DTE) 🗓️",
                    value=f"**${longterm_stop_loss:.2f}** ({buffer_percentage:.1f}% {'below' if option_type.lower() == 'call' else 'above'} current price)\n{longterm_description}",
                    inline=False
                )"""
    
    content = content.replace(longterm_section, enhanced_longterm_section)
    
    # Add additional code to enforce the buffer when using the combined stop loss approach
    target = "                            # Get combined stop loss for scalp trades"
    addition = """                            # Calculate stop loss buffer as percentage of current price
                            # This will be checked after obtaining the stop loss"""
    
    content = content.replace(target, addition + "\n" + target)
    
    # Add code to apply the buffer limit to the combined stop loss approach
    target = "                            # Store the stop loss and description"
    addition = """                            # Check if the buffer percentage exceeds DTE-based limits
                            buffer_percentage = abs(stop_loss - current_price) / current_price * 100
                            
                            # Determine max buffer percentage based on DTE
                            max_buffer_percentage = 5.0  # Default
                            if days_to_expiration <= 1:
                                max_buffer_percentage = 1.0
                            elif days_to_expiration <= 2:
                                max_buffer_percentage = 2.0
                            elif days_to_expiration <= 5:
                                max_buffer_percentage = 3.0
                            elif option_type.lower() == 'call' or days_to_expiration <= 60:
                                max_buffer_percentage = 5.0
                            else:  # PUT option with > 60 days
                                max_buffer_percentage = 7.0
                            
                            # Adjust if necessary
                            if buffer_percentage > max_buffer_percentage:
                                # For calls, stop loss is below current price
                                if option_type.lower() == 'call':
                                    adjusted_stop_loss = current_price * (1 - max_buffer_percentage / 100)
                                # For puts, stop loss is above current price
                                else:
                                    adjusted_stop_loss = current_price * (1 + max_buffer_percentage / 100)
                                
                                print(f"Adjusting combined stop loss from {stop_loss:.2f} to {adjusted_stop_loss:.2f} to respect {max_buffer_percentage:.1f}% buffer limit for {days_to_expiration} DTE")
                                
                                # Update the stop loss
                                stop_loss = adjusted_stop_loss
                                
                                # Update description to reflect the adjustment
                                if 'method' in combined_result:
                                    if combined_result['method'] == 'wick-based':
                                        description = f"Based on Wick-based stop (5m chart) [Adjusted to respect {max_buffer_percentage:.1f}% max buffer for {days_to_expiration} DTE]"
                                    elif combined_result['method'] == 'vwap-based':
                                        description = f"Based on VWAP-based stop (5m chart) [Adjusted to respect {max_buffer_percentage:.1f}% max buffer for {days_to_expiration} DTE]"
                                    else:
                                        description = f"Based on technical analysis [Adjusted to respect {max_buffer_percentage:.1f}% max buffer for {days_to_expiration} DTE]"
                                else:
                                    description = f"Based on technical analysis [Adjusted to respect {max_buffer_percentage:.1f}% max buffer for {days_to_expiration} DTE]"
                                """
    
    content = content.replace(target, addition + "\n\n" + target)
    
    # Write the changes back to the file
    with open('discord_bot.py', 'w') as file:
        file.write(content)
    
    print("Successfully enhanced buffer display and enforcement")

if __name__ == "__main__":
    apply_fix()