---
type: capture
status: archived
created: 2026-11-16
capture_id: dd5e01e3-3041-431b-81f8-3b801eec3fff
---
# ZenyHotelManager - atualização m6-operacao-fechamento E01

## Conteúdo capturado

Captura de fechamento de etapa do projeto ZenyHotelManager (M6, etapa E01 "Tipos de limpeza, créditos e faxinas programadas", primeira etapa do módulo `housekeeping`). Para cada nota de tema afetada, abaixo está o texto novo ou alterado e se ele **cria**, **complementa** ou **substitui** um trecho. O texto desta captura vale sobre as notas e sobre as capturas anteriores quando tratam do mesmo assunto. Fatos vêm do material do orquestrador do lote (`brain-capture-input.md` da etapa, derivado do handoff da E01); o que é leitura do agente vem rotulado.

Etapa: M6 E01. Branch `roadmap/m6-operacao-fechamento`, commits de `2471691` (exclusivo) a `0d3eba1`, mais os commits de documentação do fechamento. Revisão final: pronto para integrar, sem Crítico nem Importante. Gate `./gradlew build` em `0d3eba1`: 4355 testes, 0 falhas. Data: 2026-11-16.

### 1. Nota NOVA `ZenyHotelManager - Módulo housekeeping` (cria)

A nota não existe no vault (conferido em `20 Knowledge/`). Ela fica ligada ao hub, na lista "Notas do projeto → Módulos" (ver item 6). Texto proposto:

- **Pacote:** `com.zeny.hotel.housekeeping`, na camada Operação, com `@ApplicationModule(allowedDependencies = ["shared", "hotel", "rooms", "checklists"])`. É um subconjunto da linha da ARCHITECTURE §3.1, e o `ModularityTest` exige que as dependências usadas sejam exatamente as declaradas. O módulo usa o `rooms` e o `checklists` só pelas APIs públicas. O `checklists` não conhece o `housekeeping` e trata o id do tipo de limpeza como opaco.
- **Arquivos:**
  - `HousekeepingModule.kt`, `HousekeepingPermissions.kt` e `HousekeepingTypes.kt` (`CleaningTypeId`, `ScheduledCleaningId`, `CleaningTypeKey`, `HousekeepingErrorCodes`);
  - `domain/CleaningType.kt` (agregado com os créditos, mais `HousekeepingRecord` e `HousekeepingRules`) e `domain/ScheduledCleaning.kt`;
  - `application/CleaningTypesService.kt` (casos de uso, a porta `CleaningTypeStore` com `forUpdate(id)` e `hasActiveSchedules(id)`, e o bean de permissões) e `application/ScheduledCleaningsService.kt` (com a porta `ScheduledCleaningStore`);
  - `infrastructure/CleaningTypePersistence.kt` e `infrastructure/ScheduledCleaningPersistence.kt` (escrita por JPA com `saveAndFlush`, leitura por `JdbcClient`, restrições convertidas em `409` pelo nome);
  - `web/CleaningTypesController.kt` e `web/ScheduledCleaningsController.kt` (tag `housekeeping`).
- **Banco:** schema `housekeeping`, com as migrações `db/migration/housekeeping/V2026_11_15_1000__create_housekeeping.sql` e `V2026_11_15_1001__grant_housekeeping_to_app_role.sql`.
  - Tabelas: `cleaning_type` (`system_key` com CHECK nos seis valores e `updatable=false` no mapeamento; `default_priority` de 1 a 5; `linen_change_every_nights` de 1 a 60 ou nulo; `checklist_template_id` opcional, sem FK entre schemas; `version`), `cleaning_type_credit` (`credits` de 1 a 100, por `room_type_id`) e `scheduled_cleaning` (`room_id` ou `area_id`, exatamente um; `frequency_days` de 1 a 365; `last_done_on`; `next_due_on`; `active`).
  - O índice único parcial `scheduled_cleaning_active_uk` garante no máximo uma faxina ativa por (local, tipo).
  - O trigger `housekeeping.refuse_delete` recusa DELETE em `cleaning_type` e `scheduled_cleaning`. O papel da aplicação só tem DELETE em `cleaning_type_credit` (`DatabaseRolesTest`, `NO_DELETE_TABLES`).
- **Carga inicial (D5), com chave estável `key`:**

  | key | nome | inspeção | prioridade | enxoval | ativo |
  |---|---|---|---|---|---|
  | `CHECKOUT` | Saída | sim | 4 | — | sim |
  | `STAYOVER` | Permanência | não | 3 | 3 noites | sim |
  | `TOUCH_UP` | Retoque | não | 2 | — | sim |
  | `DEEP_CLEAN` | Faxina pesada | sim | 1 | — | sim |
  | `PRE_ARRIVAL` | Pré-chegada | sim | 4 | — | sim |
  | `TURNDOWN` | Abertura de cama | não | 2 | — | não (H9, Q-14) |

  O gestor troca código, nome e configuração e pode desativar um tipo da carga; a `key` nunca muda. Os testes nunca alteram os seis tipos.
- **API:**
  - `/api/v1/cleaning-types`: `GET` com cursor por código e filtro `active`; `GET /{id}` com `ETag`; `POST` (`201` com `Location` e `ETag`); `PUT /{id}` com `If-Match` obrigatório (`412`/`428`); `POST /{id}/deactivate` e `/reactivate`.
  - `/api/v1/scheduled-cleanings`: `GET` com cursor por (`nextDueOn`, `id`) e filtro `active`; `GET /{id}`; `POST`; `PUT /{id}`, que muda só `cleaningTypeId` e `frequencyDays`; `/deactivate` e `/reactivate`.
  - Nenhuma das duas tem `DELETE`. A resposta do tipo traz `key` (`x-extensible-enum`) e `missingCreditRoomTypeIds`, calculado na leitura (D6).
- **Regras:**
  - **D1:** vínculo opcional a um modelo de checklist do contexto `HOUSEKEEPING`, que precisa estar ativo e publicado no momento do vínculo. Um modelo vinculado que depois é desativado continua vinculado. Na E04, a precedência é: vínculo ativo e publicado → `ChecklistsApi.resolveTemplate(HOUSEKEEPING, …cleaningTypeId…)` → sem checklist.
  - **D6:** um tipo ativo sem crédito para um tipo de UH ativo não é recusado e aparece em `missingCreditRoomTypeIds`. Crédito para tipo de UH desativado é aceito; para tipo de UH inexistente, é `422`.
  - **D7:** `nextDueOn = lastDoneOn + frequencyDays` ou, sem `lastDoneOn`, a data operacional (`HotelApi.currentBusinessDate()`). O `lastDoneOn` não pode ser depois da data operacional. O `recordDone` do domínio nunca faz o `lastDoneOn` voltar; a E04 vai usá-lo.
  - **D8:** referência inexistente no corpo dá `422` (tipo de UH, modelo, local, tipo de limpeza). O padrão do resto do projeto é `400 UNKNOWN_*`, e a divergência vai ao arquiteto.
  - **Reativação:** a faxina reativada mantém o `nextDueOn` antigo, que pode estar vencido; a E02 decide se recalcula. O PUT que troca o tipo exige tipo ativo mesmo com a faxina inativa.
  - **Concorrência:** `CleaningTypeStore.forUpdate` faz `SELECT … FOR NO KEY UPDATE` (o `PESSIMISTIC_WRITE` do Hibernate 7). Ele não conflita com o `FOR KEY SHARE` que a FK de um INSERT toma, por isso criar, trocar o tipo ou reativar uma faxina trava o tipo antes de conferir `active`, e a desativação do tipo trava a mesma linha e confere `hasActiveSchedules`. A ordem das travas é sempre faxina → tipo. Resultado: nunca sobra faxina ativa num tipo inativo, o que os testes de corrida provam.
  - O limite é de 200 créditos por corpo, escolha do desenvolvedor que vai ao handoff.
- **Códigos de erro:** `CLEANING_TYPE_NOT_FOUND`, `CLEANING_TYPE_CODE_ALREADY_IN_USE` (409), `CLEANING_TYPE_INACTIVE`, `CLEANING_TYPE_HAS_ACTIVE_SCHEDULES`, `CLEANING_TYPE_UNKNOWN_ROOM_TYPE`, `CLEANING_TYPE_CREDIT_DUPLICATED` (400), `CLEANING_TYPE_UNKNOWN_CHECKLIST_TEMPLATE`, `CLEANING_TYPE_CHECKLIST_CONTEXT_INCOMPATIBLE`, `CLEANING_TYPE_CHECKLIST_TEMPLATE_INACTIVE`, `CLEANING_TYPE_CHECKLIST_TEMPLATE_NOT_PUBLISHED`, `SCHEDULED_CLEANING_NOT_FOUND`, `SCHEDULED_CLEANING_ALREADY_EXISTS` (409), `SCHEDULED_CLEANING_LOCATION_INVALID` (400), `SCHEDULED_CLEANING_UNKNOWN_LOCATION`, `SCHEDULED_CLEANING_LOCATION_INACTIVE`, `SCHEDULED_CLEANING_LAST_DONE_IN_FUTURE`, `SCHEDULED_CLEANING_UNKNOWN_CLEANING_TYPE` e `HOUSEKEEPING_DATA_INVALID` (400). Os 422 de referência são os listados em D6 e D8.
- **Permissões e auditoria:** `housekeeping.config.read` e `housekeeping.config.manage`, só escopo `ALL`, não sensíveis, nos modelos Gerente (MANAGER) e Governanta (HOUSEKEEPER). A autorização vem antes de qualquer checagem que revele estado. As ações de auditoria são `housekeeping.cleaning-type.<create|update|deactivate|reactivate>` e `housekeeping.scheduled-cleaning.<create|update|deactivate|reactivate>`, com retrato só da configuração.
- **Testes:** `CleaningTypesApiTest`, `CleaningTypesApiAttackTest`, `CleaningTypesEditAttackTest`, `ScheduledCleaningsApiTest`, `ScheduledCleaningsAttackTest`, `HousekeepingSchemaTest`, `HousekeepingSchemaAttackTest`, `HousekeepingPersistenceTest`, `HousekeepingPermissionsTest`, `HousekeepingTestSupport` e os testes de domínio em `housekeeping/domain`. Dois testes fixam comportamento que o arquiteto pode endurecer: a falta de trava num INSERT feito direto por SQL (`CleaningTypesEditAttackTest`, teste 7) e a leniência do Jackson (`ScheduledCleaningsAttackTest`, teste 12).
- **Notas para as próximas etapas:**
  - o N de "UH vaga há N dias" da pré-chegada fica com a E02;
  - o `CreditRule` é só por tipo de UH, e a faxina de área não tem créditos;
  - a E02 decide o que gera para um tipo com chave desativado;
  - a E02 garante "chegada acima de permanência" mesmo com prioridades editadas;
  - a E02 não deve gerar uma tarefa por dia enquanto houver uma aberta;
  - a E02 ignora local inativo, porque o `rooms` não desativa a faxina.

### 2. `ZenyHotelManager - Módulo checklists` (complementa)

Complementa o marcador "**API pública** (`ChecklistsApi`, raiz, sem checar permissão, só versões publicadas)", que hoje lista `resolveTemplate`, `version(templateId, number)` e `version(id)`. A `ChecklistsApi` ganhou `template(id: ChecklistTemplateId): ChecklistTemplateInfo?`, com `ChecklistTemplateInfo(id, name, context, active, publishedVersionNumber: Int?)`. Devolve `null` para id inexistente, e o `publishedVersionNumber` é nulo para um modelo nunca publicado. Quem a implementa é o `ChecklistsApiService`, em `checklists/application/ChecklistTemplates.kt`, que agora recebe o `ChecklistTemplateStore`. O primeiro consumidor é o `housekeeping`, no vínculo do tipo de limpeza (item 1, D1).

### 3. `ZenyHotelManager - Convenções de API` (complementa a parte de paginação)

`PageCursor.string(...)` (`shared/Pagination.kt`) passou a recusar com `400 INVALID_CURSOR` uma chave de texto que contenha NUL (U+0000). Antes, o PostgreSQL recusava NUL em `text` e a resposta era `500`. Vale para toda lista com chave de texto, e está coberto por `PageCursorTextKeyTest`. Os nomes do `housekeeping` também recusam NUL (`400 HOUSEKEEPING_DATA_INVALID`).

Para a pauta do arquiteto, sem mudança nesta etapa: o Jackson do projeto converte escalares por coerção (`"name": 12` vira `"12"`, `"7"` e `7.5` viram `7` num campo inteiro), e o NUL no fim de um UUID ou de uma data em JSON é aparado. (Leitura do agente: isso convive com a leitura estrita de datas e instantes da E18, que trata só `LocalDate` e `Instant`, não os demais escalares.)

### 4. `ZenyHotelManager - Schemas, migrações e views de relatório` (complementa)

Há um schema novo, `housekeeping`, com as migrações `V2026_11_15_1000__create_housekeeping.sql` e `V2026_11_15_1001__grant_housekeeping_to_app_role.sql`, a última migração do projeto agora (substitui qualquer indicação anterior de "última migração"; a E18 não tinha migração). O trigger `refuse_delete` vale nas tabelas de tipo e de faxina, e o papel da aplicação só tem DELETE em `cleaning_type_credit`. Detalhes de tabelas e restrições no item 1.

### 5. `ZenyHotelManager - Segurança, autenticação e autorização` (complementa)

As permissões novas são `housekeeping.config.read` e `housekeeping.config.manage` (escopo `ALL`, não sensíveis), concedidas aos modelos MANAGER e HOUSEKEEPER. A lista exaustiva do MANAGER no `AuthorizationTest` foi atualizada.

### 6. `ZenyHotelManager - Estado por marco` e Estado do hub (substitui)

**Substitui** a linha do M6 e, na subseção "M6 E18" (captura `a68d398b`, com a correção `c383eb2b`), o item "Próxima elegível: E01 …". Subseção nova, "M6 E01 — tipos de limpeza, créditos e faxinas programadas (2026-11-16)":

- **M6 (18 etapas): E01, E10, E11 e E14 a E18 `#concluida`; as demais, `#pendente`.** A E01 fechou em 2026-11-16 (módulo `housekeeping`). **A próxima elegível é a E02** (geração automática de tarefas), que depende da E01 e da E11.
- **Próxima migração:** depois de `housekeeping/V2026_11_15_1001__grant_housekeeping_to_app_role.sql`.
- Branch `roadmap/m6-operacao-fechamento`, commits de `2471691` (exclusivo) a `0d3eba1`, mais os de documentação do fechamento; o merge na `main` acontece no fim do lote. Gate `./gradlew build` em `0d3eba1`: 4355 testes, 0 falhas. Revisão final: pronto para integrar, sem Crítico nem Importante.
- **Decisões da E01 tomadas pela opção recomendada, revisáveis pelo usuário (nenhuma confirmada por ele):**
  - D1, o vínculo opcional (`0..1` em vez do `1` da SPEC §8.2.10);
  - D5, os valores da carga inicial;
  - D8, `422` para referência inexistente no corpo (o padrão do resto do projeto é `400 UNKNOWN_*`; a divergência vai ao arquiteto);
  - o limite de 200 créditos por corpo;
  - a reativação que mantém o vencimento antigo.
  Acrescentá-las à lista "Decisões sem confirmação do usuário (lista consolidada)", item M6.
- **Pauta do arquiteto:** a divergência de D8, os dois testes que fixam comportamento endurecível (item 1, "Testes") e a coerção do Jackson (item 3).

**Hub `ZenyHotelManager`:** "Estado" passa a "M6: E01, E10, E11 e E14 a E18 `#concluida`"; "Próximos passos" deixa de listar a E01 (resta E02 e demais); e "Notas do projeto → Módulos" inclui o link `[[ZenyHotelManager - Módulo housekeeping]]`.

## Contexto

Fechamento da etapa E01 do M6 do ZenyHotelManager (servidor), publicado pelo orquestrador do lote conforme a regra "ZenyHotelManager - atualização `<slug>` Eyy" do hub. A E01 abre a governança do `housekeeping`: tipos de limpeza com créditos por tipo de UH e faxinas programadas por UH ou área. A geração de tarefas (E02) e o uso do `recordDone` (E04) vêm depois.

## Origem

- Projeto: ZenyHotelManager, repositório `/home/caio/repos/ZenyHotelManager`; worktree `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m6-operacao-fechamento`.
- Branch `roadmap/m6-operacao-fechamento`, commits `2471691` (exclusivo) a `0d3eba1`.
- Fonte: `.superpowers/sdd/2026-11-15-m6-operacao-fechamento-e01/brain-capture-input.md` no worktree, preparado pelo orquestrador a partir do handoff da E01 (`docs/roadmaps/roadmap-m6-operacao-fechamento.md`, seção "E01").
- Conferido no vault antes de escrever: `ZenyHotelManager - Módulo checklists` (a `ChecklistsApi` ainda sem `template(id)`), `Estado por marco` (cabeçalho), o hub, as capturas da E18 (`a68d398b`, `c383eb2b`) e a `Inbox`: não havia captura nem nota de `housekeeping`.

## Por que registrar

O curador cria a nota do módulo `housekeeping`, acrescenta `template(id)` à API pública do `checklists`, a regra do NUL no cursor às convenções de API, o schema e as permissões às notas de plataforma, e passa o Estado por marco e o hub a E02 como próxima elegível.

## Limitações e incertezas

- Resumo do agente a partir do material do orquestrador; o código, o handoff e os números do gate (4355 testes, 0 falhas) **não foram reconferidos** pelo agente que escreveu esta captura.
- Não conferi nas notas de Convenções de API, Schemas e Segurança se já existe trecho sobre os mesmos pontos (a ferramenta de busca do escriba não permitiu); por isso os itens 3 a 5 dizem "complementa" e o curador deve checar duplicação.
- O merge na `main` ainda não aconteceu; os hashes valem na branch da etapa.
- Dependência local: o handoff e o material de entrada existem apenas no repositório e no worktree acima.

## Possíveis conexões

[[ZenyHotelManager]], [[ZenyHotelManager - Estado por marco]], [[ZenyHotelManager - Módulo checklists]], [[ZenyHotelManager - Convenções de API]], [[ZenyHotelManager - Schemas, migrações e views de relatório]], [[ZenyHotelManager - Segurança, autenticação e autorização]], [[ZenyHotelManager - Módulo rooms]], [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E18 - a68d398b]], [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E18 (correção) - c383eb2b]].
