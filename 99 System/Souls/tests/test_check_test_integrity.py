import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "agents" / "scripts" / "check_test_integrity.py"


class Repo:
    def __init__(self, root: str):
        self.root = Path(root)
        self.git("init", "-q")
        self.git("config", "user.name", "T")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "commit.gpgsign", "false")

    def git(self, *args: str) -> str:
        r = subprocess.run(["git", "-C", str(self.root), *args],
                           capture_output=True, text=True, check=True)
        return r.stdout.strip()

    def write(self, path: str, content: str) -> None:
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    def commit(self, msg: str, soul: str | None = None) -> None:
        self.git("add", "-A")
        full = msg if soul is None else f"{msg}\n\nSoul: {soul}"
        self.git("commit", "-q", "-m", full)

    def check(self, base: str, *extra: str, env: dict | None = None):
        r = subprocess.run(
            [sys.executable, "-I", str(SCRIPT), "--base", base, "--repo", str(self.root), *extra],
            capture_output=True, text=True, errors="replace",
            env={**os.environ, **(env or {})})
        return r.returncode, r.stdout


class CheckTestIntegrityTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Repo(self._tmp.name)
        self.repo.write("README.md", "x\n")
        self.repo.commit("init")
        self.base = self.repo.git("rev-parse", "HEAD")

    def dev_baseline(self):
        r = self.repo
        r.write("src/main/a.py", "def a():\n    return 1\n")
        r.write("tests/test_a.py", "def test_x(): assert a()\n")
        r.commit("dev", "desenvolvedor")

    def test_limpo(self):
        self.dev_baseline()
        r = self.repo
        r.write("tests/test_a.py", "def test_x(): assert a()\ndef test_y(): assert b()\n")
        r.commit("tester", "testador")
        code, out = r.check(self.base)
        self.assertEqual(code, 0, out)
        self.assertIn("OK: nenhum apontamento", out)

    def test_testador_producao(self):
        self.dev_baseline()
        self.repo.write("src/main/a.py", "def a():\n    return 2\n")
        self.repo.commit("tester", "testador")
        code, out = self.repo.check(self.base)
        self.assertEqual(code, 1)
        self.assertIn("[TESTADOR_PRODUCAO]", out)
        self.assertIn("src/main/a.py", out)

    def test_dev_altera_teste_do_testador(self):
        r = self.repo
        r.write("tests/test_b.py", "def test_b(): assert 1\n")
        r.commit("tester", "testador")
        r.write("tests/test_b.py", "def test_b(): assert 1\n# edit\n")
        r.commit("dev", "desenvolvedor")
        code, out = r.check(self.base)
        self.assertEqual(code, 1)
        self.assertIn("[DEV_TESTE_DO_TESTADOR]", out)

    def with_two_tests(self):
        self.dev_baseline()
        self.repo.write("tests/test_a.py", "def test_x(): assert a()\ndef test_y(): assert b()\n")
        self.repo.commit("tester", "testador")
        return self.repo.git("rev-parse", "HEAD")

    def test_teste_removido(self):
        mid = self.with_two_tests()
        self.repo.write("tests/test_a.py", "def test_x(): assert a()\n")
        self.repo.commit("dev", "desenvolvedor")
        code, out = self.repo.check(mid)
        self.assertEqual(code, 1)
        self.assertIn("[TESTE_REMOVIDO]", out)

    def test_assercao_removida(self):
        mid = self.with_two_tests()
        self.repo.write("tests/test_a.py", "def test_x(): assert a()\ndef test_y(): pass\n")
        self.repo.commit("dev", "desenvolvedor")
        code, out = self.repo.check(mid)
        self.assertEqual(code, 1)
        self.assertIn("[ASSERCAO_REMOVIDA]", out)

    def test_rename_nao_acusa(self):
        self.dev_baseline()
        mid = self.repo.git("rev-parse", "HEAD")
        self.repo.git("mv", "tests/test_a.py", "tests/test_a2.py")
        self.repo.commit("rename", "desenvolvedor")
        code, out = self.repo.check(mid)
        self.assertNotIn("TESTE_REMOVIDO", out)
        self.assertNotIn("ASSERCAO_REMOVIDA", out)
        self.assertEqual(code, 0, out)

    def test_skip_adicionado(self):
        mid = self.with_two_tests()
        self.repo.write("tests/test_a.py",
                        "@pytest.mark.skip\ndef test_x(): assert a()\ndef test_y(): assert b()\n")
        self.repo.commit("dev", "desenvolvedor")
        code, out = self.repo.check(mid)
        self.assertEqual(code, 1)
        self.assertIn("[SKIP_ADICIONADO]", out)

    def test_sem_soul_e_aviso(self):
        self.repo.write("src/main/c.py", "x = 1\n")
        self.repo.commit("sem trailer")
        code, out = self.repo.check(self.base)
        self.assertEqual(code, 0, out)
        self.assertIn("[SEM_SOUL]", out)

    def test_erro_de_git(self):
        code, _ = self.repo.check("nao-existe-rev")
        self.assertEqual(code, 2)

    # --- fix round 1 ---
    def test_git_config_hostil(self):
        mid = self.with_two_tests()
        self.repo.write("tests/test_a.py", "def test_x(): assert a()\n")
        self.repo.commit("dev", "desenvolvedor")
        for key, val in [("color.ui", "always"), ("diff.noprefix", "true"),
                         ("diff.external", "true")]:
            env = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": key, "GIT_CONFIG_VALUE_0": val}
            code, out = self.repo.check(mid, env=env)
            self.assertEqual(code, 1, (key, out))
            self.assertIn("[TESTE_REMOVIDO]", out, key)
            self.assertIn("tests/test_a.py", out, key)

    def test_caminho_com_espaco(self):
        r = self.repo
        r.write("my tests/test_a.py", "def test_x(): assert a()\ndef test_y(): assert b()\n")
        r.commit("dev", "desenvolvedor")
        mid = r.git("rev-parse", "HEAD")
        r.write("my tests/test_a.py", "def test_x(): assert a()\n")
        r.commit("dev2", "desenvolvedor")
        code, out = r.check(mid)
        self.assertEqual(code, 1, out)
        self.assertIn("my tests/test_a.py", out)

    def test_linha_removida_comecando_com_traco(self):
        r = self.repo
        r.write("tests/a.test.lua", "-- setup\nit(\"a\", function() assert.equal(1, x) end)\n")
        r.commit("dev", "desenvolvedor")
        mid = r.git("rev-parse", "HEAD")
        r.write("tests/a.test.lua", "")
        r.commit("dev2", "desenvolvedor")
        code, out = r.check(mid)
        self.assertEqual(code, 1, out)
        self.assertIn("[TESTE_REMOVIDO]", out)
        self.assertIn("[ASSERCAO_REMOVIDA]", out)

    def test_soul_multipla_e_desconhecida(self):
        r = self.repo
        r.write("src/main/a.py", "x = 1\n")
        r.git("add", "-A")
        r.git("commit", "-q", "-m", "m\n\nSoul: testador\nSoul: outro")
        code, out = r.check(self.base)
        self.assertEqual(code, 1, out)
        self.assertIn("[TESTADOR_PRODUCAO]", out)
        self.assertIn("[SOUL_DESCONHECIDA]", out)
        r.write("src/main/b.py", "x = 1\n")
        r.commit("m2", "revisor")
        code, out = r.check(r.git("rev-parse", "HEAD~1"))
        self.assertEqual(code, 0, out)
        self.assertIn("[SOUL_DESCONHECIDA]", out)

    def test_souls_conhecidas_sem_regra(self):
        r = self.repo
        for soul in ("orquestrador-etapa", "revisor-seguranca", "brain-escriba", "brain-curador"):
            with self.subTest(soul=soul):
                mid = r.git("rev-parse", "HEAD")
                r.write(f"docs/{soul}.md", "x\n")
                r.commit("doc", soul)
                code, out = r.check(mid)
                self.assertEqual(code, 0, out)
                self.assertNotIn("[SOUL_DESCONHECIDA]", out)

    def test_bytes_nao_utf8(self):
        r = self.repo
        (r.root / "tests").mkdir()
        (r.root / "tests" / "test_a.py").write_bytes(b"def test_x(): assert a()\n# \xe9\xff\n")
        r.commit("dev", "desenvolvedor")
        mid = r.git("rev-parse", "HEAD")
        (r.root / "tests" / "test_a.py").write_bytes(b"# \xe9\xff\n")
        r.commit("dev2", "desenvolvedor")
        code, out = r.check(mid)
        self.assertEqual(code, 1, out)
        self.assertIn("[TESTE_REMOVIDO]", out)

    def test_multiconjunto(self):
        r = self.repo
        r.write("tests/test_a.py", "def test_x(): assert a()\ndef test_x(): assert a()\n")
        r.commit("dev", "desenvolvedor")
        mid = r.git("rev-parse", "HEAD")
        r.write("tests/test_a.py", "")
        r.write("tests/test_c.py", "def test_x(): assert a()\n")
        r.commit("dev2", "desenvolvedor")
        code, out = r.check(mid)
        self.assertEqual(code, 1, out)
        self.assertIn("[TESTE_REMOVIDO]", out)

    def test_skip_movido_nao_acusa(self):
        r = self.repo
        r.write("tests/test_a.py", "@pytest.mark.skip\ndef test_x(): assert a()\n")
        r.commit("dev", "desenvolvedor")
        mid = r.git("rev-parse", "HEAD")
        r.git("mv", "tests/test_a.py", "tests/test_b.py")
        r.commit("mv", "desenvolvedor")
        code, out = r.check(mid)
        self.assertNotIn("SKIP_ADICIONADO", out)

    def test_merge_ignorado(self):
        r = self.repo
        r.git("checkout", "-q", "-b", "side")
        r.write("side.txt", "s\n")
        r.commit("side", "desenvolvedor")
        r.git("checkout", "-q", "-")
        r.write("main.txt", "m\n")
        r.commit("main", "desenvolvedor")
        r.git("merge", "-q", "--no-ff", "-m", "merge", "side")
        code, out = r.check(self.base)
        self.assertEqual(code, 0, out)
        self.assertIn("[MERGE_IGNORADO]", out)

    def test_dev_apaga_teste_do_testador(self):
        r = self.repo
        r.write("tests/test_b.py", "def test_b(): assert 1\n")
        r.commit("tester", "testador")
        r.git("rm", "-q", "tests/test_b.py")
        r.commit("dev", "desenvolvedor")
        code, out = r.check(self.base)
        self.assertEqual(code, 1)
        self.assertIn("[DEV_TESTE_DO_TESTADOR]", out)

    def test_uso_sem_base(self):
        r = subprocess.run([sys.executable, "-I", str(SCRIPT), "--repo", str(self.repo.root)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

    def test_head_respeitado(self):
        self.dev_baseline()
        head_ok = self.repo.git("rev-parse", "HEAD")
        self.repo.write("src/main/a.py", "y = 2\n")
        self.repo.commit("tester", "testador")
        code, out = self.repo.check(self.base, "--head", head_ok)
        self.assertEqual(code, 0, out)
        code, out = self.repo.check(self.base)
        self.assertEqual(code, 1, out)

    def test_gitattributes_nao_cega(self):
        mid = self.with_two_tests()
        self.repo.write(".gitattributes", "* -diff\n")
        self.repo.write("tests/test_a.py", "def test_x(): assert a()\n")
        self.repo.commit("dev", "desenvolvedor")
        code, out = self.repo.check(mid)
        self.assertEqual(code, 1, out)
        self.assertIn("[TESTE_REMOVIDO]", out)
        self.assertIn("[GITATTRIBUTES_ALTERADO]", out)


if __name__ == "__main__":
    unittest.main()
