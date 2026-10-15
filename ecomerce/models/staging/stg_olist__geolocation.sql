with source as (
    select * from {{ source('olist_raw', 'geolocation') }}
)

-- The raw file has many coordinates per zip prefix; keep one row per prefix.
select
    geolocation_zip_code_prefix          as zip_code_prefix,
    avg(cast(geolocation_lat as double)) as latitude,
    avg(cast(geolocation_lng as double)) as longitude,
    mode(geolocation_city)               as city,
    mode(geolocation_state)              as state,
    count(*)                             as source_point_count,
    max(cast(ingested_at as timestamp with time zone)) as ingested_at
from source
group by geolocation_zip_code_prefix
