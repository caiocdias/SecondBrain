#!/usr/bin/env python3
"""Hook do Claude Code que carrega no contexto o conhecimento de um projeto guardado no Second Brain.

Uso (no .claude/settings.json do repositório, eventos SessionStart e SubagentStart):

    load-brain.py <Projeto> [SessionStart|SubagentStart]

Imprime o JSON de `hookSpecificOutput.additionalContext` com:
- a linha `BRAIN: carregado (<Projeto>)` ou `BRAIN: indisponível (<Projeto>)`, com o motivo;
- o caminho e o conteúdo da nota de projeto (hub) em `10 Projects/`;
- a lista das capturas pendentes do projeto em `00 Inbox/`.

O hub é `10 Projects/<Projeto>.md` com `type: project` ou, na falta dele, a nota `type: project`
de `10 Projects/` que tenha `<Projeto>` nos `aliases`.

O vault vem de `SECOND_BRAIN_VAULT`, da pasta onde este script está (ele vive em
`99 System/Skills/` do vault) ou do bloco *Second Brain* de `~/.claude/CLAUDE.md`.
Nunca falha a sessão: em qualquer erro, devolve o aviso de indisponível.
"""

import json
import os
import re
import sys
from pathlib import Path

# o additionalContext tem teto de 10.000 caracteres; acima, o Claude Code corta
CONTEXT_BUDGET = 9500
MAX_PENDING_LISTED = 60


def claude_home() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def is_vault(path: Path) -> bool:
    return (path / "AGENTS.md").is_file() and (path / "99 System").is_dir()


def find_vault() -> Path | None:
    env = os.environ.get("SECOND_BRAIN_VAULT")
    if env:
        return Path(env)
    for parent in Path(__file__).resolve().parents:
        if is_vault(parent):
            return parent
    try:
        text = (claude_home() / "CLAUDE.md").read_text(encoding="utf-8")
    except OSError:
        return None
    block = re.search(r"<!-- second-brain:begin -->(.*?)<!-- second-brain:end -->", text, re.S)
    match = re.search(r"em Markdown em `([^`]+)`", block.group(1) if block else text)
    return Path(match.group(1)) if match else None


def frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---", 4)
    return text[4:end] if end > 0 else ""


def is_project(meta: str) -> bool:
    return re.search(r"^type:\s*project\s*$", meta, re.M) is not None


def aliases(meta: str) -> list[str]:
    block = re.search(r"^aliases:\s*\n((?:\s+-\s.*\n?)+)", meta, re.M)
    if not block:
        return []
    return [item.strip().strip("\"'") for item in re.findall(r"^\s+-\s+(.*)$", block.group(1), re.M)]


def find_hub(vault: Path, project: str) -> Path | None:
    projects = vault / "10 Projects"
    exact = projects / f"{project}.md"
    if exact.is_file() and is_project(frontmatter(exact)):
        return exact
    for path in sorted(projects.glob("*.md")):
        meta = frontmatter(path)
        if is_project(meta) and project.lower() in (a.lower() for a in aliases(meta)):
            return path
    return None


def pending_captures(vault: Path, project: str) -> list[Path]:
    found = []
    for path in sorted((vault / "00 Inbox").glob("*.md")):
        if path.name.startswith("."):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if re.search(r"^status:\s*inbox\s*$", text, re.M) and project.lower() in text.lower():
            found.append(path)
    return found


def build_context(project: str) -> str:
    ok, fail = f"BRAIN: carregado ({project})", f"BRAIN: indisponível ({project})"
    vault = find_vault()
    if vault is None or not is_vault(vault):
        return (
            f"{fail}\n"
            f"Motivo: vault do Second Brain não encontrado ({vault or 'caminho desconhecido'}). "
            "Configure a máquina com a skill configurar-maquina ou defina SECOND_BRAIN_VAULT."
        )
    hub = find_hub(vault, project)
    pending = pending_captures(vault, project)
    if hub is None and not pending:
        return (
            f"{fail}\n"
            f"Motivo: o projeto {project} não tem nota de projeto em {vault / '10 Projects'}/ "
            "nem capturas pendentes. Registre-o no brain (skill development-roadmap, seção do brain)."
        )
    out = [
        ok,
        f"Vault: {vault}",
        f"Contexto injetado pelo hook load-brain.py da skill development-roadmap para o projeto {project}.",
        "Leia a nota de tema do brain antes de mexer no assunto dela (notas ligadas pelo hub, em 20 Knowledge/). "
        "Esta sessão é agente externo do vault: lê notas e só cria capturas novas em 00 Inbox/.",
    ]
    if hub is None:
        out.append(
            f"Nota de projeto (hub) de {project} ainda não existe em 10 Projects/: "
            "o conhecimento do projeto está só nas capturas pendentes listadas abaixo."
        )
    else:
        out.append(f"Nota de projeto (hub): {hub}")
    if pending:
        shown = pending[:MAX_PENDING_LISTED]
        out.append(
            f"Capturas pendentes do projeto em {vault / '00 Inbox'}/ ({len(pending)}; ainda não integradas pelo "
            "curador e mais recentes que as notas quando tratam do mesmo assunto):"
        )
        out += [f"- {p.name}" for p in shown]
        if len(pending) > len(shown):
            out.append(f"- … e mais {len(pending) - len(shown)}")
    else:
        out.append("Nenhuma captura pendente do projeto em 00 Inbox/.")
    context = "\n".join(out)
    if hub is not None:
        body = hub.read_text(encoding="utf-8")
        room = CONTEXT_BUDGET - len(context) - 200
        if len(body) > room:
            body = body[: max(room, 0)] + f"\n\n[hub cortado pelo limite do hook; leia o restante em {hub}]"
        context += f"\n\n===== Conteúdo do hub ({hub.name}) =====\n{body}"
    return context[:CONTEXT_BUDGET]


def main() -> None:
    project = sys.argv[1] if len(sys.argv) > 1 else ""
    event = sys.argv[2] if len(sys.argv) > 2 else "SessionStart"
    try:
        if not project:
            raise ValueError("informe o nome do projeto como primeiro argumento")
        context = build_context(project)
    except Exception as exc:  # o hook nunca derruba a sessão
        context = f"BRAIN: indisponível ({project or '?'})\nMotivo: erro no hook ({type(exc).__name__}: {exc})."
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
