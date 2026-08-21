import pandas as pd
import pytest

from src.etl.loader import load_excel, normalize_dataframe, load_and_normalize


def test_load_excel_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_excel("does_not_exist.xlsx")


def test_load_excel_reads_file(tmp_path):
    file_path = tmp_path / "sample.xlsx"

    df = pd.DataFrame({
        "Ticker": ["reliance", "tcs"],
        "Year": ["Mar-24", "Mar-24"],
        "Revenue": [100, 200],
    })

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        pd.DataFrame([["Sample Financial Data"]]).to_excel(
            writer,
            index=False,
            header=False
        )

        df.to_excel(
            writer,
            index=False,
            startrow=1
        )

    result = load_excel(file_path)

    assert len(result) == 2
    assert "Ticker" in result.columns
    assert "Year" in result.columns


def test_normalize_dataframe_ticker():
    df = pd.DataFrame({
        "Ticker": [" reliance ", "tcs"],
        "Revenue": [100, 200],
    })

    result = normalize_dataframe(df)

    assert result["Ticker"].tolist() == ["RELIANCE", "TCS"]


def test_normalize_dataframe_year():
    df = pd.DataFrame({
        "Ticker": ["RELIANCE", "TCS"],
        "Year": ["Mar-24", "Jun-23"],
    })

    result = normalize_dataframe(df)

    assert result["Year"].tolist() == ["2024-03", "2023-06"]


def test_normalize_dataframe_does_not_change_other_columns():
    df = pd.DataFrame({
        "Ticker": ["RELIANCE"],
        "Year": ["Mar-24"],
        "Revenue": [500],
    })

    result = normalize_dataframe(df)

    assert result["Revenue"].tolist() == [500]


def test_load_and_normalize(tmp_path):
    file_path = tmp_path / "sample.xlsx"

    df = pd.DataFrame({
        "Ticker": [" reliance "],
        "Year": ["Mar-24"],
        "Revenue": [100],
    })

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        pd.DataFrame([["Sample Financial Data"]]).to_excel(
            writer,
            index=False,
            header=False
        )

        df.to_excel(
            writer,
            index=False,
            startrow=1
        )

    result = load_and_normalize(file_path)

    assert result["Ticker"].iloc[0] == "RELIANCE"
    assert result["Year"].iloc[0] == "2024-03"