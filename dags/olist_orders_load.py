from airflow.sdk import dag, task, task_group, Variable
from datetime import datetime, timedelta

@dag(
    dag_id="olist_orders_elt",
    start_date=datetime(2024, 6, 1),
    schedule="@daily",
    catchup=False,
    default_args={
        "owner": "Rick",
        "retries": 3,
        "retry_delay": timedelta(seconds=60),
        "execution_timeout": timedelta(hours=1)
    },
    tags=["olist", "orders", "elt"],
    description="ETL pipeline for Olist orders data"
)
def olist_orders_elt():
    
    @task
    def ingestion_data():
        pass

    
    ingestion = ingestion_data()
    
olist_orders_elt()