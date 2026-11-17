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
        self.assertIn("build ou validação completa", c)
        self.assertRegex(c, r"(?i)sem nenhum.{0,40}suíte inteira mais o lint")
        self.assertRegex(c, r"(?i)ondas? de uma tarefa só.{0,200}até 3 tarefas")

    def test_pergunta_nao_bloqueia(self):
        self.assertRegex(corpo("orquestrador"), r"(?is)AskUserQuestion.{0,300}(nada mais anda|fim do lote)")


class TestRevisaoFinal(unittest.TestCase):
    """Regras acrescentadas pela revisão final da branch."""

    def linha(self, nome, marca):
        return next((l for l in corpo(nome).splitlines() if marca in l), "")

    def test_ninguem_roda_a_suite_inteira_por_tarefa(self):
        self.assertRegex(corpo("desenvolvedor"), r"(?is)não rodo o gate do projeto nem a suíte inteira.{0,200}prompt implementer")
        self.assertRegex(corpo("testador"), r"(?i)não rodo o gate do projeto nem a suíte inteira")
        self.assertIn("substitui a suíte inteira", corpo("orquestrador"))

    def test_gate_vermelho_tem_continuacao_e_saida(self):
        vermelho = self.linha("orquestrador", "**Gate vermelho.**")
        for trecho in ("desde o último gate verde", "conta no limite de 5", "re-revisão escopada",
                       "o gate roda de novo", "`#bloqueada`"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, vermelho)

    def test_gate_de_integracao_coerente(self):
        gate = self.linha("orquestrador", "**Gate de integração.**")
        self.assertRegex(gate, r"(?i)onda de duas ou mais tarefas só sai com")
        self.assertNotIn("A onda seguinte só sai com o gate verde", gate)
        self.assertIn("com o SHA", gate)
        self.assertIn("saída do gate de integração no HEAD revisado, com o SHA", corpo("orquestrador"))

    def test_plano_antigo_sem_ondas(self):
        self.assertIn("cada tarefa restante é uma onda de uma tarefa só", corpo("orquestrador"))

    def test_vermelho_do_testador_de_etapa_tem_dono(self):
        self.assertIn("pela mesma regra do gate vermelho", self.linha("orquestrador", "**5. Testador de etapa"))

    def test_entrevista_de_abertura_no_fluxo(self):
        c = corpo("orquestrador")
        passo1 = c.split("**1. Entrada e plano.**")[1].split("**2. Revisão do plano.**")[0]
        paradas = c.split("## Quando paro e pergunto")[1]
        self.assertIn("entrevista de abertura do lote", passo1)
        self.assertIn("entrevista de abertura do lote", paradas)
        self.assertIn("Fora da entrevista de abertura", c)

    def test_revisor_arquitetura_confere_dependencia_na_onda(self):
        forma = self.linha("revisor-arquitetura", "`Risco: alto` sem")
        self.assertIn("na mesma onda que uma tarefa de que depende", forma)
        self.assertIn("fora de qualquer onda", forma)


class TestEsperaComPrazo(unittest.TestCase):
    """Regra contra travamento: em 2026-11-17 um laço `until ! pgrep -f` casou com a própria
    linha de comando e deixou a etapa parada por 2h39 (MEDICOES-desempenho.md, Medição 1)."""

    def test_quem_roda_teste_poe_limite_e_nao_faz_laco(self):
        for soul in ("desenvolvedor", "testador"):
            with self.subTest(soul=soul):
                c = corpo(soul)
                self.assertIn("`timeout", c)
                self.assertIn("notificação de término", c)
                self.assertRegex(c, r"(?i)não crio laço de espera")
                self.assertIn("`pgrep`", c)
                self.assertIn("`nohup`", c)
                self.assertRegex(c, r"(?i)estourou o limite")

    def test_gate_do_orquestrador_tem_limite(self):
        gate = next(l for l in corpo("orquestrador").splitlines() if "**Gate de integração.**" in l)
        self.assertIn("`timeout`", gate)
        self.assertRegex(gate, r"(?i)sem laço de espera")

    def test_orquestrador_tem_teto_de_espera_por_subagente(self):
        c = corpo("orquestrador")
        espera = next((l for l in c.splitlines() if "**Espera com teto.**" in l), "")
        self.assertRegex(espera, r"teto de \d+ min")
        self.assertIn("temporizador", espera)
        self.assertIn("SendMessage", espera)
        self.assertIn("TaskStop", espera)
        self.assertIn("não é sinal de vida", espera)


if __name__ == "__main__":
    unittest.main()
