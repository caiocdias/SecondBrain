---
type: capture
status: archived
created: 2026-10-23
capture_id: 0ebc2e6a-f82e-4b92-9941-f42708feb2a2
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E05

## Conteúdo capturado

Resumo do agente (orquestrador do lote M5, sessão externa no repositório `/home/caio/repos/ZenyHotelManager`): a etapa E05 (troca de UH, extensão, redução e early check-in) foi concluída na branch `roadmap/m5-recepcao-fnrh`, ainda não integrada à `main`. Este registro complementa a captura anterior do mesmo lote, [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh E04 - 23ba6833]] (capture_id `23ba6833-5674-4a22-aacd-3a26bf55f9bf`), e corrige um ponto dela (o check-out, abaixo).

### Para [[ZenyHotelManager]] (hub), seção "Estado" — substitui a linha do M5 da captura da E04

- M5 em andamento: E01 a E03 na `main` (até `a6c0f03`); **E04 e E05 concluídas na branch `roadmap/m5-recepcao-fnrh`** (commits `1955898`..`a439886`, 2026-10-23), à espera da decisão de integração do usuário. Próxima etapa elegível: E06 (recados).

### Para [[ZenyHotelManager - Hospedagem e recepção]] — complementa

- **Transições** (`reservations`, M5 E05):
  - `ReservationsApi.moveRoom(id, move, expectedVersion: Long? = null)` e `ReservationsApi.checkOut(id, expectedVersion: Long? = null)`: com valor, a versão é conferida logo depois de travar a reserva (`requireCurrentVersion`, `412`, o mesmo do `PUT`).
  - **Redução do hospedado sem restrições de venda:** um `PUT` de uma reserva `IN_HOUSE` que só antecipa a saída não confere estadia mínima nem CTA/CTD. A regra é `StayRepricing.onlyShortens`, com a mesma estadia e só a saída menor. A extensão continua conferindo a venda.
  - A ocupação do hospedado continua fixa (`409 IN_HOUSE_STAY_FIXED`). A troca de UH continua só para o mesmo tipo (`422 ROOM_TYPE_MISMATCH`); o upgrade está pendente de decisão do usuário.
- **Recepção: troca de UH** (RF-REC-04, M5 E05; `frontdesk/application/RoomMoveService.kt`, `FrontdeskRoomMoveService`, e `frontdesk/domain/RoomMoveTariffs.kt`):
  - **Endpoint:** `POST /api/v1/reservations/{id}/room-moves` (`@Idempotent`, `If-Match` obrigatório, `frontdesk.stays.move` para Gerente e Recepcionista, `operationId` `moveReservationRoom`). Corpo `{roomId, reason, tariff=KEEP|RECALCULATE}`. A resposta traz `{reservation, fromRoom, toRoom, tariff, remainingBefore, remainingAfter, difference}`, com o `ETag` novo; a diferença é calculada sobre as noites a partir da data operacional.
  - **Ordem:**
    1. Permissão, reserva e `If-Match` contra a versão lida (`412`).
    2. Só uma reserva hospedada (`409`, ação `MOVE_ROOM`).
    3. UH nova existente (`400 UNKNOWN_ROOM`) e pronta sem trava (`409 ROOM_NOT_READY`); se for a mesma UH, pula a prontidão, para dar `422 ROOM_MOVE_SAME_ROOM`.
    4. `moveRoom` com `expectedVersion`.
    5. As duas UHs em ordem crescente de id: a origem `markVacant(CHECK_OUT)`, que fica Vaga + Suja; o destino `markOccupiedIfReady(CHECK_IN)` com o número de hóspedes da origem.
    6. Trilha `frontdesk.stay.room-move`.
  - **Travas:** reserva → travas consultivas das UHs (`reservations`) → linhas das UHs. Tudo numa transação.
  - **Testes:** `FrontdeskRoomMoveApiTest`, com as corridas de duas trocas e de troca × check-in no mesmo destino e a de check-out × troca na mesma reserva; `RoomMoveDomainTest`.
- **Early check-in** (RF-REC-03, RN-11, H13):
  - **Pedido e resposta:** campo opcional `earlyCheckInFee` (dinheiro em texto) no `POST …/check-in` e no `POST /api/v1/walk-ins`, com `earlyCheckIn` na resposta.
  - **Conferência:** antes de qualquer escrita, por `EarlyLateFeeRules.acceptedFee` (o antigo `LateCheckOutRules`, que agora serve ao early e ao late). As recusas são `409 EARLY_LATE_FEE_CHANGED` e `422 EARLY_LATE_NOT_OFFERED`; um valor não positivo dá `400`.
  - **Lançamento:** no `ROOM_CHARGE`, como "Early check-in", origem `MANUAL`, em `CheckInSteps.complete`, depois da caução e antes da ocupação, com o valor já aceito passado explicitamente.
  - **Desfazer:** o early lançado continua na conta, e um novo check-in lança outro; o estorno é pelo `billing`.
- **Check-out** (corrige a captura da E04):
  - O check-out passa `expectedVersion` = a versão lida a `ReservationsApi.checkOut`. Se a reserva mudou entre a leitura e a trava (uma troca de UH simultânea, por exemplo), a resposta é `409 RESERVATION_CHANGED` (código novo do `frontdesk`: leia de novo e repita) e tudo é desfeito.
  - Sem isso, um check-out que esperava atrás de uma troca vagava a UH antiga e deixava a nova Ocupada sem hóspede.
- **Walk-in com hóspede mesclado:** a reserva nasce com o sobrevivente em tudo (`201`), coberta por teste.
- **Testes de ponta a ponta do hospedado:** `FrontdeskInHouseChangeApiTest` cobre a extensão com a UH livre, a extensão sem disponibilidade, a extensão sobre a UH de outra reserva, a redução e a ocupação fixa.

### Para [[ZenyHotelManager - Testes de integração]] — complementa

- `ReservationSearchApiTest` ("every search filter and every list is served by an index…") é intermitente: no filtro "period", o planner às vezes escolhe `reservation_arrival_idx` em vez de `reservation_stay_period_idx`, e o teste exige um índice exato no banco compartilhado. A sugestão, ainda não aplicada, é aceitar os dois índices nesse filtro.
- `CheckInRendezvousProbe` virou um `@Aspect` de teste que também sincroniza `RoomMoved`, `GuestCheckedOut` e as chamadas `checkOut`/`moveRoom` (corridas determinísticas). O apoio comum dos testes de recepção é `FrontdeskTestSupport`.

## Contexto

O lote do M5 foi executado com o plugin superpowers. O usuário pediu, durante o lote, que toda decisão necessária fosse tomada pela opção recomendada depois de pesar prós e contras.

Decisões da E05 que mudam a referência e ficam para confirmação na entrevista do fim do lote:
- o upgrade de tipo pendente;
- a ocupação do hospedado fixa;
- a redução sem restrições de venda;
- a origem `CHECK_OUT` no histórico da UH;
- o early também no walk-in;
- o código `RESERVATION_CHANGED`.

## Origem

- Repositório `/home/caio/repos/ZenyHotelManager`, branch `roadmap/m5-recepcao-fnrh`, commits `a15672a`, `1a1b9b1`, `515d0a1`, `5aa0c9c`, `e692d9f` e `a439886` (mais o commit de fechamento da etapa).
- Handoff completo em `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`, seção E05, "Evidências e handoff"; plano em `docs/superpowers/plans/2026-10-23-m5-recepcao-fnrh-e05.md`.

## Por que registrar

Mantém a referência técnica do projeto em dia (protocolo de atualização por capturas do hub), inclusive a correção do check-out descrito na captura da E04.

## Limitações e incertezas

- A branch não está integrada à `main`.
- As decisões listadas em "Contexto" podem mudar na entrevista.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Hospedagem e recepção]]
- [[ZenyHotelManager - Testes de integração]]
- [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh E04 - 23ba6833]]
