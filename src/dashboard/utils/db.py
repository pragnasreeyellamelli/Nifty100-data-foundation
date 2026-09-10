import sqlite3

import pandas as pd
import streamlit as st


DB_PATH = "nifty100.db"


def _read_sql(query, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(
            query,
            conn,
            params=params,
        )


@st.cache_data(ttl=600)
def get_companies():
    return _read_sql(
        """
        SELECT
            company_id,
            company_name,
            sector
        FROM companies
        ORDER BY company_name
        """
    )


@st.cache_data(ttl=600)
def get_ratios(ticker, year=None):
    if year is None:
        return _read_sql(
            """
            SELECT *
            FROM financial_ratios
            WHERE company_id = ?
            ORDER BY year DESC
            """,
            (ticker,),
        )

    return _read_sql(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
          AND year = ?
        ORDER BY year DESC
        """,
        (ticker, year),
    )


@st.cache_data(ttl=600)
def get_pl(ticker):
    return _read_sql(
        """
        SELECT *
        FROM profit_and_loss
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        (ticker,),
    )


@st.cache_data(ttl=600)
def get_bs(ticker):
    return _read_sql(
        """
        SELECT *
        FROM balance_sheet
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        (ticker,),
    )


@st.cache_data(ttl=600)
def get_cf(ticker):
    return _read_sql(
        """
        SELECT *
        FROM cash_flow
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        (ticker,),
    )


@st.cache_data(ttl=600)
def get_sectors():
    return _read_sql(
        """
        SELECT
            sector_id,
            sector_name
        FROM sectors
        ORDER BY sector_name
        """
    )


@st.cache_data(ttl=600)
def get_peers(group_name):
    return _read_sql(
        """
        SELECT *
        FROM peer_percentiles
        WHERE peer_group_name = ?
        ORDER BY company_id
        """,
        (group_name,),
    )


@st.cache_data(ttl=600)
def get_valuation(ticker):
    return _read_sql(
        """
        SELECT *
        FROM valuation_summary
        WHERE company_id = ?
        """,
        (ticker,),
    )