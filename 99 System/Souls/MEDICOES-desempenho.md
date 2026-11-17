# Souls — medições de desempenho da execução

Registro das rodadas medidas contra os critérios da §7 de [`DESIGN-desempenho.md`](DESIGN-desempenho.md). Cada entrada traz a saída do `agents/scripts/medir_sessao.py`, as correções feitas à mão e o que foi observado. Entradas novas vão no fim.

## Medição 1 — 2026-11-17, DesktopFront, M3 (E05 e E06)

Primeira rodada depois da mudança das souls (commit `db0bf19` do vault). Medida em 2026-11-17, por volta de 12:05, numa sessão curadora.

### Sessão

- Transcrito: `~/.claude/projects/-home-caio-repos-ZenyHotelManager-DesktopFront/17d41971-6b7a-4b71-93fe-644921d4163a.jsonl`
- Repositório: ZenyHotelManager-DesktopFront, roadmap `roadmap-m3-reservas`, prompt de execução com limite de 4 etapas.
- Horário: 03:01 a 12:01 (hora local). A sessão podia ainda estar aberta: a medição cobre até o último registro, 12:01.
- Trabalho feito: a E05 retomada (Tasks 2 a 7, 6 tarefas) e a E06, etapa de correção nascida da revisão adiada (três revisões no início, plano e 8 tarefas). São 14 tarefas: 11 despachadas ao `desenvolvedor` e 3 tarefas só de teste despachadas ao `testador` (E05 Task 3, E06 Tasks 2 e 8).

### Saída bruta do script

```text
RELÓGIO: subagentes ativos 8h05 (soma 12h40, paralelismo 1.57x) | só orquestrador 55m10 | nada rodando 0m00
MEDIDAS: relógio sem usuário 9h00 (espera em AskUserQuestion 0m00) | tarefas 11 | gates por tarefa 0.82 (9 gates) | testador por tarefa 0.82 (9 testadores)
ORQUESTRADOR: API 1h20 (352 chamadas, 445k tok saída, 113k pensando) | ferramentas 18m03 [run.sh 10m45, gradle 3m06, git 2m10, bash-outro 1m45, Agent 0m05, scanner 0m02] | espera bg 1h28
papel                agentes desp+ret   ativo méd/desp     API build/teste espera bg outras ferr tok saída chamadas
desenvolvedor             11       18    5h59    19m57   44m46        1h16      3h44       13m14      299k      398
testador                   9       14    5h11    22m15   52m01       55m07      2h52       31m44      407k      386
revisor-seguranca         22       23    1h16     3m20    1h16        0m00      0m00        0m31      445k      353
revisor-arquitetura        1        2   12m28     6m14   12m25        0m00      0m00        0m02       73k       24
brain-escriba              1        1    0m31     0m31    0m28        0m00      0m00        0m02        4k        6
TOTAIS (soma de agente-tempo): API 4h26 | build/teste + espera bg 10h31
```

### Correções feitas à mão

O script errou três números nesta sessão. As correções vieram de scripts avulsos sobre o mesmo transcrito.

| Número bruto | Problema | Valor corrigido |
|---|---|---|
| Paralelismo 1,57× | Conta como tempo ativo dois intervalos de espera em segundo plano acima de 1 hora: 3h32 de um `desenvolvedor` que já tinha entregado o relatório (laço `until … pgrep` deixado em segundo plano) e 2h39 do testador de etapa travado | 1,47× (soma 6h28, união 4h25) |
| 0,82 gate por tarefa | `tarefas` conta só agentes `desenvolvedor`; 3 tarefas foram feitas pelo `testador` | 0,6 (9 gates em 14 tarefas) |
| 0,82 de testador por tarefa | Conta o testador de etapa e as tarefas de teste feitas pelo `testador` | 4 ataques por tarefa em 14 tarefas (29%) |

Tempo ativo por papel sem os dois intervalos: `desenvolvedor` 2h26, `testador` 2h32, `revisor-seguranca` 1h16, `revisor-arquitetura` 12m28.

### Critérios da §7

| Critério | Antes | Alvo | Medido |
|---|---|---|---|
| Relógio por etapa | 4 a 10 h | 1 a 2 h (3–4 etapas em 4–6 h) | 4h30 em média; 3h10 sem o travamento |
| Paralelismo | 1,0–1,2× | ≥ 1,5× | 1,47× |
| Execuções do gate completo por tarefa | 4,4–6,4 | ≤ 1,5 | 0,6 |
| Tarefas com testador por tarefa | ~100% | ≤ 1/3 | 29% |
| Etapas fechadas sem revisão final limpa | 0 | 0 | Não conferido: as duas revisões finais rodaram, mas o resultado e o estado das etapas no roadmap não foram lidos |
| Achados da revisão final por etapa, e resíduos | handoffs anteriores | não piora | Não conferido |

Relógio por tarefa, pela mesma conta nas sessões antigas e na nova (relógio sem a espera pelo usuário ÷ tarefas):

| Sessão | Processo | Tarefas | Relógio por tarefa |
|---|---|---|---|
| `cb751ff8` (11/11) | antigo | 29 | 29 min |
| `dee54bd2` (13–14/11) | antigo | 37 | 35 min |
| `1b54dfc9` (16/11) | antigo | 16 | 46 min |
| `8fed532b` (14–15/11) | antigo | 19 | 50 min |
| `190efebf` (16–17/11) | ADR 0011 | 28 | 15 min |
| `17d41971` (17/11) | novo | 14 | 39 min; 27 min sem o travamento |

Nas sessões antigas, `tarefas` é o número de agentes `desenvolvedor`. Na nova, com esse mesmo divisor (11), o resultado é 49 min, ou 35 min sem o travamento.

### As regras novas foram seguidas

Execuções de build e teste por papel, comparadas com a sessão antiga `dee54bd2` (37 tarefas):

| Papel | Comando | Sessão antiga | Sessão nova |
|---|---|---|---|
| `desenvolvedor` | `./gradlew build` | 137 (3h42) | 0 |
| `desenvolvedor` | `tests/run.sh` completo | 23 (49 min) | 0 |
| `desenvolvedor` | teste focado (`--tests`) | 125 (1h06) | 45 (58 min) |
| `testador` | `./gradlew build` | 83 (2h40) | 0 |
| `testador` | `tests/run.sh` completo | 16 (36 min) | 0 |
| `testador` | teste focado (`--tests`) | 64 (36 min) | 40 (32 min) |
| `orquestrador` | `./gradlew build` | 8 | 9 |

O tempo ativo do `desenvolvedor` caiu de 20 para 13 minutos por tarefa.

### Linha do tempo

**E05 (03:01 a 05:53, 2h52)**

- 03:06–04:17: as 6 tarefas, em 1h11 (12 min por tarefa). A primeira onda teve 3 tarefas em paralelo.
- 04:09–05:02: testador de etapa, 53 min, em opus (27 min de API), com teste de mutação feito à mão.
- 05:03–05:24: espera de 19 min por uma tarefa em segundo plano do orquestrador (gate).
- 05:24–05:35: revisão final, 11 min.
- 05:36–05:53: fechamento, com um `tests/run.sh` de 5m11.

**E06 (05:53 a 12:01, 6h08; 3h29 sem o travamento)**

- 05:54–06:08: três revisões da dívida do ADR 0011 em paralelo (E03, E04 e transversal), 11 a 14 min cada.
- 06:10–06:33: plano e revisão de arquitetura, com uma rodada de correção.
- 06:33–08:34: 8 tarefas em três ondas, 2h01 (15 min por tarefa). Cada onda teve uma tarefa com testador por tarefa, de 15 a 17 min antes da revisão; a Task 1 teve duas rodadas de correção. Gates entre as ondas: 10m32 e 11m15.
- 08:34–11:35: testador de etapa. Às 08:51 um `./gradlew :app:test --tests …` passou para segundo plano depois de 180 s; a notificação de término só chegou às 11:35. Foram 2h39 sem nada mais rodando. O usuário perguntou "tem algo rodando?" às 09:35 e "está travado?" às 11:34. A causa do travamento do Gradle não foi investigada.
- 11:37–11:48: gate, 10m06.
- 11:48–11:53: revisão final.
- 11:55–12:01: fechamento, com um `tests/run.sh` de 5m28.

### Onde ficou o tempo

Do relógio de 9h00:

- **Travamento do testador de etapa da E06:** 2h39.
- **Gates no caminho crítico:** cerca de 1h40, somando a espera em segundo plano do orquestrador (1h28), o `tests/run.sh` em primeiro plano (10m45) e o Gradle (3m06). Foram 9 gates de 10 a 12 minutos, um deles de 19.
- **Testador de etapa da E05:** 53 min.
- **Testador por tarefa segurando as três ondas da E06:** 15 a 17 min por onda.
- **Revisões fora das tarefas:** 15 min da dívida, 23 min de plano e revisão de arquitetura, 16 min de revisões finais.

### Limites desta medição

- Uma sessão só, e atípica: a E05 é etapa de gate (roteiro, pacote, verificação ao vivo) e a E06 é etapa de correção, com três revisões grandes no início.
- A comparação por etapa usa etapas de tamanho diferente; a E05 foi medida sem a Task 1, feita em sessão anterior.
- Os tempos vêm dos carimbos dos transcritos, e os comandos são classificados por expressão regular.
- Os defeitos do script que apareceram aqui (espera em segundo plano depois da entrega contada como ativa; `tarefas` e fração de testador) continuam sem correção.
