import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ============================================================
# Helper — convert columns safely to numeric if possible
# ============================================================
def clean_and_convert_column(df, col):
    """Convert messy numeric-like columns to numeric safely."""
    if col not in df.columns:
        return df
    df[col] = (
        df[col]
        .astype(str)
        .replace(["N/A", "n/a", "NA", "null", "--", "-", ""], pd.NA)
        .str.replace(r"[₹$,%,]", "", regex=True)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    try:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    except Exception:
        pass
    return df


# ============================================================
# Data Cleaning Tab — Final Version (aligned layout)
# ============================================================
def data_cleaning_tab(RAW_DIR, CLEANED_DIR, RULES_DIR):
    """ETL-style Data Cleaning tab with aligned top layout and compact spacing."""

    # ---------- Inject CSS for alignment ----------
    st.markdown("""
    <style>
    /* Align right column with Step 1 top */
    [data-testid="stHorizontalBlock"] > div:nth-child(2) {
        align-self: flex-start !important;
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    /* Reduce general vertical padding */
    section.main > div { padding-top: 0.5rem !important; }
    div[data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
    }
    h2, h3, h4 { font-size: 1.5rem !important; margin-bottom: 0.25rem !important; }
    div[data-testid="stDataFrame"] { margin-top: 0.3rem !important; }
    </style>
    """, unsafe_allow_html=True)

    # ---------- Header ----------
    st.markdown(
        "<h2>🧼 Data Cleaning — Intelligent Data Preparation</h2>"
        "<p style='font-size:0.9rem;color:#cbd5e1;'>Load, clean, and prepare datasets interactively with live preview.</p>",
        unsafe_allow_html=True,
    )

    # ---------- Main Layout ----------
    left, right = st.columns([1.65, 0.7], gap="large")

    # ============================================================
    # LEFT PANEL — Steps 1, 2, 4, 5
    # ============================================================
    with left:
        # --- Step 1: Upload / Select ---
        st.markdown("### 📂 Step 1 — Upload or Select Dataset")
        uploaded = st.file_uploader("📤 Upload CSV file", type=["csv"], key="cleaning_upload_csv")

        if uploaded:
            path = os.path.join(RAW_DIR, uploaded.name)
            with open(path, "wb") as f:
                f.write(uploaded.getbuffer())
            st.session_state["selected_dataset"] = uploaded.name
            st.success(f"✅ Uploaded `{uploaded.name}`")

        files = [f for f in os.listdir(RAW_DIR) if f.endswith(".csv")]
        if not files:
            st.info("📁 No datasets available.")
            return

        selected = st.selectbox(
            "Select dataset:",
            files,
            index=files.index(st.session_state.get("selected_dataset", files[0])),
            key="cleaning_dataset_select",
        )

        # persistent load
        if "df" not in st.session_state or st.session_state.get("current_file") != selected:
            df = pd.read_csv(os.path.join(RAW_DIR, selected), encoding="utf-8-sig", on_bad_lines="skip")
            st.session_state.df = df.copy()
            st.session_state.current_file = selected

        df = st.session_state.df

        # --- Step 2: Preview ---
        st.markdown("### 📊 Step 2 — Live Dataset Preview")
        st.dataframe(df.head(50), use_container_width=True, height=380)

        # --- Step 4: Conditional Filtering ---
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### 🎯 Step 4 — Conditional Filtering")

        c1, c2, c3 = st.columns([1.3, 1, 1.3])
        with c1:
            fcol = st.selectbox("Column:", df.columns, key="cleaning_fcol")
        with c2:
            fop = st.selectbox("Operator:", ["<", ">", "<=", ">=", "==", "!="], key="cleaning_fop")
        with c3:
            fval = st.text_input("Value:", key="cleaning_fval")

        if st.button("Apply Filter", key="cleaning_apply_filter"):
            try:
                df = clean_and_convert_column(df.copy(), fcol)
                before = len(df)
                if pd.api.types.is_numeric_dtype(df[fcol]):
                    try:
                        val = float(fval)
                    except ValueError:
                        st.error("⚠️ Enter numeric value")
                        return
                    ops = {
                        "==": df[fcol] == val, "!=": df[fcol] != val,
                        ">": df[fcol] > val, "<": df[fcol] < val,
                        ">=": df[fcol] >= val, "<=": df[fcol] <= val,
                    }
                    df = df[ops[fop]]
                else:
                    if fop in ["==", "!="]:
                        df = df[df[fcol].astype(str).str.strip() == fval.strip()] if fop == "==" else df[
                            df[fcol].astype(str).str.strip() != fval.strip()
                        ]
                    else:
                        st.warning("⚠️ String columns only support == and !=.")
                        return
                st.session_state.df = df.reset_index(drop=True)
                st.success(f"✅ Filter applied — Rows removed: {before - len(df)}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

        # --- Step 5: Save Cleaned Dataset ---
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### 💾 Step 5 — Save Cleaned Dataset")
        c1, c2 = st.columns(2)
        c1.metric("Rows", len(df))
        c2.metric("Columns", len(df.columns))

        if st.button("💾 Save Cleaned Dataset", key="cleaning_save"):
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            path = os.path.join(CLEANED_DIR, ts)
            os.makedirs(path, exist_ok=True)
            out = os.path.join(path, "cleaned_dataset.csv")
            df.to_csv(out, index=False)
            st.success(f"✅ Saved at `{out}`")
            st.download_button(
                "⬇️ Download Cleaned Dataset",
                df.to_csv(index=False).encode("utf-8"),
                file_name="cleaned_dataset.csv",
                mime="text/csv",
            )

    # ============================================================
    # RIGHT PANEL — Steps 3.1, 3.2, 3.3
    # ============================================================
    with right:
        # Step 3.1 — Select Columns
        st.markdown("### ✅ Step 3.1 — Select Columns")
        cols = st.multiselect("Keep columns:", df.columns, default=df.columns, key="cleaning_keep_cols")
        if st.button("Apply", key="cleaning_apply_keep"):
            st.session_state.df = df[cols]
            st.success("✅ Columns updated")
            st.rerun()

        # Step 3.2 — Clean Characters
        st.markdown("### 🧹 Step 3.2 — Clean Characters")
        ccol = st.selectbox("Column:", df.columns, key="cleaning_ccol")
        rem = st.text_input("Chars to remove (comma-separated):", "₹,$,%,,", key="cleaning_rem")
        auto = st.checkbox("Auto-remove ₹,$,%,,", True, key="cleaning_auto")
        if st.button("Clean Column", key="cleaning_clean_btn"):
            try:
                df = df.copy()
                chars = [c.strip() for c in rem.split(",") if c.strip()]
                if auto:
                    chars += ["₹", "$", ",", "%"]
                for ch in set(chars):
                    df[ccol] = df[ccol].astype(str).str.replace(ch, "", regex=False)
                df[ccol] = pd.to_numeric(df[ccol], errors="ignore")
                st.session_state.df = df
                st.success(f"✅ Cleaned `{ccol}`")
                st.rerun()
            except Exception as e:
                st.error(str(e))

        # Step 3.3 — Handle Missing Values
        st.markdown("### 🔧 Step 3.3 — Handle Missing Values")
        ncol = st.selectbox("Column:", df.columns, key="cleaning_ncol")
        method = st.radio(
            "Method:", ["Mean", "Median", "Zero", "Mode", "Custom", "Skip"],
            horizontal=True, key="cleaning_mthd"
        )
        custom = st.text_input("Custom value:", key="cleaning_cval")
        if st.button("Apply NA", key="cleaning_apply_na"):
            try:
                df = clean_and_convert_column(df.copy(), ncol)
                df.replace(["N/A", "n/a", "NA", "null", "--", "-", ""], pd.NA, inplace=True)
                if method == "Mean" and pd.api.types.is_numeric_dtype(df[ncol]):
                    df[ncol].fillna(df[ncol].mean(), inplace=True)
                elif method == "Median" and pd.api.types.is_numeric_dtype(df[ncol]):
                    df[ncol].fillna(df[ncol].median(), inplace=True)
                elif method == "Zero" and pd.api.types.is_numeric_dtype(df[ncol]):
                    df[ncol].fillna(0, inplace=True)
                elif method == "Mode":
                    m = df[ncol].mode()
                    if not m.empty:
                        df[ncol].fillna(m.iloc[0], inplace=True)
                elif method == "Custom" and custom.strip():
                    df[ncol].fillna(custom, inplace=True)
                st.session_state.df = df
                st.success(f"✅ Filled `{ncol}` using {method}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

    st.caption("💡 All transformations instantly reflect in Step 2 Preview.")
