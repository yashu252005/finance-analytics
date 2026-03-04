import pandas as pd
import joblib
import logging

logger = logging.getLogger(__name__)


def apply_hybrid_model(input_path, model_path, output_path):
    df = pd.read_csv(input_path)
    model = joblib.load(model_path)

    # Fix: fill any NaN descriptions before predicting
    df["Description"] = df["Description"].fillna("unknown").astype(str)

    mask = df["Rule_Category"] == "Uncategorized"

    if mask.sum() > 0:
        logger.info(f"Predicting {mask.sum()} uncategorized transactions using ML model...")
        predictions = model.predict(df.loc[mask, "Description"])
        df.loc[mask, "Final_Category"] = predictions
    else:
        logger.info("No uncategorized transactions found.")

    df.loc[~mask, "Final_Category"] = df.loc[~mask, "Rule_Category"]

    df.to_csv(output_path, index=False)
    logger.info("Hybrid categorization complete.")
    logger.info(f"\n{df['Final_Category'].value_counts().to_string()}")


if __name__ == "__main__":
    apply_hybrid_model(
        "data/processed/rule_labeled.csv",
        "models/model.pkl",
        "data/processed/final_categorized.csv"
    )