#!/usr/bin/env python3
"""
Script to update the formatting in polygon_integration.py to match the desired output format
"""
import re

def update_formatting():
    """
    Update the unusual activity output in polygon_integration.py to:
    1. Change "bullish activity for TSLA" to "strongly bullish activity for TSLA, Inc."
    2. Change "245-the-money ($TSLA)" to "in-the-money (245.00)"
    3. Add the purchase date at the end
    """
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # First fix the activity description format
    content = content.replace(
        "• I'm seeing bullish activity for {ticker}",
        "• I'm seeing strongly bullish activity for {ticker}, Inc."
    )
    
    content = content.replace(
        "• I'm seeing bearish activity for {ticker}",
        "• I'm seeing strongly bearish activity for {ticker}, Inc."
    )
    
    # Replace the option description format
    # Note: We're now using the strike_price variable from the earlier fix
    bullish_section = re.search(r'if overall_sentiment == "bullish":(.*?)elif overall_sentiment == "bearish":', content, re.DOTALL)
    if bullish_section:
        bullish_text = bullish_section.group(1)
        
        # Replace the "{contract_parts[1]}-the-money" with "in-the-money"
        modified_bullish_text = bullish_text.replace(
            'summary += f"{contract_parts[1]}-the-money (${contract_parts[0]}) options expiring on {expiry_date}.',
            'summary += f"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}, purchased {timestamp_str if timestamp_str else "recently"}.'
        )
        
        # Also replace the fallback format
        modified_bullish_text = modified_bullish_text.replace(
            'summary += f"{contract_parts[1]}-the-money (${contract_parts[0]}) options expiring soon.',
            'summary += f"in-the-money (${strike_price:.2f}) options expiring soon, purchased {timestamp_str if timestamp_str else "recently"}.'
        )
        
        # Update the content
        content = content.replace(bullish_text, modified_bullish_text)
    
    # Do the same for the bearish section
    bearish_section = re.search(r'elif overall_sentiment == "bearish":(.*?)else:', content, re.DOTALL)
    if bearish_section:
        bearish_text = bearish_section.group(1)
        
        # Replace the "{contract_parts[1]}-the-money" with "in-the-money"
        modified_bearish_text = bearish_text.replace(
            'summary += f"{contract_parts[1]}-the-money (${contract_parts[0]}) options expiring on {expiry_date}.',
            'summary += f"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}, purchased {timestamp_str if timestamp_str else "recently"}.'
        )
        
        # Also replace the fallback format
        modified_bearish_text = modified_bearish_text.replace(
            'summary += f"{contract_parts[1]}-the-money (${contract_parts[0]}) options expiring soon.',
            'summary += f"in-the-money (${strike_price:.2f}) options expiring soon, purchased {timestamp_str if timestamp_str else "recently"}.'
        )
        
        # Update the content
        content = content.replace(bearish_text, modified_bearish_text)
    
    # Add bold formatting for premium amounts
    content = content.replace(
        "${premium_in_millions:.1f} million bullish",
        "**${premium_in_millions:.1f} million bullish**"
    )
    
    content = content.replace(
        "${premium_in_millions:.1f} million bearish",
        "**${premium_in_millions:.1f} million bearish**"
    )
    
    # Write back the updated content
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Updated formatting in polygon_integration.py")

if __name__ == "__main__":
    update_formatting()