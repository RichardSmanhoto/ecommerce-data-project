from airflow.sdk import dag, task, task_group, Variable
from datetime import datetime, timedelta

from dags.olist_orders_load import olist_orders_elt

@dag(
    dag_id="olist_orders_transform",
    start_date=datetime(2024, 6, 1),
    schedule="@daily",
    catchup=False,
    default_args={
        "owner": "Rick",
        "retries": 3,
        "retry_delay": timedelta(seconds=60),
        "execution_timeout": timedelta(hours=1)
    },
    tags=["olist", "orders", "transform"],
    description="Transform pipeline for Olist orders data"
)
def olist_orders_transform():
    
    @task
    def ingestion_data():
        pass

    
    ingestion = ingestion_data()
    
olist_orders_transform()