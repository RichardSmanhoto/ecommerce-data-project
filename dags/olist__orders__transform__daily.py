import os
from datetime import datetime, timedelta
from pathlib import Path

import pendulum as pdm
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import dag
from cosmos import (
    DbtTaskGroup,
    ExecutionConfig,
    ProfileConfig,
    ProjectConfig,
    RenderConfig,
)
from cosmos.constants import LoadMode

from include.config.tags import CRITICAL, Dest, Domain, PipelineType, Schedule, Source

DBT_PROJECT_DIR = Path(os.environ.get("DBT_PROJECT_DIR", "/usr/local/airflow/ecomerce"))
DBT_TARGET = os.environ.get("DBT_TARGET", "dev")
DBT_EXECUTABLE_PATH = os.environ.get("DBT_EXECUTABLE_PATH", "dbt")

profile_config = ProfileConfig(
    profile_name="ecomerce",
    target_name=DBT_TARGET,
    profiles_yml_filepath=DBT_PROJECT_DIR / "profiles.yml",
)

project_config = ProjectConfig(dbt_project_path=DBT_PROJECT_DIR)

execution_config = ExecutionConfig(dbt_executable_path=DBT_EXECUTABLE_PATH)

render_config = RenderConfig(load_method=LoadMode.DBT_LS)


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
    description="Transform Olist Parquet into staging/intermediate/marts with dbt via Cosmos.",
)
def olist_orders_transform():
    start = EmptyOperator(task_id="start")

    transform = DbtTaskGroup(
        group_id="dbt_transform",
        project_config=project_config,
        profile_config=profile_config,
        execution_config=execution_config,
        render_config=render_config,
    )

    end = EmptyOperator(task_id="end")

    start >> transform >> end


olist_orders_transform()
