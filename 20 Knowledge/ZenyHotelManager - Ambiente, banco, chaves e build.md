---
type: knowledge
status: processed
created: 2026-10-22
projects:
  - "[[ZenyHotelManager]]"
sources:
  - "[[2026-10-22 - ZenyHotelManager - Ambiente, banco, chaves e build - 2f6c86e6]]"
  - "[[2026-10-28 - ZenyHotelManager - atualização m5-recepcao-fnrh E13 - 7a6ce25a]]"
  - "[[2026-11-04 - ZenyHotelManager - atualização m5-recepcao-fnrh E14 - f8103233]]"
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

## Atualizações por capturas

Texto das capturas de atualização publicadas pelo orquestrador dos lotes no repositório, integrado sem resumo nem reescrita. Vale sobre o texto literal acima quando trata do mesmo assunto. As notas do curador estão marcadas como tal.

### Travamento de dependências (M5 E13, 2026-10-28)

Origem: [[2026-10-28 - ZenyHotelManager - atualização m5-recepcao-fnrh E13 - 7a6ce25a]]. Complementa o parágrafo "Versões".

**Travamento de dependências (M5 E13).**

- `build.gradle.kts` liga `dependencyLocking { lockAllConfigurations(); lockMode = LockMode.STRICT }` no projeto e o mesmo bloco dentro de `buildscript { }`, para o classpath dos plugins.
- Lockfiles versionados na raiz, gerados pelo Gradle e nunca editados à mão:
  - `gradle.lockfile`: todas as configurações, inclusive detekt, ktlint, kover e o compilador Kotlin (415 pacotes);
  - `buildscript-gradle.lockfile`: os plugins (74 pacotes);
  - `settings-gradle.lockfile`: hoje só `empty=incomingCatalogForLibs0`, versionado para a regeneração não sujar a árvore.
- **Convenção:** toda mudança no catálogo ou num plugin regrava os lockfiles no mesmo commit, com `./gradlew dependencies --write-locks`. Os revisores conferem catálogo, `build.gradle.kts` e lockfiles juntos.
- **Comportamento do modo estrito, medido** (numa cópia descartável, revertido). Falham o build:
  - versão maior que a travada (`{strictly X} … enforced by Dependency Locking`);
  - dependência nova fora do lockfile (`… is not part of the dependency lock state`);
  - lockfile ausente (`Locking strict mode: Configuration '…' is locked but does not have lock state`).
- **Limitação:** uma versão **menor** no catálogo é ignorada em silêncio, e o build usa a travada (o Gradle a aplica como `strictly`). A E14 acrescenta à CI o passo `./gradlew dependencies --write-locks` seguido de `git diff --exit-code -- '*.lockfile'`, que pega essa divergência.
- Os BOMs entram como `platform(...)` nativo, sem o plugin `io.spring.dependency-management`. Por isso as propriedades de versão do BOM do Spring Boot (`tomcat.version`) não valem; para fixar uma versão, use uma restrição de versão.
- **Scanner:** `osv-scanner scan source -r .` na raiz lê os lockfiles. Dentro de um worktree em `.claude/worktrees/`, ele não vê nada, porque o `.gitignore` do checkout principal ignora essa pasta. Rode-o no checkout principal, numa cópia (`git archive HEAD`) ou com `--no-ignore`.

*Nota do curador:* a frase "A E14 acrescenta à CI o passo…" ficou obsoleta com a E14 (abaixo): o passo agora existe ([[ZenyHotelManager - Docker, observabilidade e CI]]). A lista de vulnerabilidades levantada pelo scanner em 2026-10-28 (item 4 da captura da E13: 31 vulnerabilidades, 5 Critical e 15 High) foi substituída pelo resultado da E14 e não foi copiada; continua na captura arquivada.

### Spring Boot 4.1.2 e restrições de versão (M5 E14, 2026-11-04)

Origem: [[2026-11-04 - ZenyHotelManager - atualização m5-recepcao-fnrh E14 - f8103233]]. Complementa o parágrafo do travamento.

- **Spring Boot 4.1.2** (plugin e BOM, no catálogo `gradle/libs.versions.toml`). Arrasta Tomcat 11.0.27, Jackson 3.1.7, Spring Framework 7.0.10, Spring Security 7.1.2, Hibernate 7.4.13, Micrometer 1.17.2, PostgreSQL JDBC 42.7.14 e, no classpath dos plugins, httpclient5 5.6.5. Os lockfiles continuam com 415 e 74 pacotes.
- **Inventário das duas restrições de versão** (cada uma traz no catálogo o motivo, os GHSA e a condição de saída):

| Restrição | Por quê | Sai quando |
|---|---|---|
| Plataforma do Jackson 2 na 2.22.4 (`jackson2 = "2.22.4"`, lib `jackson2-bom`, `implementation(platform(libs.jackson2.bom))`) | o springdoc 3.1.1 puxa a 2.22.1, e o BOM do Boot 4.1.2 fica na 2.21.7 | o springdoc ou o BOM do Boot trouxer o Jackson 2 ≥ 2.22.3 (conferir as 7 GHSA no scanner) |
| freemarker 2.3.35 no classpath dos plugins (`freemarker = "2.3.35"`) | vem do kover 0.9.11 (`kover-features-jvm` → `intellij-coverage-reporter`), o último publicado | o kover trouxer o freemarker ≥ 2.3.35 |

- A restrição do freemarker fica em `buildscript { dependencies { constraints { classpath(libs.freemarker) { because(…) } } } }`. O acessor `libs` compila dentro do `buildscript {}`.
- **A restrição é piso de versão.** O passo da CI não acusa uma restrição que sobrou (BOM já alcançou a versão), mas acusa a **remoção** dela, porque o lockfile voltaria para a versão vulnerável. Numa subida futura do Boot ou do kover, confira a condição de saída de cada restrição.
- **Substitui o item 4 da captura da E13 (vulnerabilidades):** com o scanner numa cópia limpa (`git archive`), o resultado antes (base `15bbcdb`) era "Total 11 packages affected by 31 known vulnerabilities (5 Critical, 15 High, 8 Medium, 3 Low, 0 Unknown)". Depois (lockfiles de `2c72294`) é "Total 3 packages affected by 5 known vulnerabilities (0 Critical, 0 High, 2 Medium, 3 Low, 0 Unknown)", sobre os mesmos 415 + 74 pacotes. Agora há **0 Critical e 0 High**. Resíduos:
  - `io.opentelemetry:opentelemetry-api` 1.62.0 (GHSA-ccrj-gw8r-854m, Medium 5,3, runtime): CPU quadrática no `tracestate`, alcançável sem autenticação porque a propagação W3C está ligada em toda requisição em `application.yaml`. Sai quando o Boot trouxer ≥ 1.67.0;
  - `org.apache.commons:commons-lang3` 3.16.0 (GHSA-j288-q9x7-2f5v, Medium 6,5): só no classpath dos plugins;
  - `ch.qos.logback:logback-core` 1.3.16 (três Low): só na configuração `ktlint`.
- **Torna obsoleta** a frase da captura da E13, item 2: "A E14 acrescenta à CI o passo `./gradlew dependencies --write-locks` seguido de `git diff --exit-code -- '*.lockfile'`". Agora é fato (item 3). A limitação do rebaixamento silencioso no catálogo passa a ser coberta pela CI, não só documentada.
- A convenção continua: toda mudança de dependência ou plugin regrava os lockfiles no mesmo commit; agora a CI recusa o lockfile defasado.
- Scanner da revisão final: rode-o fora do worktree (cópia por `git archive` ou `--no-ignore`). Neste ambiente, `osv-scanner -r <diretório>` equivale a `scan source -r`.

*Nota do curador:* "item 3" refere-se ao item da captura da E14 sobre a CI, integrado em [[ZenyHotelManager - Docker, observabilidade e CI]]. A lista de vulnerabilidades é a do scanner em 2026-11-04 e muda com o tempo; rode o scanner de novo antes de agir. O risco aceito do OpenTelemetry e as demais decisões do lote estão em [[ZenyHotelManager - Estado por marco]].

---

## Proveniência

- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - Ambiente, banco, chaves e build - 2f6c86e6]] (capture_id: 2f6c86e6-ed13-4195-b090-c2817117526b): texto literal do `CLAUDE.md` do repositório ZenyHotelManager (linhas 37–64, commit `a6c0f03`), integrado sem alteração; o tipo Knowledge em `20 Knowledge/` foi escolhido pelo usuário no processamento.
- 2026-11-04 — [[2026-10-28 - ZenyHotelManager - atualização m5-recepcao-fnrh E13 - 7a6ce25a]] (capture_id: 7a6ce25a-b05d-40ab-88c0-e459a9c329ca): travamento de dependências do Gradle (lockfiles, modo estrito, limitação do rebaixamento, scanner), em "Atualizações por capturas"; a lista de vulnerabilidades da captura não foi copiada por estar substituída pela E14.
- 2026-11-04 — [[2026-11-04 - ZenyHotelManager - atualização m5-recepcao-fnrh E14 - f8103233]] (capture_id: f8103233-d5b2-48b1-b302-c9360ff5b66b): Spring Boot 4.1.2, inventário das restrições de versão e vulnerabilidades residuais, em "Atualizações por capturas".
