#!/usr/bin/env python3
"""
Fix the purchase date to use the actual trade date rather than the expiration date
"""
import re

def update_purchase_date():
    """
    Update the polygon_integration.py file to ensure we always use the actual purchase date
    from the trade data
    """
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # 1. First, make sure timestamp extraction from trade data is working correctly
    # Look for the timestamp extraction code and ensure it's correct
    timestamp_section = re.search(r'# Store the timestamp.*?timestamp_str = "".*?if \'timestamp_human\' in main_trade:.*?timestamp_str = main_trade\[\'timestamp_human\'\]', content, re.DOTALL)
    
    if timestamp_section:
        # Timestamp extraction looks good, now let's update the format strings
        
        # 2. Modify the bullish section to correctly use the timestamp
        bullish_section = re.search(r'if overall_sentiment == "bullish":(.*?)elif overall_sentiment == "bearish":', content, re.DOTALL)
        if bullish_section:
            bullish_text = bullish_section.group(1)
            
            # Find parts that need to be modified
            option_expiry_pattern = re.search(r'summary \+= f".*?options expiring on \{expiry_date\}\.', bullish_text)
            if option_expiry_pattern:
                # Get the old format string
                old_format = option_expiry_pattern.group(0)
                
                # Replace with format that adds the purchase date
                new_format = old_format.rstrip('.') + f", purchased {{timestamp_str if timestamp_str else 'recently'}}."
                
                # Update the bullish section
                modified_bullish_text = bullish_text.replace(old_format, new_format)
                
                # Also update the format for options expiring soon (not specific date)
                option_soon_pattern = re.search(r'summary \+= f".*?options expiring soon\.', modified_bullish_text)
                if option_soon_pattern:
                    old_soon_format = option_soon_pattern.group(0)
                    new_soon_format = old_soon_format.rstrip('.') + f", purchased {{timestamp_str if timestamp_str else 'recently'}}."
                    modified_bullish_text = modified_bullish_text.replace(old_soon_format, new_soon_format)
                
                # Update the content
                content = content.replace(bullish_text, modified_bullish_text)
        
        # 3. Modify the bearish section to correctly use the timestamp
        bearish_section = re.search(r'elif overall_sentiment == "bearish":(.*?)else:', content, re.DOTALL)
        if bearish_section:
            bearish_text = bearish_section.group(1)
            
            # Find parts that need to be modified
            option_expiry_pattern = re.search(r'summary \+= f".*?options expiring on \{expiry_date\}\.', bearish_text)
            if option_expiry_pattern:
                # Get the old format string
                old_format = option_expiry_pattern.group(0)
                
                # Replace with format that adds the purchase date
                new_format = old_format.rstrip('.') + f", purchased {{timestamp_str if timestamp_str else 'recently'}}."
                
                # Update the bearish section
                modified_bearish_text = bearish_text.replace(old_format, new_format)
                
                # Also update the format for options expiring soon (not specific date)
                option_soon_pattern = re.search(r'summary \+= f".*?options expiring soon\.', modified_bearish_text)
                if option_soon_pattern:
                    old_soon_format = option_soon_pattern.group(0)
                    new_soon_format = old_soon_format.rstrip('.') + f", purchased {{timestamp_str if timestamp_str else 'recently'}}."
                    modified_bearish_text = modified_bearish_text.replace(old_soon_format, new_soon_format)
                
                # Update the content
                content = content.replace(bearish_text, modified_bearish_text)
    
    # 4. Update the 'occurred at' sections to remove the timestamp from this part (it's redundant now)
    occurred_at_pattern = r'summary \+= f"occurred at \{timestamp_str\} with '
    content = content.replace(occurred_at_pattern, 'summary += f"with ')
    
    # Write back the updated content
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Updated the purchase date format to use the actual trade date from the Polygon data")

if __name__ == "__main__":
    update_purchase_date()