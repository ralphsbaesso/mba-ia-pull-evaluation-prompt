"""
Script para fazer push (PÚBLICO) do prompt otimizado v2 para o LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida a estrutura do YAML.
3. Faz push PÚBLICO para o LangSmith Hub com tags e descrição vindas do YAML.

Uso:
    ./venv/bin/python src/push_prompts.py
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import (
    load_yaml,
    check_env_vars,
    print_section_header,
)

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt no Hub (ex.: 'username/bug_to_user_story_v2')
        prompt_data: Dados do prompt (system_prompt, user_prompt, tags, etc.)

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt_data["system_prompt"]),
                ("human", prompt_data["user_prompt"]),
            ]
        )

        tags = prompt_data.get("tags", [])
        description = prompt_data.get("description", "")

        print(f"⬆️  Fazendo push PÚBLICO de '{prompt_name}'...")
        url = hub.push(
            prompt_name,
            prompt,
            new_repo_is_public=True,
            new_repo_description=description,
            tags=tags,
        )
        print(f"✅ Prompt publicado: {url}")
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer push: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (campos obrigatórios + ≥ 1 técnica).

    Aqui exigimos pelo menos 1 técnica em techniques_applied.

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = ["description", "system_prompt", "user_prompt", "version"]
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    system_prompt = prompt_data.get("system_prompt", "").strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")
    if "TODO" in system_prompt:
        errors.append("system_prompt ainda contém TODOs")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 1:
        errors.append(f"Mínimo de 1 técnica requerida, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH PROMPT — LangSmith Hub")

    # 1. Checar variáveis de ambiente
    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")

    # 2. Carregar YAML do v2
    yaml_path = "prompts/bug_to_user_story_v2.yml"
    data = load_yaml(yaml_path)
    if data is None:
        return 1

    prompt_key = "bug_to_user_story_v2"
    prompt_data = data.get(prompt_key)
    if prompt_data is None:
        print(f"❌ Chave '{prompt_key}' não encontrada em {yaml_path}")
        return 1

    # 3. Validar estrutura (antes de qualquer chamada ao Hub)
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Estrutura do prompt inválida:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print(f"✅ Estrutura do prompt '{prompt_key}' validada.")

    # 4. Push PÚBLICO
    prompt_name = f"{username}/{prompt_key}"
    if not push_prompt_to_langsmith(prompt_name, prompt_data):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
