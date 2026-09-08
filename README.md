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

**🛠️ Technologies Used**

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
│   └── validation_failures.csv
│
├── src/
│   ├── analytics/
│   ├── api/
│   │
│   ├── dashboard/
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
>>>>>>> 8453fd9 (Complete Sprint 2 KPI analytics and testing)

YELLAMELLI PRAGNASREE