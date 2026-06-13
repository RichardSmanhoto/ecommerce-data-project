import logging

from include.config.datasets import DATA_DIR, OLIST_DATASETS, PARQUET_DIR
from include.extractor.olist_extractor import extract_csv
from include.loader.parquet_loader import write_parquet

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def ingest_dataset(name: str, csv_file: str) -> str:
    """Extract one Olist CSV and write it as local Parquet."""
    df = extract_csv(DATA_DIR / csv_file, source_name=name)
    destination = write_parquet(df, PARQUET_DIR / f"{name}.parquet")
    return str(destination)


def ingest_all() -> list[str]:
    """Run the full local ingestion for every configured Olist dataset."""
    written = []
    for name, csv_file in OLIST_DATASETS.items():
        written.append(ingest_dataset(name, csv_file))
    logger.info("Ingestion finished: %s datasets", len(written))
    return written


if __name__ == "__main__":
    ingest_all()
