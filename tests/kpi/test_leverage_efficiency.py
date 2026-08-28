from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage,
    interest_coverage_label,
    interest_coverage_warning,
    net_debt,
    asset_turnover,
)


def test_debt_to_equity():
    assert debt_to_equity(50, 50, 50) == 0.5


def test_debt_to_equity_debt_free():
    assert debt_to_equity(0, 50, 50) == 0


def test_high_leverage_flag():
    assert high_leverage_flag(6, "Information Technology") is True


def test_financials_high_leverage_suppressed():
    assert high_leverage_flag(6, "Financials") is False


def test_interest_coverage():
    assert interest_coverage(100, 20, 20) == 6


def test_interest_coverage_zero_interest():
    assert interest_coverage(100, 20, 0) is None


def test_interest_coverage_label():
    assert interest_coverage_label(None) == "Debt Free"


def test_asset_turnover_zero_assets():
    assert asset_turnover(100, 0) is None