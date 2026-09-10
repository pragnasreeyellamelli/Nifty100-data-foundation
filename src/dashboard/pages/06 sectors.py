import pandas as pd
import streamlit as st
import plotly.express as px

from src.screener.engine import load_screener_data
from src.dashboard.utils.db import get_sectors


st.title("🏭 Sector Analysis")
st.caption(
    "Compare companies and financial performance by sector"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(ttl=600)
def load_sector_data():
    return load_screener_data()


df = load_sector_data().copy()


# ============================================================
# LOAD SECTOR LIST
# ============================================================

sector_master = get_sectors()

if (
    "sector_name" in sector_master.columns
    and not sector_master.empty
):
    sector_names = (
        sector_master["sector_name"]
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )
else:
    sector_names = []


# Fallback to the project peer universe if required.
if not sector_names:
    sector_names = [
        "Automobiles",
        "Consumer Finance",
        "FMCG",
        "IT Services",
        "Life Insurance",
        "Oil & Gas",
        "Pharmaceuticals",
        "Power & Utilities",
        "Private Banks",
        "Public Sector Banks",
        "Steel",
    ]


sector_names = sorted(
    set(sector_names)
)


# ============================================================
# COMPANY SECTOR COLUMN
# ============================================================

sector_column = None

for column in [
    "broad_sector",
    "sector",
]:
    if column in df.columns:
        sector_column = column
        break


# ============================================================
# SECTOR SELECTOR
# ============================================================

selected_sector = st.selectbox(
    "Select Sector",
    sector_names,
)


# ============================================================
# HANDLE MISSING SECTOR MAPPING
# ============================================================

if sector_column is None:

    st.info(
        "Sector mapping is not available in the current "
        "company dataset."
    )

    st.write(
        "The sector master contains:",
        len(sector_names),
        "sectors.",
    )

    st.stop()


# Clean sector values.
df[sector_column] = (
    df[sector_column]
    .fillna("")
    .astype(str)
    .str.strip()
)


sector_df = df[
    df[sector_column]
    .str.lower()
    == selected_sector.lower()
].copy()


# ============================================================
# NO MATCHING COMPANIES
# ============================================================

if sector_df.empty:

    st.info(
        f"No company records are currently mapped "
        f"to the '{selected_sector}' sector."
    )

    st.caption(
        "The dashboard remains functional even when "
        "sector mapping is incomplete."
    )

    st.stop()


st.subheader(
    f"📊 {selected_sector} Companies"
)


# ============================================================
# NUMERIC CLEANUP
# ============================================================

for column in [
    "sales",
    "market_cap",
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "pe_ratio",
    "pb_ratio",
]:
    if column in sector_df.columns:

        sector_df[column] = pd.to_numeric(
            sector_df[column],
            errors="coerce",
        )


# ============================================================
# BUBBLE-SIZE FALLBACK
# ============================================================

if "market_cap" in sector_df.columns:

    sector_df["plot_market_cap"] = (
        sector_df["market_cap"]
        .fillna(
            sector_df["sales"]
            if "sales" in sector_df.columns
            else 1
        )
        .fillna(1)
        .clip(lower=1)
    )

else:

    if "sales" in sector_df.columns:

        sector_df["plot_market_cap"] = (
            sector_df["sales"]
            .fillna(1)
            .clip(lower=1)
        )

    else:

        sector_df["plot_market_cap"] = 1


# ============================================================
# BUBBLE CHART
# ============================================================

has_revenue = (
    "sales" in sector_df.columns
    and sector_df["sales"].notna().any()
)

has_roe = (
    "return_on_equity_pct"
    in sector_df.columns
    and sector_df[
        "return_on_equity_pct"
    ].notna().any()
)


if has_revenue and has_roe:

    bubble_df = sector_df[
        [
            "sales",
            "return_on_equity_pct",
            "plot_market_cap",
        ]
    ].copy()

    # Remove rows Plotly cannot plot.
    bubble_df = bubble_df.dropna(
        subset=[
            "sales",
            "return_on_equity_pct",
        ]
    )

    if not bubble_df.empty:

        # Add company labels.
        if "company_name" in sector_df.columns:

            bubble_df["company_name"] = (
                sector_df.loc[
                    bubble_df.index,
                    "company_name",
                ]
                .fillna("")
                .astype(str)
            )

        elif "ticker" in sector_df.columns:

            bubble_df["company_name"] = (
                sector_df.loc[
                    bubble_df.index,
                    "ticker",
                ]
                .fillna("")
                .astype(str)
            )

        else:

            bubble_df["company_name"] = "Company"

        # ----------------------------------------------------
        # Colour field
        # ----------------------------------------------------

        if (
            "sub_sector"
            in sector_df.columns
        ):

            bubble_df["sub_sector"] = (
                sector_df.loc[
                    bubble_df.index,
                    "sub_sector",
                ]
                .fillna("Other")
                .astype(str)
            )

            color_column = "sub_sector"

        else:

            bubble_df["sub_sector"] = (
                selected_sector
            )

            color_column = "sub_sector"


        figure = px.scatter(
            bubble_df,
            x="sales",
            y="return_on_equity_pct",
            size="plot_market_cap",
            hover_name="company_name",
            color=color_column,
            title=(
                f"{selected_sector} — "
                f"Revenue vs ROE"
            ),
            labels={
                "sales": "Revenue",
                "return_on_equity_pct": "ROE (%)",
                "plot_market_cap": "Market Cap",
            },
        )

        figure.update_layout(
            height=550,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20,
            ),
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
        )

    else:

        st.info(
            "Revenue and ROE values are unavailable "
            "for this sector."
        )

else:

    st.info(
        "Revenue and ROE data are required for "
        "the sector bubble chart."
    )


# ============================================================
# COMPANY TABLE
# ============================================================

st.subheader("Companies in Selected Sector")

display_columns = [
    column
    for column in [
        "ticker",
        "company_name",
        "sales",
        "return_on_equity_pct",
        "debt_to_equity",
        "pe_ratio",
        "pb_ratio",
    ]
    if column in sector_df.columns
]


if display_columns:

    st.dataframe(
        sector_df[display_columns],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# SECTOR MEDIAN KPIs
# ============================================================

st.subheader("📌 Sector Median KPIs")


median_columns = [
    column
    for column in [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "pe_ratio",
        "pb_ratio",
    ]
    if column in sector_df.columns
]


if median_columns:

    medians = (
        sector_df[
            median_columns
        ]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
        .median()
        .reset_index()
    )

    medians.columns = [
        "Metric",
        "Median",
    ]

    st.dataframe(
        medians,
        use_container_width=True,
        hide_index=True,
    )

    chart = px.bar(
        medians,
        x="Metric",
        y="Median",
        title=(
            f"{selected_sector} "
            "Median KPI Values"
        ),
    )

    chart.update_layout(
        height=450,
    )

    st.plotly_chart(
        chart,
        use_container_width=True,
    )
else:

    st.info(
        "No numeric KPI data available "
        "for this sector."
    )