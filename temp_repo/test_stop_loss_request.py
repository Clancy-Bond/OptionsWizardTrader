"""
This script tests the handle_stop_loss_request method directly using a mock Discord message
"""
import asyncio
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up our own handler for unhandled exceptions
def my_excepthook(type, value, tb):
    logger.error("Unhandled exception: %s", str(value))
    logger.error("".join(traceback.format_exception(type, value, tb)))
    sys.__excepthook__(type, value, tb)

sys.excepthook = my_excepthook

async def test_handle_stop_loss_request():
    """
    Directly test the handle_stop_loss_request method with various inputs
    """
    # Import the bot functionality from discord_bot.py
    from discord_bot import OptionsBot
    
    # Create a mock message and user for testing
    class MockUser:
        def __init__(self, id=123456789):
            self.id = id
            self.name = "TestUser"
            self.mention = f"<@{id}>"
    
    class MockMessage:
        def __init__(self, content, author=None):
            self.content = content
            self.author = author or MockUser()
            self.channel = MockChannel()
        
        async def reply(self, content=None, embed=None):
            if embed:
                logger.info(f"Reply embed title: {embed.title}")
                fields = []
                for field in getattr(embed, '_fields', []):
                    fields.append(f"{field.name}: {field.value[:30]}...")
                logger.info(f"Embed fields: {fields}")
                return True
            elif content:
                logger.info(f"Reply content: {content[:100]}...")  # First 100 chars
                return True
            return False
    
    class MockChannel:
        async def send(self, content=None, embed=None):
            if embed:
                logger.info(f"Channel send embed title: {embed.title}")
                fields = []
                for field in getattr(embed, '_fields', []):
                    fields.append(f"{field.name}: {field.value[:30]}...")
                logger.info(f"Embed fields: {fields}")
                return True
            elif content:
                logger.info(f"Channel send content: {content[:100]}...")  # First 100 chars
                return True
            return False
    
    # Create the bot instance
    bot = OptionsBot()
    
    # Test params for direct test of handle_stop_loss_request
    message = MockMessage("What's a good stop loss for TSLA $270 calls expiring Apr 11th 2025?")
    info = {
        'ticker': 'TSLA', 
        'option_type': 'call', 
        'strike': 270.0, 
        'expiration': '2025-04-11', 
        'contract_count': 1
    }
    
    logger.info("Directly testing handle_stop_loss_request method")
    logger.info(f"Ticker: {info['ticker']}, Strike: ${info['strike']}, Type: {info['option_type']}, Expiry: {info['expiration']}")
    
    try:
        # Call the handler method directly
        logger.info("Calling handle_stop_loss_request method...")
        embed = await bot.handle_stop_loss_request(message, info)
        
        logger.info(f"Return value type: {type(embed)}")
        logger.info(f"Return value repr: {repr(embed)}")
        
        if embed:
            logger.info(f"✅ Test passed - handle_stop_loss_request returned an embed")
            logger.info(f"Embed title: {embed.title if hasattr(embed, 'title') else 'No title'}")
            logger.info(f"Description preview: {embed.description[:100] if hasattr(embed, 'description') else 'No description'}")
            
            # Test with multiple contracts
            info['contract_count'] = 5
            logger.info("\nTesting with 5 contracts")
            
            embed = await bot.handle_stop_loss_request(message, info)
            
            if embed:
                logger.info(f"✅ Test passed with multiple contracts")
                logger.info(f"Embed title: {embed.title if hasattr(embed, 'title') else 'No title'}")
                logger.info(f"Description preview: {embed.description[:100] if hasattr(embed, 'description') else 'No description'}")
            else:
                logger.error("❌ Test failed with multiple contracts - no embed returned")
                logger.error(f"Return value type: {type(embed)}")
                logger.error(f"Return value repr: {repr(embed)}")
            
            return True
        else:
            logger.error("❌ Test failed - no embed returned")
            logger.error(f"Return value type: {type(embed)}")
            logger.error(f"Return value repr: {repr(embed)}")
            return False
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    """
    Run the tests
    """
    logger.info("Starting stop loss request tests")
    
    success = await test_handle_stop_loss_request()
    
    if success:
        logger.info("✅ All stop loss request tests passed successfully!")
        return 0
    else:
        logger.error("❌ Some stop loss request tests failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)