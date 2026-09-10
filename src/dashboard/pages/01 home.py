import pandas as pd
import streamlit as st

from src.dashboard.utils.db import get_companies, get_sectors
from src.screener.engine import load_screener_data, add_composite_quality_score


st.title("🏠 NIFTY 100 Overview")
st.caption("Financial analytics summary for the NIFTY 100 universe")


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(ttl=600)
def load_home_data():

    df = load_screener_data()
    df = add_composite_quality_score(df)

    return df


df = load_home_data()


# ============================================================
# YEAR SELECTOR
# ============================================================

years = []

if "year" in df.columns:

    for value in df["year"].dropna().unique():

        text = str(value)

        if text.isdigit():
            years.append(int(text))

years = sorted(set(years))

if not years:
    years = list(range(2019, 2025))

selected_year = st.sidebar.selectbox(
    "Select Year",
    years,
    index=len(years) - 1,
)

st.sidebar.caption(
    f"Selected year: {selected_year}"
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

roe = pd.to_numeric(
    df.get(
        "return_on_equity_pct",
        pd.Series(dtype=float),
    ),
    errors="coerce",
)

pe = pd.to_numeric(
    df.get(
        "pe_ratio",
        pd.Series(dtype=float),
    ),
    errors="coerce",
)

de = pd.to_numeric(
    df.get(
        "debt_to_equity",
        pd.Series(dtype=float),
    ),
    errors="coerce",
)

revenue_cagr = pd.to_numeric(
    df.get(
        "revenue_cagr_5yr",
        pd.Series(dtype=float),
    ),
    errors="coerce",
)

debt_free_count = int(
    (de.fillna(-1) == 0).sum()
)


# ============================================================
# KPI TILES
# ============================================================

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.metric(
        "Average ROE",
        (
            f"{roe.mean():.2f}%"
            if roe.notna().any()
            else "N/A"
        ),
    )

with c2:
    st.metric(
        "Median P/E",
        (
            f"{pe.median():.2f}"
            if pe.notna().any()
            else "N/A"
        ),
    )

with c3:
    st.metric(
        "Median D/E",
        (
            f"{de.median():.2f}"
            if de.notna().any()
            else "N/A"
        ),
    )

with c4:
    st.metric(
        "Total Companies",
        len(df),
    )

with c5:
    st.metric(
        "Median Revenue CAGR 5yr",
        (
            f"{revenue_cagr.median():.2f}%"
            if revenue_cagr.notna().any()
            else "N/A"
        ),
    )

with c6:
    st.metric(
        "Debt-Free Companies",
        debt_free_count,
    )


st.divider()


# ============================================================
# TOP 5 COMPANIES
# ============================================================

st.subheader("🏆 Top 5 Companies by Composite Quality Score")

top_columns = [
    "ticker",
    "company_name",
    "return_on_equity_pct",
    "debt_to_equity",
    "composite_quality_score",
]

available_columns = [
    column
    for column in top_columns
    if column in df.columns
]

top5 = (
    df[
        available_columns
    ]
    .sort_values(
        "composite_quality_score",
        ascending=False,
    )
    .head(5)
    .copy()
)

st.dataframe(
    top5,
    use_container_width=True,
    hide_index=True,
)


st.divider()


# ============================================================
# SECTOR BREAKDOWN
# ============================================================

st.subheader("📊 Sector Breakdown")

try:

    sector_df = get_sectors()

    if (
        "sector_name"
        in sector_df.columns
    ):

        sector_counts = (
            sector_df[
                "sector_name"
            ]
            .value_counts()
            .reset_index()
        )

        sector_counts.columns = [
            "Sector",
            "Count",
        ]

        st.bar_chart(
            sector_counts.set_index(
                "Sector"
            )
        )

    else:

        st.info(
            "Sector data is available, "
            "but no sector_name column was found."
        )

except Exception as exc:

    st.warning(
        f"Sector breakdown unavailable: {exc}"
    )


# ============================================================
# INFO
# ============================================================

st.divider()

st.info(
    "Use the sidebar to open the Company Profile, "
    "Screener, Peer Comparison, Trends, Sector Analysis, "
    "Capital Allocation, and Annual Reports screens."
)