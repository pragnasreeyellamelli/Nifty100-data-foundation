import pandas as pd

from src.etl.validator import validate_dataframe


def test_dq01_duplicate_company_id():
    df = pd.DataFrame({
        "company_id": [1, 1, 2],
        "year": ["2024", "2025", "2024"],
    })

    result = validate_dataframe(df)

    assert "DQ-01" in result["rule_id"].values
    assert "CRITICAL" in result["severity"].values


def test_dq02_duplicate_company_year():
    df = pd.DataFrame({
        "company_id": [1, 1, 2],
        "year": ["2024", "2024", "2024"],
    })

    result = validate_dataframe(df)

    assert "DQ-02" in result["rule_id"].values
    assert "CRITICAL" in result["severity"].values


def test_dq02_allows_different_years():
    df = pd.DataFrame({
        "company_id": [1, 1],
        "year": ["2024", "2025"],
    })

    result = validate_dataframe(df)

    assert "DQ-02" not in result["rule_id"].values


def test_dq04_balance_sheet():
    df = pd.DataFrame({
        "total_assets": [1000],
        "total_liabilities": [800],
    })

    result = validate_dataframe(df)

    assert "DQ-04" in result["rule_id"].values


def test_dq04_valid_balance():
    df = pd.DataFrame({
        "total_assets": [1000],
        "total_liabilities": [995],
    })

    result = validate_dataframe(df)

    assert "DQ-04" not in result["rule_id"].values


def test_dq05_opm_cross_check():
    df = pd.DataFrame({
        "operating_profit": [100],
        "sales": [1000],
        "opm": [50],
    })

    result = validate_dataframe(df)

    assert "DQ-05" in result["rule_id"].values
    assert "WARNING" in result["severity"].values


def test_dq05_valid_opm():
    df = pd.DataFrame({
        "operating_profit": [100],
        "sales": [1000],
        "opm": [10],
    })

    result = validate_dataframe(df)

    assert "DQ-05" not in result["rule_id"].values


def test_dq06_negative_sales():
    df = pd.DataFrame({
        "sales": [-100],
    })

    result = validate_dataframe(df)

    assert "DQ-06" in result["rule_id"].values
    assert "WARNING" in result["severity"].values


def test_dq06_zero_sales():
    df = pd.DataFrame({
        "sales": [0],
    })

    result = validate_dataframe(df)

    assert "DQ-06" in result["rule_id"].values


def test_valid_dataframe_has_no_failures():
    df = pd.DataFrame({
        "company_id": [1, 2],
        "year": ["2024", "2025"],
        "total_assets": [1000, 2000],
        "total_liabilities": [995, 1990],
        "operating_profit": [100, 200],
        "sales": [1000, 2000],
        "opm": [10, 10],
    })

    result = validate_dataframe(df)

    assert result.empty