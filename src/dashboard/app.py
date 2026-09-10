import streamlit as st


st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.title("NIFTY 100 Financial Analytics")

st.markdown(
    """
    ## Welcome

    This dashboard provides:

    - Company profiles
    - Financial screener
    - Peer comparison
    - Trend analysis
    - Sector analysis
    - Capital allocation analysis
    - Annual reports
    - Valuation insights
    """
)

st.info(
    "Use the sidebar to navigate through the available dashboard screens."
)