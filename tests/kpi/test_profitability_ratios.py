from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    check_opm_difference,
)


def test_net_profit_margin():
    assert net_profit_margin(20, 100) == 20


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(20, 0) is None


def test_operating_profit_margin():
    assert operating_profit_margin(30, 100) == 30


def test_return_on_equity():
    assert return_on_equity(20, 50, 50) == 20


def test_return_on_equity_negative_equity():
    assert return_on_equity(20, -100, 20) is None


def test_return_on_assets():
    assert return_on_assets(10, 100) == 10


def test_return_on_capital_employed():
    assert return_on_capital_employed(30, 50, 50, 50) == 20


def test_opm_cross_check_mismatch():
    assert check_opm_difference(20, 18) is True
