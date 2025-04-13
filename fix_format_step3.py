#!/usr/bin/env python3
"""
Step 3: Fix the bullish/bearish text and add purchase date
"""

def fix_format_step3():
    """Apply specific change to remove 'bet' and add purchase date"""
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # 1. Fix the bullish text and add purchase date
    bullish_section_start = "if overall_sentiment == \"bullish\":"
    bullish_section_end = "elif overall_sentiment == \"bearish\":"
    
    bullish_start_pos = content.find(bullish_section_start)
    bullish_end_pos = content.find(bullish_section_end, bullish_start_pos)
    
    if bullish_start_pos > 0 and bullish_end_pos > bullish_start_pos:
        bullish_section = content[bullish_start_pos:bullish_end_pos]
        
        # 1.1 Remove "bet" when there's a timestamp
        bet_with_ts = "summary += f\"• I'm seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish** bet\\n\""
        flow_with_ts = "summary += f\"• I'm seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish**\\n\""
        updated_bullish = bullish_section.replace(bet_with_ts, flow_with_ts)
        
        # 1.2 Also remove the "bet with" line in the else clause
        bet_with_line = "summary += f\"bet with \""
        empty_with_line = "# Removed 'bet with'\n                "
        updated_bullish = updated_bullish.replace(bet_with_line, empty_with_line)
        
        # 1.3 Add the purchase date to the end of the options description
        options_expiry = "summary += f\"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}."
        options_with_date = "summary += f\"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}, purchased {timestamp_str if timestamp_str else '04/11/25'}."
        updated_bullish = updated_bullish.replace(options_expiry, options_with_date)
        
        # 1.4 Also add the purchase date to the "expiring soon" format
        options_soon = "summary += f\"in-the-money (${strike_price:.2f}) options expiring soon."
        options_soon_date = "summary += f\"in-the-money (${strike_price:.2f}) options expiring soon, purchased {timestamp_str if timestamp_str else '04/11/25'}."
        updated_bullish = updated_bullish.replace(options_soon, options_soon_date)
        
        # Update the content with our modified bullish section
        content = content.replace(bullish_section, updated_bullish)
    
    # 2. Now do the same for the bearish section
    bearish_section_start = "elif overall_sentiment == \"bearish\":"
    bearish_section_end = "else:"
    
    bearish_start_pos = content.find(bearish_section_start)
    bearish_end_pos = content.find(bearish_section_end, bearish_start_pos)
    
    if bearish_start_pos > 0 and bearish_end_pos > bearish_start_pos:
        bearish_section = content[bearish_start_pos:bearish_end_pos]
        
        # 2.1 Remove "bet" when there's a timestamp
        bet_with_ts = "summary += f\"• I'm seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish** bet\\n\""
        flow_with_ts = "summary += f\"• I'm seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bearish**\\n\""
        updated_bearish = bearish_section.replace(bet_with_ts, flow_with_ts)
        
        # 2.2 Also remove the "bet with" line in the else clause
        bet_with_line = "summary += f\"bet with \""
        empty_with_line = "# Removed 'bet with'\n                "
        updated_bearish = updated_bearish.replace(bet_with_line, empty_with_line)
        
        # 2.3 Add the purchase date to the end of the options description
        options_expiry = "summary += f\"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}."
        options_with_date = "summary += f\"in-the-money (${strike_price:.2f}) options expiring on {expiry_date}, purchased {timestamp_str if timestamp_str else '04/11/25'}."
        updated_bearish = updated_bearish.replace(options_expiry, options_with_date)
        
        # 2.4 Also add the purchase date to the "expiring soon" format
        options_soon = "summary += f\"in-the-money (${strike_price:.2f}) options expiring soon."
        options_soon_date = "summary += f\"in-the-money (${strike_price:.2f}) options expiring soon, purchased {timestamp_str if timestamp_str else '04/11/25'}."
        updated_bearish = updated_bearish.replace(options_soon, options_soon_date)
        
        # Update the content with our modified bearish section
        content = content.replace(bearish_section, updated_bearish)
    
    # 3. Also clean up any "occurred at" lines
    occurred_at = "summary += f\"occurred at {timestamp_str} with "
    with_only = "# Removed 'occurred at' timestamp\n            summary += f\"with "
    content = content.replace(occurred_at, with_only)
    
    # 4. Also for bearish section with more indentation
    occurred_at_bearish = "                summary += f\"occurred at {timestamp_str} with "
    with_only_bearish = "                # Removed 'occurred at' timestamp\n                summary += f\"with "
    content = content.replace(occurred_at_bearish, with_only_bearish)
    
    # Save the changes
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Step 3 complete: Removed 'bet' and added purchase date")

if __name__ == "__main__":
    fix_format_step3()