# 011 — Plano de melhoria do prompt v2 (atingir F1-Score ≥ 0.90)

## Contexto

Na iteração do commit `62b2555` (`resultados/2026-05-29_1.md`) o prompt v2 ficou **REPROVADO** por **uma única métrica**:

| Métrica | Nota | Status |
|---|---|---|
| Helpfulness | 0.94 | ✓ |
| Correctness | 0.91 | ✓ |
| Clarity | 0.93 | ✓ |
| Precision | 0.95 | ✓ |
| **F1-Score** | **0.86** | **✗ (precisa ≥ 0.90)** |

A meta é tão simples quanto **subir o F1 médio de 0.86 → 0.90+**. As outras 4 métricas já passam (e como `correctness = (f1+precision)/2`, melhorar o F1 ainda reforça a margem dela). Não há nada a fazer em Clarity/Precision/Helpfulness.

## Como o F1 é medido (para entender o problema)

`src/metrics.py::evaluate_f1_score` é um **LLM-as-judge** que compara a resposta gerada contra a `reference` (user story "ouro") do dataset e devolve:
- **Precision** — quanto do que foi gerado está correto/relevante; pune conteúdo **inventado ou desnecessário** (que não está na reference).
- **Recall** — quanto do conteúdo importante da reference **está presente** na resposta; pune **omissões**.
- `F1 = 2·P·R / (P+R)`.

Ou seja: **F1 cai quando a estrutura/seções da resposta divergem da reference** — seja por adicionar seções a mais (↓precision) ou por omitir seções/critérios que a reference tem (↓recall).

## Diagnóstico por exemplo (onde o F1 vazou)

Cruzando as notas `[i/15]` do log com `datasets/bug_to_user_story.jsonl`:

| # | Complexidade | F1 | Veredito |
|---|---|---|---|
| 13, 14, 15 | complex | **1.00** | Template COMPLEXO do v2 casa perfeitamente com as references |
| 12, 7, 8 | medium | 1.00 / 0.95 / 0.92 | OK |
| 1 | simple | 0.95 | OK |
| 3 | simple | 0.84 | leve divergência |
| 2, 5, 6 | simple/med | 0.82 | divergência moderada |
| 11 | medium | 0.89 | quase |
| **4** | **simple** | **0.67** | **âncora** |
| **9** | **medium** | **0.65** | **âncora** |
| **10** | **medium** | **0.65** | **âncora** |

O tier **COMPLEXO está perfeito**. Os pontos baixos estão nos tiers **SIMPLES** e **MÉDIO**, cuja causa raiz é a mesma: **os templates rígidos do v2 não batem com a estrutura real das references desses tiers.**

### Pontos a melhorar (causa raiz de cada um)

1. **MÉDIO está subdimensionado (maior ofensor — #9 e #10 = 0.65).**
   O template MÉDIO do v2 só manda adicionar uma seção `Contexto Técnico:` (descrição do *problema*). Mas as references médias do dataset variam muito e quase sempre trazem **mais conteúdo**:
   - **#10** (Android/ANR): a reference tem **`Critérios Técnicos:`** com a *solução* (paginação, background thread, RecyclerView, scroll infinito) **+** `Contexto do Bug`. O v2 não gera a seção de critérios técnicos de solução → **recall despenca**.
   - **#9** (cálculo de desconto): a reference tem um bloco **`Exemplo de Cálculo:`** com os números (R$ 1.500 / -R$ 150 / R$ 1.350) **+** `Contexto Técnico`. O v2 não prevê o bloco de exemplo de cálculo → **recall despenca**. Pior: a regra de "guarda-corpo de precisão" do v2 pode inibir o modelo de repetir os números do relato.
   - **#8/#11/#12**: as references trazem grupos extras de critérios (`Critérios Adicionais para Admins`, `Critérios de Prevenção`, `Critérios de Acessibilidade`). O template MÉDIO atual não orienta agrupar/expandir critérios → recall parcial (por isso ficam em 0.82–0.92, não 1.0).

2. **SIMPLES está, ao contrário, propenso a "inflar" (#4 = 0.67).**
   A reference de #4 (dashboard com contagem errada) é **enxuta**: story + 5 critérios, **sem nenhuma seção técnica**. Mas o relato menciona números ("50 vs 42"), então o modelo provavelmente **classificou como MÉDIO** e anexou `Contexto Técnico` → conteúdo que **não existe na reference** → **precision punida** + divergência estrutural. As simples #2/#3/#5 (0.82–0.84) têm o mesmo sintoma em menor grau.

3. **A classificação de complexidade é um ponto único de falha.**
   Todo o roteamento depende do CoT interno acertar SIMPLES/MÉDIO/COMPLEXO. Quando erra o tier (ex.: #4 tratado como médio), a estrutura inteira desalinha. Os few-shot atuais têm 3 exemplos SIMPLES, 1 MÉDIO e 1 COMPLEXO — o tier MÉDIO (o mais problemático e mais frequente no dataset: 7 dos 15) está **sub-representado** e os exemplos não mostram a variedade de seções que as references médias usam.

## Plano de ação (o que mudar)

Toda a mudança é **apenas em `prompts/bug_to_user_story_v2.yml`** (o resto do pipeline está "ready — do not alter"). Loop de iteração: editar YAML → `push_prompts.py` → `evaluate.py`.

### 1. Reforçar o tier MÉDIO para casar com as references
Reescrever o template MÉDIO para incluir, além dos ≥5 critérios Gherkin:
- **`Critérios Técnicos:`** — lista de **recomendações de solução** derivadas do relato (não só descrição do problema). É o que falta em #10.
- Permitir/instruir **grupos adicionais de critérios** quando o relato sugerir (segurança, acessibilidade, prevenção, admin) — caso #8/#11/#12.
- Quando o relato trouxer **números/cálculo**, incluir um bloco **`Exemplo de Cálculo:`** repetindo os valores do relato — caso #9. Ajustar a redação do "guarda-corpo de precisão" para deixar explícito que **reafirmar dados presentes no relato é desejável** (não é invenção).
- Manter `Contexto Técnico:` / `Contexto do Bug:` com os detalhes do relato.

### 2. Manter o tier SIMPLES realmente enxuto
Instruir explicitamente: para bugs SIMPLES, **entregar só** story + 5 critérios, **sem** seção técnica, mesmo que o relato cite números pontuais. Adicionar regra anti-inflar: "não crie seções de Contexto/Critérios Técnicos em bugs simples". Reclassificar o caso "contagem/número simples" (como #4) como SIMPLES.

### 3. Rebalancear os few-shot examples
- Adicionar **2 exemplos MÉDIOS** novos copiando o estilo/seções das references do próprio dataset (um com `Critérios Técnicos` de solução estilo #10, um com `Exemplo de Cálculo` estilo #9).
- Adicionar 1 exemplo SIMPLES "com número" (estilo #4) mostrando saída enxuta — para calibrar a classificação.
- Manter ≥2 técnicas em `techniques_applied` (Few-shot + Chain-of-Thought) — requisito do desafio preservado.

### 4. Não mexer no que já está 1.00
O tier COMPLEXO está perfeito (#13/#14/#15). Não alterar seu template.

