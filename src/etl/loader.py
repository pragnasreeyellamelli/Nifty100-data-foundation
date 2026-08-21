import pandas as pd

from pathlib import Path

from .normaliser import normalize_ticker, normalize_year
def load_excel(file_path):
    """Load an Excel file into a pandas DataFrame."""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return pd.read_excel(file_path, header=1)
def normalize_dataframe(df):
    """Normalize ticker and year columns when they are present."""
    df = df.copy()

    for column in df.columns:
        column_name = str(column).strip().lower()

        if column_name in {"ticker", "company_id"}:
            df[column] = df[column].apply(normalize_ticker)

        elif column_name in {"year", "financial_year", "fy"}:
            df[column] = df[column].apply(normalize_year)

    return df
def load_and_normalize(file_path):
    """Load an Excel file and normalize its data."""
    df = load_excel(file_path)
    return normalize_dataframe(df)