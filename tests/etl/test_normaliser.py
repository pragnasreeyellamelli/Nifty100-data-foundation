from src.etl.normaliser import normalize_ticker, normalize_year


def test_normalize_ticker_uppercase():
    assert normalize_ticker("tcs") == "TCS"


def test_normalize_ticker_spaces():
    assert normalize_ticker("  tcs  ") == "TCS"


def test_normalize_ticker_mixed_case():
    assert normalize_ticker("InFy") == "INFY"


def test_normalize_ticker_none():
    assert normalize_ticker(None) is None


def test_normalize_year_march():
    assert normalize_year("Mar-23") == "2023-03"


def test_normalize_year_december():
    assert normalize_year("Dec-24") == "2024-12"

def test_normalize_year_january():
    assert normalize_year("Jan-23") == "2023-01"


def test_normalize_year_june():
    assert normalize_year("Jun-23") == "2023-06"


def test_normalize_year_september():
    assert normalize_year("Sep-24") == "2024-09"


def test_normalize_year_full_year():
    assert normalize_year("2025") == "2025"


def test_normalize_year_none():
    assert normalize_year(None) is None


def test_normalize_year_whitespace():
    assert normalize_year("  Mar-23  ") == "2023-03"

def test_normalize_ticker_lowercase():
    assert normalize_ticker("reliance") == "RELIANCE"


def test_normalize_ticker_leading_spaces():
    assert normalize_ticker("  TCS") == "TCS"


def test_normalize_ticker_trailing_spaces():
    assert normalize_ticker("TCS  ") == "TCS"


def test_normalize_ticker_both_spaces():
    assert normalize_ticker("  TCS  ") == "TCS"


def test_normalize_ticker_mixed_case_with_spaces():
    assert normalize_ticker("  ReLiAnCe  ") == "RELIANCE"


def test_normalize_ticker_numeric_value():
    assert normalize_ticker(123) == "123"


def test_normalize_ticker_empty_string():
    assert normalize_ticker("") == ""


def test_normalize_ticker_whitespace_only():
    assert normalize_ticker("   ") == ""


def test_normalize_ticker_special_character():
    assert normalize_ticker("TCS.L") == "TCS.L"


def test_normalize_ticker_already_uppercase():
    assert normalize_ticker("INFY") == "INFY"

def test_normalize_year_january():
    assert normalize_year("Jan-24") == "2024-01"


def test_normalize_year_february():
    assert normalize_year("Feb-24") == "2024-02"


def test_normalize_year_april():
    assert normalize_year("Apr-24") == "2024-04"


def test_normalize_year_may():
    assert normalize_year("May-24") == "2024-05"


def test_normalize_year_july():
    assert normalize_year("Jul-24") == "2024-07"


def test_normalize_year_august():
    assert normalize_year("Aug-24") == "2024-08"


def test_normalize_year_october():
    assert normalize_year("Oct-24") == "2024-10"


def test_normalize_year_november():
    assert normalize_year("Nov-24") == "2024-11"


def test_normalize_year_lowercase():
    assert normalize_year("mar-23") == "2023-03"


def test_normalize_year_full_date():
    assert normalize_year("2024-03") == "2024-03"


def test_normalize_year_integer():
    assert normalize_year(2025) == "2025"


def test_normalize_ticker_tab_spaces():
    assert normalize_ticker("\tTCS\t") == "TCS"


def test_normalize_ticker_newline():
    assert normalize_ticker("\nINFY\n") == "INFY"

def test_normalize_year_december_2025():
    assert normalize_year("Dec-25") == "2025-12"    