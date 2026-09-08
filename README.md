# NIFTY 100 Data Foundation

A complete ETL, data-quality, financial analytics, and testing pipeline for processing NIFTY 100 financial data from multiple Excel sources and loading it into a structured SQLite database.

---

## 📌 Project Overview

This project builds the data foundation for a financial analytics system.

It ingests data from **12 Excel source files**, normalizes and validates the data using Python, and loads the processed data into a SQLite database containing multiple financial datasets.

The project is developed in multiple sprints, with each sprint adding new functionality to the data foundation and analytics pipeline.

---

# 🎯 Sprint 1 – Data Foundation

Sprint 1 focuses on building the core data ingestion, ETL, validation, and database foundation.

### Sprint 1 Goals

- Ingest 12 source Excel files
- Normalize financial data
- Apply data-quality rules
- Create a structured SQLite database
- Validate primary-key and foreign-key integrity
- Generate data-load audit reports
- Perform exploratory SQL analysis
- Build automated ETL tests

### Sprint 1 Deliverables

- Excel data ingestion pipeline
- Data normalization
- Data-quality validation
- SQLite database
- Foreign-key validation
- Data loading and audit reports
- Exploratory SQL queries
- Automated ETL testing

---

# 📊 Sprint 2 – KPI Analytics & Testing

Sprint 2 extends the data foundation by adding financial KPI analytics, edge-case handling, and automated KPI testing.

### Sprint 2 Goals

- Implement financial KPI calculations
- Calculate CAGR
- Calculate cash-flow KPIs
- Calculate profitability ratios
- Calculate leverage and efficiency metrics
- Handle analytical edge cases
- Build automated KPI tests
- Validate analytical calculations

### Sprint 2 Analytics

The following analytics modules were implemented:

- **CAGR Analysis**
- **Cashflow KPIs**
- **Profitability Ratios**
- **Leverage & Efficiency Analysis**
- **Ratio Calculations**
- **Ratio Edge-Case Handling**

### Sprint 2 Testing

Automated tests were added for:

- CAGR calculations
- Cashflow KPIs
- Leverage and efficiency metrics
- Profitability ratios

These tests help verify that KPI calculations produce reliable results and correctly handle edge cases.

---

# 🔎 Sprint 3 – Screener & Peer Comparison Engine

Sprint 3 extends the financial analytics platform by introducing a configurable financial screener, composite quality scoring, peer percentile analysis, radar charts, and peer comparison reporting.

### Sprint 3 Goals

- Build a configurable financial screener
- Implement threshold-based financial filters
- Implement six preset screeners
- Calculate composite quality scores
- Apply P10/P90 normalization
- Calculate sector-relative scores
- Compute peer percentile rankings
- Generate radar charts for companies
- Generate peer comparison Excel reports
- Validate screener and peer-ranking results
- Perform final data-quality testing

### Sprint 3 Screener

The following screener presets were implemented:

- **Quality Compounder**
- **Value Pick**
- **Growth Accelerator**
- **Dividend Champion**
- **Debt-Free Blue Chip**
- **Turnaround Watch**

The screener supports configurable financial thresholds including:

- ROE
- Debt-to-Equity
- Free Cash Flow
- Revenue CAGR
- PAT CAGR
- Operating Profit Margin
- P/E
- P/B
- Dividend Yield
- Interest Coverage
- Market Capitalization
- Net Profit
- EPS CAGR
- Asset Turnover
- Sales

### Sprint 3 Composite Quality Score

A composite quality score ranging from **0 to 100** was implemented using:

- **Profitability – 35%**
- **Cash Quality – 30%**
- **Growth – 20%**
- **Leverage – 15%**

The scoring system uses P10/P90 winsorisation and sector-relative normalization to compare companies more effectively within their sectors.

### Sprint 3 Peer Analytics

Peer percentile rankings were implemented across **11 peer groups** using the following 10 metrics:

- ROE
- ROCE
- Net Profit Margin
- Debt-to-Equity
- Free Cash Flow
- PAT CAGR 5yr
- Revenue CAGR 5yr
- EPS CAGR 5yr
- Interest Coverage
- Asset Turnover

For Debt-to-Equity, the percentile ranking is inverted so that lower debt-to-equity receives a higher percentile.

Companies without an assigned peer group are handled using:

**No peer group assigned**

### Sprint 3 Reports

The following outputs were generated:

- **screener_output.xlsx**
- **peer_comparison.xlsx**
- **Radar charts for NIFTY 100 companies**
- **peer_percentiles SQLite table**

The screener output contains one sheet per preset, while the peer comparison report contains one sheet for each of the 11 peer groups.

### Sprint 3 Testing

Testing and verification included:

- Screener preset verification
- Composite quality score validation
- Peer percentile validation
- IT Services ROE percentile spot-check
- Data-quality testing
- Full automated project test suite

The complete project test suite passes with **85 tests**.

---

# 🛠️ Technologies Used

- **Python**
- **Pandas**
- **NumPy**
- **SQLite**
- **SQL**
- **Pytest**
- **OpenPyXL**
- **Matplotlib**
- **PyYAML**
- **Git & GitHub**

---

# 📂 Project Structure

```text
nifty100-data-foundation/

│
├── config/
│   └── screener_config.yaml
│
├── data/
│   ├── raw/
│   └── supporting/
│
├── db_schema/
│   └── schema.sql
│
├── docs/
│
├── notebooks/
│   └── exploratory_queries.sql
│
├── output/
│   ├── load_audit.csv
│   ├── validation_failures.csv
│   ├── capital_allocation.csv
│   ├── screener_output.xlsx
│   └── peer_comparison.xlsx
│
├── reports/
│   ├── ratio_edge_cases.log
│   └── radar_charts/
│
├── src/
│   ├── analytics/
│   │   ├── cagr.py
│   │   ├── cashflow_kpis.py
│   │   ├── ratio_edge_cases.py
│   │   ├── ratios.py
│   │   ├── peer.py
│   │   ├── radar.py
│   │   └── peer_export.py
│   │
│   ├── api/
│   │
│   ├── dashboard/
│   │
│   ├── etl/
│   │   ├── loader.py
│   │   ├── normaliser.py
│   │   └── validator.py
│   │
│   └── screener/
│       ├── __init__.py
│       ├── engine.py
│       └── export.py
│
├── tests/
│   ├── api/
│   ├── dq/
│   ├── etl/
│   │
│   └── kpi/
│       ├── test_cagr.py
│       ├── test_cashflow_kpis.py
│       ├── test_leverage_efficiency.py
│       └── test_profitability_ratios.py
│
├── .gitignore
├── Makefile
├── nifty100.db
├── requirements.txt
└── README.md


AUTHOR

YELLAMELLI PRAGNASREE