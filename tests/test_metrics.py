"""Testes das regras de calculo (REQ-002 a REQ-008 / TEST-002 a TEST-009).

Valores de referencia conforme SPEC.md secao 9, verificados sobre os CSVs.
"""

import pytest

from src import metrics


# --- KPIs --------------------------------------------------------------

def test_kpi_total_active_products(data):
    # TEST-002
    assert metrics.total_active_products(data.products) == 23


def test_kpi_products_in_alert(data):
    # TEST-003
    assert metrics.products_in_alert(data.products) == 5


def test_kpi_out_of_stock(data):
    # TEST-004
    assert metrics.out_of_stock_products(data.products) == 1


def test_kpi_total_stock_value(data):
    # TEST-005
    assert metrics.total_stock_value(data.products) == pytest.approx(4731.00)


# --- Volume de vendas --------------------------------------------------

def test_sales_volume_top_products(data):
    # TEST-008: Sunflower Seeds (id 6) = 12 ; Terracotta Pot 8in (id 12) = 9
    sales = metrics.sales_volume_by_product(data.orders, data.order_items)
    top = sales.sort_values("sales_volume", ascending=False).reset_index(drop=True)
    assert int(top.iloc[0]["sales_volume"]) == 12
    assert int(top.iloc[1]["sales_volume"]) == 9


def test_sales_volume_excludes_cancelled(data):
    # TEST-009: Pruning Shears (id 9) aparece no pedido 7 (processing) e no
    # pedido 17 (cancelled). Apenas o pedido nao cancelado conta -> 1.
    sales = metrics.sales_volume_by_product(data.orders, data.order_items)
    by_id = dict(zip(sales["product_id"], sales["sales_volume"]))
    assert int(by_id[9]) == 1


# --- Tabela de prioridade ---------------------------------------------

def test_priority_table_structure_and_values(data):
    # TEST-006
    table = metrics.priority_table(
        data.products, data.categories, data.suppliers,
        data.orders, data.order_items,
    )
    assert len(table) == 5
    row = table.set_index("product_name").loc["Hanging Basket"]
    assert int(row["quantity_on_hand"]) == 0
    assert int(row["reorder_level"]) == 10
    assert int(row["deficit"]) == 10
    assert int(row["sales_volume"]) == 0


def test_priority_table_deficit_values(data):
    table = metrics.priority_table(
        data.products, data.categories, data.suppliers,
        data.orders, data.order_items,
    )
    deficits = dict(zip(table["product_name"], table["deficit"]))
    assert int(deficits["Tomato Seeds 'Roma'"]) == 35
    assert int(deficits["Hand Cultivator"]) == 7


# --- Semaforo ----------------------------------------------------------

def test_priority_label_critical_for_zero_stock(data):
    # TEST-007
    table = metrics.priority_table(
        data.products, data.categories, data.suppliers,
        data.orders, data.order_items,
    )
    labels = dict(zip(table["product_name"], table["priority"]))
    assert labels["Hanging Basket"] == "Critico"


def test_priority_labels_full_classification(data):
    # TEST-007 (completo): RN-007 opcao A, limiar 30% do reorder_level.
    # Hanging Basket: estoque 0 -> Critico
    # Hand Cultivator: 3 de 10 (30%) -> Critico
    # Tomato Seeds 'Roma': 5 de 40 (12,5%) -> Critico
    # Orchid Food: 6 de 10 (60%), vendas 2 -> Atencao
    # Pothos 'Golden': 8 de 12 (67%), vendas 5 -> Urgente
    table = metrics.priority_table(
        data.products, data.categories, data.suppliers,
        data.orders, data.order_items,
    )
    labels = dict(zip(table["product_name"], table["priority"]))
    assert labels["Hanging Basket"] == "Critico"
    assert labels["Hand Cultivator"] == "Critico"
    assert labels["Tomato Seeds 'Roma'"] == "Critico"
    assert labels["Orchid Food"] == "Atencao"
    assert labels["Pothos 'Golden'"] == "Urgente"


def test_priority_label_unit_rules():
    # Verificacao direta da funcao de classificacao.
    assert metrics._priority_label(0, 10, 0) == "Critico"      # zerado
    assert metrics._priority_label(3, 10, 0) == "Critico"      # 30% do minimo
    assert metrics._priority_label(4, 10, 2) == "Atencao"      # 40%, vendas baixas
    assert metrics._priority_label(4, 10, 5) == "Urgente"      # 40%, vendas altas
