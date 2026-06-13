# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ELT pipeline for the Olist Brazilian e-commerce dataset. Raw CSVs in `/data/` are ingested to local Parquet (`data/parquet/`), then transformed with dbt. Orchestrated by Airflow (Astronomer). The warehouse is DuckDB locally (`dbt-duckdb`); BigQuery is the planned target (`include/loader/bigquery_loader.py` is ready to enable once GCP credentials exist). Final layer feeds Looker Studio / Power BI dashboards.

## Commands

### Python / Dependencies

```bash
# Install dependencies (uses uv, not pip)
uv sync

# Run tests
uv run pytest tests/
```

### Airflow (via Astronomer CLI)

```bash
# Start the Airflow environment (Docker-based)
astro dev start

# Stop the environment
astro dev stop

# Restart after code changes
astro dev restart
```

### dbt (run from inside the `ecomerce/` directory)

```bash
cd ecomerce

# Run all models
dbt run

# Run a specific model
dbt run --select <model_name>

# Run tests
dbt test

# Generate and serve docs
dbt docs generate && dbt docs serve
```

## Architecture

### Data Flow

```
/data/*.csv (raw Olist CSVs)
  → include/ ingestion (CSV→Parquet, all-string raw)        data/parquet/*.parquet
  → Airflow DAG: olist__orders__ingest__daily    (dags/olist__orders__ingest__daily.py)
  → Airflow DAG: olist__orders__transform__daily (dags/olist__orders__transform__daily.py) [runs dbt]
  → dbt models in ecomerce/models/               (DuckDB: dev.duckdb; BigQuery later)
```

### Ingestion modules (`include/`)

Mirrors the `data-ingestion-service` reference layout:

- `include/config/` — `datasets.py` (table→CSV map, paths), `tags.py` (DAG tag constants).
- `include/extractor/olist_extractor.py` — reads a CSV as strings and adds lineage columns.
- `include/loader/parquet_loader.py` — DataFrame → local Parquet (snappy); `bigquery_loader.py` — lazy-imported BigQuery load, enabled later.
- `include/pipeline/olist_ingestion.py` — `ingest_dataset()` / `ingest_all()`; runnable via `uv run python -m include.pipeline.olist_ingestion`.

dbt sources read the Parquet directly via `external_location` (`ecomerce/models/staging/source.yml`).

### dbt Model Layers

| Layer | Path | Materialization | Purpose |
|-------|------|----------------|---------|
| Staging | `ecomerce/models/staging/` | table | Schema definitions over raw sources |
| Intermediate | `ecomerce/models/intermediate/` | ephemeral | Intermediate transformation logic |
| Marts | `ecomerce/models/marts/` | table | Business-ready final datasets |

### dbt Profiles

Defined in `ecomerce/profiles.yml`. Profile name: `ecomerce`.

- `dev` target: single-threaded, `dev.duckdb`
- `prod` target: 4 threads, `prod.duckdb`

### Airflow DAGs

DAG naming convention: `<source>__<domain>__<dest>__<schedule>.py`.

- `olist__orders__ingest__daily` — daily; ingests every Olist CSV to Parquet (dynamic task mapping), then triggers the transform DAG (owner: Rick).
- `olist__orders__transform__daily` — triggered by the ingest DAG; runs `dbt run` then `dbt test` via `BashOperator` (paths from `DBT_PROJECT_DIR` / `DBT_TARGET` env vars).

DAG integrity tests are in `tests/dags/`. All DAGs must have ≥2 retries and valid tags.

### Key Technology Choices

- **Orchestration:** Apache Airflow 3.2.1 on Astronomer (Astro runtime 3.2-3)
- **Warehouse:** DuckDB (local file, via `dbt-duckdb`)
- **Package manager:** `uv` (not pip) — always use `uv run` or `uv sync`
- **Python:** 3.13

## Important Notes

- The dbt project folder is named `ecomerce` (one "m") — intentional naming.
- `/data/` (CSVs and generated `data/parquet/`) is gitignored; `.env` is gitignored, use `.env.example` as the template.
- `requirements.txt` is legacy; dependency source of truth is `pyproject.toml` + `uv.lock`.
- Code style: clear English names, minimal comments, ruff line-length 120.
