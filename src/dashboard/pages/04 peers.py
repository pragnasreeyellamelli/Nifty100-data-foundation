import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from src.dashboard.utils.db import get_peers


st.title("🤝 Peer Comparison")
st.caption("Compare a company with its peer-group benchmark")


# ============================================================
# PEER GROUPS
# ============================================================

peer_groups = [
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

selected_group = st.selectbox(
    "Select Peer Group",
    peer_groups,
)


# ============================================================
# LOAD PEER DATA
# ============================================================

df = get_peers(
    selected_group
)

if df.empty:
    st.warning(
        "No peer data is available for this group."
    )
    st.stop()


# ============================================================
# COMPANY LIST
# ============================================================

companies = (
    df["company_id"]
    .dropna()
    .astype(str)
    .str.upper()
    .unique()
    .tolist()
)

selected_company = st.selectbox(
    "Select Company",
    companies,
)


# ============================================================
# METRIC MAPPING
# ============================================================

metric_map = {
    "ROE": "ROE",
    "ROCE": "ROCE",
    "NPM": "Net Profit Margin",
    "D/E": "D/E",
    "FCF Score": "FCF",
    "PAT CAGR 5yr": "PAT CAGR 5yr",
    "Revenue CAGR 5yr": "Revenue CAGR 5yr",
    "Composite Score": "Composite Score",
}


# ============================================================
# SELECTED COMPANY VALUES
# ============================================================

company_df = df[
    df["company_id"]
    .astype(str)
    .str.upper()
    == selected_company
].copy()


if company_df.empty:
    st.warning("Company data not available.")
    st.stop()


company_values = {}

peer_values = {}

for display_name, metric_name in metric_map.items():

    company_row = company_df[
        company_df["metric"]
        == metric_name
    ]

    peer_row = df[
        df["metric"]
        == metric_name
    ]

    if company_row.empty:
        company_values[display_name] = 0.0
    else:
        company_values[display_name] = float(
            pd.to_numeric(
                company_row["percentile_rank"].iloc[0],
                errors="coerce",
            )
            if pd.notna(
                company_row["percentile_rank"].iloc[0]
            )
            else 0.0
        )

    peer_values[display_name] = (
        float(
            pd.to_numeric(
                peer_row["percentile_rank"],
                errors="coerce",
            ).mean()
        )
        if not peer_row.empty
        else 0.0
    )


# ============================================================
# RADAR CHART
# ============================================================

st.subheader(
    f"📊 {selected_company} vs {selected_group} Average"
)

labels = list(
    metric_map.keys()
)

company_scores = [
    company_values[label]
    for label in labels
]

peer_scores = [
    peer_values[label]
    for label in labels
]

angles = list(
    range(len(labels))
)

angles += angles[:1]

company_scores += company_scores[:1]
peer_scores += peer_scores[:1]


fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=company_scores,
        theta=labels,
        fill="toself",
        name=selected_company,
    )
)

fig.add_trace(
    go.Scatterpolar(
        r=peer_scores,
        theta=labels,
        fill=None,
        line=dict(
            dash="dash"
        ),
        name="Peer Average",
    )
)

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100],
        )
    ),
    showlegend=True,
    height=550,
)

st.plotly_chart(
    fig,
    use_container_width=True,
)


# ============================================================
# PEER TABLE
# ============================================================

st.subheader(
    f"📋 {selected_group} Companies"
)

wide = df.pivot_table(
    index="company_id",
    columns="metric",
    values="percentile_rank",
    aggfunc="first",
).reset_index()

wide = wide.rename(
    columns={
        column: f"{column} Percentile"
        for column in wide.columns
        if column != "company_id"
    }
)

if "is_benchmark" in df.columns:

    benchmark = (
        df[
            [
                "company_id",
                "is_benchmark",
            ]
        ]
        .drop_duplicates(
            "company_id"
        )
    )

    wide = wide.merge(
        benchmark,
        on="company_id",
        how="left",
    )

else:

    wide["is_benchmark"] = False


# Highlight benchmark row
def highlight_benchmark(row):

    if row.get(
        "is_benchmark",
        False,
    ):
        return [
            "background-color: #FFD966"
        ] * len(row)

    return [""] * len(row)


st.dataframe(
    wide.style.apply(
        highlight_benchmark,
        axis=1,
    ),
    use_container_width=True,
    hide_index=True,
)