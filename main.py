import os
import subprocess
import streamlit as st
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_discord_bot():
    """Run the Discord bot in a separate process"""
    subprocess.Popen(["python", "discord_bot.py"])

def run_streamlit_admin():
    """Run the Streamlit admin interface"""
    os.system("streamlit run simple_app.py --server.port 5000")

if __name__ == "__main__":
    # Check if Discord token is set
    if not (os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_TOKEN_2")):
        print("Error: Neither DISCORD_TOKEN nor DISCORD_TOKEN_2 environment variable is set.")
        print("Please set it in the .env file or in the Replit Secrets tab.")
        exit(1)
    
    # Start the Discord bot in a separate thread
    bot_thread = threading.Thread(target=run_discord_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    print("Starting Discord bot...")
    time.sleep(2)  # Give the bot some time to initialize
    
    # Run the Streamlit admin interface in the main thread
    print("Starting Streamlit admin interface...")
    run_streamlit_admin()
