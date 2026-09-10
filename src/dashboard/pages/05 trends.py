import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from src.dashboard.utils.db import get_ratios, get_pl


st.title("📈 Trend Analysis")
st.caption("Historical financial trend analysis for a selected company")


# ============================================================
# COMPANY SELECTION
# ============================================================

ticker = st.text_input(
    "Enter Company Ticker",
    placeholder="Example: TCS",
).strip().upper()


if not ticker:
    st.info("Enter a ticker to view historical trends.")
    st.stop()


ratios = get_ratios(ticker)
pl = get_pl(ticker)


if ratios.empty and pl.empty:
    st.warning(
        "Ticker not found — please try another."
    )
    st.stop()


# ============================================================
# BUILD HISTORICAL DATA
# ============================================================

frames = []

if not ratios.empty:
    ratio_df = ratios.copy()

    if "year" in ratio_df.columns:
        ratio_df["year"] = ratio_df["year"].astype(str)

        frames.append(
            ratio_df
        )

if not pl.empty:
    pl_df = pl.copy()

    if "year" in pl_df.columns:
        pl_df["year"] = pl_df["year"].astype(str)

        frames.append(
            pl_df
        )


if not frames:
    st.warning("Historical year information is unavailable.")
    st.stop()


# Merge all available historical data
history = frames[0].copy()

for frame in frames[1:]:
    common = [
        column
        for column in [
            "company_id",
            "year",
        ]
        if column in history.columns
        and column in frame.columns
    ]

    if common:
        history = history.merge(
            frame,
            on=common,
            how="outer",
            suffixes=("", "_extra"),
        )
    else:
        history = pd.concat(
            [
                history,
                frame,
            ],
            ignore_index=True,
        )


history = history.drop_duplicates(
    subset=["year"],
    keep="first",
)


# ============================================================
# AVAILABLE METRICS
# ============================================================

metric_map = {
    "Revenue": "sales",
    "Net Profit": "net_profit",
    "ROE": "return_on_equity_pct",
    "ROCE": "return_on_capital_employed_pct",
    "Net Profit Margin": "net_profit_margin_pct",
    "Debt-to-Equity": "debt_to_equity",
    "Free Cash Flow": "free_cash_flow_cr",
    "P/E": "pe_ratio",
    "P/B": "pb_ratio",
}


available_metrics = {
    label: column
    for label, column in metric_map.items()
    if column in history.columns
}


if not available_metrics:
    st.warning(
        "No supported historical metrics are available."
    )
    st.stop()


selected_metrics = st.multiselect(
    "Select up to 3 metrics",
    list(available_metrics.keys()),
    default=list(available_metrics.keys())[:2],
    max_selections=3,
)


if not selected_metrics:
    st.info("Select at least one metric.")
    st.stop()


# ============================================================
# CHART DATA
# ============================================================

chart_df = history.copy()

chart_df = chart_df.sort_values(
    "year"
)

fig = go.Figure()

for label in selected_metrics:

    column = available_metrics[label]

    values = pd.to_numeric(
        chart_df[column],
        errors="coerce",
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df["year"],
            y=values,
            mode="lines+markers+text",
            text=[
                (
                    f"{value:.2f}"
                    if pd.notna(value)
                    else "N/A"
                )
                for value in values
            ],
            textposition="top center",
            name=label,
        )
    )


fig.update_layout(
    title=f"{ticker} — Historical Trends",
    xaxis_title="Year",
    yaxis_title="Value",
    height=550,
    hovermode="x unified",
)


st.plotly_chart(
    fig,
    use_container_width=True,
)


# ============================================================
# YEAR-OVER-YEAR CHANGE
# ============================================================

st.subheader("Year-over-Year Change")

yoy = chart_df[
    ["year"]
    + [
        available_metrics[label]
        for label in selected_metrics
    ]
].copy()

for label in selected_metrics:

    column = available_metrics[label]

    yoy[column] = pd.to_numeric(
        yoy[column],
        errors="coerce",
    )

    yoy[f"{label} YoY %"] = (
        yoy[column]
        .pct_change()
        * 100
    )


yoy_columns = ["year"]

for label in selected_metrics:
    yoy_columns.append(
        f"{label} YoY %"
    )


display_yoy = yoy[
    yoy_columns
].copy()

st.dataframe(
    display_yoy,
    use_container_width=True,
    hide_index=True,
)