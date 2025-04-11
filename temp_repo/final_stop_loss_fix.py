"""
A final fix for the filtered_result section of the get_stop_loss_recommendation function
"""

def apply_fix():
    """
    Apply a focused fix to the filtered_result section to ensure 'primary' key is properly set
    """
    with open('technical_analysis.py', 'r') as file:
        content = file.read()
    
    # Find the problematic section - the filtered_result initialization
    target = "            # Filter recommendations based on expiration date\n            filtered_result = {\"primary\": result[\"primary\"], \"trade_horizon\": trade_horizon}"
    
    # Replace with a safer version that checks if 'primary' exists in result
    replacement = """            # Filter recommendations based on expiration date
            # First check if we have a primary key in the result
            filtered_result = {"trade_horizon": trade_horizon}
            
            # Only add the primary key from result if it exists, otherwise use swing as default
            if "primary" in result:
                filtered_result["primary"] = result["primary"]
            elif "swing" in result:
                filtered_result["primary"] = result["swing"]
                print("Using swing recommendation as primary (fallback)")"""
    
    content = content.replace(target, replacement)
    
    # Add a debugging checkpoint before the return of filtered_result
    target = "            # Always ensure trade_horizon is in the filtered_result\n            filtered_result['trade_horizon'] = trade_horizon\n            \n            return filtered_result"
    
    replacement = """            # Always ensure trade_horizon is in the filtered_result
            filtered_result['trade_horizon'] = trade_horizon
            
            # Final safety check - if there's still no primary key, we need to ensure it exists
            if 'primary' not in filtered_result:
                # Look for any recommendation we can use as primary
                if 'scalp' in filtered_result:
                    filtered_result['primary'] = filtered_result['scalp']
                    print("Using scalp recommendation as primary (final fallback)")
                elif 'swing' in filtered_result:
                    filtered_result['primary'] = filtered_result['swing']
                    print("Using swing recommendation as primary (final fallback)")
                elif 'longterm' in filtered_result:
                    filtered_result['primary'] = filtered_result['longterm']
                    print("Using longterm recommendation as primary (final fallback)")
                else:
                    # Create a very basic primary recommendation as absolute last resort
                    filtered_result['primary'] = {
                        "level": current_price * 0.95 if option_type.lower() == 'call' else current_price * 1.05,
                        "recommendation": f"📊 **Stock Price Stop Level: ${current_price * 0.95 if option_type.lower() == 'call' else current_price * 1.05:.2f}** 📊",
                        "time_horizon": trade_horizon
                    }
                    print("Created emergency fallback recommendation as primary")
            
            print(f"Final filtered_result keys: {filtered_result.keys()}")
            return filtered_result"""
    
    content = content.replace(target, replacement)
    
    # Write the fixed content back to the file
    with open('technical_analysis.py', 'w') as file:
        file.write(content)
    
    print("Applied final fix to the filtered_result section")

if __name__ == "__main__":
    apply_fix()