from pathlib import Path
import re
import sqlite3

import pandas as pd
import yaml


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "nifty100.db"
CONFIG_PATH = PROJECT_ROOT / "config" / "screener_config.yaml"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

FINANCIAL_RATIOS_PATH = RAW_DIR / "financial_ratios.xlsx"
PNL_PATH = RAW_DIR / "profitandloss.xlsx"
MARKET_CAP_PATH = RAW_DIR / "market_cap.xlsx"
COMPANIES_PATH = RAW_DIR / "companies.xlsx"


# ============================================================
# CONFIGURATION
# ============================================================

def load_screener_config(config_path=CONFIG_PATH):
    """Load analyst-editable screener configuration."""
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


# ============================================================
# GENERAL HELPERS
# ============================================================

def _norm(value):
    """Normalize names for flexible column matching."""
    return re.sub(
        r"[^a-z0-9]",
        "",
        str(value).strip().lower(),
    )


def _find_column(df, names):
    """Find the first matching DataFrame column."""
    lookup = {
        _norm(column): column
        for column in df.columns
    }

    for name in names:
        key = _norm(name)

        if key in lookup:
            return lookup[key]

    return None


def _numeric(series):
    """Safely convert a Series to numeric."""
    return pd.to_numeric(
        series,
        errors="coerce",
    )


def _year_number(series):
    """Extract 4-digit year from values such as 'Sep 2024'."""
    return pd.to_numeric(
        series.astype(str)
        .str.extract(r"(\d{4})$")[0],
        errors="coerce",
    )


def _read_excel(path, headers=(0, 1, 2, 3)):
    """
    Read Excel using the header row that best matches
    the expected dataset structure.
    """

    best_df = None
    best_score = -1

    useful = {
        "id",
        "companyid",
        "ticker",
        "year",
        "sales",
        "netprofit",
        "returnonequitypct",
        "debtequity",
        "marketcap",
        "marketcapcrore",
        "companyname",
        "name",
        "sector",
    }

    for header in headers:

        try:
            df = pd.read_excel(
                path,
                header=header,
            )
        except Exception:
            continue

        score = sum(
            _norm(column) in useful
            for column in df.columns
        )

        if score > best_score:
            best_score = score
            best_df = df

    if best_df is None:
        raise ValueError(
            f"Could not read Excel file: {path}"
        )

    return best_df


def _latest_annual(
    df,
    key_col,
    year_col,
):
    """Keep latest non-TTM observation per company/ticker."""

    if year_col not in df.columns:
        return df.copy()

    result = df.copy()

    result = result[
        ~result[year_col]
        .astype(str)
        .str.strip()
        .str.upper()
        .eq("TTM")
    ].copy()

    result["_year_num"] = _year_number(
        result[year_col]
    )

    result = result.sort_values(
        [key_col, "_year_num"],
        ascending=[True, False],
        kind="stable",
    )

    result = result.drop_duplicates(
        subset=[key_col],
        keep="first",
    )

    return result.drop(
        columns="_year_num",
        errors="ignore",
    )


def _extract_ticker(value):
    """Extract ticker from common URL formats."""

    if pd.isna(value):
        return None

    text = str(value).strip()

    patterns = (
        r"[?&]symbol=NSE(?:%3A|:)([A-Za-z0-9&.\-_]+)",
        r"[?&]symbol=([A-Za-z0-9&.\-_]+)",
    )

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1).upper()

    return None


def _calculate_cagr(
    start_value,
    end_value,
    years,
):
    """Calculate CAGR percentage safely."""

    if (
        pd.isna(start_value)
        or pd.isna(end_value)
        or start_value <= 0
        or end_value <= 0
        or years <= 0
    ):
        return pd.NA

    return (
        (
            (end_value / start_value)
            ** (1 / years)
        )
        - 1
    ) * 100


# ============================================================
# COMPANY INFORMATION
# ============================================================

def load_company_info():
    """Load company metadata and attach sector when possible."""

    companies = _read_excel(
        COMPANIES_PATH,
        headers=(1, 0, 2, 3),
    )

    id_col = _find_column(
        companies,
        (
            "id",
            "company_id",
            "companyid",
            "serial_no",
            "sr_no",
        ),
    )

    if id_col is None:

        for column in companies.columns:

            values = pd.to_numeric(
                companies[column],
                errors="coerce",
            )

            if (
                len(values) > 0
                and values.notna().mean() >= 0.80
            ):
                id_col = column
                break

    name_col = _find_column(
        companies,
        (
            "company_name",
            "companyname",
            "name",
            "company",
        ),
    )

    ticker_col = _find_column(
        companies,
        (
            "ticker",
            "symbol",
            "nse_symbol",
            "stock_symbol",
        ),
    )

    if ticker_col is not None:

        ticker = (
            companies[ticker_col]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )

    else:

        ticker = companies.apply(
            lambda row: next(
                (
                    ticker_value
                    for value in row
                    for ticker_value in [
                        _extract_ticker(value)
                    ]
                    if ticker_value
                ),
                None,
            ),
            axis=1,
        )

    result = pd.DataFrame(
        index=companies.index
    )

    if id_col is not None:

        result["company_id"] = pd.to_numeric(
            companies[id_col],
            errors="coerce",
        )

    else:

        result["company_id"] = pd.NA

    if name_col is not None:

        result["company_name"] = (
            companies[name_col]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    else:

        result["company_name"] = ""

    result["ticker"] = ticker
    result["sector"] = pd.NA

    result = result[
        ~result["ticker"].isin(
            {
                "",
                "NAN",
                "NONE",
            }
        )
    ].copy()

    result["company_id"] = result[
        "company_id"
    ].astype("Int64")

    try:

        with sqlite3.connect(DB_PATH) as conn:

            db_companies = pd.read_sql_query(
                """
                SELECT
                    company_id,
                    sector
                FROM companies
                """,
                conn,
            )

        db_companies["company_id"] = (
            pd.to_numeric(
                db_companies["company_id"],
                errors="coerce",
            ).astype("Int64")
        )

        result = result.merge(
            db_companies,
            on="company_id",
            how="left",
            suffixes=("", "_db"),
        )

        if "sector_db" in result.columns:

            result["sector"] = (
                result["sector"]
                .fillna(
                    result["sector_db"]
                )
            )

            result = result.drop(
                columns=["sector_db"],
                errors="ignore",
            )

    except Exception:
        pass

    return result.reset_index(
        drop=True
    )


# ============================================================
# HISTORICAL 5-YEAR CAGR
# ============================================================

def _calculate_historical_cagrs():
    """
    Calculate Revenue CAGR, PAT CAGR and EPS CAGR
    directly from historical profit_and_loss data.
    """

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

    pnl = pnl.rename(
        columns={
            "company_id": "ticker"
        }
    )

    pnl["ticker"] = (
        pnl["ticker"]
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

    pnl["sales"] = _numeric(
        pnl["sales"]
    )

    pnl["net_profit"] = _numeric(
        pnl["net_profit"]
    )

    pnl["eps"] = _numeric(
        pnl["eps"]
    )

    rows = []

    for ticker, group in pnl.groupby(
        "ticker"
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

        if latest_rows.empty:
            continue

        latest = latest_rows.iloc[-1]

        previous_year = latest_year - 5

        previous_rows = group[
            group["_year"] == previous_year
        ]

        if previous_rows.empty:
            continue

        previous = previous_rows.iloc[-1]

        rows.append(
            {
                "ticker": ticker,
                "revenue_cagr_5yr": _calculate_cagr(
                    previous["sales"],
                    latest["sales"],
                    5,
                ),
                "pat_cagr_5yr": _calculate_cagr(
                    previous["net_profit"],
                    latest["net_profit"],
                    5,
                ),
                "eps_cagr_5yr": _calculate_cagr(
                    previous["eps"],
                    latest["eps"],
                    5,
                ),
            }
        )

    if not rows:

        return pd.DataFrame(
            columns=[
                "ticker",
                "revenue_cagr_5yr",
                "pat_cagr_5yr",
                "eps_cagr_5yr",
            ]
        )

    return pd.DataFrame(
        rows
    )


# ============================================================
# LOAD SCREENER DATA
# ============================================================

def load_screener_data():
    """Build latest annual screener DataFrame."""

    company_info = load_company_info()

    # --------------------------------------------------------
    # Financial ratios
    # --------------------------------------------------------

    ratios = _read_excel(
        FINANCIAL_RATIOS_PATH,
        headers=(0, 1, 2),
    )

    ratio_id = _find_column(
        ratios,
        (
            "company_id",
            "ticker",
        ),
    )

    if ratio_id is None:
        raise ValueError(
            "financial_ratios.xlsx has no company/ticker column."
        )

    ratios = ratios.rename(
        columns={
            ratio_id: "ticker"
        }
    )

    ratio_year = _find_column(
        ratios,
        (
            "year",
            "financial_year",
            "fy",
        ),
    )

    if ratio_year is None:
        raise ValueError(
            "financial_ratios.xlsx has no year column."
        )

    ratios = ratios.rename(
        columns={
            ratio_year: "year"
        }
    )

    ratios["ticker"] = (
        ratios["ticker"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    ratios = _latest_annual(
        ratios,
        "ticker",
        "year",
    )

    # --------------------------------------------------------
    # Profit & Loss
    # --------------------------------------------------------

    pnl = _read_excel(
        PNL_PATH,
        headers=(0, 1, 2),
    )

    pnl_id = _find_column(
        pnl,
        (
            "company_id",
            "ticker",
        ),
    )

    if pnl_id is None:
        raise ValueError(
            "profitandloss.xlsx has no company/ticker column."
        )

    pnl = pnl.rename(
        columns={
            pnl_id: "ticker"
        }
    )

    pnl["ticker"] = (
        pnl["ticker"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    pnl_year = _find_column(
        pnl,
        (
            "year",
            "financial_year",
            "fy",
        ),
    )

    if pnl_year is not None:

        pnl = pnl.rename(
            columns={
                pnl_year: "year"
            }
        )

        pnl = _latest_annual(
            pnl,
            "ticker",
            "year",
        )

    pnl_renames = {}

    sales_col = _find_column(
        pnl,
        (
            "sales",
            "revenue",
        ),
    )

    if (
        sales_col
        and sales_col != "sales"
    ):
        pnl_renames[
            sales_col
        ] = "sales"

    profit_col = _find_column(
        pnl,
        (
            "net_profit",
            "profit_after_tax",
            "profit",
        ),
    )

    if (
        profit_col
        and profit_col != "net_profit"
    ):
        pnl_renames[
            profit_col
        ] = "net_profit"

    eps_col = _find_column(
        pnl,
        (
            "eps",
            "earnings_per_share",
        ),
    )

    if (
        eps_col
        and eps_col != "eps"
    ):
        pnl_renames[
            eps_col
        ] = "eps"

    payout_col = _find_column(
        pnl,
        (
            "dividend_payout",
            "dividend_payout_ratio",
        ),
    )

    if (
        payout_col
        and payout_col
        != "dividend_payout"
    ):
        pnl_renames[
            payout_col
        ] = "dividend_payout"

    pnl = pnl.rename(
        columns=pnl_renames
    )

    pnl = pnl[
        [
            column
            for column in (
                "ticker",
                "year",
                "sales",
                "net_profit",
                "eps",
                "dividend_payout",
            )
            if column in pnl.columns
        ]
    ].copy()

    # --------------------------------------------------------
    # Market Cap
    # --------------------------------------------------------

    market = _read_excel(
        MARKET_CAP_PATH,
        headers=(0, 1, 2),
    )

    market_id = _find_column(
        market,
        (
            "company_id",
            "ticker",
        ),
    )

    if market_id is None:
        raise ValueError(
            "market_cap.xlsx has no company/ticker column."
        )

    market = market.rename(
        columns={
            market_id: "ticker"
        }
    )

    market["ticker"] = (
        market["ticker"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    market_year = _find_column(
        market,
        (
            "year",
            "date",
            "financial_year",
        ),
    )

    if market_year is not None:

        market = market.rename(
            columns={
                market_year: "year"
            }
        )

        market = _latest_annual(
            market,
            "ticker",
            "year",
        )

    market_value = _find_column(
        market,
        (
            "market_cap",
            "market_cap_crore",
            "market_cap_cr",
        ),
    )

    if market_value is not None:

        market = market.rename(
            columns={
                market_value: "market_cap"
            }
        )

    market = market[
        [
            column
            for column in (
                "ticker",
                "market_cap",
                "pe_ratio",
                "pb_ratio",
                "dividend_yield_pct",
            )
            if column in market.columns
        ]
    ].copy()

    # --------------------------------------------------------
    # Merge
    # --------------------------------------------------------

    result = ratios.merge(
        company_info[
            [
                "company_id",
                "company_name",
                "ticker",
                "sector",
            ]
        ],
        on="ticker",
        how="left",
    )

    result = result.merge(
        pnl,
        on="ticker",
        how="left",
        suffixes=("", "_pnl"),
    )

    result = result.merge(
        market,
        on="ticker",
        how="left",
        suffixes=("", "_market"),
    )

    # --------------------------------------------------------
    # Historical CAGR
    # --------------------------------------------------------

    try:

        cagrs = _calculate_historical_cagrs()

        result = result.merge(
            cagrs,
            on="ticker",
            how="left",
            suffixes=("", "_calculated"),
        )

        for column in (
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "eps_cagr_5yr",
        ):

            calculated_column = (
                f"{column}_calculated"
            )

            if calculated_column in result.columns:

                if column in result.columns:

                    result[column] = (
                        result[column]
                        .fillna(
                            result[
                                calculated_column
                            ]
                        )
                    )

                    result = result.drop(
                        columns=[
                            calculated_column
                        ]
                    )

                else:

                    result = result.rename(
                        columns={
                            calculated_column:
                                column
                        }
                    )

    except Exception:
        pass

    # --------------------------------------------------------
    # Guarantee expected columns
    # --------------------------------------------------------

    for column in (
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
    ):

        if column not in result.columns:
            result[column] = pd.NA

    if (
        "composite_quality_score"
        not in result.columns
    ):
        result[
            "composite_quality_score"
        ] = 0.0

    if "company_id" not in result.columns:
        result["company_id"] = pd.NA

    if (
        "company_name"
        not in result.columns
    ):
        result["company_name"] = ""

    if "sector" not in result.columns:
        result["sector"] = pd.NA

    return result.reset_index(
        drop=True
    )


# ============================================================
# FILTER HELPERS
# ============================================================

def _apply_min(
    df,
    column,
    threshold,
):
    """Apply a minimum threshold."""

    if (
        threshold is None
        or column not in df.columns
    ):
        return df

    values = _numeric(
        df[column]
    )

    return df.loc[
        values >= threshold
    ].copy()


def _apply_max(
    df,
    column,
    threshold,
):
    """Apply a maximum threshold."""

    if (
        threshold is None
        or column not in df.columns
    ):
        return df

    values = _numeric(
        df[column]
    )

    return df.loc[
        values <= threshold
    ].copy()


def _apply_de_max_excluding_financials(
    df,
    maximum,
):
    """
    Apply D/E maximum to non-Financials only.
    Financial companies are retained.
    """

    if (
        maximum is None
        or "debt_to_equity"
        not in df.columns
    ):
        return df

    if "sector" not in df.columns:

        return _apply_max(
            df,
            "debt_to_equity",
            maximum,
        )

    financials = (
        df["sector"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("financials")
    )

    financial_rows = df.loc[
        financials
    ].copy()

    other_rows = df.loc[
        ~financials
    ].copy()

    other_rows = _apply_max(
        other_rows,
        "debt_to_equity",
        maximum,
    )

    return pd.concat(
        [
            other_rows,
            financial_rows,
        ],
        ignore_index=True,
    )


# ============================================================
# DAY 15 — FILTER ENGINE
# ============================================================

def apply_filters(
    df,
    filters,
):
    """Apply all 15 Day-15 filters."""

    result = df.copy()

    roe_column = (
        "return_on_equity_pct"
        if (
            "return_on_equity_pct"
            in result.columns
        )
        else "roe"
    )

    result = _apply_min(
        result,
        roe_column,
        filters.get(
            "roe_min"
        ),
    )

    result = _apply_de_max_excluding_financials(
        result,
        filters.get(
            "de_max"
        ),
    )

    result = _apply_min(
        result,
        "free_cash_flow_cr",
        filters.get(
            "fcf_min"
        ),
    )

    result = _apply_min(
        result,
        "revenue_cagr_5yr",
        filters.get(
            "revenue_cagr_5yr_min"
        ),
    )

    result = _apply_min(
        result,
        "pat_cagr_5yr",
        filters.get(
            "pat_cagr_5yr_min"
        ),
    )

    result = _apply_min(
        result,
        "operating_profit_margin_pct",
        filters.get(
            "opm_min"
        ),
    )

    result = _apply_max(
        result,
        "pe_ratio",
        filters.get(
            "pe_max"
        ),
    )

    result = _apply_max(
        result,
        "pb_ratio",
        filters.get(
            "pb_max"
        ),
    )

    result = _apply_min(
        result,
        "dividend_yield_pct",
        filters.get(
            "dividend_yield_min"
        ),
    )

    # --------------------------------------------------------
    # ICR
    # --------------------------------------------------------

    icr_min = filters.get(
        "icr_min"
    )

    if (
        icr_min is not None
        and "interest_coverage"
        in result.columns
    ):

        icr = _numeric(
            result[
                "interest_coverage"
            ]
        )

        de = _numeric(
            result.get(
                "debt_to_equity",
                pd.Series(
                    index=result.index,
                    dtype=float,
                ),
            )
        )

        debt_free = (
            de.fillna(0)
            .eq(0)
        )

        text = (
            result[
                "interest_coverage"
            ]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        debt_free = (
            debt_free
            | text.eq(
                "debt free"
            )
        )

        icr = icr.mask(
            debt_free,
            float("inf"),
        )

        result = result.loc[
            icr >= icr_min
        ].copy()

    result = _apply_min(
        result,
        "market_cap",
        filters.get(
            "market_cap_min"
        ),
    )

    result = _apply_min(
        result,
        "net_profit",
        filters.get(
            "net_profit_min"
        ),
    )

    result = _apply_min(
        result,
        "eps_cagr_5yr",
        filters.get(
            "eps_cagr_min"
        ),
    )

    result = _apply_min(
        result,
        "asset_turnover",
        filters.get(
            "asset_turnover_min"
        ),
    )

    result = _apply_min(
        result,
        "sales",
        filters.get(
            "sales_min"
        ),
    )

    return result.reset_index(
        drop=True
    )


# ============================================================
# DAY 17 — COMPOSITE QUALITY SCORE
# ============================================================

def add_composite_quality_score(df):
    """
    Calculate Composite Quality Score from 0–100.

    Profitability 35%
      ROE 15%
      ROCE 10%
      NPM 10%

    Cash Quality 30%
      FCF CAGR 15%
      CFO/PAT 10%
      FCF positive 5%

    Growth 20%
      Revenue CAGR 10%
      PAT CAGR 10%

    Leverage 15%
      D/E 10%
      ICR 5%

    Metrics are winsorised at P10/P90 before scaling.
    Normalisation is performed within sector when available.
    """

    result = df.copy()

    # --------------------------------------------------------
    # Helper: locate columns
    # --------------------------------------------------------

    def first_column(candidates):

        for column in candidates:

            if column in result.columns:
                return column

        return None

    # --------------------------------------------------------
    # Winsorized normalisation
    # --------------------------------------------------------

    def normalise_metric(
        series,
        higher_is_better=True,
    ):

        values = pd.to_numeric(
            series,
            errors="coerce",
        )

        valid = values.dropna()

        if valid.empty:

            return pd.Series(
                0.0,
                index=series.index,
            )

        p10 = valid.quantile(
            0.10
        )

        p90 = valid.quantile(
            0.90
        )

        if (
            pd.isna(p10)
            or pd.isna(p90)
            or p90 <= p10
        ):

            score = pd.Series(
                50.0,
                index=series.index,
            )

            score[
                values.isna()
            ] = 0.0

            return score

        capped = values.clip(
            lower=p10,
            upper=p90,
        )

        score = (
            (
                capped - p10
            )
            / (
                p90 - p10
            )
        ) * 100.0

        if not higher_is_better:

            score = (
                100.0
                - score
            )

        return score.fillna(
            0.0
        )

    # --------------------------------------------------------
    # Sector column
    # --------------------------------------------------------

    sector_column = first_column(
        [
            "broad_sector",
            "sector",
        ]
    )

    if sector_column is None:

        result["_score_sector"] = "ALL"

    else:

        result["_score_sector"] = (
            result[
                sector_column
            ]
            .fillna("ALL")
            .astype(str)
        )

    # --------------------------------------------------------
    # Metric columns
    # --------------------------------------------------------

    roe_column = first_column(
        [
            "return_on_equity_pct",
            "roe",
        ]
    )

    roce_column = first_column(
        [
            "return_on_capital_employed_pct",
            "roce_percentage",
            "roce",
        ]
    )

    npm_column = first_column(
        [
            "net_profit_margin_pct",
            "net_margin_pct",
            "npm",
        ]
    )

    fcf_column = first_column(
        [
            "free_cash_flow_cr",
            "free_cash_flow",
        ]
    )

    revenue_cagr_column = first_column(
        [
            "revenue_cagr_5yr",
        ]
    )

    pat_cagr_column = first_column(
        [
            "pat_cagr_5yr",
        ]
    )

    de_column = first_column(
        [
            "debt_to_equity",
        ]
    )

    icr_column = first_column(
        [
            "interest_coverage",
            "interest_coverage_ratio",
        ]
    )

    cfo_column = first_column(
        [
            "cash_from_operations_cr",
            "cash_from_operations",
            "cfo",
        ]
    )

    profit_column = first_column(
        [
            "net_profit",
        ]
    )

    # --------------------------------------------------------
    # NPM if missing
    # --------------------------------------------------------

    if npm_column is None:

        sales_column = first_column(
            [
                "sales",
                "revenue",
            ]
        )

        if (
            sales_column is not None
            and profit_column is not None
        ):

            result[
                "_calculated_npm"
            ] = (
                _numeric(
                    result[
                        profit_column
                    ]
                )
                /
                _numeric(
                    result[
                        sales_column
                    ]
                ).replace(
                    0,
                    pd.NA,
                )
            ) * 100.0

            npm_column = (
                "_calculated_npm"
            )

    # --------------------------------------------------------
    # CFO / PAT
    # --------------------------------------------------------

    if (
        cfo_column is not None
        and profit_column is not None
    ):

        result[
            "_cfo_pat_ratio"
        ] = (
            _numeric(
                result[
                    cfo_column
                ]
            )
            /
            _numeric(
                result[
                    profit_column
                ]
            ).replace(
                0,
                pd.NA,
            )
        )

    else:

        result[
            "_cfo_pat_ratio"
        ] = pd.NA

    # --------------------------------------------------------
    # FCF positive flag
    # --------------------------------------------------------

    if fcf_column is not None:

        result[
            "_fcf_positive_flag"
        ] = (
            _numeric(
                result[
                    fcf_column
                ]
            ) > 0
        ).astype(float)

    else:

        result[
            "_fcf_positive_flag"
        ] = 0.0

    # --------------------------------------------------------
    # FCF CAGR 5yr
    # --------------------------------------------------------

    result[
        "_fcf_cagr_5yr"
    ] = pd.NA

    try:

        if "ticker" in result.columns:

            with sqlite3.connect(
                DB_PATH
            ) as conn:

                fcf_history = (
                    pd.read_sql_query(
                        """
                        SELECT
                            company_id,
                            year,
                            free_cash_flow_cr
                        FROM financial_ratios
                        """,
                        conn,
                    )
                )

            fcf_history = (
                fcf_history.rename(
                    columns={
                        "company_id":
                            "ticker"
                    }
                )
            )

            fcf_history[
                "ticker"
            ] = (
                fcf_history[
                    "ticker"
                ]
                .astype(str)
                .str.strip()
                .str.upper()
            )

            fcf_history[
                "_year"
            ] = _year_number(
                fcf_history[
                    "year"
                ]
            )

            fcf_history[
                "free_cash_flow_cr"
            ] = _numeric(
                fcf_history[
                    "free_cash_flow_cr"
                ]
            )

            fcf_rows = []

            for ticker, group in (
                fcf_history.groupby(
                    "ticker"
                )
            ):

                group = (
                    group.dropna(
                        subset=[
                            "_year",
                            "free_cash_flow_cr",
                        ]
                    )
                    .sort_values(
                        "_year"
                    )
                )

                if group.empty:
                    continue

                latest = group.iloc[
                    -1
                ]

                previous_year = (
                    latest[
                        "_year"
                    ] - 5
                )

                previous_rows = (
                    group[
                        group[
                            "_year"
                        ]
                        == previous_year
                    ]
                )

                if previous_rows.empty:
                    continue

                previous = (
                    previous_rows.iloc[
                        -1
                    ]
                )

                cagr = _calculate_cagr(
                    previous[
                        "free_cash_flow_cr"
                    ],
                    latest[
                        "free_cash_flow_cr"
                    ],
                    5,
                )

                if pd.notna(cagr):

                    fcf_rows.append(
                        {
                            "ticker": ticker,
                            "_fcf_cagr_5yr": cagr,
                        }
                    )

            if fcf_rows:

                fcf_cagr_df = (
                    pd.DataFrame(
                        fcf_rows
                    )
                )

                result = result.merge(
                    fcf_cagr_df,
                    on="ticker",
                    how="left",
                    suffixes=(
                        "",
                        "_calc",
                    ),
                )

                result[
                    "_fcf_cagr_5yr"
                ] = result[
                    "_fcf_cagr_5yr_calc"
                ]

                result = result.drop(
                    columns=[
                        "_fcf_cagr_5yr_calc"
                    ],
                    errors="ignore",
                )

    except Exception:
        pass

    # --------------------------------------------------------
    # Sector-relative scoring helper
    # --------------------------------------------------------

    def sector_relative_score(
        column,
        higher_is_better=True,
    ):

        if column is None:

            return pd.Series(
                0.0,
                index=result.index,
            )

        output = pd.Series(
            0.0,
            index=result.index,
            dtype=float,
        )

        for _, index_group in (
            result.groupby(
                "_score_sector"
            ).groups.items()
        ):

            group_values = result.loc[
                index_group,
                column,
            ]

            output.loc[
                index_group
            ] = normalise_metric(
                group_values,
                higher_is_better,
            )

        return output

    # --------------------------------------------------------
    # Profitability 35%
    # --------------------------------------------------------

    roe_score = (
        sector_relative_score(
            roe_column,
            higher_is_better=True,
        )
    )

    roce_score = (
        sector_relative_score(
            roce_column,
            higher_is_better=True,
        )
    )

    npm_score = (
        sector_relative_score(
            npm_column,
            higher_is_better=True,
        )
    )

    profitability_score = (
        roe_score * 0.15
        + roce_score * 0.10
        + npm_score * 0.10
    )

    # --------------------------------------------------------
    # Cash Quality 30%
    # --------------------------------------------------------

    fcf_cagr_score = (
        sector_relative_score(
            "_fcf_cagr_5yr",
            higher_is_better=True,
        )
    )

    cfo_pat_score = (
        sector_relative_score(
            "_cfo_pat_ratio",
            higher_is_better=True,
        )
    )

    fcf_positive_score = (
        result[
            "_fcf_positive_flag"
        ] * 100.0
    )

    cash_quality_score = (
        fcf_cagr_score * 0.15
        + cfo_pat_score * 0.10
        + fcf_positive_score * 0.05
    )

    # --------------------------------------------------------
    # Growth 20%
    # --------------------------------------------------------

    revenue_growth_score = (
        sector_relative_score(
            revenue_cagr_column,
            higher_is_better=True,
        )
    )

    pat_growth_score = (
        sector_relative_score(
            pat_cagr_column,
            higher_is_better=True,
        )
    )

    growth_score = (
        revenue_growth_score * 0.10
        + pat_growth_score * 0.10
    )

    # --------------------------------------------------------
    # Leverage 15%
    # --------------------------------------------------------

    de_score = (
        sector_relative_score(
            de_column,
            higher_is_better=False,
        )
    )

    icr_score = (
        sector_relative_score(
            icr_column,
            higher_is_better=True,
        )
    )

    leverage_score = (
        de_score * 0.10
        + icr_score * 0.05
    )

    # --------------------------------------------------------
    # Final 0–100 score
    # --------------------------------------------------------

    result[
        "profitability_score"
    ] = profitability_score.clip(
        0,
        35,
    )

    result[
        "cash_quality_score"
    ] = cash_quality_score.clip(
        0,
        30,
    )

    result[
        "growth_score"
    ] = growth_score.clip(
        0,
        20,
    )

    result[
        "leverage_score"
    ] = leverage_score.clip(
        0,
        15,
    )

    result[
        "composite_quality_score"
    ] = (
        result[
            "profitability_score"
        ]
        + result[
            "cash_quality_score"
        ]
        + result[
            "growth_score"
        ]
        + result[
            "leverage_score"
        ]
    ).clip(
        0,
        100,
    )

    result = result.drop(
        columns=[
            "_score_sector",
            "_calculated_npm",
            "_cfo_pat_ratio",
            "_fcf_positive_flag",
            "_fcf_cagr_5yr",
        ],
        errors="ignore",
    )

    return result


# ============================================================
# RUN SCREENER
# ============================================================

def run_screener(
    df,
    config_path=CONFIG_PATH,
):
    """Run configured Day-15 screener."""

    config = load_screener_config(
        config_path
    )

    filters = config.get(
        "filters",
        {},
    )

    settings = config.get(
        "settings",
        {},
    )

    result = apply_filters(
        df,
        filters,
    )

    result = add_composite_quality_score(
        result
    )

    sort_column = settings.get(
        "sort_by",
        "composite_quality_score",
    )

    ascending = settings.get(
        "sort_ascending",
        False,
    )

    if sort_column in result.columns:

        result = result.sort_values(
            sort_column,
            ascending=ascending,
            kind="stable",
        )

    return result.reset_index(
        drop=True
    )


def run_default_screener():
    """Load data and run configured screener."""

    return run_screener(
        load_screener_data()
    )


# ============================================================
# DAY 16 — SIX PRESET SCREENERS
# ============================================================

PRESET_SCREENERS = {

    "Quality Compounder": {
        "roe_min": 15.0,
        "de_max": 1.0,
        "fcf_min": 0.0,
        "revenue_cagr_5yr_min": 10.0,
    },

    "Value Pick": {
        "pe_max": 20.0,
        "pb_max": 3.0,
        "de_max": 2.0,
        "dividend_yield_min": 1.0,
    },

    "Growth Accelerator": {
        "pat_cagr_5yr_min": 20.0,
        "revenue_cagr_5yr_min": 15.0,
        "de_max": 2.0,
    },

    "Dividend Champion": {
        "dividend_yield_min": 2.0,
        "dividend_payout_max": 80.0,
        "fcf_min": 0.0,
    },

    "Debt-Free Blue Chip": {
        "de_max": 0.0,
        "roe_min": 12.0,
        "sales_min": 5000.0,
    },

    "Turnaround Watch": {
        "revenue_cagr_3yr_min": 10.0,
        "fcf_min": 0.0,
        "de_declining": True,
    },
}


# ============================================================
# TURNAROUND METRICS
# ============================================================

def _calculate_turnaround_metrics(df):
    """
    Calculate:
      Revenue CAGR 3yr
      D/E declining YoY
    """

    result = df.copy()

    result[
        "revenue_cagr_3yr"
    ] = pd.NA

    result[
        "de_declining"
    ] = False

    try:

        with sqlite3.connect(
            DB_PATH
        ) as conn:

            pnl = pd.read_sql_query(
                """
                SELECT
                    company_id,
                    year,
                    sales
                FROM profit_and_loss
                """,
                conn,
            )

            ratios = pd.read_sql_query(
                """
                SELECT
                    company_id,
                    year,
                    debt_to_equity
                FROM financial_ratios
                """,
                conn,
            )

        # ----------------------------------------------------
        # Revenue CAGR 3yr
        # ----------------------------------------------------

        pnl = pnl.rename(
            columns={
                "company_id":
                    "ticker"
            }
        )

        pnl["ticker"] = (
            pnl["ticker"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        pnl["_year"] = _year_number(
            pnl["year"]
        )

        pnl["sales"] = _numeric(
            pnl["sales"]
        )

        cagr_rows = []

        for ticker, group in (
            pnl.groupby("ticker")
        ):

            group = (
                group.dropna(
                    subset=[
                        "_year",
                        "sales",
                    ]
                )
                .sort_values(
                    "_year"
                )
            )

            if len(group) < 2:
                continue

            latest = group.iloc[
                -1
            ]

            target_year = (
                int(
                    latest[
                        "_year"
                    ]
                )
                - 3
            )

            previous_rows = (
                group[
                    group[
                        "_year"
                    ]
                    == target_year
                ]
            )

            if previous_rows.empty:
                continue

            previous = (
                previous_rows.iloc[
                    -1
                ]
            )

            cagr = _calculate_cagr(
                previous["sales"],
                latest["sales"],
                3,
            )

            if pd.notna(cagr):

                cagr_rows.append(
                    {
                        "ticker":
                            ticker,
                        "revenue_cagr_3yr":
                            cagr,
                    }
                )

        if cagr_rows:

            cagr_df = pd.DataFrame(
                cagr_rows
            )

            result = result.merge(
                cagr_df,
                on="ticker",
                how="left",
                suffixes=(
                    "",
                    "_calc",
                ),
            )

            result[
                "revenue_cagr_3yr"
            ] = result[
                "revenue_cagr_3yr_calc"
            ]

            result = result.drop(
                columns=[
                    "revenue_cagr_3yr_calc"
                ],
                errors="ignore",
            )

        # ----------------------------------------------------
        # D/E declining YoY
        # ----------------------------------------------------

        ratios = ratios.rename(
            columns={
                "company_id":
                    "ticker"
            }
        )

        ratios["ticker"] = (
            ratios["ticker"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        ratios["_year"] = _year_number(
            ratios["year"]
        )

        ratios[
            "debt_to_equity"
        ] = _numeric(
            ratios[
                "debt_to_equity"
            ]
        )

        flags = []

        for ticker, group in (
            ratios.groupby("ticker")
        ):

            group = (
                group.dropna(
                    subset=[
                        "_year",
                        "debt_to_equity",
                    ]
                )
                .sort_values(
                    "_year"
                )
            )

            if len(group) < 2:
                continue

            latest_de = group.iloc[
                -1
            ][
                "debt_to_equity"
            ]

            previous_de = group.iloc[
                -2
            ][
                "debt_to_equity"
            ]

            flags.append(
                {
                    "ticker":
                        ticker,
                    "de_declining":
                        latest_de
                        < previous_de,
                }
            )

        if flags:

            flags_df = pd.DataFrame(
                flags
            )

            result = result.drop(
                columns=[
                    "de_declining"
                ],
                errors="ignore",
            ).merge(
                flags_df,
                on="ticker",
                how="left",
            )

            result[
                "de_declining"
            ] = result[
                "de_declining"
            ].fillna(
                False
            )

    except Exception:
        pass

    return result


# ============================================================
# DAY 16 PRESET ENGINE
# ============================================================

def _apply_preset_filters(
    df,
    preset_name,
):
    """Apply one official Day-16 preset."""

    if preset_name not in PRESET_SCREENERS:

        raise ValueError(
            f"Unknown preset: {preset_name}"
        )

    result = df.copy()

    # --------------------------------------------------------
    # Quality Compounder
    # --------------------------------------------------------

    if (
        preset_name
        == "Quality Compounder"
    ):

        result = _apply_min(
            result,
            "return_on_equity_pct",
            15.0,
        )

        result = (
            _apply_de_max_excluding_financials(
                result,
                1.0,
            )
        )

        result = _apply_min(
            result,
            "free_cash_flow_cr",
            0.0,
        )

        result = _apply_min(
            result,
            "revenue_cagr_5yr",
            10.0,
        )

    # --------------------------------------------------------
    # Value Pick
    # --------------------------------------------------------

    elif (
        preset_name
        == "Value Pick"
    ):

        result = _apply_max(
            result,
            "pe_ratio",
            20.0,
        )

        result = _apply_max(
            result,
            "pb_ratio",
            3.0,
        )

        result = (
            _apply_de_max_excluding_financials(
                result,
                2.0,
            )
        )

        result = _apply_min(
            result,
            "dividend_yield_pct",
            1.0,
        )

    # --------------------------------------------------------
    # Growth Accelerator
    # --------------------------------------------------------

    elif (
        preset_name
        == "Growth Accelerator"
    ):

        result = _apply_min(
            result,
            "pat_cagr_5yr",
            20.0,
        )

        result = _apply_min(
            result,
            "revenue_cagr_5yr",
            15.0,
        )

        result = (
            _apply_de_max_excluding_financials(
                result,
                2.0,
            )
        )

    # --------------------------------------------------------
    # Dividend Champion
    # --------------------------------------------------------

    elif (
        preset_name
        == "Dividend Champion"
    ):

        result = _apply_min(
            result,
            "dividend_yield_pct",
            2.0,
        )

        result = _apply_max(
            result,
            "dividend_payout",
            80.0,
        )

        result = _apply_min(
            result,
            "free_cash_flow_cr",
            0.0,
        )

    # --------------------------------------------------------
    # Debt-Free Blue Chip
    # --------------------------------------------------------

    elif (
        preset_name
        == "Debt-Free Blue Chip"
    ):

        result = _apply_max(
            result,
            "debt_to_equity",
            0.0,
        )

        result = _apply_min(
            result,
            "return_on_equity_pct",
            12.0,
        )

        result = _apply_min(
            result,
            "sales",
            5000.0,
        )

    # --------------------------------------------------------
    # Turnaround Watch
    # --------------------------------------------------------

    elif (
        preset_name
        == "Turnaround Watch"
    ):

        result = (
            _calculate_turnaround_metrics(
                result
            )
        )

        result = _apply_min(
            result,
            "revenue_cagr_3yr",
            10.0,
        )

        result = _apply_min(
            result,
            "free_cash_flow_cr",
            0.0,
        )

        result = result[
            result[
                "de_declining"
            ]
            .fillna(False)
        ].copy()

    return result.reset_index(
        drop=True
    )


def run_preset_screener(
    df,
    preset_name,
):
    """Run one named Day-16 preset."""

    result = _apply_preset_filters(
        df,
        preset_name,
    )

    result = (
        add_composite_quality_score(
            result
        )
    )

    return result.sort_values(
        "composite_quality_score",
        ascending=False,
        kind="stable",
    ).reset_index(
        drop=True
    )


def run_all_presets(df):
    """Run all six Day-16 presets."""

    return {
        name: run_preset_screener(
            df,
            name,
        )
        for name in PRESET_SCREENERS
    }


def preset_summary(df):
    """Return counts for all six presets."""

    results = run_all_presets(
        df
    )

    return pd.DataFrame(
        [
            {
                "preset": name,
                "companies_returned": len(
                    result
                ),
                "within_required_range": (
                    5 <= len(result) <= 50
                ),
            }
            for name, result
            in results.items()
        ]
    )