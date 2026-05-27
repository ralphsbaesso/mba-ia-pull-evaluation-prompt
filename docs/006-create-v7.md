# Criar prompt **V7** aplicando **ReAct (Reasoning + Acting)**

## Objetivo

Criar a versão **V7** do prompt a partir do arquivo `prompts/bug_to_user_story_v1.yml`, salvando-a em `prompts/bug_to_user_story_v7.yml`. A V7 deve converter relatos de bugs em **User Stories** aplicando **ReAct** — intercalando ciclos explícitos de **Thought → Action → Observation** sobre o próprio relato do bug, em que cada *Action* é uma operação de inspeção/extração sobre o texto disponível (ex.: identificar persona afetada, extrair comportamento esperado vs. observado, mapear cenários de aceitação) e cada *Observation* registra o que foi obtido, alimentando o próximo *Thought*. O objetivo é isolar o ganho de qualidade trazido pelo raciocínio **fundamentado em evidências extraídas do bug** (ReAct) em relação à decomposição esqueleto-primeiro da V6 (SoT), à busca em árvore da V5 (ToT) e ao consenso da V4, atingindo pontuação **≥ 0.9 em todas as 5 métricas** (Helpfulness, Correctness, F1-Score, Clarity, Precision).

## Requisitos obrigatórios

1. **ReAct é a técnica central e inegociável** desta versão. O `system_prompt` deve instruir o modelo a operar em **ciclos explícitos de Thought → Action → Observation**:
   - **Thought:** raciocínio sobre o que ainda falta entender do bug para montar a User Story.
   - **Action:** uma operação concreta de extração/verificação sobre o texto do bug — sem ferramentas externas, são "ações" de inspeção do próprio relato. No mínimo cobrir:
     1. `extrair_persona` — quem é o usuário/ator afetado.
     2. `extrair_comportamento` — comportamento esperado vs. comportamento observado (o bug em si).
     3. `inferir_beneficio` — valor de negócio / motivação por trás da correção.
     4. `mapear_criterios` — cenários de aceitação verificáveis derivados do bug.
   - **Observation:** o resultado factual de cada Action, citando o trecho do bug que o fundamenta (ancoragem em evidência). Quando o relato for omisso, a Observation deve registrar explicitamente a lacuna em vez de inventar dados.
2. O raciocínio deve ser **guiado por evidência extraída do bug** — cada conclusão rastreável a uma Observation — e não um raciocínio linear sem ancoragem (que colapsaria em CoT da V3), nem decomposição esqueleto-primeiro (SoT da V6), nem exploração de hipóteses concorrentes (ToT da V5).
3. Os ciclos Thought/Action/Observation constituem o raciocínio e devem permanecer **internos** ao modelo. A saída final contém **apenas** a User Story consolidada, no formato "Como \<persona\>, eu quero \<ação\>, para \<benefício\>" + critérios de aceitação em Gherkin.
4. **Não usar Few-shot** — manter zero-shot para isolar o efeito do ReAct e permitir comparação direta com V3 (CoT), V4 (CoT + Self-Consistency), V5 (ToT) e V6 (SoT).
5. Listar **no mínimo 2 técnicas** em `techniques_applied`, contendo obrigatoriamente `ReAct` e `Chain-of-Thought` (que sustenta a fase de *Thought* de cada ciclo).
6. Manter o schema YAML esperado por `src/utils.py::validate_prompt_structure`:
   - Chave de topo `bug_to_user_story_v7`
   - Campos: `description`, `system_prompt`, `user_prompt`, `version`, `techniques_applied`, `tags`
   - Templates devem usar a variável `{bug_report}` (sintaxe LangChain).
7. Eliminar a duplicação de `{bug_report}`: a variável deve aparecer **apenas no `user_prompt`**.

## Problemas conhecidos da V1 que a V7 deve corrigir

- `{bug_report}` duplicado entre `system_prompt` e `user_prompt`.
- Instruções vagas, sem raciocínio estruturado nem critérios de qualidade.
- Sem formato de saída definido para a User Story.
- Ausência de ancoragem em evidência — V1 gera a User Story sem rastrear cada afirmação a um trecho do bug, abrindo espaço para alucinação e omissão (problema que o ReAct endereça via ciclos Action → Observation que citam o relato, melhorando a Precision e a Correctness).

## Entregáveis

- `prompts/bug_to_user_story_v7.yml` criado e validável pelos testes em `tests/test_prompts.py` (adaptar/duplicar os testes para `v7` se necessário).

## Critério de sucesso comparativo

Documentar (em commit message ou anotação) as 5 métricas da V7 lado a lado com V3 (CoT puro), V4 (CoT + Self-Consistency), V5 (ToT) e V6 (SoT), evidenciando o delta atribuível à ancoragem em evidência do ReAct e indicando se o ganho em Precision/Correctness compensa o custo de tokens dos ciclos Thought/Action/Observation.
