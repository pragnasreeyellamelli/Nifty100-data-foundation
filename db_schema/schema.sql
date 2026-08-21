PRAGMA foreign_keys = ON;

-- ============================================
-- 1. COMPANIES
-- ============================================
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY,
    company_name TEXT NOT NULL,
    ticker TEXT UNIQUE,
    sector TEXT
);

-- ============================================
-- 2. PROFIT & LOSS
-- ============================================
CREATE TABLE IF NOT EXISTS profit_loss (
    pl_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    year TEXT NOT NULL,
    sales REAL,
    operating_profit REAL,
    opm REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ============================================
-- 3. BALANCE SHEET
-- ============================================
CREATE TABLE IF NOT EXISTS balance_sheet (
    bs_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    year TEXT NOT NULL,
    total_assets REAL,
    total_liabilities REAL,
    total_equity REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ============================================
-- 4. CASH FLOW
-- ============================================
CREATE TABLE IF NOT EXISTS cash_flow (
    cf_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    year TEXT NOT NULL,
    operating_cash_flow REAL,
    investing_cash_flow REAL,
    financing_cash_flow REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ============================================
-- 5. STOCK PRICES
-- ============================================
CREATE TABLE IF NOT EXISTS stock_prices (
    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ============================================
-- 6. FINANCIAL RATIOS
-- ============================================
CREATE TABLE IF NOT EXISTS financial_ratios (
    ratio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    year TEXT NOT NULL,
    pe_ratio REAL,
    pb_ratio REAL,
    roe REAL,
    roa REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ============================================
-- 7. MARKET CAP
-- ============================================
CREATE TABLE IF NOT EXISTS market_cap (
    market_cap_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    market_cap REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ============================================
-- 8. PEER GROUPS
-- ============================================
CREATE TABLE IF NOT EXISTS peer_groups (
    peer_group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    peer_group TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- ============================================
-- 9. SECTORS
-- ============================================
CREATE TABLE IF NOT EXISTS sectors (
    sector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_name TEXT NOT NULL UNIQUE
);

-- ============================================
-- 10. ANALYSIS
-- ============================================
CREATE TABLE IF NOT EXISTS analysis (
    analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    analysis_date TEXT,
    remarks TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);