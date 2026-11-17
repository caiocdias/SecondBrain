"""Fixa, no texto das souls, as regras de DESIGN-desempenho.md que não podem sumir nem divergir."""
import re
import unittest
from pathlib import Path

AGENTS = Path(__file__).resolve().parent.parent / "agents"

# Os itens de `Risco: alto`, escritos do mesmo jeito no orquestrador e no revisor-arquitetura.
LISTA_FECHADA = (
    "autenticação ou autorização",
    "dado pessoal ou segredo",
    "cálculo de valor monetário",
    "migração ou escrita destrutiva de dados",
    "concorrência",
    "parsing de entrada externa não confiável",
)


def corpo(nome):
    """Corpo da soul, sem o frontmatter."""
    texto = (AGENTS / f"{nome}.md").read_text(encoding="utf-8")
    return re.match(r"---\n.*?\n---\n(.*)\Z", texto, re.S).group(1)


class TestVerificacaoDaTarefa(unittest.TestCase):
    def test_desenvolvedor(self):
        c = corpo("desenvolvedor")
        self.assertIn("verificação da tarefa", c)
        self.assertIn("verificação rápida", c)
        self.assertRegex(c, r"(?i)não rodo o gate")
        self.assertIn("Sem a linha", c)
        self.assertNotIn("A suíte inteira roda uma vez", c)
        self.assertNotIn("saída real da suíte inteira", c)

    def test_testador(self):
        c = corpo("testador")
        self.assertIn("verificação da tarefa", c)
        self.assertIn("verificação rápida", c)
        self.assertRegex(c, r"(?i)não rodo o gate")
        self.assertNotIn("Rodo a suíte inteira no final", c)
        self.assertNotIn("com foco nas tarefas que passaram sem mim", c)
        self.assertNotIn("saída real da suíte inteira", c)


if __name__ == "__main__":
    unittest.main()
