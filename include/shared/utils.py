import logging

import pandas as pd
import pendulum as pdm

logger = logging.getLogger(__name__)

TIMEZONE = "America/Sao_Paulo"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase and strip column names so raw schemas stay consistent."""
    df.columns = [str(column).strip().lower() for column in df.columns]
    return df


def add_ingestion_metadata(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """Attach lineage columns shared by every raw table."""
    df = df.assign(
        source_name=source_name,
        ingested_at=pdm.now(TIMEZONE).to_iso8601_string(),
    )
    return df
