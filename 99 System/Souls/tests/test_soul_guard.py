import json
import os
import shlex
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
        for c in ["date +%F", "uuidgen", 'python3 -I -c "import uuid; print(uuid.uuid4())"', "git log -1"]:
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


class FinalReviewTest(unittest.TestCase):
    """Correções da revisão final do branch."""

    def bash(self, role, cmd):
        return decide(role, "Bash", {"command": cmd}, "/r", VAULT)

    def test_spec_nao_e_diretorio_de_teste(self):
        for p in ["api/spec/openapi.yaml", "specs/design.md", "testing/helpers.go"]:
            self.assertFalse(is_test_path(p), p)
        for p in ["spec/models/user_spec.rb", "web/src/a.spec.ts"]:
            self.assertTrue(is_test_path(p), p)
        self.assertIsNotNone(decide("testador", "Write", {"file_path": "api/spec/openapi.yaml"}, "/r", VAULT))

    def test_orquestrador_nao_escreve_em_claude_nem_nas_souls(self):
        for p in [".claude/agents/testador.md", "sub/.claude/agents/x.md", ".claude/settings.json",
                  "/home/u/.claude/agents/second-brain-souls/testador.md",
                  "/home/u/cfg/agents/second-brain-souls/desenvolvedor.md",
                  str(soul_guard.souls_dir() / "testador.md")]:
            self.assertIsNotNone(decide("orquestrador", "Write", {"file_path": p}, "/r", VAULT), p)
            self.assertIsNotNone(decide("orquestrador", "Edit", {"file_path": p}, "/r", VAULT), p)
        self.assertIsNone(decide("orquestrador", "Write", {"file_path": "docs/plano.md"}, "/r", VAULT))

    def test_orquestrador_nao_escreve_nas_souls_por_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / "atalho"
            link.symlink_to(soul_guard.souls_dir())
            msg = decide("orquestrador", "Write", {"file_path": str(link / "testador.md")}, tmp, VAULT)
            self.assertIsNotNone(msg)
            (Path(tmp) / ".claude" / "agents").mkdir(parents=True)
            (Path(tmp) / "docs").symlink_to(Path(tmp) / ".claude")
            msg = decide("orquestrador", "Write", {"file_path": "docs/agents/testador.md"}, tmp, VAULT)
            self.assertIsNotNone(msg)

    def test_orquestrador_editavel(self):
        self.assertTrue(soul_guard.orquestrador_editavel("docs/x.md"))
        self.assertTrue(soul_guard.orquestrador_editavel(".superpowers/sdd/x/ledger.txt"))
        for p in ["src/A.kt", ".claude/agents/x.md", ".claude/.superpowers/x", "a/second-brain-souls/x.md"]:
            self.assertFalse(soul_guard.orquestrador_editavel(p), p)

    def test_orquestrador_em_worktree_nativo(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(os.path.realpath(tmp))
            wt = repo / ".claude" / "worktrees" / "roadmap-x"
            (repo / ".claude" / "agents").mkdir(parents=True)
            wt.mkdir(parents=True)
            for rel in ["docs/superpowers/plans/p.md", ".superpowers/sdd/ledger.json", "ROADMAP.md"]:
                for tool in ("Write", "Edit"):
                    self.assertIsNone(decide("orquestrador", tool, {"file_path": str(wt / rel)}, str(wt), VAULT), rel)
                self.assertIsNone(decide("orquestrador", "Write", {"file_path": rel}, str(wt), VAULT), rel)
            for p in [str(wt / ".claude" / "agents" / "x.md"), ".claude/agents/x.md",
                      "../../agents/testador.md", str(repo / ".claude" / "agents" / "testador.md"),
                      str(wt / "src" / "A.kt")]:
                self.assertIsNotNone(decide("orquestrador", "Write", {"file_path": p}, str(wt), VAULT), p)
            link = wt / "atalho"
            link.symlink_to(soul_guard.souls_dir())
            self.assertIsNotNone(decide("orquestrador", "Write", {"file_path": str(link / "testador.md")}, str(wt), VAULT))
            (wt / "docs2").symlink_to(repo / ".claude")
            self.assertIsNotNone(decide("orquestrador", "Write", {"file_path": "docs2/agents/t.md"}, str(wt), VAULT))
        self.assertTrue(soul_guard.orquestrador_editavel("/r/.claude/worktrees/x/docs/p.md"))
        self.assertFalse(soul_guard.orquestrador_editavel("/r/.claude/agents/p.md"))
        self.assertFalse(soul_guard.orquestrador_editavel("/r/.claude/worktrees/x/.claude/agents/p.md"))

    def test_cwd_dentro_de_claude_nao_libera(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(os.path.realpath(tmp))
            for d in ("agents", "commands", "skills/x"):
                (repo / ".claude" / d).mkdir(parents=True)
            (repo / "atalho").symlink_to(repo / ".claude")
            casos = [(repo / ".claude" / "agents", "testador.md"), (repo / ".claude", "agents/evil.md"),
                     (repo / ".claude", "commands/evil.md"), (repo / ".claude", "CLAUDE.md"),
                     (repo / ".claude", "skills/x/SKILL.md"), (repo / "atalho", "agents/evil.md")]
            for cwd, rel in casos:
                for tool in ("Write", "Edit"):
                    self.assertIsNotNone(decide("orquestrador", tool, {"file_path": rel}, str(cwd), VAULT), (cwd, rel))
                    self.assertIsNotNone(decide("orquestrador", tool, {"file_path": str(cwd / rel)}, str(cwd), VAULT), (cwd, rel))

    def test_prefixo_de_worktree_varrido_segmento_a_segmento(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(os.path.realpath(tmp))
            (repo / ".claude" / "agents").mkdir(parents=True)
            (repo / ".claude" / "commands").mkdir(parents=True)
            (repo / "atalho").symlink_to(repo / ".claude")
            bad = [".claude/agents/.claude/worktrees/y/evil.md", ".claude/commands/.claude/worktrees/y/evil.md",
                   "atalho/agents/.claude/worktrees/y/evil.md", ".claude/worktrees/t.md",
                   ".claude/worktrees/.claude/agents/t.md", ".claude/worktrees/second-brain-souls/t.md",
                   ".CLAUDE/agents/x.md", ".claude/worktrees/y/.claude/agents/x.md",
                   ".claude/worktrees/y/Second-Brain-Souls/x.md"]
            for p in bad:
                full = str(repo / p)
                self.assertIsNotNone(decide("orquestrador", "Write", {"file_path": full}, str(repo), VAULT), p)
                self.assertIsNotNone(decide("orquestrador", "Edit", {"file_path": p}, str(repo), VAULT), p)
            self.assertIsNotNone(decide("testador", "Write", {"file_path": str(repo / ".claude/agents/.claude/worktrees/y/tests/x.md")}, str(repo), VAULT))
            self.assertIsNotNone(decide("testador", "Write", {"file_path": str(repo / ".claude/worktrees/.claude/tests/x.md")}, str(repo), VAULT))
            for p in [".claude/worktrees/y/docs/p.md", ".claude/worktrees/y/.superpowers/sdd/l.json",
                      ".claude/worktrees/y/.claude/worktrees/z/docs/p.md"]:
                self.assertIsNone(decide("orquestrador", "Write", {"file_path": str(repo / p)}, str(repo), VAULT), p)
            self.assertIsNone(decide("testador", "Write", {"file_path": str(repo / ".claude/worktrees/y/tests/x.py")}, str(repo), VAULT))
        self.assertFalse(soul_guard.orquestrador_editavel(".claude/agents/.claude/worktrees/y/a.md"))
        self.assertFalse(soul_guard.orquestrador_editavel(".claude/worktrees/y/src/A.kt"))
        self.assertFalse(soul_guard.orquestrador_editavel("/h/.superpowers/r/.claude/worktrees/y/src/A.kt"))
        self.assertTrue(soul_guard.orquestrador_editavel("/r/.claude/worktrees/y/.superpowers/l.json"))

    def test_lacunas_pequenas(self):
        with tempfile.TemporaryDirectory() as tmp:
            T = Path(os.path.realpath(tmp))
            proj = T / "x" / ".superpowers" / "proj"
            (proj / "src" / "main").mkdir(parents=True)
            sdd = T / "y" / ".superpowers" / "sdd" / "proj"
            (sdd / "src" / "main").mkdir(parents=True)
            # 1: ancestral .superpowers fora do cwd não libera
            self.assertIsNotNone(decide("orquestrador", "Write", {"file_path": str(proj / "src/A.kt")}, str(proj), VAULT))
            self.assertIsNotNone(decide("testador", "Write", {"file_path": str(sdd / "src/main/README.md")}, str(sdd), VAULT))
            # 4: symlinks que levam a produção
            repo = T / "repo"
            (repo / "src" / "main").mkdir(parents=True)
            (repo / "src" / "app").mkdir(parents=True)
            (repo / ".superpowers").symlink_to(repo / "src" / "main")
            self.assertIsNotNone(decide("orquestrador", "Write", {"file_path": str(repo / ".superpowers/A.kt")}, str(repo), VAULT))
            r2 = T / "r2"
            (r2 / "src" / "main").mkdir(parents=True)
            (r2 / ".superpowers").mkdir()
            (r2 / ".superpowers" / "sdd").symlink_to(r2 / "src" / "main")
            (r2 / "tests").symlink_to(r2 / "src" / "main")
            self.assertIsNotNone(decide("testador", "Write", {"file_path": str(r2 / ".superpowers/sdd/R.md")}, str(r2), VAULT))
            self.assertIsNotNone(decide("testador", "Write", {"file_path": str(r2 / "tests/A.kt")}, str(r2), VAULT))
            # 3: caixa
            low = str(soul_guard.souls_dir()).replace("Souls", "souls")
            self.assertIsNotNone(decide("orquestrador", "Write", {"file_path": low + "/x.md"}, str(T), VAULT))
            self.assertIsNotNone(decide("testador", "Write", {"file_path": low + "/tests/test_x.py"}, str(T), VAULT))
            # 5: CLAUDE_CONFIG_DIR sem .claude no nome
            cfg = T / "cfgdir"
            (cfg / "agents").mkdir(parents=True)
            old = os.environ.get("CLAUDE_CONFIG_DIR")
            os.environ["CLAUDE_CONFIG_DIR"] = str(cfg)
            try:
                for role in ("orquestrador", "testador"):
                    self.assertIsNotNone(decide(role, "Write", {"file_path": str(cfg / "agents/tests/x.md")}, str(cfg), VAULT), role)
                self.assertIsNotNone(decide("orquestrador", "Write", {"file_path": "CLAUDE.md"}, str(cfg), VAULT))
            finally:
                if old is None:
                    del os.environ["CLAUDE_CONFIG_DIR"]
                else:
                    os.environ["CLAUDE_CONFIG_DIR"] = old
        # 6
        msg = decide("testador", "Write", {"file_path": "src/A.kt"}, "/r", VAULT)
        self.assertIn(".superpowers/sdd/", msg)

    def test_testador_confinado(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(os.path.realpath(tmp))
            (repo / ".claude" / "agents" / "tests").mkdir(parents=True)
            (repo / "src" / "main").mkdir(parents=True)
            wt = repo / ".claude" / "worktrees" / "x"
            (wt / ".superpowers" / "sdd" / "P").mkdir(parents=True)
            (wt / "src" / "test").mkdir(parents=True)
            (repo / "lnk").symlink_to(repo / ".claude" / "agents")
            souls = soul_guard.souls_dir()
            ruins = [".claude/agents/.superpowers/sdd/x.md", ".claude/agents/tests/x.md", "src/main/.superpowers/A.md",
                     ".superpowers/x.md", ".superpowers/sdd/x.py", "lnk/tests/x.md",
                     str(souls / ".superpowers" / "sdd" / "evil.md"), str(souls / "tests" / "x.md")]
            for p in ruins:
                self.assertIsNotNone(decide("testador", "Write", {"file_path": str(repo / p) if not os.path.isabs(p) else p}, str(repo), VAULT), p)
            self.assertIsNotNone(decide("testador", "Write", {"file_path": str(souls / "tests" / "x.md")}, str(souls), VAULT))
            self.assertIsNotNone(decide("testador", "Write", {"file_path": "tests/x.md"}, str(repo / ".claude" / "agents"), VAULT))
            for p in [".superpowers/sdd/P/task-1-tester-report.md", "src/test/A.kt"]:
                self.assertIsNone(decide("testador", "Write", {"file_path": str(wt / p)}, str(wt), VAULT), p)
                self.assertIsNone(decide("testador", "Write", {"file_path": p}, str(wt), VAULT), p)
            self.assertIsNone(decide("testador", "Write", {"file_path": str(repo / ".superpowers/sdd/P/r.md")}, str(repo), VAULT))

    def test_testador_grava_relatorio_em_superpowers(self):
        cwd = "/r"
        for p in [".superpowers/sdd/PLAN/task-1-tester-report.md", "/r/.superpowers/sdd/x.md"]:
            self.assertIsNone(decide("testador", "Write", {"file_path": p}, cwd, VAULT), p)
        for p in [".superpowers/x.py", ".superpowers/x.md", "src/main/A.kt", "docs/relatorio.md", "/r/.claude/x.md"]:
            self.assertIsNotNone(decide("testador", "Write", {"file_path": p}, cwd, VAULT), p)

    def test_escriba_uuid_exige_isolado(self):
        self.assertIsNone(self.bash("escriba", 'python3 -I -c "import uuid; print(uuid.uuid4())"'))
        for c in ['python3 -c "import uuid; print(uuid.uuid4())"',
                  'python3 -I -c "import uuid; print(uuid.uuid4()); open(1)"',
                  'python3 -c -I "import uuid; print(uuid.uuid4())"']:
            self.assertIsNotNone(self.bash("escriba", c), c)

    def test_push_dentro_de_shell_c(self):
        for c in ["bash -c 'git push'", "sh -c 'git push origin x'", "zsh -c \"git -C . push\"",
                  "bash -lc 'git push'", "bash -o pipefail -c 'git push'",
                  "bash -c \"sh -c 'git push'\"", "eval git push", "eval 'git push'",
                  "/bin/sh -c 'cd x && git push'", "echo 'git push' | bash", "bash <<< 'git push'"]:
            for papel in ["desenvolvedor", "testador", "curador"]:
                self.assertIsNotNone(self.bash(papel, c), (papel, c))
        self.assertIsNone(self.bash("desenvolvedor", "bash -c 'git status'"))
        self.assertIsNone(self.bash("desenvolvedor", "bash scripts/build.sh"))
        self.assertIsNone(self.bash("desenvolvedor", "git commit -m 'evita push direto'"))

    def test_curador_destrutivo_dentro_de_shell_c(self):
        for c in ["sh -c 'rm -rf x'", "bash -c 'git reset --hard'", "bash -c \"zsh -c 'git clean -fd'\"",
                  "eval rm -rf x"]:
            self.assertIsNotNone(self.bash("curador", c), c)
        self.assertIsNone(self.bash("curador", "sh -c 'git status'"))

    def test_aninhamento_excessivo_bloqueia(self):
        c = "git status"
        for _ in range(10):
            c = "bash -c " + shlex.quote(c)
        self.assertIsNotNone(self.bash("desenvolvedor", c))


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
