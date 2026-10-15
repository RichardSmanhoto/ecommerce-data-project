with items as (
    select * from {{ ref('stg_olist__order_items') }}
)

select
    order_id,
    count(*)                     as item_count,
    count(distinct product_id)   as distinct_product_count,
    count(distinct seller_id)    as distinct_seller_count,
    sum(price)                   as total_item_price,
    sum(freight_value)           as total_freight_value
from items
group by order_id
