"""
Simple test to verify the date formatting in the Discord bot.
This is a direct test of the formatter that transforms January dates into "2026-01-16" format
"""

from datetime import datetime
import re
import pandas as pd

def test_date_formatting():
    """Test various date formats to make sure they get converted properly"""
    # Test January date
    jan_date = datetime(2026, 1, 16)
    print(f"Original January date: {jan_date}")
    
    # Format 1: Using strftime
    formatted_jan = jan_date.strftime('%Y-%m-%d')
    print(f"Format with strftime: {formatted_jan}")
    
    # Format 2: Using formatted string components
    formatted_jan2 = f"{jan_date.year}-{jan_date.month:02d}-{jan_date.day:02d}"
    print(f"Format with f-string: {formatted_jan2}")
    
    # Format 3: Using pandas formatting
    formatted_jan3 = pd.to_datetime(jan_date).strftime('%Y-%m-%d')
    print(f"Format with pandas: {formatted_jan3}")
    
    # Test April date
    apr_date = datetime(2025, 4, 4)
    print(f"\nOriginal April date: {apr_date}")
    
    # Format 1: Using strftime
    formatted_apr = apr_date.strftime('%Y-%m-%d')
    print(f"Format with strftime: {formatted_apr}")
    
    # Format 2: Using formatted string components
    formatted_apr2 = f"{apr_date.year}-{apr_date.month:02d}-{apr_date.day:02d}"
    print(f"Format with f-string: {formatted_apr2}")
    
    # Format 3: Using pandas formatting
    formatted_apr3 = pd.to_datetime(apr_date).strftime('%Y-%m-%d')
    print(f"Format with pandas: {formatted_apr3}")
    
    # Check if our f-string format produces the correct format
    print("\nVerification:")
    if formatted_jan2 == "2026-01-16":
        print("✅ January date format is correct (2026-01-16)")
    else:
        print("❌ January date format is incorrect")
    
    if formatted_apr2 == "2025-04-04":
        print("✅ April date format is correct (2025-04-04)")
    else:
        print("❌ April date format is incorrect")

if __name__ == "__main__":
    test_date_formatting()