💰 Personal Finance Analytics Platform
Show Image

Automated bank transaction categorization and spending insights powered by Machine Learning


🚀 Live Demo
👉 Open App

📌 Overview
Upload any bank transaction CSV or Excel file and instantly get:

Automatic expense categorization using a Hybrid Rule-Based + ML Model
Spending distribution, monthly trends, and visual reports
Filterable transaction explorer
Downloadable categorized CSV reports


🧠 How It Works
Upload CSV/Excel
      ↓
Step 1 — Data Cleaning & Standardization (parser.py)
      ↓
Step 2 — Rule-Based Categorization (rule_engine.py)
      ↓
Step 3 — TF-IDF + Logistic Regression ML Model (ml_model.py)
      ↓
Step 4 — Hybrid Categorization (hybrid_model.py)
      ↓
Step 5 — Insights & Visualizations (insights.py)

🛠️ Tech Stack
LayerTechnologyFrontendStreamlitData ProcessingPandasMachine LearningScikit-learn (TF-IDF + Logistic Regression)VisualizationMatplotlibFile SupportCSV, Excel (.xlsx/.xls)

📂 Project Structure
finance_analytics/
│
├── app.py                  # Streamlit dashboard
├── requirements.txt        # Dependencies
│
├── src/
│   ├── parser.py           # Data cleaning
│   ├── rule_engine.py      # Keyword categorization
│   ├── ml_model.py         # ML training
│   ├── hybrid_model.py     # Hybrid classification
│   ├── insights.py         # Charts & reports
│   └── main.py             # Pipeline controller
│
├── data/                   # Auto-created on upload
├── models/                 # Auto-created on training
├── reports/                # Auto-created on analysis
└── logs/                   # Pipeline logs

▶️ Run Locally
bash# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/finance-analytics.git
cd finance-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py

📊 Supported File Formats
FormatColumns NeededCSVDate, Description/Category, Amount or Debit/CreditExcel (.xlsx)Same as aboveAny bank formatUse the column mapping UI to match your columns

✅ Features

🔄 Works with any bank statement format
🗂️ Column mapping UI — map your columns visually
🤖 ML retrained on every new upload
📊 3 visualizations: pie chart, bar chart, trend line
🔍 Transaction explorer with category/month filters
📥 Download categorized CSV, category summary, monthly summary


👩‍💻 Developed By
Yashaswini S & Rakshitha F — Internship Project 2024–2025