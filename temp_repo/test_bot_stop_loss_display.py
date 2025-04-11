"""
Test script to directly test the stop loss request handler in the Discord bot,
bypassing channel restrictions and NLP processing.
"""

import asyncio
import datetime
import discord
import os
from dotenv import load_dotenv
from discord_bot import OptionsBot

async def test_stop_loss_handler_directly():
    """
    Test the handle_stop_loss_request method directly with different expiration dates.
    This bypasses the channel restrictions and NLP processing.
    """
    bot = OptionsBot()
    
    # Test cases with different expirations (today through 180 days)
    today = datetime.datetime.now().date()
    test_cases = [
        {"ticker": "SPY", "strike": 500, "option_type": "call", "expiration": today.strftime("%Y-%m-%d"), "days": 0, "desc": "expiring today"},
        {"ticker": "SPY", "strike": 500, "option_type": "call", "expiration": (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d"), "days": 1, "desc": "expiring tomorrow"},
        {"ticker": "SPY", "strike": 500, "option_type": "call", "expiration": (today + datetime.timedelta(days=2)).strftime("%Y-%m-%d"), "days": 2, "desc": "expiring in 2 days"},
        {"ticker": "SPY", "strike": 500, "option_type": "call", "expiration": (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "days": 7, "desc": "expiring in 7 days"},
        {"ticker": "SPY", "strike": 500, "option_type": "call", "expiration": (today + datetime.timedelta(days=30)).strftime("%Y-%m-%d"), "days": 30, "desc": "expiring in 30 days"},
        {"ticker": "SPY", "strike": 500, "option_type": "call", "expiration": (today + datetime.timedelta(days=90)).strftime("%Y-%m-%d"), "days": 90, "desc": "expiring in 90 days"},
        {"ticker": "SPY", "strike": 500, "option_type": "call", "expiration": (today + datetime.timedelta(days=180)).strftime("%Y-%m-%d"), "days": 180, "desc": "expiring in 180 days"},
        {"ticker": "SPY", "strike": 500, "option_type": "put", "expiration": (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d"), "days": 1, "desc": "PUT expiring tomorrow"},
        {"ticker": "SPY", "strike": 500, "option_type": "put", "expiration": (today + datetime.timedelta(days=30)).strftime("%Y-%m-%d"), "days": 30, "desc": "PUT expiring in 30 days"}
    ]
    
    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.author = MockUser()
            self.channel = MockChannel()
        
        async def reply(self, content=None, embed=None, view=None, mention_author=True):
            print(f"\n\n===== BOT RESPONSE FOR: {self.content} =====")
            if embed:
                print(f"Title: {embed.title}")
                print(f"Description: {embed.description}")
                print("\nFields:")
                for field in embed.fields:
                    print(f"\n--- {field.name} ---")
                    print(field.value)
                if hasattr(embed, 'footer') and embed.footer:
                    print(f"\nFooter: {embed.footer.text}")
            return None
    
    class MockUser:
        def __init__(self):
            self.id = 12345
            self.name = "Test User"
            self.display_name = "Test User"
    
    class MockChannel:
        async def send(self, content=None, embed=None, view=None):
            print(f"\n\n===== BOT RESPONSE CHANNEL MESSAGE =====")
            if embed:
                print(f"Title: {embed.title}")
                print(f"Description: {embed.description}")
                print("\nFields:")
                for field in embed.fields:
                    print(f"\n--- {field.name} ---")
                    print(field.value)
                if hasattr(embed, 'footer') and embed.footer:
                    print(f"\nFooter: {embed.footer.text}")
            return None
    
    # Process each test case by calling handle_stop_loss_request directly
    for case in test_cases:
        print(f"\n{'='*50}")
        print(f"TESTING: SPY ${case['strike']} {case['option_type'].upper()} {case['desc']} ({case['expiration']})")
        print(f"{'='*50}")
        
        # Create mock message
        mock_message = MockMessage(f"What's the stop loss for {case['ticker']} ${case['strike']} {case['option_type']}s {case['desc']}?")
        
        # Create info dictionary manually (bypass NLP)
        info = {
            "type": "stop_loss",
            "ticker": case["ticker"],
            "strike_price": case["strike"],
            "option_type": case["option_type"],
            "expiration_date": case["expiration"]
        }
        
        # Call the handler directly
        try:
            await bot.handle_stop_loss_request(mock_message, info)
        except Exception as e:
            print(f"ERROR: {str(e)}")
        
        print("\n" + "-"*80)
        
        # Pause between requests to avoid rate limits
        await asyncio.sleep(1)

def main():
    asyncio.run(test_stop_loss_handler_directly())

if __name__ == "__main__":
    main()