import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime


def data_cleaning_tab(RAW_DIR, CLEANED_DIR, RULES_DIR):
    """Unified Data Cleaning tab (combines Bronze + Silver functionality)."""
    st.header("🧼 Data Cleaning — Prepare and Refine Your Dataset")

    # ============================================================
    # STEP 1: Upload or Select Dataset
    # ============================================================
    st.subheader("📂 Step 1: Upload or Select Dataset")

    uploaded_file = st.file_uploader(
        "📤 Upload a CSV dataset for cleaning",
        type=["csv"],
        key="cleaning_upload"
    )

    if uploaded_file is not None:
        save_path = os.path.join(RAW_DIR, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ File `{uploaded_file.name}` uploaded successfully to `{RAW_DIR}`")
        st.session_state["selected_dataset"] = uploaded_file.name

    available_files = [f for f in os.listdir(RAW_DIR) if f.endswith(".csv")]
    if not available_files:
        st.info("📁 No datasets found. Please upload one above to start cleaning.")
        return

    default_file = (
        st.session_state.get("selected_dataset")
        if st.session_state.get("selected_dataset") in available_files
        else available_files[0]
    )

    selected_file = st.selectbox(
        "Select dataset to clean:",
        available_files,
        index=available_files.index(default_file)
    )

    df = pd.read_csv(os.path.join(RAW_DIR, selected_file), encoding="utf-8-sig", on_bad_lines="skip")
    st.write(f"### 📄 Preview: {selected_file}")
    st.dataframe(df.head(), use_container_width=True)

    # ============================================================
    # STEP 2: Select Columns to Keep
    # ============================================================
    st.markdown("---")
    st.subheader("✅ Step 2: Select Columns to Keep")

    selected_cols = st.multiselect(
        "Select columns to include in the cleaned dataset:",
        df.columns.tolist(),
        default=df.columns.tolist()
    )

    df = df[selected_cols]
    st.write("### 📊 Filtered Dataset Preview")
    st.dataframe(df.head(), use_container_width=True)

    # ============================================================
    # STEP 3: Handle Missing Values
    # ============================================================
    st.markdown("---")
    st.subheader("🔧 Step 3: Handle Missing Values")

    all_cols = df.columns.tolist()
    selected_col = st.selectbox("Select column to handle missing values:", all_cols)
    method = st.radio(
        "Select method:",
        ["Mean", "Median", "Zero", "Mode", "Custom Value", "Skip"],
        horizontal=True
    )

    custom_val = None
    if method == "Custom Value":
        custom_val = st.text_input("Enter custom fill value:")

    if st.button("Apply Missing Value Handling", key="apply_missing"):
        try:
            df.replace(["N/A", "n/a", "NA", "null", "--", "-", ""], pd.NA, inplace=True)
            if method == "Mean" and pd.api.types.is_numeric_dtype(df[selected_col]):
                df[selected_col].fillna(df[selected_col].mean(), inplace=True)
            elif method == "Median" and pd.api.types.is_numeric_dtype(df[selected_col]):
                df[selected_col].fillna(df[selected_col].median(), inplace=True)
            elif method == "Zero" and pd.api.types.is_numeric_dtype(df[selected_col]):
                df[selected_col].fillna(0, inplace=True)
            elif method == "Mode":
                df[selected_col].fillna(df[selected_col].mode()[0], inplace=True)
            elif method == "Custom Value":
                df[selected_col].fillna(custom_val, inplace=True)
            st.success(f"✅ Applied {method} fill to `{selected_col}`")
        except Exception as e:
            st.error(f"❌ Error applying missing value handling: {e}")

    # ============================================================
    # STEP 4: Conditional Filtering
    # ============================================================
    st.markdown("---")
    st.subheader("🎯 Step 4: Conditional Filtering")

    # Helper to safely convert numeric-like strings
    def clean_numeric(val):
        """Convert messy numeric strings like '$4,000.00%' to float safely."""
        if pd.isna(val):
            return None
        if isinstance(val, (int, float)):
            return val
        val = str(val).replace("$", "").replace(",", "").replace("₹", "").replace("%", "").strip()
        try:
            return float(val)
        except ValueError:
            return None

    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col1:
        filter_col = st.selectbox("Column:", df.columns)
    with col2:
        filter_op = st.selectbox("Condition:", ["<", ">", "<=", ">=", "==", "!="])
    with col3:
        filter_val = st.text_input("Compare Value:")

    if st.button("Apply Filter", key="apply_filter"):
        try:
            df_before = len(df)

            sample_values = df[filter_col].dropna().astype(str).head(20)
            numeric_like = all(any(ch.isdigit() for ch in s) for s in sample_values)

            if numeric_like:
                df[filter_col] = df[filter_col].apply(clean_numeric)
                try:
                    val = float(filter_val.replace("$", "").replace(",", "").replace("%", "").strip())
                except ValueError:
                    st.error("❌ Please enter a valid numeric value.")
                    return

                if filter_op == "==":
                    df = df[df[filter_col] == val]
                elif filter_op == "!=":
                    df = df[df[filter_col] != val]
                elif filter_op == ">":
                    df = df[df[filter_col] > val]
                elif filter_op == "<":
                    df = df[df[filter_col] < val]
                elif filter_op == ">=":
                    df = df[df[filter_col] >= val]
                elif filter_op == "<=":
                    df = df[df[filter_col] <= val]
            else:
                val = str(filter_val).strip()
                if filter_op == "==":
                    df = df[df[filter_col].astype(str).str.strip() == val]
                elif filter_op == "!=":
                    df = df[df[filter_col].astype(str).str.strip() != val]
                else:
                    st.warning("⚠️ String columns only support '==' and '!=' operators.")
                    return

            df_after = len(df)
            st.success(f"✅ Filter applied: {filter_col} {filter_op} {filter_val} | Rows removed: {df_before - df_after}")
        except Exception as e:
            st.error(f"❌ Filter failed: {e}")

    # ============================================================
    # STEP 5: Preview and Save
    # ============================================================
    st.markdown("---")
    st.subheader("📊 Step 5: Review & Save Cleaned Dataset")
    st.dataframe(df.head(), use_container_width=True)
    st.metric("Rows after cleaning", len(df))
    st.metric("Columns", len(df.columns))

    if st.button("💾 Save Cleaned Dataset", key="save_cleaned"):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        cleaned_dir = os.path.join(CLEANED_DIR, timestamp)
        os.makedirs(cleaned_dir, exist_ok=True)
        out_path = os.path.join(cleaned_dir, "cleaned_dataset.csv")
        df.to_csv(out_path, index=False)
        st.session_state["cleaned_path"] = out_path

        st.success(f"✅ Cleaned dataset saved at: `{out_path}`")

        st.download_button(
            "⬇️ Download Cleaned Dataset",
            df.to_csv(index=False).encode("utf-8"),
            file_name="cleaned_dataset.csv",
            mime="text/csv"
        )

