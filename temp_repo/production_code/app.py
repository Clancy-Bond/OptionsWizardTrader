import streamlit as st
import os
from dotenv import load_dotenv
from theme_selector import display_theme_selector

# Load environment variables
load_dotenv()

# Set page title and layout
st.set_page_config(
    page_title="Options AI Assistant",
    page_icon="📊",
    layout="wide"
)

# Display theme selector in sidebar
display_theme_selector()

# Title and description
st.title("Options AI Assistant Dashboard")

# Main content
st.markdown("""
## Welcome to the Options AI Assistant Dashboard

This platform combines a powerful options price calculator with an intelligent Discord bot that helps traders understand their options positions and make informed decisions.

### Key Features:

1. **Options Calculator**: Estimate future option values based on target stock prices
2. **Technical Analysis**: Get support-based stop loss recommendations
3. **Unusual Activity Detection**: Identify potential market-moving options activity
4. **Discord Bot Integration**: Interact with the options calculator through natural language on Discord

### Getting Started:

- Use the **Options Calculator** page to analyze options and estimate profits/losses
- Configure your **Discord Bot** to connect with your Discord server and set channel access permissions
- Ask the bot questions in your Discord server about options prices, stop loss levels, or unusual activity
""")

# Discord bot status
st.header("Discord Bot Status")

# Check if Discord token is configured
discord_token = os.getenv('DISCORD_TOKEN')
if discord_token:
    st.success("✅ Discord Bot is configured and ready to use")
    
    # Display invitation URL (normally this would come from the bot itself)
    invitation_url = "https://discord.com/oauth2/authorize?client_id=1354551896605589584&scope=bot&permissions=379904"
    st.markdown(f"**Bot Invitation URL**: [Click to invite bot to your server]({invitation_url})")
    
    # Quick navigation to Discord configuration
    st.markdown("**[Go to Discord Bot Configuration →](/Discord_Bot_Config)**")
else:
    st.error("❌ Discord Bot is not configured")
    st.markdown("Please go to the **[Discord Bot Configuration](/Discord_Bot_Config)** page to set up your bot token.")

# Quick links
st.header("Quick Navigation")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Tools")
    st.markdown("""
    - [Options Calculator](/Options_Calculator)
    - [Discord Bot Configuration](/Discord_Bot_Config)
    """)

with col2:
    st.subheader("Documentation")
    st.markdown("""
    - [How to use the Options Calculator](#)
    - [Discord Bot Commands](#)
    - [Natural Language Query Format](#)
    """)

# Stats section (This would be populated with real data in a production app)
st.header("Usage Statistics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Calculations Performed", "1,243")
with col2:
    st.metric("Discord Queries", "856")
with col3:
    st.metric("Active Users", "32")

# Add a footer with disclaimer
st.markdown("---")
st.markdown("""
**Disclaimer:** This tool provides estimates based on current market data and mathematical models.
Options trading involves significant risk, and actual results may vary. This is not financial advice.
Always do your own research before making investment decisions.
""")