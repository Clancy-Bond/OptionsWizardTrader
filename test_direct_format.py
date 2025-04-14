"""
Test the formatting directly from Discord bot
This simulates an unusual options activity query and captures the result
"""

import discord_bot
import asyncio
import re

def run_format_checks(content):
    """Run formatting checks on the bot's response"""
    print("\nFORMAT VERIFICATION RESULTS:")
    
    # Define checks to verify proper formatting
    checks = {
        "Strike price format": (
            r'in-the-money \((\d+\.\d+)\)',
            lambda m: f"✅ Found numeric strike price: {m.group(0)}" if m else "❌ Missing numeric strike price"
        ),
        "Expiration date format": (
            r'expiring (\d{2}/\d{2}/\d{2})',
            lambda m: f"✅ Found MM/DD/YY expiration: {m.group(0)}" if m else "❌ Missing MM/DD/YY expiration"
        ),
        "Purchase date": (
            r'purchased (\d{2}/\d{2}/\d{2})',
            lambda m: f"✅ Found purchase date: {m.group(0)}" if m else "❌ Missing purchase date"
        ),
        "No bet wording": (
            r'bullish bet|bearish bet',
            lambda m: "❌ Contains unwanted 'bet' wording" if m else "✅ No 'bet' wording"
        ),
        "No 'occurred at'": (
            r'occurred at',
            lambda m: "❌ Contains unwanted 'occurred at' text" if m else "✅ No 'occurred at' text"
        ),
        "No 'on' before date": (
            r'expiring on',
            lambda m: "❌ Contains unwanted 'expiring on' text" if m else "✅ No 'expiring on' text"
        ),
        "No ticker in strike": (
            r'in-the-money \(\$[A-Z]+',
            lambda m: "❌ Contains ticker symbol in strike price" if m else "✅ No ticker in strike price"
        ),
        "No X-the-money format": (
            r'\d+-the-money',
            lambda m: "❌ Contains X-the-money format" if m else "✅ No X-the-money format"
        ),
        "Has bolded millions": (
            r'\*\*\$\d+\.\d+ million (bullish|bearish)\*\*',
            lambda m: f"✅ Properly bolded millions: {m.group(0)}" if m else "❌ Missing bolded millions"
        )
    }
    
    # Run all checks
    all_passed = True
    for check_name, (pattern, result_fn) in checks.items():
        match = re.search(pattern, content)
        
        # For 'No X' checks, we want match to be None
        expected_match = "No" not in check_name
        
        if (match and expected_match) or (not match and not expected_match):
            print(f"{check_name}: {result_fn(match)}")
        else:
            all_passed = False
            if "No" in check_name:
                # For 'No X' checks, finding a match is a failure
                print(f"{check_name}: ❌ Found forbidden pattern: {match.group(0)}")
            else:
                print(f"{check_name}: {result_fn(match)}")
    
    # Overall result
    if all_passed:
        print("\n✅ ALL FORMAT REQUIREMENTS PASSED!")
    else:
        print("\n❌ SOME FORMAT REQUIREMENTS FAILED!")

class MockMessage:
    """Mock Discord message for testing"""
    default_channel = None  # This will be set later
    
    def __init__(self, content, channel=None):
        self.content = content
        self.response_content = None
        self.response_embed = None
        self.author = MockUser()
        
        # Avoid circular dependency
        if channel is not None:
            self.channel = channel
        else:
            # Use class-level default channel
            self.channel = MockMessage.default_channel

class MockUser:
    """Mock Discord user"""
    def __init__(self, id=54321):
        self.id = id
        self.name = "TestUser"
        
    async def reply(self, content=None, embed=None, mention_author=True):
        """Capture the reply for inspection"""
        print("\nDISCORD BOT RESPONSE:\n")
        self.response_content = content
        
        if content:
            print(content)
        if embed:
            self.response_embed = embed
            print(f"Title: {embed.title}")
            print(f"Description: {embed.description}")
            for field in embed.fields:
                print(f"\n{field.name}: {field.value}")
        
        # Perform format checks on response content
        if content:
            run_format_checks(content)
            
        return self

class MockChannel:
    """Mock Discord channel"""
    def __init__(self, id=12345):
        self.id = id
        
    async def send(self, content=None, embed=None):
        """Capture the sent message for inspection"""
        print("\nDISCORD BOT RESPONSE:\n")
        
        message = MockMessage(content)
        message.response_content = content
        
        if content:
            print(content)
            # Run format checks on the content
            run_format_checks(content)
        if embed:
            message.response_embed = embed
            print(f"Title: {embed.title}")
            print(f"Description: {embed.description}")
            for field in embed.fields:
                print(f"\n{field.name}: {field.value}")
        return message

async def test_unusual_options():
    """Test the unusual options formatting in the Discord bot"""
    print("Testing Discord bot unusual options formatting for TSLA...")
    
    # Create bot instance
    bot = discord_bot.OptionsBot()
    
    # Create NLP processor
    nlp = discord_bot.OptionsBotNLP()
    
    # Parse query
    query = "show me unusual options for TSLA"
    parsed = nlp.parse_query(query)
    
    # Create mock message
    message = MockMessage(query)
    
    # Call the handler directly
    await bot.handle_unusual_activity_request(message, parsed)
    
    # Verify output format
    mock_output = """🐳 TSLA Unusual Options Activity 🐳

• I'm seeing strongly bullish activity for TSLA, Inc.. The largest flow is a **$4.7 million bullish** in-the-money (255.00) options expiring 04/17/25, purchased 04/14/25.

• Institutional Investors are heavily favoring call options with volume 2.3x the put
open interest.

Overall flow: 70% bullish / 30% bearish"""
    
    # Check format requirements
    checks = {
        "Strike price format": (
            r'in-the-money \((\d+\.\d+)\)',
            lambda m: f"✅ Found numeric strike price: {m.group(0)}" if m else "❌ Missing numeric strike price"
        ),
        "Expiration date format": (
            r'expiring (\d{2}/\d{2}/\d{2})',
            lambda m: f"✅ Found MM/DD/YY expiration: {m.group(0)}" if m else "❌ Missing MM/DD/YY expiration"
        ),
        "Purchase date": (
            r'purchased (\d{2}/\d{2}/\d{2})',
            lambda m: f"✅ Found purchase date: {m.group(0)}" if m else "❌ Missing purchase date"
        ),
        "No bet wording": (
            r'bullish bet|bearish bet',
            lambda m: "❌ Contains unwanted 'bet' wording" if m else "✅ No 'bet' wording"
        ),
        "No 'occurred at'": (
            r'occurred at',
            lambda m: "❌ Contains unwanted 'occurred at' text" if m else "✅ No 'occurred at' text"
        ),
        "No 'on' before date": (
            r'expiring on',
            lambda m: "❌ Contains unwanted 'expiring on' text" if m else "✅ No 'expiring on' text"
        ),
        "No ticker in strike": (
            r'in-the-money \(\$[A-Z]+',
            lambda m: "❌ Contains ticker symbol in strike price" if m else "✅ No ticker in strike price"
        ),
        "No X-the-money format": (
            r'\d+-the-money',
            lambda m: "❌ Contains X-the-money format" if m else "✅ No X-the-money format"
        ),
        "Has bolded millions": (
            r'\*\*\$\d+\.\d+ million (bullish|bearish)\*\*',
            lambda m: f"✅ Properly bolded millions: {m.group(0)}" if m else "❌ Missing bolded millions"
        )
    }

def run_test():
    """Run the async test"""
    # Fix circular dependency between MockMessage and MockChannel
    MockMessage.default_channel = MockChannel()
    
    # Set up mock methods needed by test
    def add_auth_mock(bot):
        bot.is_channel_whitelisted = lambda channel_id: True
        bot.is_admin = lambda user_id: True
        return bot
    
    # Monkey patch the discord_bot class to avoid connection issues
    discord_bot.OptionsBot.__init__ = lambda self: setattr(self, '_connection', None)
    
    try:
        # Run the test
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_unusual_options())
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    run_test()