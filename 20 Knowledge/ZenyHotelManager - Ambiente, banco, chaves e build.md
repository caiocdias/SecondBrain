---
type: knowledge
status: processed
created: 2026-10-22
projects:
  - "[[ZenyHotelManager]]"
sources:
  - "[[2026-10-22 - ZenyHotelManager - Ambiente, banco, chaves e build - 2f6c86e6]]"
---
# ZenyHotelManager - Ambiente, banco, chaves e build

Referência técnica do projeto [[ZenyHotelManager]]: profiles, os dois papéis do banco, chaves JWT e de cifragem (com a rotação), administrador inicial, heap do Gradle e versões.

Texto literal do `CLAUDE.md` do repositório, linhas 37–64, no commit `a6c0f03` (2026-10-22), escrito pelos agentes que executaram as etapas M0 E01 a M5 E03; integrado sem resumo nem reescrita. Referências como "SPEC", "ARCHITECTURE §x", "RF-…", "RN-…", "Hn" e "Mx Ey" apontam para `docs/SPEC.md`, `docs/ARCHITECTURE.md` e `docs/roadmaps/` do repositório; menções a uma seção (por exemplo, seção "Transições de hospedagem") apontam para outra parte do antigo `CLAUDE.md`, hoje numa das notas de tema listadas no hub. Valores como `zeny`/`zeny`, `zeny_app` e `zeny-app-dev-only` são padrões públicos de desenvolvimento local já versionados no repositório, não credenciais de um ambiente real. Mudanças posteriores chegam por capturas "ZenyHotelManager - atualização Mx Ey" (fluxo no hub).

---

Profiles: `local` (desenvolvimento) e `prod` (implantação), em `src/main/resources/application.yaml`. Não há profile padrão: informe sempre o profile.

**Banco e os dois papéis** (H4 do roadmap do M1, ARCHITECTURE §11):

- **Variáveis:** o datasource da aplicação vem de `ZENY_DB_URL`, `ZENY_DB_USERNAME` e `ZENY_DB_PASSWORD`, o **papel da aplicação**, só com DML. O Flyway conecta na mesma URL com o **dono dos schemas**, `ZENY_DB_MIGRATION_USERNAME`/`ZENY_DB_MIGRATION_PASSWORD` (`spring.flyway.user`/`password`). Em `prod` nenhuma tem valor padrão (sem elas a aplicação não sobe). Em `local` os padrões, só de desenvolvimento, são `jdbc:postgresql://localhost:5432/zeny`, o dono `zeny`/`zeny` e a aplicação `zeny_app`/`zeny_app`.
- **Criação do papel:** o papel da aplicação nasce fora das migrações, sem senha no repositório, pelo script `docker/postgres/initdb/10-create-app-role.sh`. A imagem `postgres` o roda na primeira inicialização do volume, a partir de `ZENY_DB_USERNAME`/`ZENY_DB_PASSWORD`. O papel tem `LOGIN` e `CONNECT`, e nada de superusuário, `CREATEDB` ou `CREATEROLE`. O script tira `TEMPORARY` do banco de `PUBLIC`, então o papel não cria tabelas temporárias (nada na aplicação as usa: o Hibernate usa CTE no PostgreSQL, e Flyway, ShedLock e o outbox do Modulith não as criam; o dono, superusuário, não depende do privilégio). As migrações só concedem privilégios, ao papel cujo nome chega pelo placeholder `${app_role}` do Flyway (`spring.flyway.placeholders.[app_role]` = `spring.datasource.username`).
- **Trava na partida:** o `DatabaseRoleGuard` (`shared/infrastructure/persistence/`, `ApplicationRunner` de maior precedência) impede o boot se o papel da aplicação:
  - for superusuário ou tiver `CREATEROLE`, `CREATEDB` ou `BYPASSRLS`;
  - puder criar schemas (`CREATE`) ou tabelas temporárias (`TEMPORARY`) no banco;
  - puder criar objetos num schema de módulo;
  - for dono, ou membro do dono, de schema ou tabela de módulo;
  - tiver `UPDATE` (na tabela ou em alguma coluna), `DELETE` ou `TRUNCATE` numa tabela declarada por um bean `AppendOnlyTables` (`shared`).
- **`bootRun`:** suba só o banco, com o script, por `docker run -d --name zeny-db -e POSTGRES_DB=zeny -e POSTGRES_USER=zeny -e POSTGRES_PASSWORD=zeny -e ZENY_DB_USERNAME=zeny_app -e ZENY_DB_PASSWORD=zeny_app -v "$PWD/docker/postgres/initdb:/docker-entrypoint-initdb.d:ro" -p 5432:5432 postgres:18` (o `db` do compose não publica porta).
- **Banco antigo:** um banco criado antes da E04 não tem o papel, porque o script só roda com o volume vazio. Recrie-o (`docker rm -f zeny-db`, ou `down -v` no compose) ou faça à mão, como dono, o que o script faz (`CREATE ROLE zeny_app LOGIN PASSWORD '…' NOSUPERUSER NOCREATEDB NOCREATEROLE`, `REVOKE TEMPORARY ON DATABASE zeny FROM PUBLIC`, `GRANT CONNECT ON DATABASE zeny TO zeny_app`; comando no README) e reinicie: as migrações concedem o resto. Numa implantação nova, o administrador do banco faz o mesmo antes do primeiro boot.
- **Dívida para o M8 (E11):** o Flyway roda no boot da `api` com o dono dos schemas, que no compose e nos testes é o `POSTGRES_USER` (superusuário do container), e por isso a `api` recebe `ZENY_DB_MIGRATION_*`. No M8 as migrações vão para um job ou container de uso único, e a `api` deixa de receber essas credenciais (decidido pelo usuário em 2026-10-14).
- **Nome do papel:** trocar o nome depois exige conceder de novo à mão, porque as migrações já aplicadas não rodam outra vez. Esperar uma conexão leva no máximo 5 s (`hikari.connection-timeout`). Toda conexão roda em UTC (`SET TIME ZONE 'UTC'` no Hikari) e o Hibernate grava em UTC (`hibernate.jdbc.time_zone`); `open-in-view` está desligado e `ddl-auto` é `validate` (o schema é do Flyway).

**Chaves JWT e administrador inicial** (ARCHITECTURE §8.1, módulo `iam`): `ZENY_JWT_KEYS` (`kid:base64[,kid:base64…]`, cada uma uma chave privada RSA de 2048 bits ou mais em PKCS#8 DER, em base64) e `ZENY_JWT_ACTIVE_KEY_ID` (o `kid` que assina os tokens novos) são obrigatórias em todos os profiles, sem valor padrão no código nem no YAML: sem elas a aplicação não sobe. Todas as chaves da lista valem na validação; rotação: acrescente a nova, aponte a ativa para ela e retire a antiga depois de 15 min. Para desenvolvimento: `export ZENY_JWT_KEYS="dev:$(openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 | openssl pkcs8 -topk8 -nocrypt -outform DER | base64 | tr -d '\n')" ZENY_JWT_ACTIVE_KEY_ID=dev` (o `pkcs8 -topk8` é necessário: o `genpkey -outform DER` do OpenSSL 3 grava PKCS#1). `ZENY_ADMIN_LOGIN` e `ZENY_ADMIN_PASSWORD` (12 a 128 caracteres) criam o administrador inicial no boot só se não existir nenhum usuário, com troca de senha obrigatória no primeiro login (H2); com usuários, são ignoradas (e a senha preenchida gera um aviso no log); sem usuários e sem elas, a aplicação não sobe.

**Chaves de cifragem** (ARCHITECTURE §8.3): `ZENY_ENCRYPTION_KEYS` (`id:base64[,id:base64…]`, 32 bytes por chave, AES-256) e `ZENY_ENCRYPTION_ACTIVE_KEY_ID` (a chave que cifra os valores novos) são obrigatórias em todos os profiles, inclusive `local`, e não têm valor padrão no código nem no YAML: sem elas a aplicação não sobe. Para desenvolvimento, gere uma chave e guarde-a enquanto usar o mesmo banco local (o que ela cifrou só se lê com ela): `export ZENY_ENCRYPTION_KEYS="dev:$(openssl rand -base64 32)" ZENY_ENCRYPTION_ACTIVE_KEY_ID=dev`. Rotação (o mesmo anel deriva as chaves dos tokens e dos índices cegos):
  1. acrescente a chave nova à lista e aponte `ZENY_ENCRYPTION_ACTIVE_KEY_ID` para ela (os valores novos já saem com ela; os antigos continuam legíveis e encontráveis);
  2. espere o `GuestDocumentRekeyJob` (`guests`, a cada hora) re-cifrar o número e recalcular o índice cego dos documentos de hóspede: terminou quando a métrica `zeny_guests_documents_rekey_pending` é `0` ou quando `SELECT count(*) FROM guests.guest_document WHERE number_index_key <> '<ativa>' OR left(number, length('v1:<ativa>:')) <> 'v1:<ativa>:'` dá zero;
  3. re-cifre os outros valores que ainda usam a chave antiga (`FieldCipher.isEncryptedWithActiveKey`): ainda **não há job** para eles (`guests.guest.sensitive_data`, `files.stored_file.original_name`, `notifications.push_device.token`, as respostas guardadas de `shared.idempotency_key`, que vencem em 24 h, e os anexos sensíveis no bucket) — pendência do M8 (E11);
  4. só então retire a chave antiga da lista (um valor com ela deixaria de decifrar, e um índice com ela, de ser encontrado).

**Heap do Gradle:** o `gradle.properties` da raiz fixa `org.gradle.jvmargs=-Xmx2g -Dfile.encoding=UTF-8` (o compilador Kotlin roda no daemon; com o padrão de 512 MB, o `compileKotlin` do zero dava `OutOfMemoryError` desde o M4, M4 E05); a imagem Docker passa o mesmo heap pelo `GRADLE_OPTS` (abaixo, "Docker e compose"), porque o `.dockerignore` não leva o `gradle.properties`.

**Versões** de dependências e plugins ficam só em `gradle/libs.versions.toml`. Os BOMs do Spring Boot e do Spring Modulith entram como `platform(...)`; libs gerenciadas por eles ficam no catálogo sem versão. Nunca escreva versão literal no `build.gradle.kts`. O detekt está na linha 2.0 (alpha), a única que entende Kotlin 2.4; sua configuração fica em `config/detekt/detekt.yml`, sobre os padrões. O estilo do ktlint (`ktlint_official`, 120 colunas) fica no `.editorconfig`.

---

## Proveniência

- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - Ambiente, banco, chaves e build - 2f6c86e6]] (capture_id: 2f6c86e6-ed13-4195-b090-c2817117526b): texto literal do `CLAUDE.md` do repositório ZenyHotelManager (linhas 37–64, commit `a6c0f03`), integrado sem alteração; o tipo Knowledge em `20 Knowledge/` foi escolhido pelo usuário no processamento.
