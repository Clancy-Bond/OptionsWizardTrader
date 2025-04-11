import streamlit as st
import os
from dotenv import load_dotenv
import discord_bot_config

# Load environment variables
load_dotenv()

# Set page title and layout
st.set_page_config(
    page_title="Unusual Options Bot Dashboard",
    page_icon="🐳",
    layout="wide"
)

# Title and description
st.title("Unusual Options Bot Dashboard")

# Main content
st.markdown("""
## Welcome to the Unusual Options Bot Dashboard

This platform helps you configure the Unusual Options Bot, which detects and reports unusual options activity in the stock market.

### Key Features:

1. **Unusual Activity Detection**: Identify potential market-moving options activity
2. **Discord Bot Integration**: Interact with the options data through natural language on Discord
3. **Real-time Data**: Uses current market data to track unusual options flow

### Getting Started:

- Configure your **Discord Bot** to connect with your Discord server and set channel access permissions
- Ask the bot questions in your Discord server about unusual options activity for any ticker
""")

# Discord bot status
st.header("Discord Bot Status")

# Check if Discord token is configured
discord_token = os.getenv('DISCORD_TOKEN')
if discord_token:
    st.success("✅ Discord Bot is configured and ready to use")
    
    # Display invitation URL (placeholder - will be generated properly in the config page)
    st.markdown("**[Go to Discord Bot Configuration →](/Discord_Bot_Config)**")
    
    # Run the bot
    st.markdown("""
    ### Running the Bot
    
    To run your Unusual Options Bot, use this command in your terminal:
    ```
    python run_bot.py
    ```
    
    This will start the bot and connect it to Discord. Make sure your Discord token is properly configured.
    """)
else:
    st.error("❌ Discord Bot is not configured")
    st.markdown("Please go to the **Discord Bot Configuration** page to set up your bot token.")
    
    # Link to config
    if st.button("Go to Discord Bot Configuration"):
        import discord_bot_config

# Quick links
st.header("Quick Navigation")

if st.button("Configure Discord Bot"):
    import discord_bot_config

# Add a footer with disclaimer
st.markdown("---")
st.markdown("""
**Disclaimer:** This tool provides information based on current market data.
Options trading involves significant risk, and unusual activity detection is for informational purposes only.
This is not financial advice. Always do your own research before making investment decisions.
""")

# If this is the main file being run, import and run the config
if __name__ == "__main__":
    import discord_bot_config