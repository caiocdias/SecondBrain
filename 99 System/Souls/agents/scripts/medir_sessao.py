#!/usr/bin/env python3
"""Mede onde vai o tempo de relógio de uma sessão do orquestrador.

Lê o transcrito da sessão (`<sessão>.jsonl`) e os dos subagentes
(`<sessão>/subagents/agent-*.jsonl`). Cada intervalo entre dois registros
consecutivos de um fluxo é atribuído a: API (termina em registro do assistente),
ferramenta (termina em tool_result), espera de tarefa em segundo plano (termina
em notificação) ou ocioso (termina em prompt novo ou mensagem do coordenador).

Uso: medir_sessao.py [-q] [--gate-regex R] [--build NOME=REGEX ...] SESSAO.jsonl...

Limites: a atribuição vem dos carimbos de tempo; os comandos são classificados
por expressão regular; o tempo de build é um piso (esperas indiretas ficam fora).
"""
import argparse
import collections
import glob
import json
import os
import re
import sys
from datetime import datetime

# Padrões de comando de build e teste; a ordem decide a classe quando mais de um casa.
BUILD_PADRAO = {
    'gradle': r'gradlew?\b',
    'pytest': r'\bpytest\b|python3? (-\w+ )*-m (pytest|unittest)',
    'run.sh': r'tests?/run\.sh|run_tests|make (test|check|gate)',
    'node': r'\b(npm|pnpm|yarn|npx|vitest|jest)\b',
    'build-outro': r'\b(mvn|dotnet|cargo|go test)\b',
}
# Comando que conta como uma execução do gate completo do projeto. O padrão é
# comparado com o início de cada comando da linha de shell, não com o texto todo.
GATE_PADRAO = r"(?:\./gradlew|gradle)\s+build\b"


def ts(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()


def hm(sec):
    sec = int(sec)
    return f"{sec//3600}h{(sec%3600)//60:02d}" if sec >= 3600 else f"{sec//60}m{sec%60:02d}"


def classify(cmd, build=None):
    c = cmd or ''
    for nome, padrao in (BUILD_PADRAO if build is None else build).items():
        if re.search(padrao, c): return nome
    if re.search(r'osv-scanner|pip-audit|dependencyCheck', c): return 'scanner'
    if re.search(r'\bgit\b', c): return 'git'
    return 'bash-outro'


def text_of(d):
    c = d.get('message', {}).get('content')
    if isinstance(c, str): return c
    if isinstance(c, list):
        return ' '.join(b.get('text', '') for b in c if isinstance(b, dict) and b.get('type') == 'text')
    return ''


def has_result(d):
    c = d.get('message', {}).get('content')
    return isinstance(c, list) and any(isinstance(b, dict) and b.get('type') == 'tool_result' for b in c)


def analyze(rows, is_main, build=None):
    """Devolve dict com tempos por categoria, intervalos ativos e contagens."""
    R = dict(api=0.0, tools=collections.Counter(), bgwait=0.0, idle=0.0, active=[], out=0, think=0,
             calls=0, cache_read=0, models=collections.Counter(), dispatches=0, long=[], subwait=0.0)
    seen = {}; pending = {}; prev = None
    for d in rows:
        if d.get('type') not in ('user', 'assistant') or not d.get('timestamp'): continue
        t = ts(d['timestamp']); m = d.get('message', {})
        kind = None
        if d['type'] == 'assistant':
            kind = 'api'
            mid = m.get('id')
            u = m.get('usage') or {}
            if mid not in seen:
                R['calls'] += 1; R['models'][m.get('model', '?')] += 1
            seen[mid] = u
            for b in m.get('content') or []:
                if isinstance(b, dict) and b.get('type') == 'tool_use':
                    inp = b.get('input') or {}
                    cls = classify(inp.get('command'), build) if b['name'] == 'Bash' else b['name']
                    pending[b['id']] = (cls, (inp.get('command') or '')[:150])
        elif has_result(d):
            kind = 'tool'
            cls = None
            for b in m['content']:
                if isinstance(b, dict) and b.get('type') == 'tool_result':
                    cls, cmd = pending.pop(b.get('tool_use_id'), ('?', ''))
        else:
            txt = text_of(d)
            if d.get('isMeta') and 'system-reminder' in txt[:40] and prev is not None and t - prev < 5:
                kind = 'skip'
            elif re.search(r'task-notification|background-task event|SYSTEM NOTIFICATION', txt[:400]):
                kind = 'subwait' if is_main else 'bgwait'
                if is_main and 'agent-message' not in txt[:200] and re.search(r'<task-id>b', txt[:300]):
                    kind = 'bgwait'
            elif 'agent-message' in txt[:200] or 'Subagent hand-back' in txt[:300]:
                kind = 'subwait'
            else:
                kind = 'idle'
                R['dispatches'] += 1
        if prev is not None and kind != 'skip':
            g = t - prev
            if kind == 'api': R['api'] += g; R['active'].append((prev, t))
            elif kind == 'tool':
                R['tools'][cls] += g; R['active'].append((prev, t))
                if g >= 90: R['long'].append((g, cls, cmd))
            elif kind == 'bgwait': R['bgwait'] += g; R['active'].append((prev, t))
            elif kind == 'subwait': R['subwait'] += g
            else: R['idle'] += g
        prev = t
    for u in seen.values():
        R['out'] += u.get('output_tokens', 0)
        R['think'] += (u.get('output_tokens_details') or {}).get('thinking_tokens', 0)
        R['cache_read'] += u.get('cache_read_input_tokens', 0)
    return R


def union(iv):
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1]: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out


def total(iv): return sum(b - a for a, b in iv)


def subtract(a_iv, b_iv):
    """Parte de a_iv não coberta por b_iv (ambos já unidos)."""
    res = []
    for a, b in a_iv:
        cur = a
        for c, d in b_iv:
            if d <= cur: continue
            if c >= b: break
            if c > cur: res.append([cur, c])
            cur = max(cur, d)
            if cur >= b: break
        if cur < b: res.append([cur, b])
    return res


HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1.*?^\s*\2\s*$", re.S | re.M)
SEPARADOR = re.compile(r'&&|\|\||[;\n|({]')
PREFIXO = re.compile(r'^(?:timeout\s+\S+\s+|time\s+|nice\s+(?:-n\s*\d+\s+)?|\w+=\S+\s+)*')


def executa_gate(cmd, gate_regex):
    """True se algum comando da linha de shell começa pelo gate; menção em texto ou heredoc não conta."""
    for parte in SEPARADOR.split(HEREDOC.sub('', cmd or '')):
        if re.match(gate_regex, PREFIXO.sub('', parte.strip())):
            return True
    return False


def contar_gates(rows, gate_regex):
    """Chamadas Bash distintas que executam o gate."""
    ids = set()
    for d in rows:
        if d.get('type') != 'assistant': continue
        for b in d.get('message', {}).get('content') or []:
            if (isinstance(b, dict) and b.get('type') == 'tool_use' and b.get('name') == 'Bash'
                    and executa_gate((b.get('input') or {}).get('command'), gate_regex)):
                ids.add(b.get('id'))
    return len(ids)


def razao(a, b):
    return a / b if b else None


def ler_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(l) for l in f]


def ler_meta(path):
    if not os.path.exists(path): return {}
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def medir(path, gate_regex=GATE_PADRAO, build=None):
    """Mede uma sessão. Tempos em segundos; razões são None quando o divisor é zero."""
    nomes_build = tuple(BUILD_PADRAO if build is None else build)
    def tempo_build(tools): return sum(v for k, v in tools.items() if k in nomes_build)

    rows = ler_jsonl(path)
    main_rows = [d for d in rows if not d.get('isSidechain')]
    stamps = [ts(d['timestamp']) for d in main_rows if d.get('timestamp') and d.get('type') in ('user', 'assistant')]
    t0, t1 = min(stamps), max(stamps)
    M = analyze(main_rows, True, build)
    gates = contar_gates(main_rows, gate_regex)
    subs = []
    for f in sorted(glob.glob(path[:-6] + '/subagents/agent-*.jsonl')):
        meta = ler_meta(f[:-6] + '.meta.json')
        srows = ler_jsonl(f)
        S = analyze(srows, False, build)
        st = [ts(d['timestamp']) for d in srows if d.get('timestamp')]
        S.update(role=meta.get('agentType', '?'), desc=meta.get('description', ''), model=meta.get('model') or '',
                 start=min(st), end=max(st), ativo=total(union(S['active'])), build=tempo_build(S['tools']))
        gates += contar_gates(srows, gate_regex)
        subs.append(S)
    subs.sort(key=lambda s: s['start'])
    sub_u = union([iv for s in subs for iv in s['active']])
    main_u = union(M['active'])
    busy = union([list(x) for x in sub_u] + [list(x) for x in main_u])
    por_papel = {}
    for s in subs:
        r = por_papel.setdefault(s['role'], dict(agentes=0, despachos=0, ativo=0.0, api=0.0, build=0.0,
                                                 espera_bg=0.0, outras=0.0, saida=0, chamadas=0))
        r['agentes'] += 1; r['despachos'] += max(s['dispatches'], 1); r['ativo'] += s['ativo']
        r['api'] += s['api']; r['build'] += s['build']; r['espera_bg'] += s['bgwait']
        r['outras'] += sum(s['tools'].values()) - s['build']; r['saida'] += s['out']; r['chamadas'] += s['calls']
    relogio = t1 - t0
    sub_ativo = total(sub_u)
    sub_soma = sum(s['ativo'] for s in subs)
    nada = relogio - total(busy)
    espera_usuario = M['tools'].get('AskUserQuestion', 0.0)
    tarefas = sum(1 for s in subs if s['role'] == 'desenvolvedor')
    testadores = sum(1 for s in subs if s['role'] == 'testador')
    return dict(
        inicio=t0, fim=t1, relogio=relogio, sub_ativo=sub_ativo, sub_soma=sub_soma,
        paralelismo=razao(sub_soma, sub_ativo), so_orquestrador=total(subtract(main_u, sub_u)),
        nada_rodando=nada, espera_usuario=espera_usuario, relogio_sem_usuario=relogio - nada - espera_usuario,
        tarefas=tarefas, testadores=testadores, fracao_testador=razao(testadores, tarefas),
        gates=gates, gates_por_tarefa=razao(gates, tarefas), por_papel=por_papel,
        api_total=sum(s['api'] for s in subs) + M['api'],
        build_total=sum(s['build'] + s['bgwait'] for s in subs) + tempo_build(M['tools']) + M['bgwait'],
        principal=M, subagentes=subs,
        prompt=next((text_of(d) for d in main_rows
                     if d.get('type') == 'user' and not has_result(d) and not d.get('isMeta')), ''))


def num(v, fmt="{:.2f}"):
    return '—' if v is None else fmt.format(v)


def imprimir(path, r, verbose):
    M = r['principal']; subs = r['subagentes']
    print(f"\n===== {os.path.basename(path)[:8]}  {datetime.fromtimestamp(r['inicio']):%m-%d %H:%M} → "
          f"{datetime.fromtimestamp(r['fim']):%m-%d %H:%M}  relógio {hm(r['relogio'])}")
    print("prompt:", re.sub(r'\s+', ' ', r['prompt'])[:230])
    print(f"RELÓGIO: subagentes ativos {hm(r['sub_ativo'])} (soma {hm(r['sub_soma'])}, paralelismo "
          f"{num(r['paralelismo'])}x) | só orquestrador {hm(r['so_orquestrador'])} | nada rodando {hm(r['nada_rodando'])}")
    print(f"MEDIDAS: relógio sem usuário {hm(r['relogio_sem_usuario'])} (espera em AskUserQuestion "
          f"{hm(r['espera_usuario'])}) | tarefas {r['tarefas']} | gates por tarefa {num(r['gates_por_tarefa'])} "
          f"({r['gates']} gates) | testador por tarefa {num(r['fracao_testador'])} ({r['testadores']} testadores)")
    mt = sum(M['tools'].values())
    print(f"ORQUESTRADOR: API {hm(M['api'])} ({M['calls']} chamadas, {M['out']//1000}k tok saída, {M['think']//1000}k pensando) | "
          f"ferramentas {hm(mt)} [" + ', '.join(f"{k} {hm(v)}" for k, v in M['tools'].most_common(6)) +
          f"] | espera bg {hm(M['bgwait'])}")
    print(f"{'papel':20}{'agentes':>8}{'desp+ret':>9}{'ativo':>8}{'méd/desp':>9}{'API':>8}{'build/teste':>12}"
          f"{'espera bg':>10}{'outras ferr':>12}{'tok saída':>10}{'chamadas':>9}")
    for role, p in sorted(r['por_papel'].items(), key=lambda kv: -kv[1]['ativo']):
        print(f"{role:20}{p['agentes']:>8}{p['despachos']:>9}{hm(p['ativo']):>8}{hm(p['ativo']/p['despachos']):>9}"
              f"{hm(p['api']):>8}{hm(p['build']):>12}{hm(p['espera_bg']):>10}{hm(p['outras']):>12}"
              f"{str(p['saida']//1000)+'k':>10}{p['chamadas']:>9}")
    print(f"TOTAIS (soma de agente-tempo): API {hm(r['api_total'])} | build/teste + espera bg {hm(r['build_total'])}")
    if verbose:
        print("-- agentes (início, ativo, API, build+bg, papel, modelo, desp, descrição)")
        for s in subs:
            print(f"  {datetime.fromtimestamp(s['start']):%d %H:%M} {hm(s['ativo']):>6} api {hm(s['api']):>6} "
                  f"build {hm(s['build']+s['bgwait']):>6} {s['role'][:18]:18} {s['model'][:7]:7} "
                  f"x{max(s['dispatches'],1)} {s['desc'][:60]}")
        print("-- comandos longos (≥90s), todos os fluxos, top 12")
        allc = [(g, 'orq', c, cmd) for g, c, cmd in M['long']] + \
               [(g, s['role'][:5], c, cmd) for s in subs for g, c, cmd in s['long']]
        for g, who, c, cmd in sorted(allc, reverse=True)[:12]:
            print(f"  {hm(g):>6} {who:6} {c:10} {cmd.replace(chr(10), ' ')[:110]}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Mede onde vai o tempo de uma sessão do orquestrador.")
    ap.add_argument('sessoes', nargs='+', metavar='SESSAO.jsonl')
    ap.add_argument('-q', action='store_true', help="só o resumo, sem a lista de agentes e de comandos longos")
    ap.add_argument('--gate-regex', default=GATE_PADRAO, help="comando que conta como gate completo do projeto")
    ap.add_argument('--build', action='append', metavar='NOME=REGEX',
                    help="classe de comando de build/teste; repetível; substitui os padrões")
    a = ap.parse_args(argv)
    build = None
    if a.build:
        build = {}
        for item in a.build:
            nome, sep, padrao = item.partition('=')
            if not sep or not nome or not padrao: ap.error(f"--build espera NOME=REGEX, recebeu {item!r}")
            build[nome] = padrao
    for p in a.sessoes:
        imprimir(p, medir(p, a.gate_regex, build), not a.q)


if __name__ == '__main__':
    main()
