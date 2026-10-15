"""DAG integrity tests: every DAG imports cleanly, is tagged and retries at least twice."""

import logging
import os
from contextlib import contextmanager
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DAGS_FOLDER = REPO_ROOT / "dags"

# Local runs: point Cosmos at the repo's dbt project and skip its Airflow-DB-backed dbt ls cache.
os.environ.setdefault("DBT_PROJECT_DIR", str(REPO_ROOT / "ecomerce"))
os.environ.setdefault("AIRFLOW__COSMOS__ENABLE_CACHE_DBT_LS", "False")
os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")

pytest.importorskip("airflow", reason="Airflow only installs on Linux; run in WSL or with `astro dev pytest`.")
from airflow.models import DagBag

APPROVED_TAGS = {}
EXPECTED_DAG_IDS = {"olist__orders__ingest__daily", "olist__orders__transform__daily"}


@contextmanager
def suppress_logging(namespace):
    logger = logging.getLogger(namespace)
    old_value = logger.disabled
    logger.disabled = True
    try:
        yield
    finally:
        logger.disabled = old_value


def strip_path_prefix(path):
    return os.path.relpath(path, REPO_ROOT)


with suppress_logging("airflow"):
    DAG_BAG = DagBag(dag_folder=str(DAGS_FOLDER))

# Prepend (None, None) so a test object always exists even when there are no import errors.
IMPORT_ERRORS = [(None, None)] + [(strip_path_prefix(k), v.strip()) for k, v in DAG_BAG.import_errors.items()]
DAGS = [(dag_id, dag, strip_path_prefix(dag.fileloc)) for dag_id, dag in DAG_BAG.dags.items()]


@pytest.mark.parametrize("rel_path,rv", IMPORT_ERRORS, ids=[x[0] for x in IMPORT_ERRORS])
def test_file_imports(rel_path, rv):
    """Test for import errors on a file"""
    if rel_path and rv:
        pytest.fail(f"{rel_path} failed to import with message \n {rv}")


def test_expected_dags_are_loaded():
    assert EXPECTED_DAG_IDS <= set(DAG_BAG.dags), f"missing DAGs: {EXPECTED_DAG_IDS - set(DAG_BAG.dags)}"


@pytest.mark.parametrize("dag_id,dag,fileloc", DAGS, ids=[x[2] for x in DAGS])
def test_dag_tags(dag_id, dag, fileloc):
    """Test if a DAG is tagged and if those tags are in the approved list"""
    assert dag.tags, f"{dag_id} in {fileloc} has no tags"
    if APPROVED_TAGS:
        assert not set(dag.tags) - APPROVED_TAGS


@pytest.mark.parametrize("dag_id,dag,fileloc", DAGS, ids=[x[2] for x in DAGS])
def test_dag_retries(dag_id, dag, fileloc):
    """Test if a DAG has retries set"""
    assert dag.default_args.get("retries", 0) >= 2, f"{dag_id} in {fileloc} must have task retries >= 2."
