import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def extract_basic_info(ticker_symbol):
    logger.info(f"  Extrayendo info basica de {ticker_symbol}")
    tk = yf.Ticker(ticker_symbol)
    info = tk.info
    record = {
        "ticker":         ticker_symbol,
        "industry":       info.get("industry"),
        "sector":         info.get("sector"),
        "employee_count": info.get("fullTimeEmployees"),
        "city":           info.get("city"),
        "phone":          info.get("phone"),
        "state":          info.get("state"),
        "country":        info.get("country"),
        "website":        info.get("website"),
        "address":        info.get("address1"),
    }
    return pd.DataFrame([record])


def extract_daily_prices(ticker_symbol):
    logger.info(f"  Extrayendo precios diarios de {ticker_symbol}")
    tk = yf.Ticker(ticker_symbol)
    df = tk.history(start="2024-01-01", end="2025-12-31")

    if df.empty:
        logger.warning(f"  Sin datos de precios para {ticker_symbol}")
        return pd.DataFrame()

    df = df.reset_index()
    df["ticker"] = ticker_symbol
    df["Date"] = df["Date"].dt.tz_localize(None)

    return df[["ticker", "Date", "Open", "High", "Low", "Close", "Volume"]].rename(
        columns={
            "Date": "date", "Open": "open", "High": "high",
            "Low": "low", "Close": "close", "Volume": "volume",
        }
    )


def extract_fundamentals(ticker_symbol):
    logger.info(f"  Extrayendo fundamentales de {ticker_symbol}")
    tk = yf.Ticker(ticker_symbol)
    bs = tk.balance_sheet

    if bs is None or bs.empty:
        logger.warning(f"  Sin fundamentales para {ticker_symbol}")
        return pd.DataFrame()

    records = []
    for col_date in bs.columns:
        year = col_date.year if hasattr(col_date, "year") else None
        if year and year < 2024:
            continue
        records.append({
            "ticker":           ticker_symbol,
            "date":             col_date,
            "total_assets":     _safe_get(bs, "Total Assets", col_date),
            "total_debt":       _safe_get(bs, "Total Debt", col_date),
            "invested_capital": _safe_get(bs, "Invested Capital", col_date),
            "shares_issued":    _safe_get(bs, "Share Issued", col_date),
        })
    return pd.DataFrame(records)


def extract_holders(ticker_symbol):
    logger.info(f"  Extrayendo tenedores de {ticker_symbol}")
    tk = yf.Ticker(ticker_symbol)
    holders = tk.institutional_holders

    if holders is None or holders.empty:
        logger.warning(f"  Sin tenedores para {ticker_symbol}")
        return pd.DataFrame()

    logger.info(f"    Columnas originales: {list(holders.columns)}")

    result = pd.DataFrame()
    result["ticker"] = [ticker_symbol] * len(holders)

    for col in holders.columns:
        col_lower = col.lower()
        if "holder" in col_lower:
            result["holder"] = holders[col].values
        elif "share" in col_lower:
            result["shares"] = holders[col].values
        elif "date" in col_lower:
            result["date_reported"] = holders[col].values
        elif "value" in col_lower:
            result["value"] = holders[col].values
        elif "%" in col or "pct" in col_lower:
            result["pct_held"] = holders[col].values

    return result

def extract_upgrades_downgrades(ticker_symbol):
    logger.info(f"  Extrayendo calificaciones de {ticker_symbol}")
    tk = yf.Ticker(ticker_symbol)
    upgrades = tk.upgrades_downgrades

    if upgrades is None or upgrades.empty:
        logger.warning(f"  Sin calificaciones para {ticker_symbol}")
        return pd.DataFrame()

    upgrades = upgrades.reset_index()
    upgrades["ticker"] = ticker_symbol
    upgrades = upgrades.rename(columns={
        "GradeDate": "grade_date", "Firm": "firm",
        "ToGrade": "to_grade", "FromGrade": "from_grade",
        "Action": "action",
    })
    upgrades["grade_date"] = pd.to_datetime(upgrades["grade_date"])
    upgrades = upgrades[upgrades["grade_date"] >= "2024-01-01"]
    upgrades["grade_date"] = upgrades["grade_date"].dt.tz_localize(None)

    return upgrades[["ticker", "grade_date", "firm",
                      "to_grade", "from_grade", "action"]]


def _safe_get(df, row_label, col, default=None):
    try:
        val = df.loc[row_label, col]
        if pd.isna(val):
            return default
        return float(val)
    except (KeyError, TypeError):
        return default