with source as (
    select * from {{ source('olist_raw', 'product_category_translation') }}
)

select
    product_category_name,
    product_category_name_english as product_category,
    cast(ingested_at as timestamp with time zone) as ingested_at
from source
