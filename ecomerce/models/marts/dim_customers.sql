with customers as (
    select * from {{ ref('stg_olist__customers') }}
)

select
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
from customers
