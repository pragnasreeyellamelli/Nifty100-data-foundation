import pandas as pd


def _add_failure(
    failures,
    rule_id,
    severity,
    column,
    message
):
    failures.append({
        "rule_id": rule_id,
        "severity": severity,
        "column": column,
        "message": message
    })


def validate_dataframe(
    df: pd.DataFrame,
    table_name: str = "",
    companies_df: pd.DataFrame | None = None,
    pl_df: pd.DataFrame | None = None,
    bs_df: pd.DataFrame | None = None,
    cf_df: pd.DataFrame | None = None,
    check_urls: bool = False
) -> pd.DataFrame:
    """
    Run DQ-01 to DQ-16 validation rules.

    Returns a DataFrame containing validation failures.
    """

    failures = []

    # ============================================================
    # DQ-01: Primary Key Uniqueness
    # ============================================================
    if "company_id" in df.columns:
        duplicates = df[df["company_id"].duplicated(keep=False)]

        for _, row in duplicates.iterrows():
            _add_failure(
                failures,
                "DQ-01",
                "CRITICAL",
                "company_id",
                "Duplicate company_id found"
            )

    elif table_name.lower() == "companies" and "id" in df.columns:
        duplicates = df[df["id"].duplicated(keep=False)]

        for _, row in duplicates.iterrows():
            _add_failure(
                failures,
                "DQ-01",
                "CRITICAL",
                "id",
                "Duplicate company id found"
            )

    # ============================================================
    # DQ-02: (company_id, year) Uniqueness
    # ============================================================
    if "company_id" in df.columns and "year" in df.columns:
        duplicates = df[
            df.duplicated(
                subset=["company_id", "year"],
                keep=False
            )
        ]

        for _, row in duplicates.iterrows():
            _add_failure(
                failures,
                "DQ-02",
                "CRITICAL",
                "company_id, year",
                "Duplicate company_id and year combination found"
            )

    # ============================================================
    # DQ-03: Foreign Key Integrity
    # ============================================================
    if (
        companies_df is not None
        and "company_id" in df.columns
        and "id" in companies_df.columns
    ):
        valid_ids = set(
            companies_df["id"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
        )

        child_ids = (
            df["company_id"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
        )

        invalid = df[
            ~child_ids.isin(valid_ids)
        ]

        for _, row in invalid.iterrows():
            _add_failure(
                failures,
                "DQ-03",
                "CRITICAL",
                "company_id",
                "Orphan company_id not found in companies.id"
            )

    # ============================================================
    # DQ-04: Balance Sheet Balance
    # ============================================================
    if all(
        column in df.columns
        for column in [
            "total_assets",
            "total_liabilities"
        ]
    ):
        assets = pd.to_numeric(
            df["total_assets"],
            errors="coerce"
        )

        liabilities = pd.to_numeric(
            df["total_liabilities"],
            errors="coerce"
        )

        valid_assets = assets != 0

        difference_ratio = (
            (assets - liabilities).abs()
            / assets.abs()
        )

        invalid = df[
            valid_assets
            & (difference_ratio >= 0.01)
        ]

        for _, row in invalid.iterrows():
            _add_failure(
                failures,
                "DQ-04",
                "WARNING",
                "total_assets, total_liabilities",
                "Balance sheet difference is >= 1%"
            )

    # ============================================================
    # DQ-05: OPM Cross-Check
    # ============================================================
    opm_column = None

    if "opm" in df.columns:
        opm_column = "opm"
    elif "opm_percentage" in df.columns:
        opm_column = "opm_percentage"

    if (
        opm_column is not None
        and "operating_profit" in df.columns
        and "sales" in df.columns
    ):
        sales = pd.to_numeric(
            df["sales"],
            errors="coerce"
        )

        operating_profit = pd.to_numeric(
            df["operating_profit"],
            errors="coerce"
        )

        source_opm = pd.to_numeric(
            df[opm_column],
            errors="coerce"
        )

        valid_sales = sales != 0

        expected_opm = (
            operating_profit / sales * 100
        )

        invalid = df[
            valid_sales
            & (expected_opm - source_opm).abs().ge(1.0)
        ]

        for _, row in invalid.iterrows():
            _add_failure(
                failures,
                "DQ-05",
                "WARNING",
                opm_column,
                "OPM does not match operating profit and sales"
            )

    # ============================================================
    # DQ-06: Positive Sales
    # ============================================================
    if "sales" in df.columns:
        sales = pd.to_numeric(
            df["sales"],
            errors="coerce"
        )

        if "sector" in df.columns:
            is_bank = (
                df["sector"]
                .astype(str)
                .str.contains(
                    "bank",
                    case=False,
                    na=False
                )
            )

            invalid = df[
                (~is_bank) & (sales <= 0)
            ]
        else:
            invalid = df[
                sales <= 0
            ]

        for _, row in invalid.iterrows():
            _add_failure(
                failures,
                "DQ-06",
                "WARNING",
                "sales",
                "Sales must be positive"
            )

    # ============================================================
    # DQ-07: Year Format
    # ============================================================
    if "year" in df.columns:
        year_values = (
            df["year"]
            .astype(str)
            .str.strip()
        )

        # Run this rule only when YYYY-MM style
        # values are present in the dataset.
        if year_values.str.contains(
            "-",
            regex=False,
            na=False
        ).any():

            invalid = df[
                ~year_values.str.match(
                    r"^\d{4}-\d{2}$",
                    na=False
                )
            ]

            for _, row in invalid.iterrows():
                _add_failure(
                    failures,
                    "DQ-07",
                    "CRITICAL",
                    "year",
                    "Year must match YYYY-MM format"
                )

    # ============================================================
    # DQ-08: Ticker Format
    # ============================================================
    if "ticker" in df.columns:
        ticker_values = (
            df["ticker"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        invalid = df[
            (ticker_values.str.len() < 2)
            | (ticker_values.str.len() > 12)
        ]

        for _, row in invalid.iterrows():
            _add_failure(
                failures,
                "DQ-08",
                "CRITICAL",
                "ticker",
                "Ticker length must be between 2 and 12 characters"
            )

    # ============================================================
    # DQ-09: Net Cash Check
    # ============================================================
    if all(
        column in df.columns
        for column in [
            "net_cash_flow",
            "operating_activity",
            "investing_activity",
            "financing_activity"
        ]
    ):
        net_cash = pd.to_numeric(
            df["net_cash_flow"],
            errors="coerce"
        )

        operating = pd.to_numeric(
            df["operating_activity"],
            errors="coerce"
        )

        investing = pd.to_numeric(
            df["investing_activity"],
            errors="coerce"
        )

        financing = pd.to_numeric(
            df["financing_activity"],
            errors="coerce"
        )

        expected = (
            operating
            + investing
            + financing
        )

        invalid = df[
            (net_cash - expected).abs() > 10
        ]

        for _, row in invalid.iterrows():
            _add_failure(
                failures,
                "DQ-09",
                "WARNING",
                "net_cash_flow",
                "Net cash flow differs from CFO + CFI + CFF by more than 10 Cr"
            )

    # ============================================================
    # DQ-10: Non-Negative Fixed Assets
    # ============================================================
    if "fixed_assets" in df.columns:
        fixed_assets = pd.to_numeric(
            df["fixed_assets"],
            errors="coerce"
        )

        invalid = df[
            fixed_assets < 0
        ]

        for _, row in invalid.iterrows():
            _add_failure(
                failures,
                "DQ-10",
                "WARNING",
                "fixed_assets",
                "Fixed assets cannot be negative"
            )

    # ============================================================
    # DQ-11: Tax Rate Range
    # ============================================================
    if "tax_percentage" in df.columns:
        tax = pd.to_numeric(
            df["tax_percentage"],
            errors="coerce"
        )

        invalid = df[
            (tax < 0)
            | (tax > 60)
        ]

        for _, row in invalid.iterrows():
            _add_failure(
                failures,
                "DQ-11",
                "WARNING",
                "tax_percentage",
                "Tax percentage must be between 0 and 60"
            )

    # ============================================================
    # DQ-12: Dividend Payout Cap
    # ============================================================
    if "dividend_payout" in df.columns:
        payout = pd.to_numeric(
            df["dividend_payout"],
            errors="coerce"
        )

        invalid = df[
            payout > 200
        ]

        for _, row in invalid.iterrows():
            _add_failure(
                failures,
                "DQ-12",
                "WARNING",
                "dividend_payout",
                "Dividend payout cannot exceed 200%"
            )

    # ============================================================
    # DQ-13: URL Validity
    # ============================================================
    if check_urls and "Annual_Report" in df.columns:
        import urllib.request

        for _, row in df.iterrows():
            url = row["Annual_Report"]

            if pd.isna(url) or not str(url).strip():
                continue

            try:
                request = urllib.request.Request(
                    str(url),
                    method="HEAD"
                )

                with urllib.request.urlopen(
                    request,
                    timeout=5
                ) as response:

                    status = response.status

                if status != 200:
                    _add_failure(
                        failures,
                        "DQ-13",
                        "WARNING",
                        "Annual_Report",
                        f"Annual report URL returned HTTP {status}"
                    )

            except Exception:
                _add_failure(
                    failures,
                    "DQ-13",
                    "WARNING",
                    "Annual_Report",
                    "Annual report URL could not be reached"
                )

    # ============================================================
    # DQ-14: EPS Sign Consistency
    # ============================================================
    if all(
        column in df.columns
        for column in [
            "eps",
            "net_profit"
        ]
    ):
        eps = pd.to_numeric(
            df["eps"],
            errors="coerce"
        )

        net_profit = pd.to_numeric(
            df["net_profit"],
            errors="coerce"
        )

        invalid = df[
            (
                (net_profit > 0)
                & (eps <= 0)
            )
            |
            (
                (net_profit < 0)
                & (eps >= 0)
            )
        ]

        for _, row in invalid.iterrows():
            _add_failure(
                failures,
                "DQ-14",
                "WARNING",
                "eps, net_profit",
                "EPS sign is inconsistent with net profit"
            )

    # ============================================================
    # DQ-15: Strict Balance Check
    # ============================================================
    if all(
        column in df.columns
        for column in [
            "total_assets",
            "total_liabilities",
            "total_equity"
        ]
    ):
        assets = pd.to_numeric(
            df["total_assets"],
            errors="coerce"
        )

        liabilities = pd.to_numeric(
            df["total_liabilities"],
            errors="coerce"
        )

        equity = pd.to_numeric(
            df["total_equity"],
            errors="coerce"
        )

        invalid = df[
            assets.notna()
            & liabilities.notna()
            & equity.notna()
            & (
                (assets - liabilities - equity).abs()
                > 0.01
            )
        ]

        for _, row in invalid.iterrows():
            _add_failure(
                failures,
                "DQ-15",
                "INFO",
                "total_assets, total_liabilities, total_equity",
                "Assets do not equal liabilities plus equity"
            )

    # ============================================================
    # DQ-16: Coverage Check
    # ============================================================
    if (
        pl_df is not None
        and bs_df is not None
        and cf_df is not None
    ):
        if all(
            "company_id" in table.columns
            and "year" in table.columns
            for table in [
                pl_df,
                bs_df,
                cf_df
            ]
        ):
            pl_years = (
                pl_df.groupby("company_id")["year"]
                .nunique()
            )

            bs_years = (
                bs_df.groupby("company_id")["year"]
                .nunique()
            )

            cf_years = (
                cf_df.groupby("company_id")["year"]
                .nunique()
            )

            company_ids = (
                set(pl_years.index)
                | set(bs_years.index)
                | set(cf_years.index)
            )

            for company_id in company_ids:
                counts = [
                    pl_years.get(company_id, 0),
                    bs_years.get(company_id, 0),
                    cf_years.get(company_id, 0)
                ]

                if min(counts) < 5:
                    _add_failure(
                        failures,
                        "DQ-16",
                        "WARNING",
                        "company_id",
                        f"Company {company_id} has fewer than 5 years of coverage"
                    )

    return pd.DataFrame(
        failures,
        columns=[
            "rule_id",
            "severity",
            "column",
            "message"
        ]
    )
    