with source as (
    select * from {{ source('olist_raw', 'order_items') }}
)

select
    order_id,
    cast(order_item_id as integer)             as order_item_number,
    product_id,
    seller_id,
    try_cast(shipping_limit_date as timestamp) as shipping_limit_at,
    cast(price as double)                      as price,
    cast(freight_value as double)              as freight_value,
    cast(ingested_at as timestamp with time zone) as ingested_at
from source
