---
type: knowledge
status: processed
created: 2026-10-22
projects:
  - "[[ZenyHotelManager]]"
sources:
  - "[[2026-10-22 - ZenyHotelManager - Testes de integração - e6d2c591]]"
  - "[[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh E05 - 0ebc2e6a]]"
  - "[[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh integração E04 a E06 - b2046daa]]"
---
# ZenyHotelManager - Testes de integração

Referência técnica do projeto [[ZenyHotelManager]]: @IntegrationTest, containers compartilhados, papéis do banco nos testes e relógio mutável.

Texto literal do `CLAUDE.md` do repositório, linhas 578–585, no commit `a6c0f03` (2026-10-22), escrito pelos agentes que executaram as etapas M0 E01 a M5 E03; integrado sem resumo nem reescrita. Referências como "SPEC", "ARCHITECTURE §x", "RF-…", "RN-…", "Hn" e "Mx Ey" apontam para `docs/SPEC.md`, `docs/ARCHITECTURE.md` e `docs/roadmaps/` do repositório; menções a uma seção (por exemplo, seção "Transições de hospedagem") apontam para outra parte do antigo `CLAUDE.md`, hoje numa das notas de tema listadas no hub. Valores como `zeny`/`zeny`, `zeny_app` e `zeny-app-dev-only` são padrões públicos de desenvolvimento local já versionados no repositório, não credenciais de um ambiente real. Mudanças posteriores chegam por capturas "ZenyHotelManager - atualização Mx Ey" (fluxo no hub).

---

**Testes de integração:** anote a classe com `@IntegrationTest` (`src/test/kotlin/com/zeny/hotel/testsupport/`). Ela sobe o contexto web (servlet simulado, com `MockMvc` e a cadeia do Spring Security) com o profile `local` ligado a um único `postgres:18` e a um único MinIO (`MinioContainer`, imagem `pgsty/minio` na tag do compose, preparado pelo `docker/storage/init-storage.sh`, com o usuário de serviço) compartilhados por todos os testes da JVM, acrescenta as migrações só de teste de `src/test/resources/db/testmigration/` (schema `test_support`), entrega uma chave de cifragem (`TestEncryptionKeys`) e duas chaves JWT (`TestJwtKeys`, a ativa e uma anterior) sorteadas por JVM, cria o administrador inicial `TestAdmin` (senha sorteada), baixa o custo do Argon2id (`TestAuthInitializer`) e adia os jobs de reprocessamento e de expurgo do outbox, o de expurgo de anexos órfãos, a rotação de chaves dos documentos de hóspede, o horizonte do inventário e a expiração das pré-reservas (`RESUBMISSION_JOB_DEFERRED`, `OUTBOX_PURGE_DEFERRED`, `FILES_PURGE_DEFERRED`, `GUESTS_REKEY_DEFERRED`, `INVENTORY_HORIZON_DEFERRED`, `PROVISIONAL_EXPIRY_DEFERRED`; um contexto montado à mão os passa também). Um contexto montado à mão precisa dos três inicializadores (`PostgresInitializer`, `TestEncryptionKeysInitializer`, `TestAuthInitializer`) e, no profile `prod` (sem padrão para o armazenamento), do `TestStorageInitializer`. Para avançar o relógio da aplicação (bloqueio, validade de token), importe `MutableClockConfiguration` (bean `MutableClock` `@Primary`); o apoio dos testes do `iam` (criar usuário, chamar login e refresh) é o `IamTestSupport`, pelo `@Import(IamTestConfiguration::class)`. Os testes rodam com a JVM em `America/Sao_Paulo` de propósito (`build.gradle.kts`), para pegar código que dependa do fuso da JVM. O container de testes sobe com `max_connections=400`: cada contexto em cache guarda o seu pool do Hikari; pelo mesmo motivo a JVM dos testes tem 2 GB de heap (`maxHeapSize` no `build.gradle.kts`) e o cache de contextos do Spring guarda no máximo 16 (`spring.test.context.cache.maxSize` em `src/test/resources/spring.properties`; o menos usado é fechado), depois do `OutOfMemoryError` intermitente do executor de testes com 1 GB e uns 22 contextos (decisão do usuário em 2026-10-19).

O container de testes tem os dois papéis da produção:

- o `PostgresContainer` copia o mesmo script do compose (`docker/postgres/initdb/`), que cria `zeny_app` com senha sorteada por JVM;
- o `PostgresInitializer` liga o datasource a esse papel e o Flyway ao usuário padrão do Testcontainers, o dono;
- por isso os testes rodam sem DDL e sem `UPDATE`/`DELETE` na trilha. O que precisar do dono (desligar triggers, ler o histórico do Flyway) usa `flyway.configuration.dataSource`.

---

## Atualizações por capturas

Texto das capturas de atualização publicadas pelo orquestrador dos lotes no repositório, integrado sem resumo nem reescrita. Vale sobre o texto literal acima quando trata do mesmo assunto. As notas do curador estão marcadas como tal.

### M5 E05 — troca de UH, extensão, redução e early check-in (2026-10-23)

Origem: [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh E05 - 0ebc2e6a]]. Integrada à `main` com o lote E04 a E06 (até `4a91340`, 2026-10-23, já em `origin/main`), segundo [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh integração E04 a E06 - b2046daa]].

- `ReservationSearchApiTest` ("every search filter and every list is served by an index…") é intermitente: no filtro "period", o planner às vezes escolhe `reservation_arrival_idx` em vez de `reservation_stay_period_idx`, e o teste exige um índice exato no banco compartilhado. A sugestão, ainda não aplicada, é aceitar os dois índices nesse filtro.
- `CheckInRendezvousProbe` virou um `@Aspect` de teste que também sincroniza `RoomMoved`, `GuestCheckedOut` e as chamadas `checkOut`/`moveRoom` (corridas determinísticas). O apoio comum dos testes de recepção é `FrontdeskTestSupport`.

Segundo [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh integração E04 a E06 - b2046daa]], o `ReservationSearchApiTest` não falhou na verificação da `main` integrada (`./gradlew build`, 1287 testes, 0 falhas), e a correção recomendada (aceitar os dois índices no filtro "period") continua não aplicada.

---

## Proveniência

- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - Testes de integração - e6d2c591]] (capture_id: e6d2c591-1c43-4288-83b5-6db569703ea7): texto literal do `CLAUDE.md` do repositório ZenyHotelManager (linhas 578–585, commit `a6c0f03`), integrado sem alteração; o tipo Knowledge em `20 Knowledge/` foi escolhido pelo usuário no processamento.
- 2026-10-23 — [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh E05 - 0ebc2e6a]] (capture_id: 0ebc2e6a-f82e-4b92-9941-f42708feb2a2): teste intermitente `ReservationSearchApiTest` e `CheckInRendezvousProbe` como `@Aspect`.
- 2026-10-23 — [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh integração E04 a E06 - b2046daa]] (capture_id: b2046daa-2cdb-4680-ae03-6f388769bca4): situação do teste intermitente na verificação antes do push.
