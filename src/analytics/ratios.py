from pathlib import Path


def net_profit_margin(net_profit, sales):
    """
    Calculate Net Profit Margin.

    Formula:
        (Net Profit / Sales) * 100

    Returns None when sales is zero.
    """
    if sales == 0:
        return None

    return (net_profit / sales) * 100


def operating_profit_margin(operating_profit, sales):
    """
    Calculate Operating Profit Margin.

    Formula:
        (Operating Profit / Sales) * 100

    Returns None when sales is zero.
    """
    if sales == 0:
        return None

    return (operating_profit / sales) * 100


def return_on_equity(net_profit, equity_capital, reserves):
    """
    Calculate Return on Equity (ROE).

    Formula:
        (Net Profit / (Equity Capital + Reserves)) * 100

    Returns None when equity + reserves is zero or negative.
    """
    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return (net_profit / equity) * 100


def return_on_capital_employed(
    ebit,
    equity_capital,
    reserves,
    borrowings
):
    """
    Calculate Return on Capital Employed (ROCE).

    Formula:
        (EBIT / (Equity + Reserves + Borrowings)) * 100

    Returns None when total capital employed is zero or negative.
    """
    capital_employed = equity_capital + reserves + borrowings

    if capital_employed <= 0:
        return None

    return (ebit / capital_employed) * 100


def return_on_assets(net_profit, total_assets):
    """
    Calculate Return on Assets (ROA).

    Formula:
        (Net Profit / Total Assets) * 100

    Returns None when total assets is zero.
    """
    if total_assets == 0:
        return None

    return (net_profit / total_assets) * 100


def check_opm_difference(computed_opm, source_opm):
    """
    Compare calculated OPM with the source OPM percentage.

    Returns True when the difference is greater than 1 percentage point.
    """
    if computed_opm is None or source_opm is None:
        return False

    difference = abs(computed_opm - source_opm)

    return difference > 1


def check_roce_difference(computed_roce, source_roce):
    """
    Compare calculated ROCE with the pre-computed source ROCE.

    A difference greater than 5 percentage points is treated
    as a potential edge case.
    """
    if computed_roce is None or source_roce is None:
        return False

    difference = abs(computed_roce - source_roce)

    return difference > 5


def check_roe_difference(computed_roe, source_roe):
    """
    Compare calculated ROE with the pre-computed source ROE.

    This is a cross-check only. The calculated ROE remains
    the value used for analytics.
    """
    if computed_roe is None or source_roe is None:
        return False

    difference = abs(computed_roe - source_roe)

    return difference > 5


def log_ratio_edge_case(
    company_id,
    ratio_name,
    computed_value,
    source_value,
    category="review"
):
    """
    Log a ratio anomaly to output/ratio_edge_cases.log.

    Categories:
        - data source issue
        - version difference
        - formula discrepancy
    """
    log_path = Path("output/ratio_edge_cases.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    difference = abs(computed_value - source_value)

    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(
            f"{company_id} | "
            f"{ratio_name} | "
            f"computed={computed_value:.2f} | "
            f"source={source_value:.2f} | "
            f"difference={difference:.2f} | "
            f"category={category}\n"
        )


def debt_to_equity(borrowings, equity_capital, reserves):
    """
    Calculate Debt-to-Equity ratio.

    Formula:
        Borrowings / (Equity Capital + Reserves)

    Returns 0 when borrowings are zero.
    Returns None when equity + reserves is zero or negative.
    """
    if borrowings == 0:
        return 0

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return borrowings / equity


def high_leverage_flag(debt_to_equity_value, broad_sector):
    """
    Flag companies with high leverage.

    D/E > 5 is considered high leverage, except for
    companies in the Financials sector.
    """
    if debt_to_equity_value is None:
        return False

    # Financial companies are intentionally excluded because
    # high leverage is structurally normal for banks, NBFCs,
    # and insurance companies.
    if broad_sector == "Financials":
        return False

    return debt_to_equity_value > 5


def interest_coverage(operating_profit, other_income, interest):
    """
    Calculate Interest Coverage Ratio (ICR).

    Formula:
        (Operating Profit + Other Income) / Interest

    Returns None when interest is zero.
    """
    if interest == 0:
        return None

    return (operating_profit + other_income) / interest


def interest_coverage_label(interest_coverage_value):
    """
    Return a display label for the Interest Coverage Ratio.
    """
    if interest_coverage_value is None:
        return "Debt Free"

    return None


def interest_coverage_warning(interest_coverage_value):
    """
    Flag companies with an Interest Coverage Ratio below 1.5.
    """
    if interest_coverage_value is None:
        return False

    return interest_coverage_value < 1.5


def net_debt(borrowings, investments):
    """
    Calculate Net Debt.

    Formula:
        Borrowings - Investments
    """
    return borrowings - investments


def asset_turnover(sales, total_assets):
    """
    Calculate Asset Turnover.

    Formula:
        Sales / Total Assets

    Returns None when total assets is zero.
    """
    if total_assets == 0:
        return None

    return sales / total_assets

def check_roce_difference(computed_roce, source_roce):
    """
    Compare computed ROCE with the source ROCE percentage.

    Returns True when the difference is greater than 5 percentage points.
    """
    if computed_roce is None or source_roce is None:
        return False

    difference = abs(computed_roce - source_roce)

    return difference > 5


def check_roe_difference(computed_roe, source_roe):
    """
    Compare computed ROE with the source ROE percentage.

    Returns True when the difference is greater than 5 percentage points.
    """
    if computed_roe is None or source_roe is None:
        return False

    difference = abs(computed_roe - source_roe)

    return difference > 5