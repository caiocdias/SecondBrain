#!/usr/bin/env python3
"""Hook PreToolUse das souls: aplica as travas de ferramenta por papel.

Uso: soul_guard.py <papel>   (JSON do hook no stdin)
Sai com 0 para liberar; com 2 e mensagem em stderr para bloquear.
"""
import fnmatch
import json
import os
import re
import shlex
import sys
from pathlib import Path

ROLES = {"orquestrador", "desenvolvedor", "testador", "revisor", "escriba", "curador"}
WRITE_TOOLS = {"Edit", "Write", "NotebookEdit"}

TEST_DIRS = {"test", "tests", "__tests__", "spec", "specs", "testing", "androidTest",
             "testFixtures", "integrationTest", "e2e"}
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
ESCRIBA_META = (">", ";", "&&", "||", "|", "`", "$(", "\n")
UUID_CODE = re.compile(r"^\s*import uuid\s*;\s*print\(uuid\.uuid4\(\)\)\s*$")

REVISOR_GIT = ("commit|push|reset|checkout|switch|merge|rebase|restore|clean|stash|tag|am|"
               "apply|cherry-pick")
GIT_PREFIX = r"\bgit\s+(?:(?:-C\s+\S+|-c\s+\S+|--\S+|-\S+)\s+)*"
REVISOR_PATTERNS = [
    (re.compile(r"(?:^|[;&|(]\s*)(?:rm|mv|tee)\b"), "rm, mv e tee"),
    (re.compile(r"\bsed\s+(?:\S+\s+)*?(?:-\w*i\w*|--in-place)\b"), "sed -i"),
    (re.compile(GIT_PREFIX + "(?:" + REVISOR_GIT + r")\b"), "git que altera o repositório"),
    (re.compile(r"\b(?:npm|pnpm|yarn)\s+(?:install|add|i)\b"), "instalação de pacotes"),
    (re.compile(r"\bpip3?\s+install\b"), "instalação de pacotes"),
    (re.compile(r"\b(?:brew|apt|apt-get|snap)\s+install\b"), "instalação de pacotes"),
    (re.compile(r"\b(?:go|cargo|gem)\s+install\b"), "instalação de pacotes"),
    (re.compile(r"\b(?:curl|wget)\b[^|]*\|\s*(?:sudo\s+)?(?:sh|bash)\b"), "curl/wget com pipe para shell"),
]
SAFE_REDIRECTS = re.compile(r"\d*>&\d+|&?\d*>>?\s*/dev/null")
PUSH = re.compile(GIT_PREFIX + r"push\b")
CURADOR_PATTERNS = [
    (re.compile(GIT_PREFIX + r"reset\s+(?:\S+\s+)*--hard\b"), "git reset --hard"),
    (re.compile(GIT_PREFIX + r"clean\s+(?:\S+\s+)*-\w*f"), "git clean -f"),
    (re.compile(r"\brm\s+(?:-\S+\s+)*(?:-\w*[rR]\w*f\w*|-\w*f\w*[rR]\w*|-[rR]\s+(?:-\S+\s+)*-f|-f\s+(?:-\S+\s+)*-[rR])\b"), "rm -rf"),
]


def is_test_path(path: str) -> bool:
    p = Path(path)
    if any(part in TEST_DIRS for part in p.parts[:-1]):
        return True
    return any(fnmatch.fnmatchcase(p.name, pat) for pat in TEST_FILE_PATTERNS)


def vault_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _resolve(path: str, cwd: str) -> str:
    return os.path.normpath(os.path.join(cwd or "", path))


def _tokens(command: str):
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def _decide_escriba_bash(command: str):
    toks = _tokens(command)
    if len(toks) == 3 and toks[0] == "python3" and toks[1] == "-c" and UUID_CODE.match(toks[2]):
        return None
    if any(m in command for m in ESCRIBA_META):
        return ("Trava do escriba: Bash sem redirecionamento, encadeamento, pipe ou substituição. "
                "Use apenas comandos simples e crie notas com a ferramenta Write em 00 Inbox/.")
    first = toks[0] if toks else ""
    if first in ESCRIBA_CMDS:
        return None
    if first == "git" and len(toks) > 1 and toks[1] in ESCRIBA_GIT:
        return None
    return ("Trava do escriba: Bash só permite date, uuidgen, ls, pwd, git de leitura "
            "(log, status, show, diff, rev-parse, branch) e a geração de uuid. "
            "Para escrever, use Write em 00 Inbox/.")


def _decide_bash(role: str, command: str):
    if role == "escriba":
        msg = _decide_escriba_bash(command)
        if msg:
            return msg
    if role != "orquestrador" and PUSH.search(command):
        return f"Trava do {role}: git push não é permitido. Deixe o push para o usuário."
    if role == "revisor":
        stripped = SAFE_REDIRECTS.sub(" ", command)
        if ">" in stripped:
            return ("Trava do revisor: o revisor não escreve arquivos (redirecionamento bloqueado). "
                    "Relate o achado no relatório.")
        for pat, nome in REVISOR_PATTERNS:
            if pat.search(command):
                return (f"Trava do revisor: {nome} é bloqueado. O revisor só lê e analisa; "
                        "relate o achado no relatório.")
    if role == "curador":
        for pat, nome in CURADOR_PATTERNS:
            if pat.search(command):
                return f"Trava do curador: {nome} é destrutivo e bloqueado. Peça confirmação ao usuário."
    return None


def decide(role, tool_name, tool_input, cwd, vault):
    tool_input = tool_input or {}
    if tool_name in WRITE_TOOLS:
        raw = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        path = _resolve(raw, cwd) if raw else ""
        if role == "testador" and not is_test_path(path):
            return ("Trava do testador: não altera código de produção. "
                    "Aponte o problema no relatório em vez de editar.")
        if role == "orquestrador":
            parts = Path(path).parts
            if not (path.endswith(".md") or ".superpowers" in parts):
                return ("Trava do orquestrador: só edita arquivos .md ou sob .superpowers/. "
                        "Delegue a mudança de código ao desenvolvedor.")
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


def main(argv):
    if len(argv) != 2 or argv[1] not in ROLES:
        print("uso: soul_guard.py <papel>", file=sys.stderr)
        return 0
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    role = argv[1]
    vault = vault_root() if role == "escriba" else Path(".")
    msg = decide(role, data.get("tool_name", ""), data.get("tool_input") or {},
                 data.get("cwd") or os.getcwd(), vault)
    if msg:
        print(msg, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
