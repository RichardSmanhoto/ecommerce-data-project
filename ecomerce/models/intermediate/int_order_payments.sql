with payments as (
    select * from {{ ref('stg_olist__order_payments') }}
)

select
    order_id,
    sum(payment_value)                  as total_payment_value,
    count(*)                            as payment_count,
    max(payment_installments)           as max_installments,
    string_agg(distinct payment_type, ', ') as payment_types
from payments
group by order_id
