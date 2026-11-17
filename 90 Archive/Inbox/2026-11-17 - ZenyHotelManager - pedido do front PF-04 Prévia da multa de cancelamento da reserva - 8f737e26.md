---
type: capture
status: archived
created: 2026-11-17
capture_id: 8f737e26-5881-45fe-85ec-163b1285ac0a
---

# ZenyHotelManager - pedido do front PF-04 Prévia da multa de cancelamento da reserva

## Conteúdo capturado

Pedido do front desktop (`ZenyHotelManager-DesktopFront`) ao servidor (`ZenyHotelManager`), feito pelo brain conforme o ADR 0005 do front (pedidos ao servidor pelo brain): motivo, operação desejada, etapa do front que espera, commit fixado e prioridade.

**Identificador:** PF-04
**Estado:** aberto (2026-11-17)

### Motivo

O diálogo "Cancelar reserva" do front desktop (M3 E04). O front nunca calcula preço nem prazo. Hoje o diálogo mostra, antes de confirmar, só os termos da política copiados na reserva (`CancellationTermsResponse`: tipo da multa, horas do prazo) e, depois de cancelar, a multa que o servidor lançou (`CancellationPenaltyResponse`: `amount`, `deadline`, `waived`, `postingId`). O recepcionista não vê, antes de confirmar, quanto será cobrado se cancelar agora nem até quando o cancelamento sai sem multa.

### Operação desejada

Sugestão; o desenho é do servidor. Uma leitura da prévia da multa, por exemplo `GET /api/v1/reservations/{id}/cancellation-preview`, que devolva o valor devido se a reserva for cancelada agora (`amount`, decimal em BRL, zero antes do prazo) e o prazo (`deadline`, date-time): os mesmos campos de `CancellationPenaltyResponse`, sem lançamento.

- Permissão: a de leitura de reservas ou a do cancelamento.
- Para reserva que não pode ser cancelada (já cancelada, no-show, encerrada): erro `409` com código próprio.

### Etapa do front que espera

M3 E04 (Cancelar, reativar e pendências). Não depende: quando entregue, o diálogo passa a mostrar o valor e o prazo antes da confirmação.

### Commit fixado do contrato no front

`5e06f16d51ff9913f0da09df8f62639996cd6c52` (`api/server-pin.properties`)

### Prioridade

Baixa, não bloqueante.

## Contexto

Decisão do usuário em 2026-11-17, por entrevista no fim do lote do marco M3 do front (decisão D2 de `docs/roadmaps/roadmap-m3-reservas.md`). Pedido não bloqueante: nenhuma etapa do front depende dele.

## Origem

- Projeto: `ZenyHotelManager-DesktopFront`, repositório `/home/caio/repos/ZenyHotelManager-DesktopFront`.
- Destino do pedido: projeto `ZenyHotelManager` (servidor).
- Referências no front: ADR 0005, `docs/roadmaps/roadmap-m3-reservas.md` (D2), M3 E04.
- Data: 2026-11-17.

## Limitações e incertezas

- Resumo do agente: o conteúdo foi repassado pelo orquestrador do front; o escriba não verificou endpoints, contrato nem documentos citados.
- Os documentos citados existem apenas no repositório do front, não foram copiados para o vault.

## Possíveis conexões

- Capturas anteriores PF-01 (`capture_id` 324e0e8f-f656-496a-b6a8-446fe491e384) e PF-02 (`capture_id` b6c7bc32-8f7c-4952-85c0-7e210f2b7f81), arquivadas em `90 Archive/Inbox/`, do mesmo formato; não são equivalentes, sem complemento.
- Irmã desta captura: PF-03 (trocar titular e hóspedes antes do check-in), publicada na mesma data.
