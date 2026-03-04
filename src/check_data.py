import pandas as pd

df = pd.read_csv("data/raw/transaction.csv")

print("Columns:", df.columns)
print("Number of rows:", len(df))
print(df.head())