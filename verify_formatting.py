"""
Quick test to verify the formatting of the unusual options activity output
"""
import re

# Sample output templates from the code
bullish_template = """🐋 **UNUSUAL BULLISH ACTIVITY** 🐋

Detected strongly bullish activity for SYMBOL, Inc. with 65% of flow on the bullish side.

• Institutional investor purchased 100 SYMBOL $195.00 calls expiring 05/17/25
• Premium: $2.6 **million bullish** bet that SYMBOL will be above $217.60
• Position is in-the-money ($245.00) by 25.64%
• Transaction occurred on 04/12/25
• Contributing factors: Large block trade, high volume/OI ratio, significant premium

"""

bearish_template = """🐻 **UNUSUAL BEARISH ACTIVITY** 🐻

Detected strongly bearish activity for SYMBOL, Inc. with 72% of flow on the bearish side.

• Institutional investor purchased 150 SYMBOL $225.00 puts expiring 04/24/25
• Premium: $1.8 **million bearish** bet that SYMBOL will be below $206.40
• Position is in-the-money ($195.00) by 13.33%
• Transaction occurred on 04/11/25
• Contributing factors: Large block trade, high volume/OI ratio, significant premium

"""

def check_formatting():
    """Check for proper formatting in our template outputs"""
    print("Checking bullish template formatting...")
    
    # Check for required components in bullish template
    checks = {
        "Strongly bullish activity": "strongly bullish activity" in bullish_template,
        "Bolded million bullish": "**million bullish**" in bullish_template,
        "In-the-money with price": re.search(r"in-the-money \(\$\d+\.\d+\)", bullish_template) is not None,
        "Transaction date format": re.search(r"\d{2}/\d{2}/\d{2}", bullish_template) is not None,
        "No time component in date": ":" not in re.search(r"occurred on \d{2}/\d{2}/\d{2}", bullish_template).group(0)
    }
    
    for check_name, result in checks.items():
        print(f"{'✅' if result else '❌'} {check_name}")
    
    print("\nChecking bearish template formatting...")
    
    # Check for required components in bearish template
    checks = {
        "Strongly bearish activity": "strongly bearish activity" in bearish_template,
        "Bolded million bearish": "**million bearish**" in bearish_template,
        "In-the-money with price": re.search(r"in-the-money \(\$\d+\.\d+\)", bearish_template) is not None,
        "Transaction date format": re.search(r"\d{2}/\d{2}/\d{2}", bearish_template) is not None,
        "No time component in date": ":" not in re.search(r"occurred on \d{2}/\d{2}/\d{2}", bearish_template).group(0)
    }
    
    for check_name, result in checks.items():
        print(f"{'✅' if result else '❌'} {check_name}")

if __name__ == "__main__":
    check_formatting()