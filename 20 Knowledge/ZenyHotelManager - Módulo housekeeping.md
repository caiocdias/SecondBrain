---
type: knowledge
status: processed
created: 2026-11-16
projects:
  - "[[ZenyHotelManager]]"
sources:
  - "[[2026-11-16 - ZenyHotelManager - atualização m6-operacao-fechamento E01 - dd5e01e3]]"
---
# ZenyHotelManager - Módulo housekeeping

Referência técnica do projeto [[ZenyHotelManager]]. Governança: tipos de limpeza com créditos por tipo de UH e faxinas programadas por UH ou área. Estado: M6 E01 concluída em 2026-11-16 (primeira etapa do módulo), na branch `roadmap/m6-operacao-fechamento`, ainda fora da `main`; a geração de tarefas (E02) e o uso do `recordDone` (E04) vêm depois.

Referências como "ARCHITECTURE §x", "SPEC §x", "Hn", "Q-nn" e "Dn" apontam para `docs/ARCHITECTURE.md`, `docs/SPEC.md` e `docs/roadmaps/roadmap-m6-operacao-fechamento.md` (seção "E01") do repositório. Texto da captura de fechamento da E01 (resumo do agente a partir do material do orquestrador do lote, derivado do handoff; o código e os números do gate não foram reconferidos por ele), integrado sem resumo. O estado e as decisões do lote estão em [[ZenyHotelManager - Estado por marco]] ("M6 E01"). As notas do curador estão marcadas como tal.

---

## Camada e dependências

- **Pacote:** `com.zeny.hotel.housekeeping`, na camada Operação, com `@ApplicationModule(allowedDependencies = ["shared", "hotel", "rooms", "checklists"])`. É um subconjunto da linha da ARCHITECTURE §3.1, e o `ModularityTest` exige que as dependências usadas sejam exatamente as declaradas. O módulo usa o `rooms` e o `checklists` só pelas APIs públicas. O `checklists` não conhece o `housekeeping` e trata o id do tipo de limpeza como opaco.

## Arquivos

- `HousekeepingModule.kt`, `HousekeepingPermissions.kt` e `HousekeepingTypes.kt` (`CleaningTypeId`, `ScheduledCleaningId`, `CleaningTypeKey`, `HousekeepingErrorCodes`);
- `domain/CleaningType.kt` (agregado com os créditos, mais `HousekeepingRecord` e `HousekeepingRules`) e `domain/ScheduledCleaning.kt`;
- `application/CleaningTypesService.kt` (casos de uso, a porta `CleaningTypeStore` com `forUpdate(id)` e `hasActiveSchedules(id)`, e o bean de permissões) e `application/ScheduledCleaningsService.kt` (com a porta `ScheduledCleaningStore`);
- `infrastructure/CleaningTypePersistence.kt` e `infrastructure/ScheduledCleaningPersistence.kt` (escrita por JPA com `saveAndFlush`, leitura por `JdbcClient`, restrições convertidas em `409` pelo nome);
- `web/CleaningTypesController.kt` e `web/ScheduledCleaningsController.kt` (tag `housekeeping`).

## Banco

Schema `housekeeping`, com as migrações `db/migration/housekeeping/V2026_11_15_1000__create_housekeeping.sql` e `V2026_11_15_1001__grant_housekeeping_to_app_role.sql` (ver [[ZenyHotelManager - Schemas, migrações e views de relatório]], "Schema `housekeeping`").

- Tabelas: `cleaning_type` (`system_key` com CHECK nos seis valores e `updatable=false` no mapeamento; `default_priority` de 1 a 5; `linen_change_every_nights` de 1 a 60 ou nulo; `checklist_template_id` opcional, sem FK entre schemas; `version`), `cleaning_type_credit` (`credits` de 1 a 100, por `room_type_id`) e `scheduled_cleaning` (`room_id` ou `area_id`, exatamente um; `frequency_days` de 1 a 365; `last_done_on`; `next_due_on`; `active`).
- O índice único parcial `scheduled_cleaning_active_uk` garante no máximo uma faxina ativa por (local, tipo).
- O trigger `housekeeping.refuse_delete` recusa DELETE em `cleaning_type` e `scheduled_cleaning`. O papel da aplicação só tem DELETE em `cleaning_type_credit` (`DatabaseRolesTest`, `NO_DELETE_TABLES`).

## Carga inicial (D5)

Com chave estável `key`:

| key | nome | inspeção | prioridade | enxoval | ativo |
|---|---|---|---|---|---|
| `CHECKOUT` | Saída | sim | 4 | — | sim |
| `STAYOVER` | Permanência | não | 3 | 3 noites | sim |
| `TOUCH_UP` | Retoque | não | 2 | — | sim |
| `DEEP_CLEAN` | Faxina pesada | sim | 1 | — | sim |
| `PRE_ARRIVAL` | Pré-chegada | sim | 4 | — | sim |
| `TURNDOWN` | Abertura de cama | não | 2 | — | não (H9, Q-14) |

O gestor troca código, nome e configuração e pode desativar um tipo da carga; a `key` nunca muda. Os testes nunca alteram os seis tipos.

## API

- `/api/v1/cleaning-types`: `GET` com cursor por código e filtro `active`; `GET /{id}` com `ETag`; `POST` (`201` com `Location` e `ETag`); `PUT /{id}` com `If-Match` obrigatório (`412`/`428`); `POST /{id}/deactivate` e `/reactivate`.
- `/api/v1/scheduled-cleanings`: `GET` com cursor por (`nextDueOn`, `id`) e filtro `active`; `GET /{id}`; `POST`; `PUT /{id}`, que muda só `cleaningTypeId` e `frequencyDays`; `/deactivate` e `/reactivate`.
- Nenhuma das duas tem `DELETE`. A resposta do tipo traz `key` (`x-extensible-enum`) e `missingCreditRoomTypeIds`, calculado na leitura (D6).

## Regras

- **D1:** vínculo opcional a um modelo de checklist do contexto `HOUSEKEEPING`, que precisa estar ativo e publicado no momento do vínculo (conferido pela `ChecklistsApi.template(id)`, nova; ver [[ZenyHotelManager - Módulo checklists]]). Um modelo vinculado que depois é desativado continua vinculado. Na E04, a precedência é: vínculo ativo e publicado → `ChecklistsApi.resolveTemplate(HOUSEKEEPING, …cleaningTypeId…)` → sem checklist.
- **D6:** um tipo ativo sem crédito para um tipo de UH ativo não é recusado e aparece em `missingCreditRoomTypeIds`. Crédito para tipo de UH desativado é aceito; para tipo de UH inexistente, é `422`.
- **D7:** `nextDueOn = lastDoneOn + frequencyDays` ou, sem `lastDoneOn`, a data operacional (`HotelApi.currentBusinessDate()`). O `lastDoneOn` não pode ser depois da data operacional. O `recordDone` do domínio nunca faz o `lastDoneOn` voltar; a E04 vai usá-lo.
- **D8:** referência inexistente no corpo dá `422` (tipo de UH, modelo, local, tipo de limpeza). O padrão do resto do projeto é `400 UNKNOWN_*`, e a divergência vai ao arquiteto.
- **Reativação:** a faxina reativada mantém o `nextDueOn` antigo, que pode estar vencido; a E02 decide se recalcula. O PUT que troca o tipo exige tipo ativo mesmo com a faxina inativa.
- **Concorrência:** `CleaningTypeStore.forUpdate` faz `SELECT … FOR NO KEY UPDATE` (o `PESSIMISTIC_WRITE` do Hibernate 7). Ele não conflita com o `FOR KEY SHARE` que a FK de um INSERT toma, por isso criar, trocar o tipo ou reativar uma faxina trava o tipo antes de conferir `active`, e a desativação do tipo trava a mesma linha e confere `hasActiveSchedules`. A ordem das travas é sempre faxina → tipo. Resultado: nunca sobra faxina ativa num tipo inativo, o que os testes de corrida provam.
- O limite é de 200 créditos por corpo, escolha do desenvolvedor que vai ao handoff.
- Os nomes do `housekeeping` recusam NUL (`400 HOUSEKEEPING_DATA_INVALID`; regra do cursor de texto em [[ZenyHotelManager - Convenções de API]], "NUL na chave de texto do cursor").

D1, D5, D8, o limite de 200 créditos e a reativação que mantém o vencimento antigo foram tomadas pela opção recomendada, **sem confirmação do usuário** ([[ZenyHotelManager - Estado por marco]], "M6 E01").

## Códigos de erro

`CLEANING_TYPE_NOT_FOUND`, `CLEANING_TYPE_CODE_ALREADY_IN_USE` (409), `CLEANING_TYPE_INACTIVE`, `CLEANING_TYPE_HAS_ACTIVE_SCHEDULES`, `CLEANING_TYPE_UNKNOWN_ROOM_TYPE`, `CLEANING_TYPE_CREDIT_DUPLICATED` (400), `CLEANING_TYPE_UNKNOWN_CHECKLIST_TEMPLATE`, `CLEANING_TYPE_CHECKLIST_CONTEXT_INCOMPATIBLE`, `CLEANING_TYPE_CHECKLIST_TEMPLATE_INACTIVE`, `CLEANING_TYPE_CHECKLIST_TEMPLATE_NOT_PUBLISHED`, `SCHEDULED_CLEANING_NOT_FOUND`, `SCHEDULED_CLEANING_ALREADY_EXISTS` (409), `SCHEDULED_CLEANING_LOCATION_INVALID` (400), `SCHEDULED_CLEANING_UNKNOWN_LOCATION`, `SCHEDULED_CLEANING_LOCATION_INACTIVE`, `SCHEDULED_CLEANING_LAST_DONE_IN_FUTURE`, `SCHEDULED_CLEANING_UNKNOWN_CLEANING_TYPE` e `HOUSEKEEPING_DATA_INVALID` (400). Os 422 de referência são os listados em D6 e D8.

## Permissões e auditoria

- `housekeeping.config.read` e `housekeeping.config.manage`, só escopo `ALL`, não sensíveis, nos modelos Gerente (MANAGER) e Governanta (HOUSEKEEPER) (ver [[ZenyHotelManager - Segurança, autenticação e autorização]], "Permissões do `housekeeping`"). A autorização vem antes de qualquer checagem que revele estado.
- As ações de auditoria são `housekeeping.cleaning-type.<create|update|deactivate|reactivate>` e `housekeeping.scheduled-cleaning.<create|update|deactivate|reactivate>`, com retrato só da configuração.

## Testes

- `CleaningTypesApiTest`, `CleaningTypesApiAttackTest`, `CleaningTypesEditAttackTest`, `ScheduledCleaningsApiTest`, `ScheduledCleaningsAttackTest`, `HousekeepingSchemaTest`, `HousekeepingSchemaAttackTest`, `HousekeepingPersistenceTest`, `HousekeepingPermissionsTest`, `HousekeepingTestSupport` e os testes de domínio em `housekeeping/domain`.
- Dois testes fixam comportamento que o arquiteto pode endurecer: a falta de trava num INSERT feito direto por SQL (`CleaningTypesEditAttackTest`, teste 7) e a leniência do Jackson (`ScheduledCleaningsAttackTest`, teste 12).

## Notas para as próximas etapas

- o N de "UH vaga há N dias" da pré-chegada fica com a E02;
- o `CreditRule` é só por tipo de UH, e a faxina de área não tem créditos;
- a E02 decide o que gera para um tipo com chave desativado;
- a E02 garante "chegada acima de permanência" mesmo com prioridades editadas;
- a E02 não deve gerar uma tarefa por dia enquanto houver uma aberta;
- a E02 ignora local inativo, porque o `rooms` não desativa a faxina.

*Nota do curador (conferência por `git` em 2026-11-16, só leitura, no `0d3eba1`, branch `roadmap/m6-operacao-fechamento`):* os onze arquivos de `housekeeping/` e as duas migrações existem com os nomes acima; `HousekeepingModule.kt` declara `allowedDependencies = ["shared", "hotel", "rooms", "checklists"]`; `HousekeepingTypes.kt` tem os 18 códigos de erro listados; `HousekeepingPermissions.kt` declara `housekeeping.config.read` e `housekeeping.config.manage`; a carga inicial da `V2026_11_15_1000` confere com a tabela (nome, inspeção, prioridade, enxoval e ativo dos seis tipos); os dez arquivos de teste citados existem, e em `housekeeping/domain` há `CleaningTypeDomainTest`, `ScheduledCleaningDomainTest` e `HousekeepingDomainBoundaryTest`. O corpo dos casos de uso, das travas e dos testes não foi lido. Na ponta da branch (`adba5e3`, 2026-11-16, "Handoff da E02 do M6: lote parado na onda de correção final"), a **M6 E02 está `#em-andamento`, ainda sem captura**: `HousekeepingModule.kt` já declara também `reservations` em `allowedDependencies`, e há as migrações `V2026_11_16_1000__create_housekeeping_task.sql` e `V2026_11_16_1001__grant_housekeeping_task_to_app_role.sql`. Esta nota descreve o módulo como a E01 o deixou.

---

## Proveniência

- 2026-11-16 — [[2026-11-16 - ZenyHotelManager - atualização m6-operacao-fechamento E01 - dd5e01e3]] (capture_id: dd5e01e3-3041-431b-81f8-3b801eec3fff): nota criada com o módulo `housekeeping` da M6 E01 (item 1 da captura); nota do curador com a conferência por `git`.
