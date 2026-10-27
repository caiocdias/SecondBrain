#!/usr/bin/env python3
"""Verificador estrutural de roadmaps gerados pela skill development-roadmap.

Uso: python3 check_roadmap.py <roadmap.md> [--strict]

Erros (código de saída 1) indicam violações das regras da skill.
Avisos merecem leitura, mas podem ser legítimos. Com --strict, avisos também falham.
"""

import re
import sys
from pathlib import Path

CANONICAL_TAGS = {"#pendente", "#em-andamento", "#concluida", "#bloqueada"}
# Variações comuns que não são canônicas (acentos, gênero, inglês).
TAG_LIKE = re.compile(
    r"#(pendente|em[-_ ]andamento|conclu[íi]d[ao]|bloquead[ao]|"
    r"pending|in[-_]progress|done|blocked|todo)\b",
    re.IGNORECASE,
)
STAGE_ID = re.compile(r"\bE\d{2,3}\b")
STAGE_HEADING = re.compile(r"^##\s+(E\d{2,3})\s*[—–-]\s*(.+?)\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")

# Seções obrigatórias por etapa: cada item aceita sinônimos em pt/en.
REQUIRED_SECTIONS = {
    "Objetivo": ["objetivo", "objective", "goal"],
    "Critérios de aceite": ["critérios de aceite", "criterios de aceite", "acceptance criteria"],
    "Validação": ["validação", "validacao", "validation"],
    "Revisão humana": ["revisão humana", "revisao humana", "human review"],
    "Bloqueios": ["bloqueio", "blocker"],
    "Evidências e handoff": ["handoff", "evidências", "evidencias", "evidence"],
}

# Skills do superpowers que o prompt de execução precisa acionar.
SOULS = ("orquestrador-etapa", "desenvolvedor", "testador", "revisor-seguranca")
PROMPT_SKILLS = [
    "superpowers:using-git-worktrees",
    "superpowers:writing-plans",
    "superpowers:subagent-driven-development",
    "superpowers:finishing-a-development-branch",
]

PLACEHOLDER_PATTERNS = [
    (re.compile(r"\b(TODO|TBD|FIXME)\b"), "marcador de pendência"),
    (re.compile(r"\{\{[^}]*\}\}"), "placeholder {{...}}"),
    (re.compile(r"\[(preencher|a definir|inserir|fill in)[^\]]*\]", re.IGNORECASE), "placeholder [...]"),
]
# <algo-assim> precedido de espaço, início, '(' ou '/' (não genéricos como List<String>).
# Só aviso: às vezes é um padrão legítimo ("db/migration/<módulo>").
ANGLE_PLACEHOLDER = re.compile(r"(?:(?<=^)|(?<=[\s(/`'\"]))<[a-zà-ú][a-zà-ú0-9 _\-/.]*>", re.IGNORECASE)
HUMAN_REVIEW_LINE = re.compile(r"(revis[ãa]o humana|human review)", re.IGNORECASE)
HUMAN_REVIEW_VALUE = re.compile(r"(revis[ãa]o humana|human review)\W*(sim|n[ãa]o|yes|no)\b", re.IGNORECASE)
# Marcas do formato anterior (protocolo próprio, sem superpowers).
LEGACY_MARKERS = re.compile(r"estrat[ée]gia de execu[çc][ãa]o|execu[çc][ãa]o autom[áa]tica|write-tree|prompt do verificador", re.IGNORECASE)
HTML_TAGS = {"br", "b", "i", "em", "strong", "sub", "sup", "kbd", "code", "details", "summary", "p", "div", "span", "hr"}
NO_BLOCKER = re.compile(r"nenhum bloqueio|sem bloqueio|no known blocker|no blockers?|none", re.IGNORECASE)


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, line, msg):
        self.errors.append((line, msg))

    def warn(self, line, msg):
        self.warnings.append((line, msg))


def strip_fences(lines):
    """Devolve (linha, dentro_de_bloco_de_código) para cada linha."""
    inside = False
    out = []
    for line in lines:
        if FENCE.match(line):
            out.append((line, True))
            inside = not inside
            continue
        out.append((line, inside))
    return out


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_index(lines, rep):
    """Extrai {id: (tags, deps, lineno)} da tabela de índice.

    As dependências vêm da coluna cujo cabeçalho contém "depend"; sem esse
    cabeçalho, de todas as colunas exceto a primeira e a de estado.
    """
    index = {}
    order = []
    dep_col = None
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s.startswith("|"):
            dep_col = None  # fim da tabela
            continue
        cells = split_row(s)
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue  # linha separadora
        heads = [c.lower() for c in cells]
        if not STAGE_ID.search(cells[0]) and any("depend" in h for h in heads):
            dep_col = next(n for n, h in enumerate(heads) if "depend" in h)
            continue
        m = STAGE_ID.search(cells[0])
        if not m or not re.fullmatch(r"[\s\[\]()#\w-]*", cells[0]):
            continue
        sid = m.group(0)
        rest = cells[1:]
        tags = [t for c in rest for t in re.findall(r"#[\w-]+", c) if t in CANONICAL_TAGS or TAG_LIKE.fullmatch(t)]
        if dep_col is not None and dep_col < len(cells):
            dep_cells = [cells[dep_col]]
        else:
            dep_cells = [c for c in rest if not TAG_LIKE.search(c)]
        deps = [x for c in dep_cells for x in STAGE_ID.findall(c) if x != sid]
        if sid in index:
            rep.error(i, f"{sid} aparece mais de uma vez no índice")
            continue
        index[sid] = (tags, deps, i)
        order.append(sid)
    return index, order


def parse_stages(lines, rep):
    stages = {}
    order = []
    marked = strip_fences(lines)
    current = None
    for i, (line, in_code) in enumerate(marked, 1):
        if in_code:
            if current:
                current["body"].append((i, line, True))
            continue
        m = STAGE_HEADING.match(line)
        if m:
            sid, rest = m.group(1), m.group(2)
            if sid in stages:
                rep.error(i, f"etapa {sid} definida mais de uma vez")
            current = {"id": sid, "line": i, "heading": rest, "body": []}
            stages[sid] = current
            order.append(sid)
            continue
        if line.startswith("## ") or line.startswith("# "):
            current = None
            continue
        if current:
            current["body"].append((i, line, False))
    return stages, order


def heading_tags(heading):
    return re.findall(r"#[\w-]+", heading)


def check_tags(sid, tags, where, line, rep):
    canon = [t for t in tags if t in CANONICAL_TAGS]
    bad = [t for t in tags if t not in CANONICAL_TAGS and TAG_LIKE.fullmatch(t)]
    for t in bad:
        rep.error(line, f"{sid}: tag não canônica {t} no {where} (use {', '.join(sorted(CANONICAL_TAGS))})")
    if len(canon) != 1 and not bad:
        rep.error(line, f"{sid}: {where} deve ter exatamente uma tag canônica, encontrou {canon or 'nenhuma'}")
    return canon[0] if len(canon) == 1 else None


def section_text(stage, keywords):
    """Texto da seção cujo rótulo contém uma das palavras-chave, até o próximo rótulo."""
    label = re.compile(r"^\s*(\*\*|###+\s*)([^*:]+)")
    out, inside = [], False
    for _, line, in_code in stage["body"]:
        m = None if in_code else label.match(line)
        if m:
            inside = any(k in m.group(2).lower() for k in keywords)
            if inside:
                out.append(line)
            continue
        if inside:
            out.append(line)
    return "\n".join(out)


def header_section(lines, heading_line):
    """Linhas da seção '## ...' que começa em heading_line (1-based), até o próximo '## '."""
    out = []
    for line in lines[heading_line:]:
        if line.startswith("## "):
            break
        out.append(line)
    return out


def first_code_block(section_lines):
    block, inside = [], False
    for line in section_lines:
        if FENCE.match(line):
            if inside:
                return "\n".join(block)
            inside = True
            continue
        if inside:
            block.append(line)
    return "\n".join(block) if inside else None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv
    if len(args) != 1:
        print(__doc__)
        return 2
    path = Path(args[0])
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    rep = Report()

    index, index_order = parse_index(lines, rep)
    stages, stage_order = parse_stages(lines, rep)

    if not stages:
        rep.error(1, "nenhuma etapa encontrada (formato esperado: '## E01 — Nome — #pendente')")
    if not index:
        rep.error(1, "índice de etapas não encontrado (tabela com IDs E01, E02… na primeira coluna)")

    # Tags e sincronia índice ↔ etapas
    stage_tag = {}
    for sid in stage_order:
        st = stages[sid]
        stage_tag[sid] = check_tags(sid, heading_tags(st["heading"]), "título", st["line"], rep)
    for sid in index_order:
        tags, _, line = index[sid]
        itag = check_tags(sid, tags, "índice", line, rep)
        if sid not in stages:
            rep.error(line, f"{sid} está no índice mas não tem seção '## {sid} — …'")
        elif itag and stage_tag.get(sid) and itag != stage_tag[sid]:
            rep.error(line, f"{sid}: tag do índice ({itag}) difere da tag do título ({stage_tag[sid]})")
    for sid in stage_order:
        if index and sid not in index:
            rep.error(stages[sid]["line"], f"{sid} tem seção mas não está no índice")

    # Dependências: existem e aparecem antes no documento (o que também exclui ciclos)
    pos = {sid: n for n, sid in enumerate(stage_order)}
    graph = {}
    for sid in index_order:
        _, deps, line = index[sid]
        graph[sid] = deps
        for d in deps:
            if d not in pos and d not in index:
                rep.error(line, f"{sid} depende de {d}, que não existe")
            elif sid in pos and d in pos and pos[d] > pos[sid]:
                rep.error(line, f"{sid} depende de {d}, que aparece depois no documento")

    # Coerência de estados
    in_progress = [s for s, t in stage_tag.items() if t == "#em-andamento"]
    if len(in_progress) > 1:
        rep.warn(1, f"mais de uma etapa #em-andamento ({', '.join(in_progress)}); só é válido em branches separadas")
    for sid, tag in stage_tag.items():
        if tag in ("#concluida", "#em-andamento"):
            for d in graph.get(sid, []):
                if d in stage_tag and stage_tag[d] != "#concluida":
                    rep.warn(stages[sid]["line"], f"{sid} está {tag} mas a dependência {d} está {stage_tag.get(d)}")

    roadmap_name = path.name

    # Protocolo e prompt de execução (seções de cabeçalho, fora das etapas)
    headings = {i: l[3:].strip().lower() for i, l in enumerate(lines, 1) if l.startswith("## ")}
    protocol = [i for i, h in headings.items() if "protocolo de execu" in h or "execution protocol" in h]
    if not protocol:
        rep.error(1, "seção '## Protocolo de execução' ausente no cabeçalho")
    else:
        body = "\n".join(header_section(lines, protocol[0])).lower()
        if "superpowers" not in body:
            rep.warn(protocol[0], "o protocolo de execução não menciona o superpowers")
        if "roadmap/" not in body:
            rep.warn(protocol[0], "o protocolo de execução não nomeia a branch roadmap/<slug>")
        if not all(s in body for s in SOULS):
            rep.warn(protocol[0], "o protocolo de execução não usa as souls (orquestrador-etapa, desenvolvedor, testador, revisor-seguranca)")
    prompt_heads = [i for i, h in headings.items() if "prompt de execu" in h or "execution prompt" in h]
    if not prompt_heads:
        rep.error(1, "seção '## Prompt de execução' ausente no cabeçalho")
    else:
        prompt = first_code_block(header_section(lines, prompt_heads[0]))
        if not prompt:
            rep.error(prompt_heads[0], "'Prompt de execução' sem prompt em bloco de código")
        else:
            if roadmap_name not in prompt:
                rep.error(prompt_heads[0], f"o prompt de execução não cita o arquivo do roadmap ({roadmap_name})")
            for skill in PROMPT_SKILLS:
                if skill not in prompt:
                    rep.warn(prompt_heads[0], f"o prompt de execução não aciona {skill}")
            low = prompt.lower()
            if "limite" not in low and "limit" not in low:
                rep.warn(prompt_heads[0], "o prompt de execução não define o limite de etapas por execução")
            if "push" not in low:
                rep.warn(prompt_heads[0], "o prompt de execução não proíbe push/merge sem decisão do usuário")

    # Formato anterior (fora de blocos de código)
    for i, (line, in_code) in enumerate(strip_fences(lines), 1):
        if not in_code and LEGACY_MARKERS.search(line):
            rep.warn(i, "marca do formato antigo do roadmap; migre conforme a skill (§6)")
            break

    # Conteúdo de cada etapa
    for sid in stage_order:
        st = stages[sid]
        body_plain = "\n".join(l for _, l, c in st["body"] if not c).lower()
        for name, keys in REQUIRED_SECTIONS.items():
            if not any(k in body_plain for k in keys):
                rep.error(st["line"], f"{sid}: seção obrigatória ausente: {name}")
        for ln, line, in_code in st["body"]:
            if not in_code and HUMAN_REVIEW_LINE.search(line):
                if not HUMAN_REVIEW_VALUE.search(line.replace("*", "")):
                    rep.error(ln, f"{sid}: 'Revisão humana' deve dizer sim ou não")
                break
        handoff = section_text(st, ["handoff", "evidências", "evidencias", "evidence"]).lower()
        for needle in ("plano", "commits"):
            if handoff and needle not in handoff:
                rep.warn(st["line"], f"{sid}: 'Evidências e handoff' sem o campo '{needle}'")
        if stage_tag.get(sid) == "#bloqueada":
            blk = section_text(st, ["bloqueio", "blocker"])
            if not blk or NO_BLOCKER.search(blk):
                rep.error(st["line"], f"{sid}: está #bloqueada mas a seção Bloqueios não descreve o bloqueio")
            elif not all(re.search(k, blk, re.IGNORECASE) for k in ["causa|cause", "a[çc][ãa]o|action|desbloq|unblock"]):
                rep.warn(st["line"], f"{sid}: bloqueio sem causa e/ou ação de desbloqueio explícitas")

    # Placeholders (em todo o arquivo, inclusive prompts)
    for i, line in enumerate(lines, 1):
        for pat, msg in PLACEHOLDER_PATTERNS:
            for m in pat.finditer(line):
                rep.error(i, f"{msg}: {m.group(0)!r}")
        for m in ANGLE_PLACEHOLDER.finditer(line):
            if m.group(0).strip("<>/").lower() not in HTML_TAGS:
                rep.warn(i, f"possível placeholder: {m.group(0)!r}")

    # Saída
    print(f"Roadmap: {path}  ·  {len(stage_order)} etapas  ·  índice com {len(index_order)} linhas")
    counts = {}
    for t in stage_tag.values():
        counts[t] = counts.get(t, 0) + 1
    if counts:
        print("Estados: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: str(kv[0]))))
    for line, msg in sorted(rep.errors):
        print(f"ERRO   L{line}: {msg}")
    for line, msg in sorted(rep.warnings):
        print(f"AVISO  L{line}: {msg}")
    if not rep.errors and not rep.warnings:
        print("OK: nenhum problema estrutural encontrado.")
    failed = bool(rep.errors) or (strict and bool(rep.warnings))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
