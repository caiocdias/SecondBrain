#!/usr/bin/env python3
"""Hook PreToolUse das souls: aplica as travas de ferramenta por papel.

Uso: soul_guard.py <papel>   (JSON do hook no stdin)
Sai com 0 para liberar; com 2 e mensagem em stderr para bloquear.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import shlex
import sys
from pathlib import Path

ROLES = {"orquestrador", "desenvolvedor", "testador", "revisor", "escriba", "curador"}
WRITE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}

# `spec`, `specs` e `testing` não são diretórios de teste (api/spec/openapi.yaml é produção);
# specs de RSpec contam pelo nome (*_spec.rb).
TEST_DIRS = {"test", "tests", "__tests__", "androidTest", "testFixtures", "integrationTest", "e2e"}
TEST_FILE_PATTERNS = [
    "test_*.py", "*_test.py", "conftest.py", "*_test.go",
    *[f"*.test.{e}" for e in ("js", "jsx", "ts", "tsx", "mjs", "cjs")],
    *[f"*.spec.{e}" for e in ("js", "jsx", "ts", "tsx", "mjs", "cjs")],
    *[f"*Test.{e}" for e in ("kt", "java", "scala", "groovy")],
    *[f"*Tests.{e}" for e in ("kt", "java", "cs")],
    "*IT.kt", "*IT.java", "*_spec.rb",
]

ESCRIBA_CMDS = {"date", "uuidgen", "ls", "pwd"}
ESCRIBA_GIT = {"log", "status", "show", "diff", "rev-parse", "branch"}
ESCRIBA_BRANCH_FLAGS = {"--list", "-a", "-r", "--show-current", "-v", "-vv"}
ESCRIBA_META = (">", "<", "&", ";", "|", "`", "$(", "(", ")", "\n", "\r")
UUID_CODE = re.compile(r"^\s*import uuid\s*;\s*print\(uuid\.uuid4\(\)\)\s*$")

# Interpretadores cujo `-c <texto>` (ou stdin) também é inspecionado pelas travas de Bash.
SHELLS = {"bash", "sh", "zsh", "dash", "ksh", "fish"}
MAX_NESTING = 5

SHORT_RECURSIVE = re.compile(r"^-[A-Za-z]*[rR][A-Za-z]*$")
SHORT_FORCE = re.compile(r"^-[A-Za-z]*f[A-Za-z]*$")


def is_test_path(path: str, cwd: str | None = None) -> bool:
    """Caminho de teste. Se `cwd` for dado e o caminho estiver dentro dele,
    só os segmentos relativos a `cwd` contam (evita /home/x/tests/proj)."""
    p = path
    if cwd and os.path.isabs(path) and os.path.isabs(cwd):
        rel = os.path.relpath(path, cwd)
        if not rel.startswith(".."):
            p = rel
    p = Path(p)
    if any(part in TEST_DIRS for part in p.parts[:-1]):
        return True
    return any(fnmatch.fnmatchcase(p.name, pat) for pat in TEST_FILE_PATTERNS)


def vault_root() -> Path:
    return Path(__file__).resolve().parents[4]


def souls_dir() -> Path:
    """`99 System/Souls/agents/`, já resolvido (o link second-brain-souls aponta para cá)."""
    return Path(__file__).resolve().parents[1]


def _parts_from_cwd(path: str, cwd: str | None) -> tuple[str, ...]:
    """Segmentos do caminho relativos a `cwd` quando está dentro dele (worktree nativo em
    `<repo>/.claude/worktrees/<nome>/` é o cwd legítimo); fora dele, os segmentos absolutos."""
    if cwd and os.path.isabs(path) and os.path.isabs(cwd):
        rel = os.path.relpath(path, cwd)
        if rel != ".." and not rel.startswith(".." + os.sep):
            return Path(rel).parts
    return Path(path).parts


def testador_editavel(path: str, cwd: str | None = None) -> bool:
    """Além de testes, o testador grava relatórios `.md` sob `.superpowers/`."""
    return is_test_path(path, cwd) or (
        ".superpowers" in _parts_from_cwd(path, cwd) and path.endswith(".md"))


def orquestrador_editavel(path: str, cwd: str | None = None) -> bool:
    """O orquestrador só edita `.md` e arquivos sob `.superpowers/`, nunca sob `.claude/`
    (agentes, settings e hooks do projeto) nem nas souls (`second-brain-souls/`).
    Com `cwd`, os segmentos contam relativos a ele quando o caminho está dentro."""
    parts = _parts_from_cwd(path, cwd)
    if ".claude" in parts or "second-brain-souls" in parts:
        return False
    return path.endswith(".md") or ".superpowers" in parts


def _resolve(path: str, cwd: str) -> str:
    return os.path.normpath(os.path.join(cwd or "", path))


def _tokens(command: str) -> list[str]:
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def _segments(command: str) -> list[list[str]]:
    """Tokeniza separando operadores de shell (; & | < > ( ) e quebras de linha)."""
    text = command.replace("\n", " ; ")
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        toks = list(lex)
    except ValueError:
        toks = text.split()
    segs, cur = [], []
    for t in toks:
        if t and all(c in "();&|<>" for c in t):
            if cur:
                segs.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        segs.append(cur)
    return segs


def _base(tok: str) -> str:
    return os.path.basename(tok)


def _git_calls(segs):
    """Devolve (subcomando, argumentos) para cada `git` encontrado."""
    for seg in segs:
        for i, t in enumerate(seg):
            if _base(t) != "git":
                continue
            j = i + 1
            while j < len(seg) and seg[j].startswith("-"):
                j += 2 if seg[j] in ("-C", "-c") else 1
            if j < len(seg):
                yield seg[j], seg[j + 1:]


class NestingError(Exception):
    pass


def _shell_payload(seg, i):
    """Para `sh [opções] -c <texto>` começando em seg[i], devolve <texto>.
    Devolve "" se o shell lê comandos do stdin e None se roda um script."""
    j, has_c = i + 1, False
    while j < len(seg):
        t = seg[j]
        if t in ("-o", "+o", "-O", "+O"):
            j += 2
        elif t.startswith("--"):
            j += 1
        elif len(t) > 1 and t[0] in "-+":
            has_c = has_c or "c" in t[1:]
            j += 1
        else:
            return t if has_c else None
    return ""


def _all_segments(command: str, depth: int = 0) -> list[list[str]]:
    """Segmentos do comando mais os de `sh -c <texto>` e `eval ...`, recursivamente.
    Shell lendo do stdin (pipe, here-string): todo token com espaço vira comando também."""
    if depth > MAX_NESTING:
        raise NestingError
    segs = _segments(command)
    out = list(segs)
    stdin_shell = False
    for seg in segs:
        for i, t in enumerate(seg):
            inner = None
            if _base(t) in SHELLS:
                inner = _shell_payload(seg, i)
                if inner == "":
                    stdin_shell, inner = True, None
            elif _base(t) == "eval" and i + 1 < len(seg):
                inner = " ".join(seg[i + 1:])
            if inner:
                out.extend(_all_segments(inner, depth + 1))
    if stdin_shell:
        for seg in segs:
            for t in seg:
                if any(c.isspace() for c in t):
                    out.extend(_all_segments(t, depth + 1))
    return out


def _decide_escriba_bash(command: str):
    toks = _tokens(command)
    if toks[:3] == ["python3", "-I", "-c"] and len(toks) == 4 and UUID_CODE.match(toks[3]):
        return None
    if any(m in command for m in ESCRIBA_META):
        return ("Trava do escriba: Bash sem redirecionamento, encadeamento, pipe, subshell ou substituição. "
                "Use apenas comandos simples e crie notas com a ferramenta Write em 00 Inbox/.")
    first = toks[0] if toks else ""
    if any(t.startswith("--output") for t in toks):
        return "Trava do escriba: --output grava arquivos e é bloqueado. Use Write em 00 Inbox/."
    if first in ESCRIBA_CMDS:
        return None
    if first == "git" and len(toks) > 1 and toks[1] in ESCRIBA_GIT:
        if toks[1] == "branch" and not set(toks[2:]) <= ESCRIBA_BRANCH_FLAGS:
            return ("Trava do escriba: git branch só lista (sem argumentos, --list, -a, -r, "
                    "--show-current, -v, -vv); não altera branches.")
        return None
    return ("Trava do escriba: Bash só permite date, uuidgen, ls, pwd, git de leitura "
            "(log, status, show, diff, rev-parse, branch) e a geração de uuid. "
            "Para escrever, use Write em 00 Inbox/.")


def _curador_block(segs):
    for sub, args in _git_calls(segs):
        if sub == "reset" and "--hard" in args:
            return "git reset --hard"
        if sub == "clean" and any(a == "--force" or SHORT_FORCE.match(a) for a in args):
            return "git clean -f"
    for seg in segs:
        for i, t in enumerate(seg):
            if _base(t) == "rm":
                flags = seg[i + 1:]
                rec = any(a == "--recursive" or SHORT_RECURSIVE.match(a) for a in flags)
                frc = any(a == "--force" or SHORT_FORCE.match(a) for a in flags)
                if rec and frc:
                    return "rm -rf"
    return None


def _decide_bash(role: str, command: str):
    if role == "escriba":
        msg = _decide_escriba_bash(command)
        if msg:
            return msg
    try:
        segs = _all_segments(command)
    except NestingError:
        return f"Trava do {role}: comando com shells aninhados demais; bloqueado por segurança."
    if role != "orquestrador" and any(sub == "push" for sub, _ in _git_calls(segs)):
        return f"Trava do {role}: git push não é permitido. Deixe o push para o usuário."
    if role == "revisor":
        return ("Trava do revisor: a revisora não usa Bash. Peça ao orquestrador a saída de "
                "scanners, testes ou git no pacote de revisão.")
    if role == "curador":
        what = _curador_block(segs)
        if what:
            return f"Trava do curador: {what} é destrutivo e bloqueado. Peça confirmação ao usuário."
    return None


def decide(role: str, tool_name: str, tool_input: dict, cwd: str, vault: Path) -> str | None:
    tool_input = tool_input or {}
    if tool_name in WRITE_TOOLS:
        raw = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        path = _resolve(raw, cwd) if raw else ""
        if role == "testador" and not testador_editavel(path, cwd):
            return ("Trava do testador: só altera testes e relatórios .md sob .superpowers/; "
                    "não altera código de produção. Aponte o problema no relatório em vez de editar.")
        if role == "orquestrador":
            real = Path(os.path.realpath(path))
            souls = souls_dir()
            if real == souls or souls in real.parents:
                return "Trava do orquestrador: não altera as souls."
            real_parts = _parts_from_cwd(str(real), os.path.realpath(cwd) if cwd else None)
            if not orquestrador_editavel(path, cwd) or {".claude", "second-brain-souls"} & set(real_parts):
                return ("Trava do orquestrador: só edita arquivos .md ou sob .superpowers/, "
                        "nunca sob .claude/ nem nas souls. Delegue a mudança de código ao desenvolvedor.")
        if role == "escriba":
            if tool_name != "Write":
                return ("Trava do escriba: só cria notas novas com Write em 00 Inbox/; "
                        "não edita arquivos existentes.")
            inbox = Path(os.path.realpath(vault)) / "00 Inbox"
            real = Path(os.path.realpath(path))
            if inbox not in real.parents:
                return "Trava do escriba: só pode criar arquivos dentro de 00 Inbox/."
            if os.path.exists(path):
                return "Trava do escriba: o arquivo já existe; crie uma nova captura com outro nome."
    elif tool_name == "Bash":
        return _decide_bash(role, tool_input.get("command") or "")
    return None


def _main(argv):
    if len(argv) != 2 or argv[1] not in ROLES:
        print("Trava das souls: papel ausente ou inválido; bloqueado por segurança. "
              "Papéis: " + ", ".join(sorted(ROLES)), file=sys.stderr)
        return 2
    data = json.load(sys.stdin)
    if not isinstance(data, dict) or not isinstance(data.get("tool_input", {}), dict):
        print("Trava das souls: payload do hook inválido; bloqueado por segurança.", file=sys.stderr)
        return 2
    role = argv[1]
    vault = vault_root() if role == "escriba" else Path(".")
    msg = decide(role, str(data.get("tool_name", "")), data.get("tool_input") or {},
                 data.get("cwd") or os.getcwd(), vault)
    if msg:
        print(msg, file=sys.stderr)
        return 2
    return 0


def main(argv):
    try:
        return _main(argv)
    except Exception as exc:  # falha fechada: qualquer erro bloqueia
        print(f"Trava das souls: erro interno ({type(exc).__name__}); bloqueado por segurança.",
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
