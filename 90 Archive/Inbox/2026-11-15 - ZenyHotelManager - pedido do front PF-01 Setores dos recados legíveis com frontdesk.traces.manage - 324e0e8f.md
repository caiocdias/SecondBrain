---
type: capture
status: archived
created: 2026-11-15
capture_id: 324e0e8f-f656-496a-b6a8-446fe491e384
---

# ZenyHotelManager - pedido do front PF-01 Setores dos recados legíveis com frontdesk.traces.manage

## Conteúdo capturado

Pedido do front desktop (`ZenyHotelManager-DesktopFront`) ao servidor (`ZenyHotelManager`), feito pelo brain conforme o ADR 0005 do front (pedidos ao servidor pelo brain) e o formato de "Como pedir" em `docs/pedidos-servidor.md` do front: motivo, operação desejada, etapa do front que espera, commit fixado e prioridade.

**Identificador:** PF-01
**Estado:** aberto (2026-11-15)

### Motivo

Na M2 E05 do front (Recados), a Recepcionista cria e altera recados (`frontdesk.traces.manage`, D2 da M5 E06 do servidor), e o `POST /api/v1/traces` exige `departmentId`. Porém a única forma de listar os setores, `GET /api/v1/departments`, exige `staff.employees.read`, que no modelo padrão só Gerente e Governanta têm (`StaffPermissions`). Com o modelo padrão, a Recepcionista não consegue escolher o setor e, portanto, não cria recado pelo app. Os ids dos seis setores pré-carregados só existem na migration do servidor, fora do contrato, e o front não os embute (ADR 0002 do front).

### Contorno no front (sem depender do pedido)

O `demo-seed` concede à Recepcionista da demo uma role extra "Consulta de setores (demo)" com só `staff.employees.read` (que também abre colaboradores — nome, e-mail, telefone — e turnos pela API). O app trata o 403 dos setores com uma mensagem e desabilita a criação. Decisão do orquestrador, revisável pelo usuário.

### Operação desejada (uma das duas, a critério do servidor)

- (a) `GET /api/v1/departments` legível também com `frontdesk.traces.read` ou `frontdesk.traces.manage` (só id e nome); ou
- (b) uma leitura própria, por exemplo `GET /api/v1/traces/departments`, devolvendo `id` e `name` dos setores ativos, com `frontdesk.traces.manage`.

### Etapa do front que espera

Nenhuma depende dele (regra "antes de 17/11 nenhuma etapa depende de pedido"). Quando entregue, a M2 E05 pode tirar a role extra do seed.

### Commit fixado do contrato no front

`57eb5fac5b8a18df01ed4f30e099ab1cd8dcb27b`

### Prioridade

Média: afeta toda recepcionista com o modelo padrão de role; a demo usa o contorno.

## Origem

- Projeto: `ZenyHotelManager-DesktopFront`, repositório `/home/caio/repos/ZenyHotelManager-DesktopFront` (branch `roadmap/m2-recepcao-do-dia`).
- Destino do pedido: projeto `ZenyHotelManager` (servidor).
- Referências no front: ADR 0005, ADR 0002 e `docs/pedidos-servidor.md`.
- Referências no servidor: M5 E06 (D2), `StaffPermissions`, migration dos setores.
- Data: 2026-11-15.

## Limitações e incertezas

- Resumo do agente: o conteúdo foi repassado pelo orquestrador do front; o escriba não verificou as permissões, endpoints nem ADRs citados no código dos dois repositórios.
- O contorno é uma decisão do orquestrador, revisável pelo usuário.
- Os documentos citados existem apenas nos repositórios dos projetos, não foram copiados para o vault.

## Possíveis conexões

- Capturas anteriores de ZenyHotelManager sobre a M5 (recepção e frontdesk) e de ZenyHotelManager-DesktopFront (decisões de arquitetura), na Inbox e no arquivo; sem links por não serem equivalentes.
