---
type: knowledge
status: processed
created: 2026-11-09
projects:
  - "[[ZenyHotelManager]]"
sources:
  - "[[2026-11-05 - ZenyHotelManager - atualização m5-recepcao-fnrh E07 - 9f02405c]]"
  - "[[2026-11-06 - ZenyHotelManager - atualização revisão de arquitetura dos roadmaps - c889f886]]"
  - "[[2026-11-10 - ZenyHotelManager - atualização m5-recepcao-fnrh E15 - a22890e7]]"
  - "[[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]]"
  - "[[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 (revisão humana) - 65d0d4ff]]"
  - "[[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E16 - 6095f729]]"
  - "[[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E14 - 998156dc]]"
  - "[[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E15 - c139da21]]"
---
# ZenyHotelManager - Módulo fnrh

Referência técnica do projeto [[ZenyHotelManager]]. Integração com a FNRH Digital (Serpro/MTur), API v2.4. Estado: E07, E15, E08 e E16 do M5 concluídas (configuração, domínios, porta e adaptador, validação local, descrição de gênero, envio assíncrono e a limpeza da credencial); E14 do M6 concluída (no-show na FNRH, 2026-11-14); E15 do M6 concluída (rótulos da FNRH na ficha, 2026-11-14); E16 do M6 concluída (dívidas de teste, 2026-11-14); a homologação real segue sendo a E09, `#bloqueada` só pela Q-12.

Texto das capturas de atualização publicadas no repositório, integrado sem resumo. Referências como "SPEC", "ARCHITECTURE §x", "RF-…", "RN-…", "Hn", "Q-NN", "D-E07-n" e "Rn" apontam para `docs/SPEC.md`, `docs/ARCHITECTURE.md`, `docs/roadmaps/` e `docs/superpowers/` do repositório. O levantamento da API está em `docs/fnrh/api-fnrh-v2.4.md`. As regras que a FNRH provou para toda integração estão em [[ZenyHotelManager - Eventos e jobs]]; as decisões do lote E07 e o que falta confirmar, em [[ZenyHotelManager - Estado por marco]].

**O comportamento real do Serpro só a E09 confirma.** Os stubs WireMock e o adaptador vêm da documentação v2.4 (PDF oficial); nenhuma chamada real foi feita e a E09 está bloqueada pela credencial (Q-12).

---

## Camada e dependências

- Camada "Integração governamental" (acima da Hospedagem). Pacote `com.zeny.hotel.fnrh`, com `FnrhModule.kt` na raiz.
- `allowedDependencies` (`FnrhModule.kt`): `shared`, `guests`, `reservations`, `notifications` e **`frontdesk`** (M6 E15; D-E15-4); `reservations` e `notifications` desde a E08 (D-E08-14). O `fnrh` **não** depende do `hotel` e não usa a `HotelApi.profile()` (o payload da FNRH não pede dado do hotel, D-E07-12); o consumidor de `HotelApi.profile()` é o `printing` (E11, `PrintingApiService.kt:72`). O `ModularityTest` confere a lista exata (`ModularityTest.kt:331`). A tabela da ARCHITECTURE §3.1 ainda lista `hotel` para o `fnrh`; o código é subconjunto dela (auditoria G5 da M5 E12). O handoff da M6 E14 aponta de novo a divergência ao `arquiteto`, e o da M6 E15 também (previsão ou divergência); não corrigida.
- A aresta `fnrh` → `frontdesk` existe **só pela porta `RegistrationCardLabels`** (M6 E15, prevista na sincronização do M6 em 2026-11-12; substitui "Nunca importa `iam`, `frontdesk` nem lê tabela de outro schema. `frontdesk` não pode chamar `fnrh` (camada acima)" e a "aresta prevista, ainda não no código"). Nunca importa `iam` nem lê tabela de outro schema. O `frontdesk` continua **sem** depender do `fnrh` (camada acima, ARCHITECTURE §3.1 e §3.2): a inversão é por porta definida no módulo de baixo, no mesmo padrão da `FolioOwnerDescriber` (`billing`, implementada pelo `reservations`). Para os eventos da hospedagem, o `fnrh` reage a eventos de `reservations`. O `ModularityTest` do `fnrh` exige exatamente esses cinco módulos (dependências diretas e `allowedDependencies`) e há um teste novo, `fnrh uses only the registration card labels port from frontdesk`, que compara o conjunto dos `targetType` das dependências diretas do `fnrh` dentro de `com.zeny.hotel.frontdesk.` com exatamente `{com.zeny.hotel.frontdesk.RegistrationCardLabels}` (prova o "só" e o "usa"); o teste do `frontdesk` segue sem `fnrh`. Descartada a named interface do Spring Modulith (`@NamedInterface`): o repositório não a usa e ela mudaria o modelo de API pública do `frontdesk` por uma aresta. No fechamento da E15, o comentário do `ModularityTest` do `fnrh` ainda dizia "Nunca iam, frontdesk…" logo acima de "M6 E15: frontdesk, só pela porta" (deixado para a M6 E16).

*Nota do curador (conferência por `git` em 2026-11-15, só leitura):* no `99d9e99` (fechamento da E15), o `FnrhModule.kt` declara `allowedDependencies = ["shared", "guests", "reservations", "notifications", "frontdesk"]`, com o KDoc "Do `frontdesk`, só a porta dos rótulos da ficha (`RegistrationCardLabels`, M6 E15)"; `frontdesk/RegistrationCardLabels.kt` tem a `interface RegistrationCardLabels` com `travelReason` e `transportMode`; `fnrh/application/FnrhRegistrationCardLabels.kt` é `@Component`; o `ModularityTest` tem `fnrh depends only on shared, guests, reservations, notifications and frontdesk` e `fnrh uses only the registration card labels port from frontdesk`. No merge `b42ce6f` (E14, E15 e E16), o comentário já diz "Nunca iam nem tabela de outro schema; do `frontdesk`, só a porta dos rótulos (M6 E15)", e a linha da ARCHITECTURE §3.1 do `fnrh` é "shared, hotel, reservations, guests, notifications, `frontdesk` (só a porta `RegistrationCardLabels`, M6 E15)" (o `hotel` segue na tabela). O corpo da implementação e os testes não foram conferidos.

## Pacotes

- Raiz (API pública): `FnrhModule`, `FnrhPermissions`, `FnrhErrorCodes`, `FnrhFieldCodes` e `FnrhEnvironment` (`HOMOLOGATION`, `PRODUCTION`; fica na raiz porque a web o expõe).
- `domain`: modelo de dados da FNRH, regras de configuração (`FnrhSettings`), escolha do CPF solicitante (`RequesterCpfPolicy`), mapeador do hóspede (`FnrhPersonMapper`), validador local (`FnrhLocalValidator`), `FnrhFieldError`, `FnrhDomainCatalog` e `IbgeMunicipalities`. Sem Spring.
- `application`: casos de uso e portas (`FnrhGateway`, `FnrhConnectionSource`, `FnrhIntegrationLog`, `FnrhRequesterDirectory`), `FnrhSettingsService`, `FnrhRequestersService`, `FnrhDomainsService`, `FnrhDomainValuesWriter`, `FnrhStatusService`.
- `infrastructure`: adaptador `SerproFnrhGateway` (`RestClient` com `JdkClientHttpRequestFactory` e timeouts), `FnrhMessageSanitizer`, persistência, `JdbcFnrhIntegrationLog` (transação própria, `REQUIRES_NEW`, no modelo do `PushDeliveryLog` do `notifications`), `FnrhMetrics` (`MeterBinder`) e `FnrhProperties`.
- `web`: só controllers e DTOs. `@Tag("FNRH")`.
- Classes novas da E08:
  - `domain`: `FnrhSubmission` (entidade com `FnrhOperation`, `FnrhSubmissionStatus` e `FnrhSubmissionFailure`) e `FnrhRetryPolicy`.
  - `application`: `FnrhSubmissionListeners`, `FnrhSubmissionSender` (núcleo do envio, que recusa rodar dentro de transação), `FnrhCheckInStep`, `FnrhCheckOutSteps`, `FnrhSubmissionRecorder` (grava o resultado com `@Audited @Transactional`, num bean à parte), `FnrhSubmissionsService` (fila, retry e dismiss) e as portas `FnrhSubmissionStore` e `FnrhRemoteIds`.
  - `infrastructure`: `FnrhSubmissionJob`, `FnrhSubmissionPersistence`, `FnrhSubmissionConfiguration`, `FnrhSubmissionMetrics` e `SerproFnrhLookups` (as consultas de conciliação).
  - `web`: `FnrhSubmissionsController`.
- Além das classes listadas (auditoria G5 da M5 E12): em `application`, `FnrhSubmissionFailures`, `FnrhAudit` (códigos de trilha: `fnrh.submission.send`, `.retry`, `.dismiss`, `fnrh.settings.clear-credentials`) e `FnrhMasks`; em `infrastructure`, `SerproFnrhSupport` e `SerproFnrhWire`. As extensões de teste `FnrhSubmissionDismissCompat.kt` existem em **dois** lugares (`src/test/kotlin/com/zeny/hotel/fnrh/` e `.../fnrh/domain/`), não em um; a limpeza prometida deve apagar as duas. *Pagas na M6 E16: as duas cópias saíram (ver "Envio assíncrono").*
- Classe nova da M6 E15, em `application`: `FnrhRegistrationCardLabels` (`@Component`, `com.zeny.hotel.fnrh.application`), que implementa a porta `RegistrationCardLabels` do `frontdesk` (rótulos da ficha de registro, ver [[ZenyHotelManager - Hospedagem e recepção]]) lendo `FnrhDomainCatalog.values(FnrhDomain.TRAVEL_REASONS | FnrhDomain.TRANSPORT_MODES)` e buscando o código **exato** (maiúsculas e espaços contam, como em `contains`): `automovel` e `AUTOMOVEL ` não casam com `AUTOMOVEL` e saem crus na ficha. Só leitura: **sem Serpro, sem chamada de rede e sem trilha**. Um `refresh` dos domínios (rótulo novo ou código removido) vale na ficha seguinte. A implementação é a única do contexto (teste: `getBeansOfType(RegistrationCardLabels)` tem uma entrada, do tipo `FnrhRegistrationCardLabels`).
- **Toda chamada ao Serpro roda fora de transação do banco.**

## Configuração cifrada, por ambiente (D-E07-1)

- O administrador escolhe o **ambiente** (`HOMOLOGATION` ou `PRODUCTION`); as URLs ficam em propriedade: `zeny.fnrh.homologation-url` (padrão `https://hom-lowcode.serpro.gov.br/FNRH_API/rest/v2`) e `zeny.fnrh.production-url` (padrão `https://fnrh.turismo.serpro.gov.br/FNRH_API/rest/v2`), mais `zeny.fnrh.connect-timeout` (5 s) e `zeny.fnrh.read-timeout` (20 s). Os testes apontam as duas URLs para o WireMock.
- **Trocar de ambiente exige informar a senha de novo** (`422 FNRH_PASSWORD_REQUIRED_FOR_ENVIRONMENT_CHANGE`), para a credencial de um ambiente não ir para o outro. Descartadas: URL livre na configuração (a credencial poderia ir para qualquer host) e propriedade única (cada troca pediria nova implantação).
- Usuário, senha e CPF padrão ficam cifrados (`FieldCipher`/`EncryptedStringConverter`). A tabela `fnrh.settings` tem uma linha semente (versão 0, desligada, homologação) para o primeiro `PUT` ter `ETag`.
- Regras do domínio: `password` nula mantém a atual; ligar (`enabled = true`) sem usuário, senha ou CPF padrão dá `422 FNRH_SETTINGS_INCOMPLETE`. Sem configuração (ou desligada), `FnrhConnectionSource.current()` devolve `null` e nada é enviado.
- A senha nunca volta na API; o CPF sai mascarado (`***.***.***-NN`). A trilha do `PUT` não guarda senha, CPF nem o `username` (ver [[ZenyHotelManager - Segurança, autenticação e autorização]]).
- **ARCHITECTURE §12, item "Credencial"** (decisão do usuário, 2026-11-12, E12 (f); aplicada pelo `arquiteto` em `0e58cf9`): a credencial da integração (usuário e senha) fica cifrada em repouso (os dois campos de `FnrhSettings` usam `EncryptedStringConverter`), nunca na trilha nem nos logs (nem o usuário) e é removível pela ação com trilha (`POST …/clear-credentials`, padrão inalterado). **Na API, o segredo é a senha:** nunca é devolvida, e a resposta só traz `passwordSet`. O `username` volta em `GET` e `PUT /api/v1/fnrh/settings` (`FnrhSettingsResponse.username`), que só o Administrador lê (`fnrh.settings.manage`). Contrato e código não mudaram; a divergência registrada desde a E07/E16 está encerrada. Alternativa descartada: mascarar ou tirar o usuário da resposta, o que mudaria o contrato sem proteger segredo.
- **Limpar a credencial (M5 E16):** `POST /api/v1/fnrh/settings/clear-credentials`, sem corpo, com `If-Match` obrigatório (`428` sem ele, `412` com versão velha) e `fnrh.settings.manage`, sem `Idempotency-Key`. Apaga usuário, senha e CPF padrão (as três colunas ficam `NULL`) e desliga a integração; responde `200` com a configuração e o `ETag` novo. **Mantém** o ambiente, o CPF por usuário (`fnrh.requester`, que tem `deactivate` próprio), os ids remotos, o link de pré-check-in cifrado e o `fnrh.integration_call`, que não são credencial. Repetir sobre a configuração já vazia é `200`, mantém o `ETag` e **não grava entrada na trilha** (o `AuditScopes` descarta retrato igual, como no `PUT` sem mudança). Trilha `fnrh.settings.clear-credentials` com o retrato `FnrhSettingsAuditState` (sem usuário, senha nem CPF em claro) e o autor em `audit.audit_entry.user_id`. Religar sem nova credencial dá `422 FNRH_SETTINGS_INCOMPLETE`; a recuperação é informar a credencial de novo. Caso de uso `FnrhSettingsService.clearCredentials(expectedVersion)` sobre `FnrhSettings.clearCredentials()`.
- **Depois da limpeza, nada sai ao Serpro:** a conexão é relida a cada chamada, e o envio para (`NOT_CONFIGURED` → `STOP`, sem gravar resultado nem gastar tentativa); as submissões ficam `PENDING` (D-E08-5). A limpeza no meio de uma rodada para antes da chamada seguinte, inclusive entre duas chamadas do mesmo `CHECK_IN`; a marca de escrita em curso leva à conciliação quando a integração volta, sem pessoa nem hóspede duplicado (testado).

## CPF solicitante por usuário (H5, D-E07-7, decisão (h))

- Cadastro `fnrh.requester`: id do usuário (opaco; não se confere se existe) → CPF cifrado, mostrado mascarado. `RequesterCpfPolicy.choose(performedBy, cpfOfUser, defaultCpf)` escolhe o CPF do usuário que fez a operação e, sem ele (ou com `performedBy` nulo), o padrão; sem nenhum dos dois, `null`. A porta `FnrhRequesterDirectory.cpfOf(userId)` é para a E08.
- **Sem `DELETE`:** o plano pedia `DELETE /requesters/{userId}`, mas a convenção do projeto é "a API não apaga nada" e o build pegou o erro. Em lugar dele, `POST /api/v1/fnrh/requesters/{userId}/deactivate`, que apaga o CPF e mantém a linha.
- A troca do CPF de um usuário por outro com o mesmo final deixa rastro na trilha: o `FnrhRequester` tem `@Version` e a versão entra no retrato (achado I1 da revisão final).

## Porta `FnrhGateway` e operações (D-E07-2)

A porta é a do que a API v2.4 faz, não a lista da SPEC §8.2.17 (`registerStay/checkIn/checkOut/noShow/cancel`); a revisão de 2026-11-06 passa a SPEC §8.2.17 a descrever a porta real da E07. Nomes do nosso lado em inglês; o adaptador mapeia para os do Serpro. Toda operação recebe um `correlationRef` opaco (id da reserva ou da submissão), nunca dado pessoal.

| Operação da porta | Chamada ao Serpro |
|---|---|
| `registerReservation` | `POST /reservas` (sem dado pessoal; devolve o id remoto e o link de pré-check-in) |
| `updateReservation` | `PUT /reservas/{id}` |
| `cancelReservation` | `POST /reservas/{id}/cancelar` (só vale com a reserva em `CRIADA`) |
| `findReservationByCode` | `GET /reservas?page_number=1&codigo_reserva=…` (para conciliar um `UNKNOWN_OUTCOME`; **só a página 1 é lida**) |
| `registerPerson` | `POST /pessoas` (**única** operação da porta que leva `cpf_solicitante`) |
| `addGuestToReservation` | `POST /reservas/{id}/hospedes` com `situacao_hospede_id = CHECKIN_REALIZADO`, `checkin_em`, motivo de viagem, meio de transporte e `responsavel_id` |
| `checkOut` | `PATCH /hospedes/{id}/checkout`, corpo `text/plain` com o instante, sem aspas |
| `fetchDomain` | `GET /dominios/fnrh/<domínio>` |
| `listReservationGuests` | `GET /reservas/{id}/hospedes` (lê só `dados[].hospede.hospede_id` e `.pessoa_id`; a resposta traz dado pessoal) |
| `findPersonByDocument` | `GET /pessoas/documento/{tipo}/{numero}` (com `cpf_solicitante`; lê só `dados.id`; o documento vai no caminho e a URL nunca entra no log) |
| `markNoShow` | `POST /reservas/{reserva_id}/noshow`, sem corpo (no-show **em lote, da reserva**; D-E14-1). Só leva o id remoto da reserva, que já guardamos. O corpo da resposta não é lido: qualquer `2xx` é sucesso. Falhas seguem a classificação da E07 (timeout de leitura num `POST` é `UNKNOWN_OUTCOME`). Sem `cpf_solicitante`. Operação `markNoShow` no `fnrh.integration_call` |

- **Fluxo decidido (D-E07-2, decisão (a)):** a reserva é registrada **na criação**, sem dado pessoal. No check-in entram a pessoa e o hóspede (`CHECKIN_REALIZADO`); o check-out sai por `PATCH`; o cancelamento só vale em `CRIADA`. Descartada a alternativa "registro só no check-in" (`POST /hospedagem/registrar`): o cancelamento nunca chegaria ao Serpro e o link de pré-check-in não serviria.
- Fora da porta: `hospedagem/registrar`, pré-check-in de balcão, fichas, operações em lote (salvo o no-show da reserva, `markNoShow`, desde a M6 E14), `DELETE /reservas`, `PATCH …/checkin` (o hóspede já entra com check-in) e o no-show **individual** (`PATCH /hospedes/{id}/no-show` ou `/noshow`), porque o caminho individual diverge no PDF. O no-show entrou na M6 E14 (ver 'No-show' abaixo); o gate M8 E13 pede o no-show executado na homologação ou registrado como risco aceito pelo usuário.
- Campos da reserva (`FnrhReservationData`): `numero_reserva` = `Reservation.code` (nunca o código do `Booking`); `numero_reserva_ota` = `Booking.externalId`; com OTA, `origem_reserva_id = OTA`, senão `MEIOHOSPEDAGEM`; `minors` sai da **data de nascimento** (menor de 18 anos na entrada), não de `childAges`.
- Instantes enviados ao Serpro: UTC com milissegundos e `Z` (`2026-02-10T15:00:00.000Z`), tanto no JSON quanto no `text/plain`.
- **`cpf_solicitante` só onde a API exige (D-E07-9, decisão (b)):** `POST /pessoas`, `GET /pessoas/documento/…` e `POST /hospedagem/registrar`; nesta porta, `registerPerson` e `findPersonByDocument`. O roadmap supunha o header em toda chamada; a fonte oficial prevalece. Consequência: o `performedBy` só pesa no registro da pessoa, no check-in. A ARCHITECTURE §12 foi corrigida nesse ponto no fechamento.
- O adaptador usa `Basic Auth` com o usuário e a senha da conexão de cada chamada.

## Classificação de falhas (`FnrhFailure`, com `temporary`)

| O que acontece | Falha | Temporária |
|---|---|---|
| `400`, `409`, `415`, `422` ou outro `4xx` | `VALIDATION` | não |
| `401` | `UNAUTHORIZED` | não |
| `403` | `FORBIDDEN` | não |
| `404` | `NOT_FOUND` | não |
| `429`, `3xx` ou `5xx` | `SERVER_ERROR` | sim |
| conexão recusada ou timeout de conexão (nada foi enviado) | `UNAVAILABLE` | sim |
| timeout de leitura em `GET` | `UNAVAILABLE` | sim |
| timeout de leitura em `POST`, `PUT` ou `PATCH` | `UNKNOWN_OUTCOME` | sim |
| integração sem configuração | `NOT_CONFIGURED` (sem chamada) | não |

- **`UNKNOWN_OUTCOME` × `UNAVAILABLE`:** um timeout de leitura numa escrita não diz se o Serpro gravou; é `UNKNOWN_OUTCOME` e exige conciliar antes de repetir. `UNAVAILABLE` é "nada foi enviado". `findReservationByCode` **falha fechado**: com ambiguidade devolve `UNKNOWN_OUTCOME` (achado I2 da revisão final; antes falhava aberto).
- `FnrhGatewayException(failure, httpStatus, sanitizedMessage)` **sem causa encadeada** (a mensagem do `RestClient` pode trazer o corpo). Nenhum tipo do Serpro sai da porta.

## Saneador (`FnrhMessageSanitizer`)

- A mensagem do Serpro vem de `mensagem` no corpo JSON; o corpo bruto nunca é usado. O saneador troca por `***` os valores que o adaptador acabou de enviar (de 3 caracteres ou mais) e cada palavra deles com 3 ou mais letras (ignora maiúsculas e acentos, porque o Serpro pode ecoar só "MARIA"), as sequências de 5 ou mais dígitos e os e-mails, e corta em 200 caracteres.
- Depois da revisão final: **todo caractere de controle Unicode (`Cc`) e os de formatação** são tratados no saneador e nos rótulos, inclusive U+2028 e U+2029. O saneador mascara os valores enviados e os padrões.
- A mensagem saneada vai **só** para o log e para a exceção.
- Desde o commit `8d6203a` (M5 E15), o controle Unicode é normalizado também nos valores enviados (antes, um valor com controle não casava com o eco devolvido).
- Risco aceito D-E15-6: valor de 1 ou 2 caracteres ecoado não é mascarado (`MIN_VALUE_LENGTH = 3`).

## `fnrh.integration_call` (D-E07-8, decisão (g))

- Tabela *append-only* (`REVOKE UPDATE, DELETE`, trigger, bean `AppendOnlyTables`), **sem coluna de texto livre**: `operation`, `environment`, `outcome`, `http_status`, `duration_ms`, `correlation_ref`, `remote_id`, `occurred_at`; índice `(environment, outcome, occurred_at)`; CHECK no `remote_id` (revisão final). A mensagem do Serpro nunca vai para ela: pode trazer o nome do hóspede e a tabela não admite expurgo.
- Gravada em transação própria: a linha fica mesmo quando o chamador faz rollback. Uma linha por chamada HTTP; log `INFO` no sucesso e `WARN` na falha; a URL nunca entra.

## Status e métricas

- `GET /api/v1/fnrh/status` (`fnrh.submissions.read`): `{configured, enabled, environment, lastSuccessAt, lastFailureAt, lastFailureOutcome}`, com os instantes do **ambiente atual**; `lastFailureOutcome` é `x-extensible-enum`.
- Até a M5 E16, o status respondia `500` em qualquer ambiente sem chamada bem-sucedida registrada (instalação nova ou a primeira troca para `PRODUCTION`), e a métrica `zeny_fnrh_last_success_seconds` passava pelo mesmo caminho: `JdbcFnrhCallHistory.lastSuccessAt` fazia `.single()` sobre um `max()` nulo. Corrigido em `6f4e60b` (consulta com a forma da do `lastFailure`, `ORDER BY … LIMIT 1`); teste de regressão `FnrhCallHistoryEmptyTest`.
- Métricas por `MeterBinder`, que aparecem em `/actuator/prometheus`: `zeny_fnrh_calls_total` (tags `operation`, `outcome`, `environment`), `zeny_fnrh_last_success_seconds`, `zeny_fnrh_last_failure_seconds` (`NaN` sem registro) e `zeny_fnrh_configured` (0 ou 1). **Nenhum `HealthIndicator`**: a readiness não depende da FNRH (`ActuatorExposureTest` intacto, H22). Desde a E08, o gauge `zeny_fnrh_submissions{status}` (`pending`, `failed`, `invalid`), lido da fila a cada raspagem (`NaN` se a leitura falhar).

## Domínios semeados e refresh tudo-ou-nada (D-E07-5)

- Tabela `fnrh.domain_value (domain, code, label, refreshed_at)`, chave `(domain, code)`. A migração **semeia** todos os `id` e `label` do levantamento da v2.4, então o cache nunca começa vazio (descartado o cache vazio até o primeiro `refresh`, que deixaria toda submissão inválida).
- Dez domínios: `transport-modes`, `travel-reasons`, `guest-statuses`, `genders`, `disability-options`, `races`, `disability-types`, `document-types`, `booking-statuses`, `record-statuses` (kebab-case na URL; nome desconhecido dá `404 FNRH_DOMAIN_NOT_FOUND`).
- `POST /api/v1/fnrh/domains/refresh`: o `FnrhDomainsService`, sem transação, confere a permissão e busca os 10 domínios **fora de transação**; depois chama **outro bean**, `FnrhDomainValuesWriter`, cujo método `@Audited @Transactional` só grava a substituição (num bean separado porque a autoinvocação pularia o proxy, e com ele a transação e a trilha; foi o Importante aberto na rodada 1 da revisão de arquitetura). **Se qualquer busca falhar, nada muda.** Resposta com a contagem por domínio. Mapeamento de erros: `NOT_CONFIGURED` → `422 FNRH_NOT_CONFIGURED`; `UNAUTHORIZED`/`FORBIDDEN` → `422 FNRH_CREDENTIALS_REJECTED`; temporárias → `503 FNRH_UNAVAILABLE`; `VALIDATION`/`NOT_FOUND` → `502 FNRH_REJECTED`.
- A web nunca devolve o tipo de domínio; a application o mapeia.

## Validador local e lista do IBGE (RF-FNRH-06, H21, D-E07-3, D-E07-10, D-E07-11)

- Fica em `domain`, sem Spring, junto com o mapeador e a lista do IBGE; montados pela E08 no `FnrhCheckInStep`.
- `FnrhLocalValidator.validate(person, guest, arrival, responsibleKnown)` devolve `FnrhFieldError(field, code)`, **nunca o valor**. Códigos: `REQUIRED`, `INVALID_VALUE`, `NOT_IN_DOMAIN`, `INCONSISTENT`. Regras: nome e documento obrigatórios (CPF passa pelo `Cpf`); nacionalidade e residência ISO 3166-1 alpha-2 (`Locale.getISOCountries()`, D-E07-4); nascimento, gênero e raça obrigatórios; gênero, raça, opção e tipo de deficiência, motivo de viagem e meio de transporte no catálogo; `OUTRO` exige descrição; deficiência `SIM` exige tipo; com residência `BR`, município obrigatório e na lista do IBGE, UF obrigatória e igual à do município (`INCONSISTENT`), CEP de 8 dígitos quando informado (e então logradouro, número e bairro); residência fora do `BR` não exige município nem UF; menor de 18 anos na data de entrada sem responsável gera `guest.responsibleGuestId`/`REQUIRED`.
- Mapeador: documento = CPF se houver, senão passaporte (os outros tipos, como RG, não entram); gênero e raça mapeados aos códigos da API; raça ou gênero **nulos** significam "não coletado" e a validação acusa `REQUIRED` (D-E07-10); só `NOT_DECLARED`/`NOT_INFORMED` viram `NAOINFORMAR`/`NAOINFORMADO`. O `FnrhGuestData` tem `genderDescription` e o `FnrhPersonMapper` a envia como `GeneroDescricao` somente com `OUTRO` (M5 E15; [[ZenyHotelManager - Módulo guests]]).
- **Lista do IBGE (decisão (d)):** recurso versionado `src/main/resources/fnrh/ibge-municipios.csv` (5.571 municípios; `codigo;uf`), com o cabeçalho trazendo a fonte (`https://servicodados.ibge.gov.br/api/v1/localidades/municipios`), a data do download e o SHA-256 do JSON. **Risco aceito: um município criado depois do download é recusado até o recurso ser atualizado.** A API da FNRH não tem endpoint de municípios. Descartada a validação só de formato.
- A E08 manteve a residência nula aceita e não valida o `checkedOutAt` (D-E08-10; ver 'Envio assíncrono').

## Endpoints e permissões

| Endpoint | Permissão |
|---|---|
| `GET /api/v1/fnrh/settings`, `PUT /api/v1/fnrh/settings` (`If-Match` obrigatório; `428` sem ele, `412` com ETag velho) | `fnrh.settings.manage` |
| `POST /api/v1/fnrh/settings/clear-credentials` (`If-Match` obrigatório) | `fnrh.settings.manage` |
| `GET /api/v1/fnrh/requesters`, `PUT /api/v1/fnrh/requesters/{userId}`, `POST /api/v1/fnrh/requesters/{userId}/deactivate` (o CPF nunca vai na URL) | `fnrh.settings.manage` |
| `POST /api/v1/fnrh/domains/refresh` | `fnrh.settings.manage` |
| `GET /api/v1/fnrh/domains/{domain}` | `fnrh.domains.read` |
| `GET /api/v1/fnrh/status` | `fnrh.submissions.read` |
| `GET /api/v1/fnrh/submissions?status=…` (cursor pelo `sequence`; sem dado de hóspede além de ids, código da reserva e erros sem valor) | `fnrh.submissions.read` |
| `POST /api/v1/fnrh/submissions/{id}/retry` (só `FAILED`/`INVALID`; zera as tentativas e os erros e preserva a escrita em curso; sem `@Idempotent`, e repetir dá `409`) | `fnrh.submissions.manage` |
| `POST /api/v1/fnrh/submissions/{id}/dismiss` (só `FAILED`/`INVALID`; leva a `DISMISSED`, terminal, que não segura a fila) | `fnrh.submissions.manage` |

- Nenhuma permissão é sensível. `fnrh.submissions.manage` (E08, não sensível, só o Gerente): retry, dismiss e destinatário do alerta de falha. Códigos de problema em `FnrhErrorCodes`: `FNRH_SETTINGS_INCOMPLETE`, `FNRH_PASSWORD_REQUIRED_FOR_ENVIRONMENT_CHANGE`, `FNRH_REQUESTER_NOT_FOUND`, `FNRH_DOMAIN_NOT_FOUND`, `FNRH_NOT_CONFIGURED`, `FNRH_CREDENTIALS_REJECTED`, `FNRH_UNAVAILABLE`, `FNRH_REJECTED`, `FNRH_SUBMISSION_NOT_FOUND`, `FNRH_SUBMISSION_NOT_RETRYABLE` e `FNRH_SUBMISSION_NOT_DISMISSABLE`.
- Migrações: `V2026_11_04_1000` a `V2026_11_04_1030` na pasta `fnrh/` (settings com GRANT, requesters, integration_call, domain_value). **Foram alteradas no lugar durante a etapa porque nunca saíram da branch:** um banco local de desenvolvimento que tenha aplicado uma versão anterior precisa ser recriado (`docker compose -f docker/compose.yaml down -v`). A próxima migração do projeto precisa de timestamp posterior a elas. A E08 acrescentou `V2026_11_10_1000__create_fnrh_submissions.sql` e `V2026_11_10_1100__create_fnrh_report_views.sql`; a M6 E14, `V2026_11_14_1000__add_fnrh_no_show.sql` (ver [[ZenyHotelManager - Schemas, migrações e views de relatório]]). A última migração do projeto está em [[ZenyHotelManager - Estado por marco]].

## Dados que nunca saem

- Senha, número de documento, raça/cor, deficiência, nome, e-mail e telefone não entram em log, trilha, resposta, métrica nem no registro de integração. Todo tipo que os carrega sobrescreve o `toString` (`FnrhPersonData`, `FnrhGuest`, `FnrhDocument`, `FnrhConnection`, `FnrhProperties`). **`Cpf.toString()` devolve os dígitos:** nunca interpole `Cpf` em log, mensagem nem `toString`.
- O texto do alerta, a trilha da submissão, a view e os erros de validação não levam nome, documento, raça/cor nem deficiência; os nomes dos campos sensíveis também saíram dos erros (I-3). `FnrhRemoteReservation.toString()` omite o link de pré-check-in. As respostas das consultas do Serpro trazem dado pessoal, mas o adaptador lê só os ids.

## Envio assíncrono (M5 E08)

**Padrão aprovado pelo usuário (revisão humana da E08, 2026-11-11, registrada no roadmap da branch `roadmap/m5-recepcao-fnrh`, commit `2185e41`):** uma submissão por evento, ordem causal por reserva, escrita em curso e conciliação antes de repetir, 8 tentativas, e `FAILED`/`INVALID` segurando a fila até `retry` ou `dismiss`. É **a referência para os envios assíncronos de M7 e M8**. As decisões (a) a (n) do lote E08 seguem revisáveis uma a uma ([[ZenyHotelManager - Estado por marco]]).

**Submissão por evento (D-E08-1 e 2).** Cada evento grava **uma** `FnrhSubmission`, idempotente pela chave única `(reservation_id, operation, event_key)`, em que `event_key` é o tipo do evento com a `version` dele (`created` no `ReservationCreated`). Mapeamento:

| Evento | Operação |
|---|---|
| `ReservationCreated` | `REGISTER_RESERVATION` |
| `ReservationChanged`, `ReservationConfirmed`, `ReservationReactivated` | `UPDATE_RESERVATION` (`PUT` com os dados atuais, idempotente) |
| `ReservationCancelled` | `CANCEL_RESERVATION` |
| `GuestCheckedIn` | `CHECK_IN` (todos os hóspedes da reserva; progresso por hóspede em `fnrh.remote_guest`) |
| `GuestCheckInUndone` | `UNDO_CHECK_IN` |
| `GuestCheckedOut` | `CHECK_OUT` |
| `ReservationMarkedNoShow` (M6 E14) | `NO_SHOW` |

A pré-reserva (`PROVISIONAL`) e a reserva sem documentos também são registradas, porque o registro não leva dado pessoal. A expiração vira cancelamento no MTur. `RoomMoved` não gera envio, porque a API v2.4 não tem UH. O no-show entrou na M6 E14 (ver 'No-show' abaixo); o gate M8 E13 pede o no-show executado na homologação ou registrado como risco aceito pelo usuário.

**Ordem causal (D-E08-3).** Cada submissão guarda `causal_version` (a `version` da reserva no evento; `0` no `ReservationCreated`) e o posto da operação: `REGISTER_RESERVATION` 0 < `UPDATE_RESERVATION` 1 < `CANCEL_RESERVATION` 2 < `CHECK_IN` 3 < `UNDO_CHECK_IN` 4 < `CHECK_OUT` 5 < `NO_SHOW` 6 (o `NO_SHOW` desde a M6 E14). Só anda a cabeça da reserva: a de menor `(causal_version, posto, sequence)` entre as `PENDING`, `FAILED` e `INVALID`, e só se estiver `PENDING` e vencida. `FAILED` e `INVALID` seguram as seguintes até o `retry` ou o `dismiss`. O `sequence` (identidade) é só o cursor da API. Os passos agem sobre o **estado atual** da reserva e dos ids remotos, não sobre a ordem de chegada dos eventos (D-E08-9):

- registro de reserva já cancelada (ou no-show) sem id remoto, e cancelamento sem id remoto: `SENT` sem chamada;
- `UPDATE_RESERVATION` sem id remoto: registra, sem o `PUT`;
- `UPDATE_RESERVATION` com a reserva remota cancelada por nós: `FAILED` com `REMOTE_CANCELLED` e alerta, sem chamada (o `numero_reserva` é único e a API não reativa);
- `CHECK_OUT` de reserva com hóspedes com check-in feito e nenhum deles no Serpro roda antes o check-in deles e nunca fica `SENT` vazio.

**Situações:** `PENDING`, `SENT`, `FAILED`, `INVALID`, `CANCELLED` e `DISMISSED`. `status`, `operation` e `lastFailure` são `x-extensible-enum` nas respostas.

**Retry (D-E08-4).** Falha temporária (`SERVER_ERROR`, `UNAVAILABLE`, `UNKNOWN_OUTCOME` e `INTERNAL_ERROR`) reagenda com espera `1 min × 2^(n−1)` até `1 h` (n = tentativas feitas). Na **8ª** tentativa com falha, a submissão vira `FAILED`; são cerca de 2 h no total. Falha permanente (`VALIDATION`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`) vira `FAILED` na hora. Propriedades `zeny.fnrh.submissions.*`: `interval` (`PT1M`), `initial-delay` (`PT1M`), `batch-size` (50), `max-attempts` (8), `initial-backoff` (`PT1M`), `max-backoff` (`PT1H`). Exceção que não é `FnrhGatewayException` conta como `INTERNAL_ERROR` temporária, com log só de ids. Uma submissão envenenada não para o lote (D-E08-17).

**Sem configuração (D-E08-5).** Com `FnrhConnectionSource.current()` nulo, nada sai e **nenhuma tentativa é gasta**: as submissões ficam `PENDING`. Ao ligar, todo o acumulado sai no ambiente escolhido, inclusive estadias antigas. O corte ou a limpeza fica para decidir na E09 ou na M8 E13.

**Escrita em curso (D-E08-15).** Antes de cada chamada que cria recurso (`POST /reservas`, `POST /pessoas`, `POST /reservas/{id}/hospedes`), a submissão grava `in_flight = true` em transação própria (`FnrhSubmissionStore.markInFlight`, `REQUIRES_NEW`). O id remoto gravado depois (`FnrhRemoteIds.save*`, também `REQUIRES_NEW`) limpa a marca na mesma transação. A marca vale para a reserva inteira: `anyInFlight(reservationId)` olha todas as submissões dela, inclusive `DISMISSED` e `CANCELLED`. Outra falha e o `retry` preservam a marca. A tentativa que encontra a marca concilia antes de repetir.

**Conciliação (D-E08-6 e 7).**

- Reserva: `findReservationByCode` quando havia escrita em curso.
- Hóspede: `listReservationGuests`, casando pelo `pessoa_id`, quando havia escrita em curso.
- Pessoa: **sempre** `findPersonByDocument` antes de criar, quando o hóspede não tem `person_id` conhecido no ambiente. Com `dados.id` presente, reaproveita a pessoa; ausente ou `404`, faz `POST /pessoas`. Corpo ambíguo ou incompleto dá `UNKNOWN_OUTCOME` (falha fechado). Esta é a escolha do `registerPerson` que a E07 deixou para a E08.
- `PUT`, cancelamento e `PATCH` de check-out são repetidos, porque não criam recurso. Se a repetição de um cancelamento der `VALIDATION`, a submissão fica `FAILED` com alerta.
- **Pessoa já conhecida:** o hóspede que já tem `person_id` no mesmo ambiente, de qualquer reserva (`FnrhRemoteIds.knownPerson`), é reaproveitado sem consulta nem `POST`. O hóspede é identificado pelo id do sobrevivente (`GuestsApi.identification(id).id`). Um hóspede cujo `person_id` já está entre os `remote_guest` da reserva é pulado, para uma mesclagem não duplicar a pessoa.
- A linha do hóspede recorrente em `remote_guest` é gravada **antes** do `POST` do hóspede (I-1 da revisão final, `1df90ff`). O cancelamento sem id remoto concilia quando há escrita em curso na reserva (I-2, `4d018cd`).

**Desfazer check-in e reativação (D-E08-8 e 9).** A API não tem as duas operações.

- Ao gravar o `UNDO_CHECK_IN`, o listener cancela (`CANCELLED`, por `cancelIfIdle`) os `CHECK_IN` da reserva não resolvidos, sem escrita em curso e sem hóspede no Serpro.
- No envio, sem hóspede da reserva no Serpro, o `UNDO_CHECK_IN` fica `SENT` sem chamada. Com hóspede no Serpro, fica `FAILED` com `NO_REMOTE_OPERATION` e alerta: a correção é manual, no portal, seguida de `dismiss`.
- Um novo check-in pula os hóspedes já no Serpro. Um `CHECK_IN` que sobrevive ao desfazer não cria nada novo: só concilia, grava os ids do que já existe e termina `SENT`. O `UNDO_CHECK_IN` superado por um novo check-in fica `SENT` sem chamada.

**Validação local (D-E08-10).**

- Roda só no `CHECK_IN` e no check-in que o `CHECK_OUT` roda antes. Todos os hóspedes são validados antes de qualquer chamada.
- Com erro, a submissão fica `INVALID`, com os erros por hóspede, campo e código em `fnrh.submission_error`, **sem o valor**, e alerta.
- Os campos da RN-19 (raça/cor, opção e tipo de deficiência) são neutralizados como `person.sensitiveData`/`INVALID_VALUE`, um por hóspede (I-3, `cf9d8e8`). O operador não sabe qual dos campos falta.
- A residência nula continua aceita, e o `checkedOutAt` não é validado: o check-out usa `StayGuestSummary.checkedOutAt` ou, sem ele, o instante do evento.
- Cada tentativa do `CHECK_IN` revalida todos os hóspedes, inclusive os já enviados (decisão E08 (m)).
- Menor sai depois do responsável e leva o `responsavel_id` dele. Menor cujo responsável é outro menor listado depois dá `FAILED` (`INTERNAL_ERROR`) com alerta, nunca `responsavel_id` errado. Reserva de OTA envia `BookingSummary.externalId`.

**Alerta (D-E08-11).** Cada passagem a `FAILED` ou `INVALID` chama `NotificationsApi.notify(INTEGRATION_FAILURE, "Falha no envio à FNRH", "Reserva <código>: <operação> — <falhou | dados inválidos>", withPermission(fnrh.submissions.manage))`, só com o código da reserva e rótulos fixos. O alerta sai **depois do commit, em transação própria**. Se o `notifications` falhar, o alerta se perde, mas o resultado da submissão fica gravado.

**Resultado e trilha.** O `FnrhSubmissionRecorder` grava cada resultado com `@Audited` (`fnrh.submission.send`, ator sistema; retrato só com id, operação, situação, tentativas e última falha). Ele só aplica o resultado a submissão `PENDING`. Numa submissão em qualquer outra situação (por exemplo, cancelada pelo listener do desfazer durante o envio), não grava, não alerta e só registra no log.

**Ids remotos por ambiente (D-E08-13).** `fnrh.remote_reservation` e `fnrh.remote_guest` têm `environment` na chave. Trocar de ambiente faz a próxima submissão registrar de novo. O **link de pré-check-in** fica em `remote_reservation`, cifrado (`FieldCipher`), sem exposição na API. A E11 pode usá-lo, e ele é mais um valor para a re-cifragem da M8 E15.

**Endpoints (D-E08-12 e 16):** `GET /api/v1/fnrh/submissions?status=…`, `POST /api/v1/fnrh/submissions/{id}/retry` e `POST /api/v1/fnrh/submissions/{id}/dismiss`, com as regras e permissões na tabela de "Endpoints e permissões".

Códigos novos: `404 FNRH_SUBMISSION_NOT_FOUND`, `409 FNRH_SUBMISSION_NOT_RETRYABLE`, `409 FNRH_SUBMISSION_NOT_DISMISSABLE`. Trilha: `fnrh.submission.retry` e `fnrh.submission.dismiss`.

**Job, métrica e view.** O job `fnrh-submissions-send` está descrito em [[ZenyHotelManager - Eventos e jobs]]. O gauge `zeny_fnrh_submissions{status}` está em [[ZenyHotelManager - Docker, observabilidade e CI]]. As tabelas e a view `fnrh.report_submissions` estão em [[ZenyHotelManager - Schemas, migrações e views de relatório]].

**Armadilhas para quem mexer:**

- O recorder só aplica resultado a `PENDING`. Uma transição nova que tire a submissão de `PENDING` durante o envio faz o resultado sumir (só o log registra).
- `cancelIfIdle` cancela num `UPDATE` condicional: se o job marcou `in_flight` entre a leitura e o cancelamento, não cancela. Não troque por ler e depois salvar.
- `in_flight` só muda pela store (`markInFlight`) e pelos `FnrhRemoteIds.save*`, em transação própria. Nunca grave a marca pela entidade na transação do chamador, que pode desfazer.
- A lista `SENSITIVE_FIELDS` do `FnrhCheckInStep` repete a do validador. Um campo sensível novo no validador precisa entrar nela (o ideal é uma constante compartilhada ou um teste).
- Os testes chamam `dismiss(now)` por extensões só de teste (`FnrhSubmissionDismissCompat.kt`). Migre os testes e apague essas extensões numa limpeza. São duas cópias (ver "Pacotes"); a M6 E16 apaga as duas. **Paga na M6 E16** ([[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E16 - f7e211bd]], item 4): as duas cópias de teste saíram e os testes usam o `FnrhSubmission.dismiss()` de produção; o handoff da E16 registra dois `ASSERCAO_REMOVIDA` no `FnrhSubmissionTransitionsTest` (só o argumento ignorado de `dismiss` saiu).
- A marca de escrita em curso de uma submissão `DISMISSED` fica ligada para sempre e custa um `GET` a mais por registro da reserva.
- Na gravação da linha do hóspede recorrente (I-1), a marca de escrita em curso é limpa antes do `POST` do hóspede. É a mesma janela estreita que o `registerPerson` já tinha.
- As propriedades `zeny.fnrh.submissions.*` não validam limites (zero ou negativo; M-4).
- Trocar de ambiente com submissões em execução pode gravar um id no ambiente errado (M-3). Ao trocar, drene ou pause o job (E16 ou M8 E13).
- O gauge roda um `GROUP BY` a cada raspagem. `FnrhSubmissionJobAttackTest` usa `sleep` fixo e pode ficar intermitente em CI lenta.

**Notas para as próximas etapas:**

- E09: ver "Notas para a E09".
- E09 e M8 E13: decidir corte ou limpeza do acumulado antes de ligar em homologação (D-E08-5).
- E16 ou M8 E13: drenar ou pausar o job na troca de ambiente (M-3). *Nota do curador (roadmap, commit `7aa2527`, só leitura, sem captura correspondente):* o handoff da E16 diz que a M-3 continua com a M8 E13; a limpeza mantém o ambiente, mas "limpar e depois `PUT` em outro ambiente" com um envio em curso é o mesmo cenário que o `PUT` já permite.
- M6 E14 (no-show): concluída em 2026-11-14; ver "No-show (M6 E14, 2026-11-14)" abaixo.
- M6 E15 (concluída em 2026-11-14; ver "Camada e dependências" e "Pacotes"): o `fnrh` implementa uma porta do `frontdesk` que traduz os códigos de motivo de viagem e de meio de transporte em rótulo, pelo catálogo de domínios já semeado (`FnrhDomainCatalog`, `TRAVEL_REASONS` e `TRANSPORT_MODES` em `fnrh/V2026_11_04_1030__create_fnrh_domain_values.sql`).
- M6 E16 (concluída em 2026-11-14): apagou as duas cópias de `FnrhSubmissionDismissCompat.kt` em `src/test` (D-E16-4); nenhuma chamada de `dismiss` com instante existe mais em `src/test`, e helpers de teste com o mesmo nome (como `FnrhNoShowSendAttackTest.dismiss(submission: UUID)`) ficam. Textos da E15 corrigidos (D-E16-5; nenhuma asserção mudou): o comentário do `ModularityTest` do `fnrh` passou a dizer "Nunca iam nem tabela de outro schema; do `frontdesk`, só a porta dos rótulos (M6 E15)", e o KDoc e o nome de um teste de `RegistrationCardApiTest` passaram a falar em **rótulos** da FNRH, não "códigos FNRH". Ver [[ZenyHotelManager - Testes de integração]] ("M6 E16"). *Nota do curador (conferência por `git` em 2026-11-15, só leitura):* no `d83022b` não há `FnrhSubmissionDismissCompat.kt` em `src/test`, e o comentário do `ModularityTest` tem o texto citado.
- M6 (fechamento): as pendências vêm de `fnrh.report_submissions`. `DISMISSED` não segura a fila.
- Manutenção do `fnrh`: validar só os hóspedes ainda não enviados (decisão E08 (m)); e as guardas (d) e (e) da M6 E14 (ver "No-show", a seguir), numa etapa a criar pelo `arquiteto`.

### No-show (M6 E14, 2026-11-14)

**Evento e submissão (D-E14-2).** O `ReservationMarkedNoShow` (M6 E11) grava **uma** `FnrhSubmission` com `operation = NO_SHOW`, `event_key = no-show:v<version>` e `causal_version = ReservationMarkedNoShow.version`, idempotente pela chave `(reservation_id, operation, event_key)`: a reentrega do evento (inclusive depois de `SENT`, `FAILED` ou `DISMISSED`) não grava outra. O posto de `NO_SHOW` na ordem causal é **6**, anexo ao fim (a lista passa a `REGISTER_RESERVATION` 0 < `UPDATE_RESERVATION` 1 < `CANCEL_RESERVATION` 2 < `CHECK_IN` 3 < `UNDO_CHECK_IN` 4 < `CHECK_OUT` 5 < `NO_SHOW` 6); o posto só desempata dentro da mesma `causal_version`. Como o registro tem `causal_version` 0 e o no-show tem `version` maior ou igual a 1, o no-show sai sempre depois do registro da reserva.

**Caminho (D-E14-1; decisão (a) do handoff).** Escolhido o no-show em lote da reserva, `POST /reservas/{reserva_id}/noshow`, e não um dos individuais. O critério de aceite formulava a escolha entre os dois individuais; este é um terceiro caminho. Motivo: no nosso fluxo (D-E07-2) a reserva é registrada na criação sem hóspedes e os hóspedes só entram no check-in; uma reserva no-show nunca teve check-in, então não há `hospede_id` remoto para o caminho individual. O caminho da reserva só precisa do id remoto que já guardamos, é o único sem divergência no PDF e alcança também os hóspedes de pré-check-in criados pelo próprio hóspede pelo link. É barato de desfazer (fica no adaptador, sem migração nem contrato). Alternativa descartada: o individual, que exigiria registrar hóspedes sem check-in.

**Passo do envio, pelo estado atual (D-E14-3, D-E08-9).**

- Reserva que **não está mais `NO_SHOW` aqui** (reativada antes do envio): `SENT` sem chamada, antes de qualquer conciliação, porque o no-show remoto é irreversível (decisão (b); ruling do orquestrador na revisão da Task 4). Resíduo: uma reativação entre a leitura e o `POST` ainda envia o no-show; o `UPDATE` seguinte fica `FAILED REMOTE_NO_SHOW` com alerta.
- Remota guardada, não cancelada e não no-show: `markNoShow`; no sucesso grava `no_show = true` em `fnrh.remote_reservation` (preservando o link e `cancelled = false`) e a submissão fica `SENT`.
- Sem remota guardada: com escrita em curso na reserva, concilia (o mesmo caminho do `cancel`); achada, segue acima; não achada, `SENT` sem chamada (a reserva no-show nunca é registrada: `NOT_REGISTERED`).
- Remota já cancelada ou já no-show: `SENT` sem chamada.
- **Repetição (decisão (c)):** o `POST …/noshow` é repetido no `retry` depois de `UNKNOWN_OUTCOME`, como o cancelamento da E08 (o no-show não cria recurso, então não há conciliação antes de repetir). Uma repetição recusada (`VALIDATION`) fica `FAILED` com alerta, e a remota local continua sem `no_show`; depois do `dismiss`, um `UPDATE` de reativação faria o `PUT` numa reserva `NOSHOW` no Serpro.

**Estado remoto: a remota é cancelada ou no-show, nunca as duas (D-E14-4).** A API não desfaz no-show.

- `UPDATE_RESERVATION` (inclusive o da reativação) com a remota `no_show` e a reserva ativa aqui: `FailedLocally(REMOTE_NO_SHOW)` com alerta, sem chamada (correção no portal e `dismiss`, como o `REMOTE_CANCELLED`). Com a reserva cancelada ou no-show aqui: `SENT` sem chamada.
- `CANCEL_RESERVATION` com a remota `no_show`: `SENT` sem chamada.
- **Não coberto (decisão (d)):** `CHECK_IN` e `CHECK_OUT` sobre uma remota no-show (ou cancelada, já na E08) não têm guarda local. Depois de reativação, `dismiss` e novo check-in, o envio cadastra a pessoa e recebe `4xx` (`FAILED` com alerta). Recomendação do handoff: numa manutenção do `fnrh`, `remote.closed` leva a `FailedLocally(REMOTE_CANCELLED | REMOTE_NO_SHOW)` sem chamada.
- **Lacuna anterior, da E08 (decisão (e)):** um `CANCEL_RESERVATION` pendente sai mesmo depois da reativação, e a remota é cancelada sem volta com a reserva ativa aqui. Recomendação: a mesma guarda pelo estado local (`status != CANCELLED`, sem chamada), numa etapa de manutenção do `fnrh` a criar pelo `arquiteto` (a E16 é só de teste).
- Fora de alcance, registrado também na lista da E09: check-in enviado, desfeito (`UNDO_CHECK_IN` `FAILED NO_REMOTE_OPERATION`, `dismiss`) e depois no-show; o Serpro tem um hóspede `CHECKIN_REALIZADO` e o lote pode ser recusado ou corrigir o hóspede.

**Códigos novos (D-E14-5).** `FnrhOperation.NO_SHOW` (posto 6), `FnrhSubmissionFailure.REMOTE_NO_SHOW` (`temporary = false`) e os espelhos da web `FnrhSubmissionOperationView.NO_SHOW` e `FnrhSubmissionFailureView.REMOTE_NO_SHOW`. Rótulo do alerta `integration-failure`: `no-show`. No contrato, `operation` e `lastFailure` das submissões já eram `x-extensible-enum`, então acrescentar não quebra (oasdiff sem `ERR`). As falhas locais da E08 (`REMOTE_CANCELLED`, `NO_REMOTE_OPERATION`) ganham `REMOTE_NO_SHOW`.

**Resiliência (RN-22).** Com o Serpro fora do ar durante o fechamento, o fechamento conclui `COMPLETED` e a submissão fica `PENDING` com a tentativa contada (`attempts = 1`, `SERVER_ERROR`); credenciais recusadas também não travam o fechamento. `FAILED` e `INVALID` seguram a fila da reserva até `retry` ou `dismiss`.

**Dependências do módulo.** Inalteradas: `shared`, `guests`, `reservations` e `notifications` (o `ModularityTest` não mudou). A divergência com a ARCHITECTURE §3.1 (`hotel`) está em "Camada e dependências".

Migração, CHECKs e coluna `no_show`: [[ZenyHotelManager - Schemas, migrações e views de relatório]] ("Schema `fnrh`: no-show"). Listener: [[ZenyHotelManager - Eventos e jobs]]. Testes: [[ZenyHotelManager - Testes de integração]].

*Nota do curador (conferência por `git` em 2026-11-15, só leitura, no `ad970fc`):* o `FnrhSubmissionListeners.kt` tem 9 métodos `@ApplicationModuleListener`, um deles para `ReservationMarkedNoShow` com `FnrhOperation.NO_SHOW`; o `FnrhModule.kt` declara `allowedDependencies = ["shared", "guests", "reservations", "notifications"]`. O corpo dos passos do envio não foi conferido no código.

## Notas para a E09

- Confirmar se o `POST /reservas/{id}/hospedes` aceita `CHECKIN_REALIZADO` numa reserva `CRIADA`.
- Confirmar se o filtro `codigo_reserva` casa exatamente (hoje só a página 1 é lida).
- Confirmar o limite real e o eco de `GeneroDescricao` na homologação (M5 E15).
- Confirmar o formato do `400`, a ordem de `dados_hospedes` e o limite de 200 caracteres da senha; e o no-show (os quatro itens abaixo, mais o caminho individual `/no-show` ou `/noshow`, que o PDF da API deixa divergente e que só importa se o caminho em lote for recusado).
- No-show (M6 E14; confirmar na homologação, cobrado também pelo gate M8 E13):
  - O **código de resposta** do `POST /reservas/{id}/noshow` numa reserva **sem hóspedes** (o Serpro pode recusar o lote com `4xx`; hoje isso vira `FAILED` com alerta).
  - A **situação da reserva depois do lote**: um `200` com `dados` vazio pode deixar a remota em `CRIADA` (o `no_show = true` local ficaria falso em relação ao Serpro).
  - A **resposta à repetição** do `POST …/noshow` numa reserva já `NOSHOW` (depois de um `UNKNOWN_OUTCOME`, uma recusa viraria um `FAILED` falso).
  - O **lote numa reserva com hóspede `CHECKIN_REALIZADO`** (check-in desfeito: o lote pode ser recusado ou corrigir o hóspede).
- O critério de aceite da E09 ("o no-show, se o M6 já o publicar") passa a valer: o M6 publica. O texto dele e o do critério 3 da M6 E14 pedem ajuste do `arquiteto`, porque o caminho escolhido não é nenhum dos dois individuais formulados.
- Da E08: confirmar `dados.id` na consulta por documento, o `PUT` numa reserva `EM_ANDAMENTO`, o `POST /pessoas` com documento repetido, se o `GET /reservas` devolve o link de pré-check-in (nulo numa reserva conciliada), se o `PATCH` de check-out repetido é aceito (M-6), se um `404` por rota errada se distingue de pessoa ausente e os timeouts de 100 ms dos testes do adaptador.
- A E09 segue `#bloqueada` só pela Q-12: E08 e E16 estão concluídas. A homologação continua fora do gate do M5 e passa a ser cobrada pelo gate de inauguração (M8 E13).

## Limitações

- Os fatos vêm do roadmap e do plano da E07; a captura não releu o código nem `docs/fnrh/api-fnrh-v2.4.md` por inteiro. Nomes de classes, colunas e rótulos seguem o plano e o handoff, e o plano pode ter ajustes feitos na execução que não aparecem no handoff.
- Os detalhes do saneador depois da revisão final vêm do handoff, que os descreve de forma resumida.
- A lista do IBGE é um instantâneo do download.
- O texto da E08 descreve a branch `roadmap/m5-recepcao-fnrh` (fechamento `2d07363`), ainda fora da `main` quando capturado. Vem do handoff, do plano (D-E08-1 a 17), da SPEC, da ARCHITECTURE, das migrações e de alguns arquivos de código; a captura não leu o código inteiro, e a afirmação de que `in_flight` só muda pela store vem das portas e do plano.
- O texto da M6 E14 vem do handoff, do plano (D-E14-1 a D-E14-7), da migração e de `LogMessages.kt`; a captura não leu o código de produção do `fnrh` (`FnrhGateway.kt`, `FnrhSubmissionSender.kt`, `FnrhSubmissionListeners.kt`, `domain/FnrhSubmission.kt`). Em divergência, vale o código. O caminho em lote é hipótese baseada em `docs/fnrh/api-fnrh-v2.4.md` até a E09.
- O texto da M6 E15 vem do handoff, do plano (D-E15-1 a D-E15-7) e do código da porta, da implementação, do `FnrhModule`, do `FrontdeskPermissions` e do `RegistrationCardService`; templates, testes e `RegistrationCardController` não foram lidos pela captura. Em divergência, vale o código.
- O `FnrhSettingsResponse` devolve o `username` em claro (E07; depois da limpeza da E16 ele vem nulo). A divergência com a ARCHITECTURE §12 ("nunca devolvida na API") foi resolvida em 2026-11-12 pela correção da §12, decidida pelo usuário: na API, o segredo é a senha (ver "Configuração cifrada, por ambiente").

---

## Proveniência

- 2026-11-09 — [[2026-11-05 - ZenyHotelManager - atualização m5-recepcao-fnrh E07 - 9f02405c]] (capture_id: 9f02405c-a73b-44f0-8f8c-5fb75860aa05): texto proposto para o módulo (item 2 da captura), integrado sem resumo, com abertura sugerida pela captura; o "Limite conhecido" da credencial foi substituído conforme a captura c889f886.
- 2026-11-09 — [[2026-11-06 - ZenyHotelManager - atualização revisão de arquitetura dos roadmaps - c889f886]] (capture_id: c889f886-0719-4f28-984e-f2ef23ed9520): M5 E16 (limpar credencial), M5 E15 no mapeador, conciliação e view da E08, SPEC §8.2.17 e no-show pela M6 E14.
- 2026-11-10 — [[2026-11-10 - ZenyHotelManager - atualização m5-recepcao-fnrh E15 - a22890e7]] (capture_id: a22890e7-e6b1-4e99-97d7-747bfcdd5788): frase da E15 no mapeador substituída pelo envio de `GeneroDescricao`; saneador (`8d6203a`, D-E15-6) e nota para a E09 complementados.
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]] (capture_id: 8df87866-4285-4e24-8878-0fab70c9436c): E08 (item 1 da captura): estado, dependências, pacotes, operações de conciliação na porta, seção "Envio assíncrono (M5 E08)" no lugar de "Notas para a E08", validador, métrica, endpoints, migrações, dados que nunca saem e notas para a E09.
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 (revisão humana) - 65d0d4ff]] (capture_id: 65d0d4ff-bc24-4f40-94ba-c062bdf2b9c1): aprovação do padrão de envio assíncrono pelo usuário como referência para M7 e M8.
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E16 - 6095f729]] (capture_id: 6095f729-34e7-4667-9c48-d112262c6212): E16 (item 1 da captura): limpeza da credencial e envio depois dela, linha na tabela de endpoints, correção do `500` do status, estado da abertura, nota para a E09 e limitação do `username`; nota do curador sobre a M-3.
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 - 2c135bbf]] (capture_id: 2c135bbf-8248-4987-a617-dcb3fa94c0a5): dependências substituídas (G5: sem `hotel` nem `HotelApi.profile()`) e classes a mais em "Pacotes", com as duas cópias de `FnrhSubmissionDismissCompat.kt` (G5).
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 (revisão humana) - 64ce6698]] (capture_id: 64ce6698-9d2c-4a1c-b4d0-af930d24bff5): usuário da FNRH na API decidido pelo usuário (§12 corrigida), na configuração e na limitação do `username`.
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização arquitetura e sincronização do M6 - 3a747cdc]] (capture_id: 3a747cdc-6309-4bfa-bea2-3f6cd483a30f): item "Credencial" da §12 aplicado (`0e58cf9`), aresta prevista `fnrh` → `frontdesk` e planejamento das M6 E14, E15 e E16.
- 2026-11-15 — [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E14 - 998156dc]] (capture_id: 998156dc-c51d-47f2-ad9c-86f204f7236c): M6 E14 (item 1 da captura): operação `markNoShow` na porta, no-show fora da porta só o individual, linha `NO_SHOW` no mapeamento e posto 6, subseção "No-show (M6 E14, 2026-11-14)", notas para a E09, estado, migração e limitação; nota do curador com a conferência por `git`.
- 2026-11-15 — [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E15 - c139da21]] (capture_id: c139da21-4f16-40bc-8cae-9ee2dc4444c3): M6 E15 (item 2 da captura): aresta `fnrh` → `frontdesk` só pela porta `RegistrationCardLabels` (dependências substituídas, aresta prevista dada como implementada), `FnrhRegistrationCardLabels` em "Pacotes", estado da abertura, nota da E15 nas próximas etapas e limitação; nota do curador com a conferência por `git`.
- 2026-11-15 — [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E16 - f7e211bd]] (capture_id: f7e211bd-3d35-495d-87c3-33a791c87e48): M6 E16 (item 4 da captura): `FnrhSubmissionDismissCompat.kt` removido (armadilha paga, "Pacotes" e próximas etapas), textos da E15 corrigidos e estado da abertura; nota do curador com a conferência por `git`.
