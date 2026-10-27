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
  - Tabela *append-only* (auditoria, e os lançamentos e pagamentos do M3, RN-03) recebe só `SELECT, INSERT`: revogue `UPDATE, DELETE, TRUNCATE` dela e declare-a num bean `AppendOnlyTables` do módulo, para a partida conferir. O `audit` declara `audit.audit_entry`; o `billing`, `billing.posting` (M3 E04, com um trigger que recusa `UPDATE`/`DELETE` também ao dono) e, desde a E07, `billing.cash_movement` e `billing.cashier_shift_count` (com o mesmo tipo de trigger) e, desde a E08, `billing.payment` (idem, e um trigger que confere o reembolso contra o recebimento) e, desde a E09, `billing.card_pre_authorization_release` (idem) e, desde a E10, `billing.folio_reopening` (idem). O `reservations` declara, desde o M4 E08, `reservations.reservation_history` (com o mesmo tipo de trigger).
  - O histórico do Flyway (`shared.flyway_schema_history`) fica só com o dono.
  - As migrações só de teste (schema `test_support`) seguem a mesma regra.
- **Views de relatório `report_*`** (ARCHITECTURE §11 "Leitura para relatórios", M2 E08; modelo: `checklists/V2026_10_16_1700__create_checklist_report_views.sql`). São a API de leitura do módulo para relatórios: os endpoints de relatório do próprio módulo e, no M6, o `reporting` leem só elas, nunca as tabelas internas. Publicadas: as três `checklists.report_*` (M2 E08), `guests.report_guests` (M3 E03), as cinco do `billing` (M3 E10: `report_folios`, `report_postings`, `report_payments`, `report_cashier_shifts`, `report_cashier_counts`; seção "Encerramento, reabertura, extrato e views"), as cinco do `reservations` (M4 E12: `report_reservations`, `report_room_nights`, `report_inventory`, `report_room_assignments`, `report_block_allocations`) e as duas do `rates` (M4 E12: `report_rate_plans`, `report_rate_prices`; seção "Busca, listas operacionais e views de leitura").
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

---

## Proveniência

- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - Schemas e migrações - 877877fd]] (capture_id: 877877fd-ab36-4aea-ad85-f3f152e7f81a): texto literal do `CLAUDE.md` do repositório ZenyHotelManager (linhas 83–105, commit `a6c0f03`), integrado sem alteração; o tipo Knowledge em `20 Knowledge/` foi escolhido pelo usuário no processamento.
- 2026-10-23 — [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh E06 - c3d1beeb]] (capture_id: c3d1beeb-2076-413c-af63-4e1e43af516f): schema `frontdesk` e a migração `V2026_10_23_1200`.
- 2026-10-23 — [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh integração E04 a E06 - b2046daa]] (capture_id: b2046daa-2cdb-4680-ae03-6f388769bca4): pendência do `flyway repair` mantida.
