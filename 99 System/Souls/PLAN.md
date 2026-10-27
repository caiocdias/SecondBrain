# Souls — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar as seis souls (subagentes do Claude Code com identidade e travas reais), instalá-las a partir do vault e fazer a skill `development-roadmap` usá-las.

**Architecture:**
- Cada soul é um arquivo `.md` em `99 System/Souls/agents/`. Essa pasta inteira é ligada em `~/.claude/agents/second-brain-souls` pelo `sync-skills`.
- As travas que dependem só do caminho do arquivo ou do comando ficam num único script de hook, `soul_guard.py`, chamado pelo frontmatter de cada soul.
- As travas que dependem do histórico ficam em `check_test_integrity.py`, rodado pelo orquestrador a cada tarefa.

**Tech Stack:** Markdown com frontmatter de subagente do Claude Code; Python 3 só com a biblioteca padrão e testes com `unittest`; Bash e PowerShell (sync).

**Spec:** `99 System/Souls/DESIGN.md` (aprovado pelo usuário em 2026-10-27).

## Global Constraints

- Textos das souls e da documentação em português. Termos técnicos ficam em inglês quando esse é o nome real (TDD, supply chain, hook).
- Souls em `99 System/Souls/agents/<nome>.md`. Scripts dos hooks em `99 System/Souls/agents/scripts/`. Nenhum outro `.md` dentro de `agents/`: o Claude Code varre a pasta recursivamente e trataria esses arquivos como agentes.
- Link da máquina: `~/.claude/agents/second-brain-souls` → `<vault>/99 System/Souls/agents` (junction no Windows). Já verificado em 2026-10-27: o Claude Code encontra agentes através de uma pasta ligada por symlink no Linux.
- Comando de hook em todas as souls: `python3 "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/second-brain-souls/scripts/soul_guard.py" <papel>`. Nenhum caminho absoluto de máquina específica.
- Scripts em Python 3 usam só a biblioteca padrão e rodam com `python3 -I`. Testes com `python3 -I -m unittest`.
- Todo commit feito por uma soul leva o trailer `Soul: <nome-da-soul>`.
- Souls de desenvolvimento usam `model: inherit`. Quem escolhe o modelo é o orquestrador, no despacho, pela "Model Selection" do superpowers.
- Corpo de cada soul com no máximo 120 linhas, nas seções da DESIGN §3: Quem sou, O que prezo, O que recuso, Como trabalho, Como entrego, Quando paro e pergunto. A soul aponta para as fontes da verdade (AGENTS.md, `99 System/AI/`, skills do superpowers) e não copia regras delas.
- Nenhuma URL inventada: toda URL escrita numa soul ou documento é conferida com WebFetch antes do commit.
- Vault: executar no checkout principal (`master`), **não** num worktree, porque o `sync-skills` usa o caminho do próprio script e um worktree criaria links errados. Isso exige o consentimento explícito do usuário antes da Task 1. Commits só com a concordância do usuário. Nunca fazer `push`. Fazer stage apenas dos arquivos de cada tarefa: a árvore já tem alterações de outro trabalho (notas do ZenyHotelManager e `90 Archive/Inbox/`) que não podem entrar nos commits.

## Review Focus

- Caminhos com espaço (`99 System`, `00 Inbox`) nos comandos de hook, no sync e nos scripts precisam funcionar entre aspas (Task 1 testa o guard executado num caminho com espaço; Task 7 testa o sync com vault em caminho com espaço).
- O `file_path` recebido pelo hook pode ser absoluto ou relativo ao `cwd`. As duas formas devem ter a mesma decisão (Task 1).
- Arquivo de teste renomeado não pode virar "teste removido" (Task 2).
- A `tools` do orquestrador pode ter esquecido uma ferramenta de que o fluxo do superpowers precisa, como lista de tarefas, Skill ou worktree (Task 10, smoke do orquestrador).
- No Windows, a junction de `~/.claude/agents` e a paridade do `sync-skills.ps1` não podem ser testadas nesta máquina. Revisar à mão e registrar como pendência no README (Task 7).

---

### Task 1: `soul_guard.py` — script de hook das travas

**Files:**
- Create: `99 System/Souls/agents/scripts/soul_guard.py`
- Test: `99 System/Souls/tests/test_soul_guard.py`

**Interfaces:**
- Produces:
  - `is_test_path(path: str) -> bool`
  - `vault_root() -> pathlib.Path`, que é `Path(__file__).resolve().parents[4]`
  - `decide(role: str, tool_name: str, tool_input: dict, cwd: str, vault: Path) -> str | None`, que devolve a mensagem de bloqueio ou `None` para liberar
  - CLI `soul_guard.py <papel>`: lê o JSON do hook `PreToolUse` no stdin (`tool_name`, `tool_input`, `cwd`). Sai com 0 para liberar, ou com 2 e a mensagem em stderr para bloquear.
  - Papéis: `orquestrador`, `desenvolvedor`, `testador`, `revisor`, `escriba`, `curador`.

Regras de `decide` (caminho relativo é resolvido contra `cwd`):

| Papel | Ferramenta | Bloqueia quando |
|---|---|---|
| testador | Edit, Write, NotebookEdit | o caminho não é de teste |
| orquestrador | Edit, Write, NotebookEdit | o caminho não termina em `.md` e não está sob um diretório `.superpowers/` |
| escriba | Write | o caminho não está dentro de `<vault>/00 Inbox/` ou o arquivo já existe |
| escriba | Edit, NotebookEdit | sempre |
| escriba | Bash | o comando contém `>`, `;`, `&&`, `\|\|`, `\|`, `` ` `` ou `$(`, ou se o primeiro token não está em {`date`, `uuidgen`, `ls`, `pwd`}, exceto `git` com subcomando em {`log`, `status`, `show`, `diff`, `rev-parse`, `branch`} e `python3 -c` cujo código contenha `uuid` |
| revisor | Bash | redirecionamento de escrita (`>`/`>>` que não seja para `/dev/null` nem `2>&1`); `rm`, `mv`, `sed -i`, `tee`; `git` com subcomando em {`commit`, `push`, `reset`, `checkout`, `switch`, `merge`, `rebase`, `restore`, `clean`, `stash`, `tag`, `am`, `apply`, `cherry-pick`}; instalação (`npm/pnpm/yarn install\|add\|i`, `pip/pip3 install`, `brew/apt/apt-get/snap install`, `go install`, `cargo install`, `gem install`); `curl` ou `wget` com pipe para `sh`/`bash` |
| desenvolvedor, testador, escriba, revisor, curador | Bash | `git push` |
| curador | Bash | `git reset --hard`, `git clean -f`, `rm -rf` |

`is_test_path`: verdadeiro se algum segmento de diretório estiver em {`test`, `tests`, `__tests__`, `spec`, `specs`, `testing`, `androidTest`, `testFixtures`, `integrationTest`, `e2e`} ou se o nome do arquivo casar com `test_*.py`, `*_test.py`, `conftest.py`, `*_test.go`, `*.test.{js,jsx,ts,tsx,mjs,cjs}`, `*.spec.{js,jsx,ts,tsx,mjs,cjs}`, `*Test.{kt,java,scala,groovy}`, `*Tests.{kt,java,cs}`, `*IT.{kt,java}` ou `*_spec.rb`.

- [ ] **Step 1: Escrever os testes que falham.** `test_soul_guard.py` importa o script com `sys.path.insert` do diretório `agents/scripts`. Casos:
  - `test_is_test_path`: verdadeiro para `src/test/kotlin/br/x/RoomServiceTest.kt`, `tests/test_api.py`, `pkg/foo_test.go`, `web/src/App.test.tsx`, `src/__tests__/x.js`, `app/src/integrationTest/kotlin/A.kt`; falso para `src/main/kotlin/br/x/RoomService.kt`, `src/latest/x.py`, `contest.py`, `README.md`, `build.gradle.kts`.
  - `test_testador_bloqueia_producao`: `decide("testador","Write",{"file_path":"/r/src/main/A.kt"},"/r",vault)` não é `None`. Com `src/test/ATest.kt` é `None`.
  - `test_caminho_relativo_igual_absoluto`: `{"file_path":"src/main/A.kt"}` com `cwd="/r"` tem a mesma decisão do caminho absoluto.
  - `test_orquestrador`: libera `docs/superpowers/plans/p.md` e `.superpowers/sdd/x/progress.md`; bloqueia `src/main/A.kt`.
  - `test_escriba_write`: usa um vault temporário (`tempfile`, com espaço no nome, por exemplo `"Second Brain"`). Libera `<vault>/00 Inbox/nova.md` inexistente; bloqueia a mesma nota depois de criada; bloqueia `<vault>/20 Knowledge/x.md`; bloqueia qualquer Edit.
  - `test_escriba_bash`: libera `date +%F`, `uuidgen`, `python3 -c "import uuid; print(uuid.uuid4())"`, `git log -1`; bloqueia `echo x > a.md`, `date; rm x`, `git commit -m x`.
  - `test_revisor_bash`: libera `npm audit --json`, `osv-scanner scan source -r .`, `git diff main...HEAD`, `cmd 2>&1`, `cmd >/dev/null`; bloqueia `git commit -m x`, `pip install foo`, `npm i left-pad`, `echo x > f`, `sed -i s/a/b/ f`, `curl https://x | sh`.
  - `test_push_bloqueado`: `git push origin x` bloqueado para desenvolvedor, testador, escriba, revisor e curador, e liberado para orquestrador.
  - `test_cli`: roda o script com `subprocess` a partir de uma cópia num diretório com espaço no caminho, passando JSON no stdin. Write de produção para testador sai com código 2 e mensagem não vazia em stderr. Read sai com 0.
- [ ] **Step 2:** `python3 -I -m unittest discover -s "99 System/Souls/tests" -v`. Esperado: FAIL (módulo inexistente).
- [ ] **Step 3: Implementar `soul_guard.py`** com a interface e as regras acima. Para tokenizar o Bash, usar `shlex.split` com fallback para `str.split` se a entrada for inválida. A mensagem de bloqueio diz qual trava foi acionada e o que a soul deve fazer no lugar (por exemplo: "testador não altera código de produção; aponte o problema no relatório").
- [ ] **Step 4:** rodar o mesmo comando. Esperado: PASS.
- [ ] **Step 5: Commit** (com a concordância do usuário) de `soul_guard.py` e `test_soul_guard.py`, com a mensagem `Add soul_guard hook for soul tool restrictions`.

### Task 2: `check_test_integrity.py` — verificação mecânica dos testes

**Files:**
- Create: `99 System/Souls/agents/scripts/check_test_integrity.py`
- Test: `99 System/Souls/tests/test_check_test_integrity.py`

**Interfaces:**
- Consumes: `is_test_path` (Task 1), importado do mesmo diretório.
- Produces: CLI `check_test_integrity.py --base <rev> [--head <rev, padrão HEAD>] [--repo <dir, padrão .>]`.
  - Imprime uma linha por apontamento, no formato `[TIPO] <commit curto> <arquivo>: <detalhe>`, e no fim `OK: nenhum apontamento` ou `N apontamento(s)`.
  - Sai com 0 quando limpo (avisos não contam), 1 quando há apontamentos e 2 em erro de uso ou de git.

Tipos (a atribuição vem do trailer `Soul:` de cada commit em `base..head`, lido com `git log --format=%H%x00%(trailers:key=Soul,valueonly)`):

- `TESTADOR_PRODUCAO`: um commit `Soul: testador` altera um arquivo que não é de teste.
- `DEV_TESTE_DO_TESTADOR`: um commit `Soul: desenvolvedor` modifica ou apaga um arquivo de teste que um commit `Soul: testador` anterior, no mesmo intervalo, tinha tocado.
- `TESTE_REMOVIDO`: no diff `base..head` dos arquivos de teste, uma linha de declaração de teste foi removida e não reaparece entre as linhas adicionadas de *qualquer* arquivo de teste. A comparação é global, para que renomear não gere apontamento. Declaração: `@Test\b`, `^\s*def test_`, `^\s*(async\s+)?(it|test)\s*\(`, `^\s*func Test`.
- `ASSERCAO_REMOVIDA`: o mesmo critério global para linhas de asserção: `\bassert`, `\bexpect\s*\(`, `assertThat`, `\bverify\s*\(`, `\.should`.
- `SKIP_ADICIONADO`: linha adicionada com `@Disabled`, `@Ignore`, `pytest\.mark\.skip`, `@unittest\.skip`, `\b(it|test|describe)\.skip\s*\(`, `\bx(it|describe)\s*\(` ou `t\.Skip\(`.
- `SEM_SOUL` (aviso, não conta para o código de saída): commit sem trailer `Soul:`.

- [ ] **Step 1: Escrever os testes que falham.** Cada teste monta um repositório git temporário (`git init`, `user.name`/`user.email` locais) com commits de trailers definidos e roda o CLI via `subprocess`:
  - `test_limpo`: o desenvolvedor adiciona `src/main/a.py` e `tests/test_a.py` com `def test_x(): assert a()`, e o testador acrescenta `def test_y(): assert b()`. Esperado: saída 0, `OK: nenhum apontamento`.
  - `test_testador_producao`: commit `Soul: testador` altera `src/main/a.py`. Esperado: saída 1, linha `[TESTADOR_PRODUCAO]`.
  - `test_dev_altera_teste_do_testador`: o testador adiciona `tests/test_b.py` e depois um commit `Soul: desenvolvedor` o modifica. Esperado: `[DEV_TESTE_DO_TESTADOR]`.
  - `test_teste_removido` e `test_assercao_removida`: remover `def test_y` ou trocar `assert b()` por `pass`.
  - `test_rename_nao_acusa`: `git mv tests/test_a.py tests/test_a2.py` sem mudar o conteúdo. Esperado: nenhum `TESTE_REMOVIDO`.
  - `test_skip_adicionado`: adicionar `@pytest.mark.skip` acima de um teste.
  - `test_sem_soul_e_aviso`: commit sem trailer. Esperado: linha `[SEM_SOUL]` e saída 0.
- [ ] **Step 2:** `python3 -I -m unittest discover -s "99 System/Souls/tests" -v`. Esperado: FAIL nos testes novos.
- [ ] **Step 3: Implementar `check_test_integrity.py`.** Usar `git diff --no-renames -U0 base..head` para as linhas e `git show --name-status --no-renames <commit>` por commit, com `subprocess.run(["git", "-C", repo, ...])`.
- [ ] **Step 4:** rodar a suíte. Esperado: PASS.
- [ ] **Step 5: Commit** com a mensagem `Add test integrity check for soul-attributed commits`.

### Task 3: souls `desenvolvedor` e `testador`

**Files:**
- Create: `99 System/Souls/agents/desenvolvedor.md`, `99 System/Souls/agents/testador.md`
- Test: `99 System/Souls/tests/test_souls_files.py`

**Interfaces:**
- Produces: `test_souls_files.py` com o dicionário `SOULS = {nome: papel_do_guard}`. As tasks 4 a 6 acrescentam as suas entradas. Para cada soul, o teste confere:
  - o frontmatter entre `---` tem `name: <nome>` igual ao nome do arquivo e `description:` não vazia;
  - o comando de hook, quando existir, contém `soul_guard.py <papel>` e o prefixo `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/second-brain-souls/scripts/`;
  - o corpo tem os seis títulos `## Quem sou`, `## O que prezo`, `## O que recuso`, `## Como trabalho`, `## Como entrego` e `## Quando paro e pergunto`;
  - o corpo tem no máximo 120 linhas;
  - não há `.md` em `agents/` além das souls do dicionário.

Frontmatter:

```yaml
# desenvolvedor.md
name: desenvolvedor
description: Soul de desenvolvimento. Implementa uma tarefa de plano com TDD seguindo o prompt implementer do superpowers. Use como implementador em superpowers:subagent-driven-development, inclusive nas rodadas de correção de código.
disallowedTools: Agent
model: inherit
color: blue
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: python3 "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/second-brain-souls/scripts/soul_guard.py" desenvolvedor
```

```yaml
# testador.md
name: testador
description: Soul de testes. Depois de cada tarefa implementada, analisa, ataca e completa a suíte de testes sem tocar em código de produção. Use após o desenvolvedor em cada tarefa e depois de cada correção de código.
disallowedTools: Agent
model: inherit
color: yellow
hooks:
  PreToolUse:
    - matcher: "Edit|Write|NotebookEdit|Bash"
      hooks:
        - type: command
          command: python3 "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/second-brain-souls/scripts/soul_guard.py" testador
```

O conteúdo obrigatório do corpo vem da DESIGN §4 e §5:
- **desenvolvedor:**
  - TDD por `superpowers:test-driven-development`;
  - nunca altera nem apaga testes de commits `Soul: testador`: se discordar de um, aponta o problema no relatório e devolve ao orquestrador;
  - teste vermelho do testador = corrigir o **código**;
  - não adiciona nem atualiza dependências fora do que o plano pede;
  - trailer `Soul: desenvolvedor`.
- **testador:**
  - lê o diff da tarefa, os critérios de aceite e os testes existentes;
  - ataca casos de borda, erros, entradas inválidas, regressões e concorrência quando couber;
  - só acrescenta testes e nunca enfraquece, apaga ou pula os que existem;
  - nunca forja resultado (assert trivial, mock do próprio sistema testado, teste que não roda);
  - faz commit de teste vermelho que documenta bug, com a saída real no relatório;
  - roda a suíte inteira e cola a saída;
  - trailer `Soul: testador`.

- [ ] **Step 1:** escrever `test_souls_files.py` com `SOULS = {"desenvolvedor": "desenvolvedor", "testador": "testador"}`.
- [ ] **Step 2:** rodar a suíte. Esperado: FAIL (arquivos inexistentes).
- [ ] **Step 3:** escrever as duas souls.
- [ ] **Step 4:** rodar a suíte. Esperado: PASS. Em seguida, `mkdir -p ~/.claude/agents && ln -sfn "$PWD/99 System/Souls/agents" ~/.claude/agents/second-brain-souls` (o link definitivo vem do sync, na Task 7) e `claude -p --agent testador "Diga em uma frase qual é o seu papel." < /dev/null`. Esperado: resposta coerente com o papel de testador.
- [ ] **Step 5: Commit** com a mensagem `Add desenvolvedor and testador souls`.

### Task 4: soul `revisor-seguranca`

**Files:**
- Create: `99 System/Souls/agents/revisor-seguranca.md`
- Modify: `99 System/Souls/tests/test_souls_files.py` (entrada `"revisor-seguranca": "revisor"`)

Frontmatter:
- `name: revisor-seguranca`
- `tools: Read, Grep, Glob, WebFetch, WebSearch` (sem Bash — ruling da Task 1: o papel `revisor` do guard bloqueia todo Bash)
- `model: inherit`
- `color: red`
- hook `PreToolUse` com matcher `"Bash"` → `soul_guard.py revisor` (defesa em profundidade: bloqueia qualquer Bash)
- `description`: deixa claro que serve tanto para revisor de tarefa (prompt task-reviewer ou re-review do superpowers) quanto para a revisão final do branch (prompt `code-reviewer.md` do superpowers).

O conteúdo obrigatório do corpo vem da DESIGN §4, §5 e §6:
- segurança, boas práticas, aderência ao plano e integridade dos testes;
- trata cada apontamento de `check_test_integrity.py` como algo a justificar;
- na revisão final, olha o diff inteiro com ênfase em supply chain: dependências novas, typosquatting, versões com CVE, scripts de instalação, lockfile, segredos;
- **a revisão final exige scanner**: se nenhum estiver disponível para o stack, bloqueia e recomenda qual instalar, com o link oficial de instalação;
- não aprova sem evidência;
- nunca instala nada.

A revisora não executa nada: julga as saídas de scanner e de `check_test_integrity.py` que o orquestrador anexa ao pacote. Sem saída de scanner no pacote da revisão final → bloqueia e recomenda. Inclui uma tabela curta stack → scanner (com o comando que o orquestrador deve rodar) → URL oficial de instalação. Mínimo: multi-ecossistema (`osv-scanner`), npm (`npm audit`), Python (`pip-audit`) e JVM/Gradle.

- [ ] **Step 1:** acrescentar a entrada em `SOULS` e rodar a suíte. Esperado: FAIL.
- [ ] **Step 2: Conferir as URLs.** Abrir cada URL da tabela com WebFetch e confirmar que é a página oficial de instalação da ferramenta. Registrar no relatório da tarefa a URL e o título de cada página. URL que não confirmar sai da tabela.
- [ ] **Step 3:** escrever a soul.
- [ ] **Step 4:** rodar a suíte. Esperado: PASS.
- [ ] **Step 5: Commit** com a mensagem `Add revisor-seguranca soul`.

### Task 5: soul `orquestrador-etapa`

**Files:**
- Create: `99 System/Souls/agents/orquestrador-etapa.md`
- Modify: `99 System/Souls/tests/test_souls_files.py` (entrada `"orquestrador-etapa": "orquestrador"`)

Frontmatter:
- `name: orquestrador-etapa`
- `model: inherit`
- `color: purple`
- hook `PreToolUse` com matcher `"Edit|Write|NotebookEdit"` → `soul_guard.py orquestrador`
- `tools: Agent(desenvolvedor, testador, revisor-seguranca, brain-escriba), Read, Grep, Glob, Bash, Edit, Write, Skill, AskUserQuestion, TodoWrite, ToolSearch, EnterWorktree, ExitWorktree, WebFetch`

O corpo é o único lugar com as regras de encaixe (DESIGN §5) e precisa funcionar com ou sem roadmap:
- **pré-condição:** a sessão roda como `orquestrador-etapa` e as outras souls existem. Se não, para e avisa, sem fallback.
- **planejamento:** faz o plano com `superpowers:writing-plans` e executa com `superpowers:subagent-driven-development`. O caminho inline (`executing-plans`) não vale.
- **mapeamento de despacho:**
  - implementer e correções de código → `desenvolvedor`;
  - depois de cada tarefa e depois de cada correção que mexe em produção → `testador`;
  - em seguida, roda `python3 -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/second-brain-souls/scripts/check_test_integrity.py" --base <commit anterior à tarefa>` e anexa a saída ao pacote de revisão;
  - task-reviewer e re-review → `revisor-seguranca`;
  - revisão final (prompt `code-reviewer.md`) → `revisor-seguranca`, com o modelo mais capaz; antes, o orquestrador roda o scanner de dependências do stack (tabela da soul `revisor-seguranca`) e anexa a saída ao pacote; sem scanner instalado, anexa essa ausência e a revisora bloqueia;
  - a revisora não tem Bash: tudo o que ela precisa ver (diff, saídas de scanner, de testes e da verificação mecânica) vai como arquivo no pacote;
  - captura no brain → `brain-escriba`.
- **teste vermelho do testador** (DESIGN §5): volta ao desenvolvedor, conta no limite de 5 rodadas, e a revisão só acontece com a suíte verde.
- não escreve código nem teste;
- registra no ledger cada despacho e o resultado da verificação mecânica;
- trailer `Soul: orquestrador-etapa` nos próprios commits;
- leva ao usuário, como entrevista com opção recomendada, só o que o protocolo manda ([[Decidir pendências do usuário por entrevista com opção recomendada]]).

- [ ] **Step 1:** acrescentar a entrada e rodar a suíte. Esperado: FAIL.
- [ ] **Step 2:** escrever a soul.
- [ ] **Step 3:** rodar a suíte. Esperado: PASS.
- [ ] **Step 4: Commit** com a mensagem `Add orquestrador-etapa soul`.

### Task 6: souls `brain-escriba` e `brain-curador`

**Files:**
- Create: `99 System/Souls/agents/brain-escriba.md`, `99 System/Souls/agents/brain-curador.md`
- Modify: `99 System/Souls/tests/test_souls_files.py` (entradas `"brain-escriba": "escriba"` e `"brain-curador": "curador"`)

Frontmatter:
- **brain-escriba:**
  - `tools: Read, Grep, Glob, Write, Bash`
  - `model: inherit`
  - `color: green`
  - hook com matcher `"Write|Edit|NotebookEdit|Bash"` → `soul_guard.py escriba`
- **brain-curador:**
  - sem `tools`, para herdar todas;
  - `model: inherit`
  - `color: cyan`
  - hook com matcher `"Bash"` → `soul_guard.py curador`

O conteúdo obrigatório do corpo:
- **brain-escriba:**
  - descobre o vault pelo bloco *Second Brain* de `~/.claude/CLAUDE.md`;
  - segue `AGENTS.md`, `99 System/AI/external-agents.md`, `ingestion.md` e `schemas.md`, sem copiar o conteúdo deles;
  - consulta seguindo `retrieval.md`;
  - captura só arquivos novos, nunca sobrescreve;
  - devolve o caminho da captura criada.
- **brain-curador:**
  - opera como curador conforme `AGENTS.md`: a Inbox é processada com a skill `processar-inbox` e a manutenção segue `maintenance.md`;
  - mudanças estruturais, de schema ou de regra viram proposta, conforme `mutation-policy.md`;
  - commit só com concordância e nunca `push`;
  - como o corpo substitui o system prompt padrão quando roda como sessão principal, inclui orientações mínimas de trabalho: ser conciso, usar as ferramentas dedicadas e relatar com fidelidade.

- [ ] **Step 1:** acrescentar as entradas e rodar a suíte. Esperado: FAIL.
- [ ] **Step 2:** escrever as duas souls.
- [ ] **Step 3:** rodar a suíte. Esperado: PASS.
- [ ] **Step 4: Commit** com a mensagem `Add brain-escriba and brain-curador souls`.

### Task 7: instalação — sync, setup e scanners

**Files:**
- Modify: `99 System/Skills/sync-skills.sh`, `99 System/Skills/sync-skills.ps1`
- Modify: `99 System/AI/setup.md` (tabela "O que fica onde", "Detecção", novo passo "Souls e scanners", "Verificação")
- Modify: `.claude/skills/configurar-maquina/SKILL.md` (passo 5 menciona souls e scanners; a `description` passa a citar as souls)
- Test: `99 System/Souls/tests/test_sync_souls.sh`

**Interfaces:**
- O sync garante o link `$CONFIG_DIR/agents/second-brain-souls` → `<vault>/99 System/Souls/agents`, onde `<vault>` é o pai de `VAULT_SKILLS` (`VAULT_SOULS="$(dirname "$VAULT_SKILLS")/Souls/agents"`).
  - link apontando para outro lugar, ou diretório real nesse nome → entra em `conflicts` e não é alterado;
  - link criado → mensagem `Souls do Second Brain ativadas.`;
  - sem `99 System/Souls/agents` → não faz nada.
- O `.ps1` faz o mesmo com junction.

- [ ] **Step 1: Escrever o teste que falha.** `test_sync_souls.sh` copia `99 System/Skills` e `99 System/Souls/agents` para um vault temporário com espaço no caminho, roda o sync com `CLAUDE_CONFIG_DIR=<tmp>/cfg` e confere três coisas:
  - `readlink <tmp>/cfg/agents/second-brain-souls` é igual ao caminho de `Souls/agents` copiado;
  - uma segunda execução não emite `Souls do Second Brain ativadas`;
  - com o link apontando para outro destino, a saída contém `Conflito`.

  O teste sai com status diferente de zero em qualquer falha.
- [ ] **Step 2:** `bash "99 System/Souls/tests/test_sync_souls.sh"`. Esperado: FAIL.
- [ ] **Step 3:** implementar o bloco no `.sh` e o equivalente no `.ps1` (`New-Item -ItemType Junction`), seguindo o estilo de cada arquivo.
- [ ] **Step 4:** rodar o teste. Esperado: PASS. Depois, rodar o sync real (`"99 System/Skills/sync-skills.sh"`), conferir o link em `~/.claude/agents/` e remover o link manual da Task 3, se o sync não o tiver substituído.
- [ ] **Step 5: Documentar.**
  - Atualizar `setup.md` e `configurar-maquina`. O passo de scanners instala ou confere o `osv-scanner` pelo método da documentação oficial (URL conferida com WebFetch), **com confirmação do usuário** antes de instalar, como já é a regra do setup.
  - A "Verificação" do setup passa a incluir `ls ~/.claude/agents/second-brain-souls/` e `osv-scanner --version`.
  - Registrar no README das souls (Task 9) que o `.ps1` não foi testado no Windows.
- [ ] **Step 6: Instalar o scanner nesta máquina.** Perguntar ao usuário com AskUserQuestion, com o método oficial recomendado. Instalar só se ele aprovar e conferir com `osv-scanner --version`. Se ele recusar, anotar no relatório.
- [ ] **Step 7: Commit** com a mensagem `Link souls into ~/.claude/agents and add scanner setup`.

### Task 8: `development-roadmap` passa a usar as souls

**Files:**
- Modify: `99 System/Skills/development-roadmap/SKILL.md` (§7 "Papéis e Souls")
- Modify: `99 System/Skills/development-roadmap/references/template.md`:
  - "Como usar": iniciar com `claude --agent orquestrador-etapa`;
  - tabela de papéis → papel/soul;
  - o parágrafo "Souls: nenhuma definida…" é substituído pela pré-condição sem fallback;
  - "Por etapa", passo 5: execução pelas souls, com remissão ao `orquestrador-etapa` e sem repetir as regras de encaixe;
  - bloco "Second Brain": captura via `brain-escriba`;
  - "Prompt de execução", passo 1: conferir a pré-condição.
- Modify: `99 System/Skills/development-roadmap/scripts/check_roadmap.py:278-279`
- Test: `99 System/Skills/development-roadmap/tests/test_check_roadmap_souls.py`

**Interfaces:**
- `check_roadmap.py`: o aviso `"o protocolo de execução não traz a tabela de papéis com a nota sobre Souls"` é trocado pelo aviso `"o protocolo de execução não usa as souls (orquestrador-etapa, desenvolvedor, testador, revisor-seguranca)"`, emitido quando algum desses quatro nomes falta no corpo do protocolo. Continua sendo aviso, para não quebrar roadmaps antigos.

- [ ] **Step 1: Escrever os testes que falham.** O teste extrai o esqueleto do `template.md` (bloco ` ````markdown `), grava como `roadmap-teste.md` num diretório temporário e roda `python3 -I check_roadmap.py <arquivo>` via `subprocess`. Casos:
  - `test_template_usa_souls`: a saída **não** contém `não usa as souls`;
  - `test_protocolo_sem_souls_avisa`: no mesmo esqueleto, sem as linhas que citam `testador`, a saída contém `não usa as souls`.
- [ ] **Step 2:** `python3 -I -m unittest discover -s "99 System/Skills/development-roadmap/tests" -v`. Esperado: FAIL em `test_template_usa_souls`.
- [ ] **Step 3:** editar o `template.md`, a `SKILL.md` e o `check_roadmap.py` conforme os itens acima.
- [ ] **Step 4:** rodar os testes. Esperado: PASS.
- [ ] **Step 5: Commit** com a mensagem `Make development-roadmap execute stages through souls`.

### Task 9: documentação do vault

**Files:**
- Create: `99 System/Souls/README.md`, guia do usuário no estilo de `99 System/Skills/README.md`, com:
  - o que é uma soul;
  - a tabela das seis souls;
  - como usar (`claude --agent orquestrador-etapa`, `claude --agent brain-curador`);
  - como criar uma soul nova;
  - travas e scripts;
  - pendência: Windows não testado.
- Modify: `99 System/AI/architecture.md`: linha `99 System/Souls/` na tabela de pastas, com o mesmo tratamento de `99 System/Skills/` (fora de buscas e do processamento).
- Modify: `AGENTS.md`: uma linha em "Convenções rápidas", logo depois da linha de Skills.
- Modify: `20 Knowledge/Souls - alma personalizada para cada agente de desenvolvimento.md`:
  - "Explicação" passa a refletir a implementação;
  - as perguntas em aberto ganham respostas, marcando o que foi decisão do usuário e o que foi escolha do agente;
  - linha de proveniência `2026-10-27 — sessão curadora; design em 99 System/Souls/DESIGN.md`;
  - preservar o texto e a proveniência que já existem.

- [ ] **Step 1:** escrever e editar os quatro arquivos.
- [ ] **Step 2: Conferir os links.** Todo `[[...]]` novo aponta para uma nota existente (`ls` de cada alvo). Não restam `TODO` nem `TBD` (`grep -n "TODO\|TBD"` nos arquivos tocados não retorna nada).
- [ ] **Step 3: Commit** com a mensagem `Document souls in the vault`.

### Task 10: validação ponta a ponta das travas

**Files:**
- Create: `99 System/Souls/tests/smoke_souls.sh`. Script manual (não roda no `unittest`): cria um repositório git descartável no scratchpad e executa cada soul com `claude -p --agent <soul> --permission-mode bypassPermissions "<pedido>" < /dev/null`. O resultado é conferido no **sistema de arquivos e no git**, nunca pelo texto da resposta.

- [ ] **Step 1: Escrever o script** com os casos abaixo. Cada caso imprime `PASS` ou `FAIL`, e o script sai com status diferente de zero se houver algum `FAIL`.
  1. `testador`, pedido para criar `src/main/App.kt` → o arquivo não existe.
  2. `testador`, pedido para criar `src/test/AppTest.kt` → o arquivo existe.
  3. `revisor-seguranca`, pedido para rodar `git commit --allow-empty -m x` → o número de commits não muda.
  4. `orquestrador-etapa`, pedido para criar `src/main/App.kt` → o arquivo não existe.
  5. `orquestrador-etapa`, pedido para listar as ferramentas disponíveis e dizer se consegue despachar `general-purpose` → a resposta não traz `general-purpose` entre os tipos despacháveis (conferido com grep na resposta; é o único caso conferido por texto e fica marcado como tal).
  6. `brain-escriba`, pedido para criar `<scratch>/fora.md` → o arquivo não existe.
- [ ] **Step 2:** `bash "99 System/Souls/tests/smoke_souls.sh"`. Esperado: todos `PASS`. Se o caso 5 mostrar que falta ferramenta para o fluxo do superpowers, corrigir a `tools` do orquestrador (Task 5) e rodar de novo.
- [ ] **Step 3:** rodar a suíte inteira:

  ```bash
  python3 -I -m unittest discover -s "99 System/Souls/tests" -v
  python3 -I -m unittest discover -s "99 System/Skills/development-roadmap/tests" -v
  ```

  Esperado: PASS.
- [ ] **Step 4: Commit** com a mensagem `Add end-to-end smoke test for soul guards`.
