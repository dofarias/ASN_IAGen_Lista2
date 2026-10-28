"""Dashboard de Gestao de Estoque - Garden Shop (Streamlit).

Camada de apresentacao. Toda a regra de calculo vem de src/metrics.py e
src/filters.py; este arquivo apenas carrega os dados e renderiza a interface.

Executar com:
    streamlit run app.py
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src import filters, metrics
from src.data_loader import DataLoadError, load_data

# Cores do semaforo de prioridade (DP-001: decisao de manter vermelho).
PRIORITY_COLORS = {
    "Critico": "#e53935",   # vermelho
    "Urgente": "#fb8c00",   # laranja
    "Atencao": "#fdd835",   # amarelo
}

# Rotulos amigaveis das colunas da tabela de prioridade.
COLUMN_LABELS = {
    "priority": "Prioridade",
    "product_name": "Produto",
    "category_name": "Categoria",
    "quantity_on_hand": "Estoque atual",
    "reorder_level": "Nivel de reposicao",
    "deficit": "Deficit",
    "sales_volume": "Vendas (sem cancelados)",
    "stock_value": "Valor do estoque (R$)",
    "supplier_name": "Fornecedor",
    "contact_email": "E-mail do fornecedor",
}


@st.cache_data
def get_data():
    """Carrega os dados uma vez (cache do Streamlit)."""
    return load_data()


def style_priority(table: pd.DataFrame):
    """Aplica a cor do semaforo na coluna de prioridade."""
    def color_cell(val):
        color = PRIORITY_COLORS.get(val, "")
        if not color:
            return ""
        text = "#000000" if val == "Atencao" else "#ffffff"
        return f"background-color: {color}; color: {text};"

    return table.style.map(color_cell, subset=["Prioridade"])


def main() -> None:
    st.set_page_config(
        page_title="Estoque Garden Shop", page_icon="🪴", layout="wide"
    )
    st.title("🪴 Dashboard de Gestao de Estoque - Garden Shop")
    st.caption(
        "Posicao atual do estoque e demanda (pedidos cancelados nao contam "
        "como venda). Produtos descontinuados nao recebem recomendacao."
    )

    # Carga de dados com tratamento de erro (REQ-001 / REQ-010).
    try:
        data = get_data()
    except DataLoadError as exc:
        st.error(f"Erro ao carregar os dados: {exc}")
        st.stop()

    # --- Filtros (REQ-009): afetam KPIs, tabela e grafico ---
    st.sidebar.header("Filtros")
    category = st.sidebar.selectbox(
        "Categoria", filters.category_options(data.categories)
    )
    supplier = st.sidebar.selectbox(
        "Fornecedor", filters.supplier_options(data.suppliers)
    )

    products = filters.filter_products(
        data.products, data.categories, data.suppliers,
        category_name=category, supplier_name=supplier,
    )

    if products.empty:
        st.warning(
            "Nenhum produto corresponde aos filtros selecionados. "
            "Ajuste a categoria ou o fornecedor."
        )
        st.stop()

    # IDs de produtos do subconjunto, para restringir as vendas (REQ-009).
    product_ids = set(products["product_id"])
    order_items = data.order_items[data.order_items["product_id"].isin(product_ids)]

    # --- KPIs (REQ-002 a REQ-005) ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Produtos ativos", metrics.total_active_products(products))
    k2.metric("Em alerta de reposicao", metrics.products_in_alert(products))
    k3.metric("Estoque zerado", metrics.out_of_stock_products(products))
    k4.metric("Valor do estoque (R$)", f"{metrics.total_stock_value(products):,.2f}")

    st.divider()

    # --- Tabela de prioridade (REQ-006/REQ-007) ---
    st.subheader("Prioridade de reposicao")
    table = metrics.priority_table(
        products, data.categories, data.suppliers, data.orders, order_items
    )
    if table.empty:
        st.info("Nenhum produto em alerta de reposicao para esta selecao.")
    else:
        display = table.copy()
        display["contact_email"] = display["contact_email"].fillna("-")
        display = display.rename(columns=COLUMN_LABELS)
        st.dataframe(
            style_priority(display),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "Semaforo: Critico (estoque zerado) - Urgente (alto volume "
            "de vendas) - Atencao."
        )

    st.divider()

    # --- Grafico de volume de vendas (REQ-008) ---
    st.subheader("Volume de vendas por produto (pedidos nao cancelados)")
    sales = metrics.sales_volume_by_product(data.orders, order_items)
    if sales.empty or sales["sales_volume"].sum() == 0:
        st.info("Sem vendas efetivas registradas para esta selecao.")
    else:
        sales = sales.merge(
            products[["product_id", "product_name"]], on="product_id", how="left"
        )
        top = (
            sales.sort_values("sales_volume", ascending=False)
            .head(10)
            .set_index("product_name")["sales_volume"]
        )
        st.bar_chart(top)
        st.caption("Top 10 produtos por unidades vendidas.")


if __name__ == "__main__":
    main()
