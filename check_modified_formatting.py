#!/usr/bin/env python3
"""
Script to check if formatting strings in polygon_integration.py were properly updated
"""

def check_file():
    """Check for specific formats in the polygon_integration.py file"""
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # Specific strings we expect to find after our updates
    expected_formats = [
        ("**million bullish**", "Bolded 'million bullish'"),
        ("**million bearish**", "Bolded 'million bearish'"),
        ("occurred on {timestamp_str.split()[0]}", "Date format with only date"),
        ("strongly bullish activity for {ticker}, Inc.", "Strongly bullish format with Inc."),
        ("strongly bearish activity for {ticker}, Inc.", "Strongly bearish format with Inc."),
        ("in-the-money (${contract_parts[0]}.00)", "In-the-money with price format")
    ]
    
    print("\n===== FORMATTING VERIFICATION =====\n")
    
    for expected_string, description in expected_formats:
        if expected_string in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")
    
    print("\n===== CODE PREVIEW =====\n")
    
    # Show a snippet of relevant code for visual verification
    import re
    bullish_section = re.search(r'summary \+= f"• I\'m seeing strongly bullish activity for.*?\n', content)
    bearish_section = re.search(r'summary \+= f"• I\'m seeing strongly bearish activity for.*?\n', content)
    
    if bullish_section:
        print("Bullish Format Preview:")
        print(bullish_section.group(0))
    
    if bearish_section:
        print("\nBearish Format Preview:")
        print(bearish_section.group(0))

if __name__ == "__main__":
    check_file()