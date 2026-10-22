---
type: capture
status: archived
created: 2026-10-22
capture_id: e6d2c591-1c43-4288-83b5-6db569703ea7
---
# ZenyHotelManager - Testes de integração

## Conteúdo capturado

Texto **literal** do `CLAUDE.md` do repositório ZenyHotelManager, linhas 578–585, no commit `a6c0f03` (2026-10-22): @IntegrationTest, containers compartilhados, papéis do banco nos testes e relógio mutável. Foi escrito pelos agentes que executaram as etapas do roadmap (M0 E01 a M5 E03); as decisões do usuário aparecem no próprio texto com a data e a indicação "decisão do usuário" (ou "decidida pela opção recomendada em nome do usuário (delegado ao orquestrador)"). Nada foi resumido nem reescrito.

---

**Testes de integração:** anote a classe com `@IntegrationTest` (`src/test/kotlin/com/zeny/hotel/testsupport/`). Ela sobe o contexto web (servlet simulado, com `MockMvc` e a cadeia do Spring Security) com o profile `local` ligado a um único `postgres:18` e a um único MinIO (`MinioContainer`, imagem `pgsty/minio` na tag do compose, preparado pelo `docker/storage/init-storage.sh`, com o usuário de serviço) compartilhados por todos os testes da JVM, acrescenta as migrações só de teste de `src/test/resources/db/testmigration/` (schema `test_support`), entrega uma chave de cifragem (`TestEncryptionKeys`) e duas chaves JWT (`TestJwtKeys`, a ativa e uma anterior) sorteadas por JVM, cria o administrador inicial `TestAdmin` (senha sorteada), baixa o custo do Argon2id (`TestAuthInitializer`) e adia os jobs de reprocessamento e de expurgo do outbox, o de expurgo de anexos órfãos, a rotação de chaves dos documentos de hóspede, o horizonte do inventário e a expiração das pré-reservas (`RESUBMISSION_JOB_DEFERRED`, `OUTBOX_PURGE_DEFERRED`, `FILES_PURGE_DEFERRED`, `GUESTS_REKEY_DEFERRED`, `INVENTORY_HORIZON_DEFERRED`, `PROVISIONAL_EXPIRY_DEFERRED`; um contexto montado à mão os passa também). Um contexto montado à mão precisa dos três inicializadores (`PostgresInitializer`, `TestEncryptionKeysInitializer`, `TestAuthInitializer`) e, no profile `prod` (sem padrão para o armazenamento), do `TestStorageInitializer`. Para avançar o relógio da aplicação (bloqueio, validade de token), importe `MutableClockConfiguration` (bean `MutableClock` `@Primary`); o apoio dos testes do `iam` (criar usuário, chamar login e refresh) é o `IamTestSupport`, pelo `@Import(IamTestConfiguration::class)`. Os testes rodam com a JVM em `America/Sao_Paulo` de propósito (`build.gradle.kts`), para pegar código que dependa do fuso da JVM. O container de testes sobe com `max_connections=400`: cada contexto em cache guarda o seu pool do Hikari; pelo mesmo motivo a JVM dos testes tem 2 GB de heap (`maxHeapSize` no `build.gradle.kts`) e o cache de contextos do Spring guarda no máximo 16 (`spring.test.context.cache.maxSize` em `src/test/resources/spring.properties`; o menos usado é fechado), depois do `OutOfMemoryError` intermitente do executor de testes com 1 GB e uns 22 contextos (decisão do usuário em 2026-10-19).

O container de testes tem os dois papéis da produção:

- o `PostgresContainer` copia o mesmo script do compose (`docker/postgres/initdb/`), que cria `zeny_app` com senha sorteada por JVM;
- o `PostgresInitializer` liga o datasource a esse papel e o Flyway ao usuário padrão do Testcontainers, o dono;
- por isso os testes rodam sem DDL e sem `UPDATE`/`DELETE` na trilha. O que precisar do dono (desligar triggers, ler o histórico do Flyway) usa `flyway.configuration.dataSource`.

---

## Contexto

Em 2026-10-22 o usuário pediu para enxugar o `CLAUDE.md` do repositório (638 linhas, ~435 KB) e passar o conteúdo para um projeto no Second Brain, de onde os agentes do projeto o leriam por um hook obrigatório. Esta captura é uma de várias, uma por tema. O plano, as decisões da entrevista e a estrutura proposta estão na captura-índice [[2026-10-22 - ZenyHotelManager - migração do CLAUDE.md para o brain - índice e decisões - 03d0ed3e]] (capture_id: 03d0ed3e-788d-43f3-b338-79e3077d799f).

## Origem

- Projeto: ZenyHotelManager (servidor do PMS Zeny Hotel Manager), repositório local `/home/caio/repos/ZenyHotelManager`.
- Arquivo: `CLAUDE.md`, linhas 578–585, commit `a6c0f03` (branch `main`).
- Sessão do Claude Code iniciada no repositório (agente externo), 2026-10-22.

## Por que registrar

É a referência técnica que os agentes do projeto precisam para trabalhar neste tema. Depois da integração, sai do `CLAUDE.md` e passa a viver no brain (decisão do usuário, 2026-10-22).

## Sugestão do agente para a integração

Sugestão, não decisão: uma nota `ZenyHotelManager - Testes de integração`, ligada pela nota de projeto (hub) do ZenyHotelManager, com este texto (o curador decide o `type` e se divide ou funde com outra captura). Manter o texto técnico como está: caminhos, nomes de classes e códigos de erro são usados pelos agentes ao editar o código.

## Limitações e incertezas

- O texto descreve o código no commit `a6c0f03`; etapas seguintes publicarão capturas de atualização ("ZenyHotelManager - atualização Mx Ey").
- Referências como "SPEC", "ARCHITECTURE §x", "RF-…", "RN-…", "Hn" e "Mx Ey" apontam para `docs/SPEC.md`, `docs/ARCHITECTURE.md` e `docs/roadmaps/` do repositório, que não foram copiados.
- Valores como `zeny`/`zeny`, `zeny_app` e `zeny-app-dev-only`, quando aparecem, são padrões públicos de desenvolvimento local já versionados no repositório, não credenciais de um ambiente real.

## Possíveis conexões

- [[2026-10-22 - ZenyHotelManager - migração do CLAUDE.md para o brain - índice e decisões - 03d0ed3e]]
