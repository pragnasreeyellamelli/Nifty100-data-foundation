import pandas as pd
from pathlib import Path

from .ratios import (
    return_on_equity,
    return_on_capital_employed,
)


BASE_DIR = Path(__file__).resolve().parents[2]

COMPANIES_FILE = BASE_DIR / "data" / "raw" / "companies.xlsx"
BALANCE_SHEET_FILE = BASE_DIR / "data" / "raw" / "balancesheet.xlsx"
PROFIT_LOSS_FILE = BASE_DIR / "data" / "raw" / "profitandloss.xlsx"

LOG_FILE = BASE_DIR / "output" / "ratio_edge_cases.log"


def check_roce_difference(computed_roce, source_roce):
    """Return True when ROCE differs by more than 5 percentage points."""
    if pd.isna(computed_roce) or pd.isna(source_roce):
        return False

    return abs(computed_roce - source_roce) > 5


def check_roe_difference(computed_roe, source_roe):
    """Return True when ROE differs by more than 5 percentage points."""
    if pd.isna(computed_roe) or pd.isna(source_roe):
        return False

    return abs(computed_roe - source_roe) > 5


def categorise_anomaly(computed, source):
    """Categorise a ratio anomaly."""

    if pd.isna(computed) or pd.isna(source):
        return "data source issue"

    difference = abs(computed - source)

    if difference > 20:
        return "data source issue"

    return "version difference"


def run_edge_case_check():
    """Compare computed ROCE/ROE with source values."""

    companies = pd.read_excel(COMPANIES_FILE, header=1)
    balance_sheet = pd.read_excel(BALANCE_SHEET_FILE, header=1)
    profit_loss = pd.read_excel(PROFIT_LOSS_FILE, header=1)

    companies = companies.rename(columns={
        "id": "company_id"
    })

    balance_sheet = balance_sheet.rename(columns={
        "id": "balance_id"
    })

    profit_loss = profit_loss.rename(columns={
        "id": "profit_loss_id"
    })

    # Combine balance sheet and profit & loss data
    # using company and year.
    financial_data = (
        balance_sheet
        .merge(
            profit_loss,
            on=["company_id", "year"],
            how="inner",
        )
    )

    # companies.xlsx contains company-level ROCE/ROE values
    # rather than separate values for every financial year.
    # Therefore, use the latest available financial year
    # for each company.
    latest_years = (
        financial_data
        .groupby("company_id")["year"]
        .max()
        .reset_index()
    )

    financial_data = financial_data.merge(
        latest_years,
        on=["company_id", "year"],
        how="inner",
    )

    merged = financial_data.merge(
        companies[
            [
                "company_id",
                "company_name",
                "roce_percentage",
                "roe_percentage",
            ]
        ],
        on="company_id",
        how="left",
    )

    anomalies = []

    for _, row in merged.iterrows():

        ebit = row["operating_profit"] + row["other_income"]

        computed_roce = return_on_capital_employed(
            ebit,
            row["equity_capital"],
            row["reserves"],
            row["borrowings"],
        )

        computed_roe = return_on_equity(
            row["net_profit"],
            row["equity_capital"],
            row["reserves"],
        )

        source_roce = row["roce_percentage"]
        source_roe = row["roe_percentage"]

        if check_roce_difference(computed_roce, source_roce):
            anomalies.append(
                {
                    "company": row["company_id"],
                    "year": row["year"],
                    "ratio": "ROCE",
                    "computed": computed_roce,
                    "source": source_roce,
                    "difference": abs(computed_roce - source_roce),
                    "category": categorise_anomaly(
                        computed_roce,
                        source_roce,
                    ),
                }
            )

        if check_roe_difference(computed_roe, source_roe):
            anomalies.append(
                {
                    "company": row["company_id"],
                    "year": row["year"],
                    "ratio": "ROE",
                    "computed": computed_roe,
                    "source": source_roe,
                    "difference": abs(computed_roe - source_roe),
                    "category": categorise_anomaly(
                        computed_roe,
                        source_roe,
                    ),
                }
            )

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOG_FILE, "w", encoding="utf-8") as log:
        log.write("DAY 13 — RATIO EDGE CASE LOG\n")
        log.write("=" * 60 + "\n\n")

        if not anomalies:
            log.write("No ROCE or ROE anomalies found.\n")
        else:
            for anomaly in anomalies:
                log.write(
                    f"Company: {anomaly['company']}\n"
                    f"Year: {anomaly['year']}\n"
                    f"Ratio: {anomaly['ratio']}\n"
                    f"Computed: {anomaly['computed']:.2f}\n"
                    f"Source: {anomaly['source']:.2f}\n"
                    f"Difference: {anomaly['difference']:.2f}\n"
                    f"Category: {anomaly['category']}\n"
                    f"{'-' * 60}\n"
                )

    return anomalies


if __name__ == "__main__":
    results = run_edge_case_check()
    print(f"Edge-case check complete. Anomalies found: {len(results)}")
    print(f"Log written to: {LOG_FILE}")