import re
import subprocess
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL / "references" / "template.md"
CHECKER = SKILL / "scripts" / "check_roadmap.py"
AVISO = "não usa as souls"


def esqueleto():
    texto = TEMPLATE.read_text(encoding="utf-8")
    m = re.search(r"^````markdown\n(.*?)^````$", texto, re.S | re.M)
    assert m, "bloco ````markdown não encontrado no template"
    return m.group(1)


def verificar(conteudo):
    with tempfile.TemporaryDirectory() as d:
        arq = Path(d) / "roadmap-teste.md"
        arq.write_text(conteudo, encoding="utf-8")
        r = subprocess.run(
            ["python3", "-I", str(CHECKER), str(arq)],
            capture_output=True, text=True,
        )
        return r.stdout + r.stderr


class SoulsNoProtocolo(unittest.TestCase):
    def test_template_usa_souls(self):
        self.assertNotIn(AVISO, verificar(esqueleto()))

    def test_protocolo_sem_souls_avisa(self):
        linhas = [l for l in esqueleto().splitlines() if "testador" not in l]
        self.assertIn(AVISO, verificar("\n".join(linhas) + "\n"))


if __name__ == "__main__":
    unittest.main()
