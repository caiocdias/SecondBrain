---
type: capture
status: archived
created: 2026-11-14
capture_id: df23f14d-ec3c-4fa2-aa75-462913ddaf5e
---
# ZenyHotelManager - atualização m6-operacao-fechamento E11

## Conteúdo capturado

Captura de fechamento da etapa M6 E11 (etapas financeiras e operacionais do fechamento do dia), `#concluida` em 2026-11-14 na branch `roadmap/m6-operacao-fechamento`. Resumo do agente a partir do handoff da E11 no roadmap, do plano da etapa e do código; organizada por nota de tema, dizendo se **substitui** ou **complementa** cada trecho. **Complementa** as capturas da E10 ([[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]] e [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 (revisão humana) - fa5b192f]]) e as **substitui** onde dito. Vale sobre as notas e sobre capturas pendentes quando tratarem do mesmo assunto.

### 1. Estado: `ZenyHotelManager - Estado por marco` e Estado do hub `10 Projects/ZenyHotelManager.md` (substitui o Estado do M6)

- **M6 com E10 e E11 `#concluida`.** E11 concluída em 2026-11-14; **Revisão humana: sim, pendente com o usuário**. Demais etapas seguem `#pendente`. Próxima elegível: **E14** (depende da E11), depois E15, E16, E17 e E18 (as etapas de governança, manutenção, relatórios, E12 e E13 seguem a ordem do roadmap).
- Gate: `./gradlew build` em `a9a9b39`, BUILD SUCCESSFUL em 27m 56s, **3877 testes, 0 falhas, 0 ignorados** (inclui `ModularityTest`, ArchUnit, detekt, ktlint, `checkOpenApi` e `koverVerify`). O primeiro gate, em `6bd8073`, falhou num só teste (`EndOfDayIsolationTest`: o invariante da E10 exigia propriedades iguais nas duas anotações de teste, e a espera curta do gatilho só existe no `@EndOfDayIntegrationTest`); o invariante virou "as de integração mais só a espera curta" (`a9a9b39`). Um gate anterior foi morto pelo sistema por falta de memória (Gradle do DesktopFront rodando junto).
- Commits: `3787f93` (início) a `6bd8073` sobre `57eb5fa` da `main`, mais a onda final até `a9a9b39` e o fechamento do handoff `1e35c4a`. Plano de 20 tarefas em série, com duas execuções (lote parado a pedido do usuário depois da Task 13, retomado em 2026-11-13/14). Revisão de arquitetura do plano: aprovada com notas na rodada 1 (rodada 0 bloqueada com 5 Importantes, corrigidos). Revisão final (`revisor-seguranca`): "With fixes", 0 Critical de código; o Critical de processo era a falta do gate. Onda única de correção e re-revisão aprovadas.
- Verificações: `osv-scanner` 2.7.0 com `-L` nos três lockfiles: 0 Critical/High, 2 Medium e 3 Low pré-existentes (`commons-lang3` só no buildscript, `logback-core`, `opentelemetry-api`); lockfiles e catálogo não mudaram. oasdiff sem `ERR` em `/api/v1` (o contrato só ganhou `NO_SHOW` e `RESERVATION_NO_SHOW` em `x-extensible-enum`). `check_test_integrity.py --base 57eb5fa` deu exit 1 com apontamentos julgados justificados pela revisora; com `--base 790749a` (onda), exit 0.
- Integração na `main`: merge local no fim deste lote, sem push (o push é do usuário). O hash do merge não existia no momento da captura.
- A próxima migração do projeto precisa de versão posterior a **`V2026_11_13_1000`** (substitui o "posterior a `V2026_11_12_1001`" da captura da E10).

### 2. `ZenyHotelManager - Módulo endofday` (nota proposta pela E10; complementa a proposta)

- **Dependências:** `allowedDependencies = ["shared", "hotel", "notifications", "reservations", "billing", "rooms"]` (subconjunto da linha da ARCHITECTURE §3.1; a tabela não muda). O `ModularityTest` confere a igualdade exata. O plano previa `payments` fora; o KDoc do `EndOfDayModule` justifica `billing` também pelas pré-autorizações, que só existem no M7. O `endofday` não usa tipos de `rates` nem de `frontdesk`.
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
- **Gatilho:** só dispara o motor e volta. `EndOfDayTrigger` espera por `zeny.endofday.trigger.wait` (padrão `PT5S`, até `PT1M`; H12), sem aumentar o pool do agendador. **Substitui** a obrigação "pool do agendador versus espera do gatilho" da captura da E10 e resolve o risco registrado ali.
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

### 3. `ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)` e `(inventário, disponibilidade e reservas)` (complementam)

- **Consultas por data** na `ReservationsApi` (H4; sem conferir permissão, sem trava, por id ascendente, sem limite): `pendingArrivals(date)` (`CONFIRMED` com `arrival <= date`; pré-reserva nunca vira no-show), `pendingDepartures(date)` (`IN_HOUSE` com `departure <= date`) e `inHouse(date)` (`IN_HOUSE` com `arrival <= date`). **Substitui** a afirmação "não há no-show nem consultas por data" da base técnica herdada do M5.
- **No-show:** `ReservationAction.NO_SHOW`, transição só a partir de `CONFIRMED` (`REACTIVATE` continua aceitando `NO_SHOW`); `ReservationHistoryKind.NO_SHOW`; `RoomAssignmentEndReason.RESERVATION_NO_SHOW`; `ReservationsApi.markNoShow`; a UH alocada é solta no mesmo commit (gatilho adiado `reservation_assignment_released`). Evento **`ReservationMarkedNoShow`** (`reservationId, bookingId, roomTypeId, roomId?, arrival, departure, dayUse, businessDate, penaltyCharged, performedBy, version, markedAt`), publicado pelo outbox, sem dado pessoal; a E14 o escuta.
- **Migração:** `reservations/V2026_11_13_1000__add_reservation_no_show.sql` troca as `CHECK` de `reservation_history.kind` e do motivo do fim da alocação para aceitar `NO_SHOW` e `RESERVATION_NO_SHOW`. Nenhuma coluna nova: a multa fica no lançamento, em `penalties_charged` e no histórico. Os dois enums saem como `x-extensible-enum`.
- **Regra única das cobranças da estadia** (`reservations/NightCharges.kt`): `ReservationNightCharges.of(reservation, night, tourismFeePerPersonNight)` devolve `NightCharge` (`kind` `ROOM`/`PACKAGE`/`TOURISM_FEE`, `sourceReference`, `includedInRate`) por noite congelada; valor zero não se lança; hospedagem e pacotes inclusos sem taxa de serviço (RN-11). `ReservationsApi.chargesDue` devolve `StayCharges(reservationId, folioId, charges)` por hospedada até uma data. O `endofday` não usa tipos de `rates`.
- **Pré-reservas:** `dueProvisionals` e `expireProvisional`, usados pela etapa `provisional-expiry`; o `ProvisionalExpiryJob` segue existindo.
- Só o fechamento chama `releaseUnused` para os ids de `blocksDueForRelease()` (obrigação da M4 E11 cumprida).

### 4. `ZenyHotelManager - Hospedagem e recepção` (complementa)

- O check-out da M5 E04 (`frontdesk/application/CheckOutService.kt`) passa a usar a regra única do `reservations` (`ReservationNightCharges`); `frontdesk/domain/CheckOutRules.kt` foi ajustado e `StayCharges` virou `CheckOutCharges` no `frontdesk` (renome com a asserção mantida). O lançamento do check-out e o do fechamento na mesma data usam a mesma chave e não duplicam (testado com os dois caminhos reais).

### 5. `ZenyHotelManager - Módulos hotel e staff` (complementa)

- `HotelApi.lockBusinessDate()`: leitura escalar da data operacional com a linha de `hotel.business_day` em **`FOR SHARE`** até o commit; o avanço (`FOR UPDATE`) espera os lançamentos em curso. É o que dá RF-FEC-05 por construção. Registrado na ARCHITECTURE §11.

### 6. `ZenyHotelManager - Módulo billing (contas, roteamento e taxa de serviço)` e `(caixa, pagamentos, caução e encerramento)` (complementam)

- `billing/application/BillingOperations.kt`: o `stamp()` de todo lançamento carimba a data lida por `lockBusinessDate()`; o encerramento de conta também trava a data.
- **Caixa:** a abertura, os movimentos e o fechamento de turno **travam a data como os lançamentos** (corrigido na onda final, `3abf960`; `CashierDateLockTest`, vermelho em `790749a`, verde com `3abf960`). ARCHITECTURE §11 cobre inclusive caixa e encerramento de conta.
- Nenhum lançamento fica em data fechada; um lançamento depois do avanço cai na data nova, com o caminho concorrente testado.

### 7. `ZenyHotelManager - Eventos e jobs` (complementa)

- O `EndOfDayTriggerJob` (`end-of-day-trigger`, 1 min) só dispara o motor e volta (`zeny.endofday.trigger.wait`, padrão `PT5S`, até `PT1M`), sem bloquear o agendador de uma thread por `lock-at-most-for`. ARCHITECTURE §13 (etapas do fechamento) atualizada. Novo evento publicado: `ReservationMarkedNoShow` (seção 3).

### 8. `ZenyHotelManager - Testes de integração` (complementa)

- Os testes do fechamento com as etapas reais rodam no banco isolado `zeny_endofday` (H10), em quatro formas de contexto: (1) `@EndOfDayIntegrationTest` + `EndOfDayTestConfiguration` (só as etapas falsas, as reais excluídas por `EndOfDayProductionStepsExcluded`); (2) `@EndOfDayIntegrationTest` + **`EndOfDayRealStepsTestConfiguration`** (etapas reais); (3) `EndOfDayNoStepsProductionTest` (sem etapas); (4) os testes de persistência e transições da E10 com `@EndOfDayIntegrationTest` puro, que passam a importar a exclusão.
- **`@EndOfDayIntegrationTest` com `zeny.endofday.trigger.wait=PT1S`:** é a única diferença permitida em relação ao `@IntegrationTest`; o invariante de `EndOfDayIsolationTest` passou a ser "as propriedades de integração mais só a espera curta" (**substitui** a regra de propriedades iguais da captura da E10).
- Sondas: `BillingPostProbe` (lançamento concorrente ao avanço) e `RoomsMarkProbe`. Esperas provadas por `pg_blocking_pids`, com o prazo contado a partir do avanço `RUNNING`, e testes "waits" por sondagem; o teste do no-show afirma exatamente um `ReservationMarkedNoShow`; limite do tick em 10 s.
- Regra do banco isolado mantida: cada teste termina com a data corrente sem execução ou `COMPLETED` (`EndOfDayTestRuns.settle`), devolve o `MutableClock` e desfaz a configuração do hotel; asserções só sobre os próprios dados.
- **Cuidado:** os contextos `@IntegrationTest` compartilhados registram as etapas reais, inertes só pelo `initial-delay PT24H`; nenhum teste no banco compartilhado pode disparar o fechamento.
- **Substitui** a nota da E10 "a E11 precisa rever `EndOfDayTestConfiguration`": revisto (etapas falsas `fake-one` 10 a `fake-advance` 40 continuam só no contexto do motor).

### 9. Decisões para o usuário (a)–(j) do handoff da E11

**Todas tomadas pela opção recomendada, sem confirmação do usuário, e pendentes da revisão humana da E11** (nenhuma é de arquitetura). O handoff não traz item (g) entre as decisões: ele está nas notas técnicas (seção 2, a detecção de no-show repetido supõe relógio monotônico).

- **(a)** A multa de no-show é a penalidade da política de cancelamento copiada na reserva, sem prazo e sem isenção automática, descontado o já cobrado (`penaltiesCharged`). Para isentar, faz-se o estorno depois.
- **(b)** A recusa da multa (conta encerrada ou `MULTA-NOSHOW` desativado) bloqueia o no-show inteiro, e a reserva vira pendência a cada fechamento; a UH e o inventário ficam presos nas noites seguintes até alguém agir. O mesmo vale para `ROOM_CHARGE_FAILED` por código desativado. Alternativa apontada pela revisão final: marcar o no-show e soltar a UH, com a falha da multa como pendência própria e lançamento manual.
- **(c)** Taxa de turismo = valor vigente (`tourismFeePerPersonNight`) × (adultos + crianças), por noite, nunca no day use, e só na noite que o fechamento fecha. Custo aceito: as noites recuperadas ficam sem a taxa (check-in feito durante a execução, ou item que falhou e foi recuperado no fechamento seguinte), e o operador a lança à mão. Alternativa: guardar a taxa vigente por fechamento.
- **(d)** O fechamento recupera as noites a partir da data do check-in (cada noite congelada de `max(chegada, data operacional do check-in)` até a data que fecha que ainda não tem lançamento). Resíduo: um check-in durante a execução seguido de check-out antecipado antes do próximo fechamento deixa a noite sem lançamento.
- **(e)** Hóspede além da saída não ganha diária automática, só a pendência.
- **(f)** Caixa: **corrigido na onda final**; a abertura, os movimentos e o fechamento de turno travam a data como os lançamentos.
- **(h)** O `409` da retomada quando o ShedLock dá `Busy` (trava com outro processo) gasta o token de aprovação e confirma a retomada; o `409` do `lock_timeout` desfaz tudo e não gasta o token. Esse comportamento vem da E10.
- **(i)** O avanço que esgota o prazo (30 s/10 s) fica `FAILED` até a retomada manual, e o hotel segue operando na data antiga até lá.
- **(j)** Uma etapa que falha não avisa as pendências que gravou em `REQUIRES_NEW`; só o `STEP_FAILED` é avisado.

Decisões de processo do plano (ruling): a Task 13 decidiu que as noites recuperadas não levam a taxa de turismo; a Task 19 reescreveu (pelo testador) um teste da E10 que esperava aviso das pendências de uma etapa que falha, porque o contrato de etapa diz que não há aviso.

### 10. Outras notas (complementam)

- `ZenyHotelManager - Estado por marco` / hub: a E10 foi integrada na `main` pelo merge `01c6f0e`; esta E11 entra no merge local do fim do lote.
- `README.md` do repositório: item "Etapas do fechamento (M6 E11)" já descreve as etapas.
- `ZenyHotelManager - Segurança, autenticação e autorização`, `ZenyHotelManager - Módulo notifications`, `ZenyHotelManager - Tempo real (SSE)`, `ZenyHotelManager - Docker, observabilidade e CI` e `ZenyHotelManager - Schemas, migrações e views de relatório`: sem mudança nesta etapa além da migração nova (última: `reservations/V2026_11_13_1000__add_reservation_no_show.sql`).

## Contexto

Fechamento da etapa E11 do roadmap `roadmap-m6-operacao-fechamento` do ZenyHotelManager, publicado pelo `brain-escriba` a pedido do orquestrador, conforme a regra "Atualização por capturas" do hub. Não havia captura equivalente da E11 em `00 Inbox/` nem em `90 Archive/Inbox/` (busca por nome); as da E10 são complementadas, não duplicadas.

## Origem

- Projeto: ZenyHotelManager; repositório `/home/caio/repos/ZenyHotelManager`, worktree `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m6-operacao-fechamento`, branch `roadmap/m6-operacao-fechamento`, HEAD `1e35c4a`.
- `docs/roadmaps/roadmap-m6-operacao-fechamento.md`, seção E11 ("Evidências e handoff"); plano `docs/superpowers/plans/2026-11-13-m6-operacao-fechamento-e11.md` (Global Constraints e mapa de arquivos); `docs/ARCHITECTURE.md` §11 e §13; código conferido por leitura direta: `reservations/NightCharges.kt`, `endofday/application/EndOfDayItems.kt` e a lista dos arquivos de `endofday/application/steps/`.
- Data: 2026-11-14.

## Por que registrar

Alimentar a consolidação do curador: fixa o estado do M6 após a E11, completa a nota `Módulo endofday` proposta pela E10 com as 8 etapas e o contrato real, atualiza as notas de `reservations`, `hospedagem`, `hotel`, `billing`, jobs e testes, e deixa explícitas as decisões (a)–(j) pendentes da revisão humana.

## Limitações e incertezas

- O merge na `main` acontece depois desta captura, por merge local e sem push; o hash do merge não era conhecido.
- Nem todo nome foi conferido no código: foram lidos `NightCharges.kt`, `EndOfDayItems.kt` e a lista dos arquivos de etapa; o restante (assinaturas de `ReservationsApi`, `HotelApi.lockBusinessDate`, mapeamento exato de cada etapa às APIs que chama, `RoomsApi.markDirty` na etapa 700, `HotelApi.advanceBusinessDate` na 1000, `trigger.wait` no `application.yaml`, `ReservationMarkedNoShow` e testes de apoio) vem do handoff, do plano e do relato do orquestrador. O plano descreve a intenção; o handoff diz o que foi entregue; em divergência vale o código.
- A associação de cada etapa às chamadas de API (por exemplo `markDirty` com `END_OF_DAY` na etapa 700) segue o plano e o roadmap (nota "`RoomsApi.markDirty(END_OF_DAY)` é a mudança prevista para as ocupadas"), não uma leitura do corpo de cada etapa.
- As decisões (a)–(j) não foram confirmadas pelo usuário; a Revisão humana da E11 está pendente. A nota do módulo `endofday` ainda não existe no vault (proposta pela E10).
- O worktree pode desaparecer após o merge; o conteúdo útil está acima.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Estado por marco]]
- [[ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)]]
- [[ZenyHotelManager - Módulo reservations (inventário, disponibilidade e reservas)]]
- [[ZenyHotelManager - Hospedagem e recepção]]
- [[ZenyHotelManager - Módulos hotel e staff]]
- [[ZenyHotelManager - Módulo billing (contas, roteamento e taxa de serviço)]]
- [[ZenyHotelManager - Módulo billing (caixa, pagamentos, caução e encerramento)]]
- [[ZenyHotelManager - Eventos e jobs]]
- [[ZenyHotelManager - Testes de integração]]
- [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]]
- [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 (revisão humana) - fa5b192f]]
