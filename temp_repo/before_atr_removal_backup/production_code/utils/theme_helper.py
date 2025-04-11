"""
Theme helper for Streamlit applications.
Provides functions to apply custom CSS styles for different themes.
"""
import streamlit as st

def apply_discord_style():
    """
    Apply Discord-inspired styling to the Streamlit app
    """
    st.markdown("""
    <style>
    /* Discord-inspired Theme */
    
    /* Base colors */
    :root {
        --discord-bg: #36393f;
        --discord-light-bg: #2f3136;
        --discord-darker-bg: #202225;
        --discord-text: #dcddde;
        --discord-link: #00b0f4;
        --discord-accent: #7289da;
        --discord-green: #43b581;
        --discord-red: #f04747;
        --discord-yellow: #faa61a;
    }
    
    /* Main container */
    .main .block-container {
        background-color: var(--discord-bg);
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: var(--discord-darker-bg);
    }
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6, label, .stTextInput label {
        color: #ffffff !important;
    }
    
    p, .stText, div {
        color: var(--discord-text) !important;
    }
    
    /* Links */
    a {
        color: var(--discord-link) !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: var(--discord-accent) !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
    }
    
    .stButton button:hover {
        background-color: #5b6eae !important;
    }
    
    /* Success/Error colors */
    .success {
        background-color: var(--discord-green) !important;
    }
    
    .error {
        background-color: var(--discord-red) !important;
    }
    
    /* Inputs */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: var(--discord-light-bg) !important;
        color: var(--discord-text) !important;
        border: 1px solid #1a1b1e !important;
        border-radius: 4px !important;
    }
    
    /* Dropdowns/Selects */
    .stSelectbox, .stMultiselect {
        background-color: var(--discord-light-bg) !important;
    }
    
    /* Metrics */
    .stMetric {
        background-color: var(--discord-light-bg) !important;
        padding: 10px !important;
        border-radius: 8px !important;
    }
    
    /* Divider */
    hr {
        border-color: #40444b !important;
    }
    
    /* Card-like elements */
    .element-container {
        background-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

def apply_dark_finance_style():
    """
    Apply dark finance theme styling to the Streamlit app
    """
    st.markdown("""
    <style>
    /* Dark Finance Theme */
    
    /* Base colors */
    :root {
        --finance-bg: #0f1216;
        --finance-card-bg: #171c23;
        --finance-accent: #4e89e8;
        --finance-text: #e0e0e0;
        --finance-green: #00c853;
        --finance-red: #ff5252;
        --finance-yellow: #ffc107;
        --finance-border: #2d3748;
    }
    
    /* Main container */
    .main .block-container {
        background-color: var(--finance-bg);
        padding: 2rem;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #101418;
    }
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    h1 {
        border-bottom: 1px solid var(--finance-border);
        padding-bottom: 0.5rem;
    }
    
    p, .stText, div, span {
        color: var(--finance-text) !important;
    }
    
    /* Links */
    a {
        color: var(--finance-accent) !important;
        text-decoration: none !important;
    }
    
    a:hover {
        text-decoration: underline !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: var(--finance-card-bg) !important;
        color: white !important;
        border: 1px solid var(--finance-border) !important;
        border-radius: 4px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
    }
    
    .stButton button:hover {
        background-color: var(--finance-accent) !important;
        border-color: var(--finance-accent) !important;
    }
    
    /* Success/Error colors */
    .success {
        background-color: var(--finance-green) !important;
        border: none !important;
        border-radius: 4px !important;
    }
    
    .error {
        background-color: var(--finance-red) !important;
        border: none !important;
        border-radius: 4px !important;
    }
    
    /* Inputs */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: var(--finance-card-bg) !important;
        color: var(--finance-text) !important;
        border: 1px solid var(--finance-border) !important;
        border-radius: 4px !important;
    }
    
    /* Dropdowns/Selects */
    .stSelectbox, .stMultiselect {
        background-color: var(--finance-card-bg) !important;
    }
    
    /* Metrics */
    .stMetric {
        background-color: var(--finance-card-bg) !important;
        padding: 20px !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        border: 1px solid var(--finance-border) !important;
    }
    
    /* For positive/negative values in metrics */
    .stMetric [data-testid="stMetricDelta"] svg [fill="#4da863"] {
        fill: var(--finance-green) !important;
    }
    
    .stMetric [data-testid="stMetricDelta"] svg [fill="#f44336"] {
        fill: var(--finance-red) !important;
    }
    
    /* Divider */
    hr {
        border-color: var(--finance-border) !important;
        margin: 2rem 0 !important;
    }
    
    /* Tables */
    .stTable table {
        background-color: var(--finance-card-bg) !important;
        border: 1px solid var(--finance-border) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    
    .stTable thead tr {
        background-color: #1e242c !important;
    }
    
    .stTable thead th {
        color: white !important;
        border-bottom: 1px solid var(--finance-border) !important;
    }
    
    .stTable tbody td {
        border-bottom: 1px solid var(--finance-border) !important;
    }
    
    /* Charts */
    .stPlot {
        background-color: var(--finance-card-bg) !important;
        border-radius: 8px !important;
        padding: 10px !important;
        border: 1px solid var(--finance-border) !important;
    }
    </style>
    """, unsafe_allow_html=True)