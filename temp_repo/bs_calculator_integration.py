"""
Integration script to update the option price calculation in Discord bot responses.

This script enhances the handle_stop_loss_request method in discord_bot.py to use
the more accurate Black-Scholes calculation for option prices at stop loss levels,
especially important for at-the-money options near expiration.
"""

def integrate_bs_calculator():
    """
    Adds the Black-Scholes calculation method to the Discord bot.
    """
    # First, let's read the current discord_bot.py file
    with open('discord_bot.py', 'r') as file:
        content = file.read()
    
    # Check if option_price_calculator is already imported
    if "import option_price_calculator" not in content:
        # Add the import statement after other imports
        import_section_end = content.find("intents = discord.Intents.default()")
        if import_section_end == -1:
            import_section_end = content.find("# Setup intents")
        
        updated_content = content[:import_section_end] + \
            "import option_price_calculator as opc\n\n" + \
            content[import_section_end:]
    else:
        updated_content = content
    
    # Next, identify the function that calculates option price at stop loss
    # Look for delta_approximation or similar patterns
    target_patterns = [
        "# Calculate the option price at the stop loss level using delta approximation",
        "# Use delta approximation to estimate the option price at the stop level",
        "# Calculate option price at stop loss level",
        "option_price_at_stop = max(0.01, option_price + price_change * abs(delta))"
    ]
    
    # Find location of price calculation in handle_stop_loss_request
    for pattern in target_patterns:
        if pattern in updated_content:
            # Found a match, now locate the section to replace
            pattern_pos = updated_content.find(pattern)
            
            # Find the start of the relevant section
            section_start = updated_content.rfind("\n", 0, pattern_pos) + 1
            
            # Find the end of the calculation section (typically ends with calculating loss percentage)
            section_end_patterns = [
                "price_change_pct = ",
                "price_change_percentage =",
                "loss_percentage =",
                "# Add technical analysis results to"
            ]
            
            section_end = -1
            for end_pattern in section_end_patterns:
                pos = updated_content.find(end_pattern, pattern_pos)
                if pos != -1 and (section_end == -1 or pos < section_end):
                    section_end = updated_content.rfind("\n", 0, pos) + 1
            
            if section_end == -1:
                # If we couldn't find a clear end, estimate it
                section_end = updated_content.find("\n\n", pattern_pos)
            
            # Extract the section to replace
            old_calculation = updated_content[section_start:section_end]
            
            # Create new calculation using Black-Scholes
            new_calculation = """
            # Calculate the option price at the stop loss level using enhanced Black-Scholes calculator
            try:
                # For near-expiration options, use full BS calculation instead of delta approximation
                option_price_at_stop = opc.calculate_option_price_at_stop(
                    current_option_price=option_price,
                    current_stock_price=current_price,
                    stop_stock_price=stop_level,
                    strike_price=strike_price,
                    days_to_expiration=days_to_expiration,
                    implied_volatility=iv,
                    option_type=option_type.lower(),
                    use_full_bs=True  # Always use full BS for accuracy
                )
                
                # For very low option prices, ensure a minimum displayed value
                if option_price_at_stop < 0.01:
                    option_price_at_stop = 0.01
                    
            except Exception as e:
                # Fall back to delta approximation if BS calculation fails
                price_change = stop_level - current_price
                if option_type.lower() == 'call':
                    price_change_effect = price_change * abs(delta)
                else:
                    price_change_effect = -price_change * abs(delta)
                
                option_price_at_stop = max(0.01, option_price + price_change_effect)
                print(f"Falling back to delta approximation due to: {str(e)}")
            """
            
            # Clean up indentation
            new_calculation = "\n".join([line[12:] for line in new_calculation.split("\n")])
            
            # Replace the old calculation with the new one
            updated_content = updated_content.replace(old_calculation, new_calculation)
            break
    
    # Now, let's write the updated content back to the file
    with open('discord_bot.py', 'w') as file:
        file.write(updated_content)
    
    print("Successfully integrated Black-Scholes calculator into discord_bot.py")
    print("This enhancement provides more accurate option price calculations at stop loss levels,")
    print("especially critical for at-the-money options near expiration.")

if __name__ == "__main__":
    integrate_bs_calculator()