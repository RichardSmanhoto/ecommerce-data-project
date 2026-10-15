with source as (
    select * from {{ source('olist_raw', 'orders') }}
)

select
    order_id,
    customer_id,
    order_status,
    try_cast(order_purchase_timestamp as timestamp)      as purchased_at,
    try_cast(order_approved_at as timestamp)             as approved_at,
    try_cast(order_delivered_carrier_date as timestamp)  as delivered_to_carrier_at,
    try_cast(order_delivered_customer_date as timestamp) as delivered_to_customer_at,
    try_cast(order_estimated_delivery_date as timestamp) as estimated_delivery_at,
    cast(ingested_at as timestamp with time zone) as ingested_at
from source
