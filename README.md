<div align="center">

# 🛒 Olist E-commerce Data Pipeline

**An end-to-end ELT pipeline for the Olist Brazilian e-commerce dataset — from raw CSVs to dashboard-ready marts.**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-3.2.1-017CEE?logo=apacheairflow&logoColor=white)](https://airflow.apache.org/)
[![Astronomer Cosmos](https://img.shields.io/badge/Astronomer%20Cosmos-1.14-7A4FBF?logo=astronomer&logoColor=white)](https://astronomer.github.io/astronomer-cosmos/)
[![dbt](https://img.shields.io/badge/dbt-1.11-FF694B?logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-local-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org/)
[![BigQuery](https://img.shields.io/badge/BigQuery-planned-669DF6?logo=googlebigquery&logoColor=white)](https://cloud.google.com/bigquery)
[![uv](https://img.shields.io/badge/uv-package%20manager-DE5FE9?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)
[![Status](https://img.shields.io/badge/status-WIP-yellow)]()

</div>

---

## 📖 Overview

This project ingests the public [Olist Brazilian e-commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), turning nine raw CSV files into clean, business-ready data models. Raw CSVs are converted to **local Parquet**, transformed with **dbt** across `staging → intermediate → marts`, and orchestrated by **Apache Airflow** (running dbt through **Astronomer Cosmos**). The final marts feed **Looker Studio** and **Power BI** dashboards.

The warehouse runs on **DuckDB** locally; **BigQuery** is the planned cloud target and the loader is already wired (`include/loader/bigquery_loader.py`) — only credentials are missing.

## 🏗️ Architecture

```mermaid
flowchart LR
    CSV["Olist CSVs<br/>/data/*.csv"] --> ING["Ingestion<br/>(include/)"]
    ING --> PQ[("Local Parquet<br/>data/parquet/")]
    PQ --> DBT["dbt<br/>staging → intermediate → marts"]
    DBT --> DW[("DuckDB<br/>dev.duckdb")]
    DW --> BI["📊 Looker Studio / Power BI"]

    PQ -. planned .-> BQ[("BigQuery")]
    BQ -. planned .-> DBT

    subgraph Orchestration["⛓️ Apache Airflow + Cosmos"]
        ING
        DBT
    end
```

| Stage | Tooling | Output |
|-------|---------|--------|
| **Ingestion** | `include/` Python modules | `data/parquet/*.parquet` (raw, all-string) |
| **Transformation** | dbt (via Cosmos) | `staging` → `intermediate` → `marts` |
| **Warehouse** | DuckDB (BigQuery planned) | `ecomerce/dev.duckdb` |
| **Serving** | Looker Studio / Power BI | Dashboards |

## 🧩 Data Model

> 📌 _Place the data-model (ER) diagram below. Drop the image at `docs/img/data_model.png` and it will render here automatically._

<div align="center">

<!-- ![Data Model](docs/img/data_model.png) -->
_`docs/img/data_model.png` — coming soon_

</div>

The core mart is `fct_orders` (one row per order) surrounded by `dim_customers` and `dim_products`.

## 🛠️ Tech Stack

- **Orchestration:** Apache Airflow 3.2.1 on [Astronomer](https://www.astronomer.io/) (Astro Runtime)
- **dbt orchestration:** Astronomer Cosmos (renders every dbt model as Airflow tasks)
- **Transformation:** dbt 1.11 (`dbt-duckdb`)
- **Warehouse:** DuckDB (local) · BigQuery (planned)
- **Ingestion:** pandas + PyArrow (CSV → Parquet, snappy)
- **Package manager:** [uv](https://docs.astral.sh/uv/)
- **Python:** 3.13

## 📂 Project Structure

```
ecommerce-data-project/
├── dags/                              # Airflow DAGs (<source>__<domain>__<dest>__<schedule>)
│   ├── olist__orders__ingest__daily.py      # CSV → Parquet, then triggers transform
│   └── olist__orders__transform__daily.py   # dbt run + test via Cosmos
├── include/                           # Reusable pipeline modules
│   ├── config/      # datasets map + DAG tag constants
│   ├── extractor/   # CSV → DataFrame
│   ├── loader/      # Parquet writer + (lazy) BigQuery loader
│   ├── shared/      # helpers (column normalization, lineage)
│   └── pipeline/    # ingestion entrypoint (ingest_all)
├── ecomerce/                          # dbt project ("ecomerce", one "m" — intentional)
│   └── models/{staging,intermediate,marts}/
├── notebooks/
│   └── data_validation.ipynb          # data-quality checks against Parquet + marts
├── data/                              # raw CSVs + generated parquet/ (gitignored)
├── docs/img/                          # diagrams (data model)
└── tests/dags/                        # DAG integrity tests
```

## 🚀 Getting Started

### Prerequisites
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli) (to run Airflow locally, Docker-based)

### 1. Install dependencies
```bash
uv sync
```

### 2. Configure environment
```bash
cp .env.example .env   # then fill in the values (BigQuery, dbt paths, ...)
```

### 3. Ingest the raw data (CSV → Parquet)
```bash
uv run python -m include.pipeline.olist_ingestion
```

### 4. Run the dbt transformations
```bash
cd ecomerce
uv run dbt run  --profiles-dir .
uv run dbt test --profiles-dir .
```

### 5. Validate
```bash
uv run jupyter notebook notebooks/data_validation.ipynb
```

## ⛓️ Orchestration (Airflow)

```bash
astro dev start     # start local Airflow (Docker)
astro dev stop
astro dev restart
```

DAG naming convention: `<source>__<domain>__<dest>__<schedule>.py`

| DAG | Trigger | What it does |
|-----|---------|--------------|
| `olist__orders__ingest__daily` | `@daily` | Maps over every Olist dataset (CSV → Parquet), then triggers the transform DAG |
| `olist__orders__transform__daily` | Triggered | Runs `dbt run` + `dbt test` per model via Cosmos |

All DAGs are validated by `tests/dags/` (≥ 2 retries and valid tags required).

## 🧱 dbt Layers

| Layer | Path | Materialization | Purpose |
|-------|------|-----------------|---------|
| **Staging** | `ecomerce/models/staging/` | table | Typed/renamed columns over the raw Parquet sources |
| **Intermediate** | `ecomerce/models/intermediate/` | ephemeral | Per-order aggregations (payments, items, reviews) |
| **Marts** | `ecomerce/models/marts/` | table | Business-ready models: `fct_orders`, `dim_customers`, `dim_products` |

dbt reads the Parquet files directly through DuckDB `external_location` sources (`ecomerce/models/staging/source.yml`).

## 🗺️ Roadmap

- [x] Local ingestion (CSV → Parquet)
- [x] dbt `staging → intermediate → marts` on DuckDB
- [x] Airflow DAGs (ingest + Cosmos transform)
- [x] Data-quality validation notebook
- [ ] Enable BigQuery as the warehouse
- [ ] Looker Studio dashboard
- [ ] Power BI dashboard

## 📜 License

Personal project for educational purposes. The Olist dataset is published under its original [license on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
