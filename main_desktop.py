# import os
# import sys
# from datetime import datetime
# import pandas as pd
# import numpy as np
# from PyQt5 import QtWidgets, QtGui
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure

# # ======================================================
# # THEME + COLORS
# # ======================================================
# def get_streamlit_like_qss() -> str:
#     bg = "#0f172a"
#     panel = "#111827"
#     panel2 = "#1e293b"
#     border = "#334155"
#     text = "#e2e8f0"
#     accent = "#facc15"
#     primary = "#2563eb"
#     primary_hover = "#1d4ed8"

#     return f"""
#     * {{
#         font-family: 'Segoe UI', 'Inter', 'Roboto', Arial, sans-serif;
#         color: {text};
#     }}
#     QWidget {{ background: {bg}; }}
#     QGroupBox {{
#         background: {panel};
#         border: 1px solid {border};
#         border-radius: 12px;
#         margin-top: 14px;
#         padding: 10px;
#     }}
#     QGroupBox::title {{
#         subcontrol-origin: margin;
#         left: 10px;
#         top: -8px;
#         padding: 2px 6px;
#         color: {accent};
#         background: {bg};
#     }}
#     QPushButton {{
#         background: {primary};
#         color: white;
#         border-radius: 8px;
#         padding: 6px 12px;
#     }}
#     QPushButton:hover {{ background: {primary_hover}; }}
#     QLineEdit, QComboBox {{
#         background: {panel2};
#         border: 1px solid {border};
#         border-radius: 6px;
#         padding: 5px 8px;
#     }}
#     QTableWidget {{
#         background: {panel2};
#         gridline-color: {border};
#         border: 1px solid {border};
#         border-radius: 8px;
#     }}
#     QHeaderView::section {{
#         background: {panel};
#         color: {text};
#         border: none;
#         border-right: 1px solid {border};
#     }}
#     QLabel {{ color: {text}; }}
#     """

# def apply_streamlit_theme(app: QtWidgets.QApplication):
#     pal = QtGui.QPalette()
#     pal.setColor(QtGui.QPalette.Window, QtGui.QColor("#0f172a"))
#     pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#e2e8f0"))
#     app.setPalette(pal)
#     app.setStyle("Fusion")
#     app.setStyleSheet(get_streamlit_like_qss())

# # ======================================================
# # PATHS
# # ======================================================
# ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_DIR = os.path.join(ROOT_DIR, "data")
# RAW_DIR = os.path.join(DATA_DIR, "raw")
# CLEANED_DIR = os.path.join(DATA_DIR, "cleaned")
# COMPOSED_DIR = os.path.join(DATA_DIR, "composed_data")

# for d in [DATA_DIR, RAW_DIR, CLEANED_DIR, COMPOSED_DIR]:
#     os.makedirs(d, exist_ok=True)

# # ======================================================
# # HELPERS
# # ======================================================
# def df_to_table(df: pd.DataFrame, table: QtWidgets.QTableWidget, limit=50):
#     """Render DataFrame to QTableWidget"""
#     table.clear()
#     if df is None or df.empty:
#         table.setRowCount(0)
#         table.setColumnCount(0)
#         return
#     df = df.head(limit)
#     table.setRowCount(len(df))
#     table.setColumnCount(len(df.columns))
#     table.setHorizontalHeaderLabels([str(c) for c in df.columns])
#     for r in range(len(df)):
#         for c in range(len(df.columns)):
#             table.setItem(r, c, QtWidgets.QTableWidgetItem(str(df.iat[r, c])))
#     table.resizeColumnsToContents()
#     table.horizontalHeader().setStretchLastSection(True)

# def safe_clean_numeric(val):
#     if pd.isna(val):
#         return None
#     s = str(val).replace("$", "").replace("₹", "").replace(",", "").replace("%", "").strip()
#     try:
#         return float(s)
#     except:
#         return None

# class MplCanvas(FigureCanvas):
#     def __init__(self, width=6, height=4, dpi=100):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.ax = fig.add_subplot(111)
#         super().__init__(fig)

# # ======================================================
# # COMPOSER TAB
# # ======================================================
# class ComposerTab(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#         self.all_dfs = {}
#         self.final_data = pd.DataFrame()

#         layout = QtWidgets.QVBoxLayout(self)
#         layout.addWidget(QtWidgets.QLabel("🧱 Dataset Composer — Combine & Reorder Columns"))

#         # Upload
#         hl = QtWidgets.QHBoxLayout()
#         self.upload_btn = QtWidgets.QPushButton("📂 Upload CSV Files")
#         self.upload_btn.clicked.connect(self.load_files)
#         self.info = QtWidgets.QLabel("No files uploaded.")
#         hl.addWidget(self.upload_btn)
#         hl.addWidget(self.info)
#         layout.addLayout(hl)

#         # File previews
#         self.scroll = QtWidgets.QScrollArea()
#         self.scroll.setWidgetResizable(True)
#         self.container = QtWidgets.QWidget()
#         self.grid = QtWidgets.QGridLayout(self.container)
#         self.scroll.setWidget(self.container)
#         layout.addWidget(self.scroll, 3)

#         # Preview
#         layout.addWidget(QtWidgets.QLabel("📊 Combined Dataset Preview"))
#         self.preview = QtWidgets.QTableWidget()
#         layout.addWidget(self.preview, 3)

#         # Reorder
#         reorder_box = QtWidgets.QGroupBox("Reorder / Remove Columns")
#         rv = QtWidgets.QHBoxLayout(reorder_box)
#         self.col_list = QtWidgets.QListWidget()
#         self.move_up = QtWidgets.QPushButton("⬆ Move Up")
#         self.move_down = QtWidgets.QPushButton("⬇ Move Down")
#         self.remove_btn = QtWidgets.QPushButton("❌ Remove Selected")
#         self.move_up.clicked.connect(self.move_up_col)
#         self.move_down.clicked.connect(self.move_down_col)
#         self.remove_btn.clicked.connect(self.remove_selected_col)
#         rv.addWidget(self.col_list)
#         btns = QtWidgets.QVBoxLayout()
#         btns.addWidget(self.move_up)
#         btns.addWidget(self.move_down)
#         btns.addWidget(self.remove_btn)
#         rv.addLayout(btns)
#         layout.addWidget(reorder_box)

#         # Save
#         self.save_btn = QtWidgets.QPushButton("💾 Save Composed Dataset")
#         self.save_btn.clicked.connect(self.save_dataset)
#         layout.addWidget(self.save_btn)

#     def load_files(self):
#         paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select CSV Files", RAW_DIR, "CSV Files (*.csv)")
#         if not paths:
#             return
#         self.all_dfs.clear()
#         self.final_data = pd.DataFrame()
#         while self.grid.count():
#             item = self.grid.takeAt(0)
#             if item.widget():
#                 item.widget().deleteLater()

#         for i, path in enumerate(paths):
#             df = pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip")
#             fname = os.path.basename(path)
#             self.all_dfs[fname] = df

#             box = QtWidgets.QGroupBox(f"📄 {fname}")
#             v = QtWidgets.QVBoxLayout(box)
#             listw = QtWidgets.QListWidget()
#             listw.addItems(df.columns)
#             listw.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
#             add_btn = QtWidgets.QPushButton("➕ Add Selected Columns")

#             def add_selected(fname=fname, df=df, lw=listw):
#                 selected = [i.text() for i in lw.selectedItems()]
#                 for col in selected:
#                     label = f"{fname} → {col}"
#                     self.final_data[label] = df[col]
#                 df_to_table(self.final_data, self.preview)
#                 self.col_list.clear()
#                 self.col_list.addItems(self.final_data.columns)

#             add_btn.clicked.connect(add_selected)
#             v.addWidget(listw)
#             v.addWidget(add_btn)
#             row, col = divmod(i, 3)
#             self.grid.addWidget(box, row, col)
#         self.info.setText(f"✅ Loaded {len(paths)} files")

#     def move_up_col(self):
#         row = self.col_list.currentRow()
#         if row <= 0: return
#         item = self.col_list.takeItem(row)
#         self.col_list.insertItem(row - 1, item)
#         self.reorder_columns()

#     def move_down_col(self):
#         row = self.col_list.currentRow()
#         if row < 0 or row >= self.col_list.count() - 1: return
#         item = self.col_list.takeItem(row)
#         self.col_list.insertItem(row + 1, item)
#         self.reorder_columns()

#     def remove_selected_col(self):
#         row = self.col_list.currentRow()
#         if row >= 0:
#             self.col_list.takeItem(row)
#             self.reorder_columns()

#     def reorder_columns(self):
#         if self.final_data.empty:
#             return
#         new_order = [self.col_list.item(i).text() for i in range(self.col_list.count())]
#         new_order = [c for c in new_order if c in self.final_data.columns]
#         self.final_data = self.final_data[new_order]
#         df_to_table(self.final_data, self.preview)

#     def save_dataset(self):
#         if self.final_data.empty:
#             QtWidgets.QMessageBox.warning(self, "No Data", "Nothing to save.")
#             return
#         ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#         outdir = os.path.join(COMPOSED_DIR, f"composed_{ts}")
#         os.makedirs(outdir, exist_ok=True)
#         out = os.path.join(outdir, "composed_dataset.csv")
#         self.final_data.to_csv(out, index=False)
#         QtWidgets.QMessageBox.information(self, "Saved", f"✅ Dataset saved at:\n{out}")

# # ======================================================
# # CLEANING TAB
# # ======================================================
# class CleaningTab(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#         self.df = pd.DataFrame()

#         root = QtWidgets.QVBoxLayout(self)
#         root.setSpacing(12)
#         title = QtWidgets.QLabel("🧼 Data Cleaning — Smart Tools for Refining Data")
#         title.setStyleSheet("font-size:18px; font-weight:bold; color:#facc15;")
#         root.addWidget(title)

#         grid = QtWidgets.QGridLayout()
#         grid.setColumnStretch(0, 7)
#         grid.setColumnStretch(1, 3)
#         grid.setHorizontalSpacing(14)
#         grid.setVerticalSpacing(10)

#         # Step 1
#         load_box = QtWidgets.QGroupBox("📂 Step 1 — Load Dataset")
#         hl = QtWidgets.QHBoxLayout(load_box)
#         self.load_btn = QtWidgets.QPushButton("📁 Open CSV")
#         self.load_btn.clicked.connect(self.load_csv)
#         self.file_lbl = QtWidgets.QLabel("No file loaded.")
#         hl.addWidget(self.load_btn)
#         hl.addWidget(self.file_lbl)
#         grid.addWidget(load_box, 0, 0)

#         # Step 3
#         keep_box = QtWidgets.QGroupBox("✅ Step 3 — Keep / Remove Columns")
#         kv = QtWidgets.QVBoxLayout(keep_box)
#         self.keep_list = QtWidgets.QListWidget()
#         self.keep_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
#         self.keep_btn = QtWidgets.QPushButton("Apply")
#         self.keep_btn.clicked.connect(self.keep_columns)
#         kv.addWidget(self.keep_list)
#         kv.addWidget(self.keep_btn)
#         grid.addWidget(keep_box, 0, 1, 2, 1)

#         # Step 2
#         prev_box = QtWidgets.QGroupBox("📊 Step 2 — Dataset Preview")
#         pv = QtWidgets.QVBoxLayout(prev_box)
#         self.table = QtWidgets.QTableWidget()
#         pv.addWidget(self.table)
#         grid.addWidget(prev_box, 1, 0, 3, 1)

#         # Step 4
#         na_box = QtWidgets.QGroupBox("🔧 Step 4 — Handle Missing Values")
#         nv = QtWidgets.QGridLayout(na_box)
#         nv.addWidget(QtWidgets.QLabel("Column:"), 0, 0)
#         self.na_col = QtWidgets.QComboBox()
#         nv.addWidget(self.na_col, 0, 1)
#         nv.addWidget(QtWidgets.QLabel("Method:"), 0, 2)
#         self.na_method = QtWidgets.QComboBox()
#         self.na_method.addItems(["Mean", "Median", "Zero", "Mode", "Custom Value"])
#         nv.addWidget(self.na_method, 0, 3)
#         nv.addWidget(QtWidgets.QLabel("Custom:"), 1, 0)
#         self.na_custom = QtWidgets.QLineEdit()
#         nv.addWidget(self.na_custom, 1, 1, 1, 3)
#         self.na_apply = QtWidgets.QPushButton("Apply")
#         self.na_apply.clicked.connect(self.apply_missing)
#         nv.addWidget(self.na_apply, 2, 0, 1, 4)
#         grid.addWidget(na_box, 2, 1)

#         # Step 5
#         f_box = QtWidgets.QGroupBox("🎯 Step 5 — Conditional Filtering")
#         fv = QtWidgets.QGridLayout(f_box)
#         fv.addWidget(QtWidgets.QLabel("Column:"), 0, 0)
#         self.filter_col = QtWidgets.QComboBox()
#         fv.addWidget(self.filter_col, 0, 1)
#         fv.addWidget(QtWidgets.QLabel("Operation:"), 0, 2)
#         self.filter_op = QtWidgets.QComboBox()
#         self.filter_op.addItems(["<", ">", "<=", ">=", "==", "!="])
#         fv.addWidget(self.filter_op, 0, 3)
#         fv.addWidget(QtWidgets.QLabel("Value:"), 1, 0)
#         self.filter_val = QtWidgets.QLineEdit()
#         fv.addWidget(self.filter_val, 1, 1, 1, 3)
#         self.filter_btn = QtWidgets.QPushButton("Apply Filter")
#         self.filter_btn.clicked.connect(self.apply_filter)
#         fv.addWidget(self.filter_btn, 2, 0, 1, 4)
#         grid.addWidget(f_box, 3, 1)

#         root.addLayout(grid)

#         footer = QtWidgets.QHBoxLayout()
#         self.stats_lbl = QtWidgets.QLabel("Rows: 0 | Columns: 0")
#         self.save_btn = QtWidgets.QPushButton("💾 Save Cleaned Dataset")
#         self.save_btn.clicked.connect(self.save_cleaned)
#         footer.addWidget(self.stats_lbl)
#         footer.addStretch(1)
#         footer.addWidget(self.save_btn)
#         root.addLayout(footer)

#     # ---- Logic ----
#     def load_csv(self):
#         path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select CSV", RAW_DIR, "CSV Files (*.csv)")
#         if not path: return
#         self.df = pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip")
#         df_to_table(self.df, self.table)
#         self.file_lbl.setText(os.path.basename(path))
#         self.keep_list.clear()
#         self.keep_list.addItems(self.df.columns)
#         self.na_col.clear()
#         self.na_col.addItems(self.df.columns)
#         self.filter_col.clear()
#         self.filter_col.addItems(self.df.columns)
#         self.stats_lbl.setText(f"Rows: {len(self.df)} | Columns: {len(self.df.columns)}")

#     def keep_columns(self):
#         cols = [i.text() for i in self.keep_list.selectedItems()]
#         if cols:
#             self.df = self.df[cols]
#             df_to_table(self.df, self.table)
#             self.stats_lbl.setText(f"Rows: {len(self.df)} | Columns: {len(self.df.columns)}")

#     def apply_missing(self):
#         col = self.na_col.currentText()
#         if col not in self.df.columns: return
#         method = self.na_method.currentText()
#         try:
#             if method == "Mean": self.df[col].fillna(self.df[col].mean(), inplace=True)
#             elif method == "Median": self.df[col].fillna(self.df[col].median(), inplace=True)
#             elif method == "Zero": self.df[col].fillna(0, inplace=True)
#             elif method == "Mode":
#                 m = self.df[col].mode()
#                 if not m.empty: self.df[col].fillna(m.iloc[0], inplace=True)
#             elif method == "Custom Value":
#                 self.df[col].fillna(self.na_custom.text(), inplace=True)
#             df_to_table(self.df, self.table)
#         except Exception as e:
#             QtWidgets.QMessageBox.warning(self, "Error", str(e))

#     def apply_filter(self):
#         col = self.filter_col.currentText()
#         op = self.filter_op.currentText()
#         val = self.filter_val.text().strip()
#         if col not in self.df.columns or not val:
#             return
#         try:
#             v = safe_clean_numeric(val)
#             if v is not None:
#                 expr = f"self.df[col] {op} v"
#                 mask = eval(expr)
#             else:
#                 if op not in ["==", "!="]:
#                     QtWidgets.QMessageBox.warning(self, "Invalid", "Non-numeric filters support only == or !=")
#                     return
#                 mask = self.df[col].astype(str).str.strip().__eq__(val) if op == "==" else self.df[col].astype(str).str.strip().__ne__(val)
#             self.df = self.df[mask].reset_index(drop=True)
#             df_to_table(self.df, self.table)
#             self.stats_lbl.setText(f"Rows: {len(self.df)} | Columns: {len(self.df.columns)}")
#         except Exception as e:
#             QtWidgets.QMessageBox.warning(self, "Error", str(e))

#     def save_cleaned(self):
#         if self.df.empty:
#             QtWidgets.QMessageBox.information(self, "Empty", "No data to save.")
#             return
#         ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#         outdir = os.path.join(CLEANED_DIR, ts)
#         os.makedirs(outdir, exist_ok=True)
#         out = os.path.join(outdir, "cleaned_dataset.csv")
#         self.df.to_csv(out, index=False)
#         QtWidgets.QMessageBox.information(self, "Saved", f"✅ Saved at:\n{out}")

# # ======================================================
# # DASHBOARD TAB
# # ======================================================
# class DashboardTab(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#         self.df = pd.DataFrame()
#         layout = QtWidgets.QVBoxLayout(self)
#         title = QtWidgets.QLabel("📈 Visual Dashboard — Explore Your Data")
#         title.setStyleSheet("font-size:18px; font-weight:bold; color:#facc15;")
#         layout.addWidget(title)

#         load_box = QtWidgets.QHBoxLayout()
#         self.load_latest = QtWidgets.QPushButton("📤 Load Latest Cleaned")
#         self.pick_cleaned = QtWidgets.QPushButton("📁 Open CSV")
#         self.file_lbl = QtWidgets.QLabel("No dataset loaded.")
#         load_box.addWidget(self.load_latest)
#         load_box.addWidget(self.pick_cleaned)
#         load_box.addWidget(self.file_lbl)
#         layout.addLayout(load_box)
#         self.load_latest.clicked.connect(self.load_latest_cleaned)
#         self.pick_cleaned.clicked.connect(self.pick_cleaned_csv)

#         self.table = QtWidgets.QTableWidget()
#         layout.addWidget(self.table, 3)

#         ctrl = QtWidgets.QHBoxLayout()
#         self.graph_type = QtWidgets.QComboBox()
#         self.graph_type.addItems(["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Histogram", "Box Plot"])
#         self.x_col = QtWidgets.QComboBox()
#         self.y_col = QtWidgets.QComboBox()
#         self.plot_btn = QtWidgets.QPushButton("🎯 Generate Plot")
#         ctrl.addWidget(self.graph_type)
#         ctrl.addWidget(self.x_col)
#         ctrl.addWidget(self.y_col)
#         ctrl.addWidget(self.plot_btn)
#         layout.addLayout(ctrl)
#         self.plot_btn.clicked.connect(self.draw_plot)

#         self.canvas = MplCanvas(width=7, height=4)
#         layout.addWidget(self.canvas)

#     def load_latest_cleaned(self):
#         folders = sorted([d for d in os.listdir(CLEANED_DIR) if os.path.isdir(os.path.join(CLEANED_DIR, d))])
#         if not folders:
#             QtWidgets.QMessageBox.warning(self, "No Data", "No cleaned dataset found.")
#             return
#         path = os.path.join(CLEANED_DIR, folders[-1], "cleaned_dataset.csv")
#         self._load_df(path)

#     def pick_cleaned_csv(self):
#         path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select CSV", CLEANED_DIR, "CSV Files (*.csv)")
#         if not path:
#             return
#         self._load_df(path)

#     def _load_df(self, path):
#         self.df = pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip")
#         df_to_table(self.df, self.table)
#         self.file_lbl.setText(os.path.basename(path))
#         self.x_col.clear()
#         self.y_col.clear()
#         self.x_col.addItems(self.df.columns)
#         self.y_col.addItems(self.df.select_dtypes(include=["number"]).columns)

#     def draw_plot(self):
#         if self.df.empty: return
#         gtype = self.graph_type.currentText()
#         x = self.x_col.currentText()
#         y = self.y_col.currentText()
#         self.canvas.ax.clear()
#         try:
#             if gtype == "Bar Chart":
#                 self.canvas.ax.bar(self.df[x], self.df[y])
#             elif gtype == "Line Chart":
#                 self.canvas.ax.plot(self.df[x], self.df[y])
#             elif gtype == "Scatter Plot":
#                 self.canvas.ax.scatter(self.df[x], self.df[y])
#             elif gtype == "Pie Chart":
#                 counts = self.df[x].value_counts()
#                 self.canvas.ax.pie(counts, labels=counts.index, autopct="%1.1f%%")
#             elif gtype == "Histogram":
#                 self.canvas.ax.hist(self.df[y].dropna(), bins=20)
#             elif gtype == "Box Plot":
#                 self.canvas.ax.boxplot(self.df[y].dropna())
#             self.canvas.ax.set_title(f"{gtype}: {y} vs {x}")
#             self.canvas.figure.tight_layout()
#             self.canvas.draw()
#         except Exception as e:
#             QtWidgets.QMessageBox.warning(self, "Plot Error", str(e))

# # ======================================================
# # MAIN WINDOW
# # ======================================================
# class MainWindow(QtWidgets.QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Data Transformation Pipeline (Desktop)")
#         self.resize(1200, 800)
#         tabs = QtWidgets.QTabWidget()
#         tabs.addTab(ComposerTab(), "🧱 Dataset Composer")
#         tabs.addTab(CleaningTab(), "🧼 Data Cleaning")
#         tabs.addTab(DashboardTab(), "📈 Visual Dashboard")
#         self.setCentralWidget(tabs)

# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     apply_streamlit_theme(app)
#     win = MainWindow()
#     win.show()
#     sys.exit(app.exec_())










import os
import sys
from datetime import datetime
import pandas as pd
import numpy as np
from PyQt5 import QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# ======================================================
# THEME + COLORS
# ======================================================
def get_streamlit_like_qss() -> str:
    bg = "#0f172a"
    panel = "#111827"
    panel2 = "#1e293b"
    border = "#334155"
    text = "#e2e8f0"
    accent = "#facc15"
    primary = "#2563eb"
    primary_hover = "#1d4ed8"

    return f"""
    * {{
        font-family: 'Segoe UI', 'Inter', 'Roboto', Arial, sans-serif;
        color: {text};
    }}
    QWidget {{ background: {bg}; }}
    QGroupBox {{
        background: {panel};
        border: 1px solid {border};
        border-radius: 12px;
        margin-top: 14px;
        padding: 10px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        top: -8px;
        padding: 2px 6px;
        color: {accent};
        background: {bg};
    }}
    QPushButton {{
        background: {primary};
        color: white;
        border-radius: 8px;
        padding: 6px 12px;
    }}
    QPushButton:hover {{ background: {primary_hover}; }}
    QLineEdit, QComboBox {{
        background: {panel2};
        border: 1px solid {border};
        border-radius: 6px;
        padding: 5px 8px;
    }}
    QListWidget {{
        background: {panel2};
        border: 1px solid {border};
        border-radius: 8px;
    }}
    QTableWidget {{
        background: {panel2};
        gridline-color: {border};
        border: 1px solid {border};
        border-radius: 8px;
    }}
    QLabel#hint {{
        color: #94a3b8;
    }}
    QLabel#warning {{
        color: {accent};
        font-style: italic;
    }}
    """


def apply_streamlit_theme(app: QtWidgets.QApplication):
    pal = QtGui.QPalette()
    pal.setColor(QtGui.QPalette.Window, QtGui.QColor("#0f172a"))
    pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#e2e8f0"))
    app.setPalette(pal)
    app.setStyle("Fusion")
    app.setStyleSheet(get_streamlit_like_qss())


# ======================================================
# PATHS
# ======================================================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
CLEANED_DIR = os.path.join(DATA_DIR, "cleaned")
COMPOSED_DIR = os.path.join(DATA_DIR, "composed")

for d in [DATA_DIR, RAW_DIR, CLEANED_DIR, COMPOSED_DIR]:
    os.makedirs(d, exist_ok=True)


# ======================================================
# HELPERS
# ======================================================
def df_to_table(df: pd.DataFrame, table: QtWidgets.QTableWidget, limit=50):
    """Render pandas DataFrame to QTableWidget (first `limit` rows)."""
    table.clear()
    if df is None or df.empty:
        table.setRowCount(0)
        table.setColumnCount(0)
        return
    view = df.head(limit)
    table.setRowCount(len(view))
    table.setColumnCount(len(view.columns))
    table.setHorizontalHeaderLabels([str(c) for c in view.columns])
    for r in range(len(view)):
        for c in range(len(view.columns)):
            table.setItem(r, c, QtWidgets.QTableWidgetItem(str(view.iat[r, c])))
    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)


def clean_column_symbols(df, col, extra_chars=None):
    """Remove ₹, $, %, commas, spaces, and extras safely."""
    if col not in df.columns:
        return df
    chars = ["₹", "$", "%", ",", " "]
    if extra_chars:
        for ch in extra_chars:
            if ch and ch not in chars:
                chars.append(ch)
    s = df[col].astype(str)
    for ch in chars:
        s = s.str.replace(ch, "", regex=False)
    df[col] = pd.to_numeric(s, errors="ignore")
    return df


def safe_clean_numeric(val):
    if pd.isna(val):
        return None
    if isinstance(val, (int, float, np.number)):
        return float(val)
    s = str(val).replace("$", "").replace("₹", "").replace(",", "").replace("%", "").strip()
    try:
        return float(s)
    except Exception:
        return None


class MplCanvas(FigureCanvas):
    def __init__(self, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)


# ======================================================
# COMPOSER TAB
# ======================================================
class ComposerTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.all_dfs = {}
        self.final_data = pd.DataFrame()

        layout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel("🧱 Dataset Composer — Build and Reorder Datasets")
        title.setStyleSheet("font-size:16px; font-weight:bold; color:#facc15;")
        layout.addWidget(title)

        # Upload section
        self.upload_btn = QtWidgets.QPushButton("📂 Upload CSV Files")
        self.upload_btn.clicked.connect(self.load_files)
        self.info = QtWidgets.QLabel("No files uploaded yet.")
        self.info.setObjectName("hint")

        hl = QtWidgets.QHBoxLayout()
        hl.addWidget(self.upload_btn)
        hl.addWidget(self.info)
        layout.addLayout(hl)

        # Scroll grid to hold uploaded file previews
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout(self.container)
        self.grid.setSpacing(12)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll, 3)

        # Combined dataset preview
        layout.addWidget(QtWidgets.QLabel("📊 Combined Dataset Preview"))
        self.preview = QtWidgets.QTableWidget()
        layout.addWidget(self.preview, 3)

        # Reordering controls
        reorder_box = QtWidgets.QGroupBox("Reorder or Remove Columns")
        rv = QtWidgets.QHBoxLayout(reorder_box)
        self.col_list = QtWidgets.QListWidget()

        self.move_up = QtWidgets.QPushButton("⬆ Move Up")
        self.move_down = QtWidgets.QPushButton("⬇ Move Down")
        self.remove_btn = QtWidgets.QPushButton("❌ Remove Selected")

        self.move_up.clicked.connect(self.move_up_col)
        self.move_down.clicked.connect(self.move_down_col)
        self.remove_btn.clicked.connect(self.remove_selected_col)

        rv.addWidget(self.col_list)
        btns = QtWidgets.QVBoxLayout()
        btns.addWidget(self.move_up)
        btns.addWidget(self.move_down)
        btns.addWidget(self.remove_btn)
        rv.addLayout(btns)
        layout.addWidget(reorder_box)

        # Save button
        self.save_btn = QtWidgets.QPushButton("💾 Save Composed Dataset")
        self.save_btn.clicked.connect(self.save_dataset)
        layout.addWidget(self.save_btn)

    # ---------------------------------------------------
    # Load multiple CSVs
    # ---------------------------------------------------
    def load_files(self):
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select CSV Files", "", "CSV Files (*.csv)")
        if not paths:
            return

        self.all_dfs.clear()
        self.final_data = pd.DataFrame()

        # Clear grid
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add each file
        for i, p in enumerate(paths):
            df = pd.read_csv(p, encoding="utf-8-sig", on_bad_lines="skip")
            fname = os.path.basename(p)
            self.all_dfs[fname] = df

            group = QtWidgets.QGroupBox(f"📄 {fname}")
            v = QtWidgets.QVBoxLayout(group)

            # Search bar for columns
            search = QtWidgets.QLineEdit()
            search.setPlaceholderText("🔍 Search columns...")
            v.addWidget(search)

            # Column list
            listw = QtWidgets.QListWidget()
            listw.addItems(df.columns)
            listw.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
            v.addWidget(listw)

            # Add button
            add_btn = QtWidgets.QPushButton("➕ Add Selected Columns")
            v.addWidget(add_btn)

            # Search filter
            def do_filter(le=search, lw=listw, cols=df.columns):
                txt = le.text().lower().strip()
                lw.clear()
                lw.addItems([c for c in cols if txt in c.lower()])

            search.textChanged.connect(do_filter)

            # Add selected columns
            def add_selected(fname=fname, df=df, lw=listw):
                selected = [i.text() for i in lw.selectedItems()]
                if not selected:
                    return

                for col in selected:
                    series = df[col].reset_index(drop=True)
                    if self.final_data.empty:
                        self.final_data = pd.DataFrame({f"{fname} → {col}": series})
                    else:
                        # Align lengths before adding
                        if len(series) < len(self.final_data):
                            series = pd.concat(
                                [series, pd.Series([None] * (len(self.final_data) - len(series)))],
                                ignore_index=True,
                            )
                        elif len(series) > len(self.final_data):
                            for c in self.final_data.columns:
                                self.final_data[c] = pd.concat(
                                    [self.final_data[c], pd.Series([None] * (len(series) - len(self.final_data)))],
                                    ignore_index=True,
                                )
                        self.final_data[f"{fname} → {col}"] = series

                df_to_table(self.final_data, self.preview)
                self.col_list.clear()
                self.col_list.addItems(self.final_data.columns)

            add_btn.clicked.connect(add_selected)

            row, col = divmod(i, 3)
            self.grid.addWidget(group, row, col)

        self.info.setText(f"✅ Loaded {len(paths)} file(s)")

    # ---------------------------------------------------
    # Column operations
    # ---------------------------------------------------
    def move_up_col(self):
        row = self.col_list.currentRow()
        if row <= 0:
            return
        item = self.col_list.takeItem(row)
        self.col_list.insertItem(row - 1, item)
        self.reorder_columns()

    def move_down_col(self):
        row = self.col_list.currentRow()
        if row < 0 or row >= self.col_list.count() - 1:
            return
        item = self.col_list.takeItem(row)
        self.col_list.insertItem(row + 1, item)
        self.reorder_columns()

    def remove_selected_col(self):
        row = self.col_list.currentRow()
        if row >= 0:
            self.col_list.takeItem(row)
            self.reorder_columns()

    def reorder_columns(self):
        if self.final_data.empty:
            return
        new_order = [self.col_list.item(i).text() for i in range(self.col_list.count())]
        new_order = [c for c in new_order if c in self.final_data.columns]
        self.final_data = self.final_data[new_order]
        df_to_table(self.final_data, self.preview)

    # ---------------------------------------------------
    # Save composed dataset
    # ---------------------------------------------------
    def save_dataset(self):
        if self.final_data.empty:
            QtWidgets.QMessageBox.information(self, "No Data", "Nothing to save.")
            return
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        outdir = os.path.join(COMPOSED_DIR, f"composed_{ts}")
        os.makedirs(outdir, exist_ok=True)
        outpath = os.path.join(outdir, "composed_dataset.csv")
        self.final_data.to_csv(outpath, index=False)
        QtWidgets.QMessageBox.information(self, "Saved", f"✅ Dataset saved at:\n{outpath}")

# ======================================================
# CLEANING TAB
# ======================================================
class CleaningTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.df = pd.DataFrame()
        # tracks columns that have been cleaned (symbols removed + numeric cast)
        self.cleaned_columns: set[str] = set()

        # === Root Layout ===
        root = QtWidgets.QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(20, 20, 20, 20)

        # === Header ===
        title = QtWidgets.QLabel("🧼 Data Cleaning — Smart Tools for Refining Your Data")
        title.setStyleSheet("font-size:20px; font-weight:bold; color:#facc15;")
        subtitle = QtWidgets.QLabel("Clean, filter, and refine your dataset efficiently.")
        subtitle.setStyleSheet("color:#94a3b8; margin-bottom:8px;")
        root.addWidget(title)
        root.addWidget(subtitle)

        # === Main Grid (left wide, right narrow) ===
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)
        grid.setColumnStretch(0, 7)
        grid.setColumnStretch(1, 3)

        # ---------------- Step 1 — Load CSV (top-left)
        load_group = QtWidgets.QGroupBox("📂 Step 1 — Load Dataset")
        lv = QtWidgets.QHBoxLayout(load_group)
        self.load_btn = QtWidgets.QPushButton("📁 Open CSV")
        self.load_btn.clicked.connect(self.load_csv)
        self.file_lbl = QtWidgets.QLabel("No file loaded.")
        self.file_lbl.setStyleSheet("color:#94a3b8;")
        lv.addWidget(self.load_btn)
        lv.addWidget(self.file_lbl, 1)
        grid.addWidget(load_group, 0, 0)

        # ---------------- Step 3 — Keep / Remove (top-right)
        keep_group = QtWidgets.QGroupBox("✅ Step 3 — Keep / Remove Columns")
        kv = QtWidgets.QVBoxLayout(keep_group)
        self.keep_list = QtWidgets.QListWidget()
        self.keep_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.keep_list.setMinimumHeight(220)
        self.keep_btn = QtWidgets.QPushButton("Apply Selection")
        self.keep_btn.clicked.connect(self.keep_columns)
        kv.addWidget(self.keep_list)
        kv.addWidget(self.keep_btn)
        grid.addWidget(keep_group, 0, 1, 2, 1)

        # ---------------- Step 2 — Preview (large, left)
        preview_group = QtWidgets.QGroupBox("📊 Step 2 — Dataset Preview")
        pv = QtWidgets.QVBoxLayout(preview_group)
        self.table = QtWidgets.QTableWidget()
        self.table.setMinimumHeight(480)
        pv.addWidget(self.table)
        grid.addWidget(preview_group, 1, 0, 3, 1)

        # ---------------- Step 3.2 — Clean Column (right, under Step 3)
        clean_group = QtWidgets.QGroupBox("🧹 Step 3.2 — Clean Columns (Remove ₹ $ % , etc.)")
        cv = QtWidgets.QGridLayout(clean_group)
        cv.addWidget(QtWidgets.QLabel("Column:"), 0, 0)
        self.clean_col = QtWidgets.QComboBox()
        cv.addWidget(self.clean_col, 0, 1)
        cv.addWidget(QtWidgets.QLabel("Extra Chars:"), 1, 0)
        self.extra_chars = QtWidgets.QLineEdit()
        self.extra_chars.setPlaceholderText("e.g. ₹,$,%,.")
        cv.addWidget(self.extra_chars, 1, 1)
        self.clean_btn = QtWidgets.QPushButton("💎 Clean Column")
        self.clean_btn.clicked.connect(self.clean_selected_column)
        cv.addWidget(self.clean_btn, 2, 0, 1, 2)
        grid.addWidget(clean_group, 2, 1)

        # (Helpful note about price columns)
        note_group = QtWidgets.QGroupBox("")  # visual container only
        nv = QtWidgets.QVBoxLayout(note_group)
        note = QtWidgets.QLabel(
            "💡 <b>Price/currency columns</b> often contain ₹/$/%, and commas.\n"
            "Use <b>Step 3.2</b> to clean them first. Auto-filling NAs in 'Price' is blocked until cleaned."
        )
        note.setStyleSheet("color:#94a3b8;")
        note.setWordWrap(True)
        nv.addWidget(note)
        grid.addWidget(note_group, 3, 1)

        # ---------------- Step 4 — Handle Missing Values (right)
        mv_group = QtWidgets.QGroupBox("🔧 Step 4 — Handle Missing Values")
        mv = QtWidgets.QGridLayout(mv_group)
        mv.addWidget(QtWidgets.QLabel("Column:"), 0, 0)
        self.na_col = QtWidgets.QComboBox()
        mv.addWidget(self.na_col, 0, 1)
        mv.addWidget(QtWidgets.QLabel("Method:"), 0, 2)
        self.na_method = QtWidgets.QComboBox()
        self.na_method.addItems(["Mean", "Median", "Zero", "Mode", "Custom Value", "Skip"])
        mv.addWidget(self.na_method, 0, 3)
        mv.addWidget(QtWidgets.QLabel("Custom:"), 1, 0)
        self.na_custom = QtWidgets.QLineEdit()
        mv.addWidget(self.na_custom, 1, 1, 1, 3)
        self.na_apply = QtWidgets.QPushButton("Apply Fill")
        self.na_apply.clicked.connect(self.apply_missing)
        mv.addWidget(self.na_apply, 2, 0, 1, 4)
        grid.addWidget(mv_group, 4, 1)

        # ---------------- Step 5 — Filter (right, bottom)
        filt_group = QtWidgets.QGroupBox("🎯 Step 5 — Conditional Filtering")
        fv = QtWidgets.QGridLayout(filt_group)
        fv.addWidget(QtWidgets.QLabel("Column:"), 0, 0)
        self.filter_col = QtWidgets.QComboBox()
        fv.addWidget(self.filter_col, 0, 1)
        fv.addWidget(QtWidgets.QLabel("Operation:"), 0, 2)
        self.filter_op = QtWidgets.QComboBox()
        self.filter_op.addItems(["<", ">", "<=", ">=", "==", "!="])
        fv.addWidget(self.filter_op, 0, 3)
        fv.addWidget(QtWidgets.QLabel("Value:"), 1, 0)
        self.filter_val = QtWidgets.QLineEdit()
        fv.addWidget(self.filter_val, 1, 1, 1, 3)
        self.filter_btn = QtWidgets.QPushButton("Apply Filter")
        self.filter_btn.clicked.connect(self.apply_filter)
        fv.addWidget(self.filter_btn, 2, 0, 1, 4)
        grid.addWidget(filt_group, 5, 1)

        root.addLayout(grid, 8)

        # ---------------- Footer
        footer = QtWidgets.QHBoxLayout()
        self.stats_lbl = QtWidgets.QLabel("Rows: 0 | Columns: 0")
        self.stats_lbl.setStyleSheet("color:#94a3b8;")
        self.save_btn = QtWidgets.QPushButton("💾 Save Cleaned Dataset")
        self.save_btn.clicked.connect(self.save_cleaned)
        footer.addWidget(self.stats_lbl)
        footer.addStretch(1)
        footer.addWidget(self.save_btn)
        root.addLayout(footer)

    # ===== Utilities =====
    def _refresh_controls(self):
        """Refresh all column pickers from current df."""
        cols = list(map(str, self.df.columns))
        for combo in (self.clean_col, self.na_col, self.filter_col):
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(cols)
            combo.blockSignals(False)
        self.keep_list.clear()
        self.keep_list.addItems(cols)
        self.stats_lbl.setText(f"Rows: {len(self.df)} | Columns: {len(self.df.columns)}")

    # ===== Step 1 — Load CSV =====
    def load_csv(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        self.df = pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip")
        self.cleaned_columns.clear()  # reset cleaned tracker on new load
        self.file_lbl.setText(os.path.basename(path))
        df_to_table(self.df, self.table)
        self._refresh_controls()

    # ===== Step 3 — Keep / Remove Columns =====
    def keep_columns(self):
        selected = [item.text() for item in self.keep_list.selectedItems()]
        if not selected:
            QtWidgets.QMessageBox.information(self, "No Selection", "Please select at least one column to keep.")
            return
        try:
            # Keep order based on selection order in the list
            self.df = self.df[[c for c in selected if c in self.df.columns]]
            # Drop cleaned flags for any columns no longer present
            self.cleaned_columns = {c for c in self.cleaned_columns if c in set(map(str.lower, self.df.columns))}
            df_to_table(self.df, self.table)
            self._refresh_controls()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))

    # ===== Step 3.2 — Clean Selected Column =====
    def clean_selected_column(self):
        col = self.clean_col.currentText()
        if not col:
            return
        extra = [c.strip() for c in self.extra_chars.text().split(",") if c.strip()]
        try:
            s = (
                self.df[col]
                .astype(str)
                .replace(["N/A", "n/a", "NA", "null", "--", "-", ""], pd.NA)
                .str.replace(r"[₹$,%,]", "", regex=True)
                .str.replace(",", "", regex=False)
            )
            for ch in extra:
                s = s.str.replace(ch, "", regex=False)
            # Convert to numeric; non-numeric becomes NaN
            s = pd.to_numeric(s, errors="coerce")
            self.df[col] = s

            # mark as cleaned
            self.cleaned_columns.add(col.strip().lower())

            df_to_table(self.df, self.table)
            QtWidgets.QMessageBox.information(
                self, "Cleaned",
                f"✅ '{col}' cleaned and converted to numeric.\nNow safe to fill missing values."
            )
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))

    # ===== Step 4 — Handle Missing Values =====
    def apply_missing(self):
        col = self.na_col.currentText()
        if not col:
            return

        # Block Price until cleaned (currency columns)
        if col.strip().lower() == "price" and col.strip().lower() not in self.cleaned_columns:
            QtWidgets.QMessageBox.warning(
                self, "Not Allowed",
                "⚠ The 'Price' column appears currency-based and should be cleaned in Step 3.2 first."
            )
            return

        method = self.na_method.currentText()
        try:
            self.df[col] = self.df[col].replace(["N/A", "n/a", "NA", "null", "--", "-", ""], pd.NA)

            if pd.api.types.is_numeric_dtype(self.df[col]):
                if method == "Mean":
                    self.df[col].fillna(self.df[col].mean(), inplace=True)
                elif method == "Median":
                    self.df[col].fillna(self.df[col].median(), inplace=True)
                elif method == "Zero":
                    self.df[col].fillna(0, inplace=True)
            if method == "Mode":
                m = self.df[col].mode(dropna=True)
                if not m.empty:
                    self.df[col].fillna(m.iloc[0], inplace=True)
            elif method == "Custom Value":
                val = self.na_custom.text().strip()
                if val != "":
                    self.df[col].fillna(val, inplace=True)

            df_to_table(self.df, self.table)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))

    # ===== Step 5 — Conditional Filtering =====
    def apply_filter(self):
        col = self.filter_col.currentText()
        op = self.filter_op.currentText()
        val = self.filter_val.text().strip()
        if not col or val == "":
            return
        try:
            v = safe_clean_numeric(val)
            if v is not None:
                # numeric comparison
                if op == "<":
                    mask = self.df[col] < v
                elif op == ">":
                    mask = self.df[col] > v
                elif op == "<=":
                    mask = self.df[col] <= v
                elif op == ">=":
                    mask = self.df[col] >= v
                elif op == "==":
                    mask = self.df[col] == v
                elif op == "!=":
                    mask = self.df[col] != v
            else:
                # string comparison supports only == and !=
                if op == "==":
                    mask = self.df[col].astype(str) == val
                elif op == "!=":
                    mask = self.df[col].astype(str) != val
                else:
                    QtWidgets.QMessageBox.warning(self, "Invalid", "Only == or != for text columns.")
                    return

            self.df = self.df[mask].reset_index(drop=True)
            df_to_table(self.df, self.table)
            self.stats_lbl.setText(f"Rows: {len(self.df)} | Columns: {len(self.df.columns)}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))

    # ===== Save =====
    def save_cleaned(self):
        if self.df.empty:
            QtWidgets.QMessageBox.information(self, "Empty", "No data to save.")
            return
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        outdir = os.path.join(CLEANED_DIR, ts)
        os.makedirs(outdir, exist_ok=True)
        outpath = os.path.join(outdir, "cleaned_dataset.csv")
        self.df.to_csv(outpath, index=False)
        QtWidgets.QMessageBox.information(self, "Saved", f"✅ Saved at:\n{outpath}")


# ======================================================
# DASHBOARD TAB (Visualizations)
# ======================================================
class DashboardTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.df = pd.DataFrame()
        self.current_path = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)

        # Header
        title = QtWidgets.QLabel("📈 Visual Dashboard — Explore Your Data")
        title.setStyleSheet("font-size:18px; font-weight:bold; color:#facc15;")
        layout.addWidget(title)

        # Load dataset section
        load_box = QtWidgets.QGroupBox("📂 Step 1 — Load Dataset")
        lv = QtWidgets.QHBoxLayout(load_box)
        self.load_latest = QtWidgets.QPushButton("📤 Load Latest Cleaned")
        self.pick_cleaned = QtWidgets.QPushButton("📁 Open Cleaned CSV")
        self.file_lbl = QtWidgets.QLabel("No dataset loaded.")
        self.file_lbl.setStyleSheet("color:#94a3b8;")
        lv.addWidget(self.load_latest)
        lv.addWidget(self.pick_cleaned)
        lv.addWidget(self.file_lbl, 1)
        layout.addWidget(load_box)

        self.load_latest.clicked.connect(self.load_latest_cleaned)
        self.pick_cleaned.clicked.connect(self.pick_cleaned_csv)

        # Preview
        preview_box = QtWidgets.QGroupBox("📄 Step 2 — Dataset Preview")
        pv = QtWidgets.QVBoxLayout(preview_box)
        self.table = QtWidgets.QTableWidget()
        pv.addWidget(self.table)
        layout.addWidget(preview_box, 3)

        # Visualization controls
        ctrl_box = QtWidgets.QGroupBox("🎨 Step 3 — Visualization Controls")
        cv = QtWidgets.QGridLayout(ctrl_box)

        self.numeric_lbl = QtWidgets.QLabel("Numeric: []")
        self.categorical_lbl = QtWidgets.QLabel("Categorical: []")
        self.numeric_lbl.setStyleSheet("color:#94a3b8;")
        self.categorical_lbl.setStyleSheet("color:#94a3b8;")

        self.graph_type = QtWidgets.QComboBox()
        self.graph_type.addItems([
            "Bar Chart", "Line Chart", "Scatter Plot",
            "Pie Chart", "Histogram", "Box Plot"
        ])

        self.x_col = QtWidgets.QComboBox()
        self.y_col = QtWidgets.QComboBox()

        self.aggregate_chk = QtWidgets.QCheckBox("Aggregate by X")
        self.agg_func = QtWidgets.QComboBox()
        self.agg_func.addItems(["sum", "mean", "count", "max", "min"])
        self.agg_func.setCurrentText("sum")

        self.plot_btn = QtWidgets.QPushButton("🎯 Generate Visualization")
        self.save_plot_btn = QtWidgets.QPushButton("💾 Save Plot Image")

        # layout grid
        cv.addWidget(self.numeric_lbl, 0, 0, 1, 2)
        cv.addWidget(self.categorical_lbl, 0, 2, 1, 2)

        cv.addWidget(QtWidgets.QLabel("Graph Type:"), 1, 0)
        cv.addWidget(self.graph_type, 1, 1)
        cv.addWidget(QtWidgets.QLabel("X-axis:"), 1, 2)
        cv.addWidget(self.x_col, 1, 3)

        cv.addWidget(QtWidgets.QLabel("Y-axis:"), 2, 0)
        cv.addWidget(self.y_col, 2, 1)
        cv.addWidget(self.aggregate_chk, 2, 2)
        cv.addWidget(self.agg_func, 2, 3)

        cv.addWidget(self.plot_btn, 3, 0, 1, 2)
        cv.addWidget(self.save_plot_btn, 3, 2, 1, 2)

        layout.addWidget(ctrl_box, 1)

        # Chart display area
        chart_box = QtWidgets.QGroupBox("📊 Step 4 — Visualization Output")
        cv2 = QtWidgets.QVBoxLayout(chart_box)
        self.canvas = MplCanvas(width=7, height=4)
        cv2.addWidget(self.canvas)
        layout.addWidget(chart_box, 2)

        # Connections
        self.plot_btn.clicked.connect(self.draw_plot)
        self.save_plot_btn.clicked.connect(self.save_plot)

    # ---------- Data loading ----------
    def load_latest_cleaned(self):
        try:
            folders = sorted(
                [d for d in os.listdir(CLEANED_DIR) if os.path.isdir(os.path.join(CLEANED_DIR, d))]
            )
            if not folders:
                QtWidgets.QMessageBox.information(self, "No Data", "No cleaned datasets found.")
                return
            latest = folders[-1]
            folder_path = os.path.join(CLEANED_DIR, latest)
            csvs = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]
            if not csvs:
                QtWidgets.QMessageBox.information(self, "No CSV", "No CSV in latest cleaned folder.")
                return
            self._load_df(os.path.join(folder_path, csvs[0]))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))

    def pick_cleaned_csv(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Cleaned CSV", CLEANED_DIR, "CSV Files (*.csv)"
        )
        if not path:
            return
        self._load_df(path)

    def _load_df(self, path):
        try:
            df = pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip")
            self.df = df.copy()
            self.current_path = path
            self.file_lbl.setText(f"Loaded: {os.path.basename(path)}")

            df_to_table(self.df, self.table)
            self._refresh_columns()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))

    def _refresh_columns(self):
        num_cols = self.df.select_dtypes(include=["number"]).columns.tolist()
        cat_cols = self.df.select_dtypes(include=["object", "category"]).columns.tolist()
        self.numeric_lbl.setText(f"Numeric: {num_cols}")
        self.categorical_lbl.setText(f"Categorical: {cat_cols}")
        self.x_col.clear()
        self.y_col.clear()
        self.x_col.addItems([str(c) for c in self.df.columns])
        self.y_col.addItems([str(c) for c in num_cols])

    # ---------- Aggregation helper ----------
    def _aggregate_if_needed(self, df, x, y):
        if not self.aggregate_chk.isChecked():
            return df
        func = self.agg_func.currentText()
        try:
            if func == "sum":
                return df.groupby(x, dropna=False)[y].sum().reset_index()
            if func == "mean":
                return df.groupby(x, dropna=False)[y].mean().reset_index()
            if func == "count":
                # count rows per x (y ignored)
                return df.groupby(x, dropna=False).size().reset_index(name="count")
            if func == "max":
                return df.groupby(x, dropna=False)[y].max().reset_index()
            if func == "min":
                return df.groupby(x, dropna=False)[y].min().reset_index()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Aggregation Error", str(e))
        return df

    # ---------- Plotting ----------
    def draw_plot(self):
        if self.df is None or self.df.empty:
            QtWidgets.QMessageBox.information(self, "No data", "Load a dataset first.")
            return

        gtype = self.graph_type.currentText()
        x = self.x_col.currentText()
        y = self.y_col.currentText() if gtype not in ["Pie Chart", "Histogram"] else None

        try:
            self.canvas.ax.clear()
            df = self.df.copy()

            # prepare numeric if needed
            if y and y in df.columns and not pd.api.types.is_numeric_dtype(df[y]):
                # attempt safe numeric conversion (common price-like handling)
                df[y] = df[y].apply(safe_clean_numeric)

            if gtype in ["Bar Chart", "Line Chart", "Scatter Plot", "Box Plot"] and y:
                df = self._aggregate_if_needed(df, x, y)

            if gtype == "Bar Chart":
                self.canvas.ax.bar(df[x], df[y])
                self.canvas.ax.set_ylabel(y)
            elif gtype == "Line Chart":
                self.canvas.ax.plot(df[x], df[y], marker='o')
                self.canvas.ax.set_ylabel(y)
            elif gtype == "Scatter Plot":
                self.canvas.ax.scatter(df[x], df[y], alpha=0.75)
                self.canvas.ax.set_ylabel(y)
            elif gtype == "Pie Chart":
                counts = df[x].value_counts(dropna=False)
                self.canvas.ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
            elif gtype == "Histogram":
                vals = df[x].apply(safe_clean_numeric)
                vals = pd.Series([v for v in vals if v is not None])
                if vals.empty:
                    QtWidgets.QMessageBox.information(self, "Histogram", "Selected X is not numeric-like.")
                    return
                self.canvas.ax.hist(vals.dropna(), bins=20)
                self.canvas.ax.set_xlabel(x)
            elif gtype == "Box Plot":
                if df[x].dtype.kind in "bifc":
                    QtWidgets.QMessageBox.information(self, "Box Plot", "X should be categorical for box plot.")
                    return
                groups = [g[y].dropna().values for _, g in df.groupby(x)]
                self.canvas.ax.boxplot(groups, labels=list(df.groupby(x).groups.keys()))
                self.canvas.ax.set_ylabel(y)

            self.canvas.ax.set_title(f"{gtype}: {((y + ' vs ') if y else '')}{x}")
            self.canvas.ax.set_xlabel(x)
            self.canvas.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Plot Error", str(e))

    # ---------- Save Plot ----------
    def save_plot(self):
        if self.df is None or self.df.empty:
            return
        default_dir = CLEANED_DIR
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Plot Image", os.path.join(default_dir, "visual.png"), "PNG Image (*.png)"
        )
        if not path:
            return
        try:
            self.canvas.figure.savefig(path, bbox_inches="tight")
            QtWidgets.QMessageBox.information(self, "Saved", f"Plot saved:\n{path}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Save Error", str(e))


# ======================================================
# MAIN WINDOW (Tabs)
# ======================================================
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Transformation Pipeline (Desktop)")
        self.resize(1200, 800)

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(ComposerTab(), "🧱 Dataset Composer")  # from Part 2
        tabs.addTab(CleaningTab(), "🧼 Data Cleaning")     # from Part 3
        tabs.addTab(DashboardTab(), "📈 Visual Dashboard")

        self.setCentralWidget(tabs)


# ======================================================
# APP ENTRYPOINT
# ======================================================
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # If you defined a theme helper earlier, call it here; otherwise comment out:
    # apply_streamlit_theme(app)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
