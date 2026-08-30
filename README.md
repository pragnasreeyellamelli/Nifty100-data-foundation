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

# 🛠️ Technologies Used

- **Python**
- **Pandas**
- **NumPy**
- **SQLite**
- **SQL**
- **Pytest**
- **OpenPyXL**
- **Git & GitHub**

---

# 📂 Project Structure

```text
nifty100-data-foundation/
│
├── config/
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
│   └── validation_failures.csv
│
├── reports/
│
├── src/
│   ├── analytics/
│   │   ├── cagr.py
│   │   ├── cashflow_kpis.py
│   │   ├── ratio_edge_cases.py
│   │   └── ratios.py
│   │
│   ├── api/
│   ├── dashboard/
│   │
│   └── etl/
│       ├── loader.py
│       ├── normaliser.py
│       └── validator.py
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
