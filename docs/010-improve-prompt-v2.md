# 010 — Correção do v2 para atingir a meta (F1 ≥ 0.9)

## Contexto

A rodada de avaliação (`resultados/2026-05-28_1.md`) reprovou: apenas **F1-Score (0.76)** e a
métrica derivada **Correctness (0.86)** ficaram abaixo de 0.9 — Helpfulness, Clarity e Precision
passaram.

Como `correctness = (f1 + precision)/2` e `f1 = 2·P·R/(P+R)`, e a precision do juiz é ≈1.0 na
maioria dos exemplos, o gargalo único é o **recall**: as User Stories geradas **omitem conteúdo
que existe nas respostas de referência**.

Causa raiz: as referências do dataset **escalam com a complexidade do bug**, mas o
`prompts/bug_to_user_story_v2.yml` produz uma saída mínima fixa e **proíbe** justamente o conteúdo
mais rico que as referências contêm:

- Bugs simples (exemplos 1–5): story única + 5 critérios Gherkin.
- Bugs médios (6–12): referência adiciona seção **"Contexto Técnico"** (endpoints, códigos HTTP, severidade).
- Bugs complexos (13–15): título + critérios agrupados (A/B/C/D) + **Critérios Técnicos** +
  **Contexto do Bug** (severidade/impacto) + **Tasks Técnicas Sugeridas**.

A linha `bug_to_user_story_v2.yml:28` ("Não inclua passos de reprodução, severidade, prioridade...")
e os 3 exemplos few-shot (todos simples) fazem o modelo descartar tudo que as referências
médias/complexas esperam → o recall despenca → F1 ≈ 0.76.

Problema secundário: o v2 lista apenas `Few-shot Learning` em `techniques_applied` (1 técnica), o que
viola a regra do desafio de **≥2 técnicas** (CLAUDE.md:9) e o futuro teste `test_minimum_techniques`.

Resultado esperado: o v2 gera saída cuja profundidade acompanha a complexidade de cada bug (fechando a
lacuna de recall) e declara 2 técnicas — mirando todas as cinco métricas ≥ 0.9.

## Decisões (confirmadas com o usuário)

- **Técnicas:** Few-shot + **Chain-of-Thought** (interno: analisar complexidade → escolher estrutura).
- **Saída:** **Totalmente adaptativa** entre os níveis simples / médio / complexo.

## Mudanças

### 1. `prompts/bug_to_user_story_v2.yml` (edição principal)

Reescrever o `system_prompt` para:

- **Manter** a persona de PM-sênior e o padrão de qualidade pt-BR / foco no valor ao usuário.
- **Adicionar um passo interno de CoT** (explicitamente NÃO exposto na saída): classificar o bug como
  simples / médio / complexo e então selecionar a estrutura de saída correspondente. Esta é a 2ª técnica.
- **Substituir** a proibição genérica da linha 28 por regras **condicionais à complexidade**:
  - Simples → `Como <persona>, eu quero..., para...` + ≥5 critérios Gherkin (inalterado).
  - Médio → mesma story + critérios **mais** uma seção `Contexto Técnico:` preservando os detalhes
    técnicos relevantes do relato (endpoint, status HTTP, severidade, causa provável).
  - Complexo → `Título:` + descrição + critérios de aceitação **agrupados** (A./B./C./D. com Gherkin) +
    `=== CRITÉRIOS TÉCNICOS ===` + `=== CONTEXTO DO BUG ===` (severidade + impacto) +
    `=== TASKS TÉCNICAS SUGERIDAS ===`.
  - Guarda-corpo para proteger a Precision (hoje 0.96): incluir somente conteúdo técnico/impacto que
    esteja **presente no ou diretamente inferível a partir do relato** — não inventar endpoints,
    números ou tasks.
- **Expandir os exemplos few-shot** de 3 (todos simples) para ~5, adicionando um exemplo **médio** e um
  **complexo** cuja estrutura espelhe as referências do dataset (ex.: um caso médio de webhook/integração
  com `Contexto Técnico`, e um caso complexo de checkout com múltiplas falhas usando as quatro seções
  `===`). Usar conteúdo realista porém genérico, distinto das linhas do dataset de avaliação, para evitar
  overfitting/vazamento.

Atualizar metadados:

- `techniques_applied`: `["Few-shot Learning", "Chain-of-Thought"]`
- `description`: mencionar ambas as técnicas.
- adicionar `chain-of-thought` em `tags`.

Observação sobre a tensão com `docs/007-revision.md` / `docs/008-report-revision.md` (que limitaram o
v2 a Few-shot apenas): o requisito do desafio (≥2 técnicas) prevalece para o v2 que é avaliado; os
experimentos de isolamento v3–v7 ficam intocados.

### 2. Arquivos off-limits — NÃO editar

`src/evaluate.py`, `src/metrics.py`, `src/utils.py`, `datasets/bug_to_user_story.jsonl` estão marcados
como "prontos — não alterar". A correção fica inteiramente no YAML do prompt.
(`evaluate.py:323-325` chumba a avaliação de `{username}/bug_to_user_story_v2`, então melhorar o v2 é
suficiente.)

### 3. (Opcional, separado) `tests/test_prompts.py`

Atualmente todos os testes são stubs (`pass`). Não é necessário para esta correção. Se implementados
depois, `test_minimum_techniques` passará dado o metadado com 2 técnicas, e
`test_prompt_has_few_shot_examples` passará dados os exemplos expandidos.

## Verificação (rodar após a edição)

1. Fazer push do novo v2 para o LangSmith Hub (o Hub é a fonte única que o `evaluate.py` puxa):
   ```bash
   ./venv/bin/python src/push_prompts.py
   ```
   (deve fazer push `is_public=True`; confirmar sucesso para `que-dia-eh-hoje/bug_to_user_story_v2`).
2. Re-rodar a avaliação:
   ```bash
   ./venv/bin/python src/evaluate.py
   ```
3. Inspecionar a linha de F1 por exemplo nos exemplos 6–15 (médios/complexos) — devem subir mais.
   Meta: **todas as cinco métricas ≥ 0.9**, status APROVADO.
4. Se F1 ainda < 0.9, ler o `reasoning` do juiz (comentários de recall) nos exemplos mais baixos e
   iterar sobre quais seções da referência ainda faltam — editar YAML → push → avaliar (pular o push
   avalia a versão antiga).
5. Salvar a saída da nova rodada em `resultados/2026-05-29_1.md` para registro (segue a convenção atual).

## Notas / riscos

- DeepSeek é o provider ativo (`.env`: `LLM_PROVIDER=deepseek`, principal `deepseek-v4-pro`,
  avaliação `deepseek-v4-flash`). Notas de LLM-as-judge são ruidosas; esperar 1–2 iterações de
  push/avaliação.
- Conteúdo mais rico arrisca baixar a Precision — mitigado pelo guarda-corpo "só o que está no relato"
  e pelo gating por complexidade (bugs simples permanecem mínimos).
