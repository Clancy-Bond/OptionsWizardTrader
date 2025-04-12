import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page title and layout
st.set_page_config(
    page_title="Options AI Assistant",
    page_icon="📊",
    layout="wide"
)

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
discord_token = os.getenv('DISCORD_TOKEN_2')
if discord_token:
    st.success("✅ Discord Bot is configured and ready to use")
    
    # Dynamically generate the invitation URL based on the bot ID
    try:
        # Try to ping the Discord API with the token to check validity
        import requests
        headers = {"Authorization": f"Bot {discord_token}"}
        response = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            bot_id = data.get("id", "")
            if bot_id:
                invitation_url = f"https://discord.com/api/oauth2/authorize?client_id={bot_id}&permissions=379904&scope=bot"
                st.markdown(f"**Bot Invitation URL**: [Click to invite bot to your server]({invitation_url})")
            else:
                st.warning("Could not retrieve bot ID. Please go to Discord Bot Configuration page.")
        else:
            st.warning("Could not connect to Discord API. Please check your token on the Discord Bot Configuration page.")
    except Exception as e:
        st.warning(f"Error connecting to Discord: {str(e)}")
    
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

# Functions needed for the Discord Bot Configuration page
def check_discord_token():
    """Check if Discord token is set in environment variables"""
    token = os.getenv("DISCORD_TOKEN_2")
    return token is not None and token != ""

def update_discord_token(token):
    """Update Discord token in environment variable and .env file"""
    # Update in-memory environment variable
    os.environ["DISCORD_TOKEN_2"] = token
    
    # Update .env file
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            lines = f.readlines()
        
        token_set = False
        for i, line in enumerate(lines):
            if line.startswith("DISCORD_TOKEN_2="):
                lines[i] = f"DISCORD_TOKEN_2={token}\n"
                token_set = True
                break
        
        if not token_set:
            lines.append(f"DISCORD_TOKEN_2={token}\n")
        
        with open(env_file, "w") as f:
            f.writelines(lines)
    else:
        with open(env_file, "w") as f:
            f.write(f"DISCORD_TOKEN_2={token}\n")
    
    return True
