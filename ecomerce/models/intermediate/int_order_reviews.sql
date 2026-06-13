with reviews as (
    select * from {{ ref('stg_olist__order_reviews') }}
)

select
    order_id,
    review_id,
    review_score,
    review_created_at,
    review_answered_at
from reviews
qualify row_number() over (partition by order_id order by review_created_at desc) = 1
