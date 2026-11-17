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


class TestMedirSessao(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def sessao(self, principal, subagentes=()):
        """subagentes: tuplas (id do agente, tipo, registros). Devolve o caminho do .jsonl."""
        raiz = Path(self.tmp.name)
        arq = raiz / "s.jsonl"
        arq.write_text("".join(json.dumps(r) + "\n" for r in principal), encoding="utf-8")
        if subagentes:
            pasta = raiz / "s" / "subagents"
            pasta.mkdir(parents=True)
            for aid, tipo, registros in subagentes:
                (pasta / f"agent-{aid}.jsonl").write_text(
                    "".join(json.dumps(r) + "\n" for r in registros), encoding="utf-8")
                (pasta / f"agent-{aid}.meta.json").write_text(
                    json.dumps({"agentType": tipo, "description": f"tarefa {aid}", "model": "sonnet"}),
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
             ("a3", "testador", [prompt(0), assistente(5, "c")])])
        r = self.medir(caminho)
        self.assertEqual(r["testadores"], 1)
        self.assertEqual(r["fracao_testador"], 0.5)

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
