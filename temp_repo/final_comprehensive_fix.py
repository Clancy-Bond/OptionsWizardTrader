"""
A comprehensive fix for all syntax and structure issues in technical_analysis.py
"""

def apply_fix():
    """
    Apply a comprehensive fix to ensure get_stop_loss_recommendation always works properly.
    """
    with open('technical_analysis.py', 'r') as file:
        content = file.readlines()
    
    # Find the line number where the problematic section starts
    start_line = 0
    for i, line in enumerate(content):
        if 'if "primary" not in result:' in line:
            start_line = i
            break
    
    if start_line == 0:
        print("Couldn't find the section to fix")
        return
        
    # Replace the entire primary recommendation section with a corrected version
    fixed_section = """        # Set the primary recommendation based on the trade horizon
        # Only set if not already set by enhanced stop loss
        if "primary" not in result:
            if trade_horizon == "scalp":
                try:
                    result["primary"] = scalp_recommendation
                    
                    # Create a completely integrated stop loss message
                    base_msg = result["primary"]["recommendation"].replace(
                        "Technical stop loss:", "Technical stock price stop:"
                    )
                    
                    # Get just the first section (the header and bullet points)
                    base_parts = base_msg.split("\\n\\n")
                    if len(base_parts) > 0:
                        first_section = base_parts[0]
                        
                        # Build a completely new message with proper sections
                        result["primary"]["recommendation"] = (
                            f"{first_section}\\n"
                            f"• For short-term options (1-2 days expiry)\\n\\n"
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
                except Exception as e:
                    print(f"Error formatting scalp recommendation: {e}")
            
            elif trade_horizon == "swing":
                try:
                    result["primary"] = swing_recommendation
                    
                    # Create a completely integrated stop loss message
                    base_msg = result["primary"]["recommendation"].replace(
                        "Technical stop loss:", "Technical stock price stop:"
                    )
                    
                    # Get just the first section (the header and bullet points)
                    base_parts = base_msg.split("\\n\\n")
                    if len(base_parts) > 0:
                        first_section = base_parts[0]
                        
                        # Build a completely new message with proper sections
                        result["primary"]["recommendation"] = (
                            f"{first_section}\\n"
                            f"• For medium-term options (up to 90 days expiry)\\n\\n"
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
                except Exception as e:
                    print(f"Error formatting swing recommendation: {e}")
            
            elif trade_horizon == "longterm":
                try:
                    result["primary"] = longterm_recommendation
                    
                    # Create a completely integrated stop loss message
                    base_msg = result["primary"]["recommendation"].replace(
                        "Technical stop loss:", "Technical stock price stop:"
                    )
                    
                    # Get just the first section (the header and bullet points)
                    base_parts = base_msg.split("\\n\\n")
                    if len(base_parts) > 0:
                        first_section = base_parts[0]
                        
                        # Build a completely new message with proper sections
                        result["primary"]["recommendation"] = (
                            f"{first_section}\\n"
                            f"• For long-term options (6+ months expiry)\\n\\n"
                        )
                        
                        # Add the appropriate warning based on option type
                        if option_type.lower() == 'call' and result["primary"]["level"] < current_price:
                            result["primary"]["recommendation"] += (
                                f"⚠️ Options typically lose 40-50% of value when the stock hits stop level. Long-dated options have more cushion but still decline significantly at stop levels."
                            )
                        elif option_type.lower() == 'put' and result["primary"]["level"] > current_price:
                            result["primary"]["recommendation"] += (
                                f"⚠️ Options typically lose 40-50% of value when the stock hits stop level. Long-dated options have more cushion but still decline significantly at stop levels."
                            )
                except Exception as e:
                    print(f"Error formatting longterm recommendation: {e}")
            
            else:  # unknown trade horizon
                # Set a default primary recommendation (use swing as default)
                result["primary"] = {
                    "level": swing_recommendation["level"],  # Default to swing as primary
                    "recommendation": "Based on your option details, here are stop-loss recommendations for different trading timeframes. Choose the one that matches your trading strategy and option expiration:\\n\\n" + 
                                    "1. " + scalp_recommendation["recommendation"] + "\\n\\n" +
                                    "2. " + swing_recommendation["recommendation"] + "\\n\\n" +
                                    "3. " + longterm_recommendation["recommendation"] + "\\n\\n" +
                                    "For more precise option price stop-loss calculations, please provide your specific option expiration date.",
                    "time_horizon": "multiple"
                }

"""
    
    # Find the line number where the next important section starts
    end_marker = "        # If we have the expiration date, only include recommendations appropriate for the timeframe"
    end_line = 0
    for i, line in enumerate(content[start_line:], start=start_line):
        if end_marker in line:
            end_line = i
            break
    
    if end_line == 0:
        print("Couldn't find the end of the section to fix")
        return
    
    # Replace the problematic section with our fixed version
    new_content = content[:start_line] + fixed_section.split('\n') + content[end_line:]
    
    # Add safety code to ensure 'primary' and 'trade_horizon' are always set
    target_before = "        return result"
    safety_code = """        # Ensure all necessary keys exist to prevent KeyError
        if 'primary' not in result:
            # Default to swing recommendation as primary if not already set
            result['primary'] = result['swing']
            
        # Always ensure trade_horizon is in the result
        result['trade_horizon'] = trade_horizon
        
        return result"""
    
    # Find the position of the return statement
    return_pos = 0
    for i, line in enumerate(new_content):
        if target_before in line:
            return_pos = i
            break
    
    if return_pos > 0:
        new_content[return_pos] = safety_code
    
    # Write the fixed file
    with open('technical_analysis.py', 'w') as file:
        file.writelines(new_content)
    
    print("Successfully applied comprehensive fix to technical_analysis.py")

if __name__ == "__main__":
    apply_fix()