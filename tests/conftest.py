"""Fixtures compartilhadas dos testes."""

from pathlib import Path

import pytest

from src.data_loader import GardenShopData, load_data

DATA_DIR = Path(__file__).resolve().parent.parent / "Garden Shop"


@pytest.fixture(scope="session")
def data() -> GardenShopData:
    """Carrega o conjunto completo de dados uma vez por sessao."""
    return load_data(DATA_DIR)
