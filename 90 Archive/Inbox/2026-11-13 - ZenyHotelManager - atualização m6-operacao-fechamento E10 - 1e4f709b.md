---
type: capture
status: archived
created: 2026-11-13
capture_id: 1e4f709b-7bbd-4c39-9725-1926aef1ca98
---
# ZenyHotelManager - atualização m6-operacao-fechamento E10

## Conteúdo capturado

Captura de fechamento da etapa M6 E10 (motor do fechamento do dia), concluída em 2026-11-13 na branch `roadmap/m6-operacao-fechamento`. Resumo do agente a partir do relato do orquestrador do lote; organizada por nota de tema, dizendo se **substitui** ou **complementa** cada trecho. Vale sobre as capturas pendentes quando tratarem do mesmo assunto.

### 1. Estado: `ZenyHotelManager - Estado por marco` e Estado do hub `10 Projects/ZenyHotelManager.md` (substitui o Estado do M6)

- **M6 E10 `#concluida` em 2026-11-13**; Revisão humana: **sim** (o lote parou nela). Demais etapas do M6 seguem `#pendente`. Próxima elegível: E11 (etapas financeiras e operacionais do fechamento, Revisão humana: sim), depois E14, E15, E16, E17, E01 e seguintes.
- Revisão de arquitetura do plano: aprovada na rodada 2 (`revisor-arquitetura`). Revisão final do branch: aprovada com ressalvas (0 Critical); onda única de correção feita (artefato `.superpowers` tirado do git; teste da `main` sem etapas).
- Evidência: `./gradlew build` BUILD SUCCESSFUL (3604 testes, 0 falhas, no gate anterior à onda final; o gate no HEAD que entra consta na resposta do orquestrador); oasdiff sem `ERR`; `osv-scanner` 0 Critical/High (5 Medium/Low pré-existentes: commons-lang3 3.16.0 no buildscript, logback-core 1.3.16 em 3 ocorrências, opentelemetry-api 1.62.0).
- **Hub, "Notas do projeto" → "Módulos" (complementa):** `- [[ZenyHotelManager - Módulo endofday]]: fechamento do dia, motor de etapas, execuções, pendências e gatilho automático.`

### 2. Nota nova proposta: `ZenyHotelManager - Módulo endofday`

- **Módulo** `com.zeny.hotel.endofday` (camada Operação), `allowedDependencies = ["shared", "hotel", "notifications"]` (subconjunto da linha da ARCHITECTURE §3.1; a E11 acrescenta `reservations`, `rooms`, `billing` e `payments` e muda o `ModularityTest`, que exige igualdade exata).
- **Schema** `endofday`: `run` (UNIQUE `run_business_date_uk`: uma execução por data), `run_step` (PK `(run_id, name)`, posição única por execução), `run_issue`; FKs para `run`; `CHECK` de status; `finished_at` presente se e somente se o status não é RUNNING. Grants ao `zeny_app`: `SELECT, INSERT, UPDATE` (sem `DELETE`; `DatabaseRolesTest` tem `NO_DELETE_TABLES`). Migrações `endofday/V2026_11_12_1000__create_endofday_tables.sql` e `V2026_11_12_1001__grant_endofday_to_app_role.sql`. **A próxima migração do projeto precisa de versão posterior a `V2026_11_12_1001`.**
- **Agregado** `EndOfDayRun` (status RUNNING/FAILED/COMPLETED; etapas PENDING/RUNNING/COMPLETED/FAILED/SKIPPED). `beginNext` reconcilia com o registro de etapas antes de escolher: etapa não concluída que saiu do registro vira SKIPPED com pendência `STEP_UNREGISTERED`; etapa nova entra se a posição for maior que a da última concluída; sem etapa restante, a execução conclui. Toda transição muda `updatedAt` (a versão sobe). Trava da linha por `SELECT … FOR NO KEY UPDATE` nativo (não `FOR UPDATE`, que travaria pela FK o INSERT de pendência numa transação `REQUIRES_NEW`); exige transação (`MANDATORY`).
- **Contrato de etapa** (`application/EndOfDaySteps.kt`, KDoc obrigatório para E11 e E13): `EndOfDayStepHandler(name, position, execute(context))`. Roda na transação que marca a etapa concluída; é idempotente pela **data** (nunca pelo `runId`); item que tolera falha roda em `REQUIRES_NEW` por outro bean, sem alterar a linha da execução; a pendência da falha do item é levantada na transação da etapa; exceção que escapa desfaz tudo, inclusive pendências e avisos (as transições usam `rollbackFor = Throwable`); capturar exceção de bean `REQUIRED` deixa a transação rollback-only; efeito externo (S3) tem de ser idempotente; nomes são estáveis como códigos (renomear ou remover a etapa de avanço da data é proibido); posições de 100 em 100 na ordem da RF-FEC-02. O registro (`EndOfDayStepRegistry`) recusa nome ou posição repetidos no boot.
- **Transições auditadas** (`EndOfDayRunTransitions`, ator sistema): `begin(runId)`, `complete(runId, step, attempts, work)` e `fail(runId, step, attempts, reason)`, que conferem sob a trava a mesma tentativa (corrida perdida devolve `false` ou `Busy`). Motivo da falha = `ErrorCode` da `DomainException` ou nome da classe, nunca a mensagem.
- **Motor** (`EndOfDayEngine`): trava ShedLock `end-of-day-run` com `KeepAliveLockProvider` (`zeny.endofday.lock-at-most-for` PT5M; mínimo 30 s) sobre o `LockProvider` do `shared`; executor de **uma** thread `end-of-day` (sem contexto de segurança: etapas sempre com ator sistema); `execute(runId, waitAtMost)` devolve `Finished`, `Busy` ou `StillRunning`. `Error` numa etapa vira `FAILED` (só `VirtualMachineError` não-StackOverflow escapa e deixa RUNNING); falha fora das etapas é logada em ERROR só pela classe. Executores com `@Bean(defaultCandidate = false)` + `@Qualifier` (não desligam `applicationTaskExecutor` nem `taskScheduler` do Boot).
- **Pendências** (`EndOfDayIssues`): grava e chama `NotificationsApi.notify(notifications.end-of-day-pending, "Pendência no fechamento de dd/MM/yyyy", "<kind>: <reference ou —>", withPermission(endofday.runs.read))` na mesma transação; nunca a `message`.
- **Tempo real**: tópico `end-of-day` (permissão `endofday.runs.read`), mensagem `endofday.run` (`id` = execução, `version` gravada), publicada em toda transição que muda a execução, na criação e na retomada.
- **Permissões**: `endofday.runs.read` (ALL; Gerente, Recepcionista, Financeiro) e `endofday.runs.execute` (ALL, **sensível**; Gerente). `AuthorizationTest` (lista exata do Gerente) atualizado.
- **API** (`EndOfDayController`, tag `end-of-day`):
  - `POST /api/v1/end-of-day/runs` `{businessDate}` (`@Idempotent`, step-up `endofday.run.start` / `endofday.business-date:<data>`): `201` síncrono, com espera `zeny.endofday.manual-wait` PT30S, devolvendo a execução **no estado em que estiver** (RUNNING inclusive).
  - `POST …/runs/{id}/resume` (`@Idempotent`, step-up `endofday.run.resume` / `endofday.run:<id>`, sem `If-Match`, exceção registrada): `200`.
  - `GET …/runs` (cursor), `GET …/runs/{id}` (`ETag`), `GET …/runs/{id}/issues` (cursor).
  - Códigos: `END_OF_DAY_RUN_NOT_FOUND` (404); 409 `END_OF_DAY_ALREADY_CLOSED`, `END_OF_DAY_RUN_EXISTS` (leva `runId`, que pode vir nulo na corrida perdida), `END_OF_DAY_DATE_MISMATCH` (leva `currentBusinessDate`; datas fora do alcance do `date` do PostgreSQL também), `END_OF_DAY_NOT_CONFIGURED` (registro vazio), `END_OF_DAY_RUN_NOT_RESUMABLE`, `END_OF_DAY_RUN_IN_PROGRESS`. Autorização sempre antes de qualquer checagem que revele estado. Cursor de pendências com instante fora do `timestamptz` devolve `400 INVALID_CURSOR`.
  - As consultas ficam em `application/EndOfDayQueries.kt`; a camada web só vê `EndOfDayRunView` e enums espelho com `@ExtensibleEnum`.
- **Gatilho automático**: `EndOfDaySchedule.dueAt(businessDate, endOfDayTime, zone)`: horário antes de 12:00 vence no dia seguinte; 12:00 ou depois, no próprio dia; no fuso do hotel. `EndOfDayTrigger.tick()` decide nesta ordem: `NOT_DUE`, `NO_STEPS` (registro vazio; nenhum aviso), `OUTSIDE_WINDOW` (depois de `zeny.endofday.trigger.catch-up-window`, PT24H, validada no boot até P7D: nada roda sozinho, aviso uma vez por data e processo "execute ou retome manualmente"); senão cria (`createAutomatic`, ator sistema) ou retoma a RUNNING interrompida. `FAILED` espera a retomada manual; `COMPLETED` devolve `ALREADY_CLOSED`; corrida perdida na criação é tratada. Job `EndOfDayTriggerJob` (`end-of-day-trigger`, `interval` PT1M) loga só a classe da exceção.
- **Métricas e alertas**: Timer `zeny.endofday.run.duration` (tags `outcome`, `resumed`), Counter `zeny.endofday.run.failures`, gauges `zeny.endofday.runs.failed` e `zeny.endofday.overdue.seconds` (0 antes do horário e com o registro vazio; NaN se a leitura falhar; refresh `zeny.endofday.metrics.refresh-interval` PT30S). Regras novas no grupo `zeny-end-of-day` de `docker/prometheus/alerts.yaml`: `ZenyEndOfDayFailed`, `ZenyEndOfDayNotRun` (> 3600 s), `ZenyEndOfDayMetricsUnavailable` (`promtool`: 8 regras OK). A entrega dos alertas é da M8 E18.
- **Entre a E10 e a E11 (a `main` agora)**: nenhuma etapa real registrada; `POST /runs` devolve 409 `END_OF_DAY_NOT_CONFIGURED`; o gatilho devolve `NO_STEPS` (um WARN por data), sem aviso; métricas zeradas, sem alerta. Provado por `EndOfDayNoStepsProductionTest`.

### 3. `ZenyHotelManager - Testes de integração` (complementa)

- **H10 decidida (mecanismo):** `@EndOfDayIntegrationTest` (`testsupport/EndOfDayIntegrationTest.kt`) tem as mesmas propriedades e inicializadores do `@IntegrationTest`, mas liga ao banco próprio `zeny_endofday` no mesmo container PostgreSQL (criado uma vez por JVM, com as mesmas permissões por banco do `10-create-app-role.sh`). Todo teste que roda o fechamento usa esse banco, nunca o compartilhado.
- Regra: cada teste termina com a data operacional corrente sem execução ou `COMPLETED` (`EndOfDayTestRuns.settle()` no `finally`), devolve `MutableClock` e a configuração do hotel, e afirma só sobre os próprios dados (o banco acumula execuções de outros testes, inclusive RUNNING/FAILED a +50/+60 anos e datas antigas; a data operacional só avança).
- Etapas falsas: `endofday/EndOfDayTestConfiguration.kt` (`fake-one` 10, `fake-two` 20, `fake-three` 30, `fake-advance` 40, mais `FakeStepsProbe`); a E11 precisa rever esse contexto ao registrar as etapas reais.
- **Adiamento do gatilho em todo contexto de teste:** `src/test/resources/config/application.yaml` com `zeny.endofday.trigger.initial-delay: PT24H` (vale também para contextos montados à mão e para os profiles `local` e `prod`).
- `.superpowers/` passou a estar no `.gitignore`.

### 4. `ZenyHotelManager - Eventos e jobs` (complementa)

- Jobs novos: `EndOfDayTriggerJob` (`end-of-day-trigger`, 1 min) e a trava de execução `end-of-day-run` (ShedLock com keep-alive, usada por execução manual, retomada e automático). ARCHITECTURE §13 atualizada.
- Risco registrado para a E11: o `tick()` espera o motor por até `lock-at-most-for` e o agendador do Spring tem uma thread por padrão; com etapas reais longas, os demais jobs ficariam parados (decidir pool do agendador ou espera curta no plano da E11).

### 5. Outras notas de tema (complementam)

- `ZenyHotelManager - Tempo real (SSE)`: tópico `end-of-day` (ARCHITECTURE §10).
- `ZenyHotelManager - Módulo notifications`: primeiro uso de produção do tipo `notifications.end-of-day-pending` (obrigatório no painel).
- `ZenyHotelManager - Segurança, autenticação e autorização`: duas ações sensíveis novas (`endofday.run.start`, `endofday.run.resume`, permissão `endofday.runs.execute`).
- `ZenyHotelManager - Docker, observabilidade e CI`: métricas e regras de alerta da seção 2.
- `ZenyHotelManager - Schemas, migrações e views de relatório`: schema `endofday`, sem `DELETE` para a aplicação; última migração `V2026_11_12_1001`.

### 6. Decisões tomadas pelo orquestrador (revisáveis; vão às "Decisões para o usuário" / "Perguntas abertas" do hub)

Decisões sem confirmação do usuário, tomadas pela opção recomendada:

1. Unicidade total por data (`run_business_date_uk`) com reconciliação na retomada, mais estrita que o texto do roadmap ("única por data de execução concluída").
2. `POST /runs` com `201` síncrono, espera limitada e a execução no estado em que estiver (alternativa descartada: `202` assíncrono). É contrato público.
3. Janela de 24 h do automático; fora dela só manual (protege RN-03, RN-15 e a FNRH da E14).
4. Regra do horário devido (antes de 12:00, dia seguinte).
5. `FAILED` só com retomada manual (sem novas tentativas automáticas).
6. Trocar o fuso ou o `endOfDayTime` do hotel recalcula o horário devido e pode reabrir a janela de uma data atrasada.
7. Execução síncrona do POST; banco de teste isolado no mesmo container (H10).

Pendências transversais encontradas, fora da E10: `rollbackOn` global do Spring (exceção checked confirma a transação em outros casos de uso); Jackson aceita número ou data-hora em campos `format: date`; `PageCursor.instant` sem faixa em 9 consultas de outros módulos (provável 500 com cursor de instante extremo); ShedLock com o banco fora loga a mensagem do JDBC.

### 7. Obrigações herdadas pela E11 (notas do handoff)

- Pool do agendador versus espera do gatilho.
- `resumeManually` sem `lock_timeout`.
- Captura larga de `IllegalStateException` no `fail` do motor: usar tipo próprio antes das etapas reais.
- Keep-alive sem teste de unidade.
- Pendências das etapas sem trilha própria (decidir se audita no sink).
- `message` das pendências visível a Recepção e Financeiro (RN-13 obrigatório nas etapas).
- Uma notificação por pendência por usuário (agrupar por execução ou etapa).
- Rever `EndOfDayTestConfiguration`.
- Atualizar o `ModularityTest` do `endofday`.

## Contexto

Fechamento da etapa E10 (motor do fechamento do dia) do roadmap `roadmap-m6-operacao-fechamento` do ZenyHotelManager, publicado pelo `brain-escriba` a pedido do orquestrador, conforme a regra do projeto de publicar `ZenyHotelManager - atualização <slug> Eyy` ao fim de cada etapa que muda algo descrito no brain. Segue o formato das capturas anteriores do projeto (por exemplo, a da E12 do M5).

## Origem

- Projeto: ZenyHotelManager; repositório `/home/caio/repos/ZenyHotelManager`.
- Branch `roadmap/m6-operacao-fechamento` (criada da `main` em `b23958e`), worktree `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m6-operacao-fechamento`.
- Sessão: `claude --agent orquestrador`.
- Commits da etapa: `7ae1a3b` (plano) a `8b986e7` (última correção), mais de 45 commits.
- Plano: `docs/superpowers/plans/2026-11-12-m6-operacao-fechamento-e10.md`; roadmap: `docs/roadmaps/roadmap-m6-operacao-fechamento.md`, seção E10; documentação: `docs/ARCHITECTURE.md` §3.1, §10 e §13.
- Material-fonte do orquestrador: `.superpowers/sdd/2026-11-12-m6-operacao-fechamento-e10/brain-capture-material.md` no worktree (não copiado como anexo).
- Data: 2026-11-13.

## Por que registrar

Alimentar a consolidação do curador: cria a nota do módulo `endofday` (contrato de etapa que a E11 e a E13 precisam seguir), fixa o estado do M6 após a E10, acrescenta o mecanismo de teste do fechamento (H10), os jobs e a observabilidade novos, e deixa explícitas as decisões revisáveis e as obrigações da E11.

## Limitações e incertezas

- O merge na `main` ainda vai acontecer no fim do lote, por merge local, sem push (o push é do usuário); o hash do merge não estava disponível.
- O escriba não conferiu o código: todo o conteúdo vem do relato do orquestrador. Nomes de classe, propriedades, códigos e números (3604 testes, 8 regras do `promtool`) podem divergir do código final.
- As decisões da seção 6 foram tomadas sem confirmação do usuário; a Revisão humana da E10 está pendente.
- O worktree e o material em `.superpowers/` podem desaparecer após o merge (`.superpowers/` está no `.gitignore`); o conteúdo útil está acima.
- A nota `ZenyHotelManager - Módulo endofday` ainda não existe no vault (proposta por esta captura).

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Estado por marco]]
- [[ZenyHotelManager - Arquitetura e estrutura de módulos]]
- [[ZenyHotelManager - Testes de integração]]
- [[ZenyHotelManager - Eventos e jobs]]
- [[ZenyHotelManager - Tempo real (SSE)]]
- [[ZenyHotelManager - Módulo notifications]]
- [[ZenyHotelManager - Segurança, autenticação e autorização]]
- [[ZenyHotelManager - Docker, observabilidade e CI]]
- [[ZenyHotelManager - Schemas, migrações e views de relatório]]
- [[2026-11-12 - ZenyHotelManager - atualização arquitetura e sincronização do M6 - 3a747cdc]]
- [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 - 2c135bbf]]
