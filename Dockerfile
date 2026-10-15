FROM astrocrpublic.azurecr.io/runtime:3.3-9-python-3.13

# Container paths live here, not in .env: dbt >= 1.12 auto-loads .env, which would break local dbt runs.
ENV DBT_PROJECT_DIR=/usr/local/airflow/ecomerce \
    DBT_PROFILES_DIR=/usr/local/airflow/ecomerce \
    DUCKDB_DIR=/usr/local/airflow/ecomerce \
    OLIST_PARQUET_DIR=/usr/local/airflow/data/parquet
