"""
Fix the KeyError: 'primary' bug in technical_analysis.py 
and improve buffer enforcement consistency in Discord bot.

The main issue is that the code structure in get_stop_loss_recommendation 
has an indentation problem with the code blocks. The elif conditions
should be at the same level as the first if condition.
"""

def fix_primary_key_error():
    """
    Fix the indentation issue in the technical_analysis.py file
    that causes the KeyError: 'primary' in some cases.
    """
    try:
        # Read the content of the file
        with open('technical_analysis.py', 'r') as file:
            content = file.read()
        
        # The main issue is with the indentation in the if/elif blocks
        # We need to rewrite the section from approximately line 1124 to 1182
            
        # This is the problematic section with wrong indentation
        problematic_section = """        # Set the primary recommendation based on the trade horizon
        # Only set if not already set by enhanced stop loss
        if "primary" not in result:
            if trade_horizon == "scalp":
                result["primary"] = scalp_recommendation
            
            # Create a completely integrated stop loss message
            base_msg = result["primary"]["recommendation"].replace(
                "Technical stop loss:", "Technical stock price stop:"
            )
            
            # Get just the first section (the header and bullet points)
            base_parts = base_msg.split("\n\n")
            if len(base_parts) > 0:
                first_section = base_parts[0]
                
                # Build a completely new message with proper sections
                result["primary"]["recommendation"] = (
                    f"{first_section}\n"
                    f"• For short-term options (1-2 days expiry)\n\n"
                )
                
                # Add the appropriate warning based on option type
                if option_type.lower() == 'call' and result["primary"]["level"] < current_price:
                    result["primary"]["recommendation"] += (
                        f"⚠️ Options typically lose 70-90% of value when the stock hits stop level due to accelerated delta decay and negative gamma."
                    )
                elif option_type.lower() == 'put' and result["primary"]["level"] > current_price:
                    result["primary"]["recommendation"] += (
                        f"⚠️ Options typically lose 70-90% of value when the stock hits stop level due to accelerated delta decay and negative gamma."
                    )
        
            elif trade_horizon == "swing":
                result["primary"] = swing_recommendation
            
            # Create a completely integrated stop loss message
            base_msg = result["primary"]["recommendation"].replace(
                "Technical stop loss:", "Technical stock price stop:"
            )
            
            # Get just the first section (the header and bullet points)
            base_parts = base_msg.split("\n\n")
            if len(base_parts) > 0:
                first_section = base_parts[0]
                
                # Build a completely new message with proper sections
                result["primary"]["recommendation"] = (
                    f"{first_section}\n"
                    f"• For medium-term options (up to 90 days expiry)\n\n"
                )
                
                # Add the appropriate warning based on option type
                if option_type.lower() == 'call' and result["primary"]["level"] < current_price:
                    result["primary"]["recommendation"] += (
                        f"⚠️ Options typically lose 60-80% of value when the stock hits stop level due to accelerated delta decay and negative gamma."
                    )
                elif option_type.lower() == 'put' and result["primary"]["level"] > current_price:
                    result["primary"]["recommendation"] += (
                        f"⚠️ Options typically lose 60-80% of value when the stock hits stop level due to accelerated delta decay and negative gamma."
                    )
        
            elif trade_horizon == "longterm":
                result["primary"] = longterm_recommendation"""

        # This is the corrected version with proper indentation
        corrected_section = """        # Set the primary recommendation based on the trade horizon
        # Only set if not already set by enhanced stop loss
        if "primary" not in result:
            if trade_horizon == "scalp":
                result["primary"] = scalp_recommendation
                
                # Create a completely integrated stop loss message
                base_msg = result["primary"]["recommendation"].replace(
                    "Technical stop loss:", "Technical stock price stop:"
                )
                
                # Get just the first section (the header and bullet points)
                base_parts = base_msg.split("\n\n")
                if len(base_parts) > 0:
                    first_section = base_parts[0]
                    
                    # Build a completely new message with proper sections
                    result["primary"]["recommendation"] = (
                        f"{first_section}\n"
                        f"• For short-term options (1-2 days expiry)\n\n"
                    )
                    
                    # Add the appropriate warning based on option type
                    if option_type.lower() == 'call' and result["primary"]["level"] < current_price:
                        result["primary"]["recommendation"] += (
                            f"⚠️ Options typically lose 70-90% of value when the stock hits stop level due to accelerated delta decay and negative gamma."
                        )
                    elif option_type.lower() == 'put' and result["primary"]["level"] > current_price:
                        result["primary"]["recommendation"] += (
                            f"⚠️ Options typically lose 70-90% of value when the stock hits stop level due to accelerated delta decay and negative gamma."
                        )
            
            elif trade_horizon == "swing":
                result["primary"] = swing_recommendation
                
                # Create a completely integrated stop loss message
                base_msg = result["primary"]["recommendation"].replace(
                    "Technical stop loss:", "Technical stock price stop:"
                )
                
                # Get just the first section (the header and bullet points)
                base_parts = base_msg.split("\n\n")
                if len(base_parts) > 0:
                    first_section = base_parts[0]
                    
                    # Build a completely new message with proper sections
                    result["primary"]["recommendation"] = (
                        f"{first_section}\n"
                        f"• For medium-term options (up to 90 days expiry)\n\n"
                    )
                    
                    # Add the appropriate warning based on option type
                    if option_type.lower() == 'call' and result["primary"]["level"] < current_price:
                        result["primary"]["recommendation"] += (
                            f"⚠️ Options typically lose 60-80% of value when the stock hits stop level due to accelerated delta decay and negative gamma."
                        )
                    elif option_type.lower() == 'put' and result["primary"]["level"] > current_price:
                        result["primary"]["recommendation"] += (
                            f"⚠️ Options typically lose 60-80% of value when the stock hits stop level due to accelerated delta decay and negative gamma."
                        )
            
            elif trade_horizon == "longterm":
                result["primary"] = longterm_recommendation"""

        # Update the content
        updated_content = content.replace(problematic_section, corrected_section)
        
        # Write the updated content back to the file
        with open('technical_analysis.py', 'w') as file:
            file.write(updated_content)
            
        print("Successfully fixed the primary key error in technical_analysis.py")
        
        # Also fix the longterm section which has similar issues
        with open('technical_analysis.py', 'r') as file:
            content = file.read()
            
        problematic_longterm = """            # Create a completely integrated stop loss message
            base_msg = result["primary"]["recommendation"].replace(
                "Technical stop loss:", "Technical stock price stop:"
            )
            
            # Get just the first section (the header and bullet points)
            base_parts = base_msg.split("\n\n")
            if len(base_parts) > 0:
                first_section = base_parts[0]
                
                # Build a completely new message with proper sections
                result["primary"]["recommendation"] = (
                    f"{first_section}\n"
                    f"• For long-term options (6+ months expiry)\n\n"
                )
                
                # Add the appropriate warning based on option type
                if option_type.lower() == 'call' and result["primary"]["level"] < current_price:
                    result["primary"]["recommendation"] += (
                        f"⚠️ Options typically lose 40-50% of value when the stock hits stop level. Long-dated options have more cushion but still decline significantly at stop levels."
                    )
                elif option_type.lower() == 'put' and result["primary"]["level"] > current_price:
                    result["primary"]["recommendation"] += (
                        f"⚠️ Options typically lose 40-50% of value when the stock hits stop level. Long-dated options have more cushion but still decline significantly at stop levels."
                    )"""
                    
        corrected_longterm = """                # Create a completely integrated stop loss message
                base_msg = result["primary"]["recommendation"].replace(
                    "Technical stop loss:", "Technical stock price stop:"
                )
                
                # Get just the first section (the header and bullet points)
                base_parts = base_msg.split("\n\n")
                if len(base_parts) > 0:
                    first_section = base_parts[0]
                    
                    # Build a completely new message with proper sections
                    result["primary"]["recommendation"] = (
                        f"{first_section}\n"
                        f"• For long-term options (6+ months expiry)\n\n"
                    )
                    
                    # Add the appropriate warning based on option type
                    if option_type.lower() == 'call' and result["primary"]["level"] < current_price:
                        result["primary"]["recommendation"] += (
                            f"⚠️ Options typically lose 40-50% of value when the stock hits stop level. Long-dated options have more cushion but still decline significantly at stop levels."
                        )
                    elif option_type.lower() == 'put' and result["primary"]["level"] > current_price:
                        result["primary"]["recommendation"] += (
                            f"⚠️ Options typically lose 40-50% of value when the stock hits stop level. Long-dated options have more cushion but still decline significantly at stop levels."
                        )"""
                        
        # Update the content again
        updated_content = content.replace(problematic_longterm, corrected_longterm)
        
        # Write the updated content back to the file
        with open('technical_analysis.py', 'w') as file:
            file.write(updated_content)
            
        print("Successfully fixed the longterm section in technical_analysis.py")
        
    except Exception as e:
        print(f"Error fixing primary key error: {e}")

def update_enforce_buffer_limits():
    """
    Update the enforce_buffer_limits method in discord_bot.py to ensure
    it is consistently enforcing the correct buffer limits, with improved
    logging for clarity.
    """
    try:
        # Read the content of the file
        with open('discord_bot.py', 'r') as file:
            content = file.read()
        
        # The current buffer enforcement logic works correctly, but could use 
        # more descriptive logging for debugging. Let's update the print statement.
        current_logging = "            print(f\"Adjusting stop loss from {stop_loss:.2f} to {adjusted_stop_loss:.2f} to respect {max_buffer_percentage:.1f}% buffer limit for {days_to_expiration} DTE\")"
        
        improved_logging = """            # Calculate how much we're adjusting the stop loss by
            adjustment_percentage = abs(adjusted_stop_loss - stop_loss) / current_price * 100
            print(f"Adjusting stop loss from {stop_loss:.2f} to {adjusted_stop_loss:.2f} to respect {max_buffer_percentage:.1f}% buffer limit for {days_to_expiration} DTE")
            print(f"Current price: ${current_price:.2f}, adjustment amount: {adjustment_percentage:.2f}% of price")"""
        
        # Update the content
        updated_content = content.replace(current_logging, improved_logging)
        
        # Write the updated content back to the file
        with open('discord_bot.py', 'w') as file:
            file.write(updated_content)
            
        print("Successfully updated buffer enforcement logging in discord_bot.py")
        
    except Exception as e:
        print(f"Error updating enforce_buffer_limits: {e}")

if __name__ == "__main__":
    fix_primary_key_error()
    update_enforce_buffer_limits()