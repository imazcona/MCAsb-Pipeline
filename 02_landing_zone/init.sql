-- =========================================================
-- LANDING ZONE: Tablas para datos crudos de Yahoo Finance
-- Autor: MCASB
-- Estas tablas reciben los datos TAL CUAL salen del API
-- =========================================================

-- 1. Informacion basica de cada banco
CREATE TABLE IF NOT EXISTS raw_basic_info (
    Id            SERIAL PRIMARY KEY,
    ticker        VARCHAR(10) NOT NULL,
    industry      VARCHAR(200),
    sector        VARCHAR(100),
    employee_count INTEGER,
    city          VARCHAR(100),
    phone         VARCHAR(50),
    state         VARCHAR(50),
    country       VARCHAR(50),
    website       VARCHAR(200),
    address       VARCHAR(300),
    loaded_at     TIMESTAMP DEFAULT NOW()
);

-- 2. Precio diario en bolsa
CREATE TABLE IF NOT EXISTS raw_daily_prices (
    id       SERIAL PRIMARY KEY,
    ticker   VARCHAR(10) NOT NULL,
    date     DATE NOT NULL,
    open     NUMERIC(18,6),
    high     NUMERIC(18,6),
    low      NUMERIC(18,6),
    close    NUMERIC(18,6),
    volume   BIGINT,
    loaded_at TIMESTAMP DEFAULT NOW()
);

-- 3. Fundamentales financieros
CREATE TABLE IF NOT EXISTS raw_fundamentals (
    id               SERIAL PRIMARY KEY,
    ticker           VARCHAR(10) NOT NULL,
    date             DATE,
    total_assets     NUMERIC(20,2),
    total_debt       NUMERIC(20,2),
    invested_capital NUMERIC(20,2),
    shares_issued    NUMERIC(20,2),
    loaded_at        TIMESTAMP DEFAULT NOW()
);

-- 4. Tenedores (Holders)
CREATE TABLE IF NOT EXISTS raw_holders (
    id            SERIAL PRIMARY KEY,
    ticker        VARCHAR(10) NOT NULL,
    holder        VARCHAR(300),
    shares        BIGINT,
    date_reported DATE,
    pct_held      NUMERIC(10,6),
    value         NUMERIC(20,2),
    loaded_at     TIMESTAMP DEFAULT NOW()
);

-- 5. Calificaciones (Upgrades/Downgrades)
CREATE TABLE IF NOT EXISTS raw_upgrades_downgrades (
    id          SERIAL PRIMARY KEY,
    ticker      VARCHAR(10) NOT NULL,
    grade_date  DATE,
    firm        VARCHAR(200),
    to_grade    VARCHAR(50),
    from_grade  VARCHAR(50),
    action      VARCHAR(50),
    loaded_at   TIMESTAMP DEFAULT NOW()
);

-- Indices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_prices_ticker_
cat > 03_warehouse/init.sql << 'EOF'
-- =========================================================
-- OLAP WAREHOUSE: Tablas optimizadas para analisis
-- Autor: MCASB
-- ClickHouse es mucho mas rapido que PostgreSQL para reportes
-- =========================================================

CREATE DATABASE IF NOT EXISTS warehouse;

CREATE TABLE IF NOT EXISTS warehouse.basic_info (
    ticker        String,
    industry      Nullable(String),
    sector        Nullable(String),
    employee_count Nullable(Int32),
    city          Nullable(String),
    phone         Nullable(String),
    state         Nullable(String),
    country       Nullable(String),
    website       Nullable(String),
    address       Nullable(String),
    loaded_at     DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY ticker;

CREATE TABLE IF NOT EXISTS warehouse.daily_prices (
    ticker  String,
    date    Date,
    open    Nullable(Float64),
    high    Nullable(Float64),
    low     Nullable(Float64),
    close   Nullable(Float64),
    volume  Nullable(Int64),
    loaded_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY (ticker, date);

CREATE TABLE IF NOT EXISTS warehouse.fundamentals (
    ticker           String,
    date             Date,
    total_assets     Nullable(Float64),
    total_debt       Nullable(Float64),
    invested_capital Nullable(Float64),
    shares_issued    Nullable(Float64),
    loaded_at        DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY (ticker, date);

CREATE TABLE IF NOT EXISTS warehouse.holders (
    ticker        String,
    holder        Nullable(String),
    shares        Nullable(Int64),
    date_reported Nullable(Date),
    pct_held      Nullable(Float64),
    value         Nullable(Float64),
    loaded_at     DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY (ticker, holder);

CREATE TABLE IF NOT EXISTS warehouse.upgrades_downgrades (
    ticker      String,
    grade_date  Nullable(Date),
    firm        Nullable(String),
    to_grade    Nullable(String),
    from_grade  Nullable(String),
    action      Nullable(String),
    loaded_at   DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY (ticker, grade_date);
