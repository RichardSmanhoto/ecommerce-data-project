# ecomerce (dbt project)

dbt project for the Olist e-commerce pipeline, running on DuckDB (`dbt-duckdb`). The name has one "m" on purpose.

## Layers

| Layer | Materialization | Models |
|-------|-----------------|--------|
| `models/staging` | table | `stg_olist__*`: typed and renamed columns over the raw Parquet sources, one model per source table. |
| `models/intermediate` | ephemeral | `int_order_items`, `int_order_payments`, `int_order_reviews`: per-order aggregations. |
| `models/marts` | table | `fct_orders`, `dim_customers`, `dim_products`, `dim_sellers`. |

Sources (`models/staging/source.yml`) read `$OLIST_PARQUET_DIR/<table>.parquet` (default `../data/parquet`). The DuckDB file is written to `$DUCKDB_DIR` (default: this folder): `dev.duckdb` or `prod.duckdb` depending on the target.

## Running

```bash
cd ecomerce
uv run dbt build --profiles-dir .          # run models + tests
uv run dbt docs generate --profiles-dir .  # column docs come from schema.yml
uv run dbt docs serve --profiles-dir .
```

In Airflow, the `olist__orders__transform__daily` DAG runs this project through Astronomer Cosmos.

Data dictionary and diagrams: [`../docs/data_dictionary.md`](../docs/data_dictionary.md).
