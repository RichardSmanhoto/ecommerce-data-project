import logging
from pathlib import Path

import pandas as pd

from include.shared.utils import add_ingestion_metadata, normalize_columns

logger = logging.getLogger(__name__)


def extract_csv(file_path: Path, source_name: str) -> pd.DataFrame:
    """Read a raw Olist CSV as strings and attach ingestion metadata.

    Every column is kept as string so the raw layer never loses precision to
    type inference; dbt staging casts each field to its final type.
    """
    df = pd.read_csv(file_path, dtype=str, encoding="utf-8-sig")
    df = normalize_columns(df)
    df = add_ingestion_metadata(df, source_name)

    logger.info("Extracted %s rows from %s", len(df), file_path.name)
    return df
