"""
Test script for date format recognition in the bot's NLP system.
"""
from datetime import datetime
import re
from dateutil import parser

def test_date_formats():
    """Test various date formats to verify correct parsing"""
    test_formats = [
        "Apr 4th 2025",
        "April 4 2025",
        "Apr 4 2025",
        "4 Apr 2025",
        "04/04/2025",
        "2025-04-04"
    ]
    
    # Test the regex pattern match first
    expiration_pattern = r'(?:(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t)?(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)'
    
    for date_str in test_formats:
        print(f"\nTesting date format: '{date_str}'")
        match = re.search(expiration_pattern, date_str, re.IGNORECASE)
        if match:
            print(f"  ✓ Regex matched: {match.group()}")
        else:
            print(f"  ✗ Regex did not match")
        
        # Also test parsing with dateutil
        try:
            # Remove ordinal suffixes (st, nd, rd, th)
            cleaned_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
            print(f"  Cleaned date: '{cleaned_date}'")
            
            parsed_date = parser.parse(cleaned_date)
            formatted_date = parsed_date.strftime('%Y-%m-%d')
            print(f"  ✓ Dateutil parsed to: {formatted_date}")
        except Exception as e:
            print(f"  ✗ Dateutil parsing failed: {str(e)}")
        
        # Try with multiple formats
        date_formats = [
            '%b %d %Y',     # Apr 4 2025
            '%B %d %Y',     # April 4 2025
            '%b %d, %Y',    # Apr 4, 2025
            '%B %d, %Y',    # April 4, 2025
            '%Y-%m-%d',     # 2025-04-04
            '%m/%d/%Y',     # 04/04/2025
            '%d %b %Y',     # 4 Apr 2025
            '%d %B %Y'      # 4 April 2025
        ]
        
        cleaned_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        for fmt in date_formats:
            try:
                parsed = datetime.strptime(cleaned_date, fmt)
                print(f"  ✓ Format '{fmt}' works: {parsed.strftime('%Y-%m-%d')}")
                break
            except ValueError:
                continue
        else:
            print(f"  ✗ None of the manual formats matched")

if __name__ == "__main__":
    test_date_formats()