#!/usr/bin/env python3
"""Verificação mecânica dos testes em commits atribuídos a souls.

Uso: check_test_integrity.py --base <rev> [--head <rev>] [--repo <dir>]
Saída: 0 limpo (avisos não contam), 1 com apontamentos, 2 erro de uso/git.
"""
import argparse
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


class GitError(Exception):
    pass


def git(repo: str, *args: str) -> str:
    r = subprocess.run(["git", "-C", repo, "-c", "core.quotepath=false", *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise GitError(r.stderr.strip() or f"git {' '.join(args)} falhou")
    return r.stdout


def commits(repo: str, base: str, head: str) -> list[tuple[str, str]]:
    """(sha, valor do trailer Soul) em ordem cronológica."""
    out = git(repo, "log", "--reverse", "--no-merges",
              "--format=%x01%H%x00%(trailers:key=Soul,valueonly)", f"{base}..{head}")
    result = []
    for rec in out.split("\x01"):
        if not rec.strip():
            continue
        sha, _, soul = rec.partition("\x00")
        result.append((sha.strip(), soul.strip().lower()))
    return result


def changed_files(repo: str, sha: str) -> list[str]:
    out = git(repo, "show", "--name-status", "--no-renames", "--format=", sha)
    files = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            files.append(parts[-1])
    return files


def diff_lines(repo: str, base: str, head: str):
    """Para arquivos de teste: [(arquivo, linha removida)] e [(arquivo, linha adicionada)]."""
    out = git(repo, "diff", "--no-renames", "-U0", f"{base}..{head}")
    removed, added = [], []
    old = new = None
    for line in out.splitlines():
        if line.startswith("--- "):
            old = None if line[4:] == "/dev/null" else line[6:]
        elif line.startswith("+++ "):
            new = None if line[4:] == "/dev/null" else line[6:]
        elif line.startswith("diff --git"):
            old = new = None
        elif line.startswith("-") or line.startswith("+"):
            path = new if line[0] == "+" else old
            if path is None or not is_test_path(path):
                continue
            (added if line[0] == "+" else removed).append((path, line[1:]))
    return removed, added


def matches(regexes, text: str) -> bool:
    return any(r.search(text) for r in regexes)


def check(repo: str, base: str, head: str) -> tuple[list[str], list[str]]:
    findings, warnings = [], []
    testador_tests: set[str] = set()
    for sha, soul in commits(repo, base, head):
        short = sha[:7]
        files = changed_files(repo, sha)
        if not soul:
            warnings.append(f"[SEM_SOUL] {short} -: commit sem trailer Soul:")
        elif soul == "testador":
            for f in files:
                if is_test_path(f):
                    testador_tests.add(f)
                else:
                    findings.append(f"[TESTADOR_PRODUCAO] {short} {f}: testador alterou arquivo que não é de teste")
        elif soul == "desenvolvedor":
            for f in files:
                if f in testador_tests:
                    findings.append(f"[DEV_TESTE_DO_TESTADOR] {short} {f}: desenvolvedor alterou teste do testador")
    short_head = git(repo, "rev-parse", "--short", head).strip()
    removed, added = diff_lines(repo, base, head)
    added_stripped = {t.strip() for _, t in added}
    for path, text in removed:
        if text.strip() in added_stripped:
            continue
        if matches(DECL_RE, text):
            findings.append(f"[TESTE_REMOVIDO] {short_head} {path}: {text.strip()}")
        if matches(ASSERT_RE, text):
            findings.append(f"[ASSERCAO_REMOVIDA] {short_head} {path}: {text.strip()}")
    for path, text in added:
        if matches(SKIP_RE, text):
            findings.append(f"[SKIP_ADICIONADO] {short_head} {path}: {text.strip()}")
    return findings, warnings


def main(argv=None) -> int:
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
    for line in warnings + findings:
        print(line)
    if findings:
        print(f"{len(findings)} apontamento(s)")
        return 1
    print("OK: nenhum apontamento")
    return 0


if __name__ == "__main__":
    sys.exit(main())
