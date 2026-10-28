"""Carga e normalizacao dos dados da Garden Shop (REQ-001).

Le os arquivos CSV em modo somente leitura e devolve DataFrames tipados.
Nao escreve nos arquivos de origem. Datas de pedidos sao interpretadas no
formato real dos arquivos (ISO AAAA-MM-DD), conforme decisao DP-002/ADR-003.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# Pasta padrao dos CSVs, relativa a raiz do projeto.
DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "Garden Shop"

# Arquivos necessarios para esta entrega. customers.csv nao e consumido
# (dados de clientes estao fora do escopo - ver PRD/SPEC secao 14).
REQUIRED_FILES = {
    "products": "products.csv",
    "categories": "categories.csv",
    "suppliers": "suppliers.csv",
    "orders": "orders.csv",
    "order_items": "order_items.csv",
}


class DataLoadError(Exception):
    """Erro de carga de dados (ex.: arquivo ausente ou ilegivel)."""


@dataclass
class GardenShopData:
    """Conjunto de DataFrames normalizados da Garden Shop."""

    products: pd.DataFrame
    categories: pd.DataFrame
    suppliers: pd.DataFrame
    orders: pd.DataFrame
    order_items: pd.DataFrame


def _to_bool(series: pd.Series) -> pd.Series:
    """Converte valores textuais (true/false, TRUE/FALSE) em booleano."""
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False})
    )


def _read_csv(data_dir: Path, filename: str) -> pd.DataFrame:
    """Le um CSV tratando ausencia/ilegibilidade com mensagem clara."""
    path = data_dir / filename
    if not path.exists():
        raise DataLoadError(
            f"Arquivo de dados nao encontrado: '{filename}' em '{data_dir}'."
        )
    try:
        return pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001 - mensagem de diagnostico clara
        raise DataLoadError(
            f"Nao foi possivel ler o arquivo '{filename}': {exc}"
        ) from exc


def load_data(data_dir: str | Path | None = None) -> GardenShopData:
    """Carrega e normaliza os dados da Garden Shop.

    Args:
        data_dir: pasta contendo os CSVs. Se None, usa a pasta padrao.

    Returns:
        GardenShopData com os DataFrames tipados.

    Raises:
        DataLoadError: se algum arquivo necessario estiver ausente ou ilegivel.
    """
    base = Path(data_dir) if data_dir is not None else DEFAULT_DATA_DIR

    products = _read_csv(base, REQUIRED_FILES["products"])
    categories = _read_csv(base, REQUIRED_FILES["categories"])
    suppliers = _read_csv(base, REQUIRED_FILES["suppliers"])
    orders = _read_csv(base, REQUIRED_FILES["orders"])
    order_items = _read_csv(base, REQUIRED_FILES["order_items"])

    # Normalizacao de tipos em products.
    products["discontinued"] = _to_bool(products["discontinued"])
    for col in ("price", "cost"):
        products[col] = pd.to_numeric(products[col], errors="coerce")
    for col in ("category_id", "supplier_id", "quantity_on_hand", "reorder_level"):
        products[col] = pd.to_numeric(products[col], errors="coerce").astype("Int64")

    # Datas de orders no formato real dos arquivos (ISO). Ver DP-002/ADR-003.
    orders["order_date"] = pd.to_datetime(
        orders["order_date"], format="%Y-%m-%d", errors="coerce"
    )
    orders["shipped_date"] = pd.to_datetime(
        orders["shipped_date"], format="%Y-%m-%d", errors="coerce"
    )
    orders["status"] = orders["status"].astype(str).str.strip().str.lower()

    # Numericos em order_items.
    order_items["quantity"] = pd.to_numeric(
        order_items["quantity"], errors="coerce"
    ).astype("Int64")
    order_items["unit_price"] = pd.to_numeric(
        order_items["unit_price"], errors="coerce"
    )

    return GardenShopData(
        products=products,
        categories=categories,
        suppliers=suppliers,
        orders=orders,
        order_items=order_items,
    )
