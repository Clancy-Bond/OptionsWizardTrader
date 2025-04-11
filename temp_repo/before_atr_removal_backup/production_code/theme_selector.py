"""
Theme selector module for Streamlit applications
"""
import streamlit as st
from utils.theme_helper import apply_discord_style, apply_dark_finance_style

def display_theme_selector():
    """
    Display theme selector in sidebar
    """
    st.sidebar.title("Theme Settings")
    
    # Initialize theme in session state if not already set
    if 'theme' not in st.session_state:
        st.session_state.theme = "dark_finance"
    
    # Theme selector
    selected_theme = st.sidebar.radio(
        "Select Theme:",
        options=["Dark Finance", "Discord Style", "Default Streamlit"],
        index=0 if st.session_state.theme == "dark_finance" else 
              1 if st.session_state.theme == "discord" else 2,
        key="theme_selector"
    )
    
    # Update theme in session state
    if selected_theme == "Dark Finance" and st.session_state.theme != "dark_finance":
        st.session_state.theme = "dark_finance"
        st.rerun()
    elif selected_theme == "Discord Style" and st.session_state.theme != "discord":
        st.session_state.theme = "discord"
        st.rerun()
    elif selected_theme == "Default Streamlit" and st.session_state.theme != "default":
        st.session_state.theme = "default"
        st.rerun()
    
    # Apply selected theme
    if st.session_state.theme == "dark_finance":
        apply_dark_finance_style()
    elif st.session_state.theme == "discord":
        apply_discord_style()
    
    # Add a divider
    st.sidebar.markdown("---")