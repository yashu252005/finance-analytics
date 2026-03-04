import logging
import os
import shutil

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_pipeline(input_path: str, column_map: dict = None):
    """
    Run the full finance analytics pipeline on any uploaded file.

    Args:
        input_path  : path to the uploaded CSV or Excel file
        column_map  : dict with keys date_col, desc_col, amount_col,
                      type_col, debit_col, credit_col  (all optional except date+desc)
    """

    logger.info("=" * 60)
    logger.info(f"Pipeline started for: {input_path}")
    logger.info("=" * 60)

    # ── 0. Clear previous output FILES (avoid Windows folder-lock errors) ──────
    logger.info("Step 0/5 -- Clearing previous outputs...")
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
        except Exception as e:
            logger.warning(f"Could not delete {f_path}: {e}")
    for folder in ["data/processed", "data/raw", "models", "reports", "logs"]:
        os.makedirs(folder, exist_ok=True)
    logger.info("All previous outputs cleared.")

    # ── 1. Parse & Clean ───────────────────────────────────────────────────────
    logger.info("Step 1/5 -- Cleaning data...")
    from src.parser import clean_data
    clean_data(
        input_path=input_path,
        output_path="data/processed/cleaned_transactions.csv",
        column_map=column_map
    )
    logger.info("Step 1 complete.")

    # ── 2. Rule-Based Categorization ──────────────────────────────────────────
    logger.info("Step 2/5 -- Rule-based categorization...")
    from src.rule_engine import rule_based_categorization
    rule_based_categorization(
        input_path="data/processed/cleaned_transactions.csv",
        output_path="data/processed/rule_labeled.csv"
    )
    logger.info("Step 2 complete.")

    # ── 3. Train ML Model ─────────────────────────────────────────────────────
    logger.info("Step 3/5 -- Training ML model on uploaded dataset...")
    from src.ml_model import train_ml_model
    train_ml_model(
        input_path="data/processed/rule_labeled.csv",
        model_path="models/model.pkl"
    )
    logger.info("Step 3 complete.")

    # ── 4. Hybrid Categorization ──────────────────────────────────────────────
    logger.info("Step 4/5 -- Hybrid categorization...")
    from src.hybrid_model import apply_hybrid_model
    apply_hybrid_model(
        input_path="data/processed/rule_labeled.csv",
        model_path="models/model.pkl",
        output_path="data/processed/final_categorized.csv"
    )
    logger.info("Step 4 complete.")

    # ── 5. Generate Insights ──────────────────────────────────────────────────
    logger.info("Step 5/5 -- Generating insights...")
    from src.insights import generate_insights
    generate_insights("data/processed/final_categorized.csv")
    logger.info("Step 5 complete.")

    logger.info("=" * 60)
    logger.info("Pipeline completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    # For running pipeline directly from command line
    run_pipeline("data/raw/transaction.csv")