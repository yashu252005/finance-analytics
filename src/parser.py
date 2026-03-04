import logging
import pandas as pd
import os

logger = logging.getLogger(__name__)


def find_column(df, candidates):
    """Case-insensitive column finder."""
    cols_lower = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in cols_lower:
            return cols_lower[candidate.lower()]
    return None


def load_file(input_path: str) -> pd.DataFrame:
    """Load CSV or Excel file automatically."""
    ext = os.path.splitext(input_path)[1].lower()
    if ext in [".xlsx", ".xls"]:
        df = pd.read_excel(input_path)
        logger.info(f"Loaded Excel file: {input_path} ({len(df)} rows)")
    else:
        try:
            df = pd.read_csv(input_path)
        except UnicodeDecodeError:
            df = pd.read_csv(input_path, encoding="latin1")
        logger.info(f"Loaded CSV file: {input_path} ({len(df)} rows)")
    return df


def clean_data(input_path: str, output_path: str, column_map: dict = None):
    """
    Clean and standardize any uploaded transaction file.

    column_map keys (all optional — auto-detected if not provided):
        date_col, desc_col, amount_col, type_col, debit_col, credit_col
    """
    df = load_file(input_path)
    logger.info(f"Columns found: {list(df.columns)}")

    # Remove fully empty rows
    df.dropna(how="all", inplace=True)

    cm = column_map or {}

    # ── Resolve columns ────────────────────────────────────────────────────────
    NONE = "— Not in my file —"

    def resolve(key, candidates):
        val = cm.get(key)
        if val and val != NONE:
            return val
        return find_column(df, candidates)

    date_col   = resolve("date_col",   ["date", "timestamp", "txn date", "value date", "transaction date"])
    desc_col   = resolve("desc_col",   ["description", "narration", "merchant_category", "merchant category",
                                         "details", "particulars", "remarks", "category"])
    amount_col = resolve("amount_col", ["amount", "amount (inr)", "amount(inr)", "transaction amount", "value"])
    type_col   = resolve("type_col",   ["type", "transaction type", "txn type", "dr/cr"])
    debit_col  = resolve("debit_col",  ["debit", "withdrawal", "dr", "debit (rs)", "debit (inr)"])
    credit_col = resolve("credit_col", ["credit", "deposit", "cr", "credit (rs)", "credit (inr)"])

    if not date_col:
        raise ValueError(f"Could not find a Date column. Columns available: {list(df.columns)}")
    if not desc_col:
        raise ValueError(f"Could not find a Description/Category column. Columns available: {list(df.columns)}")
    if not amount_col and not debit_col and not credit_col:
        raise ValueError(f"Could not find an Amount column. Columns available: {list(df.columns)}")

    logger.info(f"Using -> Date: '{date_col}' | Desc: '{desc_col}' | "
                f"Amount: '{amount_col}' | Type: '{type_col}' | "
                f"Debit: '{debit_col}' | Credit: '{credit_col}'")

    # ── Build Description ──────────────────────────────────────────────────────
    if type_col and type_col != desc_col:
        df["Description"] = df[type_col].astype(str) + " - " + df[desc_col].astype(str)
    else:
        df["Description"] = df[desc_col].astype(str)

    # ── Build Amount ───────────────────────────────────────────────────────────
    def to_numeric(series):
        return pd.to_numeric(
            series.astype(str).str.replace(",", "", regex=False).str.strip(),
            errors="coerce"
        )

    if amount_col:
        df["Amount"] = to_numeric(df[amount_col])
        # Use type column to determine sign
        if type_col:
            type_s = df[type_col].astype(str).str.lower()
            debit_mask = type_s.str.contains("debit|withdrawal|payment|sent|dr|p2m|p2p", na=False)
            df.loc[debit_mask,  "Amount"] = -df.loc[debit_mask,  "Amount"].abs()
            df.loc[~debit_mask, "Amount"] =  df.loc[~debit_mask, "Amount"].abs()
    elif debit_col or credit_col:
        dvals = to_numeric(df[debit_col]).fillna(0)  if debit_col  else 0
        cvals = to_numeric(df[credit_col]).fillna(0) if credit_col else 0
        df["Amount"] = cvals - dvals
    else:
        raise ValueError("No amount data found.")

    # ── Build Type ─────────────────────────────────────────────────────────────
    df["Type"] = df["Amount"].apply(lambda x: "Credit" if x > 0 else "Debit")

    # ── Parse Date ─────────────────────────────────────────────────────────────
    df["Date"] = pd.to_datetime(df[date_col], errors="coerce")

    # ── Drop invalid rows ──────────────────────────────────────────────────────
    before = len(df)
    df = df[df["Description"].notna() & df["Amount"].notna() & df["Date"].notna()]
    dropped = before - len(df)
    if dropped:
        logger.warning(f"Dropped {dropped} rows with missing Date/Description/Amount.")

    # ── Keep standard columns only ─────────────────────────────────────────────
    df = df[["Date", "Description", "Amount", "Type"]].reset_index(drop=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Cleaned data saved: {output_path} ({len(df)} rows)")
    return df


if __name__ == "__main__":
    clean_data("data/raw/transaction.csv", "data/processed/cleaned_transactions.csv")






























