import streamlit as st

def apply_dark_theme():
    """Apply global dark theme styling for all Streamlit tabs."""
    st.markdown("""
    <style>
    /* Global background and text */
    [data-testid="stAppViewContainer"] {
        background-color: #0f172a !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stHeader"] {
        background: #0f172a !important;
        color: #f8fafc !important;
    }
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        color: #f8fafc !important;
    }
    [data-testid="stMarkdownContainer"] h1, h2, h3, h4, h5, h6, p, label {
        color: #e2e8f0 !important;
    }

    /* Tabs */
    div[data-baseweb="tab-list"] {
        border-bottom: 1px solid #1e293b !important;
    }
    button[data-baseweb="tab"] {
        background: transparent !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 8px 20px !important;
        transition: color 0.2s ease-in-out, border-bottom 0.3s;
    }
    button[data-baseweb="tab"]:hover {
        color: #f8fafc !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #facc15 !important;
        border-bottom: 2px solid #facc15 !important;
    }

    /* Inputs, multiselects, text areas */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #e2e8f0 !important;
    }
    input, textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
    }

    /* File uploader */
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #1e293b !important;
        border: 1px dashed #475569 !important;
        border-radius: 10px !important;
    }

    /* DataFrames */
    div[data-testid="stDataFrame"] {
        border-radius: 10px !important;
        background-color: #1e293b !important;
    }

    /* Alerts */
    div[data-testid="stAlert"] {
        border-radius: 10px !important;
        font-weight: 500 !important;
    }

    /* Buttons */
    button[kind="primary"] {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
    }
    button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
    }
    </style>
    """, unsafe_allow_html=True)

