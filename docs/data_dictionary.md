# Data Dictionary

Columns, types and meaning for every table produced by the pipeline. Types are the DuckDB types in `ecomerce/dev.duckdb`; row counts and null rates come from the full Olist dataset (orders purchased between 2016-09-04 and 2018-10-17).

Diagrams: [source model](img/er_source.png) · [marts star schema](img/er_marts.png) · [dbt lineage](img/lineage.png) (Mermaid sources in [`diagrams/`](diagrams/)).

**Conventions**

- Raw Parquet keeps every column as `VARCHAR`; staging casts to final types and renames timestamps to `*_at`.
- Lineage columns: `source_name` (raw only, logical dataset name) and `ingested_at` (set at ingestion in America/Sao_Paulo; ISO-8601 string in raw, `TIMESTAMP WITH TIME ZONE` in staging).
- **Tests** lists the dbt tests declared in `schema.yml` (`relationships` tests also check every foreign key in staging).

---

## Marts

### `fct_orders`

One row per order, enriched with customer, item, payment and review aggregates. **Grain:** `order_id`. **Rows:** 99,441.

| Column | Type | Null % | Description | Tests |
|---|---|---|---|---|
| `order_id` | VARCHAR | 0 | Order identifier. | unique, not_null |
| `customer_id` | VARCHAR | 0 | Per-order customer key (FK → `dim_customers`). | not_null, relationships |
| `customer_unique_id` | VARCHAR | 0 | Real person behind the order; use it to count distinct customers / repeat buyers. | |
| `customer_state` | VARCHAR | 0 | Customer's state (UF, 2 letters). | |
| `customer_city` | VARCHAR | 0 | Customer's city. | |
| `order_status` | VARCHAR | 0 | `created`, `approved`, `invoiced`, `processing`, `shipped`, `delivered`, `canceled`, `unavailable`. | |
| `purchased_at` | TIMESTAMP | 0 | When the customer placed the order. | |
| `approved_at` | TIMESTAMP | 0.2 | When payment was approved. | |
| `delivered_to_customer_at` | TIMESTAMP | 3.0 | Actual delivery date; null for orders not delivered. | |
| `estimated_delivery_at` | TIMESTAMP | 0 | Delivery date promised at purchase. | |
| `delivery_days` | BIGINT | 3.0 | Days from purchase to delivery. | |
| `delivery_delay_days` | BIGINT | 3.0 | Days delivered after the estimate (negative = early). | |
| `item_count` | BIGINT | 0.8 | Number of order lines. | |
| `distinct_product_count` | BIGINT | 0.8 | Distinct products in the order. | |
| `distinct_seller_count` | BIGINT | 0.8 | Distinct sellers in the order. | |
| `total_item_price` | DOUBLE | 0.8 | Sum of item prices (BRL), excluding freight. | |
| `total_freight_value` | DOUBLE | 0.8 | Sum of freight (BRL). | |
| `total_payment_value` | DOUBLE | 0 | Sum of all payments (BRL). | |
| `payment_count` | BIGINT | 0 | Number of payment records. | |
| `max_installments` | INTEGER | 0 | Highest installment count among the payments. | |
| `payment_types` | VARCHAR | 0 | Comma-separated distinct payment methods. | |
| `review_score` | INTEGER | 0.8 | Score (1–5) of the most recent review. | |

Item columns are null for the 0.8% of orders with no items (mostly `unavailable` / `canceled`).

### `dim_customers`

**Grain:** `customer_id`. **Rows:** 99,441.

| Column | Type | Null % | Description | Tests |
|---|---|---|---|---|
| `customer_id` | VARCHAR | 0 | Per-order customer key. A new one is generated for each order. | unique, not_null |
| `customer_unique_id` | VARCHAR | 0 | Stable identifier of the person. | |
| `customer_zip_code_prefix` | VARCHAR | 0 | First 5 digits of the CEP. Kept as text to preserve leading zeros. | |
| `customer_city` | VARCHAR | 0 | City. | |
| `customer_state` | VARCHAR | 0 | State (UF). | |
| `customer_latitude` | DOUBLE | 0.3 | Latitude of the zip prefix (from `stg_olist__geolocation`). | |
| `customer_longitude` | DOUBLE | 0.3 | Longitude of the zip prefix. | |

### `dim_products`

**Grain:** `product_id`. **Rows:** 32,951.

| Column | Type | Null % | Description | Tests |
|---|---|---|---|---|
| `product_id` | VARCHAR | 0 | Product identifier. | unique, not_null |
| `product_category_name` | VARCHAR | 1.9 | Category in Portuguese. | |
| `product_category` | VARCHAR | 1.9 | Category in English. 13 products have a Portuguese category with no translation. | |
| `product_weight_g` | INTEGER | 0 | Weight in grams. | |
| `product_length_cm` | INTEGER | 0 | Length in cm. | |
| `product_height_cm` | INTEGER | 0 | Height in cm. | |
| `product_width_cm` | INTEGER | 0 | Width in cm. | |

### `dim_sellers`

**Grain:** `seller_id`. **Rows:** 3,095.

| Column | Type | Null % | Description | Tests |
|---|---|---|---|---|
| `seller_id` | VARCHAR | 0 | Seller identifier. | unique, not_null |
| `seller_zip_code_prefix` | VARCHAR | 0 | First 5 digits of the CEP. | |
| `seller_city` | VARCHAR | 0 | City. | |
| `seller_state` | VARCHAR | 0 | State (UF). | |
| `seller_latitude` | DOUBLE | 0.2 | Latitude of the zip prefix (from `stg_olist__geolocation`). | |
| `seller_longitude` | DOUBLE | 0.2 | Longitude of the zip prefix. | |

`dim_products` and `dim_sellers` relate to orders through `stg_olist__order_items` (`order_id` → `product_id`, `seller_id`); `fct_orders` has no direct product or seller key.

---

## Intermediate (ephemeral, one row per `order_id`)

| Model | Columns | Notes |
|---|---|---|
| `int_order_items` | `order_id`, `item_count`, `distinct_product_count`, `distinct_seller_count`, `total_item_price`, `total_freight_value` | Aggregates `stg_olist__order_items`. |
| `int_order_payments` | `order_id`, `total_payment_value`, `payment_count`, `max_installments`, `payment_types` | Aggregates `stg_olist__order_payments`. |
| `int_order_reviews` | `order_id`, `review_id`, `review_score`, `review_created_at`, `review_answered_at` | Keeps the latest review per order. |

---

## Staging

### `stg_olist__orders`: 99,441 rows · grain `order_id`

| Column | Type | Raw column | Description |
|---|---|---|---|
| `order_id` | VARCHAR | `order_id` | Order identifier (unique, not_null). |
| `customer_id` | VARCHAR | `customer_id` | FK → customers (not_null). |
| `order_status` | VARCHAR | `order_status` | Order lifecycle status. |
| `purchased_at` | TIMESTAMP | `order_purchase_timestamp` | Purchase time. |
| `approved_at` | TIMESTAMP | `order_approved_at` | Payment approval time. |
| `delivered_to_carrier_at` | TIMESTAMP | `order_delivered_carrier_date` | Handed to the carrier (1.8% null). |
| `delivered_to_customer_at` | TIMESTAMP | `order_delivered_customer_date` | Delivered to the customer (3.0% null). |
| `estimated_delivery_at` | TIMESTAMP | `order_estimated_delivery_date` | Promised delivery date. |

### `stg_olist__order_items`: 112,650 rows · grain `order_id` + `order_item_number`

| Column | Type | Raw column | Description |
|---|---|---|---|
| `order_id` | VARCHAR | `order_id` | FK → orders. |
| `order_item_number` | INTEGER | `order_item_id` | Line number inside the order (1..n). |
| `product_id` | VARCHAR | `product_id` | FK → products. |
| `seller_id` | VARCHAR | `seller_id` | FK → sellers. |
| `shipping_limit_at` | TIMESTAMP | `shipping_limit_date` | Deadline for the seller to hand over to the carrier. |
| `price` | DOUBLE | `price` | Item price (BRL). |
| `freight_value` | DOUBLE | `freight_value` | Freight for this item (BRL). |

### `stg_olist__order_payments`: 103,886 rows · grain `order_id` + `payment_sequential`

| Column | Type | Raw column | Description |
|---|---|---|---|
| `order_id` | VARCHAR | `order_id` | FK → orders. |
| `payment_sequential` | INTEGER | `payment_sequential` | Sequence when an order uses several payments. |
| `payment_type` | VARCHAR | `payment_type` | `credit_card`, `boleto`, `voucher`, `debit_card`, `not_defined`. |
| `payment_installments` | INTEGER | `payment_installments` | Number of installments. |
| `payment_value` | DOUBLE | `payment_value` | Amount paid (BRL). |

### `stg_olist__order_reviews`: 99,224 rows

| Column | Type | Raw column | Description |
|---|---|---|---|
| `review_id` | VARCHAR | `review_id` | Review identifier. Not unique in the source. |
| `order_id` | VARCHAR | `order_id` | FK → orders. |
| `review_score` | INTEGER | `review_score` | Satisfaction score 1–5. |
| `review_comment_title` | VARCHAR | `review_comment_title` | Optional title (88% null). |
| `review_comment_message` | VARCHAR | `review_comment_message` | Optional comment (59% null). |
| `review_created_at` | TIMESTAMP | `review_creation_date` | When the survey was sent. |
| `review_answered_at` | TIMESTAMP | `review_answer_timestamp` | When the customer answered. |

### `stg_olist__customers`: 99,441 rows · grain `customer_id`

Same columns as `dim_customers`, minus latitude/longitude.

### `stg_olist__products`: 32,951 rows · grain `product_id`

Same columns as `dim_products`, minus `product_category`. Raw columns `product_name_lenght`, `product_description_lenght` and `product_photos_qty` are not carried to staging. The misspelling "lenght" comes from the source.

### `stg_olist__sellers`: 3,095 rows · grain `seller_id`

| Column | Type | Description |
|---|---|---|
| `seller_id` | VARCHAR | Seller identifier. |
| `seller_zip_code_prefix` | VARCHAR | First 5 digits of the CEP. |
| `seller_city` | VARCHAR | City. |
| `seller_state` | VARCHAR | State (UF). |

Feeds `dim_sellers`.

### `stg_olist__product_category_translation`: 71 rows · grain `product_category_name`

| Column | Type | Raw column | Description |
|---|---|---|---|
| `product_category_name` | VARCHAR | `product_category_name` | Category in Portuguese. |
| `product_category` | VARCHAR | `product_category_name_english` | Category in English. |

---

### `stg_olist__geolocation`: 19,015 rows · grain `zip_code_prefix`

Built from the raw `geolocation` file (1,000,163 rows, several points per zip prefix), collapsed to one row per prefix.

| Column | Type | Raw column | Description |
|---|---|---|---|
| `zip_code_prefix` | VARCHAR | `geolocation_zip_code_prefix` | First 5 digits of the CEP (unique, not_null). |
| `latitude` | DOUBLE | `geolocation_lat` | Average latitude of the prefix. |
| `longitude` | DOUBLE | `geolocation_lng` | Average longitude of the prefix. |
| `city` | VARCHAR | `geolocation_city` | Most frequent city name for the prefix. |
| `state` | VARCHAR | `geolocation_state` | Most frequent state for the prefix. |
| `source_point_count` | BIGINT | | Number of raw points averaged. |

About 0.3% of customer and 0.2% of seller zip prefixes are missing from the geolocation file, so their coordinates are null.
