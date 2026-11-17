"""Fixa, no texto das souls, as regras do ciclo de execução que não podem sumir nem divergir.

O ciclo em vigor é o de DESIGN-enxuto.md (contrato da etapa, fatias em série, avaliação no fim),
com a verificação da tarefa e a espera com prazo que vieram de DESIGN-desempenho.md."""
import re
import unittest
from pathlib import Path

AGENTS = Path(__file__).resolve().parent.parent / "agents"

# Os riscos que o contrato da etapa declara, escritos do mesmo jeito no orquestrador e no revisor-arquitetura.
LISTA_FECHADA = (
    "autenticação ou autorização",
    "dado pessoal ou segredo",
    "cálculo de valor monetário",
    "migração ou escrita destrutiva de dados",
    "concorrência",
    "parsing de entrada externa não confiável",
)
ONDA = r"(?i)\bondas?\b"


def corpo(nome):
    """Corpo da soul, sem o frontmatter."""
    texto = (AGENTS / f"{nome}.md").read_text(encoding="utf-8")
    return re.match(r"---\n.*?\n---\n(.*)\Z", texto, re.S).group(1)


def linha(nome, marca):
    return next((l for l in corpo(nome).splitlines() if marca in l), "")


def trecho(nome, inicio, fim):
    """Texto do corpo entre duas marcas; vazio se a primeira não existe."""
    c = corpo(nome)
    if inicio not in c: return ""
    return c.split(inicio, 1)[1].split(fim, 1)[0]


class TestVerificacaoDaTarefa(unittest.TestCase):
    def test_desenvolvedor(self):
        c = corpo("desenvolvedor")
        self.assertIn("verificação da tarefa", c)
        self.assertIn("verificação rápida", c)
        self.assertIn("Sem a linha", c)
        self.assertNotIn("A suíte inteira roda uma vez", c)
        self.assertNotIn("saída real da suíte inteira", c)

    def test_testador(self):
        c = corpo("testador")
        self.assertIn("verificação da tarefa", c)
        self.assertIn("verificação rápida", c)
        self.assertNotIn("Rodo a suíte inteira no final", c)
        self.assertNotIn("saída real da suíte inteira", c)

    def test_ninguem_roda_a_suite_inteira_por_tarefa(self):
        self.assertRegex(corpo("desenvolvedor"), r"(?is)não rodo o gate do projeto nem a suíte inteira.{0,200}prompt implementer")
        self.assertRegex(corpo("testador"), r"(?i)não rodo o gate do projeto nem a suíte inteira")
        self.assertIn("substitui a suíte inteira", corpo("orquestrador"))


class TestContratoDaEtapa(unittest.TestCase):
    def test_plano_em_fatias(self):
        c = corpo("orquestrador")
        for trecho_ in ("de 1 a 3 fatias", "`### Task N`", "Critérios de aceite", "o comando ou o teste que o confere",
                        "Áreas tocadas", "`Riscos:`", "60 min de construção", "12 arquivos de produção"):
            with self.subTest(trecho=trecho_):
                self.assertIn(trecho_, c)

    def test_saem_ondas_estimativa_e_risco_por_tarefa(self):
        for soul in ("orquestrador", "desenvolvedor", "testador", "revisor-arquitetura"):
            with self.subTest(soul=soul):
                # A regra de transição do orquestrador cita o formato antigo de propósito.
                c = "\n".join(l for l in corpo(soul).splitlines() if "Plano fora deste formato" not in l)
                self.assertNotRegex(c, ONDA)
                self.assertNotIn("`Estimativa", c)
                self.assertNotIn("`Risco: alto`", c)

    def test_plano_fora_do_formato_tem_regra_de_transicao(self):
        transicao = linha("orquestrador", "Plano fora deste formato")
        for trecho_ in ("cada tarefa restante é uma fatia", "com revisão de fatia", "Worktree de tarefa ainda aberto",
                        "vale este texto"):
            with self.subTest(trecho=trecho_):
                self.assertIn(trecho_, transicao)

    def test_tamanho_da_fatia_e_conferivel(self):
        self.assertIn("`Tamanho:`", corpo("orquestrador"))
        forma = linha("revisor-arquitetura", "o comando ou o teste que o confere")
        self.assertIn("`Tamanho:`", forma)
        self.assertIn("mais de 3 fatias", forma)
        self.assertIn("60 min de construção", forma)
        self.assertRegex(corpo("orquestrador"), r'(?i)`Depende de:` \(fatias ou "nenhuma"')
        self.assertRegex(corpo("orquestrador"), r"(?i)confiro a forma do contrato")

    def test_lista_fechada_igual_nas_tres_souls(self):
        for soul in ("orquestrador", "revisor-arquitetura", "revisor-seguranca"):
            c = corpo(soul)
            for item in LISTA_FECHADA:
                with self.subTest(soul=soul, item=item):
                    self.assertIn(item, c)

    def test_revisor_arquitetura_confere_a_forma_do_contrato(self):
        forma = linha("revisor-arquitetura", "o comando ou o teste que o confere")
        for trecho_ in ("Importantes", "12 arquivos de produção", "`Riscos:`", "`Depende de:` declarado sem"):
            with self.subTest(trecho=trecho_):
                self.assertIn(trecho_, forma)


class TestRevisaoDeArquitetura(unittest.TestCase):
    def test_obrigatoria_em_lista_fechada_e_dispensada_fora_dela(self):
        passo = trecho("orquestrador", "**2. Revisão do plano.**", "**3. ")
        self.assertRegex(passo, r"(?is)obrigatória quando.{0,300}contrato público")
        for trecho_ in ("persistência ou migração", "fronteira de módulo ou serviço", "peça nova de runtime", "dispensada"):
            with self.subTest(trecho=trecho_):
                self.assertIn(trecho_, passo)

    CRITERIO = ("cria ou contraria decisão de ADR ou ARCHITECTURE, muda contrato público (API, DTO, schema, "
                "formato persistido), persistência ou migração, fronteira de módulo ou serviço, ou traz peça nova "
                "de runtime (serviço, banco, framework)")

    def test_criterio_igual_no_orquestrador_e_na_revisora(self):
        for soul in ("orquestrador", "revisor-seguranca"):
            with self.subTest(soul=soul):
                self.assertIn(self.CRITERIO, corpo(soul))

    def test_revisora_confere_a_dispensa_contra_o_diff(self):
        c = corpo("revisor-seguranca")
        self.assertRegex(c, r"(?is)dispensada.{0,500}bloqueio")
        self.assertRegex(c, r"(?is)`Riscos:` cobre.{0,200}Importante")

    def test_dispensa_indevida_tem_proximo_passo(self):
        passo = trecho("orquestrador", "**2. Revisão do plano.**", "**3. ")
        self.assertIn("Na dúvida, a revisão é obrigatória", passo)
        self.assertRegex(passo, r"(?is)dispensa indevida.{0,300}despacho o `revisor-arquitetura`")
        self.assertIn("antes da primeira `### Task`", passo)


class TestCicloPorFatia(unittest.TestCase):
    def test_uma_fatia_por_vez_no_worktree_da_etapa(self):
        passo = trecho("orquestrador", "**3. Ciclo por fatia.**", "**Conferência de cada despacho.**")
        self.assertRegex(passo, r"(?i)uma fatia por vez")
        self.assertIn("worktree da etapa", passo)
        self.assertNotIn("-t<N>", corpo("orquestrador"))

    def test_revisao_por_fatia_so_com_mais_de_uma(self):
        passo = trecho("orquestrador", "**3. Ciclo por fatia.**", "**Conferência de cada despacho.**")
        self.assertIn("Etapa de uma fatia só", passo)
        self.assertRegex(passo, r"(?i)duas ou mais")
        self.assertRegex(passo, r"(?i)no máximo 2 rodadas por fatia")
        self.assertIn("`#bloqueada`", passo)

    def test_superpowers_sobreposto_por_escrito(self):
        passo = trecho("orquestrador", "**3. Ciclo por fatia.**", "**Conferência de cada despacho.**")
        for trecho_ in ("rodadas 4–5", "breaker", "despacho a `revisor-seguranca` antes da fatia seguinte",
                        "revisão na revisão final", "HEAD da branch no início da etapa"):
            with self.subTest(trecho=trecho_):
                self.assertIn(trecho_, passo)
        self.assertIn("`final-review.md`", trecho("orquestrador", "**5. Fim da etapa.**", "**6. Fechamento.**"))

    def test_conferencia_de_despacho_e_integridade_ficam(self):
        c = corpo("orquestrador")
        self.assertIn("**Conferência de cada despacho.**", c)
        self.assertIn("check_test_integrity.py", trecho("orquestrador", "**3. Ciclo por fatia.**", "**Conferência"))

    def test_desenvolvedor_trabalha_por_fatia(self):
        c = corpo("desenvolvedor")
        self.assertIn("fatia", c)
        self.assertIn("worktree da etapa", c)


class TestFimDaEtapa(unittest.TestCase):
    def test_gate_de_integracao(self):
        gate = linha("orquestrador", "**Gate de integração.**")
        for trecho_ in ("gate do projeto", "build ou validação completa", "`timeout`", "com o SHA",
                        "no fim da construção", "antes do merge na principal"):
            with self.subTest(trecho=trecho_):
                self.assertIn(trecho_, gate)
        self.assertRegex(gate, r"(?i)sem nenhum.{0,40}suíte inteira mais o lint")
        self.assertRegex(gate, r"(?i)sem laço de espera")

    def test_testador_e_revisao_final_em_paralelo(self):
        fim = trecho("orquestrador", "**5. Fim da etapa.**", "**6. Fechamento.**")
        for trecho_ in ("ao mesmo tempo", "teto de 30 min", "contrato da etapa", "re-revisão escopada",
                        "resíduo", "`#bloqueada`", "com o SHA"):
            with self.subTest(trecho=trecho_):
                self.assertIn(trecho_, fim)
        self.assertRegex(fim, r"(?i)com ou sem achados")
        self.assertRegex(fim, r"(?i)no máximo 2 rodadas")

    def test_garantias_do_fim_da_etapa(self):
        fim = trecho("orquestrador", "**5. Fim da etapa.**", "**6. Fechamento.**")
        for trecho_ in ("`code-reviewer.md`", "`MERGE_BASE..HEAD`", "corrige o **código**, nunca o teste",
                        "check_test_integrity.py --base <MERGE_BASE>", "depois de cada rodada de correção",
                        "o testador corrige o próprio teste", "nunca ao desenvolvedor", "não se estaciona",
                        "testes ainda não revisados", "rodo de novo uma vez"):
            with self.subTest(trecho=trecho_):
                self.assertIn(trecho_, fim)

    def test_bloqueada_nao_entra_na_principal(self):
        fechamento = trecho("orquestrador", "**6. Fechamento.**", "**Registro.**")
        for trecho_ in ("não entra na principal nem serve de base", "última etapa `#concluida`",
                        "vermelho nunca entra na principal"):
            with self.subTest(trecho=trecho_):
                self.assertIn(trecho_, fechamento)
        recuso = trecho("orquestrador", "## O que recuso", "## Como trabalho")
        self.assertIn("Integrar na principal código de etapa `#bloqueada`", recuso)
        self.assertIn("relatório do testador de etapa", recuso)

    def test_travas_de_quem_escreve(self):
        self.assertIn("Alterar, apagar, enfraquecer ou pular testes de commits com `Soul: testador`", corpo("desenvolvedor"))
        self.assertIn("Alterar código de produção", corpo("testador"))
        self.assertIn("verde, no HEAD revisado", corpo("revisor-seguranca"))
        self.assertRegex(corpo("revisor-seguranca"), r"(?i)reviso por inteiro os testes do testador")

    def test_testador_tem_dois_casos_e_teto(self):
        c = corpo("testador")
        self.assertIn("uma vez por etapa", c)
        self.assertIn("contrato da etapa", c)
        self.assertRegex(c, r"(?i)teto de tempo")
        self.assertIn("`date +%s`", c)

    def test_revisor_seguranca_evidencia(self):
        c = corpo("revisor-seguranca")
        self.assertIn("verificação da tarefa", c)
        self.assertIn("gate do projeto", c)
        self.assertRegex(c, r"(?i)revisão de fatia")


class TestDecisoes(unittest.TestCase):
    def test_entrevista_de_abertura_no_fluxo(self):
        c = corpo("orquestrador")
        passo1 = c.split("**1. Entrada e plano.**")[1].split("**2. Revisão do plano.**")[0]
        paradas = c.split("## Quando paro e pergunto")[1]
        self.assertIn("entrevista de abertura do lote", passo1)
        self.assertIn("entrevista de abertura do lote", paradas)
        self.assertIn("Fora da entrevista de abertura", c)

    def test_pergunta_nao_bloqueia(self):
        self.assertRegex(corpo("orquestrador"), r"(?is)AskUserQuestion.{0,300}(nada mais anda|fim do lote)")


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

    def test_orquestrador_tem_teto_de_espera_por_subagente(self):
        espera = linha("orquestrador", "**Espera com teto.**")
        self.assertRegex(espera, r"teto de \d+ min")
        for trecho_ in ("temporizador", "SendMessage", "TaskStop", "não é sinal de vida"):
            with self.subTest(trecho=trecho_):
                self.assertIn(trecho_, espera)


if __name__ == "__main__":
    unittest.main()
