# SPEC — Dashboard de Gestão de Estoque da Garden Shop

> **Objetivo:** transformar os requisitos do `PRD.md` em uma especificação verificável que oriente o planejamento, a implementação e a validação do dashboard.
>
> **Documento de referência do SDD:** esta especificação é a fonte de verdade para os requisitos técnicos e comportamentais aprovados.

## 1. Metadados

- **Projeto:** Dashboard de Gestão de Estoque — Garden Shop
- **Versão da especificação:** 1.0
- **Status:** Draft
- **PRD relacionado:** `PRD.md`
- **Responsável pela aprovação:** Daniele Farias
- **Repositório:** https://github.com/dofarias/ASN_IAGen_Lista2
- **Data:** 2026-10-28

### Status permitidos

`Draft`, `In Review`, `Approved`, `Implemented`, `Verified`, `Deprecated`.

## 2. Objetivo técnico

Carregar seis arquivos CSV da Garden Shop, calcular indicadores de estoque e de vendas segundo regras de negócio definidas, e apresentá-los em um dashboard Streamlit com filtros por categoria e fornecedor. A lógica de cálculo fica isolada da camada de apresentação e é verificada por testes automatizados antes da implementação da interface.

## 3. Referências e rastreabilidade

| Requisito do PRD | Requisito da SPEC | Critério de validação |
| --- | --- | --- |
| RF-001 | REQ-001 (carga de dados) | TEST-001 |
| RF-002 | REQ-002 (KPI produtos ativos) | TEST-002 |
| RF-003 | REQ-003 (KPI em alerta) | TEST-003 |
| RF-004 | REQ-004 (KPI estoque zerado) | TEST-004 |
| RF-005 | REQ-005 (KPI valor do estoque) | TEST-005 |
| RF-006 | REQ-006 (tabela de prioridade) | TEST-006 |
| RF-007 | REQ-007 (semáforo) | TEST-007 |
| RF-008 | REQ-008 (volume de vendas) | TEST-008, TEST-009 |
| RF-009 / RF-010 | REQ-009 (filtros) | TEST-010, TEST-011 |
| RF-011 | REQ-010 (estados vazios) | TEST-011, TEST-012 |

## 4. Escopo técnico

### 4.1. Incluído

- Módulo de carga e normalização dos CSVs.
- Módulo de métricas: KPIs, volume de vendas por produto, tabela de prioridade e classificação de semáforo.
- Módulo de filtros (categoria e fornecedor).
- Aplicação Streamlit que consome os módulos acima.
- Suíte de testes `pytest` para as regras de cálculo.

### 4.2. Excluído

- Persistência ou escrita nos CSVs.
- Visualizações e filtros listados como fora de escopo no `PRD.md` (seção 5.2).
- Dados de clientes (`customers.csv` não é consumido nesta entrega).

## 5. Arquitetura proposta

### 5.1. Visão geral

Três camadas: (1) carga de dados, (2) métricas/regras de negócio, (3) apresentação (Streamlit). A camada de apresentação não contém regra de cálculo; ela chama funções puras da camada de métricas, o que permite testá-las isoladamente.

### 5.2. Componentes

| Componente | Responsabilidade | Entradas | Saídas |
| --- | --- | --- | --- |
| `data_loader` | Ler os CSVs, aplicar tipos e normalizar booleanos/datas | Caminho da pasta de dados | DataFrames de products, categories, suppliers, orders, order_items |
| `metrics` | Calcular KPIs, volume de vendas, tabela de prioridade e semáforo | DataFrames normalizados | KPIs (dict), DataFrame de vendas por produto, DataFrame da tabela de prioridade |
| `filters` | Aplicar filtros de categoria e fornecedor | DataFrames + seleção do usuário | DataFrames filtrados |
| `app` (Streamlit) | Renderizar KPIs, tabela e gráfico; expor filtros | Saídas de `metrics` e `filters` | Interface do dashboard |

> Nomes de módulos são propostos; a organização final pode ser ajustada desde que preserve a separação entre cálculo e apresentação (RNF-005).

### 5.3. Fluxo de execução

Carga dos CSVs → normalização → aplicação dos filtros selecionados → cálculo das métricas sobre o subconjunto filtrado → renderização de KPIs, tabela de prioridade e gráfico de vendas.

### 5.4. Diagrama

```
flowchart TD
    A[CSVs] --> B[data_loader]
    B --> C[filters: categoria + fornecedor]
    C --> D[metrics: KPIs, vendas, prioridade]
    D --> E[Streamlit: KPIs + tabela + grafico]
    B --> F[Erro: arquivo ausente/ilegivel]
```

## 6. Requisitos comportamentais

### REQ-001 — Carga de dados sem alterar origem

- **Origem:** RF-001, RNF-002.
- **Descrição:** o sistema deve ler os seis CSVs em modo somente leitura e disponibilizá-los como DataFrames tipados.
- **Entrada:** caminho da pasta contendo os CSVs (configurável; padrão: `Garden Shop/`).
- **Processamento:** ler CSV; converter `discontinued` e `is_active` para booleano; converter numéricos (`price`, `cost`, `quantity_on_hand`, `reorder_level`, `quantity`, `unit_price`); interpretar datas de `orders` no formato ISO `AAAA-MM-DD` (formato real dos arquivos — ver DP-002).
- **Saída:** DataFrames de products, categories, suppliers, orders, order_items.
- **Erros:** arquivo ausente ou ilegível gera erro tratado com mensagem indicando o arquivo esperado.
- **Critérios de aceitação:**
  - Dado o conjunto completo de CSVs, quando a carga é executada, então os DataFrames são criados e os arquivos permanecem inalterados.
  - Dado um arquivo ausente, quando a carga é executada, então o sistema informa qual arquivo faltou sem travar silenciosamente.

### REQ-002 — KPI Total de produtos ativos

- **Origem:** RF-002.
- **Descrição:** contar produtos com `discontinued = false`.
- **Fórmula:** `count(products[discontinued == false])`.
- **Critérios de aceitação:** dado o conjunto completo, o resultado é **23**.

### REQ-003 — KPI Produtos em alerta de reposição

- **Origem:** RF-003, RN-003.
- **Descrição:** contar produtos ativos com `quantity_on_hand <= reorder_level`.
- **Fórmula:** `count(products[discontinued == false and quantity_on_hand <= reorder_level])`.
- **Critérios de aceitação:** dado o conjunto completo, o resultado é **5** (Pothos 'Golden', Tomato Seeds 'Roma', Hand Cultivator, Hanging Basket, Orchid Food).

### REQ-004 — KPI Produtos com estoque zerado

- **Origem:** RF-004, RN-004.
- **Descrição:** contar produtos ativos com `quantity_on_hand = 0`.
- **Fórmula:** `count(products[discontinued == false and quantity_on_hand == 0])`.
- **Critérios de aceitação:** dado o conjunto completo, o resultado é **1** (Hanging Basket). É subconjunto do KPI de alerta.

### REQ-005 — KPI Valor total do estoque

- **Origem:** RF-005, RN-006.
- **Descrição:** somar `cost × quantity_on_hand` para produtos ativos.
- **Fórmula:** `sum(cost * quantity_on_hand) para products[discontinued == false]`.
- **Critérios de aceitação:** dado o conjunto completo, o resultado é **4731.00** (USD).

### REQ-006 — Tabela de Prioridade de Reposição

- **Origem:** RF-006.
- **Descrição:** listar produtos ativos em alerta com as colunas: nome do produto, categoria, estoque atual, nível de reposição, déficit, volume de vendas (sem cancelados), valor do estoque (`cost × quantity_on_hand`) e fornecedor.
- **Fórmula do déficit:** `reorder_level - quantity_on_hand`.
- **Processamento:** juntar `products` (em alerta) a `categories` e `suppliers` por chave; juntar o volume de vendas já agregado por produto (ver RN-008 e REQ-008).
- **Critérios de aceitação:** dado o conjunto completo, a tabela tem 5 linhas com os valores da seção 9 (exemplo de referência).

### REQ-007 — Classificação de prioridade (semáforo)

- **Origem:** RF-007, RN-007.
- **Descrição:** classificar cada produto em alerta em Crítico, Urgente ou Atenção.
- **Regra:**
  - **Crítico:** `quantity_on_hand == 0`.
  - **Urgente:** `0 < quantity_on_hand <= reorder_level` e volume de vendas **alto**.
  - **Atenção:** `0 < quantity_on_hand <= reorder_level` e volume de vendas **baixo ou médio**.
- **Definição de "volume alto":** limiar explícito a ser fixado na implementação e documentado aqui quando definido. Proposta inicial: "alto" = volume de vendas `>= 5` unidades (mediana aproximada dos itens em alerta no conjunto atual). Decisão registrada em SPEC-OPEN-001 até ser confirmada com um teste.
- **Cores:** Crítico = vermelho, Urgente = laranja, Atenção = amarelo (decisão DP-001; diverge do enunciado).
- **Critérios de aceitação:** Hanging Basket (estoque 0) → Crítico; os demais classificados conforme o limiar definido, de forma determinística e coberta por teste.

### REQ-008 — Volume de vendas por produto (sem cancelados)

- **Origem:** RF-008, RN-001, RN-002.
- **Descrição:** somar `quantity` de `order_items` cujos pedidos têm `status != 'cancelled'`.
- **Processamento:** juntar `order_items` a `orders` pela chave `order_id`; descartar itens de pedidos `cancelled`; agrupar por `product_id` e somar `quantity`. A agregação ocorre **antes** de juntar a `products` (RN-008), evitando duplicação de saldos.
- **Saída:** volume de vendas por `product_id` (0 para produtos sem venda efetiva).
- **Critérios de aceitação:**
  - Dado o conjunto completo, Sunflower Seeds = 12 e Terracotta Pot 8in = 9 (dois maiores).
  - Dado que o pedido 17 (`cancelled`) contém 1 unidade de Pruning Shears e o pedido 7 (`processing`) contém 1 unidade do mesmo produto, então o volume de vendas de Pruning Shears é **1** (apenas o pedido não cancelado).

### REQ-009 — Filtros por categoria e fornecedor

- **Origem:** RF-009, RF-010.
- **Descrição:** aplicar filtros de categoria e fornecedor a todos os elementos (KPIs, tabela e gráfico).
- **Processamento:** o filtro restringe o conjunto de produtos considerado; KPIs, tabela e volume de vendas são recalculados sobre o subconjunto. O volume de vendas considera apenas itens de produtos presentes no subconjunto.
- **Critérios de aceitação:**
  - Dado o filtro de categoria "Houseplants", quando aplicado, então KPIs, tabela e gráfico refletem apenas produtos dessa categoria.
  - Dado o filtro de fornecedor, o comportamento é análogo.
  - Filtros combinados aplicam a interseção (categoria E fornecedor).

### REQ-010 — Estados vazios e valores ausentes

- **Origem:** RF-011.
- **Descrição:** tratar filtros sem resultados e dados ausentes sem erro.
- **Critérios de aceitação:**
  - Dado um filtro que não retorna produtos, então o dashboard exibe estado vazio com mensagem, KPIs coerentes (ex.: 0) e sem exceção.
  - Dado um produto em alerta sem vendas (Hanging Basket, volume 0), então ele aparece na tabela com volume 0.
  - Dado um fornecedor sem e-mail cadastrado (ex.: Ironwood Tools), então a coluna de e-mail exibe vazio/indicador de ausência sem quebrar a tabela.

## 7. Contratos de dados

### 7.1. Modelos de dados (campos usados)

| Entidade | Campo | Tipo | Obrigatório | Restrições |
| --- | --- | --- | --- | --- |
| products | product_id | inteiro | Sim | único, 1–24 |
| products | product_name | texto | Sim | não vazio |
| products | category_id | inteiro | Sim | FK categories.category_id |
| products | supplier_id | inteiro | Sim | FK suppliers.supplier_id |
| products | cost | decimal | Sim | >= 0 |
| products | quantity_on_hand | inteiro | Sim | >= 0 |
| products | reorder_level | inteiro | Sim | >= 0 |
| products | discontinued | booleano | Sim | true/false |
| categories | category_id / category_name | inteiro / texto | Sim | 1–8 / nome válido |
| suppliers | supplier_id / supplier_name | inteiro / texto | Sim | único |
| suppliers | contact_email | texto | Não | pode estar ausente |
| orders | order_id | inteiro | Sim | único, 1–24 |
| orders | status | texto | Sim | shipped, pending, processing, cancelled |
| order_items | order_id | inteiro | Sim | FK orders.order_id |
| order_items | product_id | inteiro | Sim | FK products.product_id |
| order_items | quantity | inteiro | Sim | inteiro positivo |

Campos de `products.price`, `order_items.unit_price`, datas e dados de `customers` não são necessários aos cálculos desta entrega; `price` e `unit_price` podem ser carregados mas não participam das métricas definidas.

### 7.2. Contratos de entrada e saída

- **Entrada:** seis CSVs com cabeçalho, separador vírgula, codificação UTF-8.
- **Saída:** estruturas em memória (KPIs como dicionário/valores; tabela e vendas como DataFrames) consumidas pela interface. Nenhuma saída persistida em disco.
- **Erros:** carga com arquivo ausente → mensagem identificando o arquivo.

## 8. Interfaces e integrações

### 8.1. Interface pública

- Aplicação Streamlit executada localmente. Controles: seletor de categoria (lista + "Todas") e seletor de fornecedor (lista + "Todos"). Áreas: KPIs no topo, tabela de prioridade, gráfico de volume de vendas.

### 8.2. Integrações externas

Nenhuma.

### 8.3. Configuração

- Caminho da pasta de dados configurável (padrão relativo ao projeto). Sem segredos nem credenciais.

## 9. Regras de negócio (com valores de referência)

Valores calculados sobre o conjunto completo (verificados):

**Produtos em alerta (ativos):**

| Produto | Categoria | Estoque | Nível reposição | Déficit | Vendas (sem cancelados) | Valor estoque (cost×qty) |
| --- | --- | --- | --- | --- | --- | --- |
| Hanging Basket | Pots & Planters | 0 | 10 | 10 | 0 | 0.00 |
| Hand Cultivator | Tools | 3 | 10 | 7 | 2 | 10.50 |
| Tomato Seeds 'Roma' | Seeds & Bulbs | 5 | 40 | 35 | 4 | 4.50 |
| Orchid Food | Fertilizer | 6 | 10 | 4 | 2 | 24.00 |
| Pothos 'Golden' | Houseplants | 8 | 12 | 4 | 5 | 40.00 |

**Top vendas (sem cancelados), dois maiores:** Sunflower Seeds = 12; Terracotta Pot 8in = 9.

**KPIs (base completa):** ativos = 23; em alerta = 5; zerado = 1; valor total do estoque = 4731.00.

- **RN-001 a RN-008:** idênticas às do `PRD.md` seção 9 (mesma nomenclatura).

## 10. Requisitos não funcionais

- **Correção:** regras de cálculo cobertas por testes (RNF-001).
- **Integridade:** CSVs não são escritos (RNF-002).
- **Manutenibilidade:** cálculo separado da apresentação (RNF-005).
- **Portabilidade:** caminho de dados configurável (RNF-004).

## 11. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas consideradas |
| --- | --- | --- | --- |
| ADR-001 | Python + Streamlit + pandas | Montagem rápida, execução local simples, bom encaixe com TDD via pandas/pytest | Dash/Plotly (mais verboso), ferramenta de BI (sem testes automatizados) |
| ADR-002 | Agregar vendas por produto antes de juntar a products | Evita multiplicar saldos/valores na junção (RN-008) | Juntar primeiro e agregar depois (risco de duplicação) |
| ADR-003 | Interpretar datas de orders como ISO `AAAA-MM-DD` | Formato real dos CSVs, apesar do dicionário indicar DD/MM/AAAA | Seguir o dicionário (incorreto para os arquivos reais) |

## 12. Plano de implementação

### Fase 1 — Carga de dados

- **Objetivo:** `data_loader` lê os CSVs e normaliza tipos.
- **Dependências:** CSVs disponíveis.
- **Verificação:** TEST-001.

### Fase 2 — Métricas (TDD)

- **Objetivo:** KPIs, volume de vendas, tabela de prioridade e semáforo.
- **Dependências:** Fase 1.
- **Tarefas:** para cada regra, escrever o teste com o resultado esperado da seção 9, confirmar que falha, implementar e passar.
- **Verificação:** TEST-002 a TEST-009.

### Fase 3 — Filtros

- **Objetivo:** filtros de categoria e fornecedor aplicados às métricas.
- **Dependências:** Fase 2.
- **Verificação:** TEST-010, TEST-011.

### Fase 4 — Interface Streamlit

- **Objetivo:** renderizar KPIs, tabela e gráfico, com filtros e estados vazios.
- **Dependências:** Fases 2 e 3.
- **Verificação:** inspeção visual e print; TEST-012 para estado vazio na camada de métricas.

## 13. Estratégia de testes

| ID | Cenário | Tipo | Resultado esperado | Requisito |
| --- | --- | --- | --- | --- |
| TEST-001 | Carga do conjunto completo | Unitário | 5 DataFrames criados; arquivos inalterados | REQ-001 |
| TEST-002 | KPI produtos ativos | Unitário | 23 | REQ-002 |
| TEST-003 | KPI em alerta | Unitário | 5 | REQ-003 |
| TEST-004 | KPI estoque zerado | Unitário | 1 (Hanging Basket) | REQ-004 |
| TEST-005 | KPI valor do estoque | Unitário | 4731.00 | REQ-005 |
| TEST-006 | Tabela de prioridade | Unitário | 5 linhas com déficit e valores da seção 9 | REQ-006 |
| TEST-007 | Semáforo | Unitário | Hanging Basket = Crítico; demais conforme limiar | REQ-007 |
| TEST-008 | Volume de vendas (top) | Unitário | Sunflower Seeds = 12; Terracotta Pot 8in = 9 | REQ-008 |
| TEST-009 | Exclusão de cancelado | Unitário | Pruning Shears = 1 (pedido 17 cancelado ignorado) | REQ-008 |
| TEST-010 | Filtro por categoria | Unitário | Houseplants: KPIs/tabela/vendas restritos à categoria | REQ-009 |
| TEST-011 | Filtro sem resultados | Unitário | Conjunto vazio; KPIs = 0; sem exceção | REQ-009, REQ-010 |
| TEST-012 | Produto sem vendas | Unitário | Hanging Basket aparece com volume 0 | REQ-010 |

### Cobertura de validação

Fluxos principais, limites (estoque 0, déficit alto), exclusão de cancelados, filtros sem resultado, produtos sem vendas e prevenção de duplicação na junção.

## 14. Segurança e privacidade

- Dados de clientes (`customers.csv`) não são consumidos nesta entrega; nomes, e-mails e telefones não aparecem no dashboard.
- Nenhum segredo, token ou credencial no código ou nos documentos.
- A aplicação apenas lê os CSVs; não grava dados.

## 15. Observabilidade e operação

- **Execução:** comando documentado em `AGENTS.md` (Streamlit).
- **Diagnóstico:** mensagens claras para arquivo de dados ausente e filtro sem resultados.

## 16. Critérios de conclusão técnica

- Requisitos obrigatórios implementados.
- Testes TEST-001 a TEST-012 passando.
- Tabela e KPIs coerentes com os valores de referência da seção 9.
- Documentação alinhada ao dashboard final.
- Instruções de execução validadas.

## 17. Gestão de mudanças

Alterações relevantes devem identificar o requisito afetado, justificar a mudança, avaliar impacto em código/testes, atualizar critérios de aceitação e registrar a versão. Mudanças de escopo do produto também atualizam o `PRD.md`.

## 18. Pendências

| ID | Descrição | Impacto | Responsável | Status |
| --- | --- | --- | --- | --- |
| SPEC-OPEN-001 | Limiar de "volume de vendas alto" para separar Urgente de Atenção no semáforo. | Médio (afeta classificação de linhas) | Daniele Farias | Resolvido: `>= 5` (`HIGH_SALES_THRESHOLD` em `src/metrics.py`), coberto por teste |
| SPEC-OPEN-002 | Valor de "top N" do gráfico de vendas. | Baixo | Daniele Farias | Resolvido: top 10 (`app.py`) |

## 19. Histórico de versões

| Versão | Data | Alterações | Status |
| --- | --- | --- | --- |
| 1.0 | 2026-10-28 | Criação inicial a partir do brainstorm da Lista 2 | Draft |
| 1.1 | 2026-10-28 | Implementação concluída (data_loader, metrics, filters, app Streamlit); 19 testes pytest passando; SPEC-OPEN-001 e SPEC-OPEN-002 resolvidas | Implemented |
