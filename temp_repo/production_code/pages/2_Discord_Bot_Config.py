import streamlit as st
import os
import json
from dotenv import load_dotenv
from theme_selector import display_theme_selector

# Load environment variables
load_dotenv()

# Display theme selector
display_theme_selector()

# Set page title
st.title("Discord Bot Configuration")

# Main content
st.markdown("""
## Discord Bot Settings

Configure your Discord bot settings and channel permissions here. 
The bot uses these settings to determine where it's allowed to respond.
""")

# Discord token configuration
st.header("Discord Token Configuration")

# Get current token if available
current_token = os.getenv('DISCORD_TOKEN')
token_status = "✅ Configured" if current_token else "❌ Not Configured"

st.markdown(f"**Discord Token Status**: {token_status}")

# Only show the actual form if not configured or if user wants to update
if not current_token or st.checkbox("Update Discord Token"):
    with st.form("discord_token_form"):
        new_token = st.text_input("Discord Bot Token", 
                                value=current_token if current_token else "",
                                type="password",
                                help="Get this from the Discord Developer Portal")
        
        submit_button = st.form_submit_button("Save Token")
        
        if submit_button and new_token:
            try:
                # Read existing .env file
                env_vars = {}
                if os.path.exists(".env"):
                    with open(".env", "r") as f:
                        for line in f:
                            if line.strip() and not line.startswith('#'):
                                key, value = line.strip().split('=', 1)
                                env_vars[key] = value
                
                # Update the Discord token
                env_vars['DISCORD_TOKEN'] = new_token
                
                # Write back to .env file
                with open(".env", "w") as f:
                    for key, value in env_vars.items():
                        f.write(f"{key}={value}\n")
                
                st.success("Discord token updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating token: {str(e)}")

# Channel permissions manager
st.header("Channel Permissions")

st.markdown("""
Configure which Discord channels the bot is allowed to respond in.
By default, the bot will respond in all channels unless configured otherwise.
""")

# Load existing permissions
permissions = {}
if os.path.exists("discord_permissions.json"):
    try:
        with open("discord_permissions.json", "r") as f:
            permissions = json.load(f)
    except Exception as e:
        st.error(f"Error loading permissions: {str(e)}")

# Server selector
st.subheader("Server Configuration")

# Add a new server ID
with st.expander("Add a New Server"):
    with st.form("add_server_form"):
        new_server_id = st.text_input("Server ID", 
                                    help="Right-click on the server and select 'Copy ID'")
        new_server_name = st.text_input("Server Name (for reference only)",
                                      help="Enter a name to help you identify this server")
        
        new_server_defaults = st.checkbox("Allow bot to respond in new channels by default", value=False)
        
        add_server_button = st.form_submit_button("Add Server")
        
        if add_server_button and new_server_id:
            if new_server_id in permissions:
                st.warning(f"Server ID {new_server_id} already exists.")
            else:
                permissions[new_server_id] = {
                    "name": new_server_name,
                    "default_settings": {
                        "new_channels_active": new_server_defaults
                    }
                }
                
                # Save updated permissions
                with open("discord_permissions.json", "w") as f:
                    json.dump(permissions, f, indent=4)
                
                st.success(f"Added server {new_server_name} ({new_server_id})")
                st.rerun()

# Server editor
if permissions:
    servers = list(permissions.keys())
    
    selected_server = st.selectbox(
        "Select Server to Configure",
        servers,
        format_func=lambda x: f"{permissions[x].get('name', 'Unnamed Server')} ({x})"
    )
    
    if selected_server:
        st.subheader(f"Configuring: {permissions[selected_server].get('name', 'Unnamed Server')}")
        
        # Server default settings
        default_active = permissions[selected_server].get("default_settings", {}).get("new_channels_active", False)
        new_default = st.checkbox("Allow bot to respond in new channels by default", value=default_active)
        
        if new_default != default_active:
            if "default_settings" not in permissions[selected_server]:
                permissions[selected_server]["default_settings"] = {}
            
            permissions[selected_server]["default_settings"]["new_channels_active"] = new_default
            
            # Save updated permissions
            with open("discord_permissions.json", "w") as f:
                json.dump(permissions, f, indent=4)
            
            st.success("Default settings updated")
        
        # Channel configuration
        st.subheader("Channel Configuration")
        
        # Add a new channel
        with st.expander("Add a New Channel"):
            with st.form("add_channel_form"):
                new_channel_id = st.text_input("Channel ID", 
                                             help="Right-click on the channel and select 'Copy ID'")
                new_channel_name = st.text_input("Channel Name (for reference only)")
                
                can_write = st.checkbox("Allow bot to respond in this channel", value=True)
                
                add_channel_button = st.form_submit_button("Add Channel")
                
                if add_channel_button and new_channel_id:
                    if new_channel_id in permissions[selected_server]:
                        st.warning(f"Channel ID {new_channel_id} already exists for this server.")
                    else:
                        permissions[selected_server][new_channel_id] = {
                            "name": new_channel_name,
                            "write": can_write
                        }
                        
                        # Save updated permissions
                        with open("discord_permissions.json", "w") as f:
                            json.dump(permissions, f, indent=4)
                        
                        st.success(f"Added channel {new_channel_name} ({new_channel_id})")
                        st.rerun()
        
        # List and edit existing channels
        channels = {}
        for key, value in permissions[selected_server].items():
            if key != "name" and key != "default_settings":
                channels[key] = value
        
        if channels:
            st.subheader("Existing Channels")
            
            # Create a table-like display of channels with toggles
            for channel_id, channel_info in channels.items():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.text(channel_info.get("name", "Unnamed Channel"))
                
                with col2:
                    st.text(f"ID: {channel_id}")
                
                with col3:
                    channel_active = channel_info.get("write", True)
                    new_status = st.checkbox("Active", value=channel_active, key=f"channel_{channel_id}")
                    
                    if new_status != channel_active:
                        permissions[selected_server][channel_id]["write"] = new_status
                        
                        # Save updated permissions
                        with open("discord_permissions.json", "w") as f:
                            json.dump(permissions, f, indent=4)
                        
                        st.success(f"Updated channel {channel_info.get('name', 'Unnamed Channel')}")
                        st.rerun()
            
            # Delete channel button
            st.subheader("Remove Channel")
            channel_to_delete = st.selectbox(
                "Select Channel to Remove",
                list(channels.keys()),
                format_func=lambda x: f"{channels[x].get('name', 'Unnamed Channel')} ({x})"
            )
            
            if st.button("Remove Selected Channel"):
                if channel_to_delete in permissions[selected_server]:
                    del permissions[selected_server][channel_to_delete]
                    
                    # Save updated permissions
                    with open("discord_permissions.json", "w") as f:
                        json.dump(permissions, f, indent=4)
                    
                    st.success(f"Removed channel {channel_to_delete}")
                    st.rerun()
        else:
            st.info("No channels configured for this server yet. Add a channel above.")
    
    # Delete server button
    st.subheader("Remove Server")
    server_to_delete = st.selectbox(
        "Select Server to Remove",
        servers,
        format_func=lambda x: f"{permissions[x].get('name', 'Unnamed Server')} ({x})",
        key="server_delete"
    )
    
    if st.button("Remove Selected Server"):
        if server_to_delete in permissions:
            del permissions[server_to_delete]
            
            # Save updated permissions
            with open("discord_permissions.json", "w") as f:
                json.dump(permissions, f, indent=4)
            
            st.success(f"Removed server {server_to_delete}")
            st.rerun()
else:
    st.info("No servers configured yet. Add a server above to begin.")

st.markdown("---")

# Restart instructions
st.header("Bot Restart Instructions")

st.markdown("""
After making changes to the bot configuration, you may need to restart the bot for changes to take effect.

To restart the bot:
1. Stop the current bot process
2. Run `python run_bot.py` to start the bot with the new configuration

If you've updated the Discord token, you must restart the bot for the changes to take effect.
""")

# Help section
with st.expander("How to get Discord IDs"):
    st.markdown("""
    ### How to Get Discord IDs

    1. **Enable Developer Mode in Discord**:
       - Open Discord settings
       - Go to "App Settings" > "Advanced"
       - Turn on "Developer Mode"

    2. **Get Server ID**:
       - Right-click on the server icon
       - Select "Copy ID"

    3. **Get Channel ID**:
       - Right-click on the channel
       - Select "Copy ID"

    These IDs are used to configure which channels the bot is allowed to respond in.
    """)