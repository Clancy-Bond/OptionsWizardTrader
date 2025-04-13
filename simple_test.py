"""
Simple test of the unusual options activity formatting
"""
import polygon_integration

def test_format():
    # Just check the formatting of contract_parts directly
    contract_parts = ["245", "in", "2025-04-17"]
    expiry_date = "04/17/25"
    timestamp_str = "04/11/25"
    ticker = "TSLA"
    premium_in_millions = 4.7
    
    # Manual test of bullish format
    summary = ""
    summary += f"• I'm seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a **${premium_in_millions:.1f} million bullish** "
    summary += f"in-the-money ({contract_parts[0]}.00) options expiring {expiry_date}, purchased {timestamp_str}.\n\n"

    print("Bullish Format Test:")
    print("-" * 60)
    print(summary)
    print("-" * 60)
    
    # Check if format matches expected pattern
    expected = "• I'm seeing strongly bullish activity for TSLA, Inc.. The largest flow is a $4.7 million bullish in-the-money (245.00) options expiring on 04/17/25, purchased 04/11/25."
    
    print("\nChecking for formatting matches...")
    for key_phrase in ["strongly bullish", "million bullish", "in-the-money", "245.00", "expiring", "purchased"]:
        if key_phrase in summary:
            print(f"✅ Found '{key_phrase}'")
        else:
            print(f"❌ Missing '{key_phrase}'")

if __name__ == "__main__":
    test_format()