with source as (
    select * from {{ source('olist_raw', 'order_reviews') }}
)

select
    review_id,
    order_id,
    cast(review_score as integer)                  as review_score,
    review_comment_title,
    review_comment_message,
    try_cast(review_creation_date as timestamp)    as review_created_at,
    try_cast(review_answer_timestamp as timestamp) as review_answered_at,
    cast(ingested_at as timestamp with time zone) as ingested_at
from source
