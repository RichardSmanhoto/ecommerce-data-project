# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ELT pipeline for the Olist Brazilian e-commerce dataset. Raw CSV files in `/data/` are loaded and transformed using Airflow (orchestration) + dbt (transformation) + DuckDB (warehouse).

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
  → Airflow DAG: olist_orders_elt        (dags/olist_orders_load.py)     [load]
  → Airflow DAG: olist_orders_transform  (dags/olist_orders_transform.py) [trigger dbt]
  → dbt models in ecomerce/models/       (DuckDB: dev.duckdb / prod.duckdb)
```

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

- `olist_orders_elt` — daily schedule, loads raw data (owner: Rick)
- `olist_orders_transform` — depends on `olist_orders_elt`, triggers dbt transformations

DAG integrity tests are in `tests/dags/`. All DAGs must have ≥2 retries and valid tags.

### Key Technology Choices

- **Orchestration:** Apache Airflow 3.2.1 on Astronomer (Astro runtime 3.2-3)
- **Warehouse:** DuckDB (local file, via `dbt-duckdb`)
- **Package manager:** `uv` (not pip) — always use `uv run` or `uv sync`
- **Python:** 3.13

## Important Notes

- The dbt project folder is named `ecomerce` (one "m") — intentional naming.
- Raw dataset CSVs are committed to the repo under `/data/` (largest: `olist_geolocation_dataset.csv` ~61 MB).
- `requirements.txt` is legacy; dependency source of truth is `pyproject.toml` + `uv.lock`.
