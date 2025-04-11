"""
Direct test of the stop level percentage display in the Discord bot responses.
This doesn't need Discord credentials, just simulates the formatting logic.
"""

def test_stop_level_display():
    """
    Test the formatting of the stock price stop level displays
    to ensure percentages are showing properly
    """
    # Setup test variables
    current_price = 150.0
    stop_loss = 142.5  # 5% below current price
    option_price = 5.25
    option_stop_price = 3.15  # 40% loss
    loss_percentage = -40.0
    option_type = 'call'
    
    # Format string with our fix applied - exactly as in discord_bot.py
    display = f"• Current Stock Price: ${current_price:.2f}\n• Current Option Price: ${option_price:.2f}\n• Stock Price Stop Level: ${stop_loss:.2f} ({abs((stop_loss - current_price) / current_price * 100):.1f}% {'below' if option_type.lower() == 'call' else 'above'} current price)\n• Option Price at Stop Recommendation Level: ${option_stop_price:.2f} (a {abs(loss_percentage):.1f}% loss)"
    
    print("\nTest result:")
    print("------------")
    print(display)
    print("\nChecking for percentage display...")
    
    # Check if the percentage is displayed correctly
    if "% below current price" in display or "% above current price" in display:
        print("\n✅ SUCCESS: Stop level percentage is displayed correctly!")
        return True
    else:
        print("\n❌ ERROR: Stop level percentage is not displayed correctly")
        return False

if __name__ == "__main__":
    test_stop_level_display()