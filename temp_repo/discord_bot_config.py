import streamlit as st
import os
import json
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Set page title and layout
st.set_page_config(
    page_title="Unusual Options Bot Configuration",
    page_icon="🐳",
    layout="wide"
)

# Custom CSS to make it look more like Discord
st.markdown("""
<style>
    .discord-header {
        background-color: #36393f;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .discord-channel {
        background-color: #2f3136;
        color: #dcddde;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
    }
    .discord-button {
        background-color: #5865F2;
        color: white;
        border: none;
        border-radius: 3px;
        padding: 8px 16px;
        margin: 5px 0;
        cursor: pointer;
    }
    .channel-row {
        display: flex;
        align-items: center;
        padding: 5px 0;
    }
    /* Make checkbox labels more visible */
    .stCheckbox > label > p {
        color: #dcddde !important;
    }
</style>
""", unsafe_allow_html=True)

# Title and description in Discord-like header
st.markdown('<div class="discord-header"><h1>Unusual Options Bot Configuration</h1></div>', unsafe_allow_html=True)
st.markdown("""
This page allows you to configure which Discord channels the Unusual Options Bot can respond in. 
You can add or remove channels from the approved list to control where the bot will interact with your community members.
""")

# Function to load saved permissions
def load_permissions():
    try:
        if os.path.exists("discord_permissions.json"):
            with open("discord_permissions.json", "r") as f:
                return json.load(f)
        return {"approved_channels": []}
    except Exception as e:
        st.error(f"Error loading permissions: {str(e)}")
        return {"approved_channels": []}

# Function to save permissions
def save_permissions(permissions):
    try:
        with open("discord_permissions.json", "w") as f:
            json.dump(permissions, f)
        return True
    except Exception as e:
        st.error(f"Error saving permissions: {str(e)}")
        return False

# Discord token handling
discord_token = os.getenv('DISCORD_TOKEN')

if not discord_token:
    st.error("Discord token not found. Please set the DISCORD_TOKEN environment variable.")
    
    # Discord token input with custom styling
    st.markdown('<div class="discord-header"><h3>Bot Token Setup</h3></div>', unsafe_allow_html=True)
    with st.form("discord_token_form"):
        token_input = st.text_input("Enter your Discord Bot Token", type="password")
        
        # Add some instructions
        st.markdown("""
        To find your bot token:
        1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
        2. Select your application or create a new one
        3. Go to the "Bot" tab
        4. Click "Reset Token" or "Copy" if you already have one
        """)
        
        submit_button = st.form_submit_button("Save Token")
        
        if submit_button and token_input:
            # Create or update the .env file with the token
            with open(".env", "a") as f:
                f.write(f"\nDISCORD_TOKEN={token_input}")
            st.success("Token saved! Please restart the application.")
            st.rerun()
else:
    # Load saved permissions
    if "permissions" not in st.session_state:
        st.session_state.permissions = load_permissions()
    
    # Bot status indicator with Discord styling
    st.markdown('<div class="discord-header"><h3>Bot Status</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Connection Status")
        status_indicator = st.empty()
        
        # Check Discord connection
        try:
            # Try to ping the Discord API with the token to check validity
            headers = {"Authorization": f"Bot {discord_token}"}
            response = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                bot_name = data.get("username", "Unknown")
                bot_id = data.get("id", "Unknown")
                
                status_indicator.success("Connected")
                st.markdown(f"""
                <div style='background-color: #36393f; padding: 10px; border-radius: 5px;'>
                    <div style='display: flex; align-items: center;'>
                        <div style='background-color: #9370DB; width: 40px; height: 40px; border-radius: 50%; 
                                margin-right: 10px; display: flex; justify-content: center; align-items: center; color: white;'>
                            {bot_name[0].upper()}
                        </div>
                        <div>
                            <p style='margin: 0; color: white;'><strong>{bot_name}</strong></p>
                            <p style='margin: 0; color: #dcddde; font-size: 0.8em;'>ID: {bot_id}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Get bot invitation URL
                invitation_url = f"https://discord.com/oauth2/authorize?client_id={bot_id}&scope=bot&permissions=379904"
                st.markdown(f"**Bot Invitation URL**: [Click to invite bot to your server]({invitation_url})")
            else:
                status_indicator.error("Disconnected")
                st.markdown("**Error**: Could not connect to Discord API. Please check your token.")
        except Exception as e:
            status_indicator.error("Error")
            st.markdown(f"**Error**: {str(e)}")
    
    with col2:
        st.markdown("#### Quick Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Reset Bot Token", help="Clear the saved Discord token"):
                with open(".env", "r") as f:
                    lines = f.readlines()
                with open(".env", "w") as f:
                    for line in lines:
                        if not line.startswith("DISCORD_TOKEN="):
                            f.write(line)
                st.warning("Token reset! Please enter a new token.")
                st.rerun()
        
        with col2:
            if st.button("Save All Settings", help="Save all channel permissions"):
                if save_permissions(st.session_state.permissions):
                    st.success("All settings saved successfully!")
        
    # Channel Configuration Section
    st.markdown('<div class="discord-header"><h3>Channel Configuration</h3></div>', unsafe_allow_html=True)
    
    # Get current channels
    current_channels = st.session_state.permissions.get("approved_channels", [])
    
    # Channel management
    with st.form("channel_form"):
        st.markdown("#### Add Approved Channel")
        new_channel = st.text_input("Enter channel name (exactly as it appears in Discord):", 
                                     help="This should be the exact name of the channel, including special characters")
        
        add_button = st.form_submit_button("Add Channel")
        
        if add_button and new_channel:
            if new_channel not in current_channels:
                current_channels.append(new_channel)
                st.session_state.permissions["approved_channels"] = current_channels
                save_permissions(st.session_state.permissions)
                st.success(f"Added channel: {new_channel}")
                st.rerun()
            else:
                st.warning(f"Channel {new_channel} is already in the approved list.")
    
    # Display and manage current channels
    st.markdown("#### Currently Approved Channels")
    
    if not current_channels:
        st.info("No channels are currently approved. The bot will not respond in any channel.")
        st.markdown("""
        **Note:** If you leave the approved channels list empty, the bot will respond in **all** channels it has access to.
        This is not recommended for most servers.
        """)
    else:
        for i, channel in enumerate(current_channels):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class="discord-channel">
                    <span class="channel-icon">#</span> {channel}
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                if st.button("Remove", key=f"remove_{i}"):
                    current_channels.remove(channel)
                    st.session_state.permissions["approved_channels"] = current_channels
                    save_permissions(st.session_state.permissions)
                    st.success(f"Removed channel: {channel}")
                    st.rerun()
    
    # Sample code to show how to use permissions in the bot
    st.markdown('<div class="discord-header"><h3>Implementation Guide</h3></div>', unsafe_allow_html=True)
    
    st.markdown("""
    The bot reads the `discord_permissions.json` file to determine which channels it should respond in.
    This is already implemented in the `unusual_options_bot.py` file.
    
    Here's how the permission system works:
    """)
    
    st.code("""
# In unusual_options_bot.py
def __init__(self):
    self.nlp = UnusualOptionsNLP()
    
    # Define approved channels - leave empty to allow all channels
    self.approved_channels = []
    
    # Load channel restrictions if exists
    try:
        with open('discord_permissions.json', 'r') as f:
            permissions = json.load(f)
            self.approved_channels = permissions.get('approved_channels', [])
            print(f"Loaded approved channels: {self.approved_channels}")
    except Exception as e:
        print(f"Could not load channel permissions: {str(e)}")

async def handle_message(self, message):
    # Check if the message is in an approved channel (if restrictions are set)
    channel_name = message.channel.name if hasattr(message.channel, 'name') else "Unknown"
    
    # If approved_channels is not empty, only respond in those channels
    if self.approved_channels and channel_name not in self.approved_channels:
        print(f"Ignoring message in non-approved channel: {channel_name}")
        return None
    
    # Continue processing the message...
    """, language="python")
    
    st.markdown("""
    **Note:** If the approved channels list is empty, the bot will respond in all channels 
    it has access to. This is useful for small servers or private testing.
    """)

if __name__ == "__main__":
    st.sidebar.title("🐳 Unusual Options Bot")
    st.sidebar.markdown("Configure your bot's channel access")