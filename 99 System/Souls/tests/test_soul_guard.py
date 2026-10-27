import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "agents" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import soul_guard  # noqa: E402
from soul_guard import decide, is_test_path  # noqa: E402

VAULT = Path("/nonexistent/vault")


class SoulGuardTest(unittest.TestCase):
    def test_is_test_path(self):
        for p in [
            "src/test/kotlin/br/x/RoomServiceTest.kt",
            "tests/test_api.py",
            "pkg/foo_test.go",
            "web/src/App.test.tsx",
            "src/__tests__/x.js",
            "app/src/integrationTest/kotlin/A.kt",
        ]:
            self.assertTrue(is_test_path(p), p)
        for p in [
            "src/main/kotlin/br/x/RoomService.kt",
            "src/latest/x.py",
            "contest.py",
            "README.md",
            "build.gradle.kts",
        ]:
            self.assertFalse(is_test_path(p), p)

    def test_testador_bloqueia_producao(self):
        self.assertIsNotNone(decide("testador", "Write", {"file_path": "/r/src/main/A.kt"}, "/r", VAULT))
        self.assertIsNone(decide("testador", "Write", {"file_path": "/r/src/test/ATest.kt"}, "/r", VAULT))

    def test_caminho_relativo_igual_absoluto(self):
        rel = decide("testador", "Write", {"file_path": "src/main/A.kt"}, "/r", VAULT)
        ab = decide("testador", "Write", {"file_path": "/r/src/main/A.kt"}, "/r", VAULT)
        self.assertIsNotNone(rel)
        self.assertEqual(rel, ab)
        self.assertIsNone(decide("testador", "Write", {"file_path": "src/test/ATest.kt"}, "/r", VAULT))

    def test_orquestrador(self):
        for p in ["docs/superpowers/plans/p.md", ".superpowers/sdd/x/progress.md"]:
            self.assertIsNone(decide("orquestrador", "Write", {"file_path": p}, "/r", VAULT), p)
        self.assertIsNotNone(decide("orquestrador", "Write", {"file_path": "src/main/A.kt"}, "/r", VAULT))

    def test_escriba_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "Second Brain"
            (vault / "00 Inbox").mkdir(parents=True)
            (vault / "20 Knowledge").mkdir()
            nota = vault / "00 Inbox" / "nova.md"
            call = lambda p: decide("escriba", "Write", {"file_path": str(p)}, str(vault), vault)
            self.assertIsNone(call(nota))
            nota.write_text("x")
            self.assertIsNotNone(call(nota))
            self.assertIsNotNone(call(vault / "20 Knowledge" / "x.md"))
            self.assertIsNotNone(decide("escriba", "Edit", {"file_path": str(nota)}, str(vault), vault))
            self.assertIsNotNone(decide("escriba", "NotebookEdit", {"notebook_path": str(nota)}, str(vault), vault))

    def test_escriba_bash(self):
        bash = lambda c: decide("escriba", "Bash", {"command": c}, "/r", VAULT)
        for c in ["date +%F", "uuidgen", 'python3 -c "import uuid; print(uuid.uuid4())"', "git log -1"]:
            self.assertIsNone(bash(c), c)
        for c in ["echo x > a.md", "date; rm x", "git commit -m x", 'python3 -c "import uuid; open(1)"',
                  'python3 -c "import uuid; print(1); import os"']:
            self.assertIsNotNone(bash(c), c)

    def test_push_bloqueado(self):
        for papel in ["desenvolvedor", "testador", "escriba", "revisor", "curador"]:
            self.assertIsNotNone(
                decide(papel, "Bash", {"command": "git push origin x"}, "/r", VAULT), papel)
        self.assertIsNone(decide("orquestrador", "Bash", {"command": "git push origin x"}, "/r", VAULT))

    def test_curador_destrutivo(self):
        bash = lambda c: decide("curador", "Bash", {"command": c}, "/r", VAULT)
        for c in ["git reset --hard HEAD", "git clean -fd", "rm -rf x"]:
            self.assertIsNotNone(bash(c), c)
        self.assertIsNone(bash("git status"))

    def test_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "com espaco"
            d.mkdir()
            script = d / "soul_guard.py"
            shutil.copy(SCRIPTS / "soul_guard.py", script)

            def run(payload):
                return subprocess.run(["python3", "-I", str(script), "testador"],
                                      input=json.dumps(payload), capture_output=True, text=True)

            r = run({"tool_name": "Write", "tool_input": {"file_path": "/r/src/main/A.kt"}, "cwd": "/r"})
            self.assertEqual(r.returncode, 2)
            self.assertTrue(r.stderr.strip())
            r = run({"tool_name": "Read", "tool_input": {"file_path": "/r/src/main/A.kt"}, "cwd": "/r"})
            self.assertEqual(r.returncode, 0)


class HardeningTest(unittest.TestCase):
    def bash(self, role, cmd):
        return decide(role, "Bash", {"command": cmd}, "/r", VAULT)

    def test_escriba_operadores(self):
        for c in ["date & rm -rf x", "ls <(rm -rf x)", "date\nrm x", "ls $(rm x)", "date `rm x`",
                  "ls < /etc/passwd", "(rm x)"]:
            self.assertIsNotNone(self.bash("escriba", c), c)

    def test_escriba_git_output_e_branch(self):
        for c in ["git log --output=/tmp/x", "git diff --output x", "git show --output=a",
                  "git branch -D x", "git branch -m a b", "git branch novo"]:
            self.assertIsNotNone(self.bash("escriba", c), c)
        for c in ["git branch", "git branch --list", "git branch -a", "git branch -r",
                  "git branch --show-current", "git branch -vv", "git status"]:
            self.assertIsNone(self.bash("escriba", c), c)

    def test_git_entre_aspas(self):
        self.assertIsNotNone(self.bash("desenvolvedor", '"git" push origin x'))
        self.assertIsNotNone(self.bash("curador", "git -C . push"))

    def test_curador_opcoes_longas(self):
        for c in ["rm --recursive --force x", "git clean --force", "rm -r -f x", "rm -fr x"]:
            self.assertIsNotNone(self.bash("curador", c), c)
        self.assertIsNone(self.bash("curador", "rm x"))

    def test_is_test_path_relativo_ao_cwd(self):
        self.assertFalse(is_test_path("/home/x/tests/proj/src/main/A.kt", "/home/x/tests/proj"))
        self.assertTrue(is_test_path("/home/x/tests/proj/src/test/ATest.kt", "/home/x/tests/proj"))
        self.assertTrue(is_test_path("/home/x/tests/proj/src/test/A.kt", "/elsewhere"))
        self.assertIsNotNone(decide("testador", "Write",
                                    {"file_path": "/home/x/tests/proj/src/main/A.kt"},
                                    "/home/x/tests/proj", VAULT))

    def test_multiedit_e_notebook(self):
        self.assertIsNotNone(decide("testador", "MultiEdit", {"file_path": "/r/src/main/A.kt"}, "/r", VAULT))
        self.assertIsNotNone(decide("testador", "NotebookEdit", {"notebook_path": "/r/src/n.ipynb"}, "/r", VAULT))
        self.assertIsNone(decide("testador", "NotebookEdit", {"notebook_path": "/r/tests/n.ipynb"}, "/r", VAULT))

    def run_cli(self, args, stdin):
        return subprocess.run(["python3", "-I", str(SCRIPTS / "soul_guard.py")] + args,
                              input=stdin, capture_output=True, text=True)

    def test_cli_fail_closed(self):
        ok = json.dumps({"tool_name": "Read", "tool_input": {}, "cwd": "/r"})
        for args, stdin in [([], ok), (["inexistente"], ok), (["testador"], "[1]"), (["testador"], "nao json"),
                            (["testador"], ""), (["testador"], json.dumps({"tool_name": "Bash", "tool_input": []}))]:
            r = self.run_cli(args, stdin)
            self.assertEqual(r.returncode, 2, (args, stdin))
            self.assertTrue(r.stderr.strip())

    def test_cli_escriba_in_place(self):
        root = soul_guard.vault_root()
        self.assertEqual(root, HERE.parents[2])
        nova = json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(root / "00 Inbox" / "zz-inexistente-xyz.md")}, "cwd": str(root)})
        self.assertEqual(self.run_cli(["escriba"], nova).returncode, 0)
        fora = json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(root / "20 Knowledge" / "zz.md")}, "cwd": str(root)})
        self.assertEqual(self.run_cli(["escriba"], fora).returncode, 2)


class RevisorSemBashTest(unittest.TestCase):
    def test_qualquer_bash_bloqueado(self):
        for c in ["git status", "npm audit --json", "ls", "echo oi", "date"]:
            msg = decide("revisor", "Bash", {"command": c}, "/r", VAULT)
            self.assertIsNotNone(msg, c)
            self.assertIn("não usa Bash", msg)

    def test_read_liberado(self):
        self.assertIsNone(decide("revisor", "Read", {"file_path": "/r/a.kt"}, "/r", VAULT))


if __name__ == "__main__":
    unittest.main()
