"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_V2_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def prompt():
    """Retorna o dicionário interno do prompt v2 (sob a chave de topo)."""
    data = load_prompts(str(PROMPT_V2_PATH))
    assert data, "YAML do prompt v2 vazio ou não encontrado"
    # O YAML tem uma única chave de topo (ex: 'bug_to_user_story_v2')
    top_key = next(iter(data))
    return data[top_key]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert 'system_prompt' in prompt, "Campo 'system_prompt' ausente"
        assert prompt['system_prompt'].strip(), "'system_prompt' está vazio"

    def test_prompt_has_role_definition(self, prompt):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system = prompt['system_prompt'].lower()
        assert "você é um" in system or "você é uma" in system, (
            "O prompt não define uma persona (ex: 'Você é um Product Manager')"
        )

    def test_prompt_mentions_format(self, prompt):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system = prompt['system_prompt'].lower()
        assert "user story" in system, "O prompt não menciona o formato 'User Story'"
        assert "critérios de aceitação" in system, (
            "O prompt não menciona 'Critérios de Aceitação'"
        )

    def test_prompt_has_few_shot_examples(self, prompt):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system = prompt['system_prompt'].lower()
        assert "relato de bug:" in system, "Não há exemplos de entrada (Relato de Bug)"
        assert "user story:" in system, "Não há exemplos de saída (User Story)"
        # Few-shot exige mais de um exemplo de par entrada/saída
        assert system.count("relato de bug:") >= 2, (
            "Few-shot requer pelo menos 2 exemplos de entrada/saída"
        )

    def test_prompt_no_todos(self, prompt):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        for field in ('description', 'system_prompt', 'user_prompt'):
            value = prompt.get(field, '')
            assert 'TODO' not in value, f"Campo '{field}' ainda contém TODO"

    def test_minimum_techniques(self, prompt):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt.get('techniques_applied', [])
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}"
        )

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])