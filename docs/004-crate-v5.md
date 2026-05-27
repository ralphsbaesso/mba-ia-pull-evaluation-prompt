# Criar prompt **V5** aplicando **Tree of Thoughts (ToT)**

## Objetivo

Criar a versão **V5** do prompt a partir do arquivo `prompts/bug_to_user_story_v1.yml`, salvando-a em `prompts/bug_to_user_story_v5.yml`. A V5 deve converter relatos de bugs em **User Stories** aplicando **Tree of Thoughts** — explorando múltiplos ramos de raciocínio em paralelo, avaliando cada ramo segundo critérios explícitos e selecionando o melhor caminho (com possibilidade de poda e backtracking). O objetivo é isolar o ganho de qualidade trazido pela busca estruturada do ToT sobre o consenso linear do Self-Consistency da V4, atingindo pontuação **≥ 0.9 em todas as 5 métricas** (Helpfulness, Correctness, F1-Score, Clarity, Precision).

## Requisitos obrigatórios

1. **Tree of Thoughts é a técnica central e inegociável** desta versão. O `system_prompt` deve instruir o modelo a:
   - **Expandir** a partir do bug uma árvore com pelo menos **3 ramos iniciais** (ex.: diferentes interpretações de persona, escopo ou objetivo de negócio do bug).
   - Para cada ramo, gerar **passos intermediários** decompondo: persona → ação → benefício → critérios de aceitação (Gherkin).
   - **Avaliar cada ramo** segundo critérios explícitos: fidelidade ao bug, clareza da persona, completude dos critérios de aceitação, ausência de invenções (precisão).
   - **Podar** ramos inferiores e, quando um ramo promissor falhar em algum critério, aplicar **backtracking** para um nó anterior e tentar alternativa.
   - **Selecionar** o ramo vencedor e emitir a User Story final apenas a partir dele.
2. A exploração da árvore deve ser **deliberada e estruturada**, não uma simples geração de N candidatas independentes (caso contrário, colapsa em Self-Consistency e perde a justificativa sobre a V4).
3. O raciocínio (expansão, avaliação, poda, backtracking) deve permanecer **interno** ao modelo. A saída final contém **apenas** a User Story consolidada, no formato "Como <persona>, eu quero <ação>, para <benefício>" + critérios de aceitação em Gherkin.
4. **Não usar Few-shot** — manter zero-shot para isolar o efeito do ToT e permitir comparação direta com V3 (CoT) e V4 (CoT + Self-Consistency).
5. Listar **no mínimo 2 técnicas** em `techniques_applied`, contendo obrigatoriamente `Tree-of-Thoughts` e `Chain-of-Thought` (que sustenta cada ramo).
6. Manter o schema YAML esperado por `src/utils.py::validate_prompt_structure`:
   - Chave de topo `bug_to_user_story_v5`
   - Campos: `description`, `system_prompt`, `user_prompt`, `version`, `techniques_applied`, `tags`
   - Templates devem usar a variável `{bug_report}` (sintaxe LangChain).
7. Eliminar a duplicação de `{bug_report}`: a variável deve aparecer **apenas no `user_prompt`**.

## Problemas conhecidos da V1 que a V5 deve corrigir

- `{bug_report}` duplicado entre `system_prompt` e `user_prompt`.
- Instruções vagas, sem raciocínio estruturado nem critérios de qualidade.
- Sem formato de saída definido para a User Story.
- Ausência de exploração de alternativas — V1 produz uma única interpretação do bug sem comparar hipóteses concorrentes (problema que o ToT endereça via expansão + avaliação + poda).

## Entregáveis

- `prompts/bug_to_user_story_v5.yml` criado e validável pelos testes em `tests/test_prompts.py` (adaptar/duplicar os testes para `v5` se necessário).

## Critério de sucesso comparativo

Documentar (em commit message ou anotação) as 5 métricas da V5 lado a lado com V3 (CoT puro) e V4 (CoT + Self-Consistency), evidenciando o delta atribuível à busca estruturada do ToT sobre o consenso linear do Self-Consistency e indicando se o ganho compensa o custo extra de tokens da exploração em árvore.
