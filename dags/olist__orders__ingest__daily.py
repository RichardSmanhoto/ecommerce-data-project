from datetime import datetime, timedelta

import pendulum as pdm
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk import dag, task

from include.config.datasets import OLIST_DATASETS
from include.config.tags import CRITICAL, Dest, Domain, PipelineType, Schedule, Source
from include.pipeline.olist_ingestion import ingest_dataset


@dag(
    dag_id="olist__orders__ingest__daily",
    start_date=datetime(2024, 1, 1, tzinfo=pdm.timezone("America/Sao_Paulo")),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "Rick",
        "retries": 3,
        "retry_delay": timedelta(seconds=60),
        "execution_timeout": timedelta(hours=1),
    },
    tags=[Source.OLIST, Dest.LOCAL, Domain.ORDERS, PipelineType.INGESTION, Schedule.DAILY, CRITICAL],
    description="Ingest raw Olist CSVs into local Parquet, then trigger the dbt transform.",
)
def olist_orders_ingest():
    @task
    def ingest(name: str, csv_file: str) -> str:
        return ingest_dataset(name, csv_file)

    written = ingest.expand_kwargs(
        [{"name": name, "csv_file": csv_file} for name, csv_file in OLIST_DATASETS.items()]
    )

    trigger_transform = TriggerDagRunOperator(
        task_id="trigger_transform",
        trigger_dag_id="olist__orders__transform__daily",
    )

    written >> trigger_transform


olist_orders_ingest()
