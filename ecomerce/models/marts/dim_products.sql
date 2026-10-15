with products as (
    select * from {{ ref('stg_olist__products') }}
),

translation as (
    select * from {{ ref('stg_olist__product_category_translation') }}
)

select
    products.product_id,
    products.product_category_name,
    translation.product_category,
    products.product_weight_g,
    products.product_length_cm,
    products.product_height_cm,
    products.product_width_cm
from products
left join translation on products.product_category_name = translation.product_category_name
