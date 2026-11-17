---
type: knowledge
status: processed
created: 2026-11-15
projects:
  - "[[ZenyHotelManager]]"
sources:
  - "[[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]]"
  - "[[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 (revisão humana) - fa5b192f]]"
  - "[[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]]"
  - "[[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E11 - df23f14d]]"
---
# ZenyHotelManager - Módulo endofday

Referência técnica do projeto [[ZenyHotelManager]]. Fechamento do dia: motor de etapas, execuções, pendências e gatilho automático. Estado: M6 E10 (2026-11-13, merge `01c6f0e`) e M6 E11 (2026-11-14, as 8 etapas financeiras e operacionais, seção "Etapas reais (M6 E11)" abaixo) concluídas; `daily-statistics` 800 e `end-of-day-reports` 900 entram na M6 E13 e seguem o "Contrato de etapa" abaixo.

Referências como "ARCHITECTURE §x", "RF-…", "RN-…" e "Hn" apontam para `docs/ARCHITECTURE.md` (§3.1, §10 e §13) e `docs/roadmaps/roadmap-m6-operacao-fechamento.md` do repositório; plano em `docs/superpowers/plans/2026-11-12-m6-operacao-fechamento-e10.md`. Texto da captura de fechamento da E10 (relato do orquestrador do lote; o escriba não conferiu o código), integrado sem resumo, com as decisões do usuário da revisão humana da E10 (H12) aplicadas por cima. O estado e as decisões do lote estão em [[ZenyHotelManager - Estado por marco]] ("M6 E10"). A seção "Etapas reais (M6 E11)" traz o texto da captura de fechamento da E11 (resumo do agente a partir do handoff, do plano e do código; nem todo nome foi conferido no código), que vale sobre o texto da E10 onde diz; estado e decisões (a)–(j) da E11 em [[ZenyHotelManager - Estado por marco]] ("M6 E11").

---

## Camada e dependências

- **Módulo** `com.zeny.hotel.endofday` (camada Operação). **Desde a M6 E11:** `allowedDependencies = ["shared", "hotel", "notifications", "reservations", "billing", "rooms"]` (subconjunto da linha da ARCHITECTURE §3.1; a tabela não muda). O `ModularityTest` confere a igualdade exata. O plano previa `payments` fora; o KDoc do `EndOfDayModule` justifica `billing` também pelas pré-autorizações, que só existem no M7. O `endofday` não usa tipos de `rates` nem de `frontdesk`. (Na E10: `["shared", "hotel", "notifications"]`.)

## Schema `endofday` e migrações

- **Schema** `endofday`: `run` (UNIQUE `run_business_date_uk`: uma execução por data), `run_step` (PK `(run_id, name)`, posição única por execução), `run_issue`; FKs para `run`; `CHECK` de status; `finished_at` presente se e somente se o status não é RUNNING. Grants ao `zeny_app`: `SELECT, INSERT, UPDATE` (sem `DELETE`; `DatabaseRolesTest` tem `NO_DELETE_TABLES`). Migrações `endofday/V2026_11_12_1000__create_endofday_tables.sql` e `V2026_11_12_1001__grant_endofday_to_app_role.sql`. **A próxima migração do projeto precisa de versão posterior a `V2026_11_13_1000`** (`reservations/V2026_11_13_1000__add_reservation_no_show.sql`, M6 E11; substitui o "posterior a `V2026_11_12_1001`" da E10).
- A unicidade por data (`run_business_date_uk`), com reconciliação na retomada, é **decisão do usuário** (revisão humana da E10, H12), mais estrita que o texto antigo do roadmap ("única por data de execução concluída"). Mudá-la depois pede migração.

## Agregado `EndOfDayRun`

- **Agregado** `EndOfDayRun` (status RUNNING/FAILED/COMPLETED; etapas PENDING/RUNNING/COMPLETED/FAILED/SKIPPED). `beginNext` reconcilia com o registro de etapas antes de escolher: etapa não concluída que saiu do registro vira SKIPPED com pendência `STEP_UNREGISTERED`; etapa nova entra se a posição for maior que a da última concluída; sem etapa restante, a execução conclui. Toda transição muda `updatedAt` (a versão sobe). Trava da linha por `SELECT … FOR NO KEY UPDATE` nativo (não `FOR UPDATE`, que travaria pela FK o INSERT de pendência numa transação `REQUIRES_NEW`); exige transação (`MANDATORY`).

## Contrato de etapa (obrigatório para E11 e E13)

- **Contrato de etapa** (`application/EndOfDaySteps.kt`, KDoc obrigatório para E11 e E13): `EndOfDayStepHandler(name, position, execute(context))`. Roda na transação que marca a etapa concluída; é idempotente pela **data** (nunca pelo `runId`); item que tolera falha roda em `REQUIRES_NEW` por outro bean, sem alterar a linha da execução; a pendência da falha do item é levantada na transação da etapa; exceção que escapa desfaz tudo, inclusive pendências e avisos (as transições usam `rollbackFor = Throwable`); capturar exceção de bean `REQUIRED` deixa a transação rollback-only; efeito externo (S3) tem de ser idempotente; nomes são estáveis como códigos (renomear ou remover a etapa de avanço da data é proibido); posições de 100 em 100 na ordem da RF-FEC-02. O registro (`EndOfDayStepRegistry`) recusa nome ou posição repetidos no boot.

## Transições auditadas

- **Transições auditadas** (`EndOfDayRunTransitions`, ator sistema): `begin(runId)`, `complete(runId, step, attempts, work)` e `fail(runId, step, attempts, reason)`, que conferem sob a trava a mesma tentativa (corrida perdida devolve `false` ou `Busy`). Motivo da falha = `ErrorCode` da `DomainException` ou nome da classe, nunca a mensagem.

## Motor

- **Motor** (`EndOfDayEngine`): trava ShedLock `end-of-day-run` com `KeepAliveLockProvider` (`zeny.endofday.lock-at-most-for` PT5M; mínimo 30 s) sobre o `LockProvider` do `shared`; executor de **uma** thread `end-of-day` (sem contexto de segurança: etapas sempre com ator sistema); `execute(runId, waitAtMost)` devolve `Finished`, `Busy` ou `StillRunning`. `Error` numa etapa vira `FAILED` (só `VirtualMachineError` não-StackOverflow escapa e deixa RUNNING); falha fora das etapas é logada em ERROR só pela classe. Executores com `@Bean(defaultCandidate = false)` + `@Qualifier` (não desligam `applicationTaskExecutor` nem `taskScheduler` do Boot).

## Pendências

- **Pendências** (`EndOfDayIssues`): grava e chama `NotificationsApi.notify(notifications.end-of-day-pending, "Pendência no fechamento de dd/MM/yyyy", "<kind>: <reference ou —>", withPermission(endofday.runs.read))` na mesma transação; nunca a `message`. Primeiro uso de produção desse tipo ([[ZenyHotelManager - Módulo notifications]]). Desde a M6 E11 os avisos são agrupados por etapa e tipo, e a etapa que falha não avisa as pendências que gravou (seção "Etapas reais (M6 E11)").

## Tempo real

- **Tempo real**: tópico `end-of-day` (permissão `endofday.runs.read`), mensagem `endofday.run` (`id` = execução, `version` gravada), publicada em toda transição que muda a execução, na criação e na retomada (ARCHITECTURE §10; ver [[ZenyHotelManager - Tempo real (SSE)]]).

## Permissões

- **Permissões**: `endofday.runs.read` (ALL; Gerente, Recepcionista, Financeiro) e `endofday.runs.execute` (ALL, **sensível**; Gerente). `AuthorizationTest` (lista exata do Gerente) atualizado. Ações sensíveis em [[ZenyHotelManager - Segurança, autenticação e autorização]].

## API

- **API** (`EndOfDayController`, tag `end-of-day`):
  - `POST /api/v1/end-of-day/runs` `{businessDate}` (`@Idempotent`, step-up `endofday.run.start` / `endofday.business-date:<data>`): `201` síncrono, com espera `zeny.endofday.manual-wait` PT30S, devolvendo a execução **no estado em que estiver** (RUNNING inclusive). **Decisão do usuário** (revisão humana da E10, H12): o contrato continua assim (alternativa descartada: `202` assíncrono); é contrato público, e mudá-lo depois é breaking change.
  - `POST …/runs/{id}/resume` (`@Idempotent`, step-up `endofday.run.resume` / `endofday.run:<id>`, sem `If-Match`, exceção registrada): `200`.
  - `GET …/runs` (cursor), `GET …/runs/{id}` (`ETag`), `GET …/runs/{id}/issues` (cursor).
  - Códigos: `END_OF_DAY_RUN_NOT_FOUND` (404); 409 `END_OF_DAY_ALREADY_CLOSED`, `END_OF_DAY_RUN_EXISTS` (leva `runId`, que pode vir nulo na corrida perdida), `END_OF_DAY_DATE_MISMATCH` (leva `currentBusinessDate`; datas fora do alcance do `date` do PostgreSQL também), `END_OF_DAY_NOT_CONFIGURED` (registro vazio), `END_OF_DAY_RUN_NOT_RESUMABLE`, `END_OF_DAY_RUN_IN_PROGRESS`. Autorização sempre antes de qualquer checagem que revele estado. Cursor de pendências com instante fora do `timestamptz` devolve `400 INVALID_CURSOR`.
  - As consultas ficam em `application/EndOfDayQueries.kt`; a camada web só vê `EndOfDayRunView` e enums espelho com `@ExtensibleEnum`.
- **Previsto para a M6 E18 (decisão H13, ainda não implementada):** a faixa das chaves do cursor passa ao `PageCursor` do `shared`, e a validação local do `endofday` (`EndOfDayQueries.requireStorable` e as constantes dela) sai; a lista de execuções do `EndOfDayQueries` está entre as 6 consultas por data cobertas. Regra em [[ZenyHotelManager - Convenções de API]].
- **Feito na M6 E18 (2026-11-15; captura [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E18 - a68d398b]], itens 2 e 3):** a validação própria do `endofday` (`EndOfDayQueries.requireStorable` e as constantes `MIN_STORABLE_INSTANT` e `MAX_STORABLE_INSTANT_EXCLUSIVE`) saiu, e `checkNoRun` usa o `StorableRange` do `shared` ([[ZenyHotelManager - Convenções de API]], "Cursor e datas estritos: comportamento atual"). As três transições (`EndOfDayRunTransitions`) perderam o `rollbackFor = Throwable` local, coberto pelo `rollbackOn = ALL_EXCEPTIONS` global, sem mudança de comportamento ([[ZenyHotelManager - Auditoria]], "Rollback em toda exceção: comportamento atual"). O executor do `endofday` não mudou (já loga só a classe). Substitui o item "Previsto para a M6 E18" acima e a frase "as transições usam `rollbackFor = Throwable`" do "Contrato de etapa". A E18 está na branch `roadmap/m6-operacao-fechamento`, ainda fora da `main`.

## Gatilho automático

- **Gatilho automático**: `EndOfDaySchedule.dueAt(businessDate, endOfDayTime, zone)`: horário antes de 12:00 vence no dia seguinte; 12:00 ou depois, no próprio dia; no fuso do hotel. `EndOfDayTrigger.tick()` decide nesta ordem: `NOT_DUE`, `NO_STEPS` (registro vazio; nenhum aviso), `OUTSIDE_WINDOW` (depois de `zeny.endofday.trigger.catch-up-window`, PT24H, validada no boot até P7D: nada roda sozinho, aviso uma vez por data e processo "execute ou retome manualmente"); senão cria (`createAutomatic`, ator sistema) ou retoma a RUNNING interrompida. `FAILED` espera a retomada manual; `COMPLETED` devolve `ALREADY_CLOSED`; corrida perdida na criação é tratada. Job `EndOfDayTriggerJob` (`end-of-day-trigger`, `interval` PT1M) loga só a classe da exceção.
- **Decisão do usuário para a E11** (revisão humana da E10, H12): o gatilho automático passa a só disparar o motor e voltar (espera curta), sem mudar o pool do agendador do Spring. Na E10, o `tick()` ainda esperava o motor por até `lock-at-most-for` ([[ZenyHotelManager - Eventos e jobs]]); implementada na E11 com `zeny.endofday.trigger.wait` (seção "Etapas reais (M6 E11)").

## Métricas e alertas

- **Métricas e alertas**: Timer `zeny.endofday.run.duration` (tags `outcome`, `resumed`), Counter `zeny.endofday.run.failures`, gauges `zeny.endofday.runs.failed` e `zeny.endofday.overdue.seconds` (0 antes do horário e com o registro vazio; NaN se a leitura falhar; refresh `zeny.endofday.metrics.refresh-interval` PT30S). Regras novas no grupo `zeny-end-of-day` de `docker/prometheus/alerts.yaml`: `ZenyEndOfDayFailed`, `ZenyEndOfDayNotRun` (> 3600 s), `ZenyEndOfDayMetricsUnavailable` (`promtool`: 8 regras OK). A entrega dos alertas é da M8 E18. Ver [[ZenyHotelManager - Docker, observabilidade e CI]].

## Entre a E10 e a E11

- *Estado histórico, superado pela M6 E11, que registrou as etapas reais.* **Entre a E10 e a E11 (a `main` depois do merge da E10)**: nenhuma etapa real registrada; `POST /runs` devolve 409 `END_OF_DAY_NOT_CONFIGURED`; o gatilho devolve `NO_STEPS` (um WARN por data), sem aviso; métricas zeradas, sem alerta. Provado por `EndOfDayNoStepsProductionTest`.

## Testes

- Todo teste que roda o fechamento usa `@EndOfDayIntegrationTest` e o banco próprio `zeny_endofday` (H10), com as etapas falsas de `endofday/EndOfDayTestConfiguration.kt`: regras em [[ZenyHotelManager - Testes de integração]] ("M6 E10"). Desde a E11, as etapas reais rodam no mesmo banco com `EndOfDayRealStepsTestConfiguration`, em quatro formas de contexto ("M6 E11" na mesma nota).

## Obrigações herdadas pela E11 (notas do handoff da E10)

Situação depois da M6 E11 entre colchetes, segundo a captura da E11 (seção "Etapas reais (M6 E11)").

- Pool do agendador versus espera do gatilho: **resolvida pela decisão do usuário** acima (o gatilho só dispara o motor e volta, sem mudar o pool). [Implementada: `zeny.endofday.trigger.wait`.]
- `resumeManually` sem `lock_timeout`. [Feito: retomada manual com `lock_timeout` de 5 s.]
- Captura larga de `IllegalStateException` no `fail` do motor: usar tipo próprio antes das etapas reais. [Feito: `StepAttemptLostException`.]
- Keep-alive sem teste de unidade. [Segue aberta: a E13 deve conferi-lo antes de etapas longas.]
- Pendências das etapas sem trilha própria (decidir se audita no sink). [*Nota do curador:* a captura da E11 não trata deste item.]
- `message` das pendências visível a Recepção e Financeiro (RN-13 obrigatório nas etapas). [Atendida nas etapas pelo `EndOfDayItems`: mensagem `"<issueKind>: <código do erro>"`, sem dado pessoal; a referência é o id.]
- Uma notificação por pendência por usuário (agrupar por execução ou etapa). [Feito: avisos agrupados por etapa e tipo.]
- Rever `EndOfDayTestConfiguration`. [Revisto: as etapas falsas continuam só no contexto do motor.]
- Atualizar o `ModularityTest` do `endofday`. [Feito: igualdade exata com a lista nova.]

*Nota do curador (conferência no repositório em 2026-11-15, só leitura, no merge `01c6f0e`):* `EndOfDayModule.kt` declara `allowedDependencies = ["shared", "hotel", "notifications"]`; `EndOfDayErrorCodes.kt` tem os sete códigos acima; `EndOfDayPermissions.kt` declara `endofday.runs.read` e `endofday.runs.execute`; as duas migrações existem em `src/main/resources/db/migration/endofday/`; `EndOfDayQueries.kt` tem `requireStorable` e `MIN_STORABLE_INSTANT`; as propriedades `zeny.endofday.lock-at-most-for`, `manual-wait` e `trigger.catch-up-window` e o `KeepAliveLockProvider` aparecem no código. Os demais nomes, valores e números vêm do relato e não foram conferidos.

## Etapas reais (M6 E11, 2026-11-14)

Origem: [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E11 - df23f14d]] (item 2), que complementa o texto da E10 acima e o substitui onde dito. Fontes da captura: handoff da E11 no roadmap, plano `docs/superpowers/plans/2026-11-13-m6-operacao-fechamento-e11.md` e código (lidos diretamente `reservations/NightCharges.kt`, `endofday/application/EndOfDayItems.kt` e a lista de `endofday/application/steps/`; o resto vem do handoff e do plano, e em divergência vale o código). A associação de cada etapa às chamadas de API segue o plano e o roadmap, não a leitura do corpo de cada etapa. Decisões (a)–(j) da E11 em [[ZenyHotelManager - Estado por marco]] ("M6 E11").

- **As 8 etapas** (nomes estáveis, publicados; posições de 100 em 100; 800 e 900 ficam para a E13), cada uma um bean `EndOfDayStepHandler` em `endofday/application/steps/`:
  - `no-show` 100 (`NoShowStep`): reservas confirmadas com chegada pendente (`ReservationsApi.pendingArrivals`) viram `NO_SHOW` com a multa da política copiada na reserva (RN-15); a UH alocada é solta no mesmo commit.
  - `pending-departures` 200 (`PendingDeparturesStep`): hospedadas com saída passada (`pendingDepartures`) geram uma pendência por fechamento; nenhum check-out automático.
  - `room-charges` 300 (`RoomChargesStep`): diárias, pacotes e taxa de turismo das hospedadas, por noite, com `PostingSource.END_OF_DAY`.
  - `block-release` 400 (`BlockReleaseStep`): `blocksDueForRelease` + `releaseUnused` (devolve ao inventário as UHs não utilizadas dos bloqueios vencidos, RN-16).
  - `provisional-expiry` 500 (`ProvisionalExpiryStep`): `dueProvisionals` + `expireProvisional` (RN-23); processa até 1000 por execução; convive com o `ProvisionalExpiryJob` de 5 min.
  - `card-pre-authorizations` 600 (`CardPreAuthorizationsStep`): registra **`NOT_APPLICABLE` até o M7** (renovação de pré-autorizações, RF-FEC-02 passo 6). É a nota pedida pelo roadmap.
  - `occupied-rooms-dirty` 700 (`OccupiedRoomsDirtyStep`): UHs ocupadas passam a Sujo por `RoomsApi.markDirty` com origem `END_OF_DAY` (RN-09).
  - `advance-business-date` 1000 (`AdvanceBusinessDateStep`): `HotelApi.advanceBusinessDate(expectedCurrent)`, com `statement_timeout` de 30 s e `lock_timeout` de 10 s. **Renomear ou remover é proibido.** O evento `BusinessDateAdvanced` gera as rotinas de checklist do novo dia (provado em teste).
- **`EndOfDayItems`** (`application/EndOfDayItems.kt`): apoio comum ao trabalho por item. Abre a transação do item por `TransactionTemplate` `PROPAGATION_REQUIRES_NEW`, sem `@Transactional` (como `OfflineCommands`), sem tocar na linha `endofday.run`. `each(context, issueKind, items, reference, work)`: a `DomainException` de um item desfaz só aquele item e vira pendência levantada na transação da etapa, com mensagem `"<issueKind>: <código do erro>"` (sem dado pessoal, RN-13; a referência é o id); qualquer outra exceção escapa e falha a etapa, que a retomada repete. Devolve quantos itens concluíram.
- **Chaves de idempotência `sourceReference`** (H5): `reservations.reservation:<id>:<noite>:room`, `…:<noite>:package:<packageId>`, `…:<noite>:tourism-fee` e `…:<data>:no-show`. Cada etapa repetida para a mesma data não duplica efeito (RN-21, RF-FEC-03).
- **Gatilho:** só dispara o motor e volta. `EndOfDayTrigger` espera por `zeny.endofday.trigger.wait` (padrão `PT5S`, até `PT1M`; H12), sem aumentar o pool do agendador. **Substitui** a obrigação "pool do agendador versus espera do gatilho" da E10 e resolve o risco registrado ali.
- **Motor:** `StepAttemptLostException` no `fail` (tipo próprio; **substitui** a captura larga de `IllegalStateException` apontada na E10); retomada manual com `lock_timeout` de 5 s, que responde `409 END_OF_DAY_RUN_IN_PROGRESS` e desfaz tudo, inclusive o uso do token de aprovação.
- **Avisos agrupados:** as pendências levantadas notificam por etapa e tipo (não uma notificação por pendência por usuário). **Substitui** a obrigação correspondente da E10.
- **Etapa que falha não avisa** as pendências que gravou em `REQUIRES_NEW`; elas ficam no `GET` de pendências e só o `STEP_FAILED` é avisado (as etapas reais levantam pendência na transação da etapa).
- **Pendências conhecidas pelo código dos relatos:** `ROOM_CHARGE_FAILED` (código desativado, conta ou destino do roteamento encerrado), `STEP_FAILED`.
- **Ficou fora (E13/E14/M7):** snapshot de estatísticas (`daily-statistics` 800) e PDFs (`end-of-day-reports` 900) na E13; no-show na FNRH na E14; renovação de pré-autorizações no M7; relatório de pendências da RF-FEC-04 (contas com saldo, caixas abertos, FNRH, notas, ARI) com a E09/E13 pelas views `report_*`.
- **Notas técnicas deixadas pela E11:**
  - a detecção de no-show repetido na mesma data supõe relógio monotônico; avaliar um sinal explícito de "criado ou existente" no `BillingApi.post`, o que muda o contrato do `billing`;
  - a fila do executor do motor não tem limite (um pedido por rodada enquanto uma etapa está presa, todos sem efeito); sugestão: não reenfileirar enquanto houver `Future` pendente do mesmo `runId`;
  - `ReservationsApi.markNoShow`, `releaseUnused` e `expireProvisional` não conferem permissão; sugestão: regra ArchUnit "só o `endofday` chama";
  - os KDocs de `EndOfDayErrorCodes` (constante e exceção de `END_OF_DAY_RUN_IN_PROGRESS`) ainda dizem "outro executor";
  - o keep-alive do motor continua sem teste de unidade (pedido na E10); a E13 deve conferi-lo antes de etapas longas;
  - advisories pré-existentes de `opentelemetry-api` (>= 1.67.0) e `commons-lang3` (>= 3.18.0) ficaram para uma manutenção de dependências.
- O lado do `reservations` (consultas por data, no-show, `ReservationNightCharges`) está em [[ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)]] e [[ZenyHotelManager - Módulo reservations (inventário, disponibilidade e reservas)]]; a trava da data operacional (`HotelApi.lockBusinessDate()`) em [[ZenyHotelManager - Módulos hotel e staff]] e [[ZenyHotelManager - Módulo billing (caixa, pagamentos, caução e encerramento)]]; os testes em [[ZenyHotelManager - Testes de integração]] ("M6 E11").

*Nota do curador (conferência no repositório em 2026-11-15, só leitura, no merge `3eeef98` da E11):* `EndOfDayModule.kt` declara a lista de dependências acima; existem os oito arquivos de etapa em `endofday/application/steps/` com os nomes de classe acima, `EndOfDayItems.kt`, `reservations/NightCharges.kt` (`object ReservationNightCharges`, `data class StayCharges`) e a migração `reservations/V2026_11_13_1000__add_reservation_no_show.sql`; o `application.yaml` tem `zeny.endofday.trigger.wait: PT5S`; `StepAttemptLostException` aparece em `EndOfDayEngine.kt` e `EndOfDayRunTransitions.kt`. O corpo de cada etapa não foi lido.

---

## Proveniência

- 2026-11-15 — [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]] (capture_id: 1e4f709b-7bbd-4c39-9725-1926aef1ca98): nota criada com o módulo `endofday` da M6 E10 (item 2 da captura) e as obrigações herdadas pela E11 (item 7); nota do curador com a conferência no merge `01c6f0e`.
- 2026-11-15 — [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 (revisão humana) - fa5b192f]] (capture_id: fa5b192f-13a0-4e35-959a-3134613a24d8): decisões do usuário H12 sobre o contrato do `POST /runs`, a unicidade por data e o gatilho da E11 (substitui a obrigação do pool do agendador).
- 2026-11-15 — [[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]] (capture_id: 009e3130-5bd9-4e8b-bd56-81c7fc440b81): saída prevista da validação local do cursor do `endofday` na M6 E18 (H13).
- 2026-11-15 — [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E11 - df23f14d]] (capture_id: df23f14d-ec3c-4fa2-aa75-462913ddaf5e): M6 E11 (item 2 da captura): dependências e próxima migração substituídas, seção "Etapas reais (M6 E11)" com as 8 etapas, `EndOfDayItems`, chaves, gatilho, motor, avisos e notas técnicas, e situação das obrigações herdadas da E10; nota do curador com a conferência no merge `3eeef98`.
- 2026-11-16 — [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E18 - a68d398b]] (capture_id: a68d398b-2037-4b20-af27-8039b163ae0e): validação local do cursor retirada e `rollbackFor = Throwable` local retirado das transições (itens 2 e 3 da captura), em "API".
