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


class TestRevisores(unittest.TestCase):
    def test_revisor_arquitetura_lista_fechada(self):
        c = corpo("revisor-arquitetura")
        for item in LISTA_FECHADA:
            with self.subTest(item=item):
                self.assertIn(item, c)

    def test_revisor_arquitetura_achados_de_forma(self):
        c = corpo("revisor-arquitetura")
        forma = next((l for l in c.splitlines() if "`Risco: alto` sem" in l), "")
        self.assertIn("Importantes", forma)
        self.assertIn("`Risco: normal` em tarefa que toca um item da lista", forma)
        self.assertIn("## Ondas", forma)
        self.assertIn("`Depende de:` declarado sem", forma)

    def test_revisor_seguranca_evidencia(self):
        c = corpo("revisor-seguranca")
        self.assertIn("verificação da tarefa", c)
        self.assertIn("gate do projeto", c)


class TestOrquestrador(unittest.TestCase):
    def test_termos(self):
        c = corpo("orquestrador")
        for termo in ("gate de integração", "gate do projeto", "## Ondas", "verificação da tarefa",
                      "entrevista de abertura do lote"):
            with self.subTest(termo=termo):
                self.assertIn(termo, c)

    def test_lista_fechada_igual_ao_revisor(self):
        c = corpo("orquestrador")
        for item in LISTA_FECHADA:
            with self.subTest(item=item):
                self.assertIn(item, c)
        self.assertNotIn("o núcleo que a etapa existe para entregar", c)

    def test_gate(self):
        c = corpo("orquestrador")
        self.assertNotIn("rodo a suíte inteira uma vez", c)
        self.assertIn("limites das tarefas", c)
        self.assertRegex(c, r"(?i)sem (essa|a) linha.{0,80}suíte inteira")
        self.assertRegex(c, r"(?i)ondas? de uma tarefa só.{0,200}até 3 tarefas")

    def test_pergunta_nao_bloqueia(self):
        self.assertRegex(corpo("orquestrador"), r"(?is)AskUserQuestion.{0,300}(nada mais anda|fim do lote)")


if __name__ == "__main__":
    unittest.main()
