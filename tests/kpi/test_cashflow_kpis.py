from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
)


def test_free_cash_flow():
    assert free_cash_flow(100, -40) == 60


def test_free_cash_flow_negative():
    assert free_cash_flow(50, -100) == -50


def test_cfo_quality_high():
    score, quality = cfo_quality_score(
        [120, 110, 130, 125, 115],
        [100, 100, 100, 100, 100],
    )
    assert score > 1.0
    assert quality == "High Quality"


def test_cfo_quality_zero_pat():
    score, quality = cfo_quality_score(
        [100, 100, 100, 100, 100],
        [100, 0, 100, 100, 100],
    )
    assert score is None
    assert quality is None


def test_capex_intensity_asset_light():
    intensity, classification = capex_intensity(-2, 100)
    assert intensity == 2
    assert classification == "Asset Light"


def test_capex_intensity_capital_intensive():
    intensity, classification = capex_intensity(-10, 100)
    assert intensity == 10
    assert classification == "Capital Intensive"


def test_fcf_conversion_rate():
    assert fcf_conversion_rate(50, 100) == 50


def test_capital_allocation_growth_funded_by_debt():
    assert capital_allocation_pattern(-10, -20, 30) == "Growth Funded by Debt"
    