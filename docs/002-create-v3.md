# Criar prompt **V3** aplicando a técnica **Chain-of-Thought (CoT)**

## Objetivo

Criar a versão **V3** do prompt a partir do arquivo `prompts/bug_to_user_story_v1.yml`, salvando-a em `prompts/bug_to_user_story_v3.yml`. A V3 deve converter relatos de bugs em **User Stories** isolando a técnica **Chain-of-Thought** como principal alavanca de qualidade, permitindo comparar seu impacto contra a V2 (que combina Few-shot + Role Prompting + CoT). A meta é atingir pontuação **≥ 0.9 em todas as 5 métricas** (Helpfulness, Correctness, F1-Score, Clarity, Precision).

## Requisitos obrigatórios

1. **Chain-of-Thought (CoT)** é a técnica central — o `system_prompt` deve guiar o modelo por um raciocínio explícito em etapas numeradas antes de produzir a resposta final (persona → ação → benefício → critérios de aceitação → reformulação positiva do bug).
2. O raciocínio CoT deve ser **interno** ao modelo: instrua-o a pensar passo a passo, mas a **não** incluir essas etapas na saída — apenas a User Story formatada.
3. **Não usar Few-shot** nesta versão (zero-shot + CoT) para isolar o efeito da técnica. Caso adicione outra técnica complementar, ela deve ser diferente de Few-shot Learning (ex.: Role Prompting leve, SoT).
4. Listar **no mínimo 2 técnicas** no campo `techniques_applied` dos metadados (sendo `Chain-of-Thought` obrigatória).
5. Manter o schema YAML esperado por `src/utils.py::validate_prompt_structure`:
   - Chave de topo `bug_to_user_story_v3`
   - Campos: `description`, `system_prompt`, `user_prompt`, `version`, `techniques_applied`, `tags`
   - Templates devem usar a variável `{bug_report}` (sintaxe LangChain).
6. Eliminar a duplicação de `{bug_report}`: a variável deve aparecer **apenas no `user_prompt`**.

## Problemas conhecidos da V1 que a V3 deve corrigir

- `{bug_report}` aparece duplicado no `system_prompt` e no `user_prompt`.
- Instruções vagas, sem etapas de raciocínio nem critérios de qualidade.
- Sem formato de saída definido para a User Story (ex.: "Como <persona>, eu quero <ação>, para <benefício>" + critérios de aceitação em Gherkin).
- Ausência de raciocínio estruturado — o modelo pula direto para a resposta sem decompor o problema.

## Entregáveis

- `prompts/bug_to_user_story_v3.yml` criado e validável pelos testes em `tests/test_prompts.py` (adaptar/duplicar os testes para `v3` se necessário).
- Push para o LangSmith Hub via `./venv/bin/python src/push_prompts.py` (público) — ajustar o script ou parametrizar a versão alvo.
- Avaliação via `./venv/bin/python src/evaluate.py` com **todas as métricas ≥ 0.9**, lembrando que `evaluate.py` puxa o prompt do Hub (não do YAML local).

## Critério de sucesso comparativo

Documentar (em commit message ou anotação) o resultado das 5 métricas da V3 lado a lado com a V2, para evidenciar quanto da qualidade vem do CoT isoladamente versus da combinação com Few-shot.
