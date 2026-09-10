import io

import pandas as pd
import streamlit as st

from src.screener.engine import (
    load_screener_data,
    add_composite_quality_score,
    apply_filters,
    PRESET_SCREENERS,
)


st.title("🔎 Financial Screener")
st.caption(
    "Filter the NIFTY 100 universe using financial thresholds."
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(ttl=600)
def load_data():

    df = load_screener_data()
    df = add_composite_quality_score(df)

    return df


df = load_data()


# ============================================================
# DEFAULT VALUES
# ============================================================

defaults = {
    "roe_min": 0.0,
    "de_max": 10.0,
    "fcf_min": 0.0,
    "revenue_cagr_min": 0.0,
    "pat_cagr_min": 0.0,
    "opm_min": 0.0,
    "pe_max": 100.0,
    "pb_max": 20.0,
    "dividend_yield_min": 0.0,
    "icr_min": 0.0,
}


for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# PRESET FUNCTIONS
# ============================================================

def set_preset(name):

    if name == "Quality":

        st.session_state.roe_min = 15.0
        st.session_state.de_max = 1.0
        st.session_state.fcf_min = 0.0
        st.session_state.revenue_cagr_min = 10.0
        st.session_state.pat_cagr_min = 0.0
        st.session_state.opm_min = 0.0
        st.session_state.pe_max = 100.0
        st.session_state.pb_max = 20.0
        st.session_state.dividend_yield_min = 0.0
        st.session_state.icr_min = 0.0

    elif name == "Value":

        st.session_state.roe_min = 0.0
        st.session_state.de_max = 2.0
        st.session_state.fcf_min = 0.0
        st.session_state.revenue_cagr_min = 0.0
        st.session_state.pat_cagr_min = 0.0
        st.session_state.opm_min = 0.0
        st.session_state.pe_max = 20.0
        st.session_state.pb_max = 3.0
        st.session_state.dividend_yield_min = 1.0
        st.session_state.icr_min = 0.0

    elif name == "Growth":

        st.session_state.roe_min = 0.0
        st.session_state.de_max = 2.0
        st.session_state.fcf_min = 0.0
        st.session_state.revenue_cagr_min = 15.0
        st.session_state.pat_cagr_min = 20.0
        st.session_state.opm_min = 0.0
        st.session_state.pe_max = 100.0
        st.session_state.pb_max = 20.0
        st.session_state.dividend_yield_min = 0.0
        st.session_state.icr_min = 0.0

    elif name == "Dividend":

        st.session_state.roe_min = 0.0
        st.session_state.de_max = 10.0
        st.session_state.fcf_min = 0.0
        st.session_state.revenue_cagr_min = 0.0
        st.session_state.pat_cagr_min = 0.0
        st.session_state.opm_min = 0.0
        st.session_state.pe_max = 100.0
        st.session_state.pb_max = 20.0
        st.session_state.dividend_yield_min = 2.0
        st.session_state.icr_min = 0.0

    elif name == "Debt-Free":

        st.session_state.roe_min = 12.0
        st.session_state.de_max = 0.0
        st.session_state.fcf_min = 0.0
        st.session_state.revenue_cagr_min = 0.0
        st.session_state.pat_cagr_min = 0.0
        st.session_state.opm_min = 0.0
        st.session_state.pe_max = 100.0
        st.session_state.pb_max = 20.0
        st.session_state.dividend_yield_min = 0.0
        st.session_state.icr_min = 0.0

    elif name == "Turnaround":

        st.session_state.roe_min = 0.0
        st.session_state.de_max = 10.0
        st.session_state.fcf_min = 0.0
        st.session_state.revenue_cagr_min = 10.0
        st.session_state.pat_cagr_min = 0.0
        st.session_state.opm_min = 0.0
        st.session_state.pe_max = 100.0
        st.session_state.pb_max = 20.0
        st.session_state.dividend_yield_min = 0.0
        st.session_state.icr_min = 0.0


# ============================================================
# PRESET BUTTONS
# ============================================================

st.subheader("Preset Screeners")

p1, p2, p3, p4, p5, p6 = st.columns(6)

with p1:
    if st.button(
        "Quality",
        use_container_width=True,
    ):
        set_preset("Quality")
        st.rerun()

with p2:
    if st.button(
        "Value",
        use_container_width=True,
    ):
        set_preset("Value")
        st.rerun()

with p3:
    if st.button(
        "Growth",
        use_container_width=True,
    ):
        set_preset("Growth")
        st.rerun()

with p4:
    if st.button(
        "Dividend",
        use_container_width=True,
    ):
        set_preset("Dividend")
        st.rerun()

with p5:
    if st.button(
        "Debt-Free",
        use_container_width=True,
    ):
        set_preset("Debt-Free")
        st.rerun()

with p6:
    if st.button(
        "Turnaround",
        use_container_width=True,
    ):
        set_preset("Turnaround")
        st.rerun()


st.divider()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.subheader("Screener Filters")

st.sidebar.slider(
    "ROE minimum (%)",
    min_value=0.0,
    max_value=100.0,
    step=0.5,
    key="roe_min",
)

st.sidebar.slider(
    "D/E maximum",
    min_value=0.0,
    max_value=10.0,
    step=0.1,
    key="de_max",
)

st.sidebar.slider(
    "FCF minimum",
    min_value=-100000.0,
    max_value=100000.0,
    step=100.0,
    key="fcf_min",
)

st.sidebar.slider(
    "Revenue CAGR 5yr minimum (%)",
    min_value=0.0,
    max_value=50.0,
    step=0.5,
    key="revenue_cagr_min",
)

st.sidebar.slider(
    "PAT CAGR 5yr minimum (%)",
    min_value=0.0,
    max_value=100.0,
    step=1.0,
    key="pat_cagr_min",
)

st.sidebar.slider(
    "OPM minimum (%)",
    min_value=0.0,
    max_value=100.0,
    step=0.5,
    key="opm_min",
)

st.sidebar.slider(
    "P/E maximum",
    min_value=1.0,
    max_value=200.0,
    step=1.0,
    key="pe_max",
)

st.sidebar.slider(
    "P/B maximum",
    min_value=0.5,
    max_value=30.0,
    step=0.5,
    key="pb_max",
)

st.sidebar.slider(
    "Dividend Yield minimum (%)",
    min_value=0.0,
    max_value=20.0,
    step=0.5,
    key="dividend_yield_min",
)

st.sidebar.slider(
    "ICR minimum",
    min_value=0.0,
    max_value=50.0,
    step=0.5,
    key="icr_min",
)


# ============================================================
# APPLY FILTERS
# ============================================================

filters = {
    "roe_min": st.session_state.roe_min,
    "de_max": st.session_state.de_max,
    "fcf_min": st.session_state.fcf_min,
    "revenue_cagr_5yr_min":
        st.session_state.revenue_cagr_min,
    "pat_cagr_5yr_min":
        st.session_state.pat_cagr_min,
    "opm_min":
        st.session_state.opm_min,
    "pe_max":
        st.session_state.pe_max,
    "pb_max":
        st.session_state.pb_max,
    "dividend_yield_min":
        st.session_state.dividend_yield_min,
    "icr_min":
        st.session_state.icr_min,
}


result = apply_filters(
    df,
    filters,
)

result = add_composite_quality_score(
    result
)


# ============================================================
# SORT
# ============================================================

if "composite_quality_score" in result.columns:

    result = result.sort_values(
        "composite_quality_score",
        ascending=False,
        kind="stable",
    )


# ============================================================
# RESULT COUNT
# ============================================================

st.subheader(
    f"{len(result)} companies match your filters"
)


# ============================================================
# DISPLAY COLUMNS
# ============================================================

display_columns = [
    "company_id",
    "ticker",
    "company_name",
    "sector",
    "return_on_equity_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "operating_profit_margin_pct",
    "pe_ratio",
    "pb_ratio",
    "dividend_yield_pct",
    "interest_coverage",
    "composite_quality_score",
]

display_columns = [
    column
    for column in display_columns
    if column in result.columns
]

table = result[
    display_columns
].copy()


# ============================================================
# RESULTS TABLE
# ============================================================

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# CSV EXPORT
# ============================================================

st.subheader("Export")

csv_buffer = io.StringIO()

table.to_csv(
    csv_buffer,
    index=False,
)

st.download_button(
    label="⬇️ Download Results as CSV",
    data=csv_buffer.getvalue(),
    file_name="screener_results.csv",
    mime="text/csv",
    use_container_width=False,
)


# ============================================================
# CURRENT FILTER SUMMARY
# ============================================================

with st.expander("Current Filters"):

    st.json(filters)