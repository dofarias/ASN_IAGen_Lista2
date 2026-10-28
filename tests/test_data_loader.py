"""Testes da camada de carga de dados (REQ-001 / TEST-001)."""

import hashlib
from pathlib import Path

import pytest

from src.data_loader import DataLoadError, load_data

DATA_DIR = Path(__file__).resolve().parent.parent / "Garden Shop"
REQUIRED = [
    "products.csv",
    "categories.csv",
    "suppliers.csv",
    "orders.csv",
    "order_items.csv",
]


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_load_creates_all_dataframes(data):
    # TEST-001: os cinco DataFrames sao criados e nao ficam vazios.
    assert len(data.products) == 24
    assert len(data.categories) == 8
    assert len(data.suppliers) == 6
    assert len(data.orders) == 24
    assert len(data.order_items) == 48


def test_load_does_not_modify_source_files():
    # TEST-001: os arquivos originais permanecem inalterados apos a carga.
    before = {f: _hash(DATA_DIR / f) for f in REQUIRED}
    load_data(DATA_DIR)
    after = {f: _hash(DATA_DIR / f) for f in REQUIRED}
    assert before == after


def test_booleans_are_normalized(data):
    assert data.products["discontinued"].dtype == bool


def test_missing_file_raises_clear_error(tmp_path):
    # Pasta vazia -> erro de carga com mensagem identificando o arquivo.
    with pytest.raises(DataLoadError) as exc:
        load_data(tmp_path)
    assert "products.csv" in str(exc.value)
