class Source:
    OLIST = "olist"


class Dest:
    LOCAL = "dest:local"
    BIGQUERY = "dest:bigquery"


class Domain:
    ORDERS = "domain:orders"
    CUSTOMERS = "domain:customers"
    PRODUCTS = "domain:products"


class PipelineType:
    INGESTION = "type:ingestion"
    DBT = "type:dbt"


class Schedule:
    DAILY = "schedule:daily"
    ON_DEMAND = "schedule:on_demand"


CRITICAL = "critical"
NON_CRITICAL = "non-critical"
