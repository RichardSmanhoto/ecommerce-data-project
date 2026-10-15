import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def write_parquet(data: pd.DataFrame, destination: Path) -> Path:
    """Serialize a DataFrame to a local Parquet file (snappy compression).

    The file written here is the exact artifact later uploaded to BigQuery,
    so the local and cloud paths share one source of truth.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    data.to_parquet(destination, engine="pyarrow", compression="snappy", index=False)

    logger.info("Wrote %s rows to %s", len(data), destination)
    return destination
