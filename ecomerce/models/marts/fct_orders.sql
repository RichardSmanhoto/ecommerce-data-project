with orders as (
    select * from {{ ref('stg_olist__orders') }}
),

customers as (
    select * from {{ ref('stg_olist__customers') }}
),

payments as (
    select * from {{ ref('int_order_payments') }}
),

items as (
    select * from {{ ref('int_order_items') }}
),

reviews as (
    select * from {{ ref('int_order_reviews') }}
)

select
    orders.order_id,
    orders.customer_id,
    customers.customer_unique_id,
    customers.customer_state,
    customers.customer_city,
    orders.order_status,
    orders.purchased_at,
    orders.approved_at,
    orders.delivered_to_customer_at,
    orders.estimated_delivery_at,
    date_diff('day', orders.purchased_at, orders.delivered_to_customer_at)       as delivery_days,
    date_diff('day', orders.estimated_delivery_at, orders.delivered_to_customer_at) as delivery_delay_days,
    items.item_count,
    items.distinct_product_count,
    items.distinct_seller_count,
    items.total_item_price,
    items.total_freight_value,
    payments.total_payment_value,
    payments.payment_count,
    payments.max_installments,
    payments.payment_types,
    reviews.review_score
from orders
left join customers on orders.customer_id = customers.customer_id
left join payments on orders.order_id = payments.order_id
left join items on orders.order_id = items.order_id
left join reviews on orders.order_id = reviews.order_id
