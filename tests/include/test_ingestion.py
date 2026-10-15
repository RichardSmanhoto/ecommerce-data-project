import pandas as pd

from include.config.datasets import OLIST_DATASETS
from include.extractor.olist_extractor import extract_csv
from include.loader.parquet_loader import write_parquet
from include.shared.utils import add_ingestion_metadata, normalize_columns


def test_normalize_columns_lowercases_and_strips():
    df = pd.DataFrame(columns=[" Order_ID ", "PRICE"])
    assert list(normalize_columns(df).columns) == ["order_id", "price"]


def test_add_ingestion_metadata_adds_lineage_columns():
    df = add_ingestion_metadata(pd.DataFrame({"a": ["1"]}), source_name="orders")
    assert df.loc[0, "source_name"] == "orders"
    assert pd.Timestamp(df.loc[0, "ingested_at"]).tz is not None


def test_extract_csv_keeps_raw_strings(tmp_path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text("﻿Zip_Code,Price\n01310,10.50\n", encoding="utf-8")

    df = extract_csv(csv_file, source_name="sample")

    assert df.loc[0, "zip_code"] == "01310"
    assert df.loc[0, "price"] == "10.50"
    assert {"source_name", "ingested_at"} <= set(df.columns)


def test_write_parquet_round_trip(tmp_path):
    df = pd.DataFrame({"order_id": ["a", "b"]})
    destination = write_parquet(df, tmp_path / "nested" / "orders.parquet")
    pd.testing.assert_frame_equal(pd.read_parquet(destination), df, check_dtype=False)


def test_every_dataset_maps_to_a_csv():
    assert len(OLIST_DATASETS) == 9
    assert all(csv_file.endswith(".csv") for csv_file in OLIST_DATASETS.values())
