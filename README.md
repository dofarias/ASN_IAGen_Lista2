# Dashboard de Gestao de Estoque - Garden Shop

Dashboard interativo para a equipe de gestao da Garden Shop (loja virtual de
produtos de jardinagem) acompanhar a situacao do estoque: identificar produtos
que precisam de reposicao, medir o valor do estoque, visualizar o volume de
vendas e relacionar itens aos fornecedores.

Projeto da Lista de Exercicios 02 de Inteligencia Artificial Generativa.
Autora: **Daniele Farias**.

## Funcionalidades

- **4 indicadores (KPIs):** produtos ativos, produtos em alerta de reposicao,
  produtos com estoque zerado e valor total do estoque (ao custo).
- **2 filtros:** categoria e fornecedor, que afetam KPIs, tabela e grafico.
- **Tabela de prioridade de reposicao:** produtos em alerta com estoque,
  deficit, vendas, valor, fornecedor e classificacao por semaforo.
- **Grafico de volume de vendas por produto** (pedidos cancelados excluidos).

## Regras de negocio principais

- Pedidos com status `cancelled` nao contam como venda; `shipped`, `pending` e
  `processing` sao considerados demanda efetiva.
- Produto em alerta: `quantity_on_hand <= reorder_level` e nao descontinuado.
- Produto critico: estoque zerado (`quantity_on_hand = 0`).
- Produtos descontinuados nao recebem recomendacao de reposicao.
- Valor do estoque: `cost x quantity_on_hand` (apenas produtos ativos).

Detalhes completos em [`PRD.md`](PRD.md) e [`SPEC.md`](SPEC.md).

## Requisitos

- Python 3.13 (desenvolvido e testado nesta versao; 3.11+ deve funcionar).
- Dependencias em [`requirements.txt`](requirements.txt): streamlit, pandas, pytest.

## Instalacao

Crie e ative um ambiente virtual, depois instale as dependencias.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Windows (cmd):**

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Linux / macOS:**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execucao

Com o ambiente ativado, inicie o dashboard:

```bash
streamlit run app.py
```

A aplicacao abre no navegador em `http://localhost:8501`. Os dados dos CSVs em
`Garden Shop/` sao carregados automaticamente.

## Testes

As regras de calculo sao verificadas por testes automatizados (pytest):

```bash
pytest
```

Os testes validam os valores de referencia da especificacao (ex.: 23 produtos
ativos, 5 em alerta, 1 com estoque zerado, valor total do estoque de 4731.00) e
casos de borda como pedidos cancelados, produtos sem vendas e filtros sem
resultado.

## Estrutura do projeto

```
.
├── app.py                 # Interface Streamlit (apresentacao)
├── src/
│   ├── data_loader.py     # Carga e normalizacao dos CSVs
│   ├── metrics.py         # KPIs, vendas, tabela de prioridade, semaforo
│   └── filters.py         # Filtros de categoria e fornecedor
├── tests/                 # Testes pytest das regras de calculo
├── Garden Shop/           # Dados de origem (CSVs)
├── PRD.md                 # Documento de produto
├── SPEC.md                # Especificacao tecnica
├── AGENTS.md              # Instrucoes para agentes de IA
├── CLAUDE.md              # Instrucoes para Claude Code
└── requirements.txt       # Dependencias
```

A camada de calculo (`src/`) e separada da apresentacao (`app.py`) para permitir
os testes automatizados.

## Dados

Dataset de pratica *Garden Shop SQL Practice Dataset*: `products.csv`,
`categories.csv`, `suppliers.csv`, `orders.csv`, `order_items.csv` e
`customers.csv`, com o dicionario `garden_shop_dicionario_dados.xlsx`. A
aplicacao apenas le os arquivos; nao os altera.
