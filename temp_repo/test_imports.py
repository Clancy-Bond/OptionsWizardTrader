"""
Simple test script to verify imports and datetime functionality.
"""
import datetime
from discord_bot import OptionsBot

def main():
    """Main test function"""
    print("Testing imports and datetime functionality...")
    
    # Test datetime
    now = datetime.datetime.now()
    print(f"Current time: {now}")
    future = now + datetime.timedelta(days=7)
    print(f"Future time: {future}")
    
    # Test basic bot initialization
    print("\nTesting OptionsBot initialization...")
    bot = OptionsBot()
    print("OptionsBot initialized successfully")
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    main()