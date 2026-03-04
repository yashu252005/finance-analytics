import streamlit as st
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")

st.set_page_config(
    page_title="Personal Finance Analytics",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp, .main, section[data-testid="stMain"], .block-container {
        background-color: #0d234a !important;
    }
    section[data-testid="stSidebar"] { background-color: #07152e !important; }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    .stApp p, .stApp span, .stApp label, .stApp div, .stApp li { color: #e2e8f0 !important; }
    h1, h2, h3 { color: #ffffff !important; }
    .section-header {
        font-size: 20px; font-weight: 700; color: #00b496 !important;
        margin: 24px 0 12px 0; padding-bottom: 6px; border-bottom: 2px solid #00b496;
    }
    div[data-testid="stInfo"] { background-color: #1a3a6b !important; border: 1px solid #00b496 !important; border-radius: 10px !important; }
    div[data-testid="stInfo"] p { color: #ffffff !important; }
    div[data-testid="stMetric"] { background: #1a3a6b !important; border-radius: 10px !important; padding: 16px !important; border-left: 4px solid #00b496 !important; }
    div[data-testid="stMetric"] label { color: #94a3b8 !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #ffffff !important; }
    .stButton > button { background-color: #00b496 !important; color: #ffffff !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 16px !important; border: none !important; padding: 10px 28px !important; }
    .stButton > button:hover { background-color: #009b80 !important; }
    div[data-testid="stFileUploader"] { background: #1a3a6b !important; border-radius: 10px !important; padding: 10px !important; }
    hr { border-color: #1a3a6b !important; }
    div[data-testid="stDownloadButton"] button { background-color: #1a3a6b !important; color: #ffffff !important; border: 1px solid #00b496 !important; border-radius: 8px !important; font-weight: 600 !important; }
    div[data-testid="stDownloadButton"] button:hover { background-color: #00b496 !important; }
    div[data-testid="stExpander"] { background-color: #1a3a6b !important; border-radius: 10px !important; border: 1px solid #2d4a7a !important; }
    div[data-testid="stAlert"] p, div[data-testid="stWarning"] p { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

NONE_OPTION = "— Not in my file —"

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💰 Finance Analytics")
    st.markdown("*Personal Transaction Analyzer*")
    st.divider()
    st.markdown("**📂 Upload Transaction File**")
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed"
    )
    st.divider()
    st.markdown("**ℹ️ How to Use**")
    st.markdown("""
1. Upload any bank CSV or Excel file
2. Map your columns to the right fields
3. Click **Run Analytics**
4. Explore insights & download reports
    """)

# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown("# 💰 Personal Finance Analytics Platform")
st.markdown("*Automated transaction categorization and spending insights powered by ML*")
st.divider()

if uploaded_file is None:
    col1, col2, col3 = st.columns(3)
    with col1: st.info("**📤 Step 1**\n\nUpload any bank CSV or Excel file using the sidebar")
    with col2: st.info("**🗂️ Step 2**\n\nMap your columns: Date, Description, Amount")
    with col3: st.info("**📊 Step 3**\n\nGet instant insights and download your report")

else:
    # ── Load uploaded file into memory ─────────────────────────────────────────
    try:
        if uploaded_file.name.endswith((".xlsx", ".xls")):
            raw_df = pd.read_excel(uploaded_file)
        else:
            try:
                raw_df = pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                raw_df = pd.read_csv(uploaded_file, encoding="latin1")
    except Exception as e:
        st.error(f"❌ Could not read file: {e}")
        st.stop()

    st.success(f"✅ File loaded: **{uploaded_file.name}** — {len(raw_df):,} rows, {len(raw_df.columns)} columns")

    with st.expander("👁️ Preview Uploaded File", expanded=True):
        st.dataframe(raw_df.head(10), width='stretch')
        st.caption(f"Columns detected: {list(raw_df.columns)}")

    st.divider()

    # ── Column Mapping UI ──────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🗂️ Map Your Columns</div>', unsafe_allow_html=True)
    st.markdown("The system has auto-detected your columns. Adjust if anything looks wrong:")

    all_cols = [NONE_OPTION] + list(raw_df.columns)

    def best_guess(candidates):
        for c in candidates:
            for col in raw_df.columns:
                if c.lower() in col.lower():
                    return col
        return NONE_OPTION

    col1, col2, col3 = st.columns(3)
    with col1:
        date_col = st.selectbox("📅 Date column *",
            all_cols,
            index=all_cols.index(best_guess(["date","timestamp","txn date","value date","transaction date"])))
        amount_col = st.selectbox("💰 Amount column",
            all_cols,
            index=all_cols.index(best_guess(["amount","inr","value","sum"])))
    with col2:
        desc_col = st.selectbox("📝 Description / Category column *",
            all_cols,
            index=all_cols.index(best_guess(["description","narration","merchant","category","details","particulars"])))
        debit_col = st.selectbox("💸 Debit column (if no Amount)",
            all_cols,
            index=all_cols.index(best_guess(["debit","withdrawal","dr"])))
    with col3:
        type_col = st.selectbox("🔄 Transaction Type column (optional)",
            all_cols,
            index=all_cols.index(best_guess(["type","transaction type","txn type","dr/cr"])))
        credit_col = st.selectbox("💵 Credit column (if no Amount)",
            all_cols,
            index=all_cols.index(best_guess(["credit","deposit","cr"])))

    st.caption("* Required fields")

    # Validate
    errors = []
    if date_col  == NONE_OPTION: errors.append("📅 Date column is required")
    if desc_col  == NONE_OPTION: errors.append("📝 Description column is required")
    if amount_col == NONE_OPTION and debit_col == NONE_OPTION and credit_col == NONE_OPTION:
        errors.append("💰 At least one of: Amount / Debit / Credit column is required")
    if errors:
        for e in errors: st.warning(e)
        st.stop()

    column_map = {
        "date_col":   date_col,
        "desc_col":   desc_col,
        "amount_col": amount_col  if amount_col  != NONE_OPTION else None,
        "type_col":   type_col    if type_col    != NONE_OPTION else None,
        "debit_col":  debit_col   if debit_col   != NONE_OPTION else None,
        "credit_col": credit_col  if credit_col  != NONE_OPTION else None,
    }

    st.divider()

    # ── Run Button ─────────────────────────────────────────────────────────────
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        run_clicked = st.button("🚀 Run Analytics", width='stretch')

    if run_clicked:
        progress = st.progress(0, text="Initializing...")
        status   = st.empty()

        try:
            import shutil, tempfile

            os.makedirs("data/raw", exist_ok=True)
            os.makedirs("logs", exist_ok=True)

            # Save the uploaded file to disk with correct extension
            ext = os.path.splitext(uploaded_file.name)[1]
            raw_path = f"data/raw/uploaded{ext}"

            # Remove old file if exists
            if os.path.exists(raw_path):
                os.remove(raw_path)

            uploaded_file.seek(0)
            with open(raw_path, "wb") as f:
                f.write(uploaded_file.read())

            progress.progress(5, text="File saved...")

            # Run full pipeline
            from src.main import run_pipeline
            
            # We call each step individually so we can update the progress bar
            import shutil as sh

            # Step 0 — Clear old output FILES (not folders — avoids Windows permission errors)
            status.info("🗑️ Clearing previous outputs...")
            old_files = [
                "data/processed/cleaned_transactions.csv",
                "data/processed/rule_labeled.csv",
                "data/processed/final_categorized.csv",
                "models/model.pkl",
                "reports/pie_chart.png",
                "reports/monthly_bar_chart.png",
                "reports/spending_trend.png",
                "reports/category_summary.csv",
                "reports/monthly_summary.csv",
            ]
            for f_path in old_files:
                try:
                    if os.path.exists(f_path):
                        os.remove(f_path)
                except Exception:
                    pass  # Skip locked files — they will be overwritten anyway
            for folder in ["data/processed", "data/raw", "models", "reports", "logs"]:
                os.makedirs(folder, exist_ok=True)
            progress.progress(10, text="Previous outputs cleared...")

            # Step 1 — Clean
            status.info("⚙️ Step 1/5 — Cleaning & standardizing your data...")
            from src.parser import clean_data
            clean_data(raw_path, "data/processed/cleaned_transactions.csv", column_map)
            progress.progress(25, text="Data cleaned...")

            # Step 2 — Rule engine
            status.info("🏷️ Step 2/5 — Applying rule-based categorization...")
            from src.rule_engine import rule_based_categorization
            rule_based_categorization("data/processed/cleaned_transactions.csv", "data/processed/rule_labeled.csv")
            progress.progress(45, text="Rules applied...")

            # Step 3 — Train ML
            status.info("🤖 Step 3/5 — Training ML model on your dataset...")
            from src.ml_model import train_ml_model
            train_ml_model("data/processed/rule_labeled.csv", "models/model.pkl")
            progress.progress(65, text="ML model trained...")

            # Step 4 — Hybrid
            status.info("🔀 Step 4/5 — Applying hybrid categorization...")
            from src.hybrid_model import apply_hybrid_model
            apply_hybrid_model("data/processed/rule_labeled.csv", "models/model.pkl", "data/processed/final_categorized.csv")
            progress.progress(80, text="Categorization complete...")

            # Step 5 — Insights
            status.info("📊 Step 5/5 — Generating charts and insights...")
            from src.insights import generate_insights
            generate_insights("data/processed/final_categorized.csv")
            progress.progress(100, text="Done!")

            status.empty()
            st.success(f"🎉 Analysis complete for **{uploaded_file.name}**!")
            st.rerun()

        except Exception as e:
            status.empty()
            progress.empty()
            st.error(f"❌ Pipeline failed: {e}")
            import traceback
            st.code(traceback.format_exc())
            st.stop()

    # ── Results Dashboard ──────────────────────────────────────────────────────
    if os.path.exists("data/processed/final_categorized.csv"):
        df = pd.read_csv("data/processed/final_categorized.csv")
        df["Date"]  = pd.to_datetime(df["Date"], errors="coerce")
        df["Month"] = df["Date"].dt.to_period("M").astype(str)

        expenses = df[df["Type"] == "Debit"].copy()
        income   = df[df["Type"] == "Credit"].copy()
        total_income  = income["Amount"].sum()
        total_expense = expenses["Amount"].abs().sum()
        savings       = total_income - total_expense

        # KPIs
        st.markdown('<div class="section-header">💼 Financial Summary</div>', unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("💰 Total Income",   f"Rs.{total_income:,.0f}")
        k2.metric("💸 Total Expenses", f"Rs.{total_expense:,.0f}")
        k3.metric("📈 Net Savings",    f"Rs.{savings:,.0f}")
        k4.metric("🔢 Transactions",   f"{len(df):,}")

        st.divider()

        # Charts
        st.markdown('<div class="section-header">📊 Spending Visualizations</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Spending by Category**")
            if os.path.exists("reports/pie_chart.png"):
                st.image(open("reports/pie_chart.png","rb").read(), width='stretch')
        with c2:
            st.markdown("**Monthly Expenses**")
            if os.path.exists("reports/monthly_bar_chart.png"):
                st.image(open("reports/monthly_bar_chart.png","rb").read(), width='stretch')
        with c3:
            st.markdown("**Spending Trend**")
            if os.path.exists("reports/spending_trend.png"):
                st.image(open("reports/spending_trend.png","rb").read(), width='stretch')

        st.divider()

        # Category Breakdown
        st.markdown('<div class="section-header">🏷️ Category Breakdown</div>', unsafe_allow_html=True)
        cat_summary = (
            expenses.groupby("Final_Category")["Amount"]
            .agg(["sum","count"]).abs()
            .rename(columns={"sum":"Total Spent (Rs.)","count":"Transactions"})
            .sort_values("Total Spent (Rs.)", ascending=False)
            .reset_index().rename(columns={"Final_Category":"Category"})
        )
        cat_summary["Total Spent (Rs.)"] = cat_summary["Total Spent (Rs.)"].map("Rs.{:,.2f}".format)
        st.dataframe(cat_summary, width='stretch', hide_index=True)

        st.divider()

        # Transaction Explorer
        st.markdown('<div class="section-header">🔍 Transaction Explorer</div>', unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        with f1:
            cats = ["All"] + sorted(df["Final_Category"].dropna().unique().tolist())
            sel_cat = st.selectbox("Filter by Category", cats)
        with f2:
            sel_type = st.selectbox("Filter by Type", ["All","Debit","Credit"])
        with f3:
            months = ["All"] + sorted(df["Month"].dropna().unique().tolist())
            sel_month = st.selectbox("Filter by Month", months)

        filtered = df.copy()
        if sel_cat   != "All": filtered = filtered[filtered["Final_Category"] == sel_cat]
        if sel_type  != "All": filtered = filtered[filtered["Type"] == sel_type]
        if sel_month != "All": filtered = filtered[filtered["Month"] == sel_month]

        show_cols = [c for c in ["Date","Description","Amount","Type","Final_Category"] if c in filtered.columns]
        st.dataframe(filtered[show_cols].sort_values("Date", ascending=False).head(500), width='stretch', hide_index=True)
        st.caption(f"Showing {min(500, len(filtered)):,} of {len(filtered):,} transactions")

        st.divider()

        # Downloads
        st.markdown('<div class="section-header">📥 Download Reports</div>', unsafe_allow_html=True)
        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button("📄 Categorized Transactions",
                data=open("data/processed/final_categorized.csv","rb").read(),
                file_name="categorized_transactions.csv", mime="text/csv", width='stretch')
        with d2:
            if os.path.exists("reports/category_summary.csv"):
                st.download_button("📊 Category Summary",
                    data=open("reports/category_summary.csv","rb").read(),
                    file_name="category_summary.csv", mime="text/csv", width='stretch')
        with d3:
            if os.path.exists("reports/monthly_summary.csv"):
                st.download_button("📅 Monthly Summary",
                    data=open("reports/monthly_summary.csv","rb").read(),
                    file_name="monthly_summary.csv", mime="text/csv", width='stretch')