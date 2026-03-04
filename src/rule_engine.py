import logging
import pandas as pd

logger = logging.getLogger(__name__)

# Keyword dictionary for categorization
CATEGORY_KEYWORDS = {
    "Food": ["zomato", "swiggy", "restaurant", "cafe", "food"],
    "Shopping": ["amazon", "flipkart", "myntra", "ajio", "shopping"],
    "Groceries": ["dmart", "bigbasket", "grocery", "supermarket"],
    "Transport": ["uber", "ola", "petrol", "fuel", "metro", "rapido", "cab"],
    "Bills": ["electricity", "water", "recharge", "bill", "broadband", "internet", "gas"],
    "Entertainment": ["netflix", "spotify", "movie", "prime", "hotstar", "youtube"],
    "Income": ["salary", "bonus", "credit interest", "neft", "imps"],
    "Rent": ["rent", "landlord", "house"],
    "Healthcare": ["pharmacy", "hospital", "clinic", "medicine", "apollo", "medplus"],
    "Education": ["college", "course", "udemy", "fee", "tuition"],
}


def categorize_transaction(description):
    description = str(description).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description:
                return category
    return "Uncategorized"


def rule_based_categorization(input_path, output_path):
    df = pd.read_csv(input_path)
    df["Rule_Category"] = df["Description"].apply(categorize_transaction)
    df.to_csv(output_path, index=False)

    counts = df["Rule_Category"].value_counts()
    uncategorized = counts.get("Uncategorized", 0)
    total = len(df)

    logger.info(f"Rule-based categorization complete. {total - uncategorized}/{total} transactions categorized.")
    logger.info(f"Category breakdown:\n{counts.to_string()}")

    return df


if __name__ == "__main__":
    rule_based_categorization(
        "data/processed/cleaned_transactions.csv",
        "data/processed/rule_labeled.csv"
    )
