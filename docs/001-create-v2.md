# Criar prompt **V2** aplicando a técnica **Few-shot Learning**

## Objetivo

Criar a versão **V2** do prompt a partir do arquivo `prompts/bug_to_user_story_v1.yml`, salvando-a em `prompts/bug_to_user_story_v2.yml`. A V2 deve converter relatos de bugs em **User Stories** de qualidade, atingindo pontuação **≥ 0.9 em todas as 5 métricas** da avaliação (Helpfulness, Correctness, F1-Score, Clarity, Precision).

## Requisitos obrigatórios

1. **Few-shot Learning** é obrigatório — incluir de 2 a 4 exemplos representativos (par bug report → user story) dentro do `system_prompt`.
2. Combinar com **pelo menos uma** técnica adicional dentre: Chain-of-Thought (CoT), Tree-of-Thought (ToT), Skeleton-of-Thought (SoT), ReAct ou Role Prompting.
3. Listar **no mínimo 2 técnicas** no campo `techniques_applied` dos metadados.
4. Manter o schema YAML esperado por `src/utils.py::validate_prompt_structure`:
   - Chave de topo `bug_to_user_story_v2`
   - Campos: `description`, `system_prompt`, `user_prompt`, `version`, `techniques_applied`, `tags`
   - Templates devem usar a variável `{bug_report}` (sintaxe LangChain).

## Problemas conhecidos da V1 que a V2 deve corrigir

- `{bug_report}` aparece duplicado no `system_prompt` e no `user_prompt`.
- Falta de persona / role definido.
- Instruções vagas, sem critérios de qualidade nem formato de saída.
- Ausência de exemplos (zero-shot).
- Sem estrutura definida para a User Story (ex.: "Como <persona>, eu quero <ação>, para <benefício>" + critérios de aceitação).

## Entregáveis

- `prompts/bug_to_user_story_v2.yml` criado e validável pelos testes em `tests/test_prompts.py`.
- Push para o LangSmith Hub via `./venv/bin/python src/push_prompts.py` (público).
- Avaliação via `./venv/bin/python src/evaluate.py` com **todas as métricas ≥ 0.9**.
