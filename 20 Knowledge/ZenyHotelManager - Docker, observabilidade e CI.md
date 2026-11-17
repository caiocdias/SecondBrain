---
type: knowledge
status: processed
created: 2026-10-22
projects:
  - "[[ZenyHotelManager]]"
sources:
  - "[[2026-10-22 - ZenyHotelManager - Docker, observabilidade e CI - ada44296]]"
  - "[[2026-10-28 - ZenyHotelManager - atualização m5-recepcao-fnrh E13 - 7a6ce25a]]"
  - "[[2026-11-04 - ZenyHotelManager - atualização m5-recepcao-fnrh E14 - f8103233]]"
  - "[[2026-11-06 - ZenyHotelManager - atualização revisão de arquitetura dos roadmaps - c889f886]]"
  - "[[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]]"
  - "[[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]]"
  - "[[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]]"
---
# ZenyHotelManager - Docker, observabilidade e CI

Referência técnica do projeto [[ZenyHotelManager]]: imagem e compose, actuator, logs, métricas e o workflow da CI.

Texto literal do `CLAUDE.md` do repositório, linhas 540–563, no commit `a6c0f03` (2026-10-22), escrito pelos agentes que executaram as etapas M0 E01 a M5 E03; integrado sem resumo nem reescrita. Referências como "SPEC", "ARCHITECTURE §x", "RF-…", "RN-…", "Hn" e "Mx Ey" apontam para `docs/SPEC.md`, `docs/ARCHITECTURE.md` e `docs/roadmaps/` do repositório; menções a uma seção (por exemplo, seção "Transições de hospedagem") apontam para outra parte do antigo `CLAUDE.md`, hoje numa das notas de tema listadas no hub. Valores como `zeny`/`zeny`, `zeny_app` e `zeny-app-dev-only` são padrões públicos de desenvolvimento local já versionados no repositório, não credenciais de um ambiente real. Mudanças posteriores chegam por capturas "ZenyHotelManager - atualização Mx Ey" (fluxo no hub).

---

**Docker e compose** (RNF-01, ARCHITECTURE §15.1):

- `docker/Dockerfile`: build com `eclipse-temurin:25-jdk-noble` (só `bootJar`, cache do Gradle no BuildKit, sem daemon e com o Kotlin compilando no processo do build, que tem `-Dorg.gradle.jvmargs=-Xmx2g` no `GRADLE_OPTS`: com o padrão de 512 MB o `compileKotlin` dava `OutOfMemoryError` desde o M4; fora do Docker, o mesmo heap vem do `gradle.properties` da raiz), runtime `eclipse-temurin:25-jre-alpine` com as camadas do Spring Boot (`jarmode=tools extract --layers`), usuário `zeny` (10001, não-root), arquivos do root só leitura e `HEALTHCHECK` com `wget` na readiness. A imagem não define profile nem segredos; opções da JVM ficam no `ENTRYPOINT` (não use `JAVA_TOOL_OPTIONS`/`JDK_JAVA_OPTIONS`: a JVM escreveria "Picked up…" fora do JSON).
- `.dockerignore` (raiz) é uma lista de permissão: só `gradlew`, `gradle/`, os dois `*.gradle.kts` e `src/main/` entram no contexto. Arquivo novo necessário ao `bootJar` precisa entrar nela.
- `docker/compose.yaml` (projeto `zeny`): `api` (sem porta publicada, depende do `db` saudável), `db` (`postgres:18`, volume em `/var/lib/postgresql`), `storage` (MinIO pela imagem comunitária `pgsty/minio`, porque a `minio/minio` deixou de ser publicada), `storage-init` (roda `docker/storage/init-storage.sh`: cria o bucket privado `ZENY_STORAGE_BUCKET` e o usuário de serviço da `api` com política só dele, e termina; a `api` espera ele concluir) e `proxy` (Caddy, só HTTP, `docker/caddy/Caddyfile`, em `127.0.0.1:80` por padrão; responde 404 para `/actuator/prometheus` e repassa ao MinIO só as URLs pré-assinadas dos anexos comuns: `GET`/`HEAD` de `/<bucket>/<chave>` com a chave não vazia, `X-Amz-Signature` na query e sem cabeçalho `Authorization`, com o `Host` original, que a assinatura inclui; a listagem, a raiz do bucket e a assinatura por cabeçalho caem na `api` e dão 401; `/api/v1/stream`, o SSE, vai à `api` com `flush_interval -1`, sem buffer). O `init-storage.sh` recusa bucket chamado `api` ou `actuator`. O `backup` e o TLS público entram no M8.
- Variáveis: o compose lê `docker/.env` (ignorado pelo Git; o modelo é `docker/.env.example`, sem segredos: chaves, senha do admin e as senhas do MinIO, `ZENY_STORAGE_ROOT_PASSWORD` e `ZENY_STORAGE_SECRET_KEY`, vêm vazias, com os comandos `openssl` para gerá-las no cabeçalho). As credenciais não têm padrão no compose (`${VAR:?…}`): sem elas, ou vazias, `up` falha nomeando a variável. Quem conhece a senha do usuário de serviço do MinIO lê o bucket inteiro (pré-assinando ele mesmo as URLs), então ela nunca pode ser um valor conhecido. O `db` usa `ZENY_DB_MIGRATION_*` como `POSTGRES_USER`/`POSTGRES_PASSWORD` (o dono dos schemas) e monta `docker/postgres/initdb/`, que cria o papel da aplicação (`ZENY_DB_USERNAME`/`ZENY_DB_PASSWORD`) na primeira inicialização do volume. O nome do banco vem de `ZENY_DB_NAME` (padrão `zeny`), usado no `POSTGRES_DB` e na `ZENY_DB_URL` da `api`. O `api` recebe `ZENY_DB_*` e `ZENY_DB_MIGRATION_*`, `ZENY_ENCRYPTION_*`, `ZENY_JWT_*`, `ZENY_STORAGE_ACCESS_KEY`/`ZENY_STORAGE_SECRET_KEY` (obrigatórias; o usuário de serviço do MinIO), `ZENY_STORAGE_ENDPOINT` (`http://storage:9000`), `ZENY_STORAGE_PUBLIC_ENDPOINT` (padrão `http://localhost`; com outra porta do proxy, inclua-a), `ZENY_STORAGE_BUCKET`, `ZENY_ADMIN_LOGIN`/`ZENY_ADMIN_PASSWORD` (vazias por padrão: só servem no primeiro boot) e `ZENY_FCM_CREDENTIALS` (opcional, vazia por padrão: push desligado; o JSON da conta de serviço do Firebase em base64, nunca no repositório). O root do MinIO (`ZENY_STORAGE_ROOT_USER`/`ZENY_STORAGE_ROOT_PASSWORD`) vai só ao `storage` e ao `storage-init`; num `docker/.env` de antes da E08, o root era `ZENY_STORAGE_ACCESS_KEY`/`SECRET_KEY` (mova-o para `ZENY_STORAGE_ROOT_*`). Profile padrão do compose: `prod` (`ZENY_PROFILE`).

**Observabilidade** (ARCHITECTURE §16):

- Actuator: só `GET /actuator/health/liveness`, `/actuator/health/readiness` e `/actuator/prometheus` existem na web, abertos sem autenticação e sem detalhes (`{"status":"UP"}`). Os demais endpoints nem são criados (`management.endpoints.access.default: none`), e o `/actuator/health` agregado e qualquer outro caminho caem no `denyAll`. A readiness inclui o banco (`db`); a liveness, não. `ActuatorExposureTest` barra endpoint novo exposto: abrir outro exige mudar `application.yaml`, a `SecurityConfiguration` e o teste.
- Logs: no `prod`, JSON ECS numa linha por evento (`logging.structured.format.console: ecs`), com `traceId`/`spanId` e, nas requisições autenticadas, `userId` e `deviceSessionId` do MDC (`ActorMdcFilter`, só os ids, nunca login ou token); no `local`, texto legível com os mesmos campos no padrão de correlação (`logging.pattern.correlation`). O tracing é a ponte OpenTelemetry do Micrometer, sem exportador (aceita e propaga `traceparent` W3C).
- Valores do banco fora do log (M1 E03, corrigido no gate E09): numa violação de restrição, o PostgreSQL manda no DETAIL os valores da linha ("Key (login)=(…) already exists"). Por isso o driver conecta com `logServerErrorDetail=false` (`spring.datasource.hikari.data-source-properties`; a mensagem da exceção fica sem o DETAIL, e `serverErrorMessage.constraint` continua legível), o logger `org.hibernate.orm.jdbc.error` fica em `ERROR` (ele registraria em WARN cada `SQLException`) e o `db` do compose sobe com `log_error_verbosity=terse` e `log_min_error_statement=panic` (sem DETAIL nem o STATEMENT com os parâmetros). `UserManagementTest` e `RoleManagementTest` conferem que o login e o nome da role repetidos não aparecem na saída nem, numa violação forçada por SQL, na mensagem de nenhuma exceção da cadeia (e que a constraint continua legível). *(Desde a M6 E18, o log dos jobs também sai sem a mensagem do JDBC: subseção "Mensagem do JDBC fora do log dos jobs" em "Atualizações por capturas".)*
- Métricas: Micrometer no formato Prometheus, com a tag `application`. Técnicas (JVM, HTTP, Hikari) vêm do Boot. `OutboxMetrics` publica `zeny_outbox_publications{state="pending|failed|abandoned"}` e `zeny_outbox_publications_oldest_age_seconds{state=…}` (`failed` = ainda no reenvio automático; `abandoned` = fora dele, à espera do reenvio manual; M2 E12), recalculadas a cada `zeny.events.metrics.refresh-interval` (30 s; `NaN` se o banco não responder). `RealtimeMetrics` publica `zeny_realtime_connections` (conexões abertas no canal de tempo real). `GuestDocumentRekeyJob` publica `zeny_guests_documents_rekey_pending` (documentos de hóspede ainda numa chave que não é a ativa, medido no fim de cada execução; `NaN` antes da primeira). `FnrhSubmissionMetrics` (`fnrh`, M5 E08, um `MeterBinder` à parte do `FnrhMetrics` da E07) publica o gauge `zeny_fnrh_submissions{status="pending|failed|invalid"}`: quantas submissões à FNRH estão em cada situação que pede atenção, lido do banco (`countByStatus`, um `GROUP BY`) a cada raspagem. Uma leitura que falha dá `NaN`, com log só da classe da exceção, e não derruba a raspagem. Testado em `FnrhSubmissionMetricsTest`. As métricas `zeny_fnrh_*` da E07 estão em [[ZenyHotelManager - Módulo fnrh]]. Nenhuma regra de alerta nova em `docker/prometheus/alerts.yaml` na E08 (acréscimo da captura [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]], branch `roadmap/m5-recepcao-fnrh`). Regras de alerta em `docker/prometheus/alerts.yaml` (confira com `promtool check rules`). Métrica nova de módulo: um `MeterBinder` em `infrastructure`, nome `zeny.<módulo>.<coisa>`. Lista consolidada das métricas do M5 em "Métricas do M5", em "Atualizações por capturas".
- Nos testes, `@IntegrationTest` liga as métricas (`@AutoConfigureMetrics`), então o `/actuator/prometheus` responde como em produção.

**CI** (`.github/workflows/ci.yml`, GitHub Actions; ARCHITECTURE §7 e §17, RNF-03). Roda em push na `main` e em todo pull request, com três jobs em paralelo e sem nenhum passo que ignore falha:

- `build`: JDK 25 (Temurin), cache do Gradle (`gradle/actions/setup-gradle`, provedor `basic`, gravado só pela `main`), `./gradlew build` (tudo da tabela acima, com os testes de integração no Docker do runner) e `./gradlew checkOpenApi`. Publica como artefatos a documentação dos módulos (`spring-modulith-docs`, de `build/spring-modulith-docs/`) e o contrato (`openapi`); em falha, os relatórios dos testes (`test-reports`).
- `api-compatibility`: `.github/scripts/check-api-breaking.sh` compara o `api/openapi.yaml` com o da base e falha em breaking change de nível `ERR` em `/api/v1` (endpoint, parâmetro ou propriedade removidos, tipo trocado, campo que vira obrigatório…). A base é, num PR, a ponta da branch de destino (o checkout é o commit de merge); num push na `main`, o commit anterior ao push (`github.event.before`) e, se ele faltar, for só zeros ou não existir (branch nova, push forçado), o pai do `HEAD`, nunca o próprio `HEAD`. Mudança incompatível vai para `/api/v2` (ARCHITECTURE §7). A exceção, decidida pelo usuário em 2026-10-13, é remover um endpoint v1 que já estava `deprecated` na base (e, se tiver `x-sunset`, só depois dessa data): primeiro se deprecia, depois se remove. As mudanças aparecem como anotações no PR.
- **Push direto na `main` não é bloqueado:** como o trabalho é direto na `main`, uma quebra de API (ou qualquer outra falha) que entra por push só deixa a CI vermelha depois do fato. Para bloquear de verdade, seria preciso trabalhar com PR e proteger a `main` exigindo os três checks. Rode `.github/scripts/check-api-breaking.sh` e `./gradlew build` antes de cada push.
- `image`: build de `docker/Dockerfile` com Buildx, sem push, com as camadas no cache do Actions.

As actions ficam fixadas por SHA de commit, com a versão num comentário. O Dependabot (`.github/dependabot.yml`, decidido pelo usuário em 2026-10-13) abre por mês um único PR agrupado que atualiza as actions, trocando o SHA e o comentário juntos; dependências do Gradle e imagens Docker não entram nele. Numa atualização manual, troque também os dois juntos. Nenhum segredo é usado, e o token só lê o repositório (`permissions: contents: read`). Antes de subir uma mudança de API, rode `.github/scripts/check-api-breaking.sh` localmente. Valide o workflow com `docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint:1.7.12 .github/workflows/ci.yml`.

## Atualizações por capturas

Texto das capturas de atualização publicadas pelo orquestrador dos lotes no repositório, integrado sem resumo nem reescrita. Vale sobre o texto literal acima quando trata do mesmo assunto. As notas do curador estão marcadas como tal.

### Lockfiles na imagem (M5 E13, 2026-10-28)

Origem: [[2026-10-28 - ZenyHotelManager - atualização m5-recepcao-fnrh E13 - 7a6ce25a]].

- O `.dockerignore` (lista de permissão) passa a deixar entrar `gradle.lockfile` e `buildscript-gradle.lockfile`, além dos itens que a nota já lista. O `docker/Dockerfile` os copia junto de `settings.gradle.kts` e `build.gradle.kts`, antes do `./gradlew --version`.
- Sem eles, a imagem falha no `COPY`; com um lockfile defasado, falha no modo estrito.
- O cache de dependências do BuildKit passa a ser refeito quando o catálogo ou um lockfile muda.
- A CI não mudou nesta etapa. O `osv-scanner` fica fora dela por decisão do lote; a E14 acrescenta o passo de conferência dos lockfiles (item 2).

*Nota do curador:* "item 2" é o travamento de dependências, em [[ZenyHotelManager - Ambiente, banco, chaves e build]]. O passo de conferência já existe (E14, abaixo).

### Passo "Lockfiles em dia com o catálogo" (M5 E14, 2026-11-04)

Origem: [[2026-11-04 - ZenyHotelManager - atualização m5-recepcao-fnrh E14 - f8103233]].

- O job `build` de `.github/workflows/ci.yml` ganhou o passo **"Lockfiles em dia com o catálogo"**, antes do build completo.
  - O que roda: `./gradlew dependencies --write-locks`.
  - Quando falha: com `::error::`, se `git diff --exit-code -- '*.lockfile'` acusar mudança ou se `git status --porcelain -- '*.lockfile'` não sair vazio (lockfile novo não rastreado).
  - Por que fica dentro de um `if`: para a mensagem de erro sair mesmo sob `bash -e`.
- Verificado localmente, com o bloco `run` extraído do YAML e rodado com `bash --noprofile --norc -eo pipefail` em clones descartáveis: árvore em dia dá exit 0 (duas vezes, sem sujar a árvore); `shedlock = "7.10.0"` no catálogo, dependência nova (`commons-pool2`), lockfile novo não rastreado e restrição do freemarker removida dão exit 1. Sem o passo, o build estrito não falharia no rebaixamento nem na remoção da restrição, porque o Gradle aplica a versão travada como `strictly`.
- A ARCHITECTURE §17 cita a conferência dos lockfiles; o README e o comentário do `build.gradle.kts` também foram atualizados.
- **O primeiro run no GitHub ainda não existe** (depende do push, que é do usuário).

### Pendências do M8 (revisão dos roadmaps, 2026-11-06)

Origem: [[2026-11-06 - ZenyHotelManager - atualização revisão de arquitetura dos roadmaps - c889f886]]. Todas as etapas abaixo estão `#pendente`. Esta nota descreve o estado atual do código, que continua valendo até cada etapa ser executada; muda o dono e o critério das pendências.

| Etapa | Entrega | Parte afetada | Efeito | Autoria |
|---|---|---|---|---|
| M8 E14 | Migrações num container de uso único; `api` sem `ZENY_DB_MIGRATION_*` e sem Flyway no `prod`; o dono dos schemas deixa de ser o superusuário do container onde o modelo permitir | Lista de variáveis da `api` | Substitui a referência à E11 pela E14 ([[ZenyHotelManager - Ambiente, banco, chaves e build]]). A dívida não depende da Q-06. | Arquiteto (R9); a dívida em si é decisão do usuário de 2026-10-14 |
| M8 E17 | `opentelemetry-api` ≥ 1.67.0 no `productionRuntimeClasspath`, pelo Boot ou por restrição; 0 Critical e 0 High no scanner, salvo risco aceito; checksums e `osv-scanner` na CI ligados ou recusados com registro | Passos da CI | Complementa: dá etapa dona às decisões E14 (a), E13 (c) e (d), que não tinham uma | Arquiteto (R10) |
| M8 E18 | Serviços `prometheus` e `alertmanager` no compose, sem porta pública; destino por variável, obrigatório no profile de produção; alerta entregue a um receptor de teste | "Métricas", regras em `docker/prometheus/alerts.yaml` | Complementa: hoje o compose não sobe coletor, e as regras não têm quem as avalie | Usuário (R15, D19) |

- Serviço `backup` (M8 E10): a criar, pois hoje é só um comentário em `docker/compose.yaml`. A E10 ganhou critério de restauração utilizável (valor cifrado lido, anexos baixados do espelho, local das chaves fora do servidor) e revisão humana.
- M8 E11: `idle_in_transaction_session_timeout` definido e logs de acesso sem query string, com teste; um alerta de teste chega ao destino real.
- "Health" na ARCHITECTURE §16: liveness e readiness, com a saúde de cada integração por endpoint de status e métricas, sem `HealthIndicator`. Coerente com o que esta nota já descreve do actuator.


### Métricas do M5 (M5 E12, 2026-11-12)

Origem: [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 - 2c135bbf]] (auditoria G7, que consolida os trechos soltos das capturas).

- Métricas do M5 em `/actuator/prometheus` (todas por `MeterBinder`, nenhuma com regra de alerta em `docker/prometheus/alerts.yaml`): `zeny_fnrh_calls_total` (tags `operation`, `outcome`, `environment`), `zeny_fnrh_last_success_seconds`, `zeny_fnrh_last_failure_seconds` (`NaN` sem registro), `zeny_fnrh_configured` (0 ou 1) (E07, `fnrh/infrastructure/FnrhMetrics.kt:60-63`); `zeny_fnrh_submissions{status="pending|failed|invalid"}` (E08, `FnrhMetrics.kt:98`, `GROUP BY` a cada raspagem, `NaN` se a leitura falha); `zeny_printing_jobs{status="PENDING|SENT|FAILED"}` (E10, `printing/infrastructure/PrintingMetrics.kt:50`; `FAILED` só dos terminados dentro de `content-retention`). Sem `HealthIndicator` da FNRH nem do `printing`: a readiness não depende deles.
- *Nota do curador (conferência no repositório em 2026-11-15, só leitura, base `3a9542c`):* o `FnrhSubmissionMetrics` citado no item "Métricas" acima é declarado no mesmo arquivo `fnrh/infrastructure/FnrhMetrics.kt`, junto do `FnrhMetrics`.

### Compose isolado do gate (M5 E12, 2026-11-12)

Origem: [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 - 2c135bbf]], item 3. **Compose isolado do gate**, versionado em `docker/gate/` (decisão R1 da E12, sem confirmação do usuário; antes ficava no scratchpad). Para o gate do M6, é o modelo. Detalhes exatos em `docker/gate/README.md`.

- `run-gate.sh <workdir> <porta> [projeto]`: o ciclo completo. Gera o env sorteado pelo `gate-env.sh` (modo 600, nunca dentro do repositório nem sob um `.git`, nunca lê o `docker/.env`), confere a composição (`config -q`, nunca sem `-q`, que imprimiria segredos), sobe com `up -d --build`, espera o readiness (até 300 s), roda o `m5-roteiro.sh` e sempre faz `down -v --remove-orphans` por `trap` (também em falha e Ctrl+C), apagando o `gate.env` e contando as sobras do projeto. Recusa (saída 2) o projeto `zeny` (o do usuário), nome de projeto inválido e um projeto que já tenha contêiner, volume ou rede.
- `compose.gate.yaml`: `name: zeny-gate`, imagem `zeny-hotel-manager:gate` (nunca a `:dev`) e um WireMock da FNRH (`wiremock/wiremock:3.13.2` fixado por digest, sem porta publicada, só alcançável na rede do projeto) para onde apontam as URLs de homologação **e** de produção da FNRH (`ZENY_FNRH_HOMOLOGATIONURL` e `ZENY_FNRH_PRODUCTIONURL`). Logo, o gate nunca chama o Serpro real, em nenhum ambiente. Stubs da API v2.4 em `docker/gate/fnrh-mock/mappings/*.json`, com os mesmos contratos do `FnrhTestServer`.
- `m5-roteiro.sh <base-url> <projeto> <env-file>`: roteiro `curl`/`jq` pelo proxy, 13 seções (públicos, usuários, cadastro, check-in, FNRH, ficha pelo agente, estadia, check-out, walk-in e desfazer, recados, Serpro fora do ar, E16 e varredura), **302 conferências no M5**. A varredura de segredos e de dados de hóspede cobre os logs de `api`, `db`, `proxy`, `storage` e `storage-init` e a própria saída do roteiro (o `fnrh-mock` fica de fora: faz o papel do Serpro e recebe os dados por desenho). Segredos só em variáveis e arquivos temporários (modo 600), nunca em argumentos nem na saída; falhas redigem esperado e obtido.
- **O roteiro só roda num banco novo** (troca a senha do admin inicial): `up -d --build` depois de `down -v`, readiness `UP`.
- Antes do `up --build` (compila dentro do Docker): rode um build pesado por vez; confira `free -g` e que não há Gradle nem `docker build` de outra sessão; **nunca rode `./gradlew --stop`** (ver [[ZenyHotelManager - Testes de integração]]).
- Os 39 `WARN` do PDFBox ("Using fallback font", D-E11-4) no log da `api` são esperados e não são vazamento.
- *Nota do curador (roadmap, commit `b23958e`, só leitura):* a decisão E12 (d) do roadmap fala em 41 WARN do `api` em `prod`: os 39 do PDFBox e 2 da queda simulada da FNRH, todos aceitos. O handoff da E12 lista como Menores do gate, sem efeito no produto: `run-gate.sh` não propaga falha do `docker ps` em `leftovers`; a varredura não acharia a descrição de gênero se o encoder escapasse não-ASCII; dois gates no mesmo workdir sobrescrevem o `gate.env`; templating sem escape JSON no mock.

### Métricas e alertas do fechamento do dia (M6 E10, 2026-11-13)

Origem: [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]] (item 5, que remete às métricas e regras da seção 2 dela). Texto completo em [[ZenyHotelManager - Módulo endofday]] ("Métricas e alertas").

- Métricas `zeny.endofday.run.duration` (Timer), `zeny.endofday.run.failures` (Counter), `zeny.endofday.runs.failed` e `zeny.endofday.overdue.seconds` (gauges).
- Grupo novo `zeny-end-of-day` em `docker/prometheus/alerts.yaml`: `ZenyEndOfDayFailed`, `ZenyEndOfDayNotRun` (> 3600 s), `ZenyEndOfDayMetricsUnavailable` (`promtool`: 8 regras OK). A entrega dos alertas é da M8 E18.

### Log das exceções dos jobs (decisão da M6 E18, 2026-11-13; implementada em 2026-11-15)

*Nota do curador (2026-11-16):* **implementada na M6 E18**; ver a subseção "Mensagem do JDBC fora do log dos jobs (M6 E18, 2026-11-15)", abaixo. O título dizia "ainda não implementada".

Origem: [[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]] (item 5). A regra (só a classe da exceção e das causas, sem a mensagem, pelo tratador do agendador do `shared`) está em [[ZenyHotelManager - Eventos e jobs]].

*Nota do curador (conferência no repositório em 2026-11-15, só leitura, no merge `01c6f0e`):* `docker/prometheus/alerts.yaml` tem o grupo `zeny-end-of-day` com as três regras.

### Chave de MDC com raiz reservada do ECS (risco, M6 E16, 2026-11-14)

Origem: [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E16 - f7e211bd]] (item 2). **Interpretação do agente a partir do handoff**, ainda sem teste de produção; achado do testador, não reproduzido pela captura.

- Em `prod`, uma chave de MDC chamada `service` ou `process` (ou com esses prefixos e ponto) **faz o escritor ECS do Spring Boot falhar, e a linha de log some**. As chaves de hoje (`userId`, `deviceSessionId`, `traceId`, `spanId`) não colidem.
- Recomendação do handoff, para o `arquiteto`: registrar a regra "**chave de MDC nunca usa raiz reservada do ECS**" e, numa etapa que possa mexer em `src/main`, um teste que suba o log `prod` com cada constante de MDC. Pendência registrada em [[ZenyHotelManager - Estado por marco]] ("M6 E16"). O tratamento da linha ECS nos testes (`messagesOf`) está em [[ZenyHotelManager - Testes de integração]] ("M6 E16").

### Mensagem do JDBC fora do log dos jobs (M6 E18, 2026-11-15)

Origem: [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E18 - a68d398b]] (item 5; fatos do handoff da E18, segundo a captura). Complementa o marcador "Valores do banco fora do log" (M1 E03) do texto literal, que trata do DETAIL do PostgreSQL e de `logServerErrorDetail=false`; não substitui nada. O tratador e o formato do log estão em [[ZenyHotelManager - Eventos e jobs]] ("Log das exceções dos jobs: `JobErrorLoggingTaskScheduler`").

- A mensagem do JDBC ainda pode trazer valores mesmo sem o DETAIL. Desde a E18, o log das exceções que escapam de um job não tem mensagem, e o logger do ShedLock `JdbcTemplateStorageAccessor` está em `OFF`.
- **Pendência:** quatro jobs ainda **capturam e logam a própria falha com a mensagem** (ARCHITECTURE §16), fora do tratador novo, que só vê o que escapa: `FileOrphanPurgeJob.kt:36`, `ProvisionalReservations.kt:88`, `InventoryHorizonJob.kt:32` e `OutboxMetrics.kt:74`. Entram na etapa de manutenção sugerida ao `arquiteto` ([[ZenyHotelManager - Estado por marco]], "M6 E18").
- A captura repete o achado da E16 sobre a chave de MDC `service` ou `process` no log ECS de `prod`; está na subseção "Chave de MDC com raiz reservada do ECS", acima, e não foi duplicado.

---

## Proveniência

- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - Docker, observabilidade e CI - ada44296]] (capture_id: ada44296-529e-4b1f-9386-ab1e5da05933): texto literal do `CLAUDE.md` do repositório ZenyHotelManager (linhas 540–563, commit `a6c0f03`), integrado sem alteração; o tipo Knowledge em `20 Knowledge/` foi escolhido pelo usuário no processamento.
- 2026-11-04 — [[2026-10-28 - ZenyHotelManager - atualização m5-recepcao-fnrh E13 - 7a6ce25a]] (capture_id: 7a6ce25a-b05d-40ab-88c0-e459a9c329ca): lockfiles no `.dockerignore` e no `Dockerfile`, em "Atualizações por capturas".
- 2026-11-04 — [[2026-11-04 - ZenyHotelManager - atualização m5-recepcao-fnrh E14 - f8103233]] (capture_id: f8103233-d5b2-48b1-b302-c9360ff5b66b): passo "Lockfiles em dia com o catálogo" da CI, em "Atualizações por capturas".
- 2026-11-09 — [[2026-11-06 - ZenyHotelManager - atualização revisão de arquitetura dos roadmaps - c889f886]] (capture_id: c889f886-0719-4f28-984e-f2ef23ed9520): donos e critérios das pendências do M8 (E10, E11, E14, E17 e E18), em "Atualizações por capturas".
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]] (capture_id: 8df87866-4285-4e24-8878-0fab70c9436c): gauge `zeny_fnrh_submissions{status}` do `FnrhSubmissionMetrics` acrescentado ao item "Métricas" do texto literal (item 5 da captura).
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 - 2c135bbf]] (capture_id: 2c135bbf-8248-4987-a617-dcb3fa94c0a5): métricas do M5 consolidadas (G7) e compose isolado do gate em `docker/gate/` (item 3), em "Atualizações por capturas", com remissão no item "Métricas"; notas do curador conferidas no repositório e no roadmap.
- 2026-11-15 — [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]] (capture_id: 1e4f709b-7bbd-4c39-9725-1926aef1ca98): métricas e regras de alerta do fechamento do dia (item 5 da captura).
- 2026-11-15 — [[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]] (capture_id: 009e3130-5bd9-4e8b-bd56-81c7fc440b81): remissão ao log das exceções dos jobs (item 5 da captura).
- 2026-11-15 — [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E16 - f7e211bd]] (capture_id: f7e211bd-3d35-495d-87c3-33a791c87e48): risco da chave de MDC `service`/`process` no log ECS de `prod` e recomendação para o `arquiteto` (item 2 da captura).
- 2026-11-16 — [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E18 - a68d398b]] (capture_id: a68d398b-2037-4b20-af27-8039b163ae0e): mensagem do JDBC fora do log dos jobs e pendência dos quatro jobs que ainda logam a mensagem (item 5 da captura), na subseção nova "Mensagem do JDBC fora do log dos jobs", com remissão no marcador "Valores do banco fora do log"; o achado do MDC da E16 não foi duplicado.
