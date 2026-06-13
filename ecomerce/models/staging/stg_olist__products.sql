with source as (
    select * from {{ source('olist_raw', 'products') }}
)

select
    product_id,
    product_category_name,
    try_cast(product_weight_g as integer) as product_weight_g,
    try_cast(product_length_cm as integer) as product_length_cm,
    try_cast(product_height_cm as integer) as product_height_cm,
    try_cast(product_width_cm as integer)  as product_width_cm,
    ingested_at
from source
