---
type: capture
status: archived
created: 2026-11-05
capture_id: 9f02405c-a73b-44f0-8f8c-5fb75860aa05
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E07

## Conteúdo capturado

Resumo do agente (publicado a pedido do orquestrador do lote M5, sessão externa no repositório `/home/caio/repos/ZenyHotelManager`): fechamento da etapa E07 do M5 (módulo `fnrh`: configuração, domínios e adaptador Serpro). O texto abaixo é o novo ou alterado de cada nota afetada e diz o que substitui ou complementa. Os fatos vêm do handoff da E07, de "Decisões do lote E07" e da última entrada do "Histórico de revisões" de `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`, e das "Decisões desta etapa" (D-E07-1 a 12) e "Global Constraints" de `docs/superpowers/plans/2026-11-04-m5-recepcao-fnrh-e07.md`. O levantamento da API está em `docs/fnrh/api-fnrh-v2.4.md` (citado pelo handoff; não o reli por inteiro).

Complementa e em parte substitui as capturas [[2026-10-28 - ZenyHotelManager - atualização m5-recepcao-fnrh E13 - 7a6ce25a]] (capture_id: 7a6ce25a-b05d-40ab-88c0-e459a9c329ca) e [[2026-11-04 - ZenyHotelManager - atualização m5-recepcao-fnrh E14 - f8103233]] (capture_id: f8103233-d5b2-48b1-b302-c9360ff5b66b), ambas já arquivadas em `90 Archive/Inbox/` quando esta foi escrita; por isso os links podem apontar para o arquivo.

### 1. Hub `ZenyHotelManager` (seção "Estado") e [[ZenyHotelManager - Estado por marco]]: substitui a linha do M5 da captura da E14

- M5 em andamento: **E01 a E07, E13 e E14 concluídas**.
- A E07 está na branch `roadmap/m5-recepcao-fnrh` (commit `bd75afc` de fechamento; ponta de código `d5614b6`) e ainda **não** está em `origin/main`. O usuário pediu a `main` local pronta para `git push origin main`; o push é dele.
- **Próximas elegíveis: E08** (depende de E01, E02 e E07, todas concluídas) **e E10**. A E09 segue `#bloqueada` (depende da E08 e da credencial, Q-12).
- **Revisão humana pendente: E13 e E07.** O lote parou na da E07.
- Obsoleta: a indicação "próximas elegíveis: E07 e depois E10" da captura da E14, item 1.

### 2. Nota nova `ZenyHotelManager - Módulo fnrh` (proposta de texto completo)

Sugestão de abertura da nota: "Integração com a FNRH Digital (Serpro/MTur), API v2.4. Estado: E07 concluída (configuração, domínios, porta e adaptador, validação local); o envio por eventos é a E08 e a homologação real é a E09."

**Camada e dependências**

- Camada "Integração governamental" (acima da Hospedagem). Pacote `com.zeny.hotel.fnrh`, com `FnrhModule.kt` na raiz.
- `allowedDependencies` hoje: `shared` e `guests` (D-E07-12: o payload não pede dado do hotel; a `HotelApi.profile()` fica para a E11). A **E08 acrescenta `reservations` e `notifications`**, já previstos na tabela da ARCHITECTURE §3.1.
- Nunca importa `iam`, `frontdesk` nem lê tabela de outro schema. `frontdesk` não pode chamar `fnrh` (camada acima): o `fnrh` reage a eventos de `reservations`. Há um teste do `fnrh` no `ModularityTest`, com as dependências exatas.

**Pacotes**

- Raiz (API pública): `FnrhModule`, `FnrhPermissions`, `FnrhErrorCodes`, `FnrhFieldCodes` e `FnrhEnvironment` (`HOMOLOGATION`, `PRODUCTION`; fica na raiz porque a web o expõe).
- `domain`: modelo de dados da FNRH, regras de configuração (`FnrhSettings`), escolha do CPF solicitante (`RequesterCpfPolicy`), mapeador do hóspede (`FnrhPersonMapper`), validador local (`FnrhLocalValidator`), `FnrhFieldError`, `FnrhDomainCatalog` e `IbgeMunicipalities`. Sem Spring.
- `application`: casos de uso e portas (`FnrhGateway`, `FnrhConnectionSource`, `FnrhIntegrationLog`, `FnrhRequesterDirectory`), `FnrhSettingsService`, `FnrhRequestersService`, `FnrhDomainsService`, `FnrhDomainValuesWriter`, `FnrhStatusService`.
- `infrastructure`: adaptador `SerproFnrhGateway` (`RestClient` com `JdkClientHttpRequestFactory` e timeouts), `FnrhMessageSanitizer`, persistência, `JdbcFnrhIntegrationLog` (transação própria, `REQUIRES_NEW`, no modelo do `PushDeliveryLog` do `notifications`), `FnrhMetrics` (`MeterBinder`) e `FnrhProperties`.
- `web`: só controllers e DTOs. `@Tag("FNRH")`.
- **Toda chamada ao Serpro roda fora de transação do banco.**

**Configuração cifrada, por ambiente (D-E07-1)**

- O administrador escolhe o **ambiente** (`HOMOLOGATION` ou `PRODUCTION`); as URLs ficam em propriedade: `zeny.fnrh.homologation-url` (padrão `https://hom-lowcode.serpro.gov.br/FNRH_API/rest/v2`) e `zeny.fnrh.production-url` (padrão `https://fnrh.turismo.serpro.gov.br/FNRH_API/rest/v2`), mais `zeny.fnrh.connect-timeout` (5 s) e `zeny.fnrh.read-timeout` (20 s). Os testes apontam as duas URLs para o WireMock.
- **Trocar de ambiente exige informar a senha de novo** (`422 FNRH_PASSWORD_REQUIRED_FOR_ENVIRONMENT_CHANGE`), para a credencial de um ambiente não ir para o outro. Descartadas: URL livre na configuração (a credencial poderia ir para qualquer host) e propriedade única (cada troca pediria nova implantação).
- Usuário, senha e CPF padrão ficam cifrados (`FieldCipher`/`EncryptedStringConverter`). A tabela `fnrh.settings` tem uma linha semente (versão 0, desligada, homologação) para o primeiro `PUT` ter `ETag`.
- Regras do domínio: `password` nula mantém a atual; ligar (`enabled = true`) sem usuário, senha ou CPF padrão dá `422 FNRH_SETTINGS_INCOMPLETE`. Sem configuração (ou desligada), `FnrhConnectionSource.current()` devolve `null` e nada é enviado.
- A senha nunca volta na API; o CPF sai mascarado (`***.***.***-NN`). A trilha do `PUT` não guarda senha, CPF nem o `username` (ver item 3).
- Limite conhecido (decisão (i) do lote): **não há como apagar a credencial do Serpro**; ao desligar a integração, ela continua cifrada no banco. Recomendação do orquestrador: uma ação explícita de limpar, com trilha, antes do M8.

**CPF solicitante por usuário (H5, D-E07-7, decisão (h))**

- Cadastro `fnrh.requester`: id do usuário (opaco; não se confere se existe) → CPF cifrado, mostrado mascarado. `RequesterCpfPolicy.choose(performedBy, cpfOfUser, defaultCpf)` escolhe o CPF do usuário que fez a operação e, sem ele (ou com `performedBy` nulo), o padrão; sem nenhum dos dois, `null`. A porta `FnrhRequesterDirectory.cpfOf(userId)` é para a E08.
- **Sem `DELETE`:** o plano pedia `DELETE /requesters/{userId}`, mas a convenção do projeto é "a API não apaga nada" e o build pegou o erro. Em lugar dele, `POST /api/v1/fnrh/requesters/{userId}/deactivate`, que apaga o CPF e mantém a linha.
- A troca do CPF de um usuário por outro com o mesmo final deixa rastro na trilha: o `FnrhRequester` tem `@Version` e a versão entra no retrato (achado I1 da revisão final).

**Porta `FnrhGateway` e operações (D-E07-2)**

A porta é a do que a API v2.4 faz, não a lista da SPEC §8.2.17 (`registerStay/checkIn/checkOut/noShow/cancel`). Nomes do nosso lado em inglês; o adaptador mapeia para os do Serpro. Toda operação recebe um `correlationRef` opaco (id da reserva ou da submissão), nunca dado pessoal.

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

- **Fluxo decidido (D-E07-2, decisão (a)):** a reserva é registrada **na criação**, sem dado pessoal. No check-in entram a pessoa e o hóspede (`CHECKIN_REALIZADO`); o check-out sai por `PATCH`; o cancelamento só vale em `CRIADA`. Descartada a alternativa "registro só no check-in" (`POST /hospedagem/registrar`): o cancelamento nunca chegaria ao Serpro e o link de pré-check-in não serviria.
- Fora da porta: `hospedagem/registrar`, pré-check-in de balcão, fichas, operações em lote, `DELETE /reservas`, `PATCH …/checkin` (o hóspede já entra com check-in) e o **no-show**, que fica para o M6 (H15) porque o caminho individual diverge no PDF.
- Campos da reserva (`FnrhReservationData`): `numero_reserva` = `Reservation.code` (nunca o código do `Booking`); `numero_reserva_ota` = `Booking.externalId`; com OTA, `origem_reserva_id = OTA`, senão `MEIOHOSPEDAGEM`; `minors` sai da **data de nascimento** (menor de 18 anos na entrada), não de `childAges`.
- Instantes enviados ao Serpro: UTC com milissegundos e `Z` (`2026-02-10T15:00:00.000Z`), tanto no JSON quanto no `text/plain`.
- **`cpf_solicitante` só onde a API exige (D-E07-9, decisão (b)):** `POST /pessoas`, `GET /pessoas/documento/…` e `POST /hospedagem/registrar`; nesta porta, só `registerPerson`. O roadmap supunha o header em toda chamada; a fonte oficial prevalece. Consequência: o `performedBy` só pesa no registro da pessoa, no check-in. A ARCHITECTURE §12 foi corrigida nesse ponto no fechamento.
- O adaptador usa `Basic Auth` com o usuário e a senha da conexão de cada chamada.

**Classificação de falhas (`FnrhFailure`, com `temporary`)**

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

**Saneador (`FnrhMessageSanitizer`)**

- A mensagem do Serpro vem de `mensagem` no corpo JSON; o corpo bruto nunca é usado. O saneador troca por `***` os valores que o adaptador acabou de enviar (de 3 caracteres ou mais) e cada palavra deles com 3 ou mais letras (ignora maiúsculas e acentos, porque o Serpro pode ecoar só "MARIA"), as sequências de 5 ou mais dígitos e os e-mails, e corta em 200 caracteres.
- Depois da revisão final: **todo caractere de controle Unicode (`Cc`) e os de formatação** são tratados no saneador e nos rótulos, inclusive U+2028 e U+2029. O saneador mascara os valores enviados e os padrões.
- A mensagem saneada vai **só** para o log e para a exceção.

**`fnrh.integration_call` (D-E07-8, decisão (g))**

- Tabela *append-only* (`REVOKE UPDATE, DELETE`, trigger, bean `AppendOnlyTables`), **sem coluna de texto livre**: `operation`, `environment`, `outcome`, `http_status`, `duration_ms`, `correlation_ref`, `remote_id`, `occurred_at`; índice `(environment, outcome, occurred_at)`; CHECK no `remote_id` (revisão final). A mensagem do Serpro nunca vai para ela: pode trazer o nome do hóspede e a tabela não admite expurgo.
- Gravada em transação própria: a linha fica mesmo quando o chamador faz rollback. Uma linha por chamada HTTP; log `INFO` no sucesso e `WARN` na falha; a URL nunca entra.

**Status e métricas**

- `GET /api/v1/fnrh/status` (`fnrh.submissions.read`): `{configured, enabled, environment, lastSuccessAt, lastFailureAt, lastFailureOutcome}`, com os instantes do **ambiente atual**; `lastFailureOutcome` é `x-extensible-enum`.
- Métricas por `MeterBinder`, que aparecem em `/actuator/prometheus`: `zeny_fnrh_calls_total` (tags `operation`, `outcome`, `environment`), `zeny_fnrh_last_success_seconds`, `zeny_fnrh_last_failure_seconds` (`NaN` sem registro) e `zeny_fnrh_configured` (0 ou 1). **Nenhum `HealthIndicator`**: a readiness não depende da FNRH (`ActuatorExposureTest` intacto, H22). A E08 acrescentará a métrica de pendentes.

**Domínios semeados e refresh tudo-ou-nada (D-E07-5)**

- Tabela `fnrh.domain_value (domain, code, label, refreshed_at)`, chave `(domain, code)`. A migração **semeia** todos os `id` e `label` do levantamento da v2.4, então o cache nunca começa vazio (descartado o cache vazio até o primeiro `refresh`, que deixaria toda submissão inválida).
- Dez domínios: `transport-modes`, `travel-reasons`, `guest-statuses`, `genders`, `disability-options`, `races`, `disability-types`, `document-types`, `booking-statuses`, `record-statuses` (kebab-case na URL; nome desconhecido dá `404 FNRH_DOMAIN_NOT_FOUND`).
- `POST /api/v1/fnrh/domains/refresh`: o `FnrhDomainsService`, sem transação, confere a permissão e busca os 10 domínios **fora de transação**; depois chama **outro bean**, `FnrhDomainValuesWriter`, cujo método `@Audited @Transactional` só grava a substituição (num bean separado porque a autoinvocação pularia o proxy, e com ele a transação e a trilha; foi o Importante aberto na rodada 1 da revisão de arquitetura). **Se qualquer busca falhar, nada muda.** Resposta com a contagem por domínio. Mapeamento de erros: `NOT_CONFIGURED` → `422 FNRH_NOT_CONFIGURED`; `UNAUTHORIZED`/`FORBIDDEN` → `422 FNRH_CREDENTIALS_REJECTED`; temporárias → `503 FNRH_UNAVAILABLE`; `VALIDATION`/`NOT_FOUND` → `502 FNRH_REJECTED`.
- A web nunca devolve o tipo de domínio; a application o mapeia.

**Validador local e lista do IBGE (RF-FNRH-06, H21, D-E07-3, D-E07-10, D-E07-11)**

- Fica em `domain`, sem Spring, junto com o mapeador e a lista do IBGE; **a E08 os monta**.
- `FnrhLocalValidator.validate(person, guest, arrival, responsibleKnown)` devolve `FnrhFieldError(field, code)`, **nunca o valor**. Códigos: `REQUIRED`, `INVALID_VALUE`, `NOT_IN_DOMAIN`, `INCONSISTENT`. Regras: nome e documento obrigatórios (CPF passa pelo `Cpf`); nacionalidade e residência ISO 3166-1 alpha-2 (`Locale.getISOCountries()`, D-E07-4); nascimento, gênero e raça obrigatórios; gênero, raça, opção e tipo de deficiência, motivo de viagem e meio de transporte no catálogo; `OUTRO` exige descrição; deficiência `SIM` exige tipo; com residência `BR`, município obrigatório e na lista do IBGE, UF obrigatória e igual à do município (`INCONSISTENT`), CEP de 8 dígitos quando informado (e então logradouro, número e bairro); residência fora do `BR` não exige município nem UF; menor de 18 anos na data de entrada sem responsável gera `guest.responsibleGuestId`/`REQUIRED`.
- Mapeador: documento = CPF se houver, senão passaporte (os outros tipos, como RG, não entram); gênero e raça mapeados aos códigos da API; raça ou gênero **nulos** significam "não coletado" e a validação acusa `REQUIRED` (D-E07-10); só `NOT_DECLARED`/`NOT_INFORMED` viram `NAOINFORMAR`/`NAOINFORMADO`.
- **Lista do IBGE (decisão (d)):** recurso versionado `src/main/resources/fnrh/ibge-municipios.csv` (5.571 municípios; `codigo;uf`), com o cabeçalho trazendo a fonte (`https://servicodados.ibge.gov.br/api/v1/localidades/municipios`), a data do download e o SHA-256 do JSON. **Risco aceito: um município criado depois do download é recusado até o recurso ser atualizado.** A API da FNRH não tem endpoint de municípios. Descartada a validação só de formato.
- A validação local recebe a residência nula sem erro e não confere o `checkedOutAt`: a E08 decide.

**Endpoints e permissões**

| Endpoint | Permissão |
|---|---|
| `GET /api/v1/fnrh/settings`, `PUT /api/v1/fnrh/settings` (`If-Match` obrigatório; `428` sem ele, `412` com ETag velho) | `fnrh.settings.manage` |
| `GET /api/v1/fnrh/requesters`, `PUT /api/v1/fnrh/requesters/{userId}`, `POST /api/v1/fnrh/requesters/{userId}/deactivate` (o CPF nunca vai na URL) | `fnrh.settings.manage` |
| `POST /api/v1/fnrh/domains/refresh` | `fnrh.settings.manage` |
| `GET /api/v1/fnrh/domains/{domain}` | `fnrh.domains.read` |
| `GET /api/v1/fnrh/status` | `fnrh.submissions.read` |

- Nenhuma permissão é sensível. `fnrh.submissions.manage` nasce na E08 (retry da fila e destinatário do alerta de falha). Códigos de problema em `FnrhErrorCodes`: `FNRH_SETTINGS_INCOMPLETE`, `FNRH_PASSWORD_REQUIRED_FOR_ENVIRONMENT_CHANGE`, `FNRH_REQUESTER_NOT_FOUND`, `FNRH_DOMAIN_NOT_FOUND`, `FNRH_NOT_CONFIGURED`, `FNRH_CREDENTIALS_REJECTED`, `FNRH_UNAVAILABLE`, `FNRH_REJECTED`.
- Migrações: `V2026_11_04_1000` a `V2026_11_04_1030` na pasta `fnrh/` (settings com GRANT, requesters, integration_call, domain_value). **Foram alteradas no lugar durante a etapa porque nunca saíram da branch:** um banco local de desenvolvimento que tenha aplicado uma versão anterior precisa ser recriado (`docker compose -f docker/compose.yaml down -v`). A próxima migração do projeto precisa de timestamp posterior a elas.

**Dados que nunca saem**

- Senha, número de documento, raça/cor, deficiência, nome, e-mail e telefone não entram em log, trilha, resposta, métrica nem no registro de integração. Todo tipo que os carrega sobrescreve o `toString` (`FnrhPersonData`, `FnrhGuest`, `FnrhDocument`, `FnrhConnection`, `FnrhProperties`). **`Cpf.toString()` devolve os dígitos:** nunca interpole `Cpf` em log, mensagem nem `toString`.

**Notas para a E08**

- A porta não tem operação para desfazer o check-in. O cancelamento só vale com a reserva em `CRIADA`. Os ids remotos dependem do ambiente.
- `UNKNOWN_OUTCOME`: concilia-se por `findReservationByCode` no registro da reserva e por `GET /reservas/{id}/hospedes` na inclusão do hóspede. No `registerPerson`, falta decidir entre aceitar o risco de pessoa duplicada e conciliar por `GET /pessoas/documento/…`.
- `UNAVAILABLE` é temporário: **limite as tentativas** (um erro de programação no envio também cai nele). Um 503 dentro de handler offline viraria recusa permanente.
- O responsável entra antes do menor (o `responsavel_id` precisa existir). `minors` sai da data de nascimento.
- A E08 monta o validador, o mapeador e a lista do IBGE (todos em `domain`, sem Spring); a lista de eventos que geram envio e o limite de tentativas são decisões abertas dela.

**Notas para a E09**

- Confirmar se o `POST /reservas/{id}/hospedes` aceita `CHECKIN_REALIZADO` numa reserva `CRIADA`.
- Confirmar se o filtro `codigo_reserva` casa exatamente (hoje só a página 1 é lida).
- Confirmar o formato do `400`, o caminho do no-show (`/no-show` ou `/noshow`), a ordem de `dados_hospedes` e o limite de 200 caracteres da senha.

### 3. [[ZenyHotelManager - Segurança, autenticação e autorização]]: complementa

- **Permissões novas do `fnrh`:**
  - `fnrh.settings.manage`: só o **Administrador**, **sem modelo de role** (o Administrador recebe todas as permissões e não pode constar em nenhum `RoleTemplate`). Cobre a configuração, o CPF solicitante por usuário e o `refresh` dos domínios.
  - `fnrh.domains.read` e `fnrh.submissions.read`: Gerente e Recepcionista.
  - Nenhuma é sensível. `fnrh.submissions.manage` virá na E08.
- **Regra nova: credencial de integração não vai em claro para a trilha.** O `username` da configuração da FNRH foi tirado do retrato de auditoria (commit `f8d7ea9`); a trilha da configuração não guarda senha, usuário nem CPF em claro. Vale para as próximas integrações (M7, M8).
- **Convenção, protegida por teste: a API não expõe `DELETE`.** O build barrou o `DELETE /fnrh/requesters/{userId}` do plano; a saída foi a desativação (`POST …/deactivate`), que apaga o dado sensível e mantém a linha. Itens que "saem" são desativados, não apagados.

### 4. [[ZenyHotelManager - Convenções de API]]: complementa

- **Kernel (`shared`):** `ErrorKind.BAD_GATEWAY` (502) e `ErrorKind.SERVICE_UNAVAILABLE` (503), com `BadGatewayException` e `ServiceUnavailableException`. Servem às integrações de saída (a FNRH os usa em `FNRH_REJECTED` e `FNRH_UNAVAILABLE`); o `DomainErrorsTest` cobre os casos 502/503.
- **`pattern` global do `Cpf` no contrato:** passou a **aceitar pontuação** (`123.456.789-09` além de só dígitos). Mudança de contrato sem `ERR` no oasdiff.
- **`pattern` do contrato precisa ser válido em ECMA-262** (sem `(?s)` e sem recursos que só o Java aceita), porque os SDKs dos clientes são gerados do `api/openapi.yaml`. A regex da senha da FNRH foi corrigida por isso (commit `d5614b6`); uma regex inválida em ECMAScript quebra os geradores.
- **Códigos de campo:** `FnrhFieldCodes` traz `NOT_IN_DOMAIN` e `INCONSISTENT`, além dos `FieldViolationCodes` do kernel (`REQUIRED`, `INVALID_VALUE`, `INVALID_FORMAT`), que valem quando um deles serve. Em erro de campo, nunca se devolve o valor.
- `PUT` de configuração com `If-Match`/`ETag` (como o `HotelController`): `428` sem o header, `412` com ETag velho.

### 5. [[ZenyHotelManager - Módulo guests]]: complementa

- **Lacuna do gênero `OUTRO` (D-E07-11, decisão (e)):** o `guests` guarda `OTHER` mas **não guarda a descrição do gênero** que a FNRH exige quando o gênero é `OUTRO`. O mapeamento não falseia o dado e a validação acusa `person.genderDescription`/`REQUIRED`; um hóspede `OTHER` não pode ser enviado. **Recomendação (pendente de decisão do usuário):** acrescentar a descrição ao perfil e ao `FnrhGuestData`, numa etapa própria ou na E08. Raça e gênero **não coletados** (nulos) também dão `REQUIRED`.
- **Menor só com RG não é aceito pela FNRH (decisão (f), nota B2 da E02):** a API v2.4 aceita só CPF ou passaporte; um menor brasileiro com apenas RG não pode ser registrado. O hotel precisa colher o CPF do menor. Não há alternativa técnica do nosso lado. Nesse caso a validação acusa `person.document`/`REQUIRED`.
- A regra mínima de documentos do check-in (H11) **não substitui** a validação local da FNRH (H21).

### 6. "Perguntas abertas" do hub: decisões do lote E07, a confirmar

O usuário delegou a escolha em 2026-11-04, pedindo a opção recomendada depois de uma avaliação crítica dos prós e contras. As decisões (a) a (j) abaixo foram tomadas pela opção recomendada, em nome dele, pelo orquestrador (2026-11-04 e 05). **Falta a confirmação dele.** Complementa as perguntas sobre as decisões das E13 (a–f) e E14 (a–c).

- (a) Fluxo de registro: reserva na criação, sem dado pessoal; pessoa e hóspede no check-in; check-out por `PATCH`; cancelamento só em `CRIADA`; no-show no M6. A favor: o link de pré-check-in chega cedo (RF-FNRH-04), o cancelamento chega ao Serpro e o fluxo segue os eventos de reserva da E08. Contra: mais chamadas e a reserva fica sincronizada desde a criação. Descartada: registro só no check-in.
- (b) `cpf_solicitante` só nas operações em que a API o exige.
- (c) URL base por ambiente escolhido na configuração, URLs em propriedade, senha de novo ao trocar de ambiente.
- (d) Municípios IBGE: lista oficial versionada no repositório, com fonte, data e SHA-256. Risco aceito: município criado depois do download é recusado até atualizar.
- (e) Gênero `OUTRO`: a validação acusa a falta da descrição, sem falsear o dado; recomendação de acrescentar a descrição ao `guests`. Raça e gênero não coletados dão `REQUIRED`.
- (f) Menor só com RG: o hotel precisa colher o CPF do menor.
- (g) Registro de integração sem texto livre.
- (h) CPF por usuário sem `DELETE`: desativação que apaga o CPF e mantém a linha.
- (i) **Limpar a credencial do Serpro:** hoje não há como apagá-la; recomendação: ação explícita de limpar, com trilha, **antes do M8**. Em aberto.
- (j) Correções extras depois da onda única da revisão final: dois despachos mínimos (controle C1 no saneador; `pattern` da senha válido em ECMA-262, mais U+2028 e U+2029), para deixar a `main` pronta para push com o build verde e o contrato válido para os geradores de SDK. Descartada: integrar com um teste vermelho como resíduo.

Também em aberto: **revisão humana da E07 e da E13** e a **decisão sobre a descrição do gênero** (item 5).

## Fatos

- `./gradlew build` em `d5614b6`: BUILD SUCCESSFUL in 6m 37s, **1712 testes, 0 falhas, 0 erros**.
- `.github/scripts/check-api-breaking.sh 360592f`: "Nenhuma mudança incompatível (nível ERR) em /api/v1".
- Scanner (cópia de `60080b7`, sem mudança de dependência depois): 415 + 74 pacotes, **0 Critical, 0 High**, 2 Medium e 3 Low, os mesmos da E14.
- Revisão de arquitetura do plano (`revisor-arquitetura`): **aprovado com notas, em 2 rodadas**. A inicial bloqueou com 1 Crítico e 8 Importantes (tipos em camadas proibidas, fluxo de registro indefinido, resultado incerto, texto livre em tabela *append-only*, entre outros); a rodada 1 abriu o Importante da autoinvocação no refresh.
- Revisão final (`revisor-seguranca`) sobre `360592f..60080b7`: **"With fixes"**, sem Crítico. I1 (troca do CPF solicitante sem rastro na trilha; corrigido com `@Version` e a versão no retrato) e I2 (`findReservationByCode` falhava aberto; agora falha fechado). Minors corrigidos na mesma onda: controle e formatação Unicode no saneador e nos rótulos, CHECK no `remote_id`, regex da senha, casos 502/503 no `DomainErrorsTest`. **Re-revisão restrita da onda: "all findings addressed", "Ready to merge? Yes"**; ela apontou dois Minors novos (regex da senha inválida em ECMA-262; U+2028/U+2029), corrigidos em `d5614b6`. Revisões por tarefa: todas "Approved".
- Levantamento da API: `docs/fnrh/api-fnrh-v2.4.md`, a partir do PDF oficial de 60 páginas, **SHA-256 `476849fdb56642cb2d98abd24bb817a18dd583f1ff43081386f382e470cbf235`**, baixado pelo link `@@display-file` do portal. A H6 se confirmou: a documentação basta para os stubs.
- Integridade dos testes: `check_test_integrity.py --base 360592f` aponta `[DEV_TESTE_DO_TESTADOR] 24399f9 SerproFnrhGatewayRound3Test.kt`: na correção 3 da Task 4 o desenvolvedor reescreveu um arquivo do testador e apagou 5 testes; o testador os restaurou idênticos em `45aa6ef` (`SerproFnrhGatewayRequestBuildTest.kt`), e as revisões da Task 4 e a final conferiram que nenhuma asserção ficou mais fraca. O apontamento se repete enquanto o commit estiver no histórico.
- Commits da etapa (branch `roadmap/m5-recepcao-fnrh`, a partir de `360592f`): início, levantamento, plano e correções da revisão de arquitetura `3558601`, `0185647`, `fa9091b`, `08903c4`; Task 1 `4405108`, `089b175`; Task 2 `fe551a2`, `da106b5`, `f8d7ea9`, `6f58f82`; Task 3 `52ae0b1`, `60438a4`, `0316330`, `b6b6d61`; Task 4 `68911e6`, `55f14ab`, `a7e685d`, `937e7de`, `2e4aaf5`, `0a011c8`, `24399f9`, `45aa6ef`, `514c5cb`; Task 5 `2bf1b90`, `47c0797`; Task 6 `c3f6b1c`, `4928795`, `40dacfc`, `e0724b3`, `531193e`; Task 7 `635b6c1`, `60080b7`; onda da revisão final `e8b7303`, `55e5a75`, `0584d47`, `d5614b6`; fechamento `bd75afc`.

## Decisão do usuário

- O usuário pediu a `main` local pronta para `git push origin main`; o push e a decisão sobre merge são dele.
- As decisões (a) a (j) acima **não** foram do usuário: foram tomadas pela opção recomendada, em nome dele (delegação de 2026-11-04).

## Origem

- Repositório `/home/caio/repos/ZenyHotelManager` (worktree `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap+m5-recepcao-fnrh`), branch `roadmap/m5-recepcao-fnrh`, commit `bd75afc` ("Conclui a E07 do M5 (módulo fnrh), preenche o handoff e corrige a ARCHITECTURE §12"), 2026-11-05.
- `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`: seção "E07 — Configuração, domínios e adaptador Serpro da FNRH" (handoff), "Decisões do lote E07" e a entrada de 2026-11-05 do "Histórico de revisões".
- `docs/superpowers/plans/2026-11-04-m5-recepcao-fnrh-e07.md`: "Decisões desta etapa" (D-E07-1 a 12), "Global Constraints" e as Tasks 1 a 7.
- `docs/fnrh/api-fnrh-v2.4.md`: levantamento da API v2.4.

## Por que registrar

O brain ainda não conhece o módulo `fnrh` e diz que a E07 é a próxima elegível. A E08 (envio por eventos) e a E09 (homologação) dependem do fluxo de registro decidido, da classificação de falhas, do saneador e do validador; o `Estado por marco` precisa refletir E07 concluída, e a nota de segurança e a de convenções de API ganharam regras novas (credencial fora da trilha, sem `DELETE`, `pattern` ECMA-262, 502/503).

## Limitações e incertezas

- **O comportamento real do Serpro só a E09 confirma.** Os stubs WireMock e o adaptador vêm da documentação v2.4 (PDF oficial); nenhuma chamada real foi feita e a E09 está bloqueada pela credencial (Q-12). Pontos já listados para confirmar nas "Notas para a E09".
- **O recurso do IBGE pode ficar defasado:** a lista é um instantâneo do download; município criado depois é recusado até o recurso ser atualizado à mão.
- Os fatos vêm do roadmap e do plano, conforme o pedido do orquestrador. Não reli o código nem o `docs/fnrh/api-fnrh-v2.4.md` por inteiro; nomes de classes, colunas e rótulos seguem o plano e o handoff (o plano pode ter ajustes feitos durante a execução que não aparecem no handoff, como nomes de colunas além das listadas).
- Detalhes do saneador depois da revisão final (Unicode `Cc`, formatação, U+2028/U+2029) vêm do handoff, que os descreve de forma resumida.
- A E07 está só na branch local; o estado em `origin/main` muda após o push do usuário. O build foi verificado em `d5614b6`; `bd75afc` só acrescenta documentação.
- Comandos, SHA-256 do PDF e contagens (1712 testes, 5.571 municípios) são os registrados na fonte; não os reproduzi.
- As migrações `V2026_11_04_1000` a `1030` foram alteradas no lugar; bancos locais antigos precisam ser recriados.
- Pendentes de confirmação do usuário: decisões (a) a (j), a revisão humana da E07 e da E13 e a decisão sobre a descrição do gênero. Caminhos de worktree dependem da máquina local.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Estado por marco]]
- [[ZenyHotelManager - Segurança, autenticação e autorização]]
- [[ZenyHotelManager - Convenções de API]]
- [[ZenyHotelManager - Módulo guests]]
- [[ZenyHotelManager - Hospedagem e recepção]] (lista das decisões de lotes anteriores do M5)
- [[ZenyHotelManager - Eventos e jobs]] (a E08 trará os primeiros listeners de produção dos eventos de reserva e o job de envio)
- [[ZenyHotelManager - Módulo notifications]] (modelo do adaptador FCM e do `PushDeliveryLog`; alerta de falha na E08)
