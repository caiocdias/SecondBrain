"""Confere a estrutura dos arquivos de soul em agents/."""
import re
import unittest
from pathlib import Path

AGENTS = Path(__file__).resolve().parent.parent / "agents"
SOULS = {
    "desenvolvedor": "desenvolvedor",
    "testador": "testador",
    "revisor-seguranca": "revisor",
    "orquestrador-etapa": "orquestrador",
}
TITULOS = [
    "## Quem sou",
    "## O que prezo",
    "## O que recuso",
    "## Como trabalho",
    "## Como entrego",
    "## Quando paro e pergunto",
]
PREFIXO = "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/second-brain-souls/scripts/"


def dividir(texto):
    m = re.match(r"---\n(.*?)\n---\n(.*)\Z", texto, re.S)
    assert m, "frontmatter ausente"
    return m.group(1), m.group(2)


class TestSoulsFiles(unittest.TestCase):
    def test_nenhum_md_extra(self):
        achados = {p.stem for p in AGENTS.glob("*.md")}
        self.assertEqual(achados, set(SOULS))

    def test_cada_soul(self):
        for nome, papel in SOULS.items():
            with self.subTest(soul=nome):
                texto = (AGENTS / f"{nome}.md").read_text(encoding="utf-8")
                front, corpo = dividir(texto)
                self.assertRegex(front, rf"(?m)^name: {re.escape(nome)}$")
                self.assertRegex(front, r"(?m)^description: \S")
                for m in re.finditer(r"(?m)^\s*command: (.*)$", front):
                    cmd = m.group(1)
                    self.assertRegex(cmd, rf"soul_guard\.py\"? {re.escape(papel)}$")
                    self.assertIn(PREFIXO, cmd)
                for t in TITULOS:
                    self.assertRegex(corpo, rf"(?m)^{re.escape(t)}\s*$")
                self.assertLessEqual(len(corpo.strip("\n").splitlines()), 120)


if __name__ == "__main__":
    unittest.main()
