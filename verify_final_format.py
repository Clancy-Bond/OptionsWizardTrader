"""
Verify the final formatting of unusual options activity
"""
import polygon_integration

def test_unusual_activity_format():
    """Test the unusual options activity formatting directly"""
    ticker = "TSLA"
    print(f"Testing unusual options activity format for {ticker}...")
    
    result = polygon_integration.get_simplified_unusual_activity_summary(ticker)
    print("\nOutput format:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    print("\nChecking for key formatting elements:")
    
    # Check for bullish/bearish with no newline
    if "million bullish**\n" in result or "million bearish**\n" in result:
        print("❌ Found newline after 'million bullish/bearish'")
    else:
        print("✅ No newline after 'million bullish/bearish'")
    
    # Check for proper strike price format
    if "(TSLA)" in result or "($TSLA)" in result:
        print("❌ Found incorrect stock symbol in strike price")
    elif "(.00)" in result:
        print("✅ Strike price formatted correctly with .00")
    
    # Check for proper expiration date format
    if "expiring on" in result:
        print("❌ Found 'expiring on' instead of just 'expiring'")
    else:
        print("✅ Expiration date formatted correctly without 'on'")
    
    # Check for purchase date
    if "purchased" in result:
        print("✅ Purchase date included")
    else:
        print("❌ Purchase date missing")

if __name__ == "__main__":
    test_unusual_activity_format()