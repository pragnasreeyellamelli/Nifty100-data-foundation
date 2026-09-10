# NIFTY 100 Data Foundation

A complete ETL, data-quality, financial analytics, testing, financial screening, peer comparison, and Streamlit dashboard pipeline for processing NIFTY 100 financial data from multiple Excel sources and loading it into a structured SQLite database.

---

## 📌 Project Overview

This project builds the data foundation and financial analytics platform for a NIFTY 100 financial intelligence system.

It ingests data from **12 Excel source files**, normalizes and validates the data using Python, and loads the processed data into a SQLite database containing multiple financial datasets.

The project is developed in multiple sprints, with each sprint adding new functionality to the data foundation, analytics pipeline, financial screener, peer comparison engine, and interactive dashboard.

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

The scoring system uses P10/P90 normalization and sector-relative scoring to compare companies more effectively within their sectors.

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

The complete project test suite passed with **85 tests**.

---

# 🖥️ Sprint 4 – Dashboard & Valuation Module

Sprint 4 extends the project into an interactive Streamlit financial analytics dashboard.

The dashboard provides company-level analysis, screening, peer comparison, trend analysis, sector analysis, capital allocation analysis, annual report access, and a centralized financial analytics interface.

### Sprint 4 Goals

- Build a Streamlit dashboard
- Create an 8-screen navigation structure
- Add shared cached database loading utilities
- Build company profile analysis
- Add financial screener interface
- Add peer comparison interface
- Add trend analysis
- Add sector analysis
- Add capital allocation map
- Add annual report screen
- Support CSV export from the screener
- Handle missing data without crashing

### Sprint 4 Dashboard

The Streamlit dashboard contains the following screens:

- **Home**
- **Company Profile**
- **Financial Screener**
- **Peer Comparison**
- **Trend Analysis**
- **Sector Analysis**
- **Capital Allocation Map**
- **Annual Reports**

### Sprint 4 Home Screen

The Home screen provides an overview of the NIFTY 100 universe including:

- Average ROE
- Median P/E
- Median D/E
- Total Companies
- Median Revenue CAGR 5yr
- Debt-Free Companies
- Top companies by Composite Quality Score
- Year selector
- Sector information

### Sprint 4 Company Profile

The Company Profile screen provides:

- Company search by ticker or name
- Company identification
- Financial KPI summary
- ROE
- ROCE
- Net Profit Margin
- Debt-to-Equity
- Revenue CAGR 5yr
- Free Cash Flow
- Historical Revenue and Net Profit trends
- ROE and ROCE trend analysis
- Pros and cons indicators
- Missing-data handling

### Sprint 4 Screener Interface

The dashboard screener provides:

- ROE minimum filter
- D/E maximum filter
- FCF minimum filter
- Revenue CAGR minimum filter
- PAT CAGR minimum filter
- OPM minimum filter
- P/E maximum filter
- P/B maximum filter
- Dividend Yield minimum filter
- Interest Coverage minimum filter

It also provides six preset buttons:

- **Quality**
- **Value**
- **Growth**
- **Dividend**
- **Debt-Free**
- **Turnaround**

Results update dynamically and can be downloaded using the CSV export feature.

### Sprint 4 Peer Comparison

The Peer Comparison screen provides:

- Peer group selection
- Company selection
- Radar comparison
- Company percentile metrics
- Peer-group comparison
- Benchmark company highlighting

### Sprint 4 Trend Analysis

The Trend Analysis screen provides:

- Company ticker search
- Multi-metric selection
- Historical financial trend charts
- Revenue trends
- Profit trends
- ROE trends
- ROCE trends
- Debt-to-equity trends
- Year-over-year analysis

### Sprint 4 Sector Analysis

The Sector Analysis screen provides:

- Sector selection
- Revenue vs ROE comparison
- Bubble visualization
- Market-cap based bubble sizing where available
- Sector company table
- Sector median KPI analysis
- Missing-data handling

### Sprint 4 Capital Allocation

The Capital Allocation screen provides:

- Capital allocation pattern visualization
- Treemap analysis
- Pattern selection
- Company lists by allocation pattern

### Sprint 4 Annual Reports

The Annual Reports screen provides:

- Company search
- Available report years
- Report links
- Report unavailable handling

### Sprint 4 Dashboard Testing

The dashboard was tested to ensure:

- Streamlit launches successfully
- All 8 dashboard screens are available
- Company search works
- Financial metrics load
- Screener filters work
- CSV export is available
- Peer comparison loads
- Trend charts load
- Sector screen handles missing values
- Capital allocation screen loads
- Annual report screen handles unavailable data

The dashboard is launched using:

```bash
streamlit run src/dashboard/app.py