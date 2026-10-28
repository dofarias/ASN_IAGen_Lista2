"""Filtros por categoria e fornecedor (REQ-009).

O filtro restringe o conjunto de produtos; KPIs, tabela e volume de vendas
sao recalculados sobre o subconjunto (os filtros afetam tudo).
"""

from __future__ import annotations

import pandas as pd

# Rotulos "sem filtro" expostos na interface.
ALL_CATEGORIES = "Todas"
ALL_SUPPLIERS = "Todos"


def filter_products(
    products: pd.DataFrame,
    categories: pd.DataFrame,
    suppliers: pd.DataFrame,
    category_name: str | None = None,
    supplier_name: str | None = None,
) -> pd.DataFrame:
    """Filtra products por nome de categoria e/ou fornecedor.

    Valores None ou os rotulos "Todas"/"Todos" significam sem filtro.
    Filtros combinados aplicam a intersecao (categoria E fornecedor).
    """
    result = products

    if category_name and category_name != ALL_CATEGORIES:
        match = categories.loc[
            categories["category_name"] == category_name, "category_id"
        ]
        result = result[result["category_id"].isin(match)]

    if supplier_name and supplier_name != ALL_SUPPLIERS:
        match = suppliers.loc[
            suppliers["supplier_name"] == supplier_name, "supplier_id"
        ]
        result = result[result["supplier_id"].isin(match)]

    return result


def category_options(categories: pd.DataFrame) -> list[str]:
    """Lista de categorias com a opcao 'Todas' no inicio."""
    return [ALL_CATEGORIES] + sorted(categories["category_name"].tolist())


def supplier_options(suppliers: pd.DataFrame) -> list[str]:
    """Lista de fornecedores com a opcao 'Todos' no inicio."""
    return [ALL_SUPPLIERS] + sorted(suppliers["supplier_name"].tolist())
