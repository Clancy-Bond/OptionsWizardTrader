"""
Integrate the enhanced ATR-based stop loss system into technical_analysis.py

This script updates the technical_analysis.py file to:
1. Properly import and use the pattern-based stop loss logic
2. Prioritize pattern-based recommendations when they exist
3. Ensure all stop loss calculations respect ATR-based volatility buffers
4. Validate patterns with volume confirmation (≥ 1.5x average of last 10 candles)
5. Apply buffers specifically for different patterns (10% ATR for breakouts, 5% for engulfing)
"""

import re

def integrate_enhanced_stop_loss():
    """Integrate the enhanced stop loss system into technical_analysis.py"""
    
    print("Integrating enhanced ATR-based stop loss into technical_analysis.py...")
    
    # First, ensure that the imports at the top of technical_analysis.py are correct
    with open("technical_analysis.py", "r") as f:
        technical_content = f.read()
    
    # Check if the imports are already there
    if "from enhanced_atr_stop_loss import" not in technical_content:
        # Add the imports
        import_section = "import yfinance as yf\nimport pandas as pd\nimport numpy as np\nfrom scipy.signal import argrelextrema\nimport datetime\n"
        
        enhanced_imports = import_section + "\n# Import enhanced stop loss module\nfrom enhanced_atr_stop_loss import (\n    calculate_atr,\n    get_volume_confirmation,\n    identify_breakout_candle,\n    identify_engulfing_candle,\n    scale_atr_for_dte,\n    calculate_breakout_stop_loss,\n    calculate_engulfing_stop_loss,\n    validate_candle_close_beyond_stop,\n    get_enhanced_stop_loss\n)\n\n\n"
        
        # Replace the import section with our enhanced version
        technical_content = technical_content.replace(import_section, enhanced_imports)
        
        print("Added enhanced stop loss imports to technical_analysis.py")
    else:
        print("Enhanced stop loss imports already present in technical_analysis.py")
    
    # Now, ensure that the get_stop_loss_recommendation function properly uses the enhanced system
    get_stop_loss_rec_pattern = r"def get_stop_loss_recommendation\(stock, current_price, option_type, expiration=None\):.*?# Get recommendations for all timeframes(.*?)scalp_recommendation = get_scalp_stop_loss"
    
    if "enhanced_stop = get_enhanced_stop_loss" not in technical_content:
        # We need to update the function to use the enhanced stop loss
        replacement = """def get_stop_loss_recommendation(stock, current_price, option_type, expiration=None):
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
        enhanced_stop = get_enhanced_stop_loss(stock, current_price, option_type, days_to_expiration)
        
        # Get standard recommendations 
        scalp_recommendation = get_scalp_stop_loss"""
        
        # Try to replace the function signature and beginning with our enhanced version
        technical_content = re.sub(get_stop_loss_rec_pattern, replacement, technical_content, flags=re.DOTALL)
        
        print("Updated get_stop_loss_recommendation to use enhanced stop loss")
    else:
        print("get_stop_loss_recommendation already uses enhanced stop loss")
    
    # Ensure that the function correctly integrates enhanced stop results
    result_section_pattern = r"# Create a result dictionary to store all recommendations(.*?)result = \{.*?\}"
    
    if "result[\"enhanced\"] = enhanced_stop" not in technical_content:
        # Update the result dictionary creation
        replacement = """        # Create a result dictionary to store all recommendations
        result = {
            "scalp": scalp_recommendation,
            "swing": swing_recommendation,
            "longterm": longterm_recommendation,
            "trade_horizon": trade_horizon
        }
        
        # If enhanced stop loss was found, add it to the result and prioritize it
        if enhanced_stop:
            result["enhanced"] = enhanced_stop
            result["primary"] = enhanced_stop
            print(f"Using pattern-based stop loss: {enhanced_stop['pattern']} pattern")
            
        # If no enhanced stop is available, set the primary recommendation based on trade horizon
        elif trade_horizon != "unknown":
            if trade_horizon == "scalp":
                result["primary"] = scalp_recommendation
            elif trade_horizon == "swing":
                result["primary"] = swing_recommendation
            elif trade_horizon == "longterm":
                result["primary"] = longterm_recommendation
        else:
            # Default to swing if no specific horizon (most common)
            result["primary"] = swing_recommendation"""
        
        # Replace the result dictionary creation section
        technical_content = re.sub(result_section_pattern, replacement, technical_content, flags=re.DOTALL)
        
        print("Updated result dictionary creation to properly prioritize enhanced stop loss")
    else:
        print("Result dictionary already integrates enhanced stop loss")
    
    # Write the updated content back to technical_analysis.py
    with open("technical_analysis.py", "w") as f:
        f.write(technical_content)
    
    print("Integration complete. Enhanced ATR-based stop loss system is now fully integrated.")

if __name__ == "__main__":
    integrate_enhanced_stop_loss()