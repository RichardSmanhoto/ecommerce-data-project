with sellers as (
    select * from {{ ref('stg_olist__sellers') }}
),

geolocation as (
    select * from {{ ref('stg_olist__geolocation') }}
)

select
    sellers.seller_id,
    sellers.seller_zip_code_prefix,
    sellers.seller_city,
    sellers.seller_state,
    geolocation.latitude  as seller_latitude,
    geolocation.longitude as seller_longitude
from sellers
left join geolocation on sellers.seller_zip_code_prefix = geolocation.zip_code_prefix
