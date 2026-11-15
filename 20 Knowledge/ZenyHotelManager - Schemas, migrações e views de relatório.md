---
type: knowledge
status: processed
created: 2026-10-22
projects:
  - "[[ZenyHotelManager]]"
sources:
  - "[[2026-10-22 - ZenyHotelManager - Schemas e migrações - 877877fd]]"
  - "[[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh E06 - c3d1beeb]]"
  - "[[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh integração E04 a E06 - b2046daa]]"
  - "[[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]]"
  - "[[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]]"
  - "[[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]]"
---
# ZenyHotelManager - Schemas, migrações e views de relatório

Referência técnica do projeto [[ZenyHotelManager]]: schemas por módulo, convenção das migrações Flyway, privilégios do papel da aplicação, tabelas append-only e views report_*.

Texto literal do `CLAUDE.md` do repositório, linhas 83–105, no commit `a6c0f03` (2026-10-22), escrito pelos agentes que executaram as etapas M0 E01 a M5 E03; integrado sem resumo nem reescrita. Referências como "SPEC", "ARCHITECTURE §x", "RF-…", "RN-…", "Hn" e "Mx Ey" apontam para `docs/SPEC.md`, `docs/ARCHITECTURE.md` e `docs/roadmaps/` do repositório; menções a uma seção (por exemplo, seção "Transições de hospedagem") apontam para outra parte do antigo `CLAUDE.md`, hoje numa das notas de tema listadas no hub. Mudanças posteriores chegam por capturas "ZenyHotelManager - atualização Mx Ey" (fluxo no hub).

---

**Schemas e migrações** (ARCHITECTURE §11): um schema por módulo, com o nome do módulo, e uma pasta de migrações por módulo.

- As migrações ficam em `src/main/resources/db/migration/<módulo>/V<aaaa>_<mm>_<dd>_<hhmm>__<descricao>.sql` (ex.: `V2026_10_14_0930__create_room.sql`), com descrição em inglês e `snake_case`. Só migrações versionadas (`V…`); arquivo aplicado nunca muda, corrige-se com uma migração nova.
- O `ModuleSchemasFlywayCustomizer` (`shared/infrastructure/persistence/`) lê as pastas e passa cada nome como schema ao Flyway, que cria o schema antes de migrar. Há um único histórico, `shared.flyway_schema_history`, e as versões são globais: a ordem de aplicação é a do timestamp, nunca a das pastas. Duas migrações com a mesma versão, em qualquer pasta, impedem o boot.
- `outOfOrder` está desligado: uma migração com timestamp anterior à última já aplicada (de uma branch longa, por exemplo) impede o boot com "Detected resolved migration not applied to database". A correção é renomeá-la para um timestamp novo antes do merge, nunca ligar `outOfOrder`.
- `MigrationConventionTest` barra no build: arquivo fora de uma pasta de módulo, pasta que não é módulo do Modulith, nome fora do padrão ou com data inválida, versão repetida entre pastas (inclusive as de teste) e SQL que crie, altere, remova (inclusive cada nome de `DROP TABLE a, b`), referencie por FK (`REFERENCES`) ou trigger (`CREATE TRIGGER … ON`), popule (`INSERT INTO`) ou dê permissão (`GRANT`/`REVOKE … ON`, inclusive `ON FUNCTION f(numeric(14,2), …)`, cuja assinatura é ignorada) sobre objeto fora do schema do próprio módulo ou sem schema, `ALTER DEFAULT PRIVILEGES` sem `IN SCHEMA` ou noutro schema, além de `CREATE SCHEMA`. São expressões regulares, não um parser SQL: cobrem as formas usuais.
- **Privilégios do papel da aplicação:** toda pasta de módulo concede a ele, numa migração, `USAGE` no schema, DML nas tabelas e `USAGE, SELECT` nas sequences. Faça isso com `GRANT … ON ALL TABLES/SEQUENCES IN SCHEMA <módulo> TO "${app_role}"` e com `ALTER DEFAULT PRIVILEGES IN SCHEMA <módulo> GRANT … ON TABLES/SEQUENCES TO "${app_role}"` para as tabelas criadas depois (como em `iam/V2026_10_14_1741__grant_iam_to_app_role.sql`).
  - Tabela *append-only* (auditoria, e os lançamentos e pagamentos do M3, RN-03) recebe só `SELECT, INSERT`: revogue `UPDATE, DELETE, TRUNCATE` dela e declare-a num bean `AppendOnlyTables` do módulo, para a partida conferir. O `audit` declara `audit.audit_entry`; o `billing`, `billing.posting` (M3 E04, com um trigger que recusa `UPDATE`/`DELETE` também ao dono) e, desde a E07, `billing.cash_movement` e `billing.cashier_shift_count` (com o mesmo tipo de trigger) e, desde a E08, `billing.payment` (idem, e um trigger que confere o reembolso contra o recebimento) e, desde a E09, `billing.card_pre_authorization_release` (idem) e, desde a E10, `billing.folio_reopening` (idem). O `reservations` declara, desde o M4 E08, `reservations.reservation_history` (com o mesmo tipo de trigger). O `fnrh` declara, desde o M5 E07, `fnrh.integration_call` (ver "Atualizações por capturas").
  - O histórico do Flyway (`shared.flyway_schema_history`) fica só com o dono.
  - As migrações só de teste (schema `test_support`) seguem a mesma regra.
- **Views de relatório `report_*`** (ARCHITECTURE §11 "Leitura para relatórios", M2 E08; modelo: `checklists/V2026_10_16_1700__create_checklist_report_views.sql`). São a API de leitura do módulo para relatórios: os endpoints de relatório do próprio módulo e, no M6, o `reporting` leem só elas, nunca as tabelas internas. Publicadas: as três `checklists.report_*` (M2 E08), `guests.report_guests` (M3 E03), as cinco do `billing` (M3 E10: `report_folios`, `report_postings`, `report_payments`, `report_cashier_shifts`, `report_cashier_counts`; seção "Encerramento, reabertura, extrato e views"), as cinco do `reservations` (M4 E12: `report_reservations`, `report_room_nights`, `report_inventory`, `report_room_assignments`, `report_block_allocations`) e as duas do `rates` (M4 E12: `report_rate_plans`, `report_rate_prices`; seção "Busca, listas operacionais e views de leitura") e `fnrh.report_submissions` (M5 E08; ver "Atualizações por capturas").
  - **Nome e forma:** `<módulo>.report_<assunto>`, criada por `CREATE VIEW` numa migração do módulo, só sobre tabelas do próprio schema. Cada linha é um fato (uma execução, uma resposta…), com ids opacos, situações, horários e contagens; quem consulta filtra e agrega. Nada de texto livre digitado por quem opera nem dado de hóspede (RN-13); nomes de configuração (modelo, item) podem ir.
  - **Contrato:** o comentário da migração descreve cada coluna e as regras (ex.: "não se aplica" fora do denominador). Uma coluna publicada não muda de nome nem de sentido; mudança incompatível cria outra view (`report_x_v2`), e a antiga só sai quando ninguém a lê. Toda view de módulo é `report_*` (o `DatabaseRolesTest` confere).
  - **Privilégios:** o `ALTER DEFAULT PRIVILEGES … ON TABLES` da pasta também vale para views e daria `INSERT, UPDATE, DELETE`. Na mesma migração, `GRANT SELECT ON <módulo>.report_x TO "${app_role}"` e `REVOKE INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER ON <módulo>.report_x FROM "${app_role}"` (um comando por view). O `DatabaseRolesTest` confere que o papel da aplicação só tem `SELECT` em toda view de módulo. A view roda com os privilégios do dono (sem `security_invoker`), então quem só tem `SELECT` nela não precisa de nada nas tabelas.
  - **Consultas:** num adaptador `JdbcClient` em `infrastructure` (porta em `application`), só `FROM <módulo>.report_*`; o filtro de período em datas é convertido em instantes no fuso do hotel (`HotelApi.timezone()`) pelo caso de uso. Prove "só as views" num teste de integração que roda o adaptador com um papel novo, sem login, que só tem `USAGE` no schema e `SELECT` nas views (`SET ROLE` numa conexão do dono, `flyway.configuration.dataSource`), como o `ChecklistReportsTest`: tocar uma tabela dá `42501`.
- `shared` guarda a infraestrutura comum: `btree_gist` e, desde o M3 E01, `pg_trgm` (busca por trecho com índice GIN de trigramas, `public.gin_trgm_ops`), as duas no schema `public`, `shared.event_publication` (outbox do Modulith, estrutura v2 do `spring-modulith-events-jdbc`), `shared.shedlock`, `shared.idempotency_key` (respostas guardadas do `Idempotency-Key`) e, desde o M2 E05, a sincronização offline: a sequence `shared.change_seq`, a função de trigger `shared.mark_offline_change()`, `shared.sync_tombstone` (*append-only*) e `shared.offline_command` (resultados por `commandId`, retidos a partir de `retain_from`; depois, só o id com usuário, tipo, `processed_at` e `retain_from`).

Passo a passo para um módulo novo persistir dados:

1. Crie a pasta `src/main/resources/db/migration/<módulo>/`, com o mesmo nome do pacote do módulo (minúsculo, sem hífen).
2. Crie a primeira migração com o timestamp atual em UTC (`date -u +%Y_%m_%d_%H%M`), qualificando todo objeto com o schema: `CREATE TABLE <módulo>.<tabela> (…)`, `CREATE INDEX … ON <módulo>.<tabela> …`. Não crie o schema; o Flyway cria a partir da pasta. Sem FK para outro schema. Na mesma pasta, conceda os privilégios ao papel da aplicação (`"${app_role}"`, item anterior); sem eles, a aplicação recebe `permission denied`.
3. Nas entidades, use `@Table(name = "...", schema = "<módulo>")`; nas consultas com `JdbcClient`, qualifique as tabelas. Instantes em `timestamptz`.
4. Rode `./gradlew test`: `MigrationConventionTest` confere a convenção, `DatabaseMigrationsTest` aplica tudo do zero num PostgreSQL 18 e confere que o schema existe, e `DatabaseRolesTest` confere que o papel da aplicação lê e escreve toda tabela de módulo (só `SELECT, INSERT` nas *append-only*) e não executa DDL.

---

## Atualizações por capturas

Texto das capturas de atualização publicadas pelo orquestrador dos lotes no repositório, integrado sem resumo nem reescrita. Vale sobre o texto literal acima quando trata do mesmo assunto. As notas do curador estão marcadas como tal.

### M5 E06 — recados (2026-10-23)

Origem: [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh E06 - c3d1beeb]]. Integrada à `main` com o lote E04 a E06 (até `4a91340`, 2026-10-23, já em `origin/main`), segundo [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh integração E04 a E06 - b2046daa]].

- Schema novo: `frontdesk`, a partir do M5 E06, com a tabela `trace`, `GRANT` no modelo do `reservations` e exclusão física proibida por trigger. A migração `V2026_10_23_1200` teve só o comentário alterado antes da integração. Um banco local que já a aplicou precisa de `flyway repair`.

Segundo [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh integração E04 a E06 - b2046daa]], a necessidade de `flyway repair` continua valendo.

### Schema `fnrh`: fila de submissões e view (M5 E08, 2026-11-11)

Origem: [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]]. Descreve a branch `roadmap/m5-recepcao-fnrh` (fechamento `2d07363`), ainda fora da `main` quando capturada. Módulo em [[ZenyHotelManager - Módulo fnrh]].

Migrações `fnrh/V2026_11_10_1000__create_fnrh_submissions.sql` e `fnrh/V2026_11_10_1100__create_fnrh_report_views.sql`. Nenhuma coluna guarda dado de hóspede, texto livre do Serpro, documento, raça/cor ou deficiência. `reservation_id` e `guest_id` são referências opacas, sem FK para outro schema.

- `fnrh.submission`: `id`, `reservation_id`, `reservation_code`, `operation` (CHECK com as 6 operações; 7 desde a M6 E14, com `NO_SHOW`), `operation_rank`, `event_key`, `causal_version` (≥ 0), `sequence` (`GENERATED ALWAYS AS IDENTITY`, cursor da API, único), `status` (CHECK com as 6 situações), `attempts`, `next_attempt_at`, `last_failure` (CHECK com os 10 códigos; 11 desde a M6 E14, com `REMOTE_NO_SHOW`), `in_flight`, `performed_by`, `occurred_at`, `created_at`, `sent_at` e `version`. Chave única `submission_event_uk (reservation_id, operation, event_key)`. Índice parcial da fila `submission_queue_idx (reservation_id, causal_version, operation_rank, sequence) WHERE status IN ('PENDING','FAILED','INVALID')` e índice `submission_status_idx (status, sequence)`.
- `fnrh.submission_error`: `(submission_id, guest_id, field, code)` como chave, com FK para `fnrh.submission` dentro do schema. Guarda o campo e o código, nunca o valor. O `retry` apaga essas linhas; o código não apaga as demais tabelas.
- `fnrh.remote_reservation`: chave `(reservation_id, environment)`, com `remote_id`, `precheckin_link` (cifrado pelo `FieldCipher`, `v1:…`) e `cancelled`; desde a M6 E14, também `no_show` e a CHECK `remote_reservation_closed_ck` (ver "Schema `fnrh`: no-show" abaixo).
- `fnrh.remote_guest`: chave `(reservation_id, guest_id, environment)`, com `person_id`, `guest_remote_id` e `checked_out`. Índice `(guest_id, environment)` para a pessoa já conhecida.
- **Privilégios:** sem `GRANT` próprio. O `ALTER DEFAULT PRIVILEGES` de `V2026_11_04_1001` dá DML completo. Nenhuma das quatro é *append-only*.
- **View `fnrh.report_submissions`:** uma linha por submissão, com `submission_id`, `reservation_id`, `operation`, `status`, `attempts`, `last_failure`, `created_at`, `sent_at` e `next_attempt_at` (este só vale enquanto `PENDING`). Ficam fora o código da reserva (quem precisa junta com `reservations.report_reservations` pelo `reservation_id`), os erros por campo, os ids e o link do Serpro, o cursor, a escrita em curso, o autor, a versão e todo dado de hóspede. Não há texto livre com valor de hóspede. Só `SELECT` para o papel da aplicação (`GRANT SELECT` e `REVOKE INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER`), provado por `FnrhReportViewsTest`. As pendências são `PENDING`, `FAILED` e `INVALID`, e o fechamento do M6 lê só a view.


### Schemas `fnrh` e `printing`, e demais migrações do M5 (M5 E12, 2026-11-12)

Origem: [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 - 2c135bbf]] (auditoria G6 das notas contra o código, base `3a9542c`).

- **`fnrh`** (E07, `fnrh/V2026_11_04_1000` a `_1030`; E08, `V2026_11_10_1000` e `_1100`): `fnrh.settings` (linha semente, versão 0, desligada), `fnrh.requester`, `fnrh.integration_call` (*append-only*, `AppendOnlyTables` em `fnrh/infrastructure/JdbcFnrhIntegrationLog.kt:131`, sem coluna de texto livre), `fnrh.domain_value`, e da E08 `fnrh.submission`, `fnrh.submission_error`, `fnrh.remote_reservation`, `fnrh.remote_guest` (texto em [[ZenyHotelManager - Módulo fnrh]]). `GRANT` pela migração `_1001` (DML por `ALTER DEFAULT PRIVILEGES`).
- **`printing`** (E10, `printing/V2026_11_11_1000__create_printing_tables.sql` e `_1001`): `printing.print_agent` (`token_hash char(64)` único, `token_generation`, `active`, CHECK "inativo não tem hash"), `printing.printer` (`kind` CHECK `THERMAL_ESCPOS`/`A4_PDF`, FK para o agente dentro do schema), `printing.print_job` (sequence `printing.print_job_position_seq`, `position` único, `status` CHECK `PENDING/SENT/PRINTED/FAILED`, `content bytea` cifrado, `content_purged_at`, `delivered_to` sem FK, `failure_code`; índices da fila, do reenvio, da validade e do expurgo). Nenhuma tabela *append-only* e nenhuma view. Módulo em [[ZenyHotelManager - Módulo printing]].
- **Outras migrações do marco:** `reservations/V2026_10_22_1546__add_stay_transitions.sql` (E01), `billing/V2026_10_22_2330__add_posting_source_reference.sql` (E04), `guests/V2026_11_06_1000__add_guest_gender_description.sql` (E15). Nenhuma migração nas etapas E11, E13, E14, E16 (nem na E12).
- **Views `report_*`:** a lista "Publicadas" ganha `fnrh.report_submissions` (E08), a única view nova do M5 (`fnrh/V2026_11_10_1100__create_fnrh_report_views.sql:18`).
- **Tabelas *append-only*:** além das já citadas, `fnrh.integration_call` (E07).

### Schema `endofday` (M6 E10, 2026-11-13)

Origem: [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]] (item 5). Tabelas, restrições e grants em [[ZenyHotelManager - Módulo endofday]] ("Schema `endofday` e migrações").

- Schema `endofday` (`run`, `run_step`, `run_issue`), **sem `DELETE` para a aplicação** (`SELECT, INSERT, UPDATE` ao `zeny_app`; `DatabaseRolesTest` tem `NO_DELETE_TABLES`). Última migração na E10: `V2026_11_12_1001` (`endofday/V2026_11_12_1000__create_endofday_tables.sql` e `V2026_11_12_1001__grant_endofday_to_app_role.sql`); a migração seguinte precisa de versão posterior.

### Alcance de `date` e `timestamptz` (ARCHITECTURE §11, M6 E18, 2026-11-13)

Origem: [[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]] (item 6).

- A ARCHITECTURE §11 "Identificadores e tipos" registra o alcance do PostgreSQL, menor que o do Java: `timestamptz` de 4714-11-24 a.C. (ano ISO −4713) a 294276 d.C.; `date` do mesmo início a 5874897 d.C. Valor de fora que chega a uma consulta sem passar por regra de negócio (ex.: a chave do cursor) é recusado antes do banco. A recusa do cursor no `PageCursor` entra com a M6 E18 ([[ZenyHotelManager - Convenções de API]]).

### Migração do no-show (M6 E11, 2026-11-14)

Origem: [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E11 - df23f14d]] (itens 1, 3 e 10). Sem outra mudança de schema nesta etapa.

- `reservations/V2026_11_13_1000__add_reservation_no_show.sql` troca as `CHECK` de `reservation_history.kind` e do motivo do fim da alocação para aceitar `NO_SHOW` e `RESERVATION_NO_SHOW`; nenhuma coluna nova (detalhes em [[ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)]], "M6 E11"). **A próxima migração do projeto precisa de versão posterior a `V2026_11_13_1000`** (substitui o "posterior a `V2026_11_12_1001`" da subseção "Schema `endofday`" acima; substituído pela subseção "Schema `fnrh`: no-show" abaixo).

### Schema `fnrh`: no-show (M6 E14, 2026-11-14)

Origem: [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E14 - 998156dc]] (item 2). Complementa a subseção "Schema `fnrh`: fila de submissões e view (M5 E08)" acima. Envio do no-show em [[ZenyHotelManager - Módulo fnrh]] ("No-show (M6 E14, 2026-11-14)").

Migração única `fnrh/V2026_11_14_1000__add_fnrh_no_show.sql` (D-E14-6), posterior a `V2026_11_13_1000` (a última, em `reservations`). Troca CHECKs com `DROP CONSTRAINT` e `ADD CONSTRAINT` (a migração antiga, aplicada, não se edita):

- `submission_operation_ck` aceita as 6 operações da E08 mais `'NO_SHOW'` (agora são 7).
- `submission_last_failure_ck` aceita `NULL` ou os 10 códigos de antes mais `'REMOTE_NO_SHOW'` (agora são 11).
- `fnrh.remote_reservation` ganha a coluna `no_show boolean NOT NULL DEFAULT false` e a CHECK **`remote_reservation_closed_ck CHECK (NOT (cancelled AND no_show))`**: a remota é cancelada ou no-show, nunca as duas (o passo do no-show não chama numa cancelada e o do cancelamento não chama numa no-show).
- **Contrato da view `fnrh.report_submissions`:** a definição da view **não muda**, mas a nota do contrato (cabeçalho de comentário da `V2026_11_10_1100`, já aplicada e que não se edita) ganha complemento no **cabeçalho de comentário da migração nova**: a coluna `operation` passa a incluir `NO_SHOW` e a coluna `last_failure` passa a incluir `REMOTE_NO_SHOW`. Quem lê o contrato da view precisa ler os cabeçalhos das **duas** migrações (o teste `FnrhReportViewsAttackTest` "the migration comment names every…" passou a ler os dois e continua exigindo cada operação e cada situação).
- A convenção para colunas publicadas que crescem em valores (a coluna não muda de sentido, só ganha valores) fica: a migração que acrescenta o valor repete a nota do contrato no próprio cabeçalho.
- **A próxima migração do projeto precisa de versão posterior a `V2026_11_14_1000`** (substitui o "posterior a `V2026_11_13_1000`" da subseção "Migração do no-show (M6 E11)" acima).

Testes: `FnrhNoShowMigrationTest` (aceita `NO_SHOW` e `REMOTE_NO_SHOW`, recusa `BOGUS`, `no_show` falso por padrão, recusa `cancelled` e `no_show` juntos, cabeçalho documenta o contrato da view); `MigrationConventionTest` e `DatabaseMigrationsTest` passam.

*Nota do curador (conferência por `git` em 2026-11-15, só leitura, no `ad970fc`):* o conteúdo da migração (as duas CHECKs trocadas, a coluna, a `remote_reservation_closed_ck` e o cabeçalho com o contrato da view) confere com o texto acima.

---

## Proveniência

- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - Schemas e migrações - 877877fd]] (capture_id: 877877fd-ab36-4aea-ad85-f3f152e7f81a): texto literal do `CLAUDE.md` do repositório ZenyHotelManager (linhas 83–105, commit `a6c0f03`), integrado sem alteração; o tipo Knowledge em `20 Knowledge/` foi escolhido pelo usuário no processamento.
- 2026-10-23 — [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh E06 - c3d1beeb]] (capture_id: c3d1beeb-2076-413c-af63-4e1e43af516f): schema `frontdesk` e a migração `V2026_10_23_1200`.
- 2026-10-23 — [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh integração E04 a E06 - b2046daa]] (capture_id: b2046daa-2cdb-4680-ae03-6f388769bca4): pendência do `flyway repair` mantida.
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]] (capture_id: 8df87866-4285-4e24-8878-0fab70c9436c): schema `fnrh` da fila de submissões e view `fnrh.report_submissions` (item 4 da captura), inclusive na lista "Publicadas".
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 - 2c135bbf]] (capture_id: 2c135bbf-8248-4987-a617-dcb3fa94c0a5): schemas `fnrh` e `printing`, demais migrações do M5, view única do marco e `fnrh.integration_call` como *append-only* (G6), em "Atualizações por capturas", com remissão no item das tabelas *append-only*.
- 2026-11-15 — [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]] (capture_id: 1e4f709b-7bbd-4c39-9725-1926aef1ca98): schema `endofday` sem `DELETE` e última migração `V2026_11_12_1001` (item 5 da captura).
- 2026-11-15 — [[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]] (capture_id: 009e3130-5bd9-4e8b-bd56-81c7fc440b81): alcance de `date` e `timestamptz` na ARCHITECTURE §11 (item 6 da captura).
- 2026-11-15 — [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E11 - df23f14d]] (capture_id: df23f14d-ec3c-4fa2-aa75-462913ddaf5e): migração `V2026_11_13_1000` do no-show e nova versão mínima da próxima migração (itens 1, 3 e 10 da captura).
- 2026-11-15 — [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E14 - 998156dc]] (capture_id: 998156dc-c51d-47f2-ad9c-86f204f7236c): schema `fnrh` do no-show (migração `V2026_11_14_1000`, CHECKs, coluna `no_show`, contrato da view) e nova versão mínima da próxima migração (item 2 da captura); nota do curador com a migração conferida por `git`.
