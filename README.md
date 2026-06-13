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

The Olist source model is built around `orders`, linking customers, items, payments and reviews. Sellers and products attach through the order items, and `geolocation` enriches both customers and sellers by zip-code prefix.

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : places
    ORDERS ||--o{ ORDER_ITEMS : contains
    ORDERS ||--o{ ORDER_PAYMENTS : "paid by"
    ORDERS ||--o{ ORDER_REVIEWS : "reviewed in"
    PRODUCTS ||--o{ ORDER_ITEMS : "sold as"
    SELLERS ||--o{ ORDER_ITEMS : "fulfilled by"
    PRODUCT_CATEGORY_TRANSLATION ||--o{ PRODUCTS : translates
    CUSTOMERS }o--o{ GEOLOCATION : "located by zip"
    SELLERS }o--o{ GEOLOCATION : "located by zip"

    CUSTOMERS {
        string customer_id PK
        string customer_unique_id
        string customer_zip_code_prefix FK
        string customer_city
        string customer_state
    }
    ORDERS {
        string order_id PK
        string customer_id FK
        string order_status
        timestamp purchased_at
        timestamp approved_at
        timestamp delivered_to_customer_at
        timestamp estimated_delivery_at
    }
    ORDER_ITEMS {
        string order_id FK
        int order_item_number
        string product_id FK
        string seller_id FK
        timestamp shipping_limit_at
        double price
        double freight_value
    }
    ORDER_PAYMENTS {
        string order_id FK
        int payment_sequential
        string payment_type
        int payment_installments
        double payment_value
    }
    ORDER_REVIEWS {
        string review_id PK
        string order_id FK
        int review_score
        string review_comment_title
        string review_comment_message
        timestamp review_created_at
        timestamp review_answered_at
    }
    PRODUCTS {
        string product_id PK
        string product_category_name FK
        int product_weight_g
        int product_length_cm
        int product_height_cm
        int product_width_cm
    }
    SELLERS {
        string seller_id PK
        string seller_zip_code_prefix FK
        string seller_city
        string seller_state
    }
    PRODUCT_CATEGORY_TRANSLATION {
        string product_category_name PK
        string product_category
    }
    GEOLOCATION {
        string geolocation_zip_code_prefix
        double geolocation_lat
        double geolocation_lng
        string geolocation_city
        string geolocation_state
    }
```

Downstream, the marts collapse this into a star schema: the core fact `fct_orders` (one row per order) surrounded by `dim_customers` and `dim_products`.

```mermaid
erDiagram
    DIM_CUSTOMERS ||--o{ FCT_ORDERS : "ordered by"
    DIM_PRODUCTS }o--o{ FCT_ORDERS : "appears in"

    FCT_ORDERS {
        string order_id PK
        string customer_id FK
        string customer_state
        string order_status
        timestamp purchased_at
        timestamp delivered_to_customer_at
        int delivery_days
        int delivery_delay_days
        int item_count
        double total_item_price
        double total_freight_value
        double total_payment_value
        int max_installments
        int review_score
    }
    DIM_CUSTOMERS {
        string customer_id PK
        string customer_unique_id
        string customer_zip_code_prefix
        string customer_city
        string customer_state
    }
    DIM_PRODUCTS {
        string product_id PK
        string product_category_name
        string product_category
        int product_weight_g
    }
```

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
