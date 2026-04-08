from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
import os
import logging

logger = logging.getLogger(__name__)

default_args = {
    "owner": "mcasb",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def run_extraction():
    sys.path.insert(0, "/opt/airflow/scripts")
    from main import run_extraction as extract
    extract()


def run_integration():
    sys.path.insert(0, "/opt/airflow/integration")
    from pg_to_clickhouse import run_integration as integrate
    integrate()


with DAG(
    dag_id="mcasb_bank_pipeline",
    default_args=default_args,
    description="Pipeline de datos bancarios - Yahoo Finance",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["mcasb", "banks", "stocks"],
) as dag:

    extract_task = PythonOperator(
        task_id="01_extract_from_api",
        python_callable=run_extraction,
    )

    integrate_task = PythonOperator(
        task_id="02_integrate_to_clickhouse",
        python_callable=run_integration,
    )

    transform_task = BashOperator(
        task_id="03_dbt_transform",
        bash_command="cd /opt/airflow/dbt_project && dbt run --profiles-dir .",
    )

    test_task = BashOperator(
        task_id="04_dbt_test",
        bash_command="cd /opt/airflow/dbt_project && dbt test --profiles-dir .",
    )

    extract_task >> integrate_task >> transform_task >> test_task