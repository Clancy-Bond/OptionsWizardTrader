import streamlit as st
import os
import json
import requests
import re
from dotenv import load_dotenv
from utils.theme_helper import setup_page
from theme_selector import display_theme_selector

# Load environment variables
load_dotenv()

# Set page title and layout
st.set_page_config(
    page_title="Bot Configuration",
    page_icon="🤖",
    layout="wide"
)

# Display theme selector in sidebar
display_theme_selector()

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
    .discord-category {
        background-color: #2f3136;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        font-weight: bold;
    }
    .channel-icon {
        color: #8e9297;
        margin-right: 5px;
    }
    .toggle-container {
        background-color: #36393f;
        padding: 5px 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .server-header {
        background-color: #36393f;
        color: white;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
        font-size: 18px;
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
    .stCheckbox > label {
        color: #dcddde !important;
    }
    /* Make checkbox labels more visible */
    .stCheckbox > label > p {
        color: #dcddde !important;
    }
    /* Style the toggle switches to look like Discord's */
    .stCheckbox > div[role="checkbox"] {
        background-color: #36393f !important;
        border-color: #72767d !important;
    }
    .stCheckbox > div[role="checkbox"][aria-checked="true"] {
        background-color: #5865F2 !important;
        border-color: #5865F2 !important;
    }
</style>
""", unsafe_allow_html=True)

# Title and description in Discord-like header
st.markdown('<div class="discord-header"><h1>Bot Configuration</h1></div>', unsafe_allow_html=True)
st.markdown("""
This page allows you to connect your Options AI Discord bot to your servers and configure which channels it can respond in. 
You can enable or disable the bot in specific channels to control where it will interact with your community members.
""")

# Helper function to fetch Discord servers and channels
def fetch_discord_servers(token):
    """Fetch servers (guilds) the bot is in using Discord API"""
    headers = {"Authorization": f"Bot {token}"}
    
    # Get list of guilds (servers)
    response = requests.get("https://discord.com/api/v10/users/@me/guilds", headers=headers)
    
    if response.status_code != 200:
        st.error(f"Failed to fetch servers: {response.status_code}")
        return None
        
    guilds = response.json()
    
    # Get channels for each guild
    servers_data = {}
    for guild in guilds:
        guild_id = guild["id"]
        guild_name = guild["name"]
        
        # Get channels for this guild
        channels_response = requests.get(
            f"https://discord.com/api/v10/guilds/{guild_id}/channels", 
            headers=headers
        )
        
        if channels_response.status_code == 200:
            channels = channels_response.json()
            
            # Organize channels by category
            categories = {}
            text_channels = []
            
            # First, identify all categories
            for channel in channels:
                if channel["type"] == 4:  # Category type
                    categories[channel["id"]] = {
                        "name": channel["name"],
                        "position": channel["position"],
                        "channels": []
                    }
            
            # Then assign channels to categories
            for channel in channels:
                if channel["type"] == 0:  # Text channel
                    channel_data = {
                        "id": channel["id"],
                        "name": channel["name"],
                        "position": channel["position"],
                        "permissions": {
                            "write": True  # Default permission - can reply in channel
                        }
                    }
                    
                    # Check if channel belongs to a category
                    parent_id = channel.get("parent_id")
                    if parent_id and parent_id in categories:
                        categories[parent_id]["channels"].append(channel_data)
                    else:
                        text_channels.append(channel_data)
            
            # Store in servers_data
            servers_data[guild_id] = {
                "name": guild_name,
                "categories": categories,
                "channels": text_channels  # Channels not in any category
            }
    
    return servers_data

# Function to load saved permissions
def load_permissions():
    try:
        if os.path.exists("discord_permissions.json"):
            with open("discord_permissions.json", "r") as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Error loading permissions: {str(e)}")
        return {}

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
discord_token = os.getenv('DISCORD_TOKEN_2')

if not discord_token:
    st.error("Discord token not found. Please set the DISCORD_TOKEN_2 environment variable.")
    
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
            # Use the token update function from simple_app for consistency
            import sys
            sys.path.append(".")
            from simple_app import update_discord_token
            
            # Update the token
            if update_discord_token(token_input):
                # Update the in-memory token
                os.environ["DISCORD_TOKEN_2"] = token_input
                # Update the local variable 
                discord_token = token_input
                
                st.success("Token saved successfully!")
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
                bot_avatar = data.get("avatar", "")
                
                # Show bot info in a Discord-like container
                status_indicator.success("Connected")
                st.markdown(f"""
                <div style='background-color: #36393f; padding: 10px; border-radius: 5px;'>
                    <div style='display: flex; align-items: center;'>
                        <div style='background-color: #5865F2; width: 40px; height: 40px; border-radius: 50%; 
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
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Refresh Discord Data", help="Fetch the latest servers and channels from Discord"):
                # Fetch servers and channels
                st.session_state.servers = fetch_discord_servers(discord_token)
                st.rerun()
        
        with col2:
            if st.button("Reset Bot Token", help="Clear the saved Discord token"):
                # Use environment approach to clear token
                os.environ["DISCORD_TOKEN_2"] = ""
                
                # Update .env file
                env_file = ".env"
                if os.path.exists(env_file):
                    with open(env_file, "r") as f:
                        lines = f.readlines()
                    
                    with open(env_file, "w") as f:
                        for line in lines:
                            if not line.startswith("DISCORD_TOKEN_2="):
                                f.write(line)
                
                st.warning("Token reset! Please enter a new token.")
                st.rerun()
        
        with col3:
            if st.button("Save All Settings", help="Save all channel permissions"):
                if save_permissions(st.session_state.permissions):
                    st.success("All settings saved successfully!")
    
    # Initialize servers if needed
    if "servers" not in st.session_state:
        with st.spinner("Fetching Discord servers and channels..."):
            st.session_state.servers = fetch_discord_servers(discord_token)
    
    # If we have servers, display them
    if st.session_state.servers:
        st.markdown('<div class="discord-header"><h3>Server Configuration</h3></div>', unsafe_allow_html=True)
        
        # Create tabs for each server
        server_ids = list(st.session_state.servers.keys())
        server_names = [st.session_state.servers[server_id]["name"] for server_id in server_ids]
        
        if server_ids:
            tabs = st.tabs(server_names)
            
            for i, (server_id, tab) in enumerate(zip(server_ids, tabs)):
                server_data = st.session_state.servers[server_id]
                
                with tab:
                    # Server header
                    st.markdown(f"""
                    <div class="server-header">
                        <span style="font-weight: bold;">{server_data["name"]}</span>
                        <span style="color: #dcddde; font-size: 0.8em; margin-left: 10px;">ID: {server_id}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Initialize permissions for this server if not already
                    if server_id not in st.session_state.permissions:
                        st.session_state.permissions[server_id] = {}
                    
                    # Default permissions for new channels
                    with st.expander("Default for new Channels", expanded=True):
                        # Store the default setting in the permissions file
                        if "default_settings" not in st.session_state.permissions[server_id]:
                            st.session_state.permissions[server_id]["default_settings"] = {
                                "new_channels_active": False  # Default to inactive in new channels
                            }
                        
                        default_active = st.checkbox("Bot Active in Channel by Default", 
                                                    key=f"default_active_{server_id}", 
                                                    value=st.session_state.permissions[server_id]["default_settings"].get("new_channels_active", False),
                                                    help="When enabled, the bot will be active in new channels by default")
                        
                        # Update the default setting when changed
                        if "default_active" not in st.session_state or st.session_state.get(f"default_active_{server_id}") != default_active:
                            st.session_state.permissions[server_id]["default_settings"]["new_channels_active"] = default_active
                            # Save the settings
                            save_permissions(st.session_state.permissions)
                    
                    # Toggle all buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('<div class="toggle-container">', unsafe_allow_html=True)
                        if st.button("Enable in All Channels", key=f"enable_all_{server_id}"):
                            # Enable in all channels
                            for channel_type in ["channels", "categories"]:
                                if channel_type == "channels":
                                    for channel in server_data["channels"]:
                                        channel_id = channel["id"]
                                        st.session_state[f"active_{server_id}_{channel_id}"] = True
                                elif channel_type == "categories":
                                    for category_id, category in server_data["categories"].items():
                                        for channel in category["channels"]:
                                            channel_id = channel["id"]
                                            st.session_state[f"active_{server_id}_{channel_id}"] = True
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    with col2:
                        st.markdown('<div class="toggle-container">', unsafe_allow_html=True)
                        if st.button("Disable in All Channels", key=f"disable_all_{server_id}"):
                            # Disable in all channels
                            for channel_type in ["channels", "categories"]:
                                if channel_type == "channels":
                                    for channel in server_data["channels"]:
                                        channel_id = channel["id"]
                                        st.session_state[f"active_{server_id}_{channel_id}"] = False
                                elif channel_type == "categories":
                                    for category_id, category in server_data["categories"].items():
                                        for channel in category["channels"]:
                                            channel_id = channel["id"]
                                            st.session_state[f"active_{server_id}_{channel_id}"] = False
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display channels that aren't in a category first
                    if server_data["channels"]:
                        st.markdown('<div class="discord-header" style="background-color: #2f3136;"><h4>General Channels</h4></div>', unsafe_allow_html=True)
                        
                        for channel in sorted(server_data["channels"], key=lambda x: x["position"]):
                            channel_id = channel["id"]
                            channel_name = channel["name"]
                            
                            # Get saved permissions or use defaults
                            if channel_id not in st.session_state.permissions[server_id]:
                                # Get default setting for new channels
                                default_active = st.session_state.permissions[server_id].get("default_settings", {}).get("new_channels_active", False)
                                
                                st.session_state.permissions[server_id][channel_id] = {
                                    "write": default_active  # Use the default setting for new channels
                                }
                            
                            permissions = st.session_state.permissions[server_id][channel_id]
                            
                            # Display channel with checkboxes in Discord-like style
                            st.markdown(f"""
                            <div class="discord-channel">
                                <span class="channel-icon">#</span>
                                <span>{channel_name}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Channel permission toggle - simplified to just "Active" (can reply in the channel)
                            cols = st.columns([3, 1])
                            with cols[0]:
                                active = st.checkbox("Bot Active in Channel", key=f"active_{server_id}_{channel_id}", 
                                                value=permissions.get("write", True),
                                                help="When enabled, the bot will respond to messages in this channel")
                            with cols[1]:
                                if st.button("Save", key=f"save_{server_id}_{channel_id}"):
                                    # Update permissions - only track if the bot can reply
                                    st.session_state.permissions[server_id][channel_id] = {
                                        "write": st.session_state[f"active_{server_id}_{channel_id}"]
                                    }
                                    # Save to disk
                                    save_permissions(st.session_state.permissions)
                                    st.success(f"Permissions updated for #{channel_name}")
                    
                    # Display categories and their channels
                    if server_data["categories"]:
                        for category_id, category in sorted(server_data["categories"].items(), 
                                                          key=lambda x: x[1]["position"]):
                            # Category header
                            st.markdown(f"""
                            <div class="discord-category">
                                {category["name"].upper()}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Channels in this category
                            for channel in sorted(category["channels"], key=lambda x: x["position"]):
                                channel_id = channel["id"]
                                channel_name = channel["name"]
                                
                                # Get saved permissions or use defaults
                                if channel_id not in st.session_state.permissions[server_id]:
                                    # Get default setting for new channels
                                    default_active = st.session_state.permissions[server_id].get("default_settings", {}).get("new_channels_active", False)
                                    
                                    st.session_state.permissions[server_id][channel_id] = {
                                        "write": default_active  # Use the default setting for new channels
                                    }
                                
                                permissions = st.session_state.permissions[server_id][channel_id]
                                
                                # Display channel with checkboxes
                                st.markdown(f"""
                                <div class="discord-channel">
                                    <span class="channel-icon">#</span>
                                    <span>{channel_name}</span>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Channel permission toggle - simplified to just "Active" (can reply in the channel)
                                cols = st.columns([3, 1])
                                with cols[0]:
                                    active = st.checkbox("Bot Active in Channel", key=f"active_{server_id}_{channel_id}", 
                                                    value=permissions.get("write", True),
                                                    help="When enabled, the bot will respond to messages in this channel")
                                with cols[1]:
                                    if st.button("Save", key=f"save_{server_id}_{channel_id}"):
                                        # Update permissions - only track if the bot can reply
                                        st.session_state.permissions[server_id][channel_id] = {
                                            "write": st.session_state[f"active_{server_id}_{channel_id}"]
                                        }
                                        # Save to disk
                                        save_permissions(st.session_state.permissions)
                                        st.success(f"Permissions updated for #{channel_name}")
                    
                    # Button to save all changes for this server
                    if st.button("Save All Changes for This Server", key=f"save_all_{server_id}"):
                        # Update all permissions from session state
                        for channel_type in ["channels", "categories"]:
                            if channel_type == "channels":
                                for channel in server_data["channels"]:
                                    channel_id = channel["id"]
                                    st.session_state.permissions[server_id][channel_id] = {
                                        "write": st.session_state.get(f"active_{server_id}_{channel_id}", True)
                                    }
                            elif channel_type == "categories":
                                for category_id, category in server_data["categories"].items():
                                    for channel in category["channels"]:
                                        channel_id = channel["id"]
                                        st.session_state.permissions[server_id][channel_id] = {
                                            "write": st.session_state.get(f"active_{server_id}_{channel_id}", True)
                                        }
                        
                        # Save to disk
                        if save_permissions(st.session_state.permissions):
                            st.success(f"All permissions saved for {server_data['name']}!")
        else:
            st.warning("No servers found. Make sure your bot has been added to at least one server.")
            st.markdown("""
            To add your bot to a server:
            1. Make sure you have the correct permissions on the server
            2. Use the Bot Invitation URL from the Bot Status section
            3. Select the server you want to add the bot to
            4. Grant the requested permissions
            5. Return to this page and click 'Refresh Discord Data'
            """)
    else:
        st.error("Failed to fetch Discord servers. Please check your token and try again.")
        if st.button("Try Again"):
            st.rerun()
        
# Add a footer with disclaimer
st.markdown("---")
st.markdown("""
**Note:** This configuration tool connects directly to the Discord API. Changes made here will be applied to your bot's permissions system and affect how it interacts with your Discord server in real-time.

The simplified permission model allows you to:
1. Enable the bot in channels where you want it to respond to users
2. Disable the bot in channels where you don't want it to respond
3. Apply changes server-wide with a single click

For best results, make sure your bot has the necessary permissions on Discord, including:
- Read Messages
- Send Messages
- Read Message History
- Embed Links
""")