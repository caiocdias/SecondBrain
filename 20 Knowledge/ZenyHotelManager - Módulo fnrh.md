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
---
# ZenyHotelManager - Módulo fnrh

Referência técnica do projeto [[ZenyHotelManager]]. Integração com a FNRH Digital (Serpro/MTur), API v2.4. Estado: E07 concluída (configuração, domínios, porta e adaptador, validação local) e E15 concluída (descrição de gênero no envio); o envio por eventos é a E08 e a homologação real é a E09.

Texto das capturas de atualização publicadas no repositório, integrado sem resumo. Referências como "SPEC", "ARCHITECTURE §x", "RF-…", "RN-…", "Hn", "Q-NN", "D-E07-n" e "Rn" apontam para `docs/SPEC.md`, `docs/ARCHITECTURE.md`, `docs/roadmaps/` e `docs/superpowers/` do repositório. O levantamento da API está em `docs/fnrh/api-fnrh-v2.4.md`. As regras que a FNRH provou para toda integração estão em [[ZenyHotelManager - Eventos e jobs]]; as decisões do lote E07 e o que falta confirmar, em [[ZenyHotelManager - Estado por marco]].

**O comportamento real do Serpro só a E09 confirma.** Os stubs WireMock e o adaptador vêm da documentação v2.4 (PDF oficial); nenhuma chamada real foi feita e a E09 está bloqueada pela credencial (Q-12).

---

## Camada e dependências

- Camada "Integração governamental" (acima da Hospedagem). Pacote `com.zeny.hotel.fnrh`, com `FnrhModule.kt` na raiz.
- `allowedDependencies` hoje: `shared` e `guests` (D-E07-12: o payload não pede dado do hotel; a `HotelApi.profile()` fica para a E11). A **E08 acrescenta `reservations` e `notifications`**, já previstos na tabela da ARCHITECTURE §3.1.
- Nunca importa `iam`, `frontdesk` nem lê tabela de outro schema. `frontdesk` não pode chamar `fnrh` (camada acima): o `fnrh` reage a eventos de `reservations`. Há um teste do `fnrh` no `ModularityTest`, com as dependências exatas.

## Pacotes

- Raiz (API pública): `FnrhModule`, `FnrhPermissions`, `FnrhErrorCodes`, `FnrhFieldCodes` e `FnrhEnvironment` (`HOMOLOGATION`, `PRODUCTION`; fica na raiz porque a web o expõe).
- `domain`: modelo de dados da FNRH, regras de configuração (`FnrhSettings`), escolha do CPF solicitante (`RequesterCpfPolicy`), mapeador do hóspede (`FnrhPersonMapper`), validador local (`FnrhLocalValidator`), `FnrhFieldError`, `FnrhDomainCatalog` e `IbgeMunicipalities`. Sem Spring.
- `application`: casos de uso e portas (`FnrhGateway`, `FnrhConnectionSource`, `FnrhIntegrationLog`, `FnrhRequesterDirectory`), `FnrhSettingsService`, `FnrhRequestersService`, `FnrhDomainsService`, `FnrhDomainValuesWriter`, `FnrhStatusService`.
- `infrastructure`: adaptador `SerproFnrhGateway` (`RestClient` com `JdkClientHttpRequestFactory` e timeouts), `FnrhMessageSanitizer`, persistência, `JdbcFnrhIntegrationLog` (transação própria, `REQUIRES_NEW`, no modelo do `PushDeliveryLog` do `notifications`), `FnrhMetrics` (`MeterBinder`) e `FnrhProperties`.
- `web`: só controllers e DTOs. `@Tag("FNRH")`.
- **Toda chamada ao Serpro roda fora de transação do banco.**

## Configuração cifrada, por ambiente (D-E07-1)

- O administrador escolhe o **ambiente** (`HOMOLOGATION` ou `PRODUCTION`); as URLs ficam em propriedade: `zeny.fnrh.homologation-url` (padrão `https://hom-lowcode.serpro.gov.br/FNRH_API/rest/v2`) e `zeny.fnrh.production-url` (padrão `https://fnrh.turismo.serpro.gov.br/FNRH_API/rest/v2`), mais `zeny.fnrh.connect-timeout` (5 s) e `zeny.fnrh.read-timeout` (20 s). Os testes apontam as duas URLs para o WireMock.
- **Trocar de ambiente exige informar a senha de novo** (`422 FNRH_PASSWORD_REQUIRED_FOR_ENVIRONMENT_CHANGE`), para a credencial de um ambiente não ir para o outro. Descartadas: URL livre na configuração (a credencial poderia ir para qualquer host) e propriedade única (cada troca pediria nova implantação).
- Usuário, senha e CPF padrão ficam cifrados (`FieldCipher`/`EncryptedStringConverter`). A tabela `fnrh.settings` tem uma linha semente (versão 0, desligada, homologação) para o primeiro `PUT` ter `ETag`.
- Regras do domínio: `password` nula mantém a atual; ligar (`enabled = true`) sem usuário, senha ou CPF padrão dá `422 FNRH_SETTINGS_INCOMPLETE`. Sem configuração (ou desligada), `FnrhConnectionSource.current()` devolve `null` e nada é enviado.
- A senha nunca volta na API; o CPF sai mascarado (`***.***.***-NN`). A trilha do `PUT` não guarda senha, CPF nem o `username` (ver [[ZenyHotelManager - Segurança, autenticação e autorização]]).
- **Limpar a credencial:** no código da E07 não há como apagá-la; ao desligar a integração, ela continua cifrada no banco. Passa a ter etapa, a M5 E16 (decisão do usuário, R6), pré-requisito da E09, ainda `#pendente`: ação com trilha, `If-Match` e `fnrh.settings.manage`, sem `DELETE`, que apaga usuário, senha e CPF padrão e desliga a integração; religar sem nova credencial dá `422 FNRH_SETTINGS_INCOMPLETE`.

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

- **Fluxo decidido (D-E07-2, decisão (a)):** a reserva é registrada **na criação**, sem dado pessoal. No check-in entram a pessoa e o hóspede (`CHECKIN_REALIZADO`); o check-out sai por `PATCH`; o cancelamento só vale em `CRIADA`. Descartada a alternativa "registro só no check-in" (`POST /hospedagem/registrar`): o cancelamento nunca chegaria ao Serpro e o link de pré-check-in não serviria.
- Fora da porta: `hospedagem/registrar`, pré-check-in de balcão, fichas, operações em lote, `DELETE /reservas`, `PATCH …/checkin` (o hóspede já entra com check-in) e o **no-show**, porque o caminho individual diverge no PDF. O no-show vai pela M6 E14, com operação nova na porta; o gate M8 E13 pede o no-show executado na homologação ou registrado como risco aceito pelo usuário.
- Campos da reserva (`FnrhReservationData`): `numero_reserva` = `Reservation.code` (nunca o código do `Booking`); `numero_reserva_ota` = `Booking.externalId`; com OTA, `origem_reserva_id = OTA`, senão `MEIOHOSPEDAGEM`; `minors` sai da **data de nascimento** (menor de 18 anos na entrada), não de `childAges`.
- Instantes enviados ao Serpro: UTC com milissegundos e `Z` (`2026-02-10T15:00:00.000Z`), tanto no JSON quanto no `text/plain`.
- **`cpf_solicitante` só onde a API exige (D-E07-9, decisão (b)):** `POST /pessoas`, `GET /pessoas/documento/…` e `POST /hospedagem/registrar`; nesta porta, só `registerPerson`. O roadmap supunha o header em toda chamada; a fonte oficial prevalece. Consequência: o `performedBy` só pesa no registro da pessoa, no check-in. A ARCHITECTURE §12 foi corrigida nesse ponto no fechamento.
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
- Métricas por `MeterBinder`, que aparecem em `/actuator/prometheus`: `zeny_fnrh_calls_total` (tags `operation`, `outcome`, `environment`), `zeny_fnrh_last_success_seconds`, `zeny_fnrh_last_failure_seconds` (`NaN` sem registro) e `zeny_fnrh_configured` (0 ou 1). **Nenhum `HealthIndicator`**: a readiness não depende da FNRH (`ActuatorExposureTest` intacto, H22). A E08 acrescentará a métrica de pendentes.

## Domínios semeados e refresh tudo-ou-nada (D-E07-5)

- Tabela `fnrh.domain_value (domain, code, label, refreshed_at)`, chave `(domain, code)`. A migração **semeia** todos os `id` e `label` do levantamento da v2.4, então o cache nunca começa vazio (descartado o cache vazio até o primeiro `refresh`, que deixaria toda submissão inválida).
- Dez domínios: `transport-modes`, `travel-reasons`, `guest-statuses`, `genders`, `disability-options`, `races`, `disability-types`, `document-types`, `booking-statuses`, `record-statuses` (kebab-case na URL; nome desconhecido dá `404 FNRH_DOMAIN_NOT_FOUND`).
- `POST /api/v1/fnrh/domains/refresh`: o `FnrhDomainsService`, sem transação, confere a permissão e busca os 10 domínios **fora de transação**; depois chama **outro bean**, `FnrhDomainValuesWriter`, cujo método `@Audited @Transactional` só grava a substituição (num bean separado porque a autoinvocação pularia o proxy, e com ele a transação e a trilha; foi o Importante aberto na rodada 1 da revisão de arquitetura). **Se qualquer busca falhar, nada muda.** Resposta com a contagem por domínio. Mapeamento de erros: `NOT_CONFIGURED` → `422 FNRH_NOT_CONFIGURED`; `UNAUTHORIZED`/`FORBIDDEN` → `422 FNRH_CREDENTIALS_REJECTED`; temporárias → `503 FNRH_UNAVAILABLE`; `VALIDATION`/`NOT_FOUND` → `502 FNRH_REJECTED`.
- A web nunca devolve o tipo de domínio; a application o mapeia.

## Validador local e lista do IBGE (RF-FNRH-06, H21, D-E07-3, D-E07-10, D-E07-11)

- Fica em `domain`, sem Spring, junto com o mapeador e a lista do IBGE; **a E08 os monta**.
- `FnrhLocalValidator.validate(person, guest, arrival, responsibleKnown)` devolve `FnrhFieldError(field, code)`, **nunca o valor**. Códigos: `REQUIRED`, `INVALID_VALUE`, `NOT_IN_DOMAIN`, `INCONSISTENT`. Regras: nome e documento obrigatórios (CPF passa pelo `Cpf`); nacionalidade e residência ISO 3166-1 alpha-2 (`Locale.getISOCountries()`, D-E07-4); nascimento, gênero e raça obrigatórios; gênero, raça, opção e tipo de deficiência, motivo de viagem e meio de transporte no catálogo; `OUTRO` exige descrição; deficiência `SIM` exige tipo; com residência `BR`, município obrigatório e na lista do IBGE, UF obrigatória e igual à do município (`INCONSISTENT`), CEP de 8 dígitos quando informado (e então logradouro, número e bairro); residência fora do `BR` não exige município nem UF; menor de 18 anos na data de entrada sem responsável gera `guest.responsibleGuestId`/`REQUIRED`.
- Mapeador: documento = CPF se houver, senão passaporte (os outros tipos, como RG, não entram); gênero e raça mapeados aos códigos da API; raça ou gênero **nulos** significam "não coletado" e a validação acusa `REQUIRED` (D-E07-10); só `NOT_DECLARED`/`NOT_INFORMED` viram `NAOINFORMAR`/`NAOINFORMADO`. O `FnrhGuestData` tem `genderDescription` e o `FnrhPersonMapper` a envia como `GeneroDescricao` somente com `OUTRO` (M5 E15; [[ZenyHotelManager - Módulo guests]]).
- **Lista do IBGE (decisão (d)):** recurso versionado `src/main/resources/fnrh/ibge-municipios.csv` (5.571 municípios; `codigo;uf`), com o cabeçalho trazendo a fonte (`https://servicodados.ibge.gov.br/api/v1/localidades/municipios`), a data do download e o SHA-256 do JSON. **Risco aceito: um município criado depois do download é recusado até o recurso ser atualizado.** A API da FNRH não tem endpoint de municípios. Descartada a validação só de formato.
- A validação local recebe a residência nula sem erro e não confere o `checkedOutAt`: a E08 decide.

## Endpoints e permissões

| Endpoint | Permissão |
|---|---|
| `GET /api/v1/fnrh/settings`, `PUT /api/v1/fnrh/settings` (`If-Match` obrigatório; `428` sem ele, `412` com ETag velho) | `fnrh.settings.manage` |
| `GET /api/v1/fnrh/requesters`, `PUT /api/v1/fnrh/requesters/{userId}`, `POST /api/v1/fnrh/requesters/{userId}/deactivate` (o CPF nunca vai na URL) | `fnrh.settings.manage` |
| `POST /api/v1/fnrh/domains/refresh` | `fnrh.settings.manage` |
| `GET /api/v1/fnrh/domains/{domain}` | `fnrh.domains.read` |
| `GET /api/v1/fnrh/status` | `fnrh.submissions.read` |

- Nenhuma permissão é sensível. `fnrh.submissions.manage` nasce na E08 (retry da fila e destinatário do alerta de falha). Códigos de problema em `FnrhErrorCodes`: `FNRH_SETTINGS_INCOMPLETE`, `FNRH_PASSWORD_REQUIRED_FOR_ENVIRONMENT_CHANGE`, `FNRH_REQUESTER_NOT_FOUND`, `FNRH_DOMAIN_NOT_FOUND`, `FNRH_NOT_CONFIGURED`, `FNRH_CREDENTIALS_REJECTED`, `FNRH_UNAVAILABLE`, `FNRH_REJECTED`.
- Migrações: `V2026_11_04_1000` a `V2026_11_04_1030` na pasta `fnrh/` (settings com GRANT, requesters, integration_call, domain_value). **Foram alteradas no lugar durante a etapa porque nunca saíram da branch:** um banco local de desenvolvimento que tenha aplicado uma versão anterior precisa ser recriado (`docker compose -f docker/compose.yaml down -v`). A próxima migração do projeto precisa de timestamp posterior a elas.

## Dados que nunca saem

- Senha, número de documento, raça/cor, deficiência, nome, e-mail e telefone não entram em log, trilha, resposta, métrica nem no registro de integração. Todo tipo que os carrega sobrescreve o `toString` (`FnrhPersonData`, `FnrhGuest`, `FnrhDocument`, `FnrhConnection`, `FnrhProperties`). **`Cpf.toString()` devolve os dígitos:** nunca interpole `Cpf` em log, mensagem nem `toString`.

## Notas para a E08

- A porta não tem operação para desfazer o check-in. O cancelamento só vale com a reserva em `CRIADA`. Os ids remotos dependem do ambiente.
- `UNKNOWN_OUTCOME`: concilia-se antes de repetir, por `findReservationByCode` no registro da reserva e por `GET /reservas/{id}/hospedes` na inclusão do hóspede. No `registerPerson`, falta decidir entre aceitar o risco de pessoa duplicada e conciliar por `GET /pessoas/documento/…`; a escolha fica no handoff da E08.
- `UNAVAILABLE` é temporário: **limite as tentativas** (um erro de programação no envio também cai nele). Um 503 dentro de handler offline viraria recusa permanente.
- O responsável entra antes do menor (o `responsavel_id` precisa existir). `minors` sai da data de nascimento.
- A E08 monta o validador, o mapeador e a lista do IBGE (todos em `domain`, sem Spring); a lista de eventos que geram envio e o limite de tentativas são decisões abertas dela.
- O nome previsto da view é `fnrh.report_submissions`, não `report_pending_submissions`.
- A E08 depende da E15 e passa a ter revisão humana, por fixar o padrão de envio que M7 e M8 repetem.

## Notas para a E09

- Confirmar se o `POST /reservas/{id}/hospedes` aceita `CHECKIN_REALIZADO` numa reserva `CRIADA`.
- Confirmar se o filtro `codigo_reserva` casa exatamente (hoje só a página 1 é lida).
- Confirmar o limite real e o eco de `GeneroDescricao` na homologação (M5 E15).
- Confirmar o formato do `400`, o caminho do no-show (`/no-show` ou `/noshow`), a ordem de `dados_hospedes` e o limite de 200 caracteres da senha.
- A E09 segue `#bloqueada` (Q-12) e depende de E08 e E16. A homologação continua fora do gate do M5 e passa a ser cobrada pelo gate de inauguração (M8 E13).

## Limitações

- Os fatos vêm do roadmap e do plano da E07; a captura não releu o código nem `docs/fnrh/api-fnrh-v2.4.md` por inteiro. Nomes de classes, colunas e rótulos seguem o plano e o handoff, e o plano pode ter ajustes feitos na execução que não aparecem no handoff.
- Os detalhes do saneador depois da revisão final vêm do handoff, que os descreve de forma resumida.
- A lista do IBGE é um instantâneo do download.

---

## Proveniência

- 2026-11-09 — [[2026-11-05 - ZenyHotelManager - atualização m5-recepcao-fnrh E07 - 9f02405c]] (capture_id: 9f02405c-a73b-44f0-8f8c-5fb75860aa05): texto proposto para o módulo (item 2 da captura), integrado sem resumo, com abertura sugerida pela captura; o "Limite conhecido" da credencial foi substituído conforme a captura c889f886.
- 2026-11-09 — [[2026-11-06 - ZenyHotelManager - atualização revisão de arquitetura dos roadmaps - c889f886]] (capture_id: c889f886-0719-4f28-984e-f2ef23ed9520): M5 E16 (limpar credencial), M5 E15 no mapeador, conciliação e view da E08, SPEC §8.2.17 e no-show pela M6 E14.
- 2026-11-10 — [[2026-11-10 - ZenyHotelManager - atualização m5-recepcao-fnrh E15 - a22890e7]] (capture_id: a22890e7-e6b1-4e99-97d7-747bfcdd5788): frase da E15 no mapeador substituída pelo envio de `GeneroDescricao`; saneador (`8d6203a`, D-E15-6) e nota para a E09 complementados.
