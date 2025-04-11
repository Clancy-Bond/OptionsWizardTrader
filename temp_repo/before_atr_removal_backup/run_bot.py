import discord_bot
import os
import sys
import logging
import nltk

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("discord_bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("options_discord_bot")

def setup_nltk():
    """Setup NLTK data required for NLP"""
    try:
        # Download required NLTK data unconditionally to ensure all necessary components are present
        logger.info("Downloading NLTK data...")
        print("Downloading NLTK data...")
        
        # Download the main components we need - these are the only ones actually required
        nltk.download('punkt')
        nltk.download('stopwords')
        
        # Only verify stopwords, skip tokenize since we're using our own tokenizer
        from nltk.corpus import stopwords
        stopwords.words('english')
        
        logger.info("NLTK data downloaded and verified successfully.")
        print("NLTK data downloaded and verified successfully.")
        return True
    except Exception as e:
        logger.error(f"Error setting up NLTK: {str(e)}")
        print(f"Error setting up NLTK: {str(e)}")
        
        # If the error is related to punkt_tab (which doesn't exist as a package),
        # we can continue anyway as punkt is sufficient
        if "punkt_tab" in str(e):
            logger.info("punkt_tab not found, but that's OK. Using punkt instead.")
            print("punkt_tab not found, but that's OK. Using punkt instead.")
            return True
        return False

def main():
    """Run the Discord bot"""
    # First setup NLTK
    logger.info("Setting up NLTK data...")
    print("Setting up NLTK data...")
    if not setup_nltk():
        logger.error("Failed to setup NLTK data. Exiting.")
        print("Failed to setup NLTK data. Exiting.")
        return
    
    # Check if Discord token is available
    if not os.getenv('DISCORD_TOKEN'):
        logger.error("Discord token not found. Please set the DISCORD_TOKEN environment variable.")
        print("Error: Discord token not found.")
        print("Please set the DISCORD_TOKEN environment variable.")
        return
    
    logger.info("Starting Options Discord Bot...")
    print("Starting Options Discord Bot...")
    
    try:
        # Run the bot (this is a blocking call)
        discord_bot.run_discord_bot()
    except Exception as e:
        logger.error(f"Error running Discord bot: {e}")
        print(f"Error running Discord bot: {e}")

if __name__ == "__main__":
    main()