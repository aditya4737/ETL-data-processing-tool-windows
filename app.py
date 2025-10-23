import streamlit as st
import os
from modules.styling import apply_dark_theme
from modules.composer import dataset_composer_tab
from modules.cleaning import data_cleaning_tab
from modules.dashboard import visual_dashboard_tab

# ============================================================
# PATH SETUP — Standardized Folder Structure
# ============================================================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
CLEANED_DIR = os.path.join(DATA_DIR, "cleaned")
COMPOSED_DIR = os.path.join(DATA_DIR, "composed_data")
RULES_DIR = os.path.join(ROOT_DIR, "rules")

# Ensure folders exist
for d in [DATA_DIR, RAW_DIR, CLEANED_DIR, COMPOSED_DIR, RULES_DIR]:
    os.makedirs(d, exist_ok=True)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="Data Transformation Pipeline", layout="wide")
st.title("📊 Data Transformation Pipeline Dashboard")
st.caption("Interactively Compose, Clean, and Visualize Your Datasets")

# Apply global styling
apply_dark_theme()

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3 = st.tabs([
    "🧱 Dataset Composer",
    "🧼 Data Cleaning",
    "📈 Visual Dashboard"
])

# ============================================================
# TAB LOGIC
# ============================================================
with tab1:
    dataset_composer_tab(COMPOSED_DIR)

with tab2:
    data_cleaning_tab(RAW_DIR, CLEANED_DIR, RULES_DIR)

with tab3:
    visual_dashboard_tab(CLEANED_DIR)
