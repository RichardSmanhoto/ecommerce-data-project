import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_parquet_to_bigquery(
    parquet_path: Path,
    table_id: str,
    keyfile: str | None = None,
    write_disposition: str = "WRITE_TRUNCATE",
) -> str:
    """Load a local Parquet file into a BigQuery table.

    Prepared for when GCP credentials are available; `google-cloud-bigquery`
    is imported lazily so the local Parquet/DuckDB path has no cloud deps.

    Args:
        parquet_path: Local Parquet file to upload.
        table_id: Fully qualified destination, e.g. "project.dataset.table".
        keyfile: Path to a service-account JSON key. Falls back to ADC if None.
        write_disposition: BigQuery write mode (WRITE_TRUNCATE / WRITE_APPEND).

    Returns:
        The destination table_id once the load job completes.
    """
    from google.cloud import bigquery

    if keyfile:
        client = bigquery.Client.from_service_account_json(keyfile)
    else:
        client = bigquery.Client()

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=write_disposition,
        autodetect=True,
    )

    with parquet_path.open("rb") as source_file:
        load_job = client.load_table_from_file(source_file, table_id, job_config=job_config)

    load_job.result()
    logger.info("Loaded %s into %s", parquet_path.name, table_id)
    return table_id
