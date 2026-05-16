"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt `leonanluppi/bug_to_user_story_v1` do Hub
3. Salva localmente em 2026-05-16/bug_to_user_story_v1.yml
"""

import sys
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "2026-05-16/bug_to_user_story_v1.yml"


def pull_prompts_from_langsmith():
    """Faz pull do prompt v1 do LangSmith Hub e retorna como dict."""
    print(f"⬇️  Fazendo pull de '{PROMPT_NAME}'...")
    prompt = hub.pull(PROMPT_NAME)

    system_prompt = ""
    user_prompt = ""

    for message in getattr(prompt, "messages", []):
        template = getattr(message, "prompt", None)
        text = getattr(template, "template", "") if template else ""
        role = type(message).__name__.lower()

        if "system" in role:
            system_prompt = text
        elif "human" in role or "user" in role:
            user_prompt = text

    data = {
        "bug_to_user_story_v1": {
            "description": "Prompt v1 (baseline) para converter bug reports em user stories.",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "1.0.0",
            "techniques_applied": [],
            "tags": ["baseline", "v1"],
        }
    }

    return data


def main():
    """Função principal"""
    print_section_header("PULL PROMPT v1 — LangSmith Hub")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    try:
        data = pull_prompts_from_langsmith()
    except Exception as e:
        print(f"❌ Erro ao fazer pull: {e}")
        return 1

    if not save_yaml(data, OUTPUT_PATH):
        return 1

    print(f"✅ Prompt salvo em: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
