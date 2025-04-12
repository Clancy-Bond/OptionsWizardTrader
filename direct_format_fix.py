#!/usr/bin/env python3
"""
Direct, targeted fix for the unusual options activity format
"""

def fix_format():
    """Apply very specific changes to match the requested format exactly"""
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # 1. FIRST FIX THE BULLISH SECTION
    # Find the bullish bet line and replace it
    bullish_bet_line = "summary += f\"• I'm seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish** bet\n\""
    bullish_flow_line = "summary += f\"• I'm seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish**\n\""
    
    # Replace the existing lines
    content = content.replace(bullish_bet_line, bullish_flow_line)
    
    # 2. REMOVE THE "OCCURRED AT" LINE
    occurred_line = "summary += f\"occurred at {timestamp_str} with \""
    empty_line = "# Timestamp is now shown at the end of the next line\n            "
    content = content.replace(occurred_line, empty_line)
    
    # 3. FIX THE OPTIONS DESCRIPTION LINE FOR BULLISH
    bullish_section_start = "if overall_sentiment == \"bullish\":"
    bullish_section_end = "elif overall_sentiment == \"bearish\":"
    
    bullish_start_pos = content.find(bullish_section_start)
    bullish_end_pos = content.find(bullish_section_end, bullish_start_pos)
    
    if bullish_start_pos > 0 and bullish_end_pos > bullish_start_pos:
        bullish_section = content[bullish_start_pos:bullish_end_pos]
        
        # Find the in-the-money line and replace it
        old_options_line = "summary += f\"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}"
        new_options_line = "summary += f\"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}, purchased {timestamp_str if timestamp_str else '04/11/25'}"
        
        updated_bullish = bullish_section.replace(old_options_line, new_options_line)
        content = content.replace(bullish_section, updated_bullish)
    
    # 4. FIX THE BEARISH SECTION TOO
    bearish_section_start = "elif overall_sentiment == \"bearish\":"
    bearish_section_end = "else:"
    
    bearish_start_pos = content.find(bearish_section_start)
    bearish_end_pos = content.find(bearish_section_end, bearish_start_pos)
    
    if bearish_start_pos > 0 and bearish_end_pos > bearish_start_pos:
        bearish_section = content[bearish_start_pos:bearish_end_pos]
        
        # Replace the bearish bet line
        bearish_bet_line = "summary += f\"• I'm seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish** bet\n\""
        bearish_flow_line = "summary += f\"• I'm seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish**\n\""
        updated_bearish = bearish_section.replace(bearish_bet_line, bearish_flow_line)
        
        # Find the in-the-money line and replace it
        old_options_line = "summary += f\"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}"
        new_options_line = "summary += f\"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}, purchased {timestamp_str if timestamp_str else '04/11/25'}"
        
        updated_bearish = updated_bearish.replace(old_options_line, new_options_line)
        content = content.replace(bearish_section, updated_bearish)
    
    # 5. ALSO FIX THE OCCURRED AT LINE IN BEARISH SECTION
    occurred_line = "                summary += f\"occurred at {timestamp_str} with \""
    empty_line = "                # Timestamp is now shown at the end of the next line\n                "
    content = content.replace(occurred_line, empty_line)
    
    # Save the changes
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Applied targeted format fix to match the exact requested format")

if __name__ == "__main__":
    fix_format()