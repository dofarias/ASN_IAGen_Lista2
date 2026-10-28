# CLAUDE.md — Instruções para Claude Code

> **Projeto:** Dashboard de Gestão de Estoque — Garden Shop
> **Responsável:** Daniele Farias
> **Repositório:** https://github.com/dofarias/ASN_IAGen_Lista2
>
> Documento de apoio. As regras completas de trabalho estão em `AGENTS.md`; o comportamento aprovado está em `SPEC.md`. Este arquivo concentra apenas orientações úteis ao Claude Code e não duplica o `AGENTS.md`.

## 1. Objetivo

Orientar o Claude Code na compreensão, no planejamento e na execução de tarefas do dashboard de estoque da Garden Shop (Python + Streamlit), seguindo SDD + TDD.

## 2. Documentos obrigatórios

Antes de alterar o código:

- Leia `AGENTS.md` e siga suas regras (fonte principal das convenções do projeto).
- Leia `PRD.md` para compreender os objetivos e os limites do produto.
- Leia `SPEC.md` para identificar os requisitos técnicos (REQ-xxx), as fórmulas, os valores de referência (seção 9) e os critérios de aceitação (TEST-xxx).
- Consulte o dicionário `garden_shop_dicionario_dados.xlsx` e a proposta `IAGP_Lista1-Daniele_Farias.docx` para a origem das regras de negócio.

O `SPEC.md` é a referência para o comportamento técnico aprovado. Não substitua requisitos definidos nele por suposições próprias.

### Divergências já registradas (não "corrigir" por conta própria)

- **DP-001:** o enunciado pede para não usar vermelho, mas a responsável optou por manter o semáforo vermelho/laranja/amarelo. Mantenha.
- **DP-002:** o dicionário indica datas de `orders` em `DD/MM/AAAA`, mas os CSVs reais usam `AAAA-MM-DD`. Use o formato real.

## 3. Forma de atuação

### 3.1. Explore antes de implementar

- Inspecione a estrutura do repositório e os CSVs em `Garden Shop/`.
- Identifique dependências, pontos de entrada (`app.py`) e testes (`tests/`).
- Reutilize padrões já estabelecidos; evite reescritas quando uma alteração localizada resolver.

### 3.2. Planeje tarefas complexas

Para mudanças que envolvam vários componentes ou decisões de projeto:

1. Resuma o problema.
2. Identifique os requisitos relacionados da `SPEC.md`.
3. Apresente a abordagem proposta.
4. Identifique os arquivos e componentes afetados (carga, métricas, filtros, apresentação).
5. Defina os testes necessários antes de implementar.
6. Destaque ambiguidades e decisões pendentes (ex.: SPEC-OPEN-001, limiar do semáforo).

Para correções pequenas e inequívocas, siga direto para a implementação quando for seguro.

### 3.3. Implemente incrementalmente

- Faça alterações pequenas e coerentes, em branches, com PRs.
- Mantenha a lógica de cálculo separada da camada Streamlit.
- Não introduza funcionalidades fora do escopo do `PRD.md`.
- Não considere a implementação concluída só porque o código foi escrito; verifique.

## 4. Desenvolvimento orientado a especificação e a testes (SDD + TDD)

Fluxo:

1. **Specify:** compreenda/refine os requisitos em `SPEC.md`.
2. **Plan:** defina a abordagem e as etapas.
3. **Test first:** escreva o teste com o resultado esperado (ver valores da `SPEC.md` seção 9) e confirme que ele falha.
4. **Implement:** escreva o mínimo para o teste passar.
5. **Verify:** execute `pytest` e confira os critérios de aceitação.
6. **Update:** atualize a documentação e registre mudanças relevantes.

### Regras de conformidade

- Cada funcionalidade importante deve estar associada a um requisito identificável (REQ-xxx).
- Esclareça requisitos ambíguos antes de decisões de alto impacto.
- Se a especificação estiver incorreta ou incompleta, proponha a correção antes de desviar dela.
- Não altere silenciosamente o escopo ou os contratos.
- Mantenha especificação, código e testes alinhados.

## 5. Execução de comandos

- Consulte os comandos em `AGENTS.md` seção 7 (todos marcados como NÃO VERIFICADOS até serem executados).
- Use o ambiente virtual do projeto; não instale pacotes globalmente.
- Não execute comandos destrutivos sem autorização.
- Se um comando falhar, examine a causa antes de contornar.
- Não afirme que testes passaram sem verificar o resultado real.

## 6. Testes e validação

Após implementar:

1. Execute os testes relacionados (`pytest`).
2. Execute lint/formatação quando disponíveis.
3. Confira os critérios de aceitação da `SPEC.md` (TEST-001 a TEST-012).
4. Verifique regressões, duplicação de saldos na junção e efeitos colaterais.
5. Registre os testes que falharam ou não puderam ser executados.

Valores de referência para validar: 23 produtos ativos, 5 em alerta, 1 com estoque zerado (Hanging Basket), valor total do estoque = 4731.00; Sunflower Seeds = 12 e Terracotta Pot 8in = 9 em vendas; Pruning Shears = 1 (pedido 17 cancelado ignorado).

## 7. Segurança e privacidade

- Nunca exponha credenciais, tokens ou dados sensíveis.
- Não consuma nem exiba dados de clientes (`customers.csv` está fora do escopo desta entrega).
- Preserve os CSVs originais; a aplicação apenas lê os dados.
- Não remova mecanismos de segurança para facilitar a implementação.
- Solicite aprovação quando a tarefa envolver riscos relevantes ou mudanças de escopo.

## 8. Uso de ferramentas e recursos do Claude Code

- Use leitura e busca para entender o código antes de alterá-lo.
- Use edições localizadas e revisáveis.
- Use execução para validar o comportamento real.
- Não presuma que uma ferramenta, skill, MCP ou integração esteja instalada; verifique a disponibilidade.
- Revise as alterações de agentes auxiliares antes de integrá-las.

## 9. Atualização da documentação

- Atualize `SPEC.md` quando mudanças aprovadas afetarem requisitos, contratos ou critérios.
- Atualize `PRD.md` quando mudarem objetivos, público-alvo ou escopo.
- Atualize `AGENTS.md` quando mudarem convenções duradouras de desenvolvimento.
- Mantenha este arquivo focado em orientações para Claude Code; não registre detalhes transitórios de execução.

## 10. Critérios de conclusão

Antes de declarar a tarefa concluída, verifique:

- A implementação corresponde ao requisito solicitado.
- Os testes pertinentes foram executados e passaram.
- As falhas conhecidas foram tratadas ou documentadas.
- Alterações não relacionadas foram evitadas.
- A documentação afetada foi atualizada.
- O resultado e suas limitações foram comunicados.

## 11. Relatório final

Ao concluir, apresente:

### Implementação
[Resumo das alterações.]

### Arquivos afetados
[Arquivos criados ou modificados.]

### Validação
[Testes executados e resultados observados.]

### Pendências
[Limitações, decisões pendentes e próximos passos.]

## 12. Regra final

Priorize uma implementação correta, verificável, segura e consistente com a especificação e com a preservação dos dados originais. Se houver conflito entre a solução mais rápida e os requisitos aprovados, não sacrifique os requisitos sem apresentar e justificar a decisão.
