from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.screener.engine import (
    load_screener_data,
    add_composite_quality_score,
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "nifty100.db"

RADAR_DIR = (
    PROJECT_ROOT
    / "reports"
    / "radar_charts"
)


# ============================================================
# RADAR METRICS
# ============================================================

RADAR_METRICS = [
    "ROE",
    "ROCE",
    "NPM",
    "D/E",
    "FCF Score",
    "PAT CAGR 5yr",
    "Revenue CAGR 5yr",
    "Composite Score",
]


# ============================================================
# HELPERS
# ============================================================

def _numeric(series):
    return pd.to_numeric(
        series,
        errors="coerce",
    )


def _safe_number(value):
    try:
        value = float(value)

        if np.isnan(value):
            return 0.0

        return value

    except (TypeError, ValueError):
        return 0.0


def _normalise_series(series):
    """
    Normalize one metric to 0–100.

    Uses P10/P90 clipping.
    """

    values = _numeric(series)

    valid = values.dropna()

    if valid.empty:
        return pd.Series(
            0.0,
            index=series.index,
        )

    p10 = valid.quantile(0.10)
    p90 = valid.quantile(0.90)

    if (
        pd.isna(p10)
        or pd.isna(p90)
        or p90 <= p10
    ):
        result = pd.Series(
            50.0,
            index=series.index,
        )

        result[values.isna()] = 0.0

        return result

    clipped = values.clip(
        lower=p10,
        upper=p90,
    )

    result = (
        (clipped - p10)
        / (p90 - p10)
    ) * 100.0

    return result.fillna(0.0)


def _inverse_normalise_series(series):
    """Normalize with lower values treated as better."""

    result = _normalise_series(
        series
    )

    return 100.0 - result


# ============================================================
# LOAD PEER INFORMATION
# ============================================================

def load_peer_information():
    """
    Load peer group membership from peer_groups.xlsx.
    """

    path = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "peer_groups.xlsx"
    )

    peer = pd.read_excel(
        path
    )

    peer["company_id"] = (
        peer["company_id"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    peer["peer_group_name"] = (
        peer["peer_group_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return peer[
        [
            "company_id",
            "peer_group_name",
        ]
    ].copy()


# ============================================================
# LOAD FINANCIAL DATA
# ============================================================

def load_radar_data():
    """
    Load screener data and calculate composite score.
    """

    df = load_screener_data()

    df = add_composite_quality_score(
        df
    )

    df["company_id"] = (
        df["ticker"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df


# ============================================================
# PREPARE RADAR METRICS
# ============================================================

def prepare_radar_metrics(df):
    """
    Create normalized 0–100 values for the eight radar axes.
    """

    result = df.copy()

    # --------------------------------------------------------
    # ROE
    # --------------------------------------------------------

    roe_column = (
        "return_on_equity_pct"
        if "return_on_equity_pct"
        in result.columns
        else "roe"
    )

    result["ROE"] = _normalise_series(
        result[roe_column]
    )

    # --------------------------------------------------------
    # ROCE
    # --------------------------------------------------------

    roce_column = None

    for column in [
        "return_on_capital_employed_pct",
        "roce_percentage",
        "roce",
    ]:

        if column in result.columns:
            roce_column = column
            break

    if roce_column is not None:
        result["ROCE"] = _normalise_series(
            result[roce_column]
        )
    else:
        result["ROCE"] = 0.0

    # --------------------------------------------------------
    # NPM
    # --------------------------------------------------------

    npm_column = None

    for column in [
        "net_profit_margin_pct",
        "net_margin_pct",
    ]:

        if column in result.columns:
            npm_column = column
            break

    if npm_column is not None:
        result["NPM"] = _normalise_series(
            result[npm_column]
        )
    else:
        result["NPM"] = 0.0

    # --------------------------------------------------------
    # D/E — inverse
    # --------------------------------------------------------

    if "debt_to_equity" in result.columns:
        result["D/E"] = _inverse_normalise_series(
            result["debt_to_equity"]
        )
    else:
        result["D/E"] = 0.0

    # --------------------------------------------------------
    # FCF Score
    # --------------------------------------------------------

    fcf_column = None

    for column in [
        "free_cash_flow_cr",
        "free_cash_flow",
    ]:

        if column in result.columns:
            fcf_column = column
            break

    if fcf_column is not None:
        result["FCF Score"] = _normalise_series(
            result[fcf_column]
        )
    else:
        result["FCF Score"] = 0.0

    # --------------------------------------------------------
    # PAT CAGR
    # --------------------------------------------------------

    if "pat_cagr_5yr" in result.columns:
        result["PAT CAGR 5yr"] = _normalise_series(
            result["pat_cagr_5yr"]
        )
    else:
        result["PAT CAGR 5yr"] = 0.0

    # --------------------------------------------------------
    # Revenue CAGR
    # --------------------------------------------------------

    if "revenue_cagr_5yr" in result.columns:
        result["Revenue CAGR 5yr"] = _normalise_series(
            result["revenue_cagr_5yr"]
        )
    else:
        result["Revenue CAGR 5yr"] = 0.0

    # --------------------------------------------------------
    # Composite Score
    # --------------------------------------------------------

    result["Composite Score"] = _normalise_series(
        result["composite_quality_score"]
    )

    return result


# ============================================================
# SINGLE RADAR CHART
# ============================================================

def create_radar_chart(
    company_row,
    peer_group_df,
    filename,
):
    """
    Create one company-vs-peer-average radar chart.
    """

    labels = RADAR_METRICS

    company_values = [
        _safe_number(
            company_row[label]
        )
        for label in labels
    ]

    peer_average = [
        _safe_number(
            peer_group_df[label].mean()
        )
        for label in labels
    ]

    number_of_axes = len(labels)

    angles = np.linspace(
        0,
        2 * np.pi,
        number_of_axes,
        endpoint=False,
    ).tolist()

    # Close polygons.
    company_values += company_values[:1]
    peer_average += peer_average[:1]

    angles += angles[:1]

    fig = plt.figure(
        figsize=(8, 8)
    )

    ax = fig.add_subplot(
        111,
        polar=True,
    )

    # Company
    ax.plot(
        angles,
        company_values,
        linewidth=2,
        label=str(
            company_row["ticker"]
        ),
    )

    ax.fill(
        angles,
        company_values,
        alpha=0.20,
    )

    # Peer average
    ax.plot(
        angles,
        peer_average,
        linestyle="--",
        linewidth=2,
        label="Peer Average",
    )

    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        labels,
        fontsize=10,
    )

    ax.set_ylim(
        0,
        100,
    )

    ax.set_yticks(
        [20, 40, 60, 80, 100]
    )

    ax.set_yticklabels(
        [
            "20",
            "40",
            "60",
            "80",
            "100",
        ],
        fontsize=8,
    )

    company_name = str(
        company_row.get(
            "company_name",
            company_row["ticker"],
        )
    )

    peer_group_name = str(
        company_row.get(
            "peer_group_name",
            "Peer Group",
        )
    )

    ax.set_title(
        f"{company_name}\n"
        f"Peer Group: {peer_group_name}",
        fontsize=13,
        pad=25,
    )

    ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.25, 1.10),
    )

    fig.tight_layout()

    fig.savefig(
        filename,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close(fig)


# ============================================================
# NO-PEER STANDALONE CHART
# ============================================================

def create_standalone_chart(
    company_row,
    all_companies,
    filename,
):
    """
    Create a standalone radar chart for a company
    without an assigned peer group.

    Nifty 100 average is used as reference.
    """

    labels = RADAR_METRICS

    company_values = [
        _safe_number(
            company_row[label]
        )
        for label in labels
    ]

    nifty_average = [
        _safe_number(
            all_companies[label].mean()
        )
        for label in labels
    ]

    number_of_axes = len(labels)

    angles = np.linspace(
        0,
        2 * np.pi,
        number_of_axes,
        endpoint=False,
    ).tolist()

    company_values += company_values[:1]
    nifty_average += nifty_average[:1]

    angles += angles[:1]

    fig = plt.figure(
        figsize=(8, 8)
    )

    ax = fig.add_subplot(
        111,
        polar=True,
    )

    ax.plot(
        angles,
        company_values,
        linewidth=2,
        label=str(
            company_row["ticker"]
        ),
    )

    ax.fill(
        angles,
        company_values,
        alpha=0.20,
    )

    ax.plot(
        angles,
        nifty_average,
        linestyle="--",
        linewidth=2,
        label="Nifty 100 Average",
    )

    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        labels,
        fontsize=10,
    )

    ax.set_ylim(
        0,
        100,
    )

    ax.set_yticks(
        [20, 40, 60, 80, 100]
    )

    ax.set_yticklabels(
        [
            "20",
            "40",
            "60",
            "80",
            "100",
        ],
        fontsize=8,
    )

    company_name = str(
        company_row.get(
            "company_name",
            company_row["ticker"],
        )
    )

    ax.set_title(
        f"{company_name}\n"
        f"No Peer Group Assigned",
        fontsize=13,
        pad=25,
    )

    ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.25, 1.10),
    )

    fig.tight_layout()

    fig.savefig(
        filename,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close(fig)


# ============================================================
# GENERATE ALL RADAR CHARTS
# ============================================================

def generate_radar_charts():
    """
    Generate radar chart for every company.

    Peer-group companies:
        company polygon + peer-average overlay

    Unassigned companies:
        company polygon + Nifty 100 average
    """

    RADAR_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    financial = load_radar_data()

    financial = prepare_radar_metrics(
        financial
    )

    peer_groups = load_peer_information()

    # Match ticker/company IDs.
    financial["company_id"] = (
        financial["company_id"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    peer_groups["company_id"] = (
        peer_groups["company_id"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    data = financial.merge(
        peer_groups,
        on="company_id",
        how="left",
    )

    data["peer_group_name"] = (
        data["peer_group_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    created = []

    # --------------------------------------------------------
    # Companies with peer group
    # --------------------------------------------------------

    assigned = data[
        data["peer_group_name"] != ""
    ].copy()

    for peer_group_name, group in assigned.groupby(
        "peer_group_name"
    ):

        for _, company in group.iterrows():

            ticker = str(
                company["ticker"]
            ).strip()

            if not ticker:
                continue

            filename = (
                RADAR_DIR
                / f"{ticker}_radar.png"
            )

            create_radar_chart(
                company,
                group,
                filename,
            )

            created.append(
                filename
            )

    # --------------------------------------------------------
    # Companies without peer group
    # --------------------------------------------------------

    unassigned = data[
        data["peer_group_name"] == ""
    ].copy()

    for _, company in unassigned.iterrows():

        ticker = str(
            company["ticker"]
        ).strip()

        if not ticker:
            continue

        filename = (
            RADAR_DIR
            / f"{ticker}_radar.png"
        )

        create_standalone_chart(
            company,
            data,
            filename,
        )

        created.append(
            filename
        )

    return created


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    charts = generate_radar_charts()

    print(
        "RADAR CHART GENERATION COMPLETE"
    )

    print(
        f"CHARTS CREATED: {len(charts)}"
    )

    if charts:

        print(
            "FIRST CHART:",
            charts[0],
        )