---
type: capture
status: archived
created: 2026-11-15
capture_id: b6c7bc32-8f7c-4952-85c0-7e210f2b7f81
---

# ZenyHotelManager - pedido do front PF-02 Histórico do desfazer check-in com a aprovação do superior

## Conteúdo capturado

Pedido do front desktop (`ZenyHotelManager-DesktopFront`) ao servidor (`ZenyHotelManager`), feito pelo brain conforme o ADR 0005 do front (pedidos ao servidor pelo brain) e o formato de "Como pedir" em `docs/pedidos-servidor.md` do front: motivo, operação desejada, etapa do front que espera, commit fixado e prioridade.

**Identificador:** PF-02
**Estado:** aberto (2026-11-15)

### Motivo

Na M2 E06 do front (gate do marco M2), a execução do roteiro da demo contra o servidor fixado mostrou que desfazer um check-in com aprovação de superior (ação sensível, `POST /api/v1/reservations/{id}/undo-check-in` depois do `APPROVAL_REQUIRED`) grava o evento `UNDO_CHECK_IN` no histórico da reserva (`GET /api/v1/reservations/{id}/history`) com `approvalId` e `approvedBy` nulos; o ator vem preenchido. Foi conferido ao vivo, só com leitura, por dois agentes.

O orquestrador do front leu que o servidor passa `null` nesses campos em `StayTransitions.undoCheckIn` (o desenvolvedor citou `StayTransitions.kt:200-207`, no checkout local do servidor). O contrato só declara os campos como anuláveis. Assim, o histórico não mostra quem aprovou o desfazer, o que a trilha de ação sensível deveria registrar.

### Contorno no front

Nenhum código. O roteiro do M2 (`docs/demo/roteiro-m2.md`) deixou de prometer "Com aprovação de superior" na linha do histórico do desfazer e mostra só a mudança de situação ("Situação: Hospedada → Confirmada"). Quando o servidor gravar a aprovação, o app já mostra "Com aprovação de superior" (o rótulo existe no app).

### Operação desejada

No evento `UNDO_CHECK_IN` do histórico da reserva, preencher `approvalId` e `approvedBy` com a aprovação consumida pelo desfazer (como as outras ações sensíveis com aprovação), sem mudar o contrato.

### Etapa do front que espera

Nenhuma depende dele (regra "antes de 17/11 nenhuma etapa depende de pedido"). Quando entregue, o roteiro volta a citar a aprovação no histórico.

### Commit fixado do contrato no front

`57eb5fac5b8a18df01ed4f30e099ab1cd8dcb27b`

### Prioridade

Baixa a média: é trilha de auditoria de ação sensível; a demo não depende.

## Origem

- Projeto: `ZenyHotelManager-DesktopFront`, repositório `/home/caio/repos/ZenyHotelManager-DesktopFront` (branch `roadmap/m2-recepcao-do-dia`).
- Destino do pedido: projeto `ZenyHotelManager` (servidor).
- Referências no front: ADR 0005, `docs/pedidos-servidor.md`, M2 E06.
- Referência no servidor: `StayTransitions.undoCheckIn` (`StayTransitions.kt:200-207`, citado pelo desenvolvedor).
- Data: 2026-11-15.

## Limitações e incertezas

- Resumo do agente: o conteúdo foi repassado pelo orquestrador do front; o escriba não verificou nada nos repositórios (endpoints, ADRs, código citados).
- A causa no código do servidor foi lida no checkout local do servidor, não necessariamente no commit fixado do contrato.
- Os documentos citados existem apenas nos repositórios dos projetos, não foram copiados para o vault.

## Possíveis conexões

- Captura anterior PF-01 (setores dos recados legíveis com `frontdesk.traces.manage`), do mesmo formato de pedido do front ao servidor, arquivada em `90 Archive/Inbox/` (`capture_id` 324e0e8f-f656-496a-b6a8-446fe491e384); não é equivalente, sem complemento.
- Capturas de ZenyHotelManager-DesktopFront (decisões de arquitetura e marcos) na Inbox; sem links por não serem equivalentes.
