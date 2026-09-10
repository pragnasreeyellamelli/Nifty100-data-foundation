import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.dashboard.utils.db import (
    get_companies,
    get_pl,
    get_ratios,
)
from src.screener.engine import load_screener_data


st.title("👤 Company Profile")
st.caption("Financial profile and historical performance")


# ============================================================
# LOAD COMPANY LIST
# ============================================================

companies = get_companies()
screener_df = load_screener_data()

if "ticker" in screener_df.columns:
    ticker_map = screener_df[
        ["ticker", "company_name", "sector"]
    ].copy()

    ticker_map["ticker"] = (
        ticker_map["ticker"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

else:
    ticker_map = pd.DataFrame(
        columns=[
            "ticker",
            "company_name",
            "sector",
        ]
    )


# ============================================================
# SEARCH
# ============================================================

search_text = st.text_input(
    "Search company name or ticker",
    placeholder="Example: TCS or Tata Consultancy Services",
)


if search_text.strip():

    query = search_text.strip().lower()

    matches = ticker_map[
        ticker_map["ticker"]
        .str.lower()
        .str.contains(query, na=False)
        |
        ticker_map["company_name"]
        .fillna("")
        .str.lower()
        .str.contains(query, na=False)
    ].copy()

else:
    matches = ticker_map.head(0)


if matches.empty:

    if search_text.strip():
        st.warning(
            "Ticker not found — please try another."
        )

    else:
        st.info(
            "Enter a company name or ticker to begin."
        )

    st.stop()


# ============================================================
# SELECT COMPANY
# ============================================================

options = (
    matches["ticker"]
    + " — "
    + matches["company_name"].fillna("")
)

selected_display = st.selectbox(
    "Select Company",
    options.tolist(),
)

selected_ticker = (
    selected_display
    .split(" — ")[0]
    .strip()
    .upper()
)


company_row = matches[
    matches["ticker"] == selected_ticker
].iloc[0]


# ============================================================
# COMPANY CARD
# ============================================================

st.subheader(
    f"🏢 {company_row['company_name']}"
)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Ticker",
        selected_ticker,
    )

with c2:
    st.metric(
        "Sector",
        (
            company_row["sector"]
            if pd.notna(company_row["sector"])
            else "N/A"
        ),
    )

with c3:
    st.metric(
        "Company ID",
        str(
            company_row.get(
                "company_id",
                "N/A",
            )
        ),
    )


# ============================================================
# FINANCIAL DATA
# ============================================================

ratios = get_ratios(
    selected_ticker
)

pl = get_pl(
    selected_ticker
)


if ratios.empty:

    st.warning(
        "No financial ratio data is available for this ticker."
    )

    st.stop()


latest = ratios.iloc[0]


def number(
    row,
    column,
):
    if column not in row.index:
        return None

    value = pd.to_numeric(
        row[column],
        errors="coerce",
    )

    if pd.isna(value):
        return None

    return float(value)


roe = number(
    latest,
    "return_on_equity_pct",
)

roce = number(
    latest,
    "return_on_capital_employed_pct",
)

npm = number(
    latest,
    "net_profit_margin_pct",
)

de = number(
    latest,
    "debt_to_equity",
)

fcf = number(
    latest,
    "free_cash_flow_cr",
)


# Revenue CAGR from screener data
screener_match = screener_df[
    screener_df["ticker"]
    .astype(str)
    .str.upper()
    == selected_ticker
]

if not screener_match.empty:

    row = screener_match.iloc[0]

    revenue_cagr = number(
        row,
        "revenue_cagr_5yr",
    )

else:
    revenue_cagr = None


# ============================================================
# KPI TILES
# ============================================================

st.subheader("📊 Key Financial Indicators")

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    st.metric(
        "ROE",
        f"{roe:.2f}%" if roe is not None else "N/A",
    )

with k2:
    st.metric(
        "ROCE",
        f"{roce:.2f}%" if roce is not None else "N/A",
    )

with k3:
    st.metric(
        "Net Profit Margin",
        f"{npm:.2f}%" if npm is not None else "N/A",
    )

with k4:
    st.metric(
        "D/E",
        f"{de:.2f}" if de is not None else "N/A",
    )

with k5:
    st.metric(
        "Revenue CAGR 5yr",
        (
            f"{revenue_cagr:.2f}%"
            if revenue_cagr is not None
            else "N/A"
        ),
    )

with k6:
    st.metric(
        "FCF",
        (
            f"{fcf:,.2f}"
            if fcf is not None
            else "N/A"
        ),
    )


# ============================================================
# 10-YEAR REVENUE / NET PROFIT
# ============================================================

st.subheader("📈 Revenue & Net Profit Trend")

if not pl.empty:

    pl_work = pl.copy()

    year_column = (
        "year"
        if "year" in pl_work.columns
        else None
    )

    sales_column = None

    for column in [
        "sales",
        "revenue",
    ]:

        if column in pl_work.columns:
            sales_column = column
            break

    profit_column = None

    for column in [
        "net_profit",
        "profit_after_tax",
    ]:

        if column in pl_work.columns:
            profit_column = column
            break

    if (
        year_column
        and sales_column
        and profit_column
    ):

        chart_df = pl_work[
            [
                year_column,
                sales_column,
                profit_column,
            ]
        ].copy()

        chart_df["year"] = (
            chart_df[year_column]
            .astype(str)
        )

        chart_df[sales_column] = pd.to_numeric(
            chart_df[sales_column],
            errors="coerce",
        )

        chart_df[profit_column] = pd.to_numeric(
            chart_df[profit_column],
            errors="coerce",
        )

        chart_df = chart_df.dropna(
            subset=[
                "year",
                sales_column,
                profit_column,
            ]
        ).sort_values("year").tail(10)

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=chart_df["year"],
                y=chart_df[sales_column],
                name="Revenue",
            )
        )

        fig.add_trace(
            go.Bar(
                x=chart_df["year"],
                y=chart_df[profit_column],
                name="Net Profit",
            )
        )

        fig.update_layout(
            barmode="group",
            xaxis_title="Year",
            yaxis_title="Amount",
            height=450,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info(
            "Revenue and Net Profit history is not available."
        )

else:

    st.info(
        "Profit & Loss history is not available."
    )


# ============================================================
# ROE / ROCE TREND
# ============================================================

st.subheader("📉 ROE & ROCE Trend")

if not ratios.empty:

    trend = ratios.copy()

    if "year" in trend.columns:

        trend["year"] = (
            trend["year"]
            .astype(str)
        )

        trend["roe"] = pd.to_numeric(
            trend.get(
                "return_on_equity_pct"
            ),
            errors="coerce",
        )

        trend["roce"] = pd.to_numeric(
            trend.get(
                "return_on_capital_employed_pct"
            ),
            errors="coerce",
        )

        trend = trend.dropna(
            subset=["year"]
        ).sort_values(
            "year"
        ).tail(10)

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=trend["year"],
                y=trend["roe"],
                mode="lines+markers",
                name="ROE",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=trend["year"],
                y=trend["roce"],
                mode="lines+markers",
                name="ROCE",
            )
        )

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Percentage",
            height=450,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


# ============================================================
# PROS & CONS
# ============================================================

st.subheader("✅ Pros & Cons")

pros, cons = st.columns(2)

with pros:

    st.markdown("### ✅ Pros")

    if roe is not None and roe > 15:
        st.success("Strong ROE")
    else:
        st.info("ROE is below the 15% quality threshold")

    if fcf is not None and fcf > 0:
        st.success("Positive Free Cash Flow")
    else:
        st.info("Free Cash Flow is not positive")

    if de is not None and de < 1:
        st.success("Moderate Debt-to-Equity")
    else:
        st.info("Debt-to-Equity is relatively high")


with cons:

    st.markdown("### ❌ Cons")

    if roe is not None and roe <= 15:
        st.error("ROE below 15%")

    if fcf is not None and fcf <= 0:
        st.error("Negative Free Cash Flow")

    if de is not None and de >= 1:
        st.error("Debt-to-Equity above 1")
