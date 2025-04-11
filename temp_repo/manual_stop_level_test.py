"""
Simple script to manually test the stop level percentage display by analyzing the Discord bot log
"""

def check_percentage_display():
    """Look through the discord_bot.log file for responses containing stop level info"""
    try:
        with open('discord_bot.log', 'r') as f:
            log_content = f.read()
        
        # Look for stop level percentages in responses
        if "Stock Price Stop Level" in log_content:
            print("Found stop level entries in log file")
            
            # Check if the percentage is displayed in the format we want
            if "% below current price" in log_content or "% above current price" in log_content:
                print("✅ SUCCESS: Stop level percentage is displayed correctly!")
                return True
            else:
                print("❌ ERROR: Stop level percentage is not displayed correctly")
                return False
        else:
            print("No stop level entries found in log file")
            return False
    except Exception as e:
        print(f"Error checking log file: {e}")
        return False

if __name__ == "__main__":
    check_percentage_display()