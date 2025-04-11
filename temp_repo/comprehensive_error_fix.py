"""
Comprehensive fix for the stop loss error handling in technical_analysis.py.
This script completely rewrites the problematic section of the code to ensure
proper error handling and key settings.
"""

def apply_comprehensive_fix():
    """
    Apply a comprehensive fix to ensure all necessary keys are set in the result dictionary.
    """
    try:
        # Read the original file
        with open('technical_analysis.py', 'r') as file:
            lines = file.readlines()
        
        # Find the start of the get_stop_loss_recommendation function
        start_line = 0
        for i, line in enumerate(lines):
            if 'def get_stop_loss_recommendation(' in line:
                start_line = i
                break
        
        # Find the end of the function
        end_line = len(lines)
        paren_count = 0
        for i in range(start_line, len(lines)):
            line = lines[i]
            if line.strip().startswith('def ') and i > start_line:
                end_line = i
                break
        
        # Extract the function
        original_function = ''.join(lines[start_line:end_line])
        
        # Create a completely new implementation with proper error handling
        new_function = """def get_stop_loss_recommendation(stock, current_price, option_type, expiration=None):
    \"\"\"
    Get comprehensive stop loss recommendations based on expiration timeframe.
    
    Args:
        stock: yfinance Ticker object
        current_price: Current stock price
        option_type: 'call' or 'put'
        expiration: Option expiration date (string in format 'YYYY-MM-DD')
    
    Returns:
        Dictionary with stop loss recommendations for different timeframes
    \"\"\"
    try:
        # Determine the appropriate timeframe based on expiration if provided
        trade_horizon = "unknown"
        days_to_expiration = None
        
        if expiration:
            # Calculate days to expiration
            try:
                expiry_date = datetime.datetime.strptime(expiration, '%Y-%m-%d').date()
                today = datetime.datetime.now().date()
                days_to_expiration = (expiry_date - today).days
                
                if days_to_expiration <= 2:
                    trade_horizon = "scalp"  # Today or tomorrow expiry
                elif days_to_expiration <= 90:
                    trade_horizon = "swing"  # 2 weeks to 3 months
                else:
                    trade_horizon = "longterm"  # 6+ months
                    
                print(f"Days to expiration: {days_to_expiration}, Trade horizon: {trade_horizon}")
            except Exception as e:
                print(f"Error parsing expiration date: {str(e)}")
                # If date parsing fails, provide all recommendations
                trade_horizon = "unknown"
        
        # First, try to get pattern-based stop loss using the enhanced system
        enhanced_stop = get_enhanced_stop_loss(stock, current_price, option_type, days_to_expiration, trade_horizon)
        
        # Get standard recommendations 
        scalp_recommendation = get_scalp_stop_loss(stock, current_price, option_type, days_to_expiration, trade_horizon)
        swing_recommendation = get_swing_stop_loss(stock, current_price, option_type, days_to_expiration, trade_horizon)
        longterm_recommendation = get_longterm_stop_loss(stock, current_price, option_type, days_to_expiration, trade_horizon)
        
        # Create a result dictionary to store all recommendations
        result = {
            "scalp": scalp_recommendation,
            "swing": swing_recommendation,
            "longterm": longterm_recommendation,
            "trade_horizon": trade_horizon
        }
        
        # Set the primary recommendation based on the trade horizon
        if enhanced_stop:
            result["enhanced"] = enhanced_stop
            
            # If the enhanced stop is of pattern type, use it as primary
            # when it aligns with the trade horizon (or trade horizon is unknown)
            if trade_horizon == "unknown" or enhanced_stop.get("time_horizon") == trade_horizon:
                result["primary"] = enhanced_stop
                # Add note about pattern-based stop loss
                if "pattern" in enhanced_stop:
                    print(f"Using pattern-based stop loss: {enhanced_stop['pattern']} pattern")
        
        # Only set primary if not already set by enhanced stop loss
        if "primary" not in result:
            if trade_horizon == "scalp":
                result["primary"] = scalp_recommendation
                
                # Format the recommendation with proper headers and warnings
                handle_scalp_recommendation(result, current_price, option_type)
                
            elif trade_horizon == "swing":
                result["primary"] = swing_recommendation
                
                # Format the recommendation with proper headers and warnings
                handle_swing_recommendation(result, current_price, option_type)
                
            elif trade_horizon == "longterm":
                result["primary"] = longterm_recommendation
                
                # Format the recommendation with proper headers and warnings
                handle_longterm_recommendation(result, current_price, option_type)
                
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
        
        # Always ensure the trade_horizon is included in the result
        result["trade_horizon"] = trade_horizon
        
        # If we have the expiration date, only include recommendations appropriate for the timeframe
        if days_to_expiration is not None:
            # Filter recommendations based on expiration date
            filtered_result = {"primary": result["primary"], "trade_horizon": trade_horizon}
            
            # Include only relevant timeframe recommendations
            if days_to_expiration <= 2:
                filtered_result["scalp"] = result["scalp"]
            
            if days_to_expiration > 2 and days_to_expiration <= 90:
                filtered_result["swing"] = result["swing"]
            
            if days_to_expiration > 90:
                filtered_result["longterm"] = result["longterm"]
            
            # Add enhanced recommendation if available
            if "enhanced" in result:
                filtered_result["enhanced"] = result["enhanced"]
                
            # Ensure all keys are present to avoid KeyError later
            for key in ["scalp", "swing", "longterm"]:
                if key not in filtered_result:
                    filtered_result[key] = None
                    
            return filtered_result
        
        # Ensure all keys are present to avoid KeyError later
        for key in ["primary", "scalp", "swing", "longterm", "trade_horizon"]:
            if key not in result:
                result[key] = None
                
        return result
    
    except Exception as e:
        print(f"Error in comprehensive stop loss calculation: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        # Fall back to the original implementation if errors occur
        # Get support levels
        support_levels = get_support_levels(stock)
        
        # Determine the appropriate stop loss level based on option type
        stop_loss = None
        if option_type.lower() == 'call':
            # For long calls, we want support level (where price may find support)
            stop_loss = support_levels[0] if support_levels else current_price * 0.95
            
            # Add basic recommendation text - focus on support level
            recommendation = f"📉 **${stop_loss:.2f}** 📉\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({((current_price - stop_loss) / current_price * 100):.1f}% below current price)\\n• Based on significant technical support"
            
            # Create a fallback result with necessary keys
            result = {
                "primary": {
                    "level": stop_loss,
                    "recommendation": recommendation,
                    "option_stop_price": current_price * 0.5,
                    "time_horizon": "swing" if days_to_expiration and 2 < days_to_expiration <= 90 else "unknown"
                },
                "trade_horizon": "swing" if days_to_expiration and 2 < days_to_expiration <= 90 else "unknown",
                "swing": {
                    "level": stop_loss,
                    "recommendation": recommendation,
                    "option_stop_price": current_price * 0.5,
                    "time_horizon": "swing"
                }
            }
            
        else:  # Put options
            # For long puts, we want resistance level (where price may find resistance)
            stop_loss = support_levels[0] if support_levels else current_price * 1.05
            
            # Add basic recommendation text - focus on resistance level
            recommendation = f"📈 **${stop_loss:.2f}** 📈\\n\\n• Stock Price Stop Level: ${stop_loss:.2f} ({((stop_loss - current_price) / current_price * 100):.1f}% above current price)\\n• Based on significant technical resistance"
            
            # Create a fallback result with necessary keys
            result = {
                "primary": {
                    "level": stop_loss,
                    "recommendation": recommendation,
                    "option_stop_price": current_price * 0.5,
                    "time_horizon": "swing" if days_to_expiration and 2 < days_to_expiration <= 90 else "unknown"
                },
                "trade_horizon": "swing" if days_to_expiration and 2 < days_to_expiration <= 90 else "unknown",
                "swing": {
                    "level": stop_loss,
                    "recommendation": recommendation,
                    "option_stop_price": current_price * 0.5,
                    "time_horizon": "swing"
                }
            }
        
        # Ensure all keys are present in the fallback result
        for key in ["scalp", "longterm"]:
            if key not in result:
                result[key] = result["swing"]  # Use swing as fallback for other timeframes
                
        return result

def handle_scalp_recommendation(result, current_price, option_type):
    \"\"\"Format the scalp recommendation with proper headers and warnings\"\"\"
    try:
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
        # Leave the recommendation as is if there's an error

def handle_swing_recommendation(result, current_price, option_type):
    \"\"\"Format the swing recommendation with proper headers and warnings\"\"\"
    try:
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
        # Leave the recommendation as is if there's an error

def handle_longterm_recommendation(result, current_price, option_type):
    \"\"\"Format the longterm recommendation with proper headers and warnings\"\"\"
    try:
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
        # Leave the recommendation as is if there's an error
"""
        
        # Replace the original function with the new one
        content = ''.join(lines)
        updated_content = content.replace(original_function, new_function)
        
        # Check for the handler functions - add them if they don't exist
        if "def handle_scalp_recommendation" not in updated_content:
            # Add these 3 handler helper functions after the get_stop_loss_recommendation function
            handler_functions = """

def handle_scalp_recommendation(result, current_price, option_type):
    """Format the scalp recommendation with proper headers and warnings"""
    try:
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
        # Leave the recommendation as is if there's an error

def handle_swing_recommendation(result, current_price, option_type):
    """Format the swing recommendation with proper headers and warnings"""
    try:
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
        # Leave the recommendation as is if there's an error

def handle_longterm_recommendation(result, current_price, option_type):
    """Format the longterm recommendation with proper headers and warnings"""
    try:
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
        # Leave the recommendation as is if there's an error
"""
            
            # Insert handler functions after the get_stop_loss_recommendation function
            position = end_line
            updated_lines = updated_content.split('\n')
            updated_lines.insert(position, handler_functions)
            updated_content = '\n'.join(updated_lines)
        
        # Write the updated content back to the file
        with open('technical_analysis.py', 'w') as file:
            file.write(updated_content)
            
        print("Successfully applied the comprehensive fix to technical_analysis.py")
        
    except Exception as e:
        print(f"Error applying comprehensive fix: {e}")

if __name__ == "__main__":
    apply_comprehensive_fix()