import pandas as pd
from sqlalchemy import create_engine
from clickhouse_driver import Client
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

PG_URL = "postgresql://admin:admin123@localhost:5432/landing_zone"
CH_HOST = "localhost"
CH_USER = "admin"
CH_PASSWORD = "admin123"


def get_pg_data(table_name):
    engine = create_engine(PG_URL)
    df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
    engine.dispose()
    logger.info(f"  Leidos {len(df)} registros de PostgreSQL.{table_name}")
    return df


def load_to_clickhouse(df, table_name):
    if df.empty:
        logger.info(f"  Sin datos para {table_name}, saltando.")
        return

    client = Client(
        host=CH_HOST, user=CH_USER, password=CH_PASSWORD, database="warehouse"
    )

    columns = list(df.columns)
    columns = [c for c in columns if c not in ["id", "loaded_at"]]
    df = df[columns]

    for col in df.columns:
        if df[col].dtype == "datetime64[ns]":
            df[col] = df[col].astype(str)
        if df[col].dtype == "object":
            df[col] = df[col].fillna("")
        else:
            df[col] = df[col].fillna(0)

    data = df.values.tolist()
    col_str = ", ".join(columns)
    client.execute(f"INSERT INTO {table_name} ({col_str}) VALUES", data)
    logger.info(f"  -> {len(data)} registros cargados en ClickHouse.{table_name}")


def run_integration():
    logger.info("=" * 55)
    logger.info("MCASB PIPELINE - INTEGRACION PG -> CLICKHOUSE")
    logger.info("=" * 55)

    tables = {
        "raw_basic_info": "basic_info",
        "raw_daily_prices": "daily_prices",
        "raw_fundamentals": "fundamentals",
        "raw_holders": "holders",
        "raw_upgrades_downgrades": "upgrades_downgrades",
    }

    for pg_table, ch_table in tables.items():
        logger.info(f"\nTransfiriendo {pg_table} -> {ch_table}")
        try:
            df = get_pg_data(pg_table)
            load_to_clickhouse(df, ch_table)
        except Exception as e:
            logger.error(f"  ERROR: {e}")

    logger.info("\n" + "=" * 55)
    logger.info("INTEGRACION COMPLETADA")
    logger.info("=" * 55)


if __name__ == "__main__":
    run_integration()