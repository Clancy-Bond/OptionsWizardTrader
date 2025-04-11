"""
Theme helper module for Streamlit applications
"""
import streamlit as st

def setup_page(title="Options AI Assistant", icon="📊", layout="wide"):
    """
    Set up the Streamlit page with consistent configuration
    
    Args:
        title: Page title
        icon: Page icon
        layout: Page layout ('wide' or 'centered')
    """
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout=layout
    )
    
    # Apply custom CSS for better UI
    st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 4rem;
        }
        h1, h2, h3 {
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
        }
        .stTextInput > div > div > input {
            border-radius: 5px;
        }
        .stButton > button {
            border-radius: 5px;
        }
        .stSelectbox > div > div > div > div {
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)
    
def apply_discord_style():
    """
    Apply Discord-inspired styling to the Streamlit app
    """
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
    
def apply_dark_finance_style():
    """
    Apply dark finance-themed styling to the Streamlit app
    """
    st.markdown("""
    <style>
        .finance-card {
            background-color: #1e222d;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .finance-header {
            color: #e0e0e0;
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 10px;
            border-bottom: 1px solid #2c313c;
            padding-bottom: 8px;
        }
        .profit {
            color: #4caf50;
            font-weight: bold;
        }
        .loss {
            color: #f44336;
            font-weight: bold;
        }
        .neutral {
            color: #888888;
        }
        .data-label {
            color: #888888;
            font-size: 12px;
        }
        .data-value {
            color: white;
            font-size: 16px;
            font-weight: bold;
        }
        .ticker {
            background-color: #2c313c;
            padding: 4px 8px;
            border-radius: 4px;
            margin-right: 5px;
            font-weight: bold;
        }
        .chart-container {
            background-color: #1e222d;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
        }
    </style>
    """, unsafe_allow_html=True)