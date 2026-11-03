"""Confere a estrutura dos arquivos de soul em agents/."""
import re
import unittest
from pathlib import Path

AGENTS = Path(__file__).resolve().parent.parent / "agents"
SOULS = {
    "desenvolvedor": "desenvolvedor",
    "testador": "testador",
    "revisor-seguranca": "revisor",
    "orquestrador": "orquestrador",
    "arquiteto": "arquiteto",
    "revisor-arquitetura": "revisor",
    "brain-escriba": "escriba",
    "brain-curador": "curador",
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
                # Escalar YAML sem aspas não aceita ": " nem " #"; o Claude Code
                # descarta em silêncio o agente com frontmatter inválido.
                desc = re.search(r"(?m)^description: (.*)$", front).group(1)
                self.assertNotIn(": ", desc)
                self.assertNotIn(" #", desc)
                comandos = re.findall(r"(?m)^\s*command: (.*)$", front)
                self.assertGreaterEqual(len(comandos), 1, "soul sem comando de guard")
                for cmd in comandos:
                    self.assertRegex(cmd, rf"soul_guard\.py\"? {re.escape(papel)}$")
                    self.assertIn(PREFIXO, cmd)
                for t in TITULOS:
                    self.assertRegex(corpo, rf"(?m)^{re.escape(t)}\s*$")
                self.assertLessEqual(len(corpo.strip("\n").splitlines()), 120)

    def test_orquestrador_despacha_souls_e_curadoria_sem_general_purpose(self):
        front, _ = dividir((AGENTS / "orquestrador.md").read_text(encoding="utf-8"))
        tools = re.search(r"(?m)^tools: (.*)$", front).group(1)
        tipos = {t.strip() for t in re.search(r"Agent\(([^)]*)\)", tools).group(1).split(",")}
        curadoria = {"curadoria-leitor-visual", "curadoria-auditor-visual", "curadoria-investigador",
                     "curadoria-corretor", "curadoria-verificador"}
        souls = {"desenvolvedor", "testador", "revisor-seguranca", "revisor-arquitetura", "brain-escriba"}
        self.assertEqual(tipos, souls | curadoria)
        self.assertNotIn("general-purpose", tipos)

    def test_escriba_ensina_o_comando_uuid_que_o_guard_aceita(self):
        import sys
        sys.path.insert(0, str(AGENTS / "scripts"))
        from soul_guard import decide
        texto = (AGENTS / "brain-escriba.md").read_text(encoding="utf-8")
        cmd = 'python3 -I -c "import uuid; print(uuid.uuid4())"'
        self.assertIn(f"`{cmd}`", texto)
        self.assertIsNone(decide("escriba", "Bash", {"command": cmd}, "/r", Path("/nao/existe")))


if __name__ == "__main__":
    unittest.main()
