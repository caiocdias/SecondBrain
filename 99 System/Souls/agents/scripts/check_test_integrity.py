#!/usr/bin/env python3
"""Verificação mecânica dos testes em commits atribuídos a souls.

Uso: check_test_integrity.py --base <rev> [--head <rev>] [--repo <dir>]
Saída: 0 limpo (avisos não contam), 1 com apontamentos, 2 erro de uso/git.
"""
import argparse
from collections import Counter
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from soul_guard import is_test_path  # noqa: E402

DECL = [r"@Test\b", r"^\s*def test_", r"^\s*(async\s+)?(it|test)\s*\(", r"^\s*func Test"]
ASSERT = [r"\bassert", r"\bexpect\s*\(", r"assertThat", r"\bverify\s*\(", r"\.should"]
SKIP = [r"@Disabled", r"@Ignore", r"pytest\.mark\.skip", r"@unittest\.skip",
        r"\b(it|test|describe)\.skip\s*\(", r"\bx(it|describe)\s*\(", r"t\.Skip\("]
DECL_RE = [re.compile(p) for p in DECL]
ASSERT_RE = [re.compile(p) for p in ASSERT]
SKIP_RE = [re.compile(p) for p in SKIP]


KNOWN_SOULS = {"testador", "desenvolvedor"}


class GitError(Exception):
    pass


def git(repo: str, *args: str) -> str:
    r = subprocess.run(["git", "-C", repo, "-c", "core.quotepath=false", *args],
                       capture_output=True, encoding="utf-8", errors="surrogateescape")
    if r.returncode != 0:
        raise GitError(r.stderr.strip() or f"git {' '.join(args)} falhou")
    return r.stdout


def commits(repo: str, base: str, head: str) -> list[tuple[str, list[str]]]:
    """(sha, valores do trailer Soul) em ordem cronológica, sem merges."""
    out = git(repo, "log", "--no-color", "--reverse", "--no-merges",
              "--format=%x01%H%x00%(trailers:key=Soul,valueonly)", f"{base}..{head}")
    result = []
    for rec in out.split("\x01"):
        if not rec.strip():
            continue
        sha, _, souls = rec.partition("\x00")
        values = [v.strip().lower() for v in souls.splitlines() if v.strip()]
        result.append((sha.strip(), values))
    return result


def count_merges(repo: str, base: str, head: str) -> int:
    out = git(repo, "log", "--no-color", "--merges", "--format=%H", f"{base}..{head}")
    return len(out.split())


def changed_files(repo: str, sha: str) -> list[str]:
    out = git(repo, "show", "--no-color", "--name-status", "--no-renames", "--format=", "-z", sha)
    parts = out.split("\0")
    files = []
    for i in range(0, len(parts) - 1, 2):
        files.append(parts[i + 1])
    return files


def diff_lines(repo: str, base: str, head: str):
    """Para arquivos de teste: linhas removidas e adicionadas [(arquivo, linha)].
    Um diff por arquivo (caminhos NUL-safe); só linhas após o primeiro @@ contam."""
    names = git(repo, "diff", "--no-color", "--no-ext-diff", "--no-textconv",
                "--no-renames", "--name-only", "-z", f"{base}..{head}")
    removed, added = [], []
    for path in names.split("\0"):
        if not path or not is_test_path(path):
            continue
        out = git(repo, "diff", "--no-color", "--no-ext-diff", "--no-textconv", "--text",
                  "--src-prefix=a/", "--dst-prefix=b/", "--no-renames", "-U0",
                  f"{base}..{head}", "--", path)
        in_hunk = False
        for line in out.splitlines():
            if line.startswith("@@"):
                in_hunk = True
            elif in_hunk and line[:1] == "-":
                removed.append((path, line[1:]))
            elif in_hunk and line[:1] == "+":
                added.append((path, line[1:]))
    return removed, added


def matches(regexes, text: str) -> bool:
    return any(r.search(text) for r in regexes)


def excess(removed, added, regexes):
    """Linhas removidas (casando regexes) além das que reaparecem adicionadas (multiconjunto)."""
    pool = Counter(t.strip() for _, t in added)
    result = []
    for path, text in removed:
        if not matches(regexes, text):
            continue
        key = text.strip()
        if pool[key] > 0:
            pool[key] -= 1
        else:
            result.append((path, key))
    return result


def check(repo: str, base: str, head: str) -> tuple[list[str], list[str]]:
    findings, warnings = [], []
    testador_tests: set[str] = set()
    merges = count_merges(repo, base, head)
    if merges:
        warnings.append(f"[MERGE_IGNORADO] - -: {merges} merge(s) no intervalo não foram analisados por commit")
    for sha, souls in commits(repo, base, head):
        short = sha[:7]
        files = changed_files(repo, sha)
        if any(f.rsplit("/", 1)[-1] == ".gitattributes" for f in files):
            warnings.append(f"[GITATTRIBUTES_ALTERADO] {short} .gitattributes: pode alterar como o git exibe diffs")
        if not souls:
            warnings.append(f"[SEM_SOUL] {short} -: commit sem trailer Soul:")
        if len(souls) > 1 or any(s not in KNOWN_SOULS for s in souls):
            warnings.append(f"[SOUL_DESCONHECIDA] {short} -: trailer(s) Soul: {', '.join(souls)}")
        if "testador" in souls:
            for f in files:
                if is_test_path(f):
                    testador_tests.add(f)
                else:
                    findings.append(f"[TESTADOR_PRODUCAO] {short} {f}: testador alterou arquivo que não é de teste")
        if "desenvolvedor" in souls:
            for f in files:
                if f in testador_tests:
                    findings.append(f"[DEV_TESTE_DO_TESTADOR] {short} {f}: desenvolvedor alterou teste do testador")
    short_head = git(repo, "rev-parse", "--short", head).strip()
    where = f"(diff do intervalo até {short_head})"
    removed, added = diff_lines(repo, base, head)
    for path, text in excess(removed, added, DECL_RE):
        findings.append(f"[TESTE_REMOVIDO] {short_head} {path}: {text} {where}")
    for path, text in excess(removed, added, ASSERT_RE):
        findings.append(f"[ASSERCAO_REMOVIDA] {short_head} {path}: {text} {where}")
    removed_skips = Counter(t.strip() for _, t in removed if matches(SKIP_RE, t))
    for path, text in added:
        if not matches(SKIP_RE, text):
            continue
        key = text.strip()
        if removed_skips[key] > 0:
            removed_skips[key] -= 1
            continue
        findings.append(f"[SKIP_ADICIONADO] {short_head} {path}: {key} {where}")
    return findings, warnings


def main(argv=None) -> int:
    sys.stdout.reconfigure(errors="backslashreplace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--repo", default=".")
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    try:
        findings, warnings = check(args.repo, args.base, args.head)
    except (GitError, OSError) as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # nunca confundir falha interna com apontamento
        print(f"ERRO inesperado: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    for line in warnings + findings:
        print(line)
    if findings:
        print(f"{len(findings)} apontamento(s)")
        return 1
    print("OK: nenhum apontamento")
    return 0


if __name__ == "__main__":
    sys.exit(main())
