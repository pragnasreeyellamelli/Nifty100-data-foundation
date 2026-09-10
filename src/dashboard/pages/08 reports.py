import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


st.title("📄 Annual Reports")
st.caption(
    "Find available annual report years and BSE links"
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DB_PATH = PROJECT_ROOT / "nifty100.db"


# ============================================================
# DATABASE HELPER
# ============================================================

def read_table(
    table_name,
):

    try:

        with sqlite3.connect(
            DB_PATH
        ) as conn:

            return pd.read_sql_query(
                f"SELECT * FROM {table_name}",
                conn,
            )

    except Exception:
        return pd.DataFrame()


# ============================================================
# LOAD DOCUMENT DATA
# ============================================================

documents = read_table(
    "documents"
)


if documents.empty:

    st.info(
        "Annual report data is not currently available."
    )

    st.stop()


# ============================================================
# IDENTIFY COLUMNS
# ============================================================

company_column = None

for column in [
    "company_id",
    "ticker",
    "symbol",
]:
    if column in documents.columns:
        company_column = column
        break


name_column = None

for column in [
    "company_name",
    "name",
]:
    if column in documents.columns:
        name_column = column
        break


year_column = None

for column in [
    "year",
    "report_year",
    "financial_year",
]:
    if column in documents.columns:
        year_column = column
        break


url_column = None

for column in [
    "bse_pdf",
    "bse_url",
    "annual_report_url",
    "pdf_url",
    "url",
]:
    if column in documents.columns:
        url_column = column
        break


# ============================================================
# SEARCH
# ============================================================

search = st.text_input(
    "Search company name or ticker",
    placeholder="Example: TCS",
)


filtered = documents.copy()


if search.strip():

    query = search.strip().lower()

    mask = pd.Series(
        False,
        index=filtered.index,
    )

    if company_column:

        mask = (
            mask
            |
            filtered[
                company_column
            ]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(
                query,
                na=False,
            )
        )

    if name_column:

        mask = (
            mask
            |
            filtered[
                name_column
            ]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.contains(
                query,
                na=False,
            )
        )

    filtered = filtered[
        mask
    ]


if filtered.empty:

    st.warning(
        "Ticker not found — please try another."
    )

    st.stop()


# ============================================================
# COMPANY SELECTION
# ============================================================

if company_column:

    company_options = (
        filtered[
            company_column
        ]
        .fillna("")
        .astype(str)
        .str.upper()
        .unique()
        .tolist()
    )

    selected_company = st.selectbox(
        "Select Company",
        company_options,
    )

    filtered = filtered[
        filtered[
            company_column
        ]
        .fillna("")
        .astype(str)
        .str.upper()
        == selected_company
    ]


# ============================================================
# REPORT LIST
# ============================================================

st.subheader("Available Annual Reports")


for _, row in filtered.iterrows():

    if year_column:
        year = row.get(
            year_column,
            "Unknown",
        )
    else:
        year = "Unknown"

    report_name = (
        f"Annual Report {year}"
    )

    st.markdown(
        f"### {report_name}"
    )

    if url_column:

        url = row.get(
            url_column
        )

        if (
            pd.notna(url)
            and str(url).strip()
        ):

            url = str(url).strip()

            st.markdown(
                f"[📄 Open BSE Annual Report]({url})"
            )

        else:

            st.error(
                "Report unavailable"
            )

    else:

        st.error(
            "Report unavailable"
        )

    st.divider()