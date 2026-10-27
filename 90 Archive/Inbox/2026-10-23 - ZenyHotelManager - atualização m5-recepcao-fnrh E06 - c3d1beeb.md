---
type: capture
status: archived
created: 2026-10-23
capture_id: c3d1beeb-2076-413c-af63-4e1e43af516f
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E06

## Conteúdo capturado

Resumo do agente (orquestrador do lote M5, sessão externa no repositório `/home/caio/repos/ZenyHotelManager`): a etapa E06 (recados) foi concluída na branch `roadmap/m5-recepcao-fnrh`, que ainda não foi integrada à `main`. Complementa as capturas anteriores do mesmo lote: [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh E04 - 23ba6833]] e [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh E05 - 0ebc2e6a]].

### Para [[ZenyHotelManager]] (hub), seção "Estado" — substitui a linha do M5 das capturas anteriores

- M5 em andamento: E01 a E03 já estão na `main` (até `a6c0f03`). **E04, E05 e E06 estão concluídas na branch `roadmap/m5-recepcao-fnrh`** (commits `1955898`..`3dfeafe` e os de fechamento, de 2026-10-23), à espera da decisão de integração do usuário. As próximas elegíveis são E07 (FNRH: configuração e adaptador) e E10 (impressão, com revisão humana). A E08 depende da E07, e a E09 segue bloqueada (Q-12).

### Para [[ZenyHotelManager - Hospedagem e recepção]] — complementa

- **Recados** (RF-REC-07, SPEC §8.2.6 `Trace`, M5 E06). É o **primeiro estado próprio do `frontdesk`**: schema `frontdesk` (criado pelo Flyway a partir da pasta) e migrações `frontdesk/V2026_10_23_1200__create_traces.sql` e `…1201__grant_frontdesk_to_app_role.sql`.
  - **Tabela `frontdesk.trace`:**
    - Colunas: setor (`department_id`), vencimento (`due_on`), texto de 1 a 500 caracteres, `reservation_id` **ou** `room_id` (CHECK: exatamente um), `assignee_user_id` opcional, criação, resolução (`resolved_at` e `resolved_by` juntos) e `version`.
    - Índices: `(due_on, id)`, por setor, por reserva e por UH.
    - Sem `DELETE`: o trigger `trace_refuse_delete` usa `frontdesk.refuse_delete()`.
  - **Código:** domínio `frontdesk/domain/Trace.kt` (`Trace`, `TraceLink`, `TraceRules`), `JdbcTraceStore`, caso de uso `FrontdeskTraceService` e um componente `TraceReferences` para as leituras de outros módulos.
  - **Endpoints** (tag `frontdesk`):
    - `POST /api/v1/traces` cria o recado (`201`, `Location`, `ETag`).
    - `GET /api/v1/traces` lista, com filtros `departmentId`, `dueOn`, `status` (`OPEN`/`RESOLVED`), `reservationId` e `roomId`, por cursor `(due_on, id)`.
    - `GET /api/v1/traces/{id}` lê um recado, com `ETag`.
    - `PUT /api/v1/traces/{id}` altera setor, vencimento, texto e responsável. Exige `If-Match`; o vínculo é fixo; num recado resolvido dá `409 TRACE_ALREADY_RESOLVED`.
    - `POST /api/v1/traces/{id}/resolve` resolve, travando a linha. Resolver de novo dá `409`.
  - **Recusas:** `400 TRACE_INVALID` (texto, vínculo ou vencimento antes da data operacional, com o campo); `UNKNOWN_DEPARTMENT`, `UNKNOWN_RESERVATION`, `UNKNOWN_ROOM` e `UNKNOWN_ASSIGNEE` (`400`); `422 ROOM_INACTIVE`; `404 TRACE_NOT_FOUND`.
  - **Permissões** (escopo `ALL`, nenhuma sensível):
    - `frontdesk.traces.read` e `frontdesk.traces.resolve`: Gerente, Recepcionista, Governanta, Manutenção, Comercial/Eventos, Caixa A&B e Cozinha/Bar.
    - `frontdesk.traces.manage` (criar e alterar): Gerente e Recepcionista.
  - **Responsável:** um usuário vinculado a um colaborador, conferido pela `StaffApi.employeeOfUser`. A resposta traz o nome do colaborador e o do setor, lidos da `StaffApi` a cada leitura.
  - **Privacidade (H10 do M3):** o texto do recado nunca vai para a trilha (só `textLength`, em code points, e `textChanged`), nem para log, problemas ou `toString`. A descrição do campo pede que não se escrevam dados pessoais do hóspede.
  - **Módulo:** o `frontdesk` depende também de `staff`, só por `StaffApi`, `DepartmentId`, `DepartmentSummary` e `EmployeeSummary` (`ModularityTest` e ARCHITECTURE §3.1).

### Para [[ZenyHotelManager - Schemas, migrações e views de relatório]] — complementa

- Schema novo: `frontdesk`, a partir do M5 E06, com a tabela `trace`, `GRANT` no modelo do `reservations` e exclusão física proibida por trigger. A migração `V2026_10_23_1200` teve só o comentário alterado antes da integração. Um banco local que já a aplicou precisa de `flyway repair`.

## Contexto

Execução do lote do M5 com o plugin superpowers. O usuário pediu que toda decisão fosse tomada pela opção recomendada depois de pesar prós e contras. Três decisões da E06 ficam para confirmação na entrevista do fim do lote:
- o responsável como usuário vinculado a um colaborador;
- a permissão de resolver separada, com os modelos que a recebem;
- o vínculo fixo.

## Origem

- Repositório `/home/caio/repos/ZenyHotelManager`, branch `roadmap/m5-recepcao-fnrh`, commits `fb2ae34`, `b56ceaa`, `d938259` e `3dfeafe`, mais o commit de fechamento da etapa.
- Handoff em `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`, seção E06; plano em `docs/superpowers/plans/2026-10-23-m5-recepcao-fnrh-e06.md`.

## Por que registrar

Mantém a referência técnica do projeto em dia, segundo o protocolo de capturas do hub. Registra o primeiro schema próprio do `frontdesk`.

## Limitações e incertezas

- A branch não está integrada à `main`.
- As decisões podem mudar na entrevista.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Hospedagem e recepção]]
- [[ZenyHotelManager - Schemas, migrações e views de relatório]]
- [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh E05 - 0ebc2e6a]]
