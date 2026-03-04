import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import joblib
import logging

logger = logging.getLogger(__name__)


def train_ml_model(input_path, model_path):
    df = pd.read_csv(input_path)

    # Fix NaN descriptions
    df["Description"] = df["Description"].fillna("unknown").astype(str)

    # Only train on categorized rows
    df = df[df["Rule_Category"] != "Uncategorized"]

    if len(df) < 10:
        raise ValueError(
            f"Not enough categorized data to train ML model (only {len(df)} rows). "
            "Add more keyword rules in rule_engine.py for this dataset."
        )

    X = df["Description"]
    y = df["Rule_Category"]

    # If only one class, skip split
    if y.nunique() < 2:
        logger.warning("Only one category found — skipping train/test split.")
        model = Pipeline([
            ("tfidf", TfidfVectorizer()),
            ("classifier", LogisticRegression(max_iter=1000))
        ])
        model.fit(X, y)
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        model = Pipeline([
            ("tfidf", TfidfVectorizer()),
            ("classifier", LogisticRegression(max_iter=1000))
        ])
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        logger.info(f"Model Accuracy: {accuracy_score(y_test, y_pred):.2f}")
        logger.info(f"\n{classification_report(y_test, y_pred)}")

    joblib.dump(model, model_path)
    logger.info(f"Model saved to {model_path}")


if __name__ == "__main__":
    train_ml_model("data/processed/rule_labeled.csv", "models/model.pkl")