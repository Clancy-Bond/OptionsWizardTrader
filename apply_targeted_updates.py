#!/usr/bin/env python3
"""
Script to apply specific, targeted updates to polygon_integration.py without breaking indentation
"""

def update_file():
    """Apply very specific find-and-replace operations"""
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # 1. Update "million bullish" to "**million bullish**"
    content = content.replace('million bullish bet that', '**million bullish** bet that')
    content = content.replace('million bullish\nbet', '**million bullish**\nbet')
    
    # 2. Update "million bearish" to "**million bearish**"
    content = content.replace('million bearish bet that', '**million bearish** bet that')
    content = content.replace('million bearish\nbet', '**million bearish**\nbet')
    
    # 3. Change "occurred at" to "occurred on" and format timestamp
    content = content.replace('occurred at {timestamp_str}', 'occurred on {timestamp_str.split()[0]}')
    
    # 4. Improve "in-the-money" formatting 
    content = content.replace('in-the-money (${contract_parts[0]}) options', 'in-the-money (${contract_parts[0]}.00) options')
    
    # 5. Update to "strongly bullish/bearish activity for {ticker}, Inc."
    content = content.replace("bullish activity for {ticker}", "strongly bullish activity for {ticker}, Inc.")
    content = content.replace("bearish activity for {ticker}", "strongly bearish activity for {ticker}, Inc.")
    
    # Write the updated content back to the file
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Applied targeted updates to polygon_integration.py without breaking indentation")

if __name__ == "__main__":
    update_file()