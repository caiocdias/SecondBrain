---
type: capture
status: archived
created: 2026-11-12
capture_id: 2c135bbf-8248-4987-a617-dcb3fa94c0a5
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E12

## Conteúdo capturado

Captura de fechamento da etapa M5 E12 (gate do marco), concluída em 2026-11-12 na branch `roadmap/m5-recepcao-fnrh`. Organizada por nota de tema; em cada item diz se **substitui** ou **complementa** qual trecho. Os itens 1 e 2 (correções G1 a G14) vêm da auditoria só de leitura das notas contra o código, feita na base `3a9542c`; os acréscimos da E12 estão nos itens 3 a 6. Esta captura vale sobre as capturas pendentes das E08, E10, E11 e E16 onde tratarem do mesmo trecho.

### 1. Correções da auditoria (G1 a G14), por nota

**1.1 `ZenyHotelManager - Hospedagem e recepção`**

- **G1, complementa** (nova subseção "Estado final do M5" em "Atualizações por capturas"; a lista literal do check-in orquestrado, com 8 entradas, está desatualizada): **Dependências do `frontdesk` (2026-11-12):** `allowedDependencies = ["shared", "hotel", "reservations", "rooms", "guests", "billing", "files", "rates", "staff", "printing"]` (`frontdesk/FrontdeskModule.kt:34-36`). O `rates` entra só pelos tipos públicos da `ReservationsApi`; o `staff`, só pela `StaffApi` (recados, E06); o `printing`, só pela `PrintingApi` e pelos tipos de documento (ficha de registro, E11). Nunca `fnrh` nem `iam`. O `ModularityTest` confere a lista exata (`ModularityTest.kt:368-425`).
- **G2, substitui** a frase "Sem consumidor de produção até a E08 (`fnrh`) e o M6 (`housekeeping`)" (eventos) por: `GuestCheckedIn`, `GuestCheckInUndone` e `GuestCheckedOut` têm consumidor de produção desde a E08: `FnrhSubmissionListeners` (`fnrh/application/FnrhSubmissionListeners.kt:39-111`), que só grava a submissão de envio à FNRH, uma por evento, com a `version` do evento como ordem causal. `RoomMoved` segue sem consumidor (a API v2.4 da FNRH não tem UH); o M6 (`housekeeping`) é o próximo consumidor de `GuestCheckedOut` e de `RoomMoved`. O `frontdesk` continua sem chamar o `fnrh`.
- **G3, complementa** o item "Ficha de registro (M5 E11)" (a captura E11 está correta no comportamento; faltam nomes de código e as decisões da revisão humana): Código: `RegistrationCardService` (caso de uso `@Audited("frontdesk.registration-card.print")`, entidade de trilha `frontdesk.registration-card`), `RegistrationCardController` (`@RequestMapping("/reservations/{id}/registration-card")`, `GET /pdf` e `POST /print`), `FrontdeskDocumentTemplates` (código do template `frontdesk.registration-card`, `templates/frontdesk/registration-card.xhtml` e `.txt`). Situações aceitas: `WITH_CARD = {CONFIRMED, IN_HOUSE, CHECKED_OUT}` (`RegistrationCardService.kt:169`); outras: `409 REGISTRATION_CARD_UNAVAILABLE`. Decisões do usuário (revisão humana de 2026-11-12): a ficha fica sob `frontdesk.stays.checkin`, `GET` sem trilha (D-E11-10); **ainda não aplicado no código**: a descrição da permissão em `FrontdeskPermissions.kt` continua "Fazer o check-in de uma reserva confirmada (com a caução opcional)" e deve passar a dizer que ela abre a ficha (mudar descrição altera o catálogo; fica para a etapa de manutenção do M6). Os rótulos de motivo de viagem e meio de transporte seguem como "(código FNRH)"; a inversão por porta do `frontdesk` implementada pelo `fnrh` (D-E11-11) é uma etapa de manutenção ainda inexistente no roadmap.

**1.2 `ZenyHotelManager - Módulo printing` (nota nova proposta pelas capturas E10 e E11)**

- **G4, complementa** o texto composto das duas capturas (conferidas contra o código e corretas; faltam estes fatos):
  - **Realm do agente:** `PrintAgentRealm` (`printing/infrastructure/PrintAgentRealm.kt:19-44`): `name = "print-agent"`, `pathPrefix = "/api/v1/print-agents/me/"`, `openApiScheme = "printAgentToken"`; `authenticate` só consulta o banco se o token começa por `zpa_`, numa transação `REQUIRES_NEW`, e grava o contato (`recordContact`, no máximo uma vez por minuto, `printing/infrastructure/PrintingPersistence.kt:22`). Falha de banco propaga (`500`), nunca `401`.
  - **Permissões de leitura das impressoras:** `GET /api/v1/printers` e `GET /api/v1/printers/{id}` exigem `printing.jobs.read` (`PrintAgentsService.kt:199,205`); criar, alterar, desativar impressora e todo o cadastro de agentes exigem `printing.agents.manage`. A tabela "Rotas e permissões" da captura E10 junta tudo numa linha; as duas leituras de impressora são a exceção.
  - **Trilha** (`printing/application/PrintingAudit.kt:8-19`, `PrintJobsService.kt:251`): `printing.agent.create`, `printing.agent.rotate-token`, `printing.agent.deactivate`, `printing.printer.create`, `printing.printer.update`, `printing.printer.deactivate`, `printing.job.create` (rota manual e `PrintingApi.enqueue`/`print`), `printing.job.claim`, `printing.job.ack`, `printing.job.release` (as três últimas do ator sistema). O contato do agente não tem trilha.
  - **Validação das propriedades:** diferente do `fnrh`, `PrintingProperties` valida limites ("precisa ser positivo"; `max-manual-content-bytes` não passa de `max-content-bytes`) e a partida falha se violados (`PrintingProperties.kt:49,56`).
  - **Dependências finais:** `shared`, `hotel` e `files` (`PrintingModule.kt:14`); consumidores da `PrintingApi`: `billing` (extrato), `frontdesk` (ficha) e `reservations` (confirmação). Substitui a frase "só `shared`" da captura E10.
  - **Templates dos donos:** `templates/billing/statement.{xhtml,txt}`, `templates/frontdesk/registration-card.{xhtml,txt}`, `templates/reservations/confirmation.{xhtml,txt}` e o layout `templates/printing/layout.xhtml` (só PDF).
  - **Imagem e licença:** a captura E11 traz o crescimento da imagem (171,5 para 178,0 MB); o aviso da LGPL-2.1+ do openhtmltopdf deve entrar na documentação de implantação do M8 (D-E11-1).

**1.3 `ZenyHotelManager - Módulo fnrh`**

- **G5, substitui** o item "`allowedDependencies` hoje" da seção "Camada e dependências" (no lugar do texto da captura E08 item 1.2, que dizia "A `HotelApi.profile()` fica para a E11" como se o `fnrh` a usasse): `allowedDependencies`: `shared`, `guests`, `reservations` e `notifications` (as duas últimas desde a E08, D-E08-14). O `fnrh` **não** depende do `hotel` e não usa a `HotelApi.profile()` (o payload da FNRH não pede dado do hotel, D-E07-12); o consumidor de `HotelApi.profile()` é o `printing` (E11, `PrintingApiService.kt:72`). O `ModularityTest` confere a lista exata (`ModularityTest.kt:331`). A tabela da ARCHITECTURE §3.1 ainda lista `hotel` para o `fnrh`; o código é subconjunto dela.
- **G5, complementa** "Pacotes" (captura E08 item 1.3): além das classes listadas, o código tem em `application`: `FnrhSubmissionFailures`, `FnrhAudit` (códigos de trilha: `fnrh.submission.send`, `.retry`, `.dismiss`, `fnrh.settings.clear-credentials`) e `FnrhMasks`; em `infrastructure`: `SerproFnrhSupport` e `SerproFnrhWire`. As extensões de teste `FnrhSubmissionDismissCompat.kt` existem em **dois** lugares (`src/test/kotlin/com/zeny/hotel/fnrh/` e `.../fnrh/domain/`), não em um; a limpeza prometida deve apagar as duas.

**1.4 `ZenyHotelManager - Schemas, migrações e views de relatório`**

- **G6, complementa** "Atualizações por capturas" com a subseção "Schemas `fnrh` e `printing`, e demais migrações do M5":
  - **`fnrh`** (E07, `fnrh/V2026_11_04_1000` a `_1030`; E08, `V2026_11_10_1000` e `_1100`): `fnrh.settings` (linha semente, versão 0, desligada), `fnrh.requester`, `fnrh.integration_call` (*append-only*, `AppendOnlyTables` em `fnrh/infrastructure/JdbcFnrhIntegrationLog.kt:131`, sem coluna de texto livre), `fnrh.domain_value`, e da E08 `fnrh.submission`, `fnrh.submission_error`, `fnrh.remote_reservation`, `fnrh.remote_guest` (texto em "Módulo fnrh"). `GRANT` pela migração `_1001` (DML por `ALTER DEFAULT PRIVILEGES`).
  - **`printing`** (E10, `printing/V2026_11_11_1000__create_printing_tables.sql` e `_1001`): `printing.print_agent` (`token_hash char(64)` único, `token_generation`, `active`, CHECK "inativo não tem hash"), `printing.printer` (`kind` CHECK `THERMAL_ESCPOS`/`A4_PDF`, FK para o agente dentro do schema), `printing.print_job` (sequence `printing.print_job_position_seq`, `position` único, `status` CHECK `PENDING/SENT/PRINTED/FAILED`, `content bytea` cifrado, `content_purged_at`, `delivered_to` sem FK, `failure_code`; índices da fila, do reenvio, da validade e do expurgo). Nenhuma tabela *append-only* e nenhuma view.
  - **Outras migrações do marco:** `reservations/V2026_10_22_1546__add_stay_transitions.sql` (E01), `billing/V2026_10_22_2330__add_posting_source_reference.sql` (E04), `guests/V2026_11_06_1000__add_guest_gender_description.sql` (E15). Nenhuma migração nas etapas E11, E13, E14, E16 (nem na E12).
  - **Views `report_*`:** a lista "Publicadas" ganha `fnrh.report_submissions` (E08), a única view nova do M5 (`fnrh/V2026_11_10_1100__create_fnrh_report_views.sql:18`).
  - **Tabelas *append-only*:** além das já citadas, `fnrh.integration_call` (E07).

**1.5 `ZenyHotelManager - Docker, observabilidade e CI`**

- **G7, complementa** "Métricas" (consolida os trechos soltos das capturas): métricas do M5 em `/actuator/prometheus` (todas por `MeterBinder`, nenhuma com regra de alerta em `docker/prometheus/alerts.yaml`): `zeny_fnrh_calls_total` (tags `operation`, `outcome`, `environment`), `zeny_fnrh_last_success_seconds`, `zeny_fnrh_last_failure_seconds` (`NaN` sem registro), `zeny_fnrh_configured` (0 ou 1) (E07, `fnrh/infrastructure/FnrhMetrics.kt:60-63`); `zeny_fnrh_submissions{status="pending|failed|invalid"}` (E08, `FnrhMetrics.kt:98`, `GROUP BY` a cada raspagem, `NaN` se a leitura falha); `zeny_printing_jobs{status="PENDING|SENT|FAILED"}` (E10, `printing/infrastructure/PrintingMetrics.kt:50`; `FAILED` só dos terminados dentro de `content-retention`). Sem `HealthIndicator` da FNRH nem do `printing`: a readiness não depende deles.

**1.6 `ZenyHotelManager - Ambiente, banco, chaves e build`**

- **G8, substitui** "Os lockfiles continuam com 415 e 74 pacotes." (seção "Spring Boot 4.1.2 e restrições de versão") por: Desde a E11, `gradle.lockfile` tem 426 pacotes (eram 415) e `buildscript-gradle.lockfile`, 74. A E11 acrescentou `io.github.openhtmltopdf:openhtmltopdf-core` e `-pdfbox` 1.1.110, `org.apache.pdfbox:pdfbox`, `fontbox`, `pdfbox-io` e `xmpbox` 3.0.8, `de.rototor.pdfbox:graphics2d` 3.0.1, `org.thymeleaf:thymeleaf` e `thymeleaf-spring6` 3.1.5, `org.attoparser:attoparser` 2.0.7, `org.unbescape:unbescape` 1.1.6 e subiu `commons-logging` de 1.3.6 para 1.4.0 (commit `8241810`). Declarações diretas no catálogo: `thymeleaf-spring6` (versão do BOM do Boot), `openhtmltopdf-pdfbox` e, só em teste, `pdfbox`. O openhtmltopdf é **LGPL-2.1+** (D-E11-1): registrar o aviso na documentação de implantação do M8. Propriedades novas, todas com padrão em `application.yaml` e sem variável de ambiente: `zeny.fnrh.submissions.*` e `zeny.printing.*`.

**1.7 `ZenyHotelManager - Testes de integração`**

- **G9, complementa:**
  - O `@IntegrationTest` adia oito jobs (`testsupport/IntegrationTest.kt:26-35`): `RESUBMISSION_JOB_DEFERRED`, `OUTBOX_PURGE_DEFERRED`, `FILES_PURGE_DEFERRED`, `GUESTS_REKEY_DEFERRED`, `INVENTORY_HORIZON_DEFERRED`, `PROVISIONAL_EXPIRY_DEFERRED`, `FNRH_SEND_DEFERRED` (`zeny.fnrh.submissions.initial-delay=PT24H`, `:90`: um job solto enviaria as submissões de outros testes do banco compartilhado e gastaria as respostas do WireMock) e `PRINTING_MAINTENANCE_DEFERRED` (`:96`). Os testes de envio chamam `sendDueFor` só para a própria reserva.
  - `FnrhTestServer` (`testsupport/FnrhTestServer.kt:30`): **um WireMock por JVM**, compartilhado por todos os contextos; cada teste chama `reset()` no início e no fim, filtra as requisições pelos ids remotos ou pelo código da própria reserva e só envia as submissões dela. `FnrhTestConfiguration` aponta as duas URLs para ele. O teste que mexe na configuração da FNRH, no perfil do hotel ou na política de early/late devolve o original em `finally`.
  - `InventoryListenersQuiescence` espera também as publicações de `FnrhSubmissionListeners` antes de baixar `/api/v1/sync/changes` (`testsupport/InventoryListenersQuiescence.kt:43`).

**1.8 `ZenyHotelManager - Módulo notifications`**

- **G10, complementa:** **Primeiro disparo de `integration-failure` (M5 E08):** `FnrhSubmissionRecorder` chama `NotificationsApi.notify(INTEGRATION_FAILURE, "Falha no envio à FNRH", "Reserva <código>: <operação> — <falhou | dados inválidos>", NotificationRecipients.withPermission(fnrh.submissions.manage))` depois do commit, em transação própria; só o código da reserva e rótulos fixos entram no texto (`fnrh/application/FnrhSubmissionRecorder.kt:127`). O `fnrh` passa a depender do `notifications` (`FnrhModule.kt:18`). O `printing` **não** depende do `notifications`: sem alerta de falha de impressão (decisão (d) do usuário na revisão humana da E10).

**1.9 `ZenyHotelManager - Módulo guests`**

- **G11, complementa** a descrição da API pública: **`GuestsApi.identification(id): GuestIdentification?`** (M5 E02 e E11, `guests/GuestsApi.kt:83`): o perfil **corrente** (num mesclado, o sobrevivente, com o id dele em `GuestIdentification.id`), a situação, a nacionalidade, a data de nascimento, os documentos como `MaskedGuestDocument(id, type, issuingCountry, maskedNumber)` (sufixo gravado em claro; nada é decifrado) e, desde a E11, `address: Address?` (nulo sem endereço ou anonimizado; `GuestsApi.kt:271`). `toString` não leva dado pessoal nem o endereço. Consumida pelo `frontdesk` (regra mínima do check-in e ficha de registro) e pelo `fnrh` (`GuestsApi.identification(id).id` para identificar o sobrevivente).

**1.10 `ZenyHotelManager - Módulo billing (contas, roteamento e taxa de serviço)` e `ZenyHotelManager - Módulo billing (caixa, pagamentos, caução e encerramento)`**

- **G12, complementa** a primeira nota (lista literal `["shared","hotel","guests","notifications","payments"]`): `allowedDependencies` do `billing` em 2026-11-12: `shared`, `hotel`, `guests`, `notifications`, `payments` e `printing` (o `printing` desde a E11, só a `PrintingApi` e os tipos de documento, para o extrato em PDF e ESC/POS; `billing/BillingModule.kt:24`). Nunca `iam` nem reservas: o dono da conta é descrito pela porta `FolioOwnerDescriber`, que o dono implementa.
- **G12, complementa** a segunda nota, em "caução" (que cobre `unsettledCardPreAuthorizations` e `release`, mas não o registro): `BillingApi.registerCardPreAuthorization(folioId, NewCardPreAuthorization)` (M5 E02, `billing/BillingApi.kt:118`) registra a caução do check-in com as regras de `POST /api/v1/folios/{id}/card-pre-authorizations` **menos a permissão**, auditada `billing.card-pre-authorization.register`; não muda saldo nem versão da conta, não exige turno de caixa, exige usuário autenticado. Fecha a trinca da caução na `BillingApi` junto com `unsettledCardPreAuthorizations` e `releaseCardPreAuthorization` (E04).

**1.11 `ZenyHotelManager - Módulo reservations (inventário, disponibilidade e reservas)`**

- **G13, complementa** (o texto diz `["shared","hotel","rooms"]` e, desde a E06, `rates`): `allowedDependencies` do `reservations` em 2026-11-12: `shared`, `hotel`, `rooms`, `rates`, `guests`, `billing`, `notifications`, `printing` (`reservations/ReservationsModule.kt:24`; o `printing` desde a E11, só a `PrintingApi`, para a confirmação de reserva). Implementa `FolioOwnerDescriber` para `FolioOwnerType.RESERVATION` (`ReservationFolioOwnerDescriber`).

**1.12 Hub `10 Projects/ZenyHotelManager.md` (fatos da auditoria, G14)**

- **Complementa** "Notas do projeto" → "Módulos": `- [[ZenyHotelManager - Módulo printing]]: agentes, impressoras, fila de impressão, documentos (render e print) e o token do agente.` (já previsto na captura E10 item 7).
- **Complementa** "Próximos passos": o `arquiteto` cria duas etapas de manutenção que ainda não existem em roadmap: (1) `guests`, corpo mínimo de `restrict`, `lift-restriction` e `merge` sem `guests.profiles.read` (E15 (h), decidida pelo usuário); (2) rótulos de motivo de viagem e meio de transporte da ficha por porta do `frontdesk` implementada pelo `fnrh` (D-E11-11). M6 começa pelas E10 e E11 do M6 (fechamento com a chave do check-out).
- **Complementa** a descrição do M5 pronto em "Estado por marco": `printing` (E10, E11) é módulo de Plataforma com dependências `shared`, `hotel`, `files`; documentos em PDF e ESC/POS nos três donos; `fnrh` envia por eventos (E08) e limpa a credencial (E16).

**1.13 Conferido e consistente (sem lacuna)**

A auditoria conferiu 62 itens; 14 lacunas (as acima), 4 delas com erro factual em texto já escrito (G1, G2, G5, G8), o resto são faltas. Estão **corretas** e conferidas contra o código: as capturas E08, E10, E11 e E16 nos fatos conferidos; as 10 operações do `FnrhGateway` e o mapeamento evento para operação (8 listeners); a política de retry (8 tentativas, 1 min × 2^(n-1) até 1 h) e as propriedades `zeny.fnrh.submissions.*`; as tabelas e a view da E08; o job `fnrh-submissions-send` e o gauge `zeny_fnrh_submissions`; o alerta `integration-failure`; os endpoints de submissões e `clear-credentials` (E16) e a correção do `500` do status; as permissões do `fnrh`, do `printing` e do `frontdesk`; o realm de credencial de serviço (cadeia `@Order(1)`, 401 pelo `ProblemWriter`) e o esquema `printAgentToken` no contrato; o schema, as rotas, as propriedades `zeny.printing.*`, o job `printing-jobs-maintenance` e o gauge do `printing`; a `PrintingApi` (fachada única), o registro de templates e os três donos; `FolioOwnerDescriber`; o extrato e a confirmação em PDF; `HotelApi.profile()`; `FilesApi.readContent`; as versões da E11; as transições de hospedagem, os eventos e a `RoomsApi`; `frontdesk` sem importar `fnrh`; `printing` e `notifications` sem escutar eventos de negócio; `frontdesk.trace`; os lockfiles na imagem e na CI (E13, E14); `spring-boot = "4.1.2"`; `allowedDependencies` de `hotel`, `guests` e `files`; nenhum `HealthIndicator` novo; o SSE do agente fora do `RealtimeHub`; nenhuma view `report_*` além de `fnrh.report_submissions`; a divergência conhecida `FnrhSettingsResponse.username` em claro contra a ARCHITECTURE §12 (item 6).

### 2. Pendências fora do brain achadas pela auditoria

- `docs/ARCHITECTURE.md` §14 dizia "o `printing` só depende do `shared`" (resíduo da E10): **corrigido na E12** (o `printing` depende de `shared`, `hotel`, `files`).
- `README.md` dizia "O PDF do extrato vem no M5" apesar da E11: corrigido na E12 para apontar para "Documentos impressos".
- Descrição de `frontdesk.stays.checkin` sem mencionar a ficha (D-E11-10): não corrigida (altera o catálogo); fica para a manutenção do M6.
- Duas cópias de `FnrhSubmissionDismissCompat.kt` nos testes: dívida de teste, não é gate.
- Nenhum defeito de produção achado na auditoria.

### 3. `ZenyHotelManager - Docker, observabilidade e CI` (complementa, E12)

**Compose isolado do gate**, versionado em `docker/gate/` (decisão R1 da E12; antes ficava no scratchpad). Para o gate do M6, é o modelo. Detalhes exatos em `docker/gate/README.md`.

- `run-gate.sh <workdir> <porta> [projeto]`: o ciclo completo. Gera o env sorteado pelo `gate-env.sh` (modo 600, nunca dentro do repositório nem sob um `.git`, nunca lê o `docker/.env`), confere a composição (`config -q`, nunca sem `-q`, que imprimiria segredos), sobe com `up -d --build`, espera o readiness (até 300 s), roda o `m5-roteiro.sh` e sempre faz `down -v --remove-orphans` por `trap` (também em falha e Ctrl+C), apagando o `gate.env` e contando as sobras do projeto. Recusa (saída 2) o projeto `zeny` (o do usuário), nome de projeto inválido e um projeto que já tenha contêiner, volume ou rede.
- `compose.gate.yaml`: `name: zeny-gate`, imagem `zeny-hotel-manager:gate` (nunca a `:dev`) e um WireMock da FNRH (`wiremock/wiremock:3.13.2` fixado por digest, sem porta publicada, só alcançável na rede do projeto) para onde apontam as URLs de homologação **e** de produção da FNRH (`ZENY_FNRH_HOMOLOGATIONURL` e `ZENY_FNRH_PRODUCTIONURL`). Logo, o gate nunca chama o Serpro real, em nenhum ambiente. Stubs da API v2.4 em `docker/gate/fnrh-mock/mappings/*.json`, com os mesmos contratos do `FnrhTestServer`.
- `m5-roteiro.sh <base-url> <projeto> <env-file>`: roteiro `curl`/`jq` pelo proxy, 13 seções (públicos, usuários, cadastro, check-in, FNRH, ficha pelo agente, estadia, check-out, walk-in e desfazer, recados, Serpro fora do ar, E16 e varredura), **302 conferências no M5**. A varredura de segredos e de dados de hóspede cobre os logs de `api`, `db`, `proxy`, `storage` e `storage-init` e a própria saída do roteiro (o `fnrh-mock` fica de fora: faz o papel do Serpro e recebe os dados por desenho). Segredos só em variáveis e arquivos temporários (modo 600), nunca em argumentos nem na saída; falhas redigem esperado e obtido.
- **O roteiro só roda num banco novo** (troca a senha do admin inicial): `up -d --build` depois de `down -v`, readiness `UP`.
- Antes do `up --build` (compila dentro do Docker): rode um build pesado por vez; confira `free -g` e que não há Gradle nem `docker build` de outra sessão; **nunca rode `./gradlew --stop`** (ver item 4).
- Os 39 `WARN` do PDFBox ("Using fallback font", D-E11-4) no log da `api` são esperados e não são vazamento.

### 4. `ZenyHotelManager - Testes de integração` (complementa e substitui, E12)

**Complementa** com o `MilestoneM5EndToEndTest` (raiz do pacote de testes, 8 testes) como modelo de teste de gate:

- operadores pelos modelos de role do boot; o Administrador só para as ações sem modelo de role (FNRH, agente e impressora, política);
- só as submissões FNRH da **própria reserva** são enviadas e contadas no WireMock compartilhado;
- o relógio é devolvido no `finally`;
- o "desfazer expirado" recua o `checked_in_on` da própria reserva em vez de avançar a data operacional do banco compartilhado (**nunca avance a data operacional**);
- varredura de dados de hóspede no banco inteiro.

**Substitui**, na captura pendente `2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E11 - d1100f5a` (item 9, primeiro marcador, por volta da linha 67: "Rode um Gradle por vez e `./gradlew --stop` entre tarefas"), a recomendação do `./gradlew --stop` por: **nunca rode `./gradlew --stop`**: ele derruba os daemons de outras sessões do usuário (aconteceu na E12 com a sessão do ZenyHotelManager-DesktopFront). Antes de execução longa, confira a memória livre (`free -g`) e se há build pesado de outra sessão. Máquina de 14 GB: um Gradle ou `docker build` por vez (o resto do marcador, sobre a memória esgotada e o Java morto pelo kernel, segue valendo).

### 5. Estado: `ZenyHotelManager - Estado por marco` e o Estado do hub `10 Projects/ZenyHotelManager.md` (substitui, E12)

**Substitui** a linha de estado do M5 (a das capturas E11 e anteriores) por: **M5 com todas as etapas concluídas, exceto a E09 `#bloqueada`** (Q-12; pendência obrigatória antes da operação real, cobrada pelo gate de inauguração M8 E13). **E12 (gate) `#concluida` em 2026-11-12**, com o gate verificado:

- numa **cópia limpa** (`git archive` de `6c16557`), em três rodadas: `clean build` e 2x `clean test`, 3228 testes e 0 falhas cada; `lint checkOpenApi` verde; lockfiles sem diferença; oasdiff contra `ffae917` sem `ERR`; `osv-scanner` 426 + 74 pacotes, 0 Critical, 0 High, 2 Medium e 3 Low aceitos na E14;
- no **compose isolado** a partir da cópia: 302 conferências, 0 falhas, listener do `fnrh` `COMPLETED` para `ReservationCreated`, `GuestCheckedIn` e `GuestCheckedOut`.

**Revisão humana da E12 pendente** (a etapa tem "Revisão humana: sim"). **Próximo marco: M6** (sincronizar o roadmap do M6 com o código antes do primeiro lote). Revisão final: aprovado com ressalvas, pronto para merge. Integração na `main` por merge local no fim do lote (o push é do usuário).

**Hub, "Próximos passos" — substitui** "Executar o gate E12 do M5 pelo `claude --agent orquestrador`, depois da revisão humana da E11" (e variantes) por: "Revisão humana da E12; depois, sincronizar o roadmap do M6 com o código e executar o M6".

### 6. Hub, "Perguntas abertas" (complementa, E12)

**Decisões da E12 sem confirmação do usuário** (opção recomendada, pelo orquestrador; a revisão humana da E12 pode revertê-las):

- **R1:** o compose isolado do gate versionado em `docker/gate/` (item 3).
- **R2:** defeito achado no gate corrigido na própria etapa, sem mexer em tag de outra etapa; nenhum defeito de produção apareceu.
- A imagem do mock (WireMock) tem CVEs de SO segundo scanners de terceiros: **aceita como risco** (só no gate, sem porta publicada).
- A ARCHITECTURE §14 foi corrigida (o `printing` depende de `shared`, `hotel`, `files`).

**Decisões de arquitetura que esperam o usuário:**

- a ordem interna da camada Hospedagem na ARCHITECTURE §3.2 (nota da E03);
- o `FnrhSettingsResponse.username` devolvido em claro contra a ARCHITECTURE §12 ("nunca devolvida"), desde a E07/E16 (`FnrhSettingsController.kt:121-132`, `docs/ARCHITECTURE.md:499`); não é falha grave de segurança (usuário não é segredo), mas é inconsistência de documento ou de contrato.

**Git:** o lote será integrado na `main` por merge local; o hash do merge não estava disponível na publicação, e o push é do usuário.

## Contexto

Fechamento da etapa E12 (gate) do roadmap `roadmap-m5-recepcao-fnrh` do ZenyHotelManager, publicado pelo `brain-escriba` por pedido do orquestrador de etapa, conforme a regra do projeto de publicar `ZenyHotelManager - atualização <slug> Eyy` ao fim de cada etapa que muda algo descrito no brain.

## Origem

- Projeto: ZenyHotelManager; repositório `/home/caio/repos/ZenyHotelManager`.
- Worktree: `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m5-recepcao-fnrh`; branch `roadmap/m5-recepcao-fnrh`.
- Commits da etapa: `6c87b04..` (gate verificado em `6c16557`; auditoria das notas na base `3a9542c`).
- Plano: `docs/superpowers/plans/2026-11-12-m5-recepcao-fnrh-e12.md`.
- Roadmap: `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`, seção E12.
- Documentação: `docker/gate/README.md`; `docs/ARCHITECTURE.md` §3.1, §12 e §14.
- Relatório da auditoria (itens G1 a G14): `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m5-recepcao-fnrh/.superpowers/sdd/2026-11-12-m5-recepcao-fnrh-e12/task-8-report.md`.
- Data: 2026-11-12.

## Por que registrar

Alimentar a consolidação do curador: a auditoria corrige erros factuais e lacunas em notas de tema (hospedagem, fnrh, printing, schemas, Docker/CI, ambiente, testes, notifications, guests, billing, reservations), a E12 acrescenta o compose isolado do gate e o teste de gate, e o Estado do M5 fecha o marco.

## Limitações e incertezas

- Os itens G1 a G14 e os números do gate vêm do relatório da auditoria e do pedido do orquestrador; o escriba conferiu só o texto do `docker/gate/README.md` e a captura E11 (para localizar o trecho do `./gradlew --stop`), não o código. Os números de linha de código citados são da base `3a9542c` e podem ter mudado.
- As decisões R1, R2, a aceitação de risco do mock e a correção da ARCHITECTURE §14 foram tomadas sem confirmação do usuário; a revisão humana da E12 está pendente.
- O hash do merge na `main` não estava disponível; o worktree e o relatório em `.superpowers/sdd/` podem desaparecer após o merge, e não foram copiados como anexo (o conteúdo está acima).
- Dados sensíveis omitidos de propósito: CPFs de teste, credenciais e valores do `gate.env`.
- A nota `ZenyHotelManager - Módulo printing` ainda não existe no vault (proposta pelas capturas E10 e E11).

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Estado por marco]]
- [[ZenyHotelManager - Hospedagem e recepção]]
- [[ZenyHotelManager - Módulo fnrh]]
- [[ZenyHotelManager - Schemas, migrações e views de relatório]]
- [[ZenyHotelManager - Docker, observabilidade e CI]]
- [[ZenyHotelManager - Ambiente, banco, chaves e build]]
- [[ZenyHotelManager - Testes de integração]]
- [[ZenyHotelManager - Módulo notifications]]
- [[ZenyHotelManager - Módulo guests]]
- [[ZenyHotelManager - Módulo billing (contas, roteamento e taxa de serviço)]]
- [[ZenyHotelManager - Módulo billing (caixa, pagamentos, caução e encerramento)]]
- [[ZenyHotelManager - Módulo reservations (inventário, disponibilidade e reservas)]]
- [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E11 - d1100f5a]]
- [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 - 4dd12e66]]
- [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]]
