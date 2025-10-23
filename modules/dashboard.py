import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime


def visual_dashboard_tab(CLEANED_DIR):
    """Interactive Visualization Dashboard for cleaned datasets."""
    st.header("📊 Visual Dashboard — Explore and Visualize Your Cleaned Data")

    # ============================================================
    # STEP 1: Load Cleaned Dataset
    # ============================================================
    cleaned_folders = sorted(
        [d for d in os.listdir(CLEANED_DIR) if os.path.isdir(os.path.join(CLEANED_DIR, d))]
    )

    if not cleaned_folders:
        st.warning("⚠️ No cleaned datasets found. Please clean your data first.")
        return

    latest_folder = cleaned_folders[-1]
    latest_path = os.path.join(CLEANED_DIR, latest_folder)
    cleaned_files = [f for f in os.listdir(latest_path) if f.endswith(".csv")]

    selected_file = st.selectbox("📂 Select a cleaned dataset:", cleaned_files)
    df = pd.read_csv(os.path.join(latest_path, selected_file), encoding="utf-8-sig", on_bad_lines="skip")

    st.write(f"### 🧾 Dataset Preview — {selected_file}")
    st.dataframe(df.head(), use_container_width=True)
    st.caption(f"Rows: {len(df)} | Columns: {len(df.columns)}")

    # ============================================================
    # STEP 2: Column Detection
    # ============================================================
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    st.markdown("---")
    st.subheader("🧠 Column Overview")
    st.write(f"**Numeric Columns:** {numeric_cols if numeric_cols else 'None'}")
    st.write(f"**Categorical Columns:** {cat_cols if cat_cols else 'None'}")

    # ============================================================
    # STEP 3: Visualization Controls
    # ============================================================
    st.markdown("---")
    st.subheader("🎨 Visualization Controls")

    graph_type = st.selectbox(
        "📊 Select Visualization Type:",
        ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Histogram", "Box Plot"]
    )

    # Choose X and Y columns
    x_col = st.selectbox("🧩 Select X-axis Column:", df.columns)
    y_col = None
    if graph_type not in ["Pie Chart", "Histogram"]:
        y_col = st.selectbox("🧮 Select Y-axis Column:", numeric_cols, index=0 if numeric_cols else None)

    # Optional aggregation
    aggregate = st.checkbox("🧠 Aggregate by X-axis (grouped mean/sum)", value=False)
    agg_func = None
    if aggregate:
        agg_func = st.selectbox("Aggregation Function:", ["sum", "mean", "count", "max", "min"])
        if y_col:
            try:
                if agg_func == "sum":
                    df = df.groupby(x_col)[y_col].sum().reset_index()
                elif agg_func == "mean":
                    df = df.groupby(x_col)[y_col].mean().reset_index()
                elif agg_func == "count":
                    df = df.groupby(x_col)[y_col].count().reset_index()
                elif agg_func == "max":
                    df = df.groupby(x_col)[y_col].max().reset_index()
                elif agg_func == "min":
                    df = df.groupby(x_col)[y_col].min().reset_index()
            except Exception as e:
                st.error(f"⚠️ Error aggregating data: {e}")

    # ============================================================
    # STEP 4: Generate Visualization
    # ============================================================
    st.markdown("---")
    st.subheader("📈 Visualization Output")

    if st.button("✨ Generate Visualization"):
        try:
            fig, ax = plt.subplots(figsize=(8, 5))

            if graph_type == "Bar Chart":
                ax.bar(df[x_col], df[y_col])
                ax.set_ylabel(y_col)
            elif graph_type == "Line Chart":
                ax.plot(df[x_col], df[y_col], marker='o')
                ax.set_ylabel(y_col)
            elif graph_type == "Scatter Plot":
                ax.scatter(df[x_col], df[y_col], alpha=0.7)
                ax.set_ylabel(y_col)
            elif graph_type == "Pie Chart":
                if x_col in cat_cols:
                    pie_data = df[x_col].value_counts()
                    ax.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%", startangle=90)
                else:
                    st.error("⚠️ Pie chart requires a categorical column.")
                    return
            elif graph_type == "Histogram":
                if x_col in numeric_cols:
                    ax.hist(df[x_col], bins=20, color='skyblue', edgecolor='black')
                else:
                    st.error("⚠️ Histogram requires a numeric column.")
                    return
            elif graph_type == "Box Plot":
                if x_col in cat_cols and y_col in numeric_cols:
                    df.boxplot(column=y_col, by=x_col, ax=ax)
                else:
                    st.error("⚠️ Box plot requires categorical X and numeric Y.")
                    return

            ax.set_title(f"{graph_type} of {y_col if y_col else x_col} vs {x_col}")
            ax.set_xlabel(x_col)
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)

            # Save plot
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            plot_path = os.path.join(latest_path, f"visual_{graph_type.replace(' ', '_')}_{timestamp}.png")
            fig.savefig(plot_path, bbox_inches="tight")

            st.success(f"✅ Visualization saved to `{plot_path}`")

            with open(plot_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download Visualization Image",
                    data=f,
                    file_name=os.path.basename(plot_path),
                    mime="image/png"
                )

        except Exception as e:
            st.error(f"❌ Failed to generate visualization: {e}")
