import os
import sys
import time
import logging
import pandas as pd
from sqlalchemy import create_engine

sys.path.insert(0, os.path.dirname(__file__))

from tickers import US_BANK_TICKERS
from extractors import (
    extract_basic_info,
    extract_daily_prices,
    extract_fundamentals,
    extract_holders,
    extract_upgrades_downgrades,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB   = os.getenv("PG_DB", "landing_zone")
PG_USER = os.getenv("PG_USER", "admin")
PG_PASS = os.getenv("PG_PASSWORD", "admin123")

DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"

RATE_LIMIT_DELAY = 3


def load_to_postgres(df, table_name):
    if df is None or df.empty:
        logger.info(f"    -> Sin datos para {table_name}, saltando.")
        return
    engine = create_engine(DATABASE_URL)
    df.to_sql(table_name, engine, if_exists="append", index=False)
    logger.info(f"    -> {len(df)} registros cargados en {table_name}")
    engine.dispose()


def run_extraction():
    logger.info("=" * 55)
    logger.info("MCASB PIPELINE - INICIO DE EXTRACCION")
    logger.info(f"Bancos a procesar: {len(US_BANK_TICKERS)}")
    logger.info("=" * 55)

    exitosos = 0
    fallidos = 0

    for i, ticker in enumerate(US_BANK_TICKERS, 1):
        logger.info(f"\n[{i}/{len(US_BANK_TICKERS)}] Procesando {ticker}...")
        errores_ticker = 0

        try:
            info_df = extract_basic_info(ticker)
            load_to_postgres(info_df, "raw_basic_info")
        except Exception as e:
            errores_ticker += 1
            logger.error(f"    ERROR basic_info: {e}")

        try:
            prices_df = extract_daily_prices(ticker)
            load_to_postgres(prices_df, "raw_daily_prices")
        except Exception as e:
            errores_ticker += 1
            logger.error(f"    ERROR daily_prices: {e}")

        try:
            fund_df = extract_fundamentals(ticker)
            load_to_postgres(fund_df, "raw_fundamentals")
        except Exception as e:
            errores_ticker += 1
            logger.error(f"    ERROR fundamentals: {e}")

        try:
            holders_df = extract_holders(ticker)
            load_to_postgres(holders_df, "raw_holders")
        except Exception as e:
            errores_ticker += 1
            logger.error(f"    ERROR holders: {e}")

        try:
            grades_df = extract_upgrades_downgrades(ticker)
            load_to_postgres(grades_df, "raw_upgrades_downgrades")
        except Exception as e:
            errores_ticker += 1
            logger.error(f"    ERROR upgrades: {e}")

        if errores_ticker == 0:
            exitosos += 1
            logger.info(f"  OK {ticker} completado")
        else:
            fallidos += 1
            logger.info(f"  PARCIAL {ticker} - {errores_ticker} errores")

        if i < len(US_BANK_TICKERS):
            logger.info(f"  Esperando {RATE_LIMIT_DELAY}s (rate limit)...")
            time.sleep(RATE_LIMIT_DELAY)

    logger.info("\n" + "=" * 55)
    logger.info("EXTRACCION COMPLETADA")
    logger.info(f"  Exitosos: {exitosos}")
    logger.info(f"  Fallidos: {fallidos}")
    logger.info("=" * 55)


if __name__ == "__main__":
    run_extraction()