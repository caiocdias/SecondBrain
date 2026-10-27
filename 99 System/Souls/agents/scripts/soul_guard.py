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
ESCRIBA_BRANCH_FLAGS = {"--list", "-a", "-r", "--show-current", "-v", "-vv"}
ESCRIBA_META = (">", "<", "&", ";", "|", "`", "$(", "(", ")", "\n", "\r")
UUID_CODE = re.compile(r"^\s*import uuid\s*;\s*print\(uuid\.uuid4\(\)\)\s*$")

REVISOR_TOOLS = {"cat", "head", "tail", "less", "grep", "rg", "ls", "find", "wc", "sort", "uniq", "cut",
                 "tr", "diff", "file", "stat", "tree", "pwd", "date", "echo", "printf", "sha256sum",
                 "md5sum", "jq", "which", "basename", "dirname", "realpath", "true"}
REVISOR_GIT_OK = {"log", "show", "diff", "status", "rev-parse", "blame", "ls-files", "ls-tree", "grep",
                  "merge-base", "describe", "shortlog", "cat-file", "branch"}
FIND_BAD = {"-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprintf", "-fls"}
GRADLE_TASKS = {"dependencies", "buildEnvironment", "dependencyCheckAnalyze"}
MVN_GOALS = {"dependency:tree", "org.owasp:dependency-check-maven:check"}
REVISOR_FAMILIES = ("leitura (cat, grep, rg, ls, find, jq...), git de leitura (log, show, diff, status...), "
                    "auditoria de dependências (osv-scanner, pip-audit, npm audit, dependency-check, "
                    "gradle dependencies, mvn dependency:tree), curl/wget só para stdout e "
                    "check_test_integrity.py")
SAFE_REDIRECTS = re.compile(r"\d*>&\d+|&?\d*>>?\s*/dev/null")
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


def _first_arg(seg, i):
    for t in seg[i + 1:]:
        if not t.startswith("-"):
            return t
    return None


def _decide_escriba_bash(command: str):
    toks = _tokens(command)
    if len(toks) == 3 and toks[0] == "python3" and toks[1] == "-c" and UUID_CODE.match(toks[2]):
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


def _revisor_segments(command: str):
    """Segmentos separados por | || && ; & e newline. None se houver subshell/parênteses.
    `<` e o alvo seguinte são descartados (leitura). Redirecionamentos seguros já removidos."""
    text = SAFE_REDIRECTS.sub(" ", command).replace("\n", " ; ")
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        toks = list(lex)
    except ValueError:
        return None
    segs, cur, skip = [], [], False
    for t in toks:
        if skip:
            skip = False
            continue
        if t and all(c in "()" for c in t):
            return None
        if t and all(c in ";&|" for c in t):
            if cur:
                segs.append(cur)
            cur = []
        elif t and all(c == "<" for c in t):
            skip = True
        else:
            cur.append(t)
    if cur:
        segs.append(cur)
    return segs


def _revisor_git_ok(seg) -> bool:
    j = 1
    while j < len(seg) and seg[j].startswith("-"):
        if seg[j] == "-c":
            return False
        j += 2 if seg[j] == "-C" else 1
    if j >= len(seg) or seg[j] not in REVISOR_GIT_OK:
        return False
    sub, args = seg[j], seg[j + 1:]
    if any(a.startswith("--output") for a in args):
        return False
    if sub == "grep" and any(a.startswith("-O") or a.startswith("--open-files-in-pager") for a in args):
        return False
    if sub == "branch" and not set(args) <= ESCRIBA_BRANCH_FLAGS:
        return False
    return True


def _revisor_net_ok(name: str, seg) -> bool:
    args = seg[1:]
    if name == "curl":
        return not any(
            a in ("--output", "--remote-name", "--remote-name-all", "-T", "--upload-file")
            or a.startswith("--output") or (re.match(r"^-[A-Za-z]*[oOT]", a) and not a.startswith("--"))
            for a in args)
    return (any(re.match(r"^-[A-Za-z]*O-$", a) or a == "--output-document=-" for a in args)
            or any(x == "-O" and y == "-" for x, y in zip(args, args[1:])))


def _revisor_segment_ok(seg) -> bool:
    cmd = seg[0]
    name = _base(cmd)
    args = seg[1:]
    pos = [a for a in args if not a.startswith("-")]
    if "/" in cmd and name != "gradlew" and name != "python3":
        return False
    if name in REVISOR_TOOLS:
        if any(a.startswith("--output") for a in args):
            return False
        if name == "find" and any(a in FIND_BAD for a in args):
            return False
        if name in ("sort", "tree") and any(re.match(r"^-[A-Za-z]*o", a) for a in args if not a.startswith("--")):
            return False
        if name == "uniq" and len(pos) > 1:
            return False
        if name == "file" and "-C" in args:
            return False
        if name == "date" and any(a in ("-s", "--set") or a.startswith("--set=") for a in args):
            return False
        if name == "rg" and any(a.startswith("--pre") for a in args):
            return False
        return True
    if name == "git":
        return _revisor_git_ok(seg)
    if name in ("osv-scanner", "pip-audit", "dependency-check"):
        if "fix" in args or "--fix" in args or any(a.startswith("--output") for a in args):
            return False
        return not (name == "pip-audit" and "-o" in args)
    if name in ("npm", "pnpm", "yarn"):
        sub = pos[0] if pos else None
        ok = {"audit", "ls", "view", "outdated"} if name == "npm" else {"audit"}
        return sub in ok and "fix" not in args
    if name in ("pip", "pip3"):
        return bool(pos) and pos[0] in {"show", "list"}
    if name in ("gradle", "gradlew"):
        return (len(pos) == 1 and pos[0] in GRADLE_TASKS
                and not any(a == "-I" or a.startswith("--init-script") for a in args))
    if name == "mvn":
        return len(pos) == 1 and pos[0] in MVN_GOALS
    if name in ("curl", "wget"):
        return _revisor_net_ok(name, seg)
    if name == "python3":
        return len(args) >= 2 and args[0] == "-I" and _base(args[1]) == "check_test_integrity.py"
    return False


def _revisor_block(command: str):
    """Allowlist: devolve o motivo do bloqueio ou None. Atribuições `VAR=x cmd` são
    bloqueadas (o primeiro token deve ser um comando permitido)."""
    if any(m in command for m in ("`", "$(", "<(", ">(")):
        return "substituição de comando ou de processo"
    if ">" in SAFE_REDIRECTS.sub(" ", command):
        return "redirecionamento de escrita"
    segs = _revisor_segments(command)
    if segs is None:
        return "subshell ou comando malformado"
    for seg in segs:
        if not _revisor_segment_ok(seg):
            return f"comando não permitido ({' '.join(seg[:3])})"
    return None


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
    segs = _segments(command)
    if role != "orquestrador" and any(sub == "push" for sub, _ in _git_calls(segs)):
        return f"Trava do {role}: git push não é permitido. Deixe o push para o usuário."
    if role == "revisor":
        what = _revisor_block(command)
        if what:
            return (f"Trava do revisor: a revisora é somente leitura; bloqueado: {what}. "
                    f"Permitido: {REVISOR_FAMILIES}. Relate o achado no relatório.")
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
        if role == "testador" and not is_test_path(path, cwd):
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
