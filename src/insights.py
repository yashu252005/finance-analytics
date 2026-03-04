import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import logging

logger = logging.getLogger(__name__)

# Fixed dimensions for ALL charts — same width, same height, same dpi
CHART_W  = 6      # inches
CHART_H  = 4      # inches
CHART_DPI = 120
COLORS = ["#00b496", "#e76f51", "#457b9d", "#f4a261", "#0d234a", "#2d6a4f", "#1a3a6b"]


def save_fig(fig, path):
    """Save figure at exact fixed size — no bbox_inches=tight which changes dimensions."""
    fig.set_size_inches(CHART_W, CHART_H)
    fig.savefig(path, dpi=CHART_DPI, format="png")
    plt.close("all")


def generate_insights(input_path):
    df = pd.read_csv(input_path)
    df["Date"]  = pd.to_datetime(df["Date"], errors="coerce")
    df["Month"] = df["Date"].dt.to_period("M")

    expenses = df[df["Type"] == "Debit"]
    os.makedirs("reports", exist_ok=True)

    category_summary = expenses.groupby("Final_Category")["Amount"].sum().abs()
    monthly_summary  = expenses.groupby("Month")["Amount"].sum().abs()

    category_summary.to_csv("reports/category_summary.csv")
    monthly_summary.to_csv("reports/monthly_summary.csv")
    logger.info("CSV summaries saved.")

    # ── Pie Chart ──────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(CHART_W, CHART_H))
    ax.pie(
        category_summary.values,
        labels=category_summary.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=COLORS[:len(category_summary)],
        textprops={"fontsize": 9},      # smaller labels so they fit inside the fixed size
        pctdistance=0.75,
        labeldistance=1.05,
    )
    ax.set_title("Spending by Category", fontsize=11, fontweight="bold", pad=8)
    save_fig(fig, "reports/pie_chart.png")
    logger.info(f"Pie chart saved: {os.path.getsize('reports/pie_chart.png')} bytes")

    # ── Bar Chart ──────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(CHART_W, CHART_H))
    x = range(len(monthly_summary))
    ax.bar(x, monthly_summary.values, color="#00b496", edgecolor="white", width=0.7)
    ax.set_xticks(list(x))
    ax.set_xticklabels([str(m) for m in monthly_summary.index], rotation=45, ha="right", fontsize=7)
    ax.set_title("Monthly Expenses", fontsize=11, fontweight="bold")
    ax.set_xlabel("Month", fontsize=9)
    ax.set_ylabel("Total Expense", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    save_fig(fig, "reports/monthly_bar_chart.png")

    # ── Line Chart ─────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(CHART_W, CHART_H))
    ax.plot(range(len(monthly_summary)), monthly_summary.values,
            color="#00b496", linewidth=2, marker="o", markersize=4)
    ax.set_xticks(range(len(monthly_summary)))
    ax.set_xticklabels([str(m) for m in monthly_summary.index], rotation=45, ha="right", fontsize=7)
    ax.set_title("Monthly Spending Trend", fontsize=11, fontweight="bold")
    ax.set_xlabel("Month", fontsize=9)
    ax.set_ylabel("Total Expense", fontsize=9)
    ax.grid(linestyle="--", alpha=0.4)
    fig.tight_layout()
    save_fig(fig, "reports/spending_trend.png")

    logger.info("All visualizations saved.")


if __name__ == "__main__":
    generate_insights("data/processed/final_categorized.csv")