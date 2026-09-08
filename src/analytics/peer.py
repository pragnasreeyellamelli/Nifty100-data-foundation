from pathlib import Path
import sqlite3

import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "nifty100.db"
PEER_GROUPS_PATH = (
    PROJECT_ROOT / "data" / "raw" / "peer_groups.xlsx"
)


# ============================================================
# HELPERS
# ============================================================

def _norm(value):
    """Normalize text for flexible column matching."""
    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
    )


def _find_column(df, candidates):
    """Find the first matching column."""
    lookup = {
        _norm(column): column
        for column in df.columns
    }

    for candidate in candidates:
        key = _norm(candidate)

        if key in lookup:
            return lookup[key]

    return None


def _numeric(series):
    return pd.to_numeric(
        series,
        errors="coerce",
    )


def _year_number(series):
    return pd.to_numeric(
        series.astype(str)
        .str.extract(r"(\d{4})$")[0],
        errors="coerce",
    )


def _latest_annual(df):
    """Keep the latest non-TTM row per ticker."""

    result = df.copy()

    if "year" not in result.columns:
        return result

    result = result[
        ~result["year"]
        .astype(str)
        .str.strip()
        .str.upper()
        .eq("TTM")
    ].copy()

    result["_year_num"] = _year_number(
        result["year"]
    )

    result = result.sort_values(
        ["company_id", "_year_num"],
        ascending=[True, False],
        kind="stable",
    )

    result = result.drop_duplicates(
        subset=["company_id"],
        keep="first",
    )

    return result.drop(
        columns="_year_num",
        errors="ignore",
    )


# ============================================================
# LOAD PEER GROUPS
# ============================================================

def load_peer_groups():
    """
    Load peer_groups.xlsx.

    Actual source structure:
        id
        peer_group_name
        company_id   -> ticker
        is_benchmark
    """

    peer = pd.read_excel(
        PEER_GROUPS_PATH,
        header=0,
    )

    group_col = _find_column(
        peer,
        [
            "peer_group_name",
            "peer_group",
            "group",
            "group_name",
        ],
    )

    company_col = _find_column(
        peer,
        [
            "company_id",
            "ticker",
            "symbol",
        ],
    )

    benchmark_col = _find_column(
        peer,
        [
            "is_benchmark",
            "benchmark",
        ],
    )

    if group_col is None:
        raise ValueError(
            "peer_groups.xlsx does not contain "
            "peer_group_name."
        )

    if company_col is None:
        raise ValueError(
            "peer_groups.xlsx does not contain "
            "company_id/ticker."
        )

    result = pd.DataFrame()

    # IMPORTANT:
    # company_id in peer_groups.xlsx is a TICKER,
    # not a numeric database ID.
    result["company_id"] = (
        peer[company_col]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    result["peer_group_name"] = (
        peer[group_col]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    if benchmark_col is not None:
        result["is_benchmark"] = (
            peer[benchmark_col]
            .fillna(False)
            .astype(bool)
        )
    else:
        result["is_benchmark"] = False

    result = result[
        (result["company_id"] != "")
        & (result["peer_group_name"] != "")
    ].copy()

    return result.reset_index(
        drop=True
    )


# ============================================================
# LOAD FINANCIAL METRICS
# ============================================================

def load_peer_metrics():
    """
    Load latest financial ratios.

    In this project financial_ratios.company_id
    contains ticker symbols such as ABB, HDFCBANK, etc.
    """

    with sqlite3.connect(DB_PATH) as conn:

        ratios = pd.read_sql_query(
            """
            SELECT *
            FROM financial_ratios
            """,
            conn,
        )

    ratios["company_id"] = (
        ratios["company_id"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    ratios = _latest_annual(
        ratios
    )

    return ratios.reset_index(
        drop=True
    )


# ============================================================
# ADD CAGR METRICS
# ============================================================

def add_cagr_metrics(df):
    """
    Calculate 5-year Revenue, PAT and EPS CAGR
    from historical profit_and_loss data.
    """

    result = df.copy()

    with sqlite3.connect(DB_PATH) as conn:

        pnl = pd.read_sql_query(
            """
            SELECT
                company_id,
                year,
                sales,
                net_profit,
                eps
            FROM profit_and_loss
            """,
            conn,
        )

    pnl["company_id"] = (
        pnl["company_id"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    pnl = pnl[
        ~pnl["year"]
        .astype(str)
        .str.upper()
        .eq("TTM")
    ].copy()

    pnl["_year"] = _year_number(
        pnl["year"]
    )

    for column in [
        "sales",
        "net_profit",
        "eps",
    ]:
        pnl[column] = _numeric(
            pnl[column]
        )

    rows = []

    for company_id, group in pnl.groupby(
        "company_id"
    ):

        group = group.dropna(
            subset=["_year"]
        ).sort_values(
            "_year"
        )

        if group.empty:
            continue

        latest_year = int(
            group["_year"].max()
        )

        latest_rows = group[
            group["_year"] == latest_year
        ]

        previous_rows = group[
            group["_year"] == latest_year - 5
        ]

        if (
            latest_rows.empty
            or previous_rows.empty
        ):
            continue

        latest = latest_rows.iloc[-1]
        previous = previous_rows.iloc[-1]

        def cagr(start, end):
            if (
                pd.isna(start)
                or pd.isna(end)
                or start <= 0
                or end <= 0
            ):
                return pd.NA

            return (
                (
                    end / start
                ) ** (1 / 5)
                - 1
            ) * 100

        rows.append(
            {
                "company_id": company_id,
                "revenue_cagr_5yr": cagr(
                    previous["sales"],
                    latest["sales"],
                ),
                "pat_cagr_5yr": cagr(
                    previous["net_profit"],
                    latest["net_profit"],
                ),
                "eps_cagr_5yr": cagr(
                    previous["eps"],
                    latest["eps"],
                ),
            }
        )

    if not rows:
        return result.assign(
            revenue_cagr_5yr=pd.NA,
            pat_cagr_5yr=pd.NA,
            eps_cagr_5yr=pd.NA,
        )

    cagr_df = pd.DataFrame(
        rows
    )

    return result.merge(
        cagr_df,
        on="company_id",
        how="left",
    )


# ============================================================
# METRIC MAP
# ============================================================

METRICS = {
    "ROE": [
        "return_on_equity_pct",
        "roe",
    ],

    "ROCE": [
        "return_on_capital_employed_pct",
        "roce_percentage",
        "roce",
    ],

    "Net Profit Margin": [
        "net_profit_margin_pct",
        "net_margin_pct",
    ],

    "D/E": [
        "debt_to_equity",
    ],

    "FCF": [
        "free_cash_flow_cr",
        "free_cash_flow",
    ],

    "PAT CAGR 5yr": [
        "pat_cagr_5yr",
    ],

    "Revenue CAGR 5yr": [
        "revenue_cagr_5yr",
    ],

    "EPS CAGR 5yr": [
        "eps_cagr_5yr",
    ],

    "Interest Coverage": [
        "interest_coverage",
        "interest_coverage_ratio",
    ],

    "Asset Turnover": [
        "asset_turnover",
    ],
}


# ============================================================
# PERCENT RANK
# ============================================================

def _percent_rank(values):
    """
    Excel-style PERCENT_RANK equivalent.

    Returns values from 0 to 100.
    """

    numeric_values = pd.to_numeric(
        values,
        errors="coerce",
    )

    if numeric_values.notna().sum() == 0:
        return pd.Series(
            pd.NA,
            index=values.index,
        )

    if numeric_values.notna().sum() == 1:
        output = pd.Series(
            pd.NA,
            index=values.index,
            dtype=float,
        )

        only_index = (
            numeric_values.dropna()
            .index[0]
        )

        output.loc[
            only_index
        ] = 100.0

        return output

    ranks = (
        numeric_values
        .rank(
            method="min",
            ascending=True,
        )
    )

    n = numeric_values.notna().sum()

    return (
        (ranks - 1)
        / (n - 1)
    ) * 100.0


# ============================================================
# COMPUTE PEER PERCENTILES
# ============================================================

def compute_peer_percentiles():

    peer_groups = load_peer_groups()

    financial = load_peer_metrics()

    financial = add_cagr_metrics(
        financial
    )

    # Ensure ticker/company IDs match.
    peer_groups["company_id"] = (
        peer_groups["company_id"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    financial["company_id"] = (
        financial["company_id"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # --------------------------------------------------------
    # Join peer groups to financial data
    # --------------------------------------------------------

    merged = peer_groups.merge(
        financial,
        on="company_id",
        how="left",
        suffixes=(
            "_peer",
            "",
        ),
    )

    rows = []

    # --------------------------------------------------------
    # Calculate percentile for every peer group
    # --------------------------------------------------------

    for peer_group_name, group in merged.groupby(
        "peer_group_name"
    ):

        for metric_name, candidates in METRICS.items():

            column = None

            for candidate in candidates:

                if candidate in group.columns:
                    column = candidate
                    break

            if column is None:
                continue

            values = _numeric(
                group[column]
            )

            percentile = _percent_rank(
                values
            )

            # D/E: inverse percentile.
            # Lower D/E = higher percentile.
            if metric_name == "D/E":
                percentile = percentile.apply(
                    lambda value:
                        (
                            100.0 - value
                            if pd.notna(value)
                            else pd.NA
                        )
                )

            for index, row in group.iterrows():

                value = _numeric(
                    pd.Series(
                        [row[column]]
                    )
                ).iloc[0]

                rank_value = percentile.loc[
                    index
                ]

                rows.append(
                    {
                        "company_id":
                            row["company_id"],
                        "peer_group_name":
                            peer_group_name,
                        "metric":
                            metric_name,
                        "value":
                            value,
                        "percentile_rank":
                            rank_value,
                        "year":
                            row.get(
                                "year"
                            ),
                    }
                )

    result = pd.DataFrame(
        rows,
        columns=[
            "company_id",
            "peer_group_name",
            "metric",
            "value",
            "percentile_rank",
            "year",
        ],
    )

    # --------------------------------------------------------
    # Companies with no peer group
    # --------------------------------------------------------

    assigned_companies = set(
        peer_groups[
            "company_id"
        ]
        .tolist()
    )

    all_companies = set(
        financial[
            "company_id"
        ]
        .dropna()
        .tolist()
    )

    unassigned = (
        all_companies
        - assigned_companies
    )

    if unassigned:

        no_group_rows = pd.DataFrame(
            [
                {
                    "company_id": company_id,
                    "peer_group_name":
                        "No peer group assigned",
                    "metric":
                        "No peer group assigned",
                    "value": pd.NA,
                    "percentile_rank": pd.NA,
                    "year": None,
                }
                for company_id
                in sorted(unassigned)
            ]
        )

        result = pd.concat(
            [
                result,
                no_group_rows,
            ],
            ignore_index=True,
        )

    return result


# ============================================================
# SAVE TO SQLITE
# ============================================================

def save_peer_percentiles(df):

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS peer_percentiles (
                company_id TEXT,
                peer_group_name TEXT,
                metric TEXT,
                value REAL,
                percentile_rank REAL,
                year TEXT
            )
            """
        )

        conn.execute(
            "DELETE FROM peer_percentiles"
        )

        df.to_sql(
            "peer_percentiles",
            conn,
            if_exists="append",
            index=False,
        )

        conn.commit()


# ============================================================
# MAIN FUNCTION
# ============================================================

def build_peer_percentiles():

    result = compute_peer_percentiles()

    save_peer_percentiles(
        result
    )

    return result


if __name__ == "__main__":

    result = build_peer_percentiles()

    print(
        "PEER PERCENTILES CREATED"
    )

    print(
        "ROWS:",
        len(result),
    )

    print(
        "PEER GROUPS:",
        result[
            "peer_group_name"
        ].nunique(),
    )

    print(
        "METRICS:",
        result[
            "metric"
        ].nunique(),
    )

    print(
        result.head(20).to_string(
            index=False
        )
    )