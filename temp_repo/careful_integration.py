"""
Careful integration of enhanced ATR-based stop loss into technical_analysis.py

This script adds the functions from enhanced_atr_stop_loss.py to technical_analysis.py
while ensuring no indentation issues occur.
"""

def integrate_carefully():
    """Carefully integrate enhanced ATR stop loss into technical_analysis.py"""
    
    # First, add the import at the top of the file
    with open("technical_analysis.py", "r") as file:
        ta_content = file.read()
    
    new_imports = """import yfinance as yf
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import datetime
"""

    # Read the enhanced ATR stop loss functions (without imports)
    with open("enhanced_atr_stop_loss.py", "r") as file:
        enhanced_content = file.read()
        
    # Remove existing imports and module docstring
    enhanced_content = enhanced_content.split("import datetime", 1)[1]
    
    # Add the enhanced functions to technical_analysis.py
    updated_content = ta_content.replace(new_imports, new_imports + "\n" + enhanced_content)
    
    # Now, modify get_stop_loss_recommendation to use the enhanced functions
    # Find where it calculates the recommendations
    recommendation_section = """        # Get recommendations for all timeframes
        scalp_recommendation = get_scalp_stop_loss(stock, current_price, option_type, days_to_expiration)
        swing_recommendation = get_swing_stop_loss(stock, current_price, option_type, days_to_expiration)
        longterm_recommendation = get_longterm_stop_loss(stock, current_price, option_type, days_to_expiration)"""
    
    enhanced_section = """        # First, try to get pattern-based stop loss using the enhanced system
        enhanced_stop = get_enhanced_stop_loss(stock, current_price, option_type, days_to_expiration)
        
        # Get standard recommendations 
        scalp_recommendation = get_scalp_stop_loss(stock, current_price, option_type, days_to_expiration)
        swing_recommendation = get_swing_stop_loss(stock, current_price, option_type, days_to_expiration)
        longterm_recommendation = get_longterm_stop_loss(stock, current_price, option_type, days_to_expiration)"""
    
    updated_content = updated_content.replace(recommendation_section, enhanced_section)
    
    # Update the result dictionary creation to include enhanced stop
    result_dict_section = """        # Create a result dictionary to store all recommendations
        result = {
            "scalp": scalp_recommendation,
            "swing": swing_recommendation,
            "longterm": longterm_recommendation,
            "trade_horizon": trade_horizon
        }"""
    
    enhanced_result_dict = """        # Create a result dictionary to store all recommendations
        result = {
            "scalp": scalp_recommendation,
            "swing": swing_recommendation,
            "longterm": longterm_recommendation,
            "trade_horizon": trade_horizon
        }
        
        # If enhanced stop loss was found, add it to the result and prioritize it
        if enhanced_stop:
            result["enhanced"] = enhanced_stop
            
            # If the enhanced stop is of pattern type, use it as primary
            # when it aligns with the trade horizon (or trade horizon is unknown)
            if trade_horizon == "unknown" or enhanced_stop["time_horizon"] == trade_horizon:
                result["primary"] = enhanced_stop
                # Add note about pattern-based stop loss
                print(f"Using pattern-based stop loss: {enhanced_stop['pattern']} pattern")"""
    
    updated_content = updated_content.replace(result_dict_section, enhanced_result_dict)
    
    # Update the primary recommendation section to check for enhanced stop first
    primary_section = """        # Set the primary recommendation based on the trade horizon
        if trade_horizon == "scalp":"""
    
    enhanced_primary = """        # Set the primary recommendation based on the trade horizon
        # Only set if not already set by enhanced stop loss
        if "primary" not in result:
            if trade_horizon == "scalp":"""
    
    updated_content = updated_content.replace(primary_section, enhanced_primary)
    
    # Add candle close validation to the wrapper function
    wrapper_function_end = """        print(f"DEBUG: Adapted result: {adapted_result}")
        
        return adapted_result"""
    
    enhanced_wrapper_end = """        print(f"DEBUG: Adapted result: {adapted_result}")
        
        # Add candle close validation information
        if "level" in adapted_result:
            stop_level = adapted_result["level"]
            candle_close_validation = validate_candle_close_beyond_stop(stock, stop_level, option_type)
            adapted_result["requires_candle_close"] = True
            adapted_result["candle_close_validated"] = candle_close_validation
            
            # Add note about candle close validation
            if "recommendation" in adapted_result:
                adapted_result["recommendation"] += "\\n\\n⚠️ IMPORTANT: Stop loss triggers ONLY on candle CLOSE beyond stop level (not just wick touches)."
        
        return adapted_result"""
    
    updated_content = updated_content.replace(wrapper_function_end, enhanced_wrapper_end)
    
    # Write the updated content to technical_analysis.py
    with open("technical_analysis.py", "w") as file:
        file.write(updated_content)
    
    print("Enhanced ATR-based stop loss carefully integrated into technical_analysis.py")

if __name__ == "__main__":
    integrate_carefully()