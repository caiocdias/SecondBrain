# Souls — ondas com fila de integração — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fazer uma rodada de 3 a 4 etapas do orquestrador caber em 4 a 6 horas, mantendo revisão, teste independente e gate verde, conforme o design aprovado.

**Architecture:**
- **Regras nas souls:** o gate completo sai dos agentes e passa ao orquestrador, uma vez por ponto de integração; o testador por tarefa fica restrito a uma lista fechada de riscos; o plano nasce com a seção `## Ondas`; a pergunta de arquitetura deixa de travar o lote. As regras de encaixe continuam só em `orquestrador.md`.
- **Medição:** o script que gerou a linha de base vira `agents/scripts/medir_sessao.py`, com as medidas que faltam e os padrões como parâmetro.
- **Verificação:** como o produto é prosa de soul, os testes fixam os termos e as regras que não podem sumir nem divergir entre souls. O comportamento real é conferido nas duas primeiras rodadas, pelos critérios da §7 do design.

**Tech Stack:** Markdown com frontmatter de subagente do Claude Code; Python 3 só com a biblioteca padrão e `unittest`; Bash.

**Spec:** `99 System/Souls/DESIGN-desempenho.md` (aprovado pelo usuário em 2026-11-17).

## Global Constraints

- Textos em português; corpo de cada soul ≤ 120 linhas, com as seis seções (Quem sou, O que prezo, O que recuso, Como trabalho, Como entrego, Quando paro e pergunto). O corpo do `orquestrador.md` tem 108 linhas: reescrever de forma compacta, editando os parágrafos existentes.
- Nenhum comando de projeto dentro das souls; frontmatter, ferramentas e hooks das souls não mudam. `soul_guard.py` e `check_test_integrity.py` não mudam.
- **Termos exatos**, iguais em todas as souls: `verificação da tarefa`, `verificação rápida`, `gate de integração`, `gate do projeto`, `## Ondas`, `entrevista de abertura do lote`.
- **Lista fechada de `Risco: alto`**, com estes seis itens escritos exatamente assim: `autenticação ou autorização`; `dado pessoal ou segredo`; `cálculo de valor monetário`; `migração ou escrita destrutiva de dados`; `concorrência`; `parsing de entrada externa não confiável`.
- **Contrato da verificação da tarefa:** os testes dos arquivos que a tarefa tocou e dos módulos que usam o que mudou, mais a compilação e o lint desses módulos; só compilação e lint não bastam. A linha `verificação rápida` do `CLAUDE.md` do projeto dá a forma do comando (com parâmetro de módulo e filtro de teste); sem ela, o agente monta o comando a partir das linhas de teste e lint.
- **Pontos do gate de integração** (gate do projeto completo, na branch da etapa): depois de cada onda de duas ou mais tarefas; para ondas de uma tarefa só, depois de até 3 tarefas integradas sem gate ou antes da próxima onda de duas ou mais; depois do testador de etapa e antes da revisão final; depois da onda única de correção e antes do merge na principal. Sem a linha `gate do projeto`, vale a suíte inteira.
- Não mudam: tamanho de tarefa (~45 min, 3 arquivos de produção), limite de 5 rodadas de correção, revisão do plano com até 2 rodadas, ordem do fim da etapa (testador de etapa → gate → scanner → revisão final → onda única de correção → resíduo).
- Python 3 só com a biblioteca padrão. Testes: `python3 -I -m unittest discover -s "99 System/Souls/tests"`, `python3 -I -m unittest discover -s "99 System/Skills/development-roadmap/tests"` e `bash "99 System/Souls/tests/test_sync_souls.sh"`.
- Trabalhar numa branch em worktree (`superpowers:using-git-worktrees`): `~/.claude/agents/second-brain-souls` aponta para o checkout principal, então as souls vivas só mudam no merge. Commits só dos arquivos de cada tarefa, staged por caminho explícito; nada de `.obsidian/graph.json`, `00 Inbox/` nem `__pycache__`. Mensagens em inglês, no estilo do histórico, terminando com `Co-Authored-By: Claude <noreply@anthropic.com>`. Merge local em `master` no fim; nunca `push`.
- Proveniência: `DESIGN.md` e `DESIGN-arquiteto.md` não são reescritos; só ganham nota.
- Nenhuma URL inventada.

## Review Focus

- Projeto sem as linhas `verificação rápida` e `gate do projeto` no `CLAUDE.md`: desenvolvedor, testador e orquestrador precisam dizer o que vale no lugar (Tasks 2 e 4).
- Gate vermelho numa onda de 3 tarefas sem dono evidente: o orquestrador precisa dizer como acha o dono (Task 4).
- Plano com tudo `Risco: normal` para fugir do testador: o `revisor-arquitetura` continua barrando `normal` em tarefa que toca a lista fechada (Task 3).
- Sessão sem subagentes ou sem nenhum `desenvolvedor`: o script não divide por zero (Task 1).
- Subagente retomado horas depois: o intervalo entre a entrega do relatório e a mensagem do coordenador não conta como tempo ativo (Task 1).

---

### Task 1: Script de medição `medir_sessao.py`

**Files:**
- Move: `99 System/Souls/medir_sessao.py` → `99 System/Souls/agents/scripts/medir_sessao.py` (o arquivo de origem ainda não está no git: `mv` e `git add` do destino)
- Create: `99 System/Souls/tests/test_medir_sessao.py`
- Modify: `99 System/Souls/README.md` (seção "Travas e scripts": um item para o script, com o comando de uso)

**Interfaces:**
- Consumes: nada.
- Produces:
  - `GATE_PADRAO = r"(?:\./gradlew|\bgradle)\s+build\b"`
  - `medir(path: str, gate_regex: str = GATE_PADRAO, build: dict[str, str] | None = None) -> dict`, com as chaves `relogio`, `sub_ativo`, `sub_soma`, `paralelismo`, `so_orquestrador`, `nada_rodando`, `espera_usuario`, `relogio_sem_usuario`, `tarefas`, `testadores`, `fracao_testador`, `gates`, `gates_por_tarefa`, `por_papel`. Tempos em segundos (float). `paralelismo`, `fracao_testador` e `gates_por_tarefa` são `None` quando o divisor é zero.
  - CLI: `medir_sessao.py [-q] [--gate-regex R] [--build NOME=REGEX ...] SESSAO.jsonl...`

Definições: `tarefas` = agentes `desenvolvedor` distintos (arquivos `subagents/agent-*.jsonl` cujo `.meta.json` traz `agentType: desenvolvedor`); `testadores` = idem para `testador`; `gates` = comandos `Bash`, em qualquer fluxo, cujo `command` casa com `gate_regex`; `espera_usuario` = tempo de ferramenta `AskUserQuestion` na sessão principal; `relogio_sem_usuario` = `relogio − nada_rodando − espera_usuario`. `build` substitui os padrões de `classify` (os atuais viram o padrão). As funções `analyze`, `union`, `subtract` e a saída impressa atual ficam como estão, para os números continuarem comparáveis com a linha de base.

- [ ] **Step 1: Escrever os testes que falham** em `tests/test_medir_sessao.py`. Cada teste monta, num diretório temporário, um `s.jsonl` e `s/subagents/agent-<id>.jsonl` com `.meta.json`, com registros mínimos (`type`, `timestamp`, `message` com `id`, `usage`, `content`). Importa o módulo com `sys.path.insert(0, str(AGENTS / "scripts"))`, como `test_souls_files.py`.
  - `test_paralelismo_e_tarefas`: dois `desenvolvedor` ativos 100 s cada, sobrepostos 50 s → `sub_soma == 200`, `sub_ativo == 150`, `paralelismo` ≈ 1,333 (`assertAlmostEqual`, 2 casas), `tarefas == 2`.
  - `test_gates_por_tarefa`: a principal roda `./gradlew build` uma vez; um dos dois `desenvolvedor` roda `./gradlew build --max-workers=2` duas vezes e `./gradlew :app:test --tests X` uma vez → `gates == 3`, `gates_por_tarefa == 1.5`.
  - `test_gate_regex_parametro`: um comando `pytest -q` → `gates == 0` com o padrão e `gates == 1` com `gate_regex=r"pytest -q$"`.
  - `test_fracao_testador`: 2 `desenvolvedor` e 1 `testador` → `fracao_testador == 0.5`.
  - `test_relogio_sem_usuario`: principal com prompt em t=0; assistente em t=10 com `tool_use` de `AskUserQuestion`; `tool_result` em t=310; assistente em t=320; novo prompt do usuário (texto) em t=520; assistente em t=530 → `relogio == 530`, `espera_usuario == 300`, `nada_rodando == 200`, `relogio_sem_usuario == 30`.
  - `test_sessao_sem_subagentes`: só a principal → `tarefas == 0`, `paralelismo is None`, `gates_por_tarefa is None`, `fracao_testador is None`, sem exceção.
  - `test_retomada_nao_conta_como_ativo`: um subagente com `tool_result` de entrega em t=100 e, em t=4000, um registro `user` de texto começando com `The coordinator sent a message`, seguido de assistente em t=4010 → o tempo ativo do subagente fica abaixo de 200 s.
  - `test_cli`: `python3 -I medir_sessao.py -q <s.jsonl>` sai com código 0 e a saída contém `gates por tarefa`.
- [ ] **Step 2: Rodar e ver falhar.** `python3 -I -m unittest discover -s "99 System/Souls/tests" -p "test_medir_sessao.py"` → erro de importação (o módulo ainda não está em `agents/scripts/`).
- [ ] **Step 3: Mover o script e implementar `medir`, `GATE_PADRAO`, os parâmetros da CLI e as linhas novas da saída** (`relógio sem usuário`, `gates por tarefa`, `testador por tarefa`). `main` passa a chamar `medir` e imprimir a partir do dicionário.
- [ ] **Step 4: Rodar e ver passar.** Mesmo comando do Step 2 → `OK`. Rodar também a suíte inteira das souls.
- [ ] **Step 5: Acrescentar o item do script ao `README.md`** ("Travas e scripts"): o que mede, que os padrões são parâmetros e o comando `python3 -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/second-brain-souls/scripts/medir_sessao.py" -q <sessão>.jsonl`.
- [ ] **Step 6: Commit** com a mensagem `Add session timing script for the souls`.

### Task 2: Verificação da tarefa no `desenvolvedor` e no `testador`

**Files:**
- Modify: `99 System/Souls/agents/desenvolvedor.md` ("Como trabalho" itens 2 e 7, "Como entrego")
- Modify: `99 System/Souls/agents/testador.md` ("Quem sou", "Como trabalho" itens 5 e 7, "Como entrego")
- Create: `99 System/Souls/tests/test_souls_desempenho.py`

**Interfaces:**
- Consumes: os termos e o contrato de Global Constraints.
- Produces: em `test_souls_desempenho.py`, o helper `corpo(nome: str) -> str` (corpo da soul sem o frontmatter) e a constante `LISTA_FECHADA` (tupla com os seis itens, na ordem de Global Constraints), que as Tasks 3 e 4 reutilizam.

- [ ] **Step 1: Escrever os testes que falham** (classe `TestVerificacaoDaTarefa`):
  - `test_desenvolvedor`: o corpo contém `verificação da tarefa` e `verificação rápida`; casa com `(?i)não rodo o gate`; contém `Sem a linha`; não contém `A suíte inteira roda uma vez` nem `saída real da suíte inteira`.
  - `test_testador`: o corpo contém `verificação da tarefa` e `verificação rápida`; casa com `(?i)não rodo o gate`; não contém `Rodo a suíte inteira no final`, `com foco nas tarefas que passaram sem mim` nem `saída real da suíte inteira`.
- [ ] **Step 2: Rodar e ver falhar.** `python3 -I -m unittest discover -s "99 System/Souls/tests" -p "test_souls_desempenho.py"` → 2 falhas.
- [ ] **Step 3: Reescrever os trechos do `desenvolvedor.md`.**
  - Item 2: teste focado a cada passo; antes de cada commit, os testes da área; antes do DONE e de devolver cada rodada, a verificação da tarefa, com o contrato de Global Constraints e a regra do "Sem a linha"; não roda o gate do projeto, que é do orquestrador na integração; a regra vale mesmo que o `CLAUDE.md` peça a suíte inteira antes de cada commit.
  - Item 7: a verificação da tarefa usa a fração de núcleos que o despacho indicar.
  - "Como entrego": comando e saída real da verificação da tarefa, colada.
- [ ] **Step 4: Reescrever os trechos do `testador.md`.**
  - "Quem sou": os três casos de despacho são tarefa `Risco: alto`, lacuna de teste apontada pela revisora e, uma vez por etapa, o diff inteiro antes da revisão final, cobrindo todas as tarefas.
  - Item 5: roda a verificação da tarefa no final; no despacho de etapa, o mesmo contrato sobre os módulos que a etapa tocou; não roda o gate do projeto.
  - Item 7 e "Como entrego": mesma troca do desenvolvedor; o status final passa a ser "testes verdes, ou vermelhos com os bugs listados".
- [ ] **Step 5: Rodar e ver passar**, e rodar `test_souls_files.py` (seis seções, ≤ 120 linhas).
- [ ] **Step 6: Commit** com a mensagem `Replace full-suite runs with task verification in desenvolvedor and testador`.

### Task 3: Achados novos no `revisor-arquitetura` e evidência no `revisor-seguranca`

**Files:**
- Modify: `99 System/Souls/agents/revisor-arquitetura.md` ("Como trabalho" item 3)
- Modify: `99 System/Souls/agents/revisor-seguranca.md` ("Como trabalho" itens 1 a 3, "Quando paro e pergunto")
- Modify: `99 System/Souls/tests/test_souls_desempenho.py`

**Interfaces:**
- Consumes: `corpo`, `LISTA_FECHADA` (Task 2).
- Produces: nada para as tarefas seguintes.

- [ ] **Step 1: Escrever os testes que falham** (classe `TestRevisores`):
  - `test_revisor_arquitetura_lista_fechada`: o corpo contém cada item de `LISTA_FECHADA`.
  - `test_revisor_arquitetura_achados_de_forma`: o corpo contém `## Ondas`; casa com `` (?s)`Risco: normal`.{0,200}Importante `` e com `` (?s)`Risco: alto` sem.{0,200}Importante ``; contém `Depende de`.
  - `test_revisor_seguranca_evidencia`: o corpo contém `verificação da tarefa` e `gate do projeto`.
- [ ] **Step 2: Rodar e ver falhar** → 3 falhas.
- [ ] **Step 3: Reescrever o item 3 do `revisor-arquitetura.md`.** Mantém o que já confere (tarefa sem `Estimativa`, `Depende de` ou `Risco`; acima de ~45 min ou de 3 arquivos de produção; tarefas da mesma onda que tocam o mesmo arquivo). Passam a ser achados Importantes:
  - `Risco: normal` em tarefa que toca um item da lista fechada (a lista substitui "entrada externa, concorrência, segurança, contrato ou persistência");
  - `Risco: alto` sem citar o item da lista que o justifica;
  - plano sem a seção `## Ondas`;
  - `Depende de:` declarado sem que a tarefa use símbolo ou arquivo que a outra cria.
- [ ] **Step 4: Ajustar o `revisor-seguranca.md`.**
  - Revisão de tarefa: a evidência de teste é a saída da verificação da tarefa no relatório; a saída do gate do projeto não é esperada por tarefa.
  - Revisão final: o pacote traz a saída do gate do projeto no HEAD revisado; sem ela, para e devolve ao orquestrador (acrescentar em "Quando paro e pergunto").
- [ ] **Step 5: Rodar e ver passar**, mais `test_souls_files.py`.
- [ ] **Step 6: Commit** com a mensagem `Teach reviewers the closed risk list, waves and task verification`.

### Task 4: Ondas, gate de integração e decisões no `orquestrador`

**Files:**
- Modify: `99 System/Souls/agents/orquestrador.md` ("O que recuso"; "Como trabalho" passos 1, 3, 3a e 5; "Registro"; "Decisões"; "Quando paro e pergunto")
- Modify: `99 System/Souls/tests/test_souls_desempenho.py`

**Interfaces:**
- Consumes: `corpo`, `LISTA_FECHADA` (Task 2).
- Produces: nada.

- [ ] **Step 1: Escrever os testes que falham** (classe `TestOrquestrador`):
  - `test_termos`: o corpo contém `gate de integração`, `gate do projeto`, `## Ondas`, `verificação da tarefa` e `entrevista de abertura do lote`.
  - `test_lista_fechada_igual_ao_revisor`: o corpo contém cada item de `LISTA_FECHADA`; não contém `o núcleo que a etapa existe para entregar`.
  - `test_gate`: não contém `rodo a suíte inteira uma vez`; contém `limites das tarefas`; casa com `(?i)sem (essa|a) linha.{0,80}suíte inteira`; contém `até 3 tarefas`.
  - `test_pergunta_nao_bloqueia`: casa com `(?is)AskUserQuestion.{0,300}(nada mais anda|fim do lote)`.
- [ ] **Step 2: Rodar e ver falhar** → 4 falhas.
- [ ] **Step 3: Reescrever os passos 1 e 3.**
  - Passo 1: `Risco: alto` só quando a tarefa toca um item da lista fechada, e o plano cita o item; o resto é `normal`. `Depende de:` só quando a tarefa usa símbolo ou arquivo que a outra cria. O plano traz a seção `## Ondas`: as ondas na ordem, com as tarefas de cada uma; contrato ou interface que várias tarefas usam vai numa tarefa da primeira onda.
  - Passo 3 e "O que recuso": onde hoje se lê suíte verde ou vermelha da tarefa, passa a valer a verificação da tarefa. O subpasso 2 continua: testador por tarefa só em `Risco: alto`.
- [ ] **Step 4: Reescrever o passo 3a.**
  - As ondas vêm da seção `## Ondas` do plano; limite de 3 por onda, redutível no prompt.
  - A revisora de cada tarefa é despachada assim que a tarefa fica verde; a integração continua em série, na ordem do plano e só com revisão limpa.
  - Gate de integração: o gate do projeto completo, na branch da etapa, nos pontos de Global Constraints; sem a linha `gate do projeto` no `CLAUDE.md`, a suíte inteira. Roda em segundo plano, com uma única espera. A onda seguinte só sai com o gate verde.
  - Gate vermelho: o dono é a tarefa cujo arquivo aparece no teste ou no erro (`git log` no intervalo da onda); sem dono evidente, rodar o gate nos limites das tarefas integradas. A correção volta ao desenvolvedor dono, na branch da etapa, como rodada de correção da tarefa.
  - No despacho de onda, a fração de núcleos vale para a verificação da tarefa.
- [ ] **Step 5: Reescrever o passo 5, "Registro", "Decisões" e "Quando paro e pergunto".**
  - Passo 5: o testador de etapa roda sempre, uma vez, sobre `MERGE_BASE..HEAD`, cobrindo todas as tarefas; teste vermelho segue o subpasso 3, como hoje. Depois vêm o gate de integração, o scanner e a revisão final; a saída do gate entra no pacote. Onda única de correção e resíduo não mudam.
  - "Registro": a linha de onda passa a `Onda <k>: tasks <N, M> → integrada <a7>..<b7>, gate <resultado>, <arquivo>`; linha nova `Gate: vermelho → dono Task <N> (<evidência>)`.
  - "Decisões": entrevista de abertura do lote (antes da primeira etapa, ler as seções das etapas que cabem no limite e as "Hipóteses e decisões em aberto"; as decisões de arquitetura previsíveis viram uma entrevista só). Durante o lote, a decisão de arquitetura vai para o handoff já em forma de entrevista com opção recomendada; o orquestrador segue no que não depende dela e, se a etapa não anda, marca `#bloqueada` e passa à próxima elegível. `AskUserQuestion` só quando nada mais anda ou no fim do lote.
  - "Quando paro e pergunto": coerente com o item acima.
- [ ] **Step 6: Rodar e ver passar**, mais `test_souls_files.py` (corpo ≤ 120 linhas).
- [ ] **Step 7: Commit** com a mensagem `Move the project gate to integration points and plan for waves in orquestrador`.

### Task 5: Documentos, skill `development-roadmap` e nota de conhecimento

**Files:**
- Modify: `99 System/Souls/README.md` (parágrafo de abertura, tabela das souls, "Como usar")
- Modify: `99 System/Souls/DESIGN-desempenho.md` (linha de status), `99 System/Souls/DESIGN.md` (nota no topo)
- Modify: `99 System/Skills/development-roadmap/references/brain.md` (item 3 do modelo do `CLAUDE.md`), `99 System/Skills/development-roadmap/SKILL.md` (parágrafo "Projeto sem código")
- Modify: `20 Knowledge/Souls - alma personalizada para cada agente de desenvolvimento.md`

**Interfaces:**
- Consumes: os termos de Global Constraints e o texto final das souls (Tasks 2 a 4).
- Produces: nada.

- [ ] **Step 1: `README.md` das souls.** O parágrafo de abertura cita também `DESIGN-desempenho.md`. Na tabela: `orquestrador` (ondas pela seção `## Ondas` do plano, gate de integração, entrevista de abertura do lote), `desenvolvedor` e `testador` (verificação da tarefa; testador por tarefa só na lista fechada e uma vez por etapa sobre o diff inteiro). "Como usar": uma linha sobre as duas linhas do `CLAUDE.md` do projeto (`verificação rápida`, `gate do projeto`) e o que vale sem elas.
- [ ] **Step 2: Notas de design.** Em `DESIGN-desempenho.md`, o status passa a "aprovado pelo usuário em 2026-11-17; a fonte da verdade são as souls em `agents/`". Em `DESIGN.md`, uma nota no topo, no formato da que já existe: em 2026-11-17 o ciclo por tarefa mudou (testador por tarefa só em lista fechada, gate do projeto na integração), ver `DESIGN-desempenho.md`. O corpo dos dois não é reescrito.
- [ ] **Step 3: Skill `development-roadmap`.**
  - `references/brain.md`, item 3: a tabela de comandos traz também duas linhas nomeadas, `verificação rápida` (forma de comando com parâmetro de módulo e filtro de teste, que roda os testes do que a tarefa tocou mais compilação e lint) e `gate do projeto` (o que precisa estar verde antes de integrar).
  - `SKILL.md`, "Projeto sem código (greenfield)": a primeira etapa registra também essas duas linhas.
  - Ler `references/template.md` e `scripts/check_roadmap.py` e confirmar que nada ali contradiz as souls novas; a leitura do design indica que não precisam mudar. Se contradisser, corrigir só a frase.
- [ ] **Step 4: Nota de conhecimento.** Acrescentar o bloco "Atualização (2026-11-17): desempenho da execução", no formato dos blocos anteriores, com os marcadores do design: meta de 4 a 6 horas e qualidade mantida **[usuário]**; abordagem B **[usuário]**; não adotar agora o desenho de um construtor por etapa **[usuário]**; lista fechada, pontos do gate, contrato da verificação da tarefa, ordem do fim da etapa e entrevista de abertura **[agente]**. Acrescentar a linha de proveniência: `2026-11-17 — sessão curadora; design em 99 System/Souls/DESIGN-desempenho.md, a partir da medição de cerca de 20 sessões do orquestrador`.
- [ ] **Step 5: Rodar as três suítes** de Global Constraints → todas `OK`.
- [ ] **Step 6: Commit** com a mensagem `Document the wave and integration-gate cycle`.

---

## Depois do plano (não são tarefas)

- O teste de fumaça `bash "99 System/Souls/tests/smoke_souls.sh"` chama o Claude de verdade e roda só à mão, depois do merge.
- Em cada repositório de projeto, na própria sessão: linha `verificação rápida` no `CLAUDE.md`, avaliação do gate e do build e, no DesktopFront, a decisão de revogar o ADR 0011 (design §6).
- Nas duas primeiras rodadas do orquestrador, medir com `medir_sessao.py` e comparar com a tabela da §7 do design.
