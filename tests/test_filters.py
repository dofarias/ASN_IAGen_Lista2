"""Testes de filtros e estados vazios (REQ-009/REQ-010 / TEST-010 a TEST-012)."""

from src import filters, metrics


def test_filter_by_category_restricts_products(data):
    # TEST-010: Houseplants -> somente produtos da categoria 1.
    subset = filters.filter_products(
        data.products, data.categories, data.suppliers,
        category_name="Houseplants",
    )
    assert set(subset["category_id"].unique()) == {1}
    # KPIs recalculam sobre o subconjunto: 5 ativos, 1 em alerta (Pothos).
    assert metrics.total_active_products(subset) == 5
    assert metrics.products_in_alert(subset) == 1


def test_filter_by_supplier_restricts_products(data):
    subset = filters.filter_products(
        data.products, data.categories, data.suppliers,
        supplier_name="Ironwood Tools",
    )
    assert set(subset["supplier_id"].unique()) == {5}


def test_combined_filters_apply_intersection(data):
    subset = filters.filter_products(
        data.products, data.categories, data.suppliers,
        category_name="Tools", supplier_name="Ironwood Tools",
    )
    # Tools (cat 3) + Ironwood (sup 5): Pruning Shears, Garden Trowel,
    # Hand Cultivator. Em alerta: apenas Hand Cultivator.
    assert metrics.products_in_alert(subset) == 1


def test_empty_filter_result_is_safe(data):
    # TEST-011: combinacao sem produtos -> conjunto vazio, KPIs = 0, sem erro.
    subset = filters.filter_products(
        data.products, data.categories, data.suppliers,
        category_name="Fertilizer", supplier_name="Ironwood Tools",
    )
    assert len(subset) == 0
    assert metrics.total_active_products(subset) == 0
    assert metrics.products_in_alert(subset) == 0
    assert metrics.total_stock_value(subset) == 0.0


def test_priority_table_includes_product_without_sales(data):
    # TEST-012: Hanging Basket (sem vendas) aparece com volume 0.
    table = metrics.priority_table(
        data.products, data.categories, data.suppliers,
        data.orders, data.order_items,
    )
    row = table.set_index("product_name").loc["Hanging Basket"]
    assert int(row["sales_volume"]) == 0


def test_supplier_without_email_does_not_break_table(data):
    # Ironwood Tools nao tem e-mail; a tabela deve conter a linha sem quebrar.
    table = metrics.priority_table(
        data.products, data.categories, data.suppliers,
        data.orders, data.order_items,
    )
    row = table.set_index("product_name").loc["Hand Cultivator"]
    assert row["supplier_name"] == "Ironwood Tools"
