import os
from datetime import datetime, timedelta

import pendulum as pdm
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag

from include.config.tags import CRITICAL, Dest, Domain, PipelineType, Schedule, Source

DBT_PROJECT_DIR = os.environ.get("DBT_PROJECT_DIR", "/usr/local/airflow/ecomerce")
DBT_TARGET = os.environ.get("DBT_TARGET", "dev")


@dag(
    dag_id="olist__orders__transform__daily",
    start_date=datetime(2024, 1, 1, tzinfo=pdm.timezone("America/Sao_Paulo")),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "Rick",
        "retries": 2,
        "retry_delay": timedelta(seconds=60),
        "execution_timeout": timedelta(hours=1),
    },
    tags=[Source.OLIST, Dest.LOCAL, Domain.ORDERS, PipelineType.DBT, Schedule.DAILY, CRITICAL],
    description="Transform Olist Parquet into staging/intermediate/marts with dbt.",
)
def olist_orders_transform():
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run --profiles-dir . --target {DBT_TARGET}",
    )
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test --profiles-dir . --target {DBT_TARGET}",
    )

    dbt_run >> dbt_test


olist_orders_transform()
