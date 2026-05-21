# Criar prompt **V4** aplicando **Chain-of-Thought (CoT)** com **Self-Consistency**

## Objetivo

Criar a versão **V4** do prompt a partir do arquivo `prompts/bug_to_user_story_v1.yml`, salvando-a em `prompts/bug_to_user_story_v4.yml`. A V4 deve converter relatos de bugs em **User Stories** combinando **Chain-of-Thought** com **Self-Consistency** — gerando múltiplos raciocínios independentes e consolidando a User Story final por consenso entre eles. O objetivo é isolar o ganho de qualidade trazido pelo Self-Consistency sobre a V3 (CoT puro, zero-shot), atingindo pontuação **≥ 0.9 em todas as 5 métricas** (Helpfulness, Correctness, F1-Score, Clarity, Precision).

## Requisitos obrigatórios

1. **Self-Consistency é a técnica central e inegociável** desta versão. O `system_prompt` deve instruir o modelo a:
   - Gerar **N caminhos de raciocínio independentes** (recomendado N = 3 a 5), cada um decompondo o bug em persona → ação → benefício → critérios de aceitação.
   - Comparar as N candidatas e **escolher por consenso** (maioria / convergência semântica) a User Story final — não a média textual, mas a versão mais consistente entre os caminhos.
   - Em caso de empate ou divergência relevante, aplicar critério de desempate explícito (ex.: maior cobertura de critérios de aceitação, maior fidelidade ao bug original).
2. **Chain-of-Thought** sustenta cada um dos N caminhos: cada candidata é produzida via raciocínio passo a passo explícito.
3. O raciocínio (tanto as N candidatas quanto a deliberação de consenso) deve permanecer **interno** ao modelo. A saída final contém **apenas** a User Story consolidada, no formato "Como <persona>, eu quero <ação>, para <benefício>" + critérios de aceitação em Gherkin.
4. **Não usar Few-shot** — manter zero-shot para isolar o efeito de CoT + Self-Consistency e permitir comparação direta com a V3.
5. Listar **no mínimo 2 técnicas** em `techniques_applied`, contendo obrigatoriamente `Chain-of-Thought` e `Self-Consistency`.
6. Manter o schema YAML esperado por `src/utils.py::validate_prompt_structure`:
   - Chave de topo `bug_to_user_story_v4`
   - Campos: `description`, `system_prompt`, `user_prompt`, `version`, `techniques_applied`, `tags`
   - Templates devem usar a variável `{bug_report}` (sintaxe LangChain).
7. Eliminar a duplicação de `{bug_report}`: a variável deve aparecer **apenas no `user_prompt`**.

## Problemas conhecidos da V1 que a V4 deve corrigir

- `{bug_report}` duplicado entre `system_prompt` e `user_prompt`.
- Instruções vagas, sem raciocínio estruturado nem critérios de qualidade.
- Sem formato de saída definido para a User Story.
- Resposta única e não-deliberada — sem mecanismo para mitigar variância do modelo (problema que o Self-Consistency endereça diretamente).

## Entregáveis

- `prompts/bug_to_user_story_v4.yml` criado e validável pelos testes em `tests/test_prompts.py` (adaptar/duplicar os testes para `v4` se necessário).
- Push para o LangSmith Hub via `./venv/bin/python src/push_prompts.py` (público) — parametrizar/ajustar o script para a versão alvo.
- Avaliação via `./venv/bin/python src/evaluate.py` com **todas as métricas ≥ 0.9**, lembrando que `evaluate.py` puxa o prompt do Hub (não do YAML local).

## Critério de sucesso comparativo

Documentar (em commit message ou anotação) as 5 métricas da V4 lado a lado com V2 (Few-shot + Role + CoT) e V3 (CoT puro, zero-shot), evidenciando o delta atribuível ao Self-Consistency sobre CoT puro e indicando se o ganho compensa o custo extra de tokens dos N caminhos de raciocínio.
