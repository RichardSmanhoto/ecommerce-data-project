with source as (
    select * from {{ source('olist_raw', 'sellers') }}
)

select
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state,
    ingested_at
from source
