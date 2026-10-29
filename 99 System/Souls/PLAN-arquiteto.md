# Soul arquiteto e renomeação do orquestrador — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar as souls `arquiteto` e `revisor-arquitetura`, ligar a revisão de plano ao fluxo do orquestrador e renomear `orquestrador-etapa` para `orquestrador` no vault e no ZenyHotelManager.

**Architecture:**
- **Souls:** as duas souls novas são arquivos em `99 System/Souls/agents/`, com as travas no `soul_guard.py`: o papel novo `arquiteto` e o papel `revisor`, que já existe.
- **Revisão de plano:** fica só no `orquestrador.md`, e a `revisor-seguranca` confere a seção "Revisão de arquitetura" na revisão final.
- **Renomeação:** mantém `orquestrador-etapa` como alias histórico em `check_test_integrity.py`, porque o histórico do Zeny tem commits com esse trailer.

**Tech Stack:** Markdown com frontmatter de subagente do Claude Code; Python 3 só com a biblioteca padrão e `unittest`; Bash.

**Spec:** `99 System/Souls/DESIGN-arquiteto.md` (aprovado em 2026-10-29) e pedido do usuário de 2026-10-29: renomear `orquestrador-etapa` → `orquestrador` e, ao fim, fazer commit e push na branch principal (vault `master`; ZenyHotelManager `main`).

## Global Constraints

- Textos em português; corpo de cada soul ≤ 120 linhas, com as seis seções (Quem sou, O que prezo, O que recuso, Como trabalho, Como entrego, Quando paro e pergunto).
- Comando de hook: `python3 "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/second-brain-souls/scripts/soul_guard.py" <papel>`.
- Python 3 só com a biblioteca padrão; testes com `python3 -I -m unittest discover -s "99 System/Souls/tests"` e `python3 -I -m unittest discover -s "99 System/Skills/development-roadmap/tests"`.
- Nenhuma URL inventada.
- Commits só dos arquivos de cada tarefa, staged por caminho explícito; nada de `.obsidian/graph.json`, nem `00 Inbox/` (há uma captura pendente de outra sessão), nem `__pycache__`. Push só no fim (controlador).
- Os trailers `Soul: orquestrador`, `Soul: arquiteto` e `Soul: revisor-arquitetura` são válidos; `Soul: orquestrador-etapa` continua aceito como alias histórico.
- Proveniência: documentos históricos (`DESIGN.md`, `PLAN.md`, handoffs e histórico dos roadmaps) não são reescritos, só ganham uma nota da renomeação.

## Review Focus

- Escrita legítima do arquiteto num worktree nativo (`<repo>/.claude/worktrees/<n>/docs/adr/0001-x.md`, `api/openapi.yaml`) precisa passar (Task 2).
- `api/` como diretório ancestral fora do projeto não pode liberar YAML de código (por exemplo `/srv/api/proj/src/app.yaml` com o cwd no projeto) (Task 2).
- Um commit `Soul: orquestrador-etapa` antigo continua tratado como orquestrador, e não como `SOUL_DESCONHECIDA` (Task 1).
- A pré-condição do orquestrador exige o `revisor-arquitetura`; sem ele, a sessão para (Task 4).
- A revisão final bloqueia um plano sem a seção "Revisão de arquitetura" (Task 4).

---

### Task 1: Renomear `orquestrador-etapa` → `orquestrador` no vault

**Files:**
- Rename: `99 System/Souls/agents/orquestrador-etapa.md` → `99 System/Souls/agents/orquestrador.md` (`name: orquestrador`; a description e o corpo usam `claude --agent orquestrador`)
- Modify: `agents/scripts/check_test_integrity.py` (`KNOWN_SOULS` e a regra `ORQUESTRADOR_CODIGO`), `tests/test_souls_files.py`, `tests/test_check_test_integrity.py`, `tests/smoke_souls.sh`, `README.md`, as outras souls que citam o orquestrador
- Modify: `99 System/Skills/development-roadmap/SKILL.md`, `references/template.md`, `scripts/check_roadmap.py` (lista `SOULS`), `tests/test_check_roadmap_souls.py`
- Modify: `10 Projects/ZenyHotelManager.md` (linha de estado), `20 Knowledge/Souls - alma personalizada para cada agente de desenvolvimento.md` (texto atual + nota de revisão datada)
- Modify (nota no topo, sem reescrever): `99 System/Souls/DESIGN.md`, `99 System/Souls/PLAN.md` — "Em 2026-10-29 a soul `orquestrador-etapa` foi renomeada para `orquestrador`."

**Interfaces:**
- Produces:
  - `KNOWN_SOULS` contém `orquestrador` e o alias `orquestrador-etapa`;
  - `ORQUESTRADOR_CODIGO` vale para os dois trailers;
  - a soul responde por `name: orquestrador`.

- [ ] **Step 1: Escrever os testes que falham.**
  - `test_souls_files`: `SOULS` usa `"orquestrador": "orquestrador"`.
  - `test_check_test_integrity`: novo `test_alias_orquestrador_etapa`. Um commit `Soul: orquestrador-etapa` que toca `src/A.kt` dá `[ORQUESTRADOR_CODIGO]` e nenhum `SOUL_DESCONHECIDA`; um commit `Soul: orquestrador` que toca `src/A.kt` também dá `[ORQUESTRADOR_CODIGO]`.
- [ ] **Step 2:** rodar as duas suítes. Esperado: FAIL.
- [ ] **Step 3: Fazer a renomeação.** Usar `git mv` e substituir em todos os arquivos listados. Conferir com `grep -rn "orquestrador-etapa"` fora de `90 Archive/`, `DESIGN.md`, `PLAN.md`, `.git/` e do alias em `check_test_integrity.py`. Esperado: só ocorrências históricas declaradas, como a nota de revisão da nota de conhecimento.
- [ ] **Step 4:** rodar as suítes. Esperado: PASS. Conferir também que `~/.claude/agents/second-brain-souls/orquestrador.md` existe (o link aponta para a pasta).
- [ ] **Step 5: Commit** com a mensagem `Rename orquestrador-etapa soul to orquestrador`.

### Task 2: Papel `arquiteto` no guard e na verificação de integridade

**Files:**
- Modify: `99 System/Souls/agents/scripts/soul_guard.py`, `agents/scripts/check_test_integrity.py`
- Test: `tests/test_soul_guard.py`, `tests/test_check_test_integrity.py`

**Interfaces:**
- Produces:
  - `ROLES` inclui `arquiteto`;
  - `arquiteto_editavel(path: str, cwd: str | None = None) -> bool`;
  - para o papel `arquiteto`, `decide` bloqueia Edit/Write/MultiEdit/NotebookEdit quando `arquiteto_editavel` é falso no caminho normalizado **ou** no realpath. A regra é a mesma do orquestrador: proteção grudenta de `.claude`/`second-brain-souls` com o prefixo de worktree nativo consumido, diretório das souls, `CLAUDE_CONFIG_DIR` e `~/.claude`;
  - no Bash, o arquiteto bloqueia `git push` (§8 do design: o usuário faz o push);
  - em `check_test_integrity.py`: `KNOWN_SOULS` inclui `arquiteto` e `revisor-arquitetura`, e há a regra nova `[ARQUITETO_CODIGO]` para um commit `Soul: arquiteto` que toca caminho onde `arquiteto_editavel` é falso.

`arquiteto_editavel` é verdadeiro quando o caminho não é protegido e, nas partes de liberação (relativas ao cwd ou depois do prefixo de worktree, como `_partes_de_liberacao`):

- termina em `.md`, `.mmd`, `.puml`, `.plantuml` ou `.drawio` (sem diferenciar maiúsculas); **ou**
- termina em `.yaml`/`.yml` **e** tem um segmento `api` nas partes de liberação.

- [ ] **Step 1: Escrever os testes que falham** (`test_soul_guard.py::ArquitetoTest`).
  - Liberados, com cwd = `<repo>`: `docs/adr/0001-x.md`, `docs/diagramas/c4.mmd`, `docs/x.puml`, `docs/x.drawio`, `api/openapi.yaml`.
  - Liberados num worktree nativo: `<repo>/.claude/worktrees/w/docs/adr/0001-x.md` e `<repo>/.claude/worktrees/w/api/openapi.yaml`.
  - Bloqueados: `src/main/A.kt`, `build.gradle.kts`, `config/app.yaml` (YAML fora de `api/`), `/srv/api/proj/src/app.yaml` com cwd `/srv/api/proj`, `.claude/agents/x.md`, `<souls>/x.md`, `~/.claude/CLAUDE.md`, arquivo-symlink `docs/nota.md -> ../src/main/A.kt` (o realpath não termina em `.md`) e `git push` no Bash.
  - Liberado no Bash: `git log -5`.
  - `test_check_test_integrity.py::test_arquiteto_codigo`: commit `Soul: arquiteto` em `src/A.kt` → `[ARQUITETO_CODIGO]`, exit 1; em `docs/adr/0001.md` → exit 0, sem `SOUL_DESCONHECIDA`.
- [ ] **Step 2:** rodar a suíte. Esperado: FAIL.
- [ ] **Step 3:** implementar reaproveitando os helpers do orquestrador (`_scan`, `_partes_de_liberacao`, `_dentro_das_souls`, `_dentro_da_config`, `_real_e_cwd`).
- [ ] **Step 4:** rodar a suíte. Esperado: PASS.
- [ ] **Step 5: Commit** com a mensagem `Add arquiteto role to soul guard and integrity check`.

### Task 3: Souls `arquiteto` e `revisor-arquitetura`

**Files:**
- Create: `99 System/Souls/agents/arquiteto.md`, `99 System/Souls/agents/revisor-arquitetura.md`
- Modify: `tests/test_souls_files.py` (`"arquiteto": "arquiteto"`, `"revisor-arquitetura": "revisor"`)

Frontmatter:
- **arquiteto:**
  - `model: inherit`
  - `color: blue` (ou outra cor livre)
  - `tools: Agent(brain-escriba), Read, Grep, Glob, Bash, Edit, Write, Skill, AskUserQuestion, TodoWrite, ToolSearch, WebFetch, WebSearch`
  - hook `PreToolUse` com matcher `"Edit|Write|MultiEdit|NotebookEdit|Bash"` → `soul_guard.py arquiteto`
- **revisor-arquitetura:**
  - `tools: Read, Grep, Glob`
  - `model: inherit` (o orquestrador despacha no modelo mais capaz)
  - hook com matcher `"Bash"` → `soul_guard.py revisor`

Conteúdo obrigatório (DESIGN-arquiteto §1–§5):
- **arquiteto.md**, a única fonte da identidade:
  - a lente da §3 em "O que prezo";
  - o processo pelo `superpowers:brainstorming` e pelo `/development-roadmap`, sem substituí-los;
  - ADR com contexto, decisão, alternativas descartadas e consequências, em `docs/adr/NNNN-titulo.md` quando o projeto não tiver convenção;
  - captura das decisões pelo `brain-escriba`;
  - leitura direta do brain (caminho no bloco *Second Brain* de `~/.claude/CLAUDE.md`);
  - git conforme as regras do projeto fora de roadmap, commit só a pedido, sem worktree, trailer `Soul: arquiteto`;
  - para na spec ou no roadmap quando o brainstorming encaminhar para o `writing-plans`, e indica `claude --agent orquestrador`;
  - registro de projeto novo no brain fica numa sessão comum;
  - orientações mínimas de trabalho, porque roda como sessão principal;
  - "O que recuso": código, plano de etapa, `.claude/`, push.
- **revisor-arquitetura.md**, curto:
  - antes de revisar, lê as seções "O que prezo" e "O que recuso" de `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/second-brain-souls/arquiteto.md`;
  - julga o plano contra a spec ou a seção da etapa, a ARCHITECTURE e os ADRs recebidos como arquivos;
  - sem ARCHITECTURE nem ADRs, julga contra a spec e as convenções e registra a falta como nota, sem bloquear;
  - parecer: achados Críticos/Importantes/Menores, cada um com o trecho do plano e a decisão de arquitetura que o sustenta, e veredito aprovado / aprovado com notas / bloqueado;
  - nunca aprova sem citar evidência; não revisa código.

- [ ] **Step 1:** acrescentar as entradas em `SOULS` e rodar a suíte. Esperado: FAIL.
- [ ] **Step 2:** escrever as duas souls.
- [ ] **Step 3:** rodar a suíte. Esperado: PASS.
- [ ] **Step 4: Commit** com a mensagem `Add arquiteto and revisor-arquitetura souls`.

### Task 4: Revisão de plano no orquestrador e conferência na revisão final

**Files:**
- Modify: `99 System/Souls/agents/orquestrador.md`, `99 System/Souls/agents/revisor-seguranca.md`

No **orquestrador.md** (DESIGN-arquiteto §5):
- `tools: Agent(desenvolvedor, testador, revisor-seguranca, revisor-arquitetura, brain-escriba), …`;
- a pré-condição exige também o `revisor-arquitetura` (inclusive a checagem de agentes de projeto homônimos);
- passo novo entre o plano e a execução, em **todo** plano:
  - despacha o `revisor-arquitetura` no modelo mais capaz, com o plano, a spec ou a seção da etapa, a ARCHITECTURE e os ADRs como arquivos;
  - achado Crítico ou Importante bloqueia: o orquestrador corrige o plano e retoma o mesmo revisor (SendMessage) para a re-revisão, em até 2 rodadas (correção + re-revisão);
  - divergência persistente vira pergunta ao usuário e a etapa espera;
  - aprovado: grava a seção **"Revisão de arquitetura"** no plano (veredito, rodadas, modelo, notas Menores) e uma linha no ledger;
- o pacote da revisão final inclui o plano.

No **revisor-seguranca.md**: na revisão final, conferir que o plano tem a seção "Revisão de arquitetura" com veredito aprovado (ou aprovado com notas). Sem ela, bloqueia.

- [ ] **Step 1:** rodar a suíte (`test_souls_files`) antes. Esperado: PASS (base).
- [ ] **Step 2:** editar as duas souls. Corpos ≤ 120 linhas; se o orquestrador passar do limite, condensar sem perder regra.
- [ ] **Step 3:** `grep -n "revisor-arquitetura\|Revisão de arquitetura" agents/orquestrador.md agents/revisor-seguranca.md`. Esperado: pré-condição, Agent, passo novo, pacote final e conferência presentes. Rodar a suíte. Esperado: PASS.
- [ ] **Step 4: Commit** com a mensagem `Add plan review by revisor-arquitetura to the orchestrator`.

### Task 5: `development-roadmap` com o revisor de plano

**Files:**
- Modify: `99 System/Skills/development-roadmap/references/template.md`:
  - tabela de papéis: linha `| Revisor de plano | revisor-arquitetura, subagente novo por etapa, modelo mais capaz | revisão do plano antes da execução |`;
  - parágrafo "Souls": exige também o `revisor-arquitetura`;
  - passo 4 (Plano): o plano passa pela revisão de arquitetura do `orquestrador` antes da execução;
  - prompt de execução, passo 1: a pré-condição cita o `revisor-arquitetura`.
- Modify: `SKILL.md` §7 (papel novo e a soul `arquiteto` como sessão de desenho), `scripts/check_roadmap.py` (lista `SOULS` com `revisor-arquitetura`; continua aviso)
- Test: `tests/test_check_roadmap_souls.py`

- [ ] **Step 1: Escrever o teste que falha.** `test_protocolo_sem_revisor_arquitetura_avisa`: o esqueleto do template sem as linhas que citam `revisor-arquitetura` → a saída contém `não usa as souls`. `test_template_usa_souls` continua sem o aviso.
- [ ] **Step 2:** rodar. Esperado: FAIL.
- [ ] **Step 3:** editar o template, a SKILL e o `check_roadmap.py`; atualizar a mensagem do aviso para listar as cinco souls.
- [ ] **Step 4:** rodar. Esperado: PASS.
- [ ] **Step 5: Commit** com a mensagem `Add plan reviewer role to development-roadmap`.

### Task 6: Documentação e smoke

**Files:**
- Modify: `99 System/Souls/README.md` (tabela com as oito souls, uso do `claude --agent arquiteto`, fluxo desenho → execução), `99 System/Souls/DESIGN.md` (uma linha apontando para `DESIGN-arquiteto.md`), `20 Knowledge/Souls - ...md` (arquiteto e revisor de plano, com proveniência 2026-10-29), `99 System/Souls/tests/smoke_souls.sh`
- Commit também: `99 System/Souls/DESIGN-arquiteto.md`, `99 System/Souls/PLAN-arquiteto.md` (ainda não versionados)

- [ ] **Step 1:** acrescentar ao smoke os casos de bloqueio provado:
  - **arquiteto:** Write de `src/main/App.kt` → arquivo ausente + "Trava do" no log + run completo;
  - **arquiteto:** Write de `docs/adr/0001-teste.md` → arquivo presente;
  - **revisor-arquitetura:** `Bash` ausente no `system/init`.
- [ ] **Step 2:** `bash "99 System/Souls/tests/smoke_souls.sh"`. Esperado: todos PASS (custa tokens). Registrar a saída no relatório.
- [ ] **Step 3:** atualizar a documentação; conferir links (`ls` de cada alvo) e que não há `TODO`/`TBD`.
- [ ] **Step 4: Commit** com a mensagem `Document arquiteto souls and extend smoke test`.

### Task 7: ZenyHotelManager com o orquestrador renomeado e a revisão de plano

**Files (repositório `/home/caio/repos/ZenyHotelManager`):**
- Modify: `CLAUDE.md`, `docs/roadmaps/README.md`, `docs/roadmaps/roadmap-m{5..10}-*.md`. Mudar só "Como usar", "Protocolo de execução" e "Prompt de execução", alinhados ao template da Task 5:
  - `orquestrador-etapa` → `orquestrador`;
  - linha "Revisor de plano";
  - pré-condição com o `revisor-arquitetura`.

  Mais uma entrada datada no "Histórico de revisões" de cada roadmap. Handoffs e histórico existentes não mudam.

- [ ] **Step 1:** `git -C /home/caio/repos/ZenyHotelManager status` e `git fetch`. Esperado: `main` limpa e em dia com `origin/main`; se não estiver, parar e relatar.
- [ ] **Step 2:** aplicar as edições e rodar `python3 -I ~/.claude/skills/development-roadmap/scripts/check_roadmap.py` em cada roadmap. Esperado: nenhum erro e nenhum aviso `não usa as souls`.
- [ ] **Step 3:** `grep -rn "orquestrador-etapa" CLAUDE.md docs/roadmaps/`. Esperado: só ocorrências em handoffs ou no histórico (registro do que aconteceu).
- [ ] **Step 4:** commit (mensagem em português) com só esses arquivos: `Renomeia o orquestrador e inclui a revisão de plano nos roadmaps M5 a M10`. O push fica com o controlador, no fim.
