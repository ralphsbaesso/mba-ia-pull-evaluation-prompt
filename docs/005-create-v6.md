# Criar prompt **V6** aplicando **Skeleton of Thought (SoT)**

## Objetivo

Criar a versão **V6** do prompt a partir do arquivo `prompts/bug_to_user_story_v1.yml`, salvando-a em `prompts/bug_to_user_story_v6.yml`. A V6 deve converter relatos de bugs em **User Stories** aplicando **Skeleton of Thought** — primeiro gerando um **esqueleto** enxuto (a lista dos pontos que comporão a resposta) e, em seguida, **expandindo cada ponto** do esqueleto em conteúdo completo. O objetivo é isolar o ganho de qualidade trazido pela estruturação esqueleto-primeiro do SoT em relação à busca em árvore da V5 (ToT) e ao consenso da V4, atingindo pontuação **≥ 0.9 em todas as 5 métricas** (Helpfulness, Correctness, F1-Score, Clarity, Precision).

## Requisitos obrigatórios

1. **Skeleton of Thought é a técnica central e inegociável** desta versão. O `system_prompt` deve instruir o modelo a operar em **duas etapas explícitas**:
   - **Etapa 1 — Esqueleto:** a partir do bug, produzir uma lista curta e enxuta dos pontos da User Story, cada um em 3–5 palavras. O esqueleto deve cobrir, no mínimo:
     1. Persona
     2. Ação desejada
     3. Benefício / valor de negócio
     4. Critérios de aceitação (um item por cenário relevante)
   - **Etapa 2 — Expansão:** percorrer cada ponto do esqueleto e expandi-lo em conteúdo completo, mantendo fidelidade estrita ao esqueleto (não introduzir pontos novos nem omitir os listados).
2. A estruturação deve ser **esqueleto-primeiro e paralela por ponto** — cada ponto expandido de forma independente a partir do esqueleto — e não um raciocínio linear contínuo (caso contrário colapsa em CoT e perde a justificativa sobre a V3) nem uma exploração de hipóteses concorrentes (que seria o ToT da V5).
3. O esqueleto e a expansão constituem o raciocínio e devem permanecer **internos** ao modelo. A saída final contém **apenas** a User Story consolidada, no formato "Como <persona>, eu quero <ação>, para <benefício>" + critérios de aceitação em Gherkin.
4. **Não usar Few-shot** — manter zero-shot para isolar o efeito do SoT e permitir comparação direta com V3 (CoT), V4 (CoT + Self-Consistency) e V5 (ToT).
5. Listar **no mínimo 2 técnicas** em `techniques_applied`, contendo obrigatoriamente `Skeleton-of-Thought` e `Chain-of-Thought` (que sustenta a expansão de cada ponto).
6. Manter o schema YAML esperado por `src/utils.py::validate_prompt_structure`:
   - Chave de topo `bug_to_user_story_v6`
   - Campos: `description`, `system_prompt`, `user_prompt`, `version`, `techniques_applied`, `tags`
   - Templates devem usar a variável `{bug_report}` (sintaxe LangChain).
7. Eliminar a duplicação de `{bug_report}`: a variável deve aparecer **apenas no `user_prompt`**.

## Problemas conhecidos da V1 que a V6 deve corrigir

- `{bug_report}` duplicado entre `system_prompt` e `user_prompt`.
- Instruções vagas, sem raciocínio estruturado nem critérios de qualidade.
- Sem formato de saída definido para a User Story.
- Ausência de um plano explícito da resposta — V1 gera a User Story de uma só vez, sem decompor previamente seus componentes (problema que o SoT endereça via esqueleto → expansão, reduzindo omissões e melhorando a completude/cobertura que pesa em F1-Score e Correctness).

## Entregáveis

- `prompts/bug_to_user_story_v6.yml` criado e validável pelos testes em `tests/test_prompts.py` (adaptar/duplicar os testes para `v6` se necessário).

## Critério de sucesso comparativo

Documentar (em commit message ou anotação) as 5 métricas da V6 lado a lado com V3 (CoT puro), V4 (CoT + Self-Consistency) e V5 (ToT), evidenciando o delta atribuível à estruturação esqueleto-primeiro do SoT e indicando se o ganho de completude compensa o custo de tokens das duas etapas (esqueleto + expansão).
