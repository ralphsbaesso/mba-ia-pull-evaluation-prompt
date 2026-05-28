# Implementar o push dos prompts para o LangSmith Hub

## Objetivo

Implementar o script `src/push_prompts.py` para fazer **push público** de um prompt
otimizado (`prompts/bug_to_user_story_{v2..v7}.yml`) para o LangSmith Prompt Hub.

O script deve receber **por parâmetro** qual versão será publicada e validar que o
valor está no intervalo permitido (**v2 a v7**), antes de qualquer chamada ao Hub.

## Comportamento esperado

O script deve:

1. Ler a versão do prompt informada por parâmetro de linha de comando.
2. Validar que a versão está entre `v2` e `v7` (recusar `v1` e versões inexistentes).
3. Carregar o YAML correspondente de `prompts/bug_to_user_story_{versao}.yml`.
4. Validar a estrutura do prompt (campos obrigatórios + mínimo de 2 técnicas).
5. Fazer push **PÚBLICO** para o LangSmith Hub (`is_public=True`).
6. Anexar metadados ao push: `tags` e descrição vindas do próprio YAML.

## Parâmetros (CLI)

```bash
./venv/bin/python src/push_prompts.py <versao>
# exemplos:
./venv/bin/python src/push_prompts.py v2
./venv/bin/python src/push_prompts.py v7
```

Regras de validação do parâmetro:

- Obrigatório. Sem argumento → imprimir uso e sair com código `1`.
- Aceitar apenas `v2`, `v3`, `v4`, `v5`, `v6` e `v7`.
- Qualquer outro valor (ex.: `v1`, `v8`, `2`, `foo`) → mensagem de erro clara e saída `1`.

## Funções a implementar

- `validate_prompt(prompt_data: dict) -> tuple[bool, list]`
  Reaproveitar `utils.validate_prompt_structure` (campos obrigatórios e ≥ 2 técnicas).
  Retornar `(is_valid, errors)`.

- `push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool`
  Montar um `ChatPromptTemplate` a partir de `system_prompt` e `user_prompt` do YAML e
  publicar com `hub.push(..., is_public=True)`. Retornar `True`/`False`.

- `main()`
  Orquestrar: ler/validar argumento → checar `LANGSMITH_API_KEY` → carregar YAML →
  validar estrutura → push. Retornar `0` em sucesso, `1` em falha.

## Nome do prompt no Hub

Construir a partir de `USERNAME_LANGSMITH_HUB` do `.env`:
`{username}/bug_to_user_story_{versao}` — coerente com o que `evaluate.py` espera.
Sem a variável, abortar com erro.

## Convenções do projeto

- Reusar os helpers de `src/utils.py`: `load_yaml`, `check_env_vars`,
  `print_section_header`, `validate_prompt_structure`.
- Seguir o estilo de `src/pull_prompts.py` (mensagens com emoji, `sys.exit(main())`).
- A chave do YAML é `bug_to_user_story_{versao}`; os templates usam sintaxe LangChain
  (`{bug_report}`).

## Critérios de aceite

- [ ] `push_prompts.py v1` falha com mensagem de versão inválida.
- [ ] `push_prompts.py` sem argumento imprime o uso e sai com `1`.
- [ ] `push_prompts.py v2` publica o prompt público no Hub com tags e descrição.
- [ ] Estrutura inválida (sem 2 técnicas) bloqueia o push antes da chamada ao Hub.
- [ ] O nome publicado segue `{USERNAME_LANGSMITH_HUB}/bug_to_user_story_{versao}`.
