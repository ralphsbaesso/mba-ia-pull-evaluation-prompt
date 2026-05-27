# Relatório de revisão — prompts v1 a v7

**Objetivo da revisão:** garantir que cada `bug_to_user_story_{v2..v7}` aplique **exatamente uma** técnica da lista abaixo, sem misturar duas técnicas no mesmo arquivo.

Técnicas da atividade (uma por arquivo):

- Few-shot
- Chain of Thought (CoT)
- Chain of Thought (CoT) with Self-Consistency
- Tree of Thoughts (ToT)
- Skeleton of Thought (SoT)
- ReAct

## Premissas adotadas

1. **Role Prompting é tratado como baseline neutro.** A persona *"Você é um Product Manager sênior especialista..."* aparece em todos os prompts (v2–v7) e é considerada contexto-base compartilhado, **não** contabilizada como técnica. Portanto só há "mistura" quando **duas técnicas da lista** convivem no mesmo arquivo.
   - Consequência: onde `techniques_applied` lista `"Role Prompting"`, isso é apenas ruído de metadado — deve ser removido para refletir a premissa, mas não caracteriza mistura conceitual.
2. **`v4` (CoT + Self-Consistency) é uma única técnica da lista.** Self-Consistency é, por definição, amostragem de múltiplos caminhos de CoT seguida de consenso; a lista trata isso como uma entrada única ("CoT with Self-Consistency"). Logo `v4` **não** é mistura.
3. **`v1` está fora do escopo de "uma técnica":** é o prompt-base intencionalmente ruim (sem técnica aplicada). Mantido como referência.

## Mapeamento esperado (1 técnica por arquivo)

| Arquivo | Técnica única esperada |
|---------|------------------------|
| v2 | Few-shot |
| v3 | Chain of Thought (CoT) |
| v4 | CoT with Self-Consistency |
| v5 | Tree of Thoughts (ToT) |
| v6 | Skeleton of Thought (SoT) |
| v7 | ReAct |

## Resumo do diagnóstico

| Arquivo | Técnicas da lista presentes | Veredito |
|---------|-----------------------------|----------|
| v1 | — (baseline ruim) | ✅ N/A |
| v2 | Few-shot **+ Chain of Thought** | ❌ Misturado |
| v3 | Chain of Thought | ✅ Conforme (ajuste de metadado) |
| v4 | CoT + Self-Consistency (entrada única) | ✅ Conforme (ajuste de metadado) |
| v5 | Tree of Thoughts | ✅ Conforme (ajuste de metadado) |
| v6 | Skeleton of Thought **+ Chain of Thought** | ❌ Misturado |
| v7 | ReAct **+ Chain of Thought** | ❌ Misturado |

---

## Detalhamento por arquivo

### `prompts/bug_to_user_story_v1.yml` — ✅ sem ação

Prompt-base intencionalmente ruim (descrito no CLAUDE.md). Não aplica técnica; serve de referência. Nenhuma alteração necessária.

---

### `prompts/bug_to_user_story_v2.yml` — ❌ MISTURADO (Few-shot + CoT)

**Problema:** o arquivo deveria isolar **Few-shot**, mas aplica também **Chain of Thought** de forma explícita.

**Trechos a remover (CoT):**

- `description` (linha 2): remove a menção a "Chain-of-Thought" e "Role Prompting" (manter apenas Few-shot como técnica destacada).
- `system_prompt` — bloco **"## Raciocínio passo a passo (Chain-of-Thought — interno)"** (linhas 10–16): seção inteira deve sair. É o coração do CoT (5 etapas de raciocínio interno) e não pertence a um prompt Few-shot puro.
- `system_prompt` — linha 82: a frase *"aplicando o mesmo padrão **e raciocínio**"* deve perder o "e raciocínio" para não reintroduzir CoT implícito; algo como *"aplicando o mesmo padrão dos exemplos acima"*.
- `techniques_applied` (linhas 92–95): remover `"Chain-of-Thought"` e `"Role Prompting"`. Deixar apenas `"Few-shot Learning"`.
- `tags` (linhas 96–102): remover `"chain-of-thought"` e `"role-prompting"`; manter `"few-shot"`.

**O que preservar:** os três exemplos (Exemplo 1, 2, 3) — eles **são** a técnica Few-shot e devem permanecer. O formato de saída obrigatório e os critérios de qualidade são scaffolding neutro e podem ficar.

**Resultado esperado:** prompt cuja única técnica é a demonstração por exemplos (Few-shot), sem instruções de raciocínio passo a passo.

---

### `prompts/bug_to_user_story_v3.yml` — ✅ conforme (apenas metadado)

**Diagnóstico:** o conteúdo aplica **somente CoT** (7 etapas de raciocínio interno). A persona é baseline neutro. Não há segunda técnica da lista. **Não é mistura.**

**Ajuste de metadado (consistência):**

- `description` (linha 2): remover a menção a "Role Prompting leve" para não sugerir uma segunda técnica. Manter foco em CoT.
- `techniques_applied` (linhas 50–52): remover `"Role Prompting"`, deixando apenas `"Chain-of-Thought"`.
- `tags` (linha 57): remover `"role-prompting"`.

**Nenhuma alteração no corpo do `system_prompt`.**

---

### `prompts/bug_to_user_story_v4.yml` — ✅ conforme (apenas metadado)

**Diagnóstico:** aplica **CoT + Self-Consistency**, que é **uma única técnica da lista** ("CoT with Self-Consistency"). Self-Consistency exige múltiplos caminhos de CoT por definição; portanto não é mistura de duas técnicas distintas. A persona é baseline.

**Ajuste de metadado (opcional, para clareza):**

- `techniques_applied` (linhas 76–78): hoje lista `"Chain-of-Thought"` e `"Self-Consistency"` separadamente. Para alinhar com a lista da atividade, considerar unificar em uma única entrada `"Chain-of-Thought with Self-Consistency"` (ou manter as duas, deixando claro no `description` que formam uma técnica composta). **Não é bloqueante.**

**Nenhuma alteração no corpo do `system_prompt`.**

---

### `prompts/bug_to_user_story_v5.yml` — ✅ conforme (apenas metadado)

**Diagnóstico:** aplica **somente Tree of Thoughts** (expansão de ramos, avaliação, poda, backtracking, emissão do ramo vencedor). O texto inclusive se diferencia explicitamente de Self-Consistency. A persona é baseline. **Não é mistura.**

**Ajuste de metadado (consistência):**

- `techniques_applied` (linhas 83–85): remover `"Role Prompting"`, deixando apenas `"Tree-of-Thoughts"`.
- `tags` (linha 91): remover `"role-prompting"`.

**Nenhuma alteração no corpo do `system_prompt`.**

---

### `prompts/bug_to_user_story_v6.yml` — ❌ MISTURADO (SoT + CoT)

**Problema:** o arquivo deveria isolar **Skeleton of Thought**, mas declara e estrutura explicitamente **Chain of Thought** como motor de expansão de cada ponto.

**Trechos a corrigir (remover CoT explícito):**

- `description` (linha 2): remover a frase *"A expansão de cada ponto é sustentada por Chain-of-Thought."*
- `system_prompt` — título da **Etapa 2** (linha 22): *"### Etapa 2 — Expansão ponto a ponto **(Chain-of-Thought por ponto)**"* → remover o parêntese com CoT. Sugestão: *"### Etapa 2 — Expansão ponto a ponto"*.
- `techniques_applied` (linhas 72–74): remover `"Chain-of-Thought"`, deixando apenas `"Skeleton-of-Thought"`.
- `tags` (linha 80): remover `"chain-of-thought"`.

**Observação:** a essência do SoT (Etapa 1 esqueleto enxuto → Etapa 2 expansão independente por ponto → Etapa 3 consolidação) deve ser preservada. O ajuste é remover a **rotulação/declaração** de CoT, mantendo a expansão como mecanismo próprio do SoT, não como "raciocínio CoT".

---

### `prompts/bug_to_user_story_v7.yml` — ❌ MISTURADO (ReAct + CoT)

**Problema:** o arquivo deveria isolar **ReAct**, mas declara explicitamente **Chain of Thought** como técnica que sustenta a fase de Thought.

**Trechos a corrigir (remover CoT explícito):**

- `description` (linha 2): remover a frase *"A fase de Thought é sustentada por Chain-of-Thought."*
- `system_prompt` — bloco "Anatomia de cada ciclo" / "Thought" (linha 14): a descrição do **Thought** pode permanecer (raciocinar é intrínseco ao ReAct), mas **não** deve nomear "Chain-of-Thought". Verificar que nenhuma outra menção a CoT reste no corpo.
- `techniques_applied` (linhas 68–70): remover `"Chain-of-Thought"`, deixando apenas `"ReAct"`.
- `tags` (linha 76): remover `"chain-of-thought"`.

**Observação:** o raciocínio dentro do `Thought` é parte natural do ReAct (Reasoning + Acting). A correção é **não declarar CoT como técnica separada** nem listá-la em metadados — assim o arquivo passa a representar ReAct puro, com seus ciclos Thought → Action → Observation ancorados em evidência.

---

## Checklist de aplicação (quando for corrigir os arquivos)

- [ ] **v2:** remover seção de CoT (raciocínio passo a passo) e a palavra "raciocínio" da chamada final; `techniques_applied` = apenas Few-shot.
- [ ] **v3:** limpar metadados (remover Role Prompting); corpo inalterado.
- [ ] **v4:** (opcional) unificar metadado em "CoT with Self-Consistency"; corpo inalterado.
- [ ] **v5:** limpar metadados (remover Role Prompting); corpo inalterado.
- [ ] **v6:** remover declaração de CoT na `description` e no título da Etapa 2; `techniques_applied` = apenas SoT.
- [ ] **v7:** remover declaração de CoT na `description` e em qualquer menção no corpo; `techniques_applied` = apenas ReAct.

## Nota final

Após as correções, cada arquivo v2–v7 passará a aplicar **uma única técnica** da lista, com a persona (Role Prompting) mantida apenas como baseline neutro compartilhado e **não** declarada em `techniques_applied`. Recomenda-se padronizar `techniques_applied` para conter **exatamente uma** entrada por arquivo (no caso de v4, uma entrada composta), facilitando a verificação automatizada de que nenhum prompt mistura técnicas.
