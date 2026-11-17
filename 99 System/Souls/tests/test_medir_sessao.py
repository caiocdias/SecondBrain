"""Confere as medidas de medir_sessao.py sobre transcritos sintéticos."""
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "agents" / "scripts"
sys.path.insert(0, str(SCRIPTS))

T0 = 1_800_000_000


def quando(t):
    return datetime.fromtimestamp(T0 + t, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def prompt(t, texto="faça a tarefa"):
    return {"type": "user", "timestamp": quando(t), "message": {"role": "user", "content": texto}}


def assistente(t, mid, *usos):
    """usos: tuplas (id da chamada, nome da ferramenta, input)."""
    conteudo = [{"type": "tool_use", "id": i, "name": n, "input": inp} for i, n, inp in usos]
    return {"type": "assistant", "timestamp": quando(t),
            "message": {"id": mid, "model": "claude-teste", "usage": {"output_tokens": 1}, "content": conteudo}}


def resultado(t, uso_id):
    return {"type": "user", "timestamp": quando(t),
            "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": uso_id, "content": "ok"}]}}


def bash(uso_id, comando):
    return (uso_id, "Bash", {"command": comando})


def notificacao(t):
    """Aviso de término de uma tarefa em segundo plano, como o subagente o recebe."""
    return prompt(t, "[SYSTEM NOTIFICATION - NOT USER INPUT]\nThis is an automated background-task event.\n"
                     "<task-notification><task-id>b1</task-id><status>completed</status></task-notification>")


def entrega(uso_id):
    return (uso_id, "SubagentHandback", {"message": "pronto"})


class TestMedirSessao(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def sessao(self, principal, subagentes=()):
        """subagentes: tuplas (id do agente, tipo, registros[, descrição]). Devolve o caminho do .jsonl."""
        raiz = Path(self.tmp.name)
        arq = raiz / "s.jsonl"
        arq.write_text("".join(json.dumps(r) + "\n" for r in principal), encoding="utf-8")
        if subagentes:
            pasta = raiz / "s" / "subagents"
            pasta.mkdir(parents=True)
            for aid, tipo, registros, *resto in subagentes:
                desc = resto[0] if resto else f"Task {aid}"
                (pasta / f"agent-{aid}.jsonl").write_text(
                    "".join(json.dumps(r) + "\n" for r in registros), encoding="utf-8")
                (pasta / f"agent-{aid}.meta.json").write_text(
                    json.dumps({"agentType": tipo, "description": desc, "model": "sonnet"}),
                    encoding="utf-8")
        return str(arq)

    def medir(self, *args, **kwargs):
        from medir_sessao import medir
        return medir(*args, **kwargs)

    def test_paralelismo_e_tarefas(self):
        caminho = self.sessao(
            [prompt(0), assistente(1, "m0")],
            [("a1", "desenvolvedor", [prompt(0), assistente(100, "a")]),
             ("a2", "desenvolvedor", [prompt(50), assistente(150, "b")])])
        r = self.medir(caminho)
        self.assertEqual(r["sub_soma"], 200)
        self.assertEqual(r["sub_ativo"], 150)
        self.assertAlmostEqual(r["paralelismo"], 1.333, places=2)
        self.assertEqual(r["tarefas"], 2)

    def test_gates_por_tarefa(self):
        caminho = self.sessao(
            [prompt(0), assistente(1, "m0", bash("t0", "./gradlew build")), resultado(5, "t0"),
             assistente(6, "m1")],
            [("a1", "desenvolvedor", [
                prompt(0),
                assistente(10, "a", bash("t1", "./gradlew build --max-workers=2")), resultado(20, "t1"),
                assistente(21, "b", bash("t2", "./gradlew build --max-workers=2 2>&1 | tail -3")),
                resultado(30, "t2"),
                assistente(31, "c", bash("t3", "./gradlew :app:test --tests X")), resultado(40, "t3"),
                assistente(41, "d")]),
             ("a2", "desenvolvedor", [prompt(0), assistente(5, "e")])])
        r = self.medir(caminho)
        self.assertEqual(r["gates"], 3)
        self.assertEqual(r["gates_por_tarefa"], 1.5)

    def test_gate_regex_parametro(self):
        caminho = self.sessao(
            [prompt(0), assistente(1, "m0", bash("t0", "pytest -q")), resultado(5, "t0"), assistente(6, "m1")],
            [("a1", "desenvolvedor", [prompt(0), assistente(5, "a")])])
        self.assertEqual(self.medir(caminho)["gates"], 0)
        self.assertEqual(self.medir(caminho, gate_regex=r"pytest -q$")["gates"], 1)

    def test_gate_mencionado_em_texto_nao_conta(self):
        comandos = [
            'echo "gate: ./gradlew build → BUILD SUCCESSFUL" >> progress.md',
            "cat > relatorio.md <<'EOF'\n./gradlew build passou\nEOF",
            "cd app && timeout 300 ./gradlew build",
            "free -m; ./gradlew build ktlintCheck > saida.txt 2>&1; echo $?",
        ]
        principal = [prompt(0)]
        for i, c in enumerate(comandos):
            principal += [assistente(10 * i + 1, f"m{i}", bash(f"t{i}", c)), resultado(10 * i + 5, f"t{i}")]
        caminho = self.sessao(principal, [("a1", "desenvolvedor", [prompt(0), assistente(5, "a")])])
        self.assertEqual(self.medir(caminho)["gates"], 2)

    def test_fracao_testador(self):
        caminho = self.sessao(
            [prompt(0), assistente(1, "m0")],
            [("a1", "desenvolvedor", [prompt(0), assistente(5, "a")]),
             ("a2", "desenvolvedor", [prompt(0), assistente(5, "b")]),
             ("a3", "testador", [prompt(0), assistente(5, "c")], "Testador ataca Task 1")])
        r = self.medir(caminho)
        self.assertEqual(r["testadores"], 1)
        self.assertEqual(r["ataques"], 1)
        self.assertEqual(r["fracao_testador"], 0.5)

    def test_tarefa_de_teste_conta_como_tarefa_e_etapa_nao_conta_como_ataque(self):
        um = [prompt(0), assistente(5, "x")]
        caminho = self.sessao(
            [prompt(0), assistente(1, "m0", bash("t0", "./gradlew build")), resultado(5, "t0"), assistente(6, "m1")],
            [("a1", "desenvolvedor", um, "E06 Task 1: estado das permissões"),
             ("a2", "desenvolvedor", um, "Implementar Task 4 (pacote)"),
             ("a3", "testador", um, "E06 Task 2: fixtures dos ataques"),
             ("a4", "testador", um, "E06 testador ataca Task 1"),
             ("a5", "testador", um, "Testador de etapa da E06")])
        r = self.medir(caminho)
        self.assertEqual(r["tarefas"], 3)
        self.assertEqual(r["testadores"], 3)
        self.assertEqual(r["ataques"], 1)
        self.assertAlmostEqual(r["fracao_testador"], 1 / 3)
        self.assertAlmostEqual(r["gates_por_tarefa"], 1 / 3)

    def test_descricoes_de_ataque_das_sessoes_antigas(self):
        from medir_sessao import classe_testador
        for desc in ("Testar E02 Task 3", "E02 Task 4 testes de ataque", "Testador Task 1 (busca no core)",
                     "Test Task 2: port and texts", "Task 5: testador da tela", "Testador da Task 7",
                     "E10 Task 6: testador ataca o token"):
            with self.subTest(desc=desc):
                self.assertEqual(classe_testador(desc), "ataque")
        for desc in ("E08: testador de etapa", "Testador de etapa (foco Task 8)"):
            with self.subTest(desc=desc):
                self.assertEqual(classe_testador(desc), "etapa")
        for desc in ("E06 Task 2: fixtures dos ataques", "Task 3: travas aceitam roteiro-m3",
                     "E06 Task 8: nomes de teste e travas"):
            with self.subTest(desc=desc):
                self.assertEqual(classe_testador(desc), "tarefa")

    def test_espera_depois_da_entrega_nao_conta_como_ativo(self):
        caminho = self.sessao(
            [prompt(0), assistente(1, "m0")],
            [("a1", "desenvolvedor", [
                prompt(0),
                assistente(50, "a", entrega("h1")),
                resultado(100, "h1"),
                notificacao(4000),
                assistente(4005, "b")])])
        r = self.medir(caminho)
        self.assertEqual(r["sub_ativo"], 105)
        self.assertEqual(r["esperas_longas"], [])

    def test_espera_longa_sem_entrega_sai_do_ativo_e_e_listada(self):
        caminho = self.sessao(
            [prompt(0), assistente(1, "m0")],
            [("a1", "testador", [
                prompt(0),
                assistente(10, "a", bash("t1", "nohup python3 mutantes.py &")),
                resultado(20, "t1"),
                notificacao(3020),
                assistente(3030, "b")], "Testador de etapa da E06")])
        r = self.medir(caminho)
        self.assertEqual(r["sub_ativo"], 30)
        self.assertEqual(len(r["esperas_longas"]), 1)
        self.assertEqual(r["esperas_longas"][0]["papel"], "testador")
        self.assertEqual(r["esperas_longas"][0]["segundos"], 3000)
        self.assertEqual(r["espera_longa_total"], 3000)

    def test_espera_curta_em_segundo_plano_continua_ativa(self):
        caminho = self.sessao(
            [prompt(0), assistente(1, "m0")],
            [("a1", "desenvolvedor", [
                prompt(0),
                assistente(10, "a", bash("t1", "timeout 600 ./gradlew build")),
                resultado(20, "t1"),
                notificacao(620),
                assistente(630, "b")])])
        r = self.medir(caminho)
        self.assertEqual(r["sub_ativo"], 630)
        self.assertEqual(r["esperas_longas"], [])

    def test_relogio_sem_usuario(self):
        caminho = self.sessao([
            prompt(0),
            assistente(10, "m0", ("q1", "AskUserQuestion", {"questions": []})),
            resultado(310, "q1"),
            assistente(320, "m1"),
            prompt(520, "continue"),
            assistente(530, "m2")])
        r = self.medir(caminho)
        self.assertEqual(r["relogio"], 530)
        self.assertEqual(r["espera_usuario"], 300)
        self.assertEqual(r["nada_rodando"], 200)
        self.assertEqual(r["relogio_sem_usuario"], 30)

    def test_sessao_sem_subagentes(self):
        r = self.medir(self.sessao([prompt(0), assistente(1, "m0")]))
        self.assertEqual(r["tarefas"], 0)
        self.assertIsNone(r["paralelismo"])
        self.assertIsNone(r["gates_por_tarefa"])
        self.assertIsNone(r["fracao_testador"])

    def test_retomada_nao_conta_como_ativo(self):
        caminho = self.sessao(
            [prompt(0), assistente(1, "m0")],
            [("a1", "desenvolvedor", [
                prompt(0),
                assistente(50, "a", ("h1", "SubagentHandback", {"message": "pronto"})),
                resultado(100, "h1"),
                prompt(4000, "The coordinator sent a message while you were working:\ncorrija"),
                assistente(4010, "b")])])
        r = self.medir(caminho)
        self.assertEqual(r["sub_ativo"], 110)
        self.assertEqual(r["por_papel"]["desenvolvedor"]["ativo"], 110)

    def test_cli(self):
        caminho = self.sessao(
            [prompt(0), assistente(1, "m0")],
            [("a1", "desenvolvedor", [prompt(0), assistente(5, "a")])])
        saida = subprocess.run([sys.executable, "-I", str(SCRIPTS / "medir_sessao.py"), "-q", caminho],
                               capture_output=True, text=True)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        self.assertIn("gates por tarefa", saida.stdout)


if __name__ == "__main__":
    unittest.main()
