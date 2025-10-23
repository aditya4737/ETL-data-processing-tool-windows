import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_sortables import sort_items


def dataset_composer_tab(COMPOSED_DIR):
    """Handle dataset composition logic."""
    st.title("🧱 Dataset Composer — Build Custom Datasets from Multiple CSVs")

    # Upload section
    uploaded = st.file_uploader(
        "📂 Upload one or more CSV files",
        type=["csv"],
        accept_multiple_files=True,
        key="composer_upload"
    )

    # If no file uploaded — lock the composer section
    if not uploaded:
        st.warning("🔒 Please upload at least one CSV file to unlock dataset composition options.")
        st.markdown("""
        <div style='opacity: 0.5; pointer-events: none;'>
            <b>Dataset Composer Locked</b><br>
            Upload one or more CSV files to start building a composed dataset.
        </div>
        """, unsafe_allow_html=True)
        return

    # Load CSV files safely
    all_dfs = {}
    for f in uploaded:
        try:
            df = pd.read_csv(f, encoding="utf-8-sig", on_bad_lines="skip")
            all_dfs[f.name] = df
        except Exception as e:
            st.error(f"❌ Error reading {f.name}: {e}")

    st.success(f"✅ Loaded {len(all_dfs)} file(s) successfully.")

    # Initialize session states
    if "final_selection" not in st.session_state:
        st.session_state["final_selection"] = []
    if "final_data" not in st.session_state:
        st.session_state["final_data"] = pd.DataFrame()
    if "refresh_flag" not in st.session_state:
        st.session_state["refresh_flag"] = 0
    if "file_selected" not in st.session_state:
        st.session_state["file_selected"] = {}
    if "save_composed_clicked" not in st.session_state:
        st.session_state["save_composed_clicked"] = False
    if "composed_df" not in st.session_state:
        st.session_state["composed_df"] = None  # To hold final composed preview

    file_names = list(all_dfs.keys())
    cols = st.columns(min(len(file_names), 3))

    # Iterate through uploaded files
    for i, fname in enumerate(file_names):
        df = all_dfs[fname]
        with cols[i % len(cols)]:
            st.markdown(f"#### 📄 {fname}")

            search_key = f"search_{fname}"
            search = st.text_input(
                f"🔍 Search columns in {fname}",
                value=st.session_state.get(search_key, ""),
                key=search_key
            )
            filtered_cols = [c for c in df.columns if search.lower() in c.lower()] if search else df.columns.tolist()

            selected = st.multiselect(
                f"Select columns from {fname}",
                filtered_cols,
                default=st.session_state["file_selected"].get(fname, []),
                key=f"select_{fname}"
            )

            st.session_state["file_selected"][fname] = selected

            # Add selected columns to final dataset
            if st.button(f"➕ Add Selected from {fname}", key=f"add_{fname}"):
                added = []
                for col in selected:
                    label = f"{fname} → {col}"
                    if label not in st.session_state["final_selection"]:
                        st.session_state["final_selection"].append(label)
                        col_data = all_dfs[fname][col]
                        final_len = len(st.session_state["final_data"])
                        col_len = len(col_data)

                        # Align column lengths safely
                        if final_len == 0:
                            st.session_state["final_data"] = pd.DataFrame({col: col_data})
                        else:
                            if col_len < final_len:
                                col_data = pd.concat(
                                    [col_data, pd.Series([None] * (final_len - col_len))],
                                    ignore_index=True
                                )
                            elif col_len > final_len:
                                diff = col_len - final_len
                                for c in st.session_state["final_data"].columns:
                                    st.session_state["final_data"][c] = pd.concat(
                                        [st.session_state["final_data"][c], pd.Series([None] * diff)],
                                        ignore_index=True
                                    )
                            st.session_state["final_data"][col] = col_data
                        added.append(col)

                if added:
                    st.success(f"✅ Added {len(added)} new column(s) from {fname}")
                    st.session_state["refresh_flag"] += 1
                    st.rerun()

    # ------------------------------------------------------------
    # Final dataset reorder and preview (no auto-save)
    # ------------------------------------------------------------
    st.markdown("---")
    st.subheader("📦 Final Dataset (Reorder Columns)")

    if st.session_state["final_selection"]:
        result_final = sort_items(
            items=st.session_state["final_selection"],
            multi_containers=False,
            direction="horizontal",
            key=f"final_dataset_zone_{st.session_state['refresh_flag']}"
        )

        st.session_state["final_selection"] = result_final
        ordered_cols = [
            item.split(" → ", 1)[1]
            for item in result_final
            if "→" in item and item.split(" → ", 1)[1] in st.session_state["final_data"].columns
        ]
        combined = st.session_state["final_data"][ordered_cols]

        # Just preview — never auto-save
        st.dataframe(combined.head(), use_container_width=True)
        st.caption(f"🧾 {len(combined.columns)} columns • {len(combined)} rows")

        # ------------------------------------------------------------
        # Explicit Save Action (only on button click)
        # ------------------------------------------------------------
        if st.button("💾 Save Final Composed Dataset", key="save_composed_btn"):
            os.makedirs(COMPOSED_DIR, exist_ok=True)
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            composed_dir = os.path.join(COMPOSED_DIR, f"composed_{ts}")
            os.makedirs(composed_dir, exist_ok=True)
            out_path = os.path.join(composed_dir, "composed_dataset.csv")
            combined.to_csv(out_path, index=False)

            st.session_state["composed_df"] = combined  # Store preview in session
            st.success(f"✅ Composed dataset saved successfully to `{out_path}`")

        # ------------------------------------------------------------
        # Show preview after saving (within Streamlit)
        # ------------------------------------------------------------
        if st.session_state["composed_df"] is not None:
            st.markdown("---")
            st.subheader("📊 Composed Dataset Preview (After Saving)")
            st.dataframe(st.session_state["composed_df"].head(50), use_container_width=True)
            st.download_button(
                "⬇️ Download Composed Dataset",
                st.session_state["composed_df"].to_csv(index=False).encode("utf-8"),
                file_name="composed_dataset.csv",
                mime="text/csv"
            )
