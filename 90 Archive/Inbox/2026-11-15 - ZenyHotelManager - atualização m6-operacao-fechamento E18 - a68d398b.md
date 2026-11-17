---
type: capture
status: archived
created: 2026-11-15
capture_id: a68d398b-2037-4b20-af27-8039b163ae0e
---
# ZenyHotelManager - atualização m6-operacao-fechamento E18

## Conteúdo capturado

Captura de fechamento de etapa do projeto ZenyHotelManager (M6, etapa E18 "Faixa do cursor, rollback em toda exceção, datas estritas e log dos jobs"). Para cada nota de tema afetada, abaixo está o texto novo ou alterado e se ele **substitui** ou **complementa** um trecho. O texto desta captura vale sobre as notas e sobre as capturas anteriores quando tratam do mesmo assunto. Fatos vêm do handoff da E18 (roadmap do M6, seção "E18", bloco "Evidências e handoff") e da ARCHITECTURE §5, §7, §11 e §13 do repositório; o que é leitura do agente vem rotulado.

### Aviso ao usuário

O front desktop deve saber da mudança do `""` em datas e instantes opcionais: antes virava `null` e era aceito, agora dá `400 INVALID_FORMAT` (decisão (c) abaixo).

### 1. `ZenyHotelManager - Estado por marco`

**Substitui**, na subseção "M6 E17", as linhas "Próximas elegíveis: E18 … e depois a E01" e "M6 com E10, E11, E14, E15, E16 e E17 `#concluida`", e a nota do curador que diz que a E18 está `#em-andamento` e sem captura. **Complementa** com a subseção nova abaixo.

Subseção nova, "M6 E18 — faixa do cursor, rollback em toda exceção, datas estritas e log dos jobs (2026-11-15)":

- **M6 com E10, E11, E14, E15, E16, E17 e E18 `#concluida`.** A E18 foi concluída em 2026-11-15, na branch `roadmap/m6-operacao-fechamento`, de `a5b0902` a `ed0f5ab`. O merge na `main` acontece no fim do lote; até lá a E18 não está na `main` nem no remoto.
- **Próxima elegível:** E01 (governança: tipos de limpeza, créditos e faxinas programadas, primeira etapa do módulo `housekeeping`). A E18 não tinha dependência dentro do roadmap, e o gate do M6 (E12) continua dependendo dela e das demais.
- **Próxima migração:** sem mudança (a E18 não tem migração).
- **Fatos:**
  - Plano `docs/superpowers/plans/2026-11-15-m6-operacao-fechamento-e18.md`, 7 tarefas (1, 2, 3a, 3b, 4, 5 e 6), todas `Risco: alto`. Revisão de arquitetura (`revisor-arquitetura`, opus) aprovada com notas na rodada 2; bloqueada na rodada 0 (limite superior do instante, leitura de "registrado" no comando offline, tamanho das Tasks 1 e 2) e na rodada 1 (risco da Task 2, caminho ISO do `POST /end-of-day/runs` com o admin).
  - Execução em dois lotes: o primeiro (Tasks 1 a 3b) parou a pedido do usuário em `5d0dd27`; o segundo retomou na Task 4.
  - Commits por tarefa: Task 1 `df8d98c`, `6245b71`, `46eb615`, `d21e463`; ARCHITECTURE §11 `04004ba`; Task 2 `38d8354`, `f4d28c5`; Task 3a `7d3936d`; Task 3b `59ccaa8`; Task 4 `a689c80`, `76f884b`, `54977db`; Task 5 `5fa3c8a`, `29cc525`, `5bfb6e9`; Task 6 `38fbf96`, `2ead411`, `ed0f5ab`. Cada tarefa passou por desenvolvedor, testador, verificação mecânica e `revisor-seguranca`.
  - **Gate:** `./gradlew build` em `ed0f5ab` com BUILD SUCCESSFUL em 23m 4s, **4160 testes, 0 falhas, 0 ignorados** (contagem dos XML do JUnit), com `checkOpenApi`, detekt, ktlint e `koverVerify`. A primeira tentativa foi encerrada pelo Claude Code por falta de memória, e o usuário autorizou rodar de novo numa janela livre.
  - oasdiff (`check-api-breaking.sh`): "No changes detected" e nenhuma mudança `ERR` em `/api/v1` (o contrato não mudou). `osv-scanner` 2.7.0 com `-L` em `gradle.lockfile` (426 pacotes) e `buildscript-gradle.lockfile` (74): 0 Critical, 0 High, 2 Medium e 3 Low, todos anteriores à etapa. `check_test_integrity.py --base 5e06f16`: exit 1 com 4 `DEV_TESTE_DO_TESTADOR`, todos justificados (acréscimos que o plano manda). Na Task 3b, exit 1 com `ASSERCAO_REMOVIDA` justificado (só a assinatura de um helper mudou).
  - **Revisão final** (`revisor-seguranca`, opus, `5e06f16..ed0f5ab`): "Ready to merge: With fixes", 0 Crítico. I1 (handoff sem o inventário) foi tratado no fechamento; I2 (regressão estreita da faixa do cursor) ficou para manutenção (decisão (e)); os 7 Menores foram para as notas, sem onda final de correção.
  - **Revisão humana:** não (roadmap). Nenhuma decisão da etapa foi confirmada pelo usuário; todas abaixo seguem como "opção recomendada, revisável".
- **Entregue** (resumo do agente a partir do handoff; o detalhe técnico está nas notas de tema abaixo): faixa do cursor no `PageCursor` (`StorableRange`); `rollbackOn = ALL_EXCEPTIONS` global; leitura estrita de `LocalDate` e `Instant` no mapeador único; log dos jobs só com nome e classes (`JobErrorLoggingTaskScheduler`).
- **Acrescenta à lista "Decisões sem confirmação do usuário (lista consolidada)", item M6:** as decisões (a) a (f) da E18 (subseção "M6 E18"; texto na seção "Decisões para o usuário" abaixo).
- **Pendências para o `arquiteto` (etapa de manutenção sugerida):** ver o item 9 desta captura.

### 2. `ZenyHotelManager - Convenções de API`

**Substitui** a subseção "Cursor e datas: leitura estrita (decisão da M6 E18, 2026-11-13; ainda não implementada)": o que era decisão passa a ser comportamento atual, com os detalhes abaixo. **Complementa** os marcadores "Paginação" e "Contrato" do texto literal (cursor e datas).

- **Faixa do cursor (`PageCursor`, `shared/Pagination.kt`; ARCHITECTURE §7 "Paginação" e §11):** `com.zeny.hotel.shared.StorableRange` define o alcance que o PostgreSQL e o driver guardam: `MIN_DATE` e `MIN_INSTANT` = `-4712-01-01`, `MAX_DATE` = `+5874897-12-31` e `MAX_INSTANT` = `+294276-12-31T23:59:59.999999Z`, extremos inclusivos. `PageCursor.instant(i)` e `PageCursor.localDate(i)` aceitam os extremos e recusam com `400 INVALID_CURSOR` o que fica fora. Vale, sem código local, para as 15 consultas por cursor de instante ou de data (9 por instante e 6 por data, as mesmas listadas na subseção substituída). A validação própria do `endofday` (`EndOfDayQueries.requireStorable` e as constantes `MIN_STORABLE_INSTANT` e `MAX_STORABLE_INSTANT_EXCLUSIVE`) saiu, e `checkNoRun` usa o `StorableRange`.
  - **Piso `-4712-01-01`, não `-4713-11-24`** (decisão (a)): o testador mediu que o pgjdbc envia como `-infinity` qualquer data ou instante anterior a `-4712-01-01`. Sem o piso, o cursor nos 38 dias antes dele devolvia uma página errada em silêncio. Por isso o vermelho antes da correção veio como `200` vazio, e não como `500`.
- **Datas e instantes estritos no JSON** (`shared/infrastructure/json/StrictDateTimeJson.kt`, ARCHITECTURE §7 "Datas e valores"): um `JsonMapperBuilderCustomizer` com `leniency=false` e um `DelegatingDeserializer` (`IsoText`) em `LocalDate` e `Instant`, no mapeador único da aplicação (Jackson 3). Regras:
  - só **texto**, **sem espaço nas pontas**; no `Instant`, o `T` é obrigatório;
  - recusa número, epoch em texto, data-hora numa data (`"2026-11-13T00:00:00"`, com ou sem `Z`), array (`[2026,11,13]`) e objeto, com `400 VALIDATION_FAILED` e o erro no campo, inclusive em objeto aninhado e em lista;
  - **`""` numa data ou num instante dá `400 INVALID_FORMAT`**; num campo opcional, antes virava `null` e era aceito. Ausente ou `null` seguem como antes;
  - o JSON que o próprio servidor grava e relê (em `reservations` e `checklists`) continua legível em todo o alcance; a saída não mudou; o contrato `api/openapi.yaml` não mudou.
- **Comandos offline (`POST /api/v1/sync/commands`):** o mapeador é o mesmo; um comando com payload fora do formato volta **`REJECTED` com o código `COMMAND_PAYLOAD_INVALID`**, sem efeito, e o reenvio dá a mesma recusa. **Não é guardado** (decisão (b)): "registrado" foi lido como "devolvido com `REJECTED` e código, nunca descartado em silêncio"; o protocolo da ARCHITECTURE §9 não mudou.
- **Pendências registradas (fora do escopo da E18, achadas pelo plano e pela revisão):**
  - datas e instantes em **query string e path** (conversão do Spring MVC, não do Jackson) seguem lenientes: aceitam o formato curto do locale (`13/11/25`) e epoch em milissegundos, e dão `500` fora do alcance do banco (`audit-entries`, `traces`, `out-of-order`, `schedule`);
  - datas e instantes **fora do alcance no corpo** de outros endpoints: um recado criado com `dueOn` = `+999999999-12-31` dá `201` e é gravado como `infinity`; na leitura vira `LocalDate.MAX`, e o próximo cursor da lista sai fora do `StorableRange`, então o `PageCursor` o recusa com `400 INVALID_CURSOR` e o resto da lista fica inalcançável (**regressão I2 da revisão final**; antes da E18 a paginação seguia). Também há `500` com `+5874898-01-01`. A correção recomendada é recusar no corpo o que estiver fora do `StorableRange`, e não afrouxar o cursor; fazer isso no mapeador agora quebraria a releitura de JSON persistido.
- **Testes:** `PaginationTest` (extremos exatos e vizinhos de fora), `CursorKeyRangeApiTest` (as 15 consultas e as pendências do `endofday`), `StrictDateTimeJsonApiTest` (`POST /end-of-day/runs` com um usuário sem `endofday.runs.execute`, e `dueOn` dos recados; `expiresAt` da pré-autorização para instantes) e `OfflineSyncTest` (comando com data numérica rejeitado; com ISO, aplicado). O admin não foi usado no teste de `end-of-day/runs` (H10).

### 3. `ZenyHotelManager - Auditoria` (parte de transações)

**Substitui** a subseção "Rollback em toda exceção (decisão da M6 E18, 2026-11-13; ainda não implementada)": agora é comportamento atual. **Complementa** o marcador "**Transação**" do texto literal.

- `@EnableTransactionManagement(..., rollbackOn = RollbackOn.ALL_EXCEPTIONS)` em `TransactionOrderingConfiguration` (`shared/infrastructure/audit/AuditAspect.kt`). Exceção *checked* que escapa de um caso de uso `@Transactional` desfaz a escrita, e a escrita não fica mais confirmada sem trilha (o `AuditAspect` só grava em sucesso ou em `DomainException`).
- **`noRollbackFor` seguem valendo**, porque a regra explícita é mais específica que a de `Exception`: login e refresh com falha, aprovação recusada (`Authentication` ×2, `TokenRefreshService`, `Approvals`) e `files` (`FilesService.download`, `recordRejections`). Teste: "an explicit noRollbackFor still commits with ALL_EXCEPTIONS", com ataques (subclasse da listada, *checked* não listada, `Error`, ouvinte `REQUIRES_NEW`, transação unida).
- **Efeito novo, provado em teste:** uma *checked* que um chamador **engole** dentro de uma transação unida (REQUIRED) faz o commit externo falhar com `UnexpectedRollbackException`. KDoc sugerido em `TransactionOrderingConfiguration` (ainda não escrito).
- **`endofday`:** as três transições (`EndOfDayRunTransitions`) perderam o `rollbackFor = Throwable` local; o comportamento não mudou (o teste `a checked exception from the work undoes the complete like any other` segue verde).
- **`TransactionTemplate` programático** desfaz em qualquer `Throwable`, independente do atributo (conferido no bytecode do `spring-tx` 7.0.10). Proxies de repositório do Spring Data têm fonte de atributos própria e não herdam o `rollbackOn`; é inofensivo, porque entram na transação do caso de uso, que decide.
- **Inventário dos caminhos com exceção *checked* dentro de `@Transactional`** (critério da etapa): **nenhum caminho dependia do commit**. Onde havia escrita antes do ponto que lança, o commit antigo era o defeito.
  - `printing`: `HtmlPdfRenderer.render` (`SAXException`/`IOException`) via `PrintingApiService.render`/`print`; os `pdf(...)` são `readOnly` e os `print(...)` renderizam antes da única escrita (`jobs.enqueue`): antes confirmava uma transação vazia, agora desfaz uma vazia.
  - `shared`: `StreamController`/`RealtimeHub` fora de transação; `IdempotencyFilter` fora de proxy, grava por `TransactionTemplate`; as cifras capturam `GeneralSecurityException` na decifragem; `OfflineCommandService` já aplicava o handler num `TransactionTemplate`.
  - `files`: o `presigned.url().toURI()` (`URISyntaxException`, `S3FileStorage.kt:183`) é alcançado por `FilesService.downloadUrl` (não por `download`, como dizia o plano), sem escrita antes. No `upload`, o reencode roda antes das escritas e um rollback agora também apaga o objeto do S3 (`removeOnRollback`), como no caminho de `RuntimeException`.
  - `MessageDigest.getInstance("SHA-256")` (`PrintAgent`, `OfflineChanges`, `RefreshTokens`, `PushDevice`, `FileContentRules`, `IdempotencyFilter`): inalcançável.
  - `fnrh`: `RestClient` converte `IOException` em `ResourceAccessException`; envio fora de transação.
  - `notifications`: `FcmPushGateway` captura as exceções; **achado**: `SignedJWT.sign` declara `JOSEException`, não capturada em `requestAccessToken` (virou pendência, item 9). O ouvinte de push não tem escrita própria.
  - `endofday`, `reservations`, `guests` e jobs (`ProvisionalExpiry`, `InventoryHorizonJob`, `GuestDocumentRekeyJob`, `FileOrphanPurgeJob`): transação própria por item ou `TransactionTemplate`, sem transação externa. `iam`: `JwtEncodingException` é não-checada.
  - Dos 83 `catch`/`runCatching` amplos de `src/main`, nenhum engole uma *checked* vinda de um proxy que compartilhe a transação (conferência por amostragem da revisora nos cinco `noRollbackFor` e nos `catch` dos casos de uso).
- **Teste do critério:** `RollbackOnAllExceptionsTest` "a checked exception from an audited use case leaves neither the write nor the trail entry", vermelho antes (`expected:<0> but was:<1>`).

### 4. `ZenyHotelManager - Eventos e jobs`

**Substitui** a subseção "Log das exceções dos jobs (decisão da M6 E18, 2026-11-13; ainda não implementada)": agora é comportamento atual, com os detalhes abaixo. **Complementa** o marcador "Jobs são `@Scheduled` com `@SchedulerLock`" do texto literal (que cita `SchedulingConfiguration.kt`).

- **`JobErrorLoggingTaskScheduler`** (`shared/infrastructure/scheduling/ScheduledJobErrors.kt`): subclasse do `ThreadPoolTaskScheduler`, montada pelo builder do Boot como o bean **`taskScheduler`**. Vale para os 15 `@Scheduled` de hoje e para os futuros, sem código por job (a alternativa `try/catch` por job continua descartada). Um `TaskDecorator` não serviu: no Spring 7.0.10 ele recebe o future e não chega ao nome do job.
- **Formato:** toda falha de tarefa do agendador sai em `ERROR` como `Job <Classe.método> falhou: <Classe>[ <- <Causa>…]`: só o nome do job e as classes da exceção e das causas, **sem mensagem, sem stack trace e sem as suprimidas**, com proteção contra ciclo. Inclui a falha da trava do ShedLock com o banco fora, que acontece antes do método. O nome logado é o `toString()` do `Runnable` (o KDoc ainda não avisa isso).
- **Logger do ShedLock em `OFF`** (decisão (d)): `net.javacrumbs.shedlock.provider.jdbctemplate.JdbcTemplateStorageAccessor` fica em `OFF` no `application.yaml`, porque logava a `DataAccessException` com a mensagem do JDBC (ARCHITECTURE §16). **Custo:** o "Unlock failed after 10 attempts" também some; uma trava que não se solta fica presa até o `lockAtMostFor`, sem sinal no log. Alternativa: um filtro que descarte só os eventos com exceção, mantendo a linha sem ela.
- **`spring.task.execution.mode: force`** (decisão (f)): o bean `taskScheduler` novo desligava o `applicationTaskExecutor` (dos `@Async` e dos ouvintes do Modulith); o `force` o mantém. Efeitos:
  - há **dois beans `Executor` padrão** (o agendador e o `applicationTaskExecutor`): injetar `Executor`/`TaskExecutor` sem qualificador falha no boot, de forma ruidosa;
  - ligar *virtual threads* não troca mais o agendador;
  - um `schedule`/`submit` **avulso** no agendador (um `Future` que ninguém espera) passa a logar e engolir a exceção; hoje não há uso em `src/main`.
- **Atenção ao upgrade do ShedLock:** no `master` do ShedLock, o `KeepAliveLockProvider` loga a exceção (`warn` com `e`); a 7.10.1 não. Ao subir de versão, rever esse logger, que o `OFF` atual não cobre e que o `endofday` usa (trava `end-of-day-run` com keep-alive).
- **Teste do critério:** `ScheduledJobErrorLogTest` "a failing lock is logged with the job name and only the exception classes": job real `IdempotencyKeyPurgeJob.purgeExpiredKeys`, com a trava falhando com sentinela na mensagem e na causa; o vermelho antes vinha do `TaskUtils$LoggingErrorHandler`. Ataques: suprimidas, ciclo, 5000 causas, `Error`, `toString()` que lança, falha no corpo, reagendamento (cron, rate e delay) e `@Async`/ouvintes no `applicationTaskExecutor`.
- Mudar o executor do `endofday` ficou fora (já loga só a classe).

### 5. `ZenyHotelManager - Docker, observabilidade e CI`

**Complementa** o marcador "Valores do banco fora do log" (M1 E03), que trata do DETAIL do PostgreSQL e de `logServerErrorDetail=false`; não substitui nada.

- A mensagem do JDBC ainda pode trazer valores mesmo sem o DETAIL. Desde a E18, o log das exceções que escapam de um job não tem mensagem (item 4 acima), e o logger do ShedLock `JdbcTemplateStorageAccessor` está em `OFF`.
- **Pendência:** quatro jobs ainda **capturam e logam a própria falha com a mensagem** (ARCHITECTURE §16), fora do tratador novo, que só vê o que escapa: `FileOrphanPurgeJob.kt:36`, `ProvisionalReservations.kt:88`, `InventoryHorizonJob.kt:32` e `OutboxMetrics.kt:74`. Entram na etapa de manutenção sugerida (item 9).
- Ainda sobre o log, achado da E16 (já no handoff dela): em `prod`, chave de MDC chamada `service` ou `process` (ou com esses prefixos e ponto) faz o escritor ECS falhar e a linha some; as chaves de hoje não colidem.

### 6. `ZenyHotelManager - Schemas, migrações e views de relatório`

**Complementa** (a nota não trata do alcance dos tipos de data; entra um parágrafo novo, ao lado de "Schemas e migrações" ou da persistência):

- **Piso efetivo do driver (ARCHITECTURE §11, atualizada em `04004ba`):** o `date` e o `timestamptz` do PostgreSQL vão até `-4713-11-24` e `+5874897-12-31` / `+294276-12-31`, mas o **pgjdbc só representa a partir de `-4712-01-01`**: qualquer data ou instante anterior a esse dia é enviado como `-infinity`, sem erro. O piso efetivo do projeto é `-4712-01-01` (`StorableRange`, ver item 2). A §11 dizia `-4713-11-24` antes.
- Efeito sobre dados: uma data `LocalDate.MAX` é gravada como `infinity` e relida como `LocalDate.MAX` (ver pendência I2 no item 2).
- Sem migração nova na E18; a última continua `printing/V2026_11_11_1001__grant_printing_to_app_role.sql` do ponto de vista do roadmap herdado do M5, sem mudança neste lote.

### 7. `ZenyHotelManager - Testes de integração`

**Complementa** (sem substituir nada) o texto literal sobre `@IntegrationTest` e contexto em cache.

- **`KernelProbesConfiguration`** (`src/test/kotlin/com/zeny/hotel/testsupport/KernelProbes.kt`, `@TestConfiguration`): a **combinação de contexto** para testes do kernel que precisam de sondas (`@IntegrationTest` + esta configuração), para reaproveitar o mesmo contexto em cache. Traz:
  - `TransactionProbe` (casos de uso só de teste `@Audited` + `@Transactional` que gravam, descrevem a entidade e lançam uma *checked* ou uma recusa com `noRollbackFor`) e `RollbackScenarios` (cenários do rollback: `noRollbackFor` listado, de superclasse, não listado, `RuntimeException`, `Error`, escrita com sucesso, *checked* engolida numa transação unida e listener `@ApplicationModuleListener` assíncrono que lança);
  - `FailingLockProvider` (bean `@Primary`, `ExtensibleLockProvider`: delega ao `lockProvider` de produção e só falha para o nome de trava que o teste arma com `failFor(nome, erro)`; **quem arma desarma num `finally`** com `disarm()`, porque o contexto é compartilhado). Serve às sondas da transação e da trava do agendador;
  - sem `@Service`: os beans vêm só da configuração, para não entrar na varredura de todos os contextos.
- **Helpers** `insertMarker(jdbc, marker)` e `rowsWithMarker(jdbc, marker)` (mesmo arquivo, `internal`): gravam e contam linhas em `test_support.example_task` com o marcador como título; é como os testes de rollback provam que a escrita foi ou não desfeita. Os helpers de teste foram unificados na rodada 1 da Task 4 (`54977db`).
- **Log dos testes:** `ProductionProfileApiTest` e dois do `LogMessagesAttackTest` sobem o profile `prod` e reinicializam o logback da JVM inteira (ECS, `root: INFO`) até o próximo contexto; uma asserção negativa sobre linha DEBUG pode passar à toa conforme a ordem (achado da E16, ainda aberto).
- **Processo (memória):** a máquina de 14 GB **não comporta o `./gradlew build` deste repositório junto com o build do DesktopFront**. No segundo lote da E18, a RAM livre caiu a ~700 MB, e o Claude Code encerrou o primeiro gate e o vigia de memória. O orquestrador pôs `oom_score_adj=800` nas JVMs do Gradle e do Kotlin dos dois projetos, para o OOM derrubar um build e não uma sessão. Regra: rodar o gate com o front parado, ou com `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1`. Testes de uma etapa não devem usar laço `while pgrep -f` com um trecho de comando (o padrão casa com a linha do próprio laço e nunca termina; nota da E17).
- **Trailer `Soul:`** dos commits precisa ficar no mesmo parágrafo do `Co-Authored-By` (senão não é lido como trailer; achado da verificação mecânica).

### 8. Menores da revisão final, sem correção na E18 (para o curador conhecer)

- Comentário do Jackson em `application.yaml:13-20` ficou acima do bloco `task:`; o KDoc de `ScheduledJobErrors.kt` não avisa que o nome logado é o `toString()` do `Runnable` nem que o `Future` avulso engole a exceção.
- Testes: `StrictDateTimeJsonAttackTest.read` não distingue recusa de `null` (o `""` num `Instant` não está provado; a forma `"2026-1-3"` não está no teste); o teste "the async executor is not the job scheduler" afirma a ausência antes do log poder sair; o teste offline do array confere só o `code`; `expectDateMismatch()` do `EndOfDayStorableRangeAttackTest` não confere a data corrente; helpers no meio do `PaginationTest`, `roomAndReservation()` sobrando na 3a, `assertInvalidCursorOn` não tipado, lista repetida na escala e o *wrapper* `rowsWith` de uma linha.

### 9. Etapa de manutenção sugerida (para o `arquiteto`)

- Recusar no corpo as datas e os instantes fora do `StorableRange` (resolve a decisão (e), o `500` com `+5874898-01-01` e o `infinity` com `LocalDate.MAX` nos recados; conferir `out-of-order` e a escala).
- Um `Converter` estrito para datas e instantes em query string e path.
- Tirar a mensagem do log de `FileOrphanPurgeJob.kt:36`, `ProvisionalReservations.kt:88`, `InventoryHorizonJob.kt:32` e `OutboxMetrics.kt:74`.
- Trocar o `OFF` do ShedLock por um filtro (decisão (d)).
- Capturar a `JOSEException` em `FcmPushGateway.requestAccessToken`.
- Subir o `opentelemetry-api` 1.62.0 (GHSA-ccrj-gw8r-854m, DoS por regex no `W3CTraceContextPropagator` lendo `tracestate`; corrigido na 1.67.0), nota herdada da E17; já tem etapa dona na M8 E17.
- Hub `ZenyHotelManager`: a seção "Estado" deve passar a "M6: E10, E11 e E14 a E18 `#concluida`" e "Próximos passos" deixa de listar a E18 (resta E01 e demais).

## Decisões para o usuário

Decisões (a) a (f) do handoff da E18, tomadas pela opção recomendada e **revisáveis; nenhuma foi confirmada pelo usuário**. A etapa não tinha revisão humana. Texto do handoff, com redação do agente:

- **(a) Piso da faixa do cursor em `-4712-01-01`**, e não `-4713-11-24` como a ARCHITECTURE §11 dizia. O testador mediu que o pgjdbc envia como `-infinity` qualquer data ou instante anterior a esse dia; sem a mudança, o cursor no trecho de 38 dias antes do piso devolvia uma página errada em silêncio. A §11 foi atualizada em `04004ba`. Voltar atrás custa trocar uma constante.
- **(b) "Registrado" no comando offline (H13 c)** se lê como "devolvido com `REJECTED COMMAND_PAYLOAD_INVALID`, nunca descartado em silêncio", sem guardar a recusa. O protocolo da §9 continua como está; guardar a recusa mudaria o protocolo offline.
- **(c) A leitura estrita vai além do mínimo do critério, pela §7 ("só o texto"):** recusa também o array `[a,m,d]`, o epoch em texto num instante, o texto sem `T` num instante e o texto com espaço nas pontas. `""` numa data ou num instante agora dá `400 INVALID_FORMAT`; num campo opcional, antes virava `null` e era aceito. Ausente ou `null` seguem como antes. **Avisar o front desktop.** Voltar atrás é afrouxar o `IsoText`.
- **(d) Logger do ShedLock `JdbcTemplateStorageAccessor` em `OFF`.** Pela §16, ele não pode logar a mensagem do JDBC. O custo é que o "Unlock failed after 10 attempts" também some, e uma trava que não se solta fica presa até o `lockAtMostFor`, sem sinal no log. A alternativa é um filtro que descarte só os eventos com exceção, mantendo a linha sem ela.
- **(e) A regressão I2 da revisão final fica para uma etapa de manutenção.** Um recado criado com `dueOn` = `+999999999-12-31` dá `201` e é gravado como `infinity`; na leitura vira `LocalDate.MAX`, e o próximo cursor da lista sai fora do `StorableRange`, então o `PageCursor` o recusa com `400 INVALID_CURSOR` e o resto da lista fica inalcançável. Antes da E18, a paginação seguia. Exige uma data absurda posta de propósito por quem pode escrever recados, e nenhum cliente está em produção. A correção recomendada é recusar no corpo as datas e os instantes fora do `StorableRange`, e não afrouxar o cursor. Fazer isso agora no mapeador quebraria a releitura de JSON persistido e o teste de releitura do alcance inteiro, e o roadmap põe datas fora do alcance no corpo fora do escopo desta etapa.
- **(f) `spring.task.execution.mode: force`.** Há dois beans `Executor` padrão (o agendador e o `applicationTaskExecutor`): injetar `Executor`/`TaskExecutor` sem qualificador falha no boot, de forma ruidosa. Ligar *virtual threads* não troca mais o agendador. Um `schedule`/`submit` avulso no agendador passa a logar e engolir a exceção (hoje não há uso em `src/main`).

**Aviso:** o front desktop deve saber da mudança do `""` em datas e instantes opcionais (agora `400 INVALID_FORMAT`; para "sem valor", omitir o campo ou enviar `null`).

## Contexto

Fechamento da etapa E18 do M6 do ZenyHotelManager (servidor), publicado pelo orquestrador do lote, conforme a regra "ZenyHotelManager - atualização `<slug>` Eyy" do hub. A E18 resolveu no `shared` quatro problemas transversais achados na E10 (decisão do usuário de 2026-11-13, H12, com escopo de H13): cursor com chave fora do alcance do banco dando 500, exceção *checked* confirmando transação, datas fora do ISO-8601 e log de job com mensagem do JDBC. Nenhum foi introduzido pela E10. A E18 ficou entre o fechamento/manutenção herdada e a governança (E01 em diante).

## Origem

- Projeto: ZenyHotelManager, repositório `/home/caio/repos/ZenyHotelManager`; worktree `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m6-operacao-fechamento`.
- Branch `roadmap/m6-operacao-fechamento`, commits `a5b0902` a `ed0f5ab` (E18); ainda não integrada na `main`.
- Fonte principal: `docs/roadmaps/roadmap-m6-operacao-fechamento.md`, seção "E18 — Faixa do cursor, rollback em toda exceção, datas estritas e log dos jobs", bloco "Evidências e handoff" (já escrito e conferido, segundo o orquestrador). Contexto: `docs/ARCHITECTURE.md` §5, §7 ("Datas e valores"), §11 e §13.
- `KernelProbesConfiguration` e os helpers `insertMarker`/`rowsWithMarker`: lidos diretamente em `src/test/kotlin/com/zeny/hotel/testsupport/KernelProbes.kt` do worktree.
- Notas e capturas lidas do vault antes de escrever: `ZenyHotelManager - Estado por marco` (subseções "M6 E17", lista de decisões), `Convenções de API`, `Auditoria`, `Eventos e jobs`, `Docker, observabilidade e CI`, `Schemas, migrações e views de relatório` e `Testes de integração`; capturas pendentes do projeto em `00 Inbox/` (três, todas sobre o front desktop e o pedido PF-02; nenhuma trata de cursor, transação, datas ou jobs, então nada aqui as contradiz).

## Por que registrar

Atualizar as notas de tema na próxima passagem do curador: três subseções "ainda não implementada" (Convenções de API, Auditoria, Eventos e jobs) viram comportamento atual; o Estado por marco ganha a E18; as decisões (a) a (f) entram na lista de decisões sem confirmação; e as pendências de manutenção ficam para o `arquiteto`.

## Limitações e incertezas

- Resumo do agente a partir do handoff e dos arquivos citados; os números do gate (4160 testes, 23m 4s), do oasdiff, do `osv-scanner` e as provas de mutação seguem o handoff e **não foram reconferidos** pelo agente que escreveu esta captura.
- O texto da ARCHITECTURE §11 e o código de `StorableRange`, `StrictDateTimeJson` e `ScheduledJobErrors` não foram lidos diretamente; vêm do handoff.
- O merge na `main` ainda não aconteceu; os hashes `a5b0902` a `ed0f5ab` valem na branch da etapa.
- Dependência local: o roadmap, os planos e o arquivo `KernelProbes.kt` existem apenas no repositório e no worktree acima.
- Não foi verificado se o `README.md` ou o `api/openapi.yaml` precisam de texto novo; o handoff diz que o contrato não mudou.

## Possíveis conexões

[[ZenyHotelManager]], [[ZenyHotelManager - Estado por marco]], [[ZenyHotelManager - Convenções de API]], [[ZenyHotelManager - Auditoria]], [[ZenyHotelManager - Eventos e jobs]], [[ZenyHotelManager - Docker, observabilidade e CI]], [[ZenyHotelManager - Schemas, migrações e views de relatório]], [[ZenyHotelManager - Testes de integração]], [[ZenyHotelManager - Módulo endofday]], [[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]], [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E17 - cb3979d0]].
