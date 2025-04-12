#!/usr/bin/env python3
"""
Script to update the formatting of unusual options activity in polygon_integration.py
"""
import re

def update_file():
    """Apply all required formatting changes to the polygon_integration.py file"""
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # 1. Update bullish activity format to include "strongly" and "Inc."
    # Replace "I'm seeing bullish activity for" with "I'm seeing strongly bullish activity for {ticker}, Inc."
    content = re.sub(
        r"• I'm seeing bullish activity for ([^.]+)\.",
        r"• I'm seeing strongly bullish activity for \1, Inc.",
        content
    )
    
    # 2. Bold "million bullish" and "million bearish" statements
    content = re.sub(
        r"(\$\d+\.\d+) million (bullish|bearish)",
        r"\1 **million \2**",
        content
    )
    
    # 3. Fix timestamp to only show date (MM/DD/YY) without time
    content = re.sub(
        r"occurred at (\d{2}/\d{2}/\d{2}) \d{2}:\d{2}:\d{2}",
        r"occurred on \1",
        content
    )
    
    # 4. Format options information as "in-the-money ($245.00)"
    content = re.sub(
        r"(\d+)-the-money",
        r"in-the-money ($\1.00)",
        content
    )
    
    # Clean up any potential double spaces or formatting issues
    content = content.replace("  ", " ")
    
    with open('polygon_integration.py', 'w') as file:
        file.write(content)
    
    print("Updated polygon_integration.py with new formatting")

if __name__ == "__main__":
    update_file()