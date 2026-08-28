<<<<<<< HEAD
**NIFTY 100 Data Foundation**

A complete ETL and data-quality pipeline for processing NIFTY 100 financial data from multiple Excel sources and loading it into a structured SQLite database.

**📌 Project Overview**

This project builds the data foundation for a financial analytics system.

It ingests data from **12 Excel source files**, normalizes and validates the data using Python, and loads the processed data into a SQLite database containing multiple financial datasets.

The project also includes automated data-quality validation, audit reporting, exploratory SQL queries, and unit testing.

**🎯 Sprint 1 Goals**

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
- **SQLite**
- **SQL**
- **Pytest**
- **OpenPyXL**
- **Git & GitHub**

**📂 Project Structure**
=======
# Nifty100 Data Foundation

A complete data ingestion, ETL, validation, and SQLite database project for Nifty 100 financial data.

## Sprint 1 – Data Foundation

This project implements the complete Sprint 1 Data Foundation pipeline:

- Excel data ingestion
- Data normalization
- Data quality validation
- SQLite database creation
- Foreign key validation
- Full data loading
- Exploratory SQL queries
- Automated unit testing
- Load and validation audit reports

## Tech Stack

- Python
- SQLite
- Pandas
- NumPy
- OpenPyXL
- Pytest
- SQL

## Project Structure
>>>>>>> 8453fd9 (Complete Sprint 2 KPI analytics and testing)

```text
nifty100-data-foundation/
│
├── config/
├── data/
<<<<<<< HEAD
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
│   ├── dashboard/
│   └── etl/
│       ├── loader.py
│       ├── normaliser.py
│       └── validator.py
│
├── tests/
│   ├── api/
│   ├── dq/
│   └── etl/
│
├── nifty100.db
├── Makefile
├── requirements.txt
└── README.md

**Author**
Yellamelli Pragna Sree
=======
├── db_schema/
├── docs/
├── notebooks/
├── output/
├── reports/
├── src/
│   ├── etl/
│   └── ...
├── tests/
│   ├── dq/
│   └── etl/
│
├── .gitignore
├── Makefile
├── nifty100.db
├── requirements.txt
└── README.md
>>>>>>> 8453fd9 (Complete Sprint 2 KPI analytics and testing)
