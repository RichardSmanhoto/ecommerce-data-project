with customers as (
    select * from {{ ref('stg_olist__customers') }}
),

geolocation as (
    select * from {{ ref('stg_olist__geolocation') }}
)

select
    customers.customer_id,
    customers.customer_unique_id,
    customers.customer_zip_code_prefix,
    customers.customer_city,
    customers.customer_state,
    geolocation.latitude  as customer_latitude,
    geolocation.longitude as customer_longitude
from customers
left join geolocation on customers.customer_zip_code_prefix = geolocation.zip_code_prefix
