"""
Targeted integration of Black-Scholes calculation for specific edge cases.

This script enhances the Discord bot's option price calculation only for cases
where delta approximation produces unrealistic results (like 0.0% loss) for
near-expiration at-the-money options.
"""

def integrate_targeted_bs_calculation():
    """
    Adds a targeted Black-Scholes calculation method to the Discord bot
    only for problematic near-expiration ATM scenarios.
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
    
    # Find the section where option price at stop loss is calculated
    target_patterns = [
        "# Calculate the option price at the stop loss level using delta approximation",
        "# Use delta approximation to estimate the option price at the stop level",
        "# Calculate option price at stop loss level",
        "option_price_at_stop = max(0.01, option_price + price_change * abs(delta))"
    ]
    
    for pattern in target_patterns:
        if pattern in updated_content:
            # Found a match, now locate the section to replace
            pattern_pos = updated_content.find(pattern)
            
            # Find the start of the relevant section (price change calculation)
            section_start = updated_content.rfind("\n", 0, pattern_pos) + 1
            
            # Find the end of the calculation section
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
            
            # Create new targeted calculation that uses BS only in specific cases
            new_calculation = """
            # Calculate the option price at the stop loss level
            # Standard delta approximation for most cases, BS for near-expiration ATM options
            price_change = stop_level - current_price
            
            # Determine if this is a case requiring full BS calculation
            needs_full_bs = False
            
            # Check for near-expiration ATM scenario
            if days_to_expiration <= 1:
                # Check if option is ATM or near ATM (within 0.5% of strike)
                price_to_strike_ratio = current_price / strike_price
                is_near_atm = 0.995 <= price_to_strike_ratio <= 1.005
                
                # Check if delta is small (would result in unrealistic price change)
                is_delta_problematic = abs(delta) < 0.2
                
                # Use full BS calculation if ATM and has problematic delta
                if is_near_atm and is_delta_problematic:
                    needs_full_bs = True
            
            if needs_full_bs:
                try:
                    # For problematic near-expiration ATM options, use full BS recalculation
                    iv = 0.3  # Use a reasonable default IV if not available
                    
                    # Ensure minimum time to expiration for calculation stability
                    effective_dte = max(0.05, days_to_expiration)
                    
                    option_price_at_stop = opc.calculate_option_price_at_stop(
                        current_option_price=option_price,
                        current_stock_price=current_price,
                        stop_stock_price=stop_level,
                        strike_price=strike_price,
                        days_to_expiration=effective_dte,
                        implied_volatility=iv,
                        option_type=option_type.lower(),
                        use_full_bs=True
                    )
                    
                    print(f"Used full BS calculation for ATM {days_to_expiration}DTE {option_type}")
                except Exception as e:
                    # Fall back to delta approximation with minimum price impact
                    if option_type.lower() == 'call':
                        price_change_effect = price_change * max(0.2, abs(delta))
                    else:
                        price_change_effect = -price_change * max(0.2, abs(delta))
                    
                    option_price_at_stop = max(0.01, option_price + price_change_effect)
                    print(f"BS calculation failed, using enhanced delta approx: {str(e)}")
            else:
                # Standard delta approximation for normal cases
                if option_type.lower() == 'call':
                    price_change_effect = price_change * abs(delta)
                else:
                    price_change_effect = -price_change * abs(delta)
                
                option_price_at_stop = max(0.01, option_price + price_change_effect)
            """
            
            # Clean up indentation
            new_calculation = "\n".join([line[12:] for line in new_calculation.split("\n")])
            
            # Replace the old calculation with the new one
            updated_content = updated_content.replace(old_calculation, new_calculation)
            break
    
    # Now, let's write the updated content back to the file
    with open('discord_bot.py', 'w') as file:
        file.write(updated_content)
    
    print("Successfully integrated targeted Black-Scholes calculation for edge cases in discord_bot.py")
    print("This enhancement provides more accurate option price calculations specifically for")
    print("near-expiration at-the-money options where delta approximation produces unrealistic results.")

if __name__ == "__main__":
    integrate_targeted_bs_calculation()