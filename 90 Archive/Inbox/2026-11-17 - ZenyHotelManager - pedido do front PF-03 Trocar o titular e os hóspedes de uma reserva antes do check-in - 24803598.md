---
type: capture
status: archived
created: 2026-11-17
capture_id: 24803598-810b-4344-997b-c28c79463e5c
---

# ZenyHotelManager - pedido do front PF-03 Trocar o titular e os hóspedes de uma reserva antes do check-in

## Conteúdo capturado

Pedido do front desktop (`ZenyHotelManager-DesktopFront`) ao servidor (`ZenyHotelManager`), feito pelo brain conforme o ADR 0005 do front (pedidos ao servidor pelo brain): motivo, operação desejada, etapa do front que espera, commit fixado e prioridade.

**Identificador:** PF-03
**Estado:** aberto (2026-11-17)

### Motivo

A tela "Alterar reserva" do front desktop (M3 E03). O `PUT /api/v1/reservations/{id}` altera datas, ocupação, tipo de UH, plano, segmento e pedidos, mas não troca o titular nem os hóspedes, e o contrato não tem outra operação para isso antes do check-in. Hoje, para corrigir o titular ou a lista de hóspedes de uma reserva ainda não hospedada, o recepcionista precisa cancelar e criar outra reserva, o que perde o preço congelado e o histórico.

### Operação desejada

Sugestão; o desenho é do servidor. Uma operação que troque o hóspede titular e a lista dos demais hóspedes de uma reserva enquanto ela não fez check-in. Pode ser o próprio `PUT /api/v1/reservations/{id}` aceitando esses campos, ou uma operação própria (por exemplo `PUT /api/v1/reservations/{id}/guests`).

- Campos: o id do hóspede titular e os ids dos demais hóspedes.
- `ETag`/`If-Match` (412 tratado), como as outras escritas da reserva.
- Registro no histórico da reserva (`GET /api/v1/reservations/{id}/history`).
- Sem recalcular o preço congelado quando a ocupação não muda.

### Etapa do front que espera

M3 E03 (Nova reserva e alteração). Não depende: quando entregue, a tela de alteração ganha a troca de titular e de hóspedes.

### Commit fixado do contrato no front

`5e06f16d51ff9913f0da09df8f62639996cd6c52` (`api/server-pin.properties`)

### Prioridade

Baixa, não bloqueante.

## Contexto

Decisão do usuário em 2026-11-17, por entrevista no fim do lote do marco M3 do front (decisão D1 de `docs/roadmaps/roadmap-m3-reservas.md`). Pedido não bloqueante: nenhuma etapa do front depende dele.

## Origem

- Projeto: `ZenyHotelManager-DesktopFront`, repositório `/home/caio/repos/ZenyHotelManager-DesktopFront`.
- Destino do pedido: projeto `ZenyHotelManager` (servidor).
- Referências no front: ADR 0005, `docs/roadmaps/roadmap-m3-reservas.md` (D1), M3 E03.
- Data: 2026-11-17.

## Limitações e incertezas

- Resumo do agente: o conteúdo foi repassado pelo orquestrador do front; o escriba não verificou endpoints, contrato nem documentos citados.
- Os documentos citados existem apenas no repositório do front, não foram copiados para o vault.

## Possíveis conexões

- Capturas anteriores PF-01 (`capture_id` 324e0e8f-f656-496a-b6a8-446fe491e384) e PF-02 (`capture_id` b6c7bc32-8f7c-4952-85c0-7e210f2b7f81), arquivadas em `90 Archive/Inbox/`, do mesmo formato; não são equivalentes, sem complemento.
- Irmã desta captura: PF-04 (prévia da multa de cancelamento), publicada na mesma data.
