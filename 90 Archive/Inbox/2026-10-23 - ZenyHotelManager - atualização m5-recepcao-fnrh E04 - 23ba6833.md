---
type: capture
status: archived
created: 2026-10-23
capture_id: 23ba6833-5674-4a22-aacd-3a26bf55f9bf
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E04

## Conteúdo capturado

Resumo do agente (orquestrador do lote M5, sessão externa no repositório `/home/caio/repos/ZenyHotelManager`): a etapa E04 (check-out) do roadmap `docs/roadmaps/roadmap-m5-recepcao-fnrh.md` foi concluída na branch `roadmap/m5-recepcao-fnrh`, ainda não integrada à `main`. Texto novo ou alterado para cada nota afetada:

### Para [[ZenyHotelManager]] (hub), seção "Estado" — substitui a linha do M5

- M0 a M4 concluídos. M5 em andamento: E01 a E03 na `main` (até `a6c0f03`); **E04 (check-out) concluída na branch `roadmap/m5-recepcao-fnrh`** (commits `1955898`..`51a0533`, 2026-10-23), aguardando a decisão de integração do usuário. É o primeiro lote no formato novo, com o superpowers. Próxima etapa elegível: E05.

### Para [[ZenyHotelManager - Hospedagem e recepção]] — complementa, com um item novo depois de "Recepção: walk-in"

- **Recepção: check-out** (RF-REC-06 sem nota fiscal nem contas a receber, RN-06, RN-09, RN-11, H12 a H14 do M5, M5 E04). Caso de uso `frontdesk/application/CheckOutService.kt` (`FrontdeskCheckOutService`), regras puras em `frontdesk/domain/CheckOutRules.kt` (`StayCharges`, `StayCharge`, `LateCheckOutRules`, `StayNotSettledException`, `EarlyLateFeeChangedException`) e `StayRules.requireCheckOut`. Sem estado próprio.
  - **Endpoint:** `POST /api/v1/reservations/{id}/check-out` (`@Idempotent`, `frontdesk.stays.checkout`, Gerente e Recepcionista, não sensível; `operationId` `checkOutReservation`).
    - Corpo opcional: `{lateCheckOutFee?}`, dinheiro em texto, o valor da cotação `GET …/early-late-quote`.
    - `200` com o `ETag` da reserva e `{reservation, room, stayCharges[], lateCheckOut?, releasedPreAuthorizations[], closedFolios[]}`. Cada lançamento traz `serviceCharge?`.
  - **Ordem** (e das travas, reserva → inventário → conta(s) → UH):
    1. Antes de qualquer escrita: a permissão; a reserva (`404`); só uma hospedada (`409 RESERVATION_TRANSITION_NOT_ALLOWED`, ação `CHECK_OUT`); o late (`422 EARLY_LATE_NOT_OFFERED`; `409 EARLY_LATE_FEE_CHANGED` com `currentFee`).
    2. `ReservationsApi.checkOut`, que trava a reserva, devolve o inventário do antecipado e encerra a alocação.
    3. As cobranças da H14.
    4. O late, no `ROOM_CHARGE`, como "Late check-out", origem `MANUAL`.
    5. O saldo pela `BillingApi.balanceOf`. Se não estiver quitado, `409 FOLIO_BALANCE_NOT_ZERO` com `folios` (`folioId`, `number`, `status`, `balance`) e `total`, **já com as cobranças pendentes e o late**; tudo é desfeito.
    6. A liberação de todas as cauções não encerradas, inclusive as vencidas e as de um check-in desfeito.
    7. O `closeFolio` de cada conta aberta.
    8. A UH, por `RoomsApi.markVacant(CHECK_OUT)` (Vaga + Suja).
    9. A trilha `frontdesk.stay.check-out`.
  - **Cobranças da H14:** só quando a data operacional do check-out é a data da chegada (o day use, ou o pernoite que sai no dia em que chegou). A noite da chegada gera:
    - a hospedagem `roomAmount − includedPackagesAmount` no `ROOM_CHARGE`;
    - cada pacote da noite no `transactionCodeId` dele (quantidade × unitário, com o nome do pacote como descrição). Os **inclusos vão sem taxa de serviço** (`serviceChargeRate` zero), e os adicionais seguem o código.

    A origem é `END_OF_DAY`, e os valores zero não são lançados. Cada cobrança leva a chave `reservations.reservation:<id>:<data>:room` ou `…:package:<packageId>`. Nas outras estadias, o check-out não lança nada.
  - **Testes:** `CheckOutDomainTest` e `FrontdeskCheckOutApiTest` (no contexto das reservas, com `MutableClockConfiguration`), mais o apoio comum `FrontdeskTestSupport`.
  - **Limites até o M10:** o check-out só aceita saldo zero por pagamento (sem transferência para contas a receber). A captura da caução é feita antes, pelo `billing`; a nota fiscal é do M7; a tarefa de limpeza é do M6, pelo `GuestCheckedOut`.
  - **Risco residual:** as contas da reserva são travadas uma a uma, não em ordem de id. Um lançamento roteado simultâneo pode dar deadlock (`500`, raro).
- O `frontdesk` usa do `rates` só os tipos `RatePlanId`, `GuaranteeType`, `PackageId` e `PackageCharge`, nunca a `RatesApi`. O `ModularityTest` confere os quatro.

### Para [[ZenyHotelManager - Módulo billing (contas, roteamento e taxa de serviço)]] — complementa

- **Lançamento idempotente** (M5 E04, H14):
  - `NewPosting.sourceReference` é opcional, com o mesmo valor em `PostingSummary.sourceReference`.
  - No banco: coluna `billing.posting.source_reference`, `CHECK posting_source_reference_ck` (`^[A-Za-z0-9._:-]{1,200}$`) e índice único parcial `posting_source_reference_uk`, na migração `billing/V2026_10_22_2330__add_posting_source_reference.sql`.
  - Com uma chave já gravada, a `BillingApi.post` devolve o lançamento existente, com a taxa de serviço dele, sem gravar nem auditar (`audit.noChanges()`), mesmo com a conta encerrada. A busca roda sob a trava da conta pedida, depois do roteamento e antes do `requireOpen`. Chave inválida: `400 POSTING_INVALID`, campo `sourceReference`.
  - A API HTTP de lançamentos não mudou.
- **Nota obrigatória para o M6:** o fechamento usa a **mesma chave** do check-out, separa os inclusos da hospedagem e lança os inclusos sem taxa de serviço. A repetição é silenciosa: o lançamento existente volta mesmo se o valor pedido for outro, então confira o valor no M6.

### Para [[ZenyHotelManager - Módulo billing (caixa, pagamentos, caução e encerramento)]] — complementa

- `BillingApi.unsettledCardPreAuthorizations(folioId)` (M5 E04, H12): as cauções nem capturadas por inteiro nem liberadas, por id, com a situação calculada agora (inclusive `EXPIRED`). Sem trava e sem permissão; conta inexistente devolve lista vazia.
- `BillingApi.releaseCardPreAuthorization(folioId, id)`: as regras de `…/release` menos a permissão, auditada `billing.card-pre-authorization.release`, na transação de quem chama. Trava a conta e depois a caução; vale com a conta encerrada e depois da validade. Já encerrada: `409 PRE_AUTHORIZATION_SETTLED`. De outra conta: `404 PRE_AUTHORIZATION_NOT_FOUND`.

## Contexto

Execução do roadmap M5 pelo prompt de execução, com o plugin superpowers (plano, um implementador e um revisor por tarefa, e uma revisão final no modelo mais capaz). Decisões da etapa tomadas pela opção recomendada, em nome do usuário (delegado ao orquestrador). As que mudam a referência ficam pendentes de confirmação na entrevista do fim do lote:
- os inclusos lançados à parte e sem taxa de serviço;
- o problema de saldo com as cobranças pendentes;
- a liberação das cauções vencidas.

## Origem

- Repositório `/home/caio/repos/ZenyHotelManager`, branch `roadmap/m5-recepcao-fnrh`, commits `1955898`, `b944c4a`, `27c1ab1`, `7ad294c`, `99c5bd7` e `51a0533` (mais o commit de fechamento da etapa).
- Handoff completo em `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`, seção E04, "Evidências e handoff"; plano em `docs/superpowers/plans/2026-10-22-m5-recepcao-fnrh-e04.md`.

## Por que registrar

Mantém a referência técnica do projeto em dia (protocolo de atualização por capturas do hub), principalmente a nota obrigatória para o M6 e o novo comportamento idempotente da `BillingApi`.

## Limitações e incertezas

- A branch ainda não foi integrada à `main`. Se o usuário descartar ou mudar a branch, este texto deixa de valer.
- As três decisões listadas em "Contexto" ainda podem mudar na entrevista. Uma mudança gera uma captura complementar.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Hospedagem e recepção]]
- [[ZenyHotelManager - Módulo billing (contas, roteamento e taxa de serviço)]]
- [[ZenyHotelManager - Módulo billing (caixa, pagamentos, caução e encerramento)]]
