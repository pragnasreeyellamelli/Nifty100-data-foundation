import pandas as pd
import sqlite3

from pathlib import Path

from .normaliser import normalize_ticker, normalize_year


def load_excel(file_path):
    """Load an Excel file into a pandas DataFrame."""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # The first row contains the actual column headers.
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


def save_to_sqlite(df, db_path, table_name):
    """Save matching DataFrame columns into an existing SQLite table."""
    conn = sqlite3.connect(db_path)

    try:
        # Get the existing SQLite table columns.
        table_info = pd.read_sql_query(
            f"PRAGMA table_info({table_name})",
            conn
        )

        sqlite_columns = table_info["name"].tolist()

        # Keep only columns that actually exist in SQLite.
        matching_columns = [
            column for column in df.columns
            if column in sqlite_columns
        ]

        if not matching_columns:
            raise ValueError(
                f"No matching columns found between DataFrame and "
                f"SQLite table '{table_name}'."
            )

        df_to_save = df[matching_columns].copy()

        df_to_save.to_sql(
            table_name,
            conn,
            if_exists="append",
            index=False
        )

    finally:
        conn.close()