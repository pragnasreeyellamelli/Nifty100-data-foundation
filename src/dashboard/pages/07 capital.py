from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px


st.title("💰 Capital Allocation Map")
st.caption(
    "NIFTY 100 companies grouped by capital allocation pattern"
)


# ============================================================
# FIND CAPITAL ALLOCATION FILE
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CAPITAL_FILE = (
    PROJECT_ROOT
    / "output"
    / "capital_allocation.csv"
)


if not CAPITAL_FILE.exists():

    st.warning(
        "Capital allocation file is not available."
    )

    st.info(
        "Expected file: output/capital_allocation.csv"
    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(
    CAPITAL_FILE
)


if df.empty:
    st.info("No capital allocation data available.")
    st.stop()


# ============================================================
# IDENTIFY COLUMNS
# ============================================================

pattern_column = None

for column in [
    "capital_allocation_pattern",
    "capital_allocation",
    "pattern",
    "classification",
    "capital_allocation_class",
]:
    if column in df.columns:
        pattern_column = column
        break


if pattern_column is None:

    st.error(
        "No capital allocation pattern column was found."
    )

    st.write(
        "Available columns:",
        list(df.columns),
    )

    st.stop()


# ============================================================
# TREEMAP
# ============================================================

summary = (
    df[pattern_column]
    .fillna("Unknown")
    .astype(str)
    .value_counts()
    .reset_index()
)

summary.columns = [
    "Pattern",
    "Company Count",
]


st.subheader(
    "Capital Allocation Patterns"
)


figure = px.treemap(
    summary,
    path=["Pattern"],
    values="Company Count",
    title="NIFTY 100 Capital Allocation Patterns",
)


figure.update_layout(
    height=600,
)


st.plotly_chart(
    figure,
    use_container_width=True,
)


# ============================================================
# PATTERN SELECTOR
# ============================================================

patterns = sorted(
    df[pattern_column]
    .fillna("Unknown")
    .astype(str)
    .unique()
)


selected_pattern = st.selectbox(
    "Select Pattern",
    patterns,
)


pattern_df = df[
    df[pattern_column]
    .fillna("Unknown")
    .astype(str)
    == selected_pattern
].copy()


st.subheader(
    f"Companies in: {selected_pattern}"
)


display_columns = [
    column
    for column in [
        "company_id",
        "ticker",
        "company_name",
        "sector",
        pattern_column,
    ]
    if column in pattern_df.columns
]


st.dataframe(
    pattern_df[display_columns],
    use_container_width=True,
    hide_index=True,
)