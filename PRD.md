# PRD — Dashboard de Gestão de Estoque da Garden Shop

> **Objetivo:** definir o problema, os usuários, os objetivos e os requisitos do dashboard de estoque antes de iniciar a implementação. Este documento é a referência de produto; o comportamento técnico detalhado está em `SPEC.md`.

## 1. Identificação do projeto

- **Nome do projeto:** Dashboard de Gestão de Estoque — Garden Shop
- **Versão do documento:** 1.0
- **Status:** Rascunho
- **Responsável:** Daniele Farias
- **Repositório:** https://github.com/dofarias/ASN_IAGen_Lista2
- **Data:** 2026-10-28

## 2. Visão geral

### 2.1. Contexto

A Garden Shop é uma loja virtual de produtos de jardinagem (plantas, sementes, ferramentas, vasos, substratos, itens de irrigação, fertilizantes e decoração). A gestão acompanha o estoque de forma manual e fragmentada, cruzando planilhas de produtos, pedidos e fornecedores para decidir o que comprar.

Na Aula 1 foi elaborada uma proposta de dashboard de estoque (documento `IAGP_Lista1-Daniele_Farias.docx`). Esta entrega dá continuidade à proposta, transformando-a em uma **versão funcional** do dashboard, documentada e implementada com apoio de IA generativa.

### 2.2. Problema

A equipe de gestão não tem uma visão única e atualizada da situação do estoque. Isso dificulta responder com rapidez a perguntas operacionais como:

- Quais produtos estão abaixo do nível de reposição recomendado?
- Quais produtos estão com estoque zerado?
- Quais produtos vendem mais e, por isso, exigem atenção à disponibilidade?
- Qual é o valor de capital imobilizado no estoque atual?
- A quais fornecedores recorrer para repor os itens em alerta?

Sem essa visão, há risco de ruptura de estoque em itens de alta demanda e de compras desnecessárias em itens descontinuados.

### 2.3. Solução proposta

Um dashboard interativo que consolida os dados de produtos, categorias, fornecedores e pedidos em uma única tela, com indicadores de alto nível, filtros por categoria e fornecedor, uma tabela acionável de prioridade de reposição e um gráfico de volume de vendas por produto. A execução é local (não é necessário hospedar na internet).

### 2.4. Proposta de valor

Substituir o monitoramento manual por uma leitura visual e confiável que apoie decisões de compra e reposição, priorizando os produtos de maior risco operacional.

## 3. Objetivos e resultados esperados

### 3.1. Objetivos

- Mostrar, em uma tela, a situação atual do estoque com indicadores claros.
- Destacar os produtos que precisam de reposição, ordenados por prioridade.
- Relacionar cada produto em alerta ao seu fornecedor para apoiar a compra.
- Evidenciar o volume de vendas por produto, considerando apenas vendas efetivas.
- Entregar uma base funcional, testada e coerente com os dados disponíveis, que possa evoluir.

### 3.2. Indicadores de sucesso

| Indicador | Situação atual | Meta | Como medir |
| --- | --- | --- | --- |
| Tempo para identificar itens em alerta | Consulta manual a múltiplas planilhas | Leitura direta no dashboard | Abrir o dashboard e ler o KPI "Produtos em alerta" e a tabela de prioridade |
| Correção dos indicadores calculados | Não verificada | 100% dos KPIs e da tabela coerentes com o cálculo manual sobre um recorte dos CSVs | Testes automatizados (pytest) sobre recortes definidos na `SPEC.md` |

Observação: não há meta numérica de negócio definida pela gestão (ex.: reduzir X% de rupturas). A medição de sucesso é a correção dos cálculos e a disponibilidade das informações, não uma meta operacional inventada.

### 3.3. Critérios de sucesso

- Os quatro KPIs, a tabela de prioridade e o gráfico de vendas são exibidos com os dados carregados.
- Os filtros de categoria e fornecedor alteram, de forma consistente, KPIs, tabela e gráfico.
- Os valores calculados batem com a verificação manual sobre o recorte definido na `SPEC.md`.
- Casos sem dados (filtro sem resultados, produto sem vendas) são tratados sem erro e com mensagem clara.

## 4. Usuários e necessidades

### 4.1. Público-alvo

Equipe de gestão da Garden Shop, em especial:

- **Gestor de compras:** decide o que repor e com qual fornecedor.
- **Analista de estoque:** monitora níveis, identifica rupturas e acompanha a demanda.

### 4.2. Necessidades dos usuários

- Como gestor de compras, quero ver os produtos em alerta com estoque, déficit e fornecedor, para decidir a reposição sem abrir outras planilhas.
- Como analista de estoque, quero ver quais produtos têm estoque zerado, para priorizar os casos de ruptura total.
- Como gestor, quero filtrar por categoria e fornecedor, para analisar um recorte específico e negociar compras.
- Como analista, quero ver o volume de vendas efetivas por produto, para cruzar demanda com disponibilidade.

### 4.3. Jornada principal

1. O usuário abre o dashboard localmente; os dados dos CSVs são carregados automaticamente.
2. Lê os quatro KPIs no topo para ter a visão geral.
3. Aplica filtros de categoria e/ou fornecedor conforme sua análise.
4. Consulta a tabela de prioridade de reposição (ordenada por urgência) e o gráfico de volume de vendas.
5. Usa as informações (déficit, fornecedor, demanda) para decidir a reposição.

## 5. Escopo do produto

### 5.1. Incluído no escopo (primeira entrega)

- **Quatro indicadores (KPIs):** Total de produtos ativos, Produtos em alerta de reposição, Produtos com estoque zerado e Valor total do estoque (ao custo).
- **Dois filtros:** Categoria e Fornecedor, afetando KPIs, tabela e gráfico.
- **Tabela de Prioridade de Reposição:** produtos ativos em alerta, com classificação de prioridade (semáforo).
- **Gráfico de Volume de Vendas por Produto:** soma de unidades vendidas em pedidos não cancelados (top N).

### 5.2. Fora do escopo (possibilidades futuras)

- Gráfico de rosca de alertas por categoria.
- Gráfico de valor do estoque por categoria.
- Tabela dedicada de fornecedores associados a produtos em alerta.
- Filtros adicionais de status do estoque e de "incluir descontinuados".
- Cross-filtering por clique nos gráficos, tooltips ricos e exportação para Excel.
- Curva ABC, análise de margem de contribuição, previsão de demanda e sazonalidade (inviáveis ou pouco confiáveis com o volume de dados atual).

### 5.3. Premissas

- Os seis CSVs e o dicionário de dados da Aula 1 estão disponíveis e são a única fonte de dados.
- `quantity_on_hand` representa o estoque atual; não há histórico de movimentações nem prazo de entrega dos fornecedores.
- `reorder_level` cadastrado em `products` é o limiar oficial de alerta de reposição.

### 5.4. Restrições

- **Tecnologia:** Python + Streamlit (dashboard), pandas (cálculos), pytest (testes).
- **Dados:** devem ser preservados em seu estado original; apenas leitura e seleção dos campos necessários.
- **Execução:** local é suficiente; não é obrigatório hospedar na internet.
- **Processo:** abordagem SDD + TDD, com repositório GitHub, branches e PRs (ver `AGENTS.md`).
- **Ambiente:** versão exata do Python a confirmar no ambiente (ver `AGENTS.md`).

## 6. Requisitos funcionais

| ID | Requisito | Prioridade | Critério de aceitação |
| --- | --- | --- | --- |
| RF-001 | O dashboard deve carregar os seis CSVs e disponibilizá-los para análise sem alterar os arquivos originais. | Must | Ao iniciar, o dashboard exibe os indicadores com os dados carregados; os arquivos CSV permanecem inalterados. |
| RF-002 | O dashboard deve exibir o KPI "Total de produtos ativos" (produtos com `discontinued = false`). | Must | Com a base completa, o KPI exibe 23. |
| RF-003 | O dashboard deve exibir o KPI "Produtos em alerta de reposição" (`quantity_on_hand <= reorder_level` e `discontinued = false`). | Must | Com a base completa, o KPI exibe 5. |
| RF-004 | O dashboard deve exibir o KPI "Produtos com estoque zerado" (`quantity_on_hand = 0` e `discontinued = false`). | Must | Com a base completa, o KPI exibe 1 (Hanging Basket). |
| RF-005 | O dashboard deve exibir o KPI "Valor total do estoque" (soma de `cost × quantity_on_hand` para produtos ativos). | Must | O valor corresponde ao cálculo manual sobre os produtos ativos. |
| RF-006 | O dashboard deve exibir uma tabela de prioridade com os produtos ativos em alerta, incluindo nome, categoria, estoque atual, nível de reposição, déficit, volume de vendas, valor do estoque e fornecedor. | Must | A tabela lista os 5 produtos em alerta com as colunas descritas e valores coerentes. |
| RF-007 | A tabela de prioridade deve classificar cada produto em Crítico, Urgente ou Atenção conforme a lógica de semáforo. | Should | Cada linha exibe uma classificação coerente com a regra RN-007. |
| RF-008 | O dashboard deve exibir um gráfico de volume de vendas por produto, considerando apenas pedidos não cancelados. | Must | O gráfico mostra as unidades vendidas por produto; o pedido cancelado não é contabilizado. |
| RF-009 | O dashboard deve oferecer filtro por categoria, aplicado a KPIs, tabela e gráfico. | Must | Ao selecionar uma categoria, todos os elementos passam a refletir apenas essa categoria. |
| RF-010 | O dashboard deve oferecer filtro por fornecedor, aplicado a KPIs, tabela e gráfico. | Must | Ao selecionar um fornecedor, todos os elementos passam a refletir apenas esse fornecedor. |
| RF-011 | O dashboard deve tratar graciosamente filtros sem resultados e produtos sem vendas. | Should | Filtro sem resultados exibe estado vazio com mensagem; produto sem vendas aparece com volume 0, sem erro. |

Prioridades: Must (obrigatório), Should (importante), Could (desejável). Os critérios de aceitação descrevem resultados observáveis.

## 7. Requisitos não funcionais

| ID | Categoria | Requisito | Critério de verificação |
| --- | --- | --- | --- |
| RNF-001 | Correção | As regras de cálculo devem ser verificadas por testes automatizados antes da implementação da UI. | `pytest` passa para os cenários definidos na `SPEC.md`. |
| RNF-002 | Integridade dos dados | Os CSVs originais não devem ser modificados pela aplicação. | Comparação dos arquivos antes e depois da execução; a aplicação apenas lê os dados. |
| RNF-003 | Usabilidade | O dashboard deve ser legível em tela cheia e em monitor menor, com os elementos mais urgentes no topo. | Inspeção visual do layout; print do dashboard em execução. |
| RNF-004 | Portabilidade | O projeto deve ser executável em outra máquina seguindo o `AGENTS.md`, com caminhos de dados configuráveis. | Instalação e execução a partir das instruções documentadas. |
| RNF-005 | Manutenibilidade | A lógica de cálculo deve ficar separada da camada de apresentação. | Módulo de dados/cálculo independente do arquivo Streamlit, coberto por testes. |

## 8. Dados e integrações

- **Fontes de dados:** `products.csv`, `categories.csv`, `suppliers.csv`, `orders.csv`, `order_items.csv`, `customers.csv` e o dicionário `garden_shop_dicionario_dados.xlsx` (referência).
- **Entradas:** arquivos CSV lidos em modo somente leitura.
- **Saídas:** indicadores, tabela e gráfico renderizados na interface; nenhum arquivo de dados é gravado.
- **Integrações externas:** nenhuma.
- **Dados sensíveis:** os CSVs contêm nomes, e-mails e telefones de clientes (`customers.csv`). A primeira entrega **não** utiliza dados de clientes; esses campos não são exibidos no dashboard.
- **Observação de dicionário:** o dicionário descreve as datas de `orders` no formato `DD/MM/AAAA`, mas os CSVs reais usam `AAAA-MM-DD` (ISO). O tratamento deve seguir o formato real dos arquivos. Divergência registrada em DP-002.

## 9. Regras de negócio

- **RN-001 — Vendas efetivas:** pedidos com `status = 'cancelled'` não compõem vendas. Pedidos `shipped`, `pending` e `processing` são considerados vendas efetivas (demanda confirmada).
- **RN-002 — Volume de vendas:** volume de vendas de um produto é a soma de `quantity` em `order_items` vinculados a pedidos não cancelados.
- **RN-003 — Produto em alerta:** `quantity_on_hand <= reorder_level` e `discontinued = false`.
- **RN-004 — Produto crítico (estoque zerado):** `quantity_on_hand = 0`. É um subconjunto mais grave de "em alerta", não uma categoria separada.
- **RN-005 — Descontinuados:** produtos com `discontinued = true` não recebem recomendação de reposição e não entram nos KPIs de produtos ativos.
- **RN-006 — Valor do estoque:** `cost × quantity_on_hand`, considerando apenas produtos ativos. Usa custo (capital investido), não preço de venda.
- **RN-007 — Prioridade (semáforo):** Crítico (`quantity_on_hand = 0`); Urgente (`0 < quantity_on_hand <= reorder_level` com volume de vendas alto); Atenção (`0 < quantity_on_hand <= reorder_level` com volume de vendas baixo ou médio).
- **RN-008 — Prevenção de duplicação:** a posição de estoque vem de `products` (uma linha por produto); o volume de vendas é agregado por produto a partir de `order_items` **antes** de qualquer junção com `products`, para não multiplicar saldos nem valores.

> **Decisão do usuário sobre cores:** o enunciado da Lista 2 pede para não usar a cor vermelha (reservada às correções). O usuário optou por **manter** o semáforo da Lista 1 nas cores vermelho/laranja/amarelo. Esta decisão diverge da instrução do enunciado e está registrada como tal em DP-001, para permitir revisão futura.

## 10. Fluxos e exceções

### 10.1. Fluxo principal

Carregamento dos dados → cálculo dos KPIs → aplicação dos filtros selecionados → renderização de KPIs, tabela de prioridade e gráfico de vendas.

### 10.2. Fluxos alternativos

- Usuário aplica filtro de categoria e/ou fornecedor: todos os elementos recalculam para o subconjunto.
- Produto em alerta sem vendas registradas: aparece na tabela com volume de vendas 0.

### 10.3. Tratamento de erros

- Arquivo de dados ausente ou ilegível: o dashboard exibe mensagem clara indicando o arquivo esperado, em vez de falhar silenciosamente.
- Filtro sem resultados: exibe estado vazio informando que nenhum produto corresponde à seleção.
- Valores ausentes (ex.: e-mail de fornecedor): exibidos como vazio/indicador de ausência, sem quebrar a tabela.

## 11. Experiência e interface

- **Plataforma:** aplicação web local via Streamlit.
- **Estados da interface:** carregando, com dados, vazio (filtro sem resultados) e erro (dados ausentes).
- **Layout:** filtros e KPIs no topo; tabela de prioridade em destaque; gráfico de vendas na sequência. Elementos mais urgentes em posição de maior visibilidade.
- **Cores:** semáforo vermelho/laranja/amarelo para prioridade (ver DP-001).

## 12. Riscos e dependências

| Risco ou dependência | Impacto | Mitigação |
| --- | --- | --- |
| Uso de vermelho diverge do enunciado | Médio | Decisão registrada em DP-001; troca de paleta é ajuste simples caso revisada. |
| Divergência de formato de data no dicionário | Baixo | Tratar pelo formato real (ISO) e documentar (DP-002). |
| Dataset pequeno (24 produtos, 24 pedidos) | Baixo | Escopo limitado a métricas de posição e demanda; análises preditivas ficam fora de escopo. |
| Versão do Python não confirmada | Baixo | Registrar faixa e confirmar no ambiente antes de implementar (AGENTS.md). |

## 13. Entregáveis

- Dashboard funcional em Python + Streamlit, executável localmente.
- Documentos `PRD.md`, `SPEC.md` e `AGENTS.md` no repositório (e `CLAUDE.md` como referência opcional).
- Testes automatizados das regras de cálculo.
- Print do dashboard em execução com dados carregados, mostrando KPIs, filtro e visualização.

## 14. Critérios de conclusão do produto

- Os requisitos obrigatórios (Must) implementados e verificados.
- Critérios de aceitação conferidos, inclusive para filtros sem resultados e produtos sem vendas.
- Testes das regras de cálculo passando.
- Documentação coerente com a aplicação.
- Procedimento de execução validado em ambiente limpo.

## 15. Relação com os documentos técnicos

- **Especificação de referência:** `SPEC.md`
- **Instruções gerais para agentes:** `AGENTS.md`
- **Instruções para Claude Code:** `CLAUDE.md`

## 16. Decisões pendentes

| ID | Questão | Responsável | Status |
| --- | --- | --- | --- |
| DP-001 | Uso do vermelho no semáforo diverge do enunciado ("não usar vermelho"). Usuário optou por manter. | Daniele Farias | Decidido (mantido), passível de revisão |
| DP-002 | Formato de data do dicionário (`DD/MM/AAAA`) diverge dos CSVs reais (`AAAA-MM-DD`). | Daniele Farias | Resolvido: usar formato real (ISO) |
| DP-003 | Versão exata do Python do ambiente. | Daniele Farias | Resolvido: Python 3.13.0 |

## 17. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 1.0 | 2026-10-28 | Criação inicial a partir do brainstorm da Lista 2 |
