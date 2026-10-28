"""Regras de calculo do dashboard (REQ-002 a REQ-008).

Funcoes puras sobre DataFrames, sem dependencia da camada de apresentacao,
para permitir verificacao por testes. Valores de referencia em SPEC.md secao 9.
"""

from __future__ import annotations

import pandas as pd

# Status de pedido que NAO compoem vendas efetivas (RN-001).
CANCELLED_STATUS = "cancelled"

# Limiar de "volume de vendas alto" que separa Urgente de Atencao no
# semaforo (SPEC-OPEN-001). >= 5 unidades.
HIGH_SALES_THRESHOLD = 5

# Fracao do reorder_level abaixo da qual o estoque e considerado "muito
# abaixo do minimo" e o produto e classificado como Critico (RN-007).
# Ex.: 0.30 => estoque <= 30% do nivel de reposicao.
CRITICAL_STOCK_RATIO = 0.30


# --- Helpers -----------------------------------------------------------

def active_products(products: pd.DataFrame) -> pd.DataFrame:
    """Produtos ativos (nao descontinuados) - RN-005."""
    return products[products["discontinued"] == False]  # noqa: E712


def _alert_mask(products: pd.DataFrame) -> pd.Series:
    """Mascara de produtos ativos em alerta (RN-003)."""
    return (products["discontinued"] == False) & (  # noqa: E712
        products["quantity_on_hand"] <= products["reorder_level"]
    )


# --- KPIs --------------------------------------------------------------

def total_active_products(products: pd.DataFrame) -> int:
    """REQ-002: contagem de produtos ativos."""
    return int(len(active_products(products)))


def products_in_alert(products: pd.DataFrame) -> int:
    """REQ-003: produtos ativos com estoque <= nivel de reposicao."""
    return int(_alert_mask(products).sum())


def out_of_stock_products(products: pd.DataFrame) -> int:
    """REQ-004: produtos ativos com estoque zerado."""
    mask = (products["discontinued"] == False) & (  # noqa: E712
        products["quantity_on_hand"] == 0
    )
    return int(mask.sum())


def total_stock_value(products: pd.DataFrame) -> float:
    """REQ-005: soma de cost * quantity_on_hand para produtos ativos."""
    act = active_products(products)
    value = (act["cost"].astype(float) * act["quantity_on_hand"].astype(float)).sum()
    return round(float(value), 2)


# --- Volume de vendas --------------------------------------------------

def sales_volume_by_product(
    orders: pd.DataFrame, order_items: pd.DataFrame
) -> pd.DataFrame:
    """REQ-008: soma de quantity por produto em pedidos nao cancelados.

    A agregacao ocorre ANTES de qualquer juncao com products (RN-008/ADR-002),
    evitando duplicacao de saldos.

    Returns:
        DataFrame com colunas product_id e sales_volume.
    """
    valid_orders = orders.loc[orders["status"] != CANCELLED_STATUS, "order_id"]
    items = order_items[order_items["order_id"].isin(valid_orders)]
    grouped = (
        items.groupby("product_id", as_index=False)["quantity"]
        .sum()
        .rename(columns={"quantity": "sales_volume"})
    )
    grouped["sales_volume"] = grouped["sales_volume"].astype(int)
    return grouped


# --- Tabela de prioridade e semaforo ----------------------------------

def _priority_label(
    quantity_on_hand: int, reorder_level: int, sales_volume: int
) -> str:
    """RN-007: classifica o produto em alerta (Critico/Urgente/Atencao).

    - Critico: estoque zerado OU muito abaixo do minimo
      (quantity_on_hand <= CRITICAL_STOCK_RATIO * reorder_level).
    - Urgente: em alerta com volume de vendas alto (>= HIGH_SALES_THRESHOLD).
    - Atencao: demais produtos em alerta.
    """
    if quantity_on_hand == 0:
        return "Critico"
    if quantity_on_hand <= CRITICAL_STOCK_RATIO * reorder_level:
        return "Critico"
    if sales_volume >= HIGH_SALES_THRESHOLD:
        return "Urgente"
    return "Atencao"


def priority_table(
    products: pd.DataFrame,
    categories: pd.DataFrame,
    suppliers: pd.DataFrame,
    orders: pd.DataFrame,
    order_items: pd.DataFrame,
) -> pd.DataFrame:
    """REQ-006/REQ-007: tabela de produtos ativos em alerta.

    Colunas: product_name, category_name, quantity_on_hand, reorder_level,
    deficit, sales_volume, stock_value, supplier_name, contact_email, priority.
    """
    alert = products[_alert_mask(products)].copy()

    # Volume de vendas agregado por produto (antes da juncao - RN-008).
    sales = sales_volume_by_product(orders, order_items)
    alert = alert.merge(sales, on="product_id", how="left")
    alert["sales_volume"] = alert["sales_volume"].fillna(0).astype(int)

    # Juncoes de contexto (categoria e fornecedor).
    alert = alert.merge(
        categories[["category_id", "category_name"]], on="category_id", how="left"
    )
    alert = alert.merge(
        suppliers[["supplier_id", "supplier_name", "contact_email"]],
        on="supplier_id",
        how="left",
    )

    alert["deficit"] = (
        alert["reorder_level"].astype(int) - alert["quantity_on_hand"].astype(int)
    )
    alert["stock_value"] = (
        alert["cost"].astype(float) * alert["quantity_on_hand"].astype(float)
    ).round(2)
    alert["priority"] = alert.apply(
        lambda r: _priority_label(
            int(r["quantity_on_hand"]),
            int(r["reorder_level"]),
            int(r["sales_volume"]),
        ),
        axis=1,
    )

    # Ordena pela urgencia (maior deficit primeiro, estoque zerado no topo).
    alert = alert.sort_values(
        ["quantity_on_hand", "deficit"], ascending=[True, False]
    ).reset_index(drop=True)

    columns = [
        "product_name",
        "category_name",
        "quantity_on_hand",
        "reorder_level",
        "deficit",
        "sales_volume",
        "stock_value",
        "supplier_name",
        "contact_email",
        "priority",
    ]
    return alert[columns]
