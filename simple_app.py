import streamlit as st
import os
import json
from discord_bot_config import BotConfig

# Initialize configuration
bot_config = BotConfig()

def check_discord_token():
    """Check if Discord token is set in environment variables"""
    token = os.getenv("DISCORD_TOKEN")
    return token is not None and token != ""

def update_discord_token(token):
    """Update Discord token in environment variable and .env file"""
    # Update in-memory environment variable
    os.environ["DISCORD_TOKEN"] = token
    
    # Update .env file
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            lines = f.readlines()
        
        token_set = False
        for i, line in enumerate(lines):
            if line.startswith("DISCORD_TOKEN="):
                lines[i] = f"DISCORD_TOKEN={token}\n"
                token_set = True
                break
        
        if not token_set:
            lines.append(f"DISCORD_TOKEN={token}\n")
        
        with open(env_file, "w") as f:
            f.writelines(lines)
    else:
        with open(env_file, "w") as f:
            f.write(f"DISCORD_TOKEN={token}\n")
    
    return True

# Set up the Streamlit app
st.set_page_config(page_title="OptionsWizard Admin", page_icon="🧙", layout="wide")

st.title("🧙 OptionsWizard Admin Interface")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Status", "Channel Configuration", "Admin Users"])

# Status page
if page == "Status":
    st.header("System Status")
    
    # Check Discord token
    token_status = check_discord_token()
    token_status_text = "✅ Set" if token_status else "❌ Not Set"
    token_status_color = "green" if token_status else "red"
    
    st.markdown(f"**Discord Token:** <span style='color:{token_status_color}'>{token_status_text}</span>", unsafe_allow_html=True)
    
    if not token_status:
        with st.form("token_form"):
            new_token = st.text_input("Enter Discord Bot Token", type="password")
            submit_button = st.form_submit_button("Save Token")
            
            if submit_button and new_token:
                if update_discord_token(new_token):
                    st.success("Token updated successfully. Please restart the application for changes to take effect.")
                    st.experimental_rerun()
                else:
                    st.error("Failed to update token.")
    
    # Channel whitelist status
    channels = bot_config.get_channel_whitelist()
    if channels:
        st.markdown(f"**Whitelisted Channels:** {len(channels)}")
        for channel in channels:
            st.markdown(f"- {channel}")
    else:
        st.markdown("**Whitelisted Channels:** None (all channels allowed)")
    
    # Admin users status
    admins = bot_config.get_admin_users()
    if admins:
        st.markdown(f"**Admin Users:** {len(admins)}")
        for admin in admins:
            st.markdown(f"- {admin}")
    else:
        st.markdown("**Admin Users:** None")

# Channel Configuration page
elif page == "Channel Configuration":
    st.header("Channel Whitelist Configuration")
    st.info("Adding channels to the whitelist restricts the bot to only respond in those channels. If the whitelist is empty, the bot will respond in all channels.")
    
    # Show current whitelisted channels
    channels = bot_config.get_channel_whitelist()
    if channels:
        st.subheader("Current Whitelisted Channels")
        for i, channel_id in enumerate(channels):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"Channel ID: {channel_id}")
            with col2:
                if st.button("Remove", key=f"remove_channel_{i}"):
                    if bot_config.remove_channel(channel_id):
                        st.success(f"Removed channel {channel_id} from whitelist")
                        st.rerun()
                    else:
                        st.error("Failed to remove channel")
    else:
        st.warning("No channels in whitelist. Bot will respond in all channels.")
    
    # Add new channel
    st.subheader("Add Channel to Whitelist")
    with st.form("add_channel_form"):
        new_channel = st.text_input("Enter Channel ID")
        submit_button = st.form_submit_button("Add Channel")
        
        if submit_button and new_channel:
            try:
                # Clean input and convert to integer to validate
                new_channel = new_channel.strip()
                int(new_channel)  # Validate that it's a number
                
                if bot_config.add_channel(new_channel):
                    st.success(f"Added channel {new_channel} to whitelist")
                    st.rerun()
                else:
                    st.error("Channel already in whitelist")
            except ValueError:
                st.error("Invalid channel ID. Must be a number.")

# Admin Users page
elif page == "Admin Users":
    st.header("Admin Users Configuration")
    st.info("Admin users have access to this configuration interface and can manage the bot settings.")
    
    # Show current admin users
    admins = bot_config.get_admin_users()
    if admins:
        st.subheader("Current Admin Users")
        for i, admin_id in enumerate(admins):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"User ID: {admin_id}")
            with col2:
                if st.button("Remove", key=f"remove_admin_{i}"):
                    if bot_config.remove_admin(admin_id):
                        st.success(f"Removed user {admin_id} from admins")
                        st.rerun()
                    else:
                        st.error("Failed to remove admin")
    else:
        st.warning("No admin users configured.")
    
    # Add new admin
    st.subheader("Add Admin User")
    with st.form("add_admin_form"):
        new_admin = st.text_input("Enter User ID")
        submit_button = st.form_submit_button("Add Admin")
        
        if submit_button and new_admin:
            try:
                # Clean input and convert to integer to validate
                new_admin = new_admin.strip()
                int(new_admin)  # Validate that it's a number
                
                if bot_config.add_admin(new_admin):
                    st.success(f"Added user {new_admin} as admin")
                    st.rerun()
                else:
                    st.error("User already an admin")
            except ValueError:
                st.error("Invalid user ID. Must be a number.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("© 2023 OptionsWizard")
