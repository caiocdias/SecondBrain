---
type: capture
status: archived
created: 2026-11-11
capture_id: 8df87866-4285-4e24-8878-0fab70c9436c
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E08

## Conteúdo capturado

Captura de fechamento da etapa M5 E08 (envio assíncrono e pendências da FNRH), concluída em 2026-11-11. O texto abaixo vem do handoff da E08, das decisões D-E08-1 a 17 do plano, da SPEC §8.2.17, da ARCHITECTURE §12 e §13, do README, das migrações e de trechos do código da branch. Está organizado por nota de tema. Em cada nota, a captura indica se o texto **substitui** ou **complementa** a seção e traz o texto pronto para colar. Os rótulos "Decisão" marcam o que o orquestrador decidiu pela opção recomendada, em nome do usuário e **sem confirmação dele**.

---

### 1. `ZenyHotelManager - Módulo fnrh`

**1.1 Substitui** a frase "Estado:" da abertura:

> Estado: E07 concluída (configuração, domínios, porta e adaptador, validação local), E15 concluída (descrição de gênero no envio) e E08 concluída (envio assíncrono por eventos, fila de pendências, alerta, métrica e view). A homologação real é a E09, ainda `#bloqueada` (Q-12).

**1.2 Substitui**, em "Camada e dependências", o item "`allowedDependencies` hoje":

> - `allowedDependencies`: `shared`, `guests`, `reservations` e `notifications` (as duas últimas desde a E08, D-E08-14, já previstas na ARCHITECTURE §3.1). A `HotelApi.profile()` fica para a E11.

**1.3 Complementa** "Pacotes" (classes novas da E08):

> - `domain`: `FnrhSubmission` (entidade com `FnrhOperation`, `FnrhSubmissionStatus` e `FnrhSubmissionFailure`) e `FnrhRetryPolicy`.
> - `application`: `FnrhSubmissionListeners`, `FnrhSubmissionSender` (núcleo do envio, que recusa rodar dentro de transação), `FnrhCheckInStep`, `FnrhCheckOutSteps`, `FnrhSubmissionRecorder` (grava o resultado com `@Audited @Transactional`, num bean à parte), `FnrhSubmissionsService` (fila, retry e dismiss) e as portas `FnrhSubmissionStore` e `FnrhRemoteIds`.
> - `infrastructure`: `FnrhSubmissionJob`, `FnrhSubmissionPersistence`, `FnrhSubmissionConfiguration`, `FnrhSubmissionMetrics` e `SerproFnrhLookups` (as consultas de conciliação).
> - `web`: `FnrhSubmissionsController`.

**1.4 Complementa** a tabela "Porta `FnrhGateway` e operações" com duas linhas (consultas de conciliação da E08, D-E08-6):

> | `listReservationGuests` | `GET /reservas/{id}/hospedes` (lê só `dados[].hospede.hospede_id` e `.pessoa_id`; a resposta traz dado pessoal) |
> | `findPersonByDocument` | `GET /pessoas/documento/{tipo}/{numero}` (com `cpf_solicitante`; lê só `dados.id`; o documento vai no caminho e a URL nunca entra no log) |

E **substitui**, no item "`cpf_solicitante` só onde a API exige", a frase "nesta porta, só `registerPerson`" por: "nesta porta, `registerPerson` e `findPersonByDocument`".

**1.5 Substitui** a seção inteira "Notas para a E08" por esta seção nova:

> ## Envio assíncrono (M5 E08)
>
> **Submissão por evento (D-E08-1 e 2).** Cada evento grava **uma** `FnrhSubmission`, idempotente pela chave única `(reservation_id, operation, event_key)`, em que `event_key` é o tipo do evento com a `version` dele (`created` no `ReservationCreated`). Mapeamento:
>
> | Evento | Operação |
> |---|---|
> | `ReservationCreated` | `REGISTER_RESERVATION` |
> | `ReservationChanged`, `ReservationConfirmed`, `ReservationReactivated` | `UPDATE_RESERVATION` (`PUT` com os dados atuais, idempotente) |
> | `ReservationCancelled` | `CANCEL_RESERVATION` |
> | `GuestCheckedIn` | `CHECK_IN` (todos os hóspedes da reserva; progresso por hóspede em `fnrh.remote_guest`) |
> | `GuestCheckInUndone` | `UNDO_CHECK_IN` |
> | `GuestCheckedOut` | `CHECK_OUT` |
>
> A pré-reserva (`PROVISIONAL`) e a reserva sem documentos também são registradas, porque o registro não leva dado pessoal. A expiração vira cancelamento no MTur. `RoomMoved` não gera envio, porque a API v2.4 não tem UH. O no-show fica para a M6 E14 (H15).
>
> **Ordem causal (D-E08-3).** Cada submissão guarda `causal_version` (a `version` da reserva no evento; `0` no `ReservationCreated`) e o posto da operação: `REGISTER_RESERVATION` 0 < `UPDATE_RESERVATION` 1 < `CANCEL_RESERVATION` 2 < `CHECK_IN` 3 < `UNDO_CHECK_IN` 4 < `CHECK_OUT` 5. Só anda a cabeça da reserva: a de menor `(causal_version, posto, sequence)` entre as `PENDING`, `FAILED` e `INVALID`, e só se estiver `PENDING` e vencida. `FAILED` e `INVALID` seguram as seguintes até o `retry` ou o `dismiss`. O `sequence` (identidade) é só o cursor da API. Os passos agem sobre o **estado atual** da reserva e dos ids remotos, não sobre a ordem de chegada dos eventos (D-E08-9):
>
> - registro de reserva já cancelada (ou no-show) sem id remoto, e cancelamento sem id remoto: `SENT` sem chamada;
> - `UPDATE_RESERVATION` sem id remoto: registra, sem o `PUT`;
> - `UPDATE_RESERVATION` com a reserva remota cancelada por nós: `FAILED` com `REMOTE_CANCELLED` e alerta, sem chamada (o `numero_reserva` é único e a API não reativa);
> - `CHECK_OUT` de reserva com hóspedes com check-in feito e nenhum deles no Serpro roda antes o check-in deles e nunca fica `SENT` vazio.
>
> **Situações:** `PENDING`, `SENT`, `FAILED`, `INVALID`, `CANCELLED` e `DISMISSED`. `status`, `operation` e `lastFailure` são `x-extensible-enum` nas respostas.
>
> **Retry (D-E08-4).** Falha temporária (`SERVER_ERROR`, `UNAVAILABLE`, `UNKNOWN_OUTCOME` e `INTERNAL_ERROR`) reagenda com espera `1 min × 2^(n−1)` até `1 h` (n = tentativas feitas). Na **8ª** tentativa com falha, a submissão vira `FAILED`; são cerca de 2 h no total. Falha permanente (`VALIDATION`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`) vira `FAILED` na hora. Propriedades `zeny.fnrh.submissions.*`: `interval` (`PT1M`), `initial-delay` (`PT1M`), `batch-size` (50), `max-attempts` (8), `initial-backoff` (`PT1M`), `max-backoff` (`PT1H`). Exceção que não é `FnrhGatewayException` conta como `INTERNAL_ERROR` temporária, com log só de ids. Uma submissão envenenada não para o lote (D-E08-17).
>
> **Sem configuração (D-E08-5).** Com `FnrhConnectionSource.current()` nulo, nada sai e **nenhuma tentativa é gasta**: as submissões ficam `PENDING`. Ao ligar, todo o acumulado sai no ambiente escolhido, inclusive estadias antigas. O corte ou a limpeza fica para decidir na E09 ou na M8 E13.
>
> **Escrita em curso (D-E08-15).** Antes de cada chamada que cria recurso (`POST /reservas`, `POST /pessoas`, `POST /reservas/{id}/hospedes`), a submissão grava `in_flight = true` em transação própria (`FnrhSubmissionStore.markInFlight`, `REQUIRES_NEW`). O id remoto gravado depois (`FnrhRemoteIds.save*`, também `REQUIRES_NEW`) limpa a marca na mesma transação. A marca vale para a reserva inteira: `anyInFlight(reservationId)` olha todas as submissões dela, inclusive `DISMISSED` e `CANCELLED`. Outra falha e o `retry` preservam a marca. A tentativa que encontra a marca concilia antes de repetir.
>
> **Conciliação (D-E08-6 e 7).**
>
> - Reserva: `findReservationByCode` quando havia escrita em curso.
> - Hóspede: `listReservationGuests`, casando pelo `pessoa_id`, quando havia escrita em curso.
> - Pessoa: **sempre** `findPersonByDocument` antes de criar, quando o hóspede não tem `person_id` conhecido no ambiente. Com `dados.id` presente, reaproveita a pessoa; ausente ou `404`, faz `POST /pessoas`. Corpo ambíguo ou incompleto dá `UNKNOWN_OUTCOME` (falha fechado). Esta é a escolha do `registerPerson` que a E07 deixou para a E08.
> - `PUT`, cancelamento e `PATCH` de check-out são repetidos, porque não criam recurso. Se a repetição de um cancelamento der `VALIDATION`, a submissão fica `FAILED` com alerta.
> - **Pessoa já conhecida:** o hóspede que já tem `person_id` no mesmo ambiente, de qualquer reserva (`FnrhRemoteIds.knownPerson`), é reaproveitado sem consulta nem `POST`. O hóspede é identificado pelo id do sobrevivente (`GuestsApi.identification(id).id`). Um hóspede cujo `person_id` já está entre os `remote_guest` da reserva é pulado, para uma mesclagem não duplicar a pessoa.
> - A linha do hóspede recorrente em `remote_guest` é gravada **antes** do `POST` do hóspede (I-1 da revisão final, `1df90ff`). O cancelamento sem id remoto concilia quando há escrita em curso na reserva (I-2, `4d018cd`).
>
> **Desfazer check-in e reativação (D-E08-8 e 9).** A API não tem as duas operações.
>
> - Ao gravar o `UNDO_CHECK_IN`, o listener cancela (`CANCELLED`, por `cancelIfIdle`) os `CHECK_IN` da reserva não resolvidos, sem escrita em curso e sem hóspede no Serpro.
> - No envio, sem hóspede da reserva no Serpro, o `UNDO_CHECK_IN` fica `SENT` sem chamada. Com hóspede no Serpro, fica `FAILED` com `NO_REMOTE_OPERATION` e alerta: a correção é manual, no portal, seguida de `dismiss`.
> - Um novo check-in pula os hóspedes já no Serpro. Um `CHECK_IN` que sobrevive ao desfazer não cria nada novo: só concilia, grava os ids do que já existe e termina `SENT`. O `UNDO_CHECK_IN` superado por um novo check-in fica `SENT` sem chamada.
>
> **Validação local (D-E08-10).**
>
> - Roda só no `CHECK_IN` e no check-in que o `CHECK_OUT` roda antes. Todos os hóspedes são validados antes de qualquer chamada.
> - Com erro, a submissão fica `INVALID`, com os erros por hóspede, campo e código em `fnrh.submission_error`, **sem o valor**, e alerta.
> - Os campos da RN-19 (raça/cor, opção e tipo de deficiência) são neutralizados como `person.sensitiveData`/`INVALID_VALUE`, um por hóspede (I-3, `cf9d8e8`). O operador não sabe qual dos campos falta.
> - A residência nula continua aceita, e o `checkedOutAt` não é validado: o check-out usa `StayGuestSummary.checkedOutAt` ou, sem ele, o instante do evento.
> - Cada tentativa do `CHECK_IN` revalida todos os hóspedes, inclusive os já enviados (decisão E08 (m)).
> - Menor sai depois do responsável e leva o `responsavel_id` dele. Menor cujo responsável é outro menor listado depois dá `FAILED` (`INTERNAL_ERROR`) com alerta, nunca `responsavel_id` errado. Reserva de OTA envia `BookingSummary.externalId`.
>
> **Alerta (D-E08-11).** Cada passagem a `FAILED` ou `INVALID` chama `NotificationsApi.notify(INTEGRATION_FAILURE, "Falha no envio à FNRH", "Reserva <código>: <operação> — <falhou | dados inválidos>", withPermission(fnrh.submissions.manage))`, só com o código da reserva e rótulos fixos. O alerta sai **depois do commit, em transação própria**. Se o `notifications` falhar, o alerta se perde, mas o resultado da submissão fica gravado.
>
> **Resultado e trilha.** O `FnrhSubmissionRecorder` grava cada resultado com `@Audited` (`fnrh.submission.send`, ator sistema; retrato só com id, operação, situação, tentativas e última falha). Ele só aplica o resultado a submissão `PENDING`. Numa submissão em qualquer outra situação (por exemplo, cancelada pelo listener do desfazer durante o envio), não grava, não alerta e só registra no log.
>
> **Ids remotos por ambiente (D-E08-13).** `fnrh.remote_reservation` e `fnrh.remote_guest` têm `environment` na chave. Trocar de ambiente faz a próxima submissão registrar de novo. O **link de pré-check-in** fica em `remote_reservation`, cifrado (`FieldCipher`), sem exposição na API. A E11 pode usá-lo, e ele é mais um valor para a re-cifragem da M8 E15.
>
> **Endpoints (D-E08-12 e 16):**
>
> | Endpoint | Permissão |
> |---|---|
> | `GET /api/v1/fnrh/submissions?status=…` (cursor pelo `sequence`; sem dado de hóspede além de ids, código da reserva e erros sem valor) | `fnrh.submissions.read` |
> | `POST /api/v1/fnrh/submissions/{id}/retry` (só `FAILED`/`INVALID`; zera as tentativas e os erros e preserva a escrita em curso; sem `@Idempotent`, e repetir dá `409`) | `fnrh.submissions.manage` |
> | `POST /api/v1/fnrh/submissions/{id}/dismiss` (só `FAILED`/`INVALID`; leva a `DISMISSED`, terminal, que não segura a fila) | `fnrh.submissions.manage` |
>
> Códigos novos: `404 FNRH_SUBMISSION_NOT_FOUND`, `409 FNRH_SUBMISSION_NOT_RETRYABLE`, `409 FNRH_SUBMISSION_NOT_DISMISSABLE`. Trilha: `fnrh.submission.retry` e `fnrh.submission.dismiss`.
>
> **Job, métrica e view.** O job `fnrh-submissions-send` está descrito em [[ZenyHotelManager - Eventos e jobs]]. O gauge `zeny_fnrh_submissions{status}` está em [[ZenyHotelManager - Docker, observabilidade e CI]]. As tabelas e a view `fnrh.report_submissions` estão em [[ZenyHotelManager - Schemas, migrações e views de relatório]].
>
> **Armadilhas para quem mexer:**
>
> - O recorder só aplica resultado a `PENDING`. Uma transição nova que tire a submissão de `PENDING` durante o envio faz o resultado sumir (só o log registra).
> - `cancelIfIdle` cancela num `UPDATE` condicional: se o job marcou `in_flight` entre a leitura e o cancelamento, não cancela. Não troque por ler e depois salvar.
> - `in_flight` só muda pela store (`markInFlight`) e pelos `FnrhRemoteIds.save*`, em transação própria. Nunca grave a marca pela entidade na transação do chamador, que pode desfazer.
> - A lista `SENSITIVE_FIELDS` do `FnrhCheckInStep` repete a do validador. Um campo sensível novo no validador precisa entrar nela (o ideal é uma constante compartilhada ou um teste).
> - Os testes chamam `dismiss(now)` por extensões só de teste (`FnrhSubmissionDismissCompat.kt`). Migre os testes e apague essas extensões numa limpeza.
> - A marca de escrita em curso de uma submissão `DISMISSED` fica ligada para sempre e custa um `GET` a mais por registro da reserva.
> - Na gravação da linha do hóspede recorrente (I-1), a marca de escrita em curso é limpa antes do `POST` do hóspede. É a mesma janela estreita que o `registerPerson` já tinha.
> - As propriedades `zeny.fnrh.submissions.*` não validam limites (zero ou negativo; M-4).
> - Trocar de ambiente com submissões em execução pode gravar um id no ambiente errado (M-3). Ao trocar, drene ou pause o job (E16 ou M8 E13).
> - O gauge roda um `GROUP BY` a cada raspagem. `FnrhSubmissionJobAttackTest` usa `sleep` fixo e pode ficar intermitente em CI lenta.
>
> **Notas para as próximas etapas:**
>
> - E09: confirmar `dados.id` na consulta por documento, o `PUT` numa reserva `EM_ANDAMENTO`, o `POST /pessoas` com documento repetido, se o `GET /reservas` devolve o link de pré-check-in (nulo numa reserva conciliada), se o `PATCH` de check-out repetido é aceito (M-6), se um `404` por rota errada se distingue de pessoa ausente e os timeouts de 100 ms dos testes do adaptador.
> - E09 e M8 E13: decidir corte ou limpeza do acumulado antes de ligar em homologação (D-E08-5).
> - E16 ou M8 E13: drenar ou pausar o job na troca de ambiente (M-3).
> - M6 E14 (no-show): acrescentar a operação na porta, `markNoShow` publicando o evento e o listener gravando `NO_SHOW` com posto próprio na ordem causal. Hoje o registro e a atualização de reserva no-show sem id remoto ficam `SENT` sem chamada.
> - M6 (fechamento): as pendências vêm de `fnrh.report_submissions`. `DISMISSED` não segura a fila.
> - Manutenção do `fnrh`: validar só os hóspedes ainda não enviados (decisão E08 (m)).

**1.6 Substitui**, em "Validador local e lista do IBGE", a frase "A validação local recebe a residência nula sem erro e não confere o `checkedOutAt`: a E08 decide." por: "A E08 manteve a residência nula aceita e não valida o `checkedOutAt` (D-E08-10; ver 'Envio assíncrono')." E, no mesmo bloco, troca "**a E08 os monta**" por "montados pela E08 no `FnrhCheckInStep`".

**1.7 Substitui**, em "Status e métricas", a frase "A E08 acrescentará a métrica de pendentes." por: "Desde a E08, o gauge `zeny_fnrh_submissions{status}` (`pending`, `failed`, `invalid`), lido da fila a cada raspagem (`NaN` se a leitura falhar)."

**1.8 Complementa** "Endpoints e permissões": as três linhas de `/api/v1/fnrh/submissions` (tabela acima). Também **substitui** "`fnrh.submissions.manage` nasce na E08 (retry da fila e destinatário do alerta de falha)" por: "`fnrh.submissions.manage` (E08, não sensível, só o Gerente): retry, dismiss e destinatário do alerta de falha." E acrescenta aos códigos de problema `FNRH_SUBMISSION_NOT_FOUND`, `FNRH_SUBMISSION_NOT_RETRYABLE` e `FNRH_SUBMISSION_NOT_DISMISSABLE`. No item das migrações, acrescenta `V2026_11_10_1000__create_fnrh_submissions.sql` e `V2026_11_10_1100__create_fnrh_report_views.sql`.

**1.9 Complementa** "Notas para a E09" com os itens da E09 listados em "Notas para as próximas etapas" acima.

**1.10 Complementa** "Dados que nunca saem": "O texto do alerta, a trilha da submissão, a view e os erros de validação não levam nome, documento, raça/cor nem deficiência; os nomes dos campos sensíveis também saíram dos erros (I-3). `FnrhRemoteReservation.toString()` omite o link de pré-check-in. As respostas das consultas do Serpro trazem dado pessoal, mas o adaptador lê só os ids."

---

### 2. `ZenyHotelManager - Eventos e jobs`

**Complementa** "Atualizações por capturas" com uma subseção nova:

> ### Primeiros consumidores dos eventos de reserva e hospedagem e job do envio à FNRH (M5 E08, 2026-11-11)
>
> - **`FnrhSubmissionListeners`** (`fnrh`, M5 E08) são os primeiros consumidores de produção de `ReservationCreated`, `ReservationChanged`, `ReservationConfirmed`, `ReservationReactivated` e `ReservationCancelled` (M4) e de `GuestCheckedIn`, `GuestCheckInUndone` e `GuestCheckedOut` (M5 E01). São 8 métodos `@ApplicationModuleListener`, e o outbox passa a gravar essas publicações. Cada um **só grava** a `FnrhSubmission`, nunca envia. São idempotentes pela chave `(reservation_id, operation, event_key)`, com `INSERT … ON CONFLICT DO NOTHING`: a reentrega, inclusive fora de ordem ou com a submissão já `SENT`, não grava outra. A ordem entre eles não importa, porque a fila ordena pela versão causal. `RoomMoved` não tem listener no `fnrh`; `AvailabilityChanged`, `RatesChanged` e `RestrictionsChanged` seguem sem consumidor de produção (M8).
> - **Job `FnrhSubmissionJob`** (ShedLock `fnrh-submissions-send`, a cada `zeny.fnrh.submissions.interval`, 1 min, depois de 1 min do boot): envia as cabeças vencidas da fila (até `batch-size`, 50) pelo `FnrhSubmissionSender`, que não é `@Transactional` e chama o Serpro fora de transação. O resultado é gravado pelo `FnrhSubmissionRecorder` (`@Audited`, ator sistema). `lockAtMostFor = PT1H` (decisão E08 (k)), porque uma execução pode levar muito mais que os 10 min dos outros jobs (50 submissões, várias chamadas de até 25 s). Custo: uma instância que morre com a trava atrasa o envio em até 1 h. Sem configuração da FNRH, não faz nada.
> - **Testes:** `FNRH_SEND_DEFERRED` (`zeny.fnrh.submissions.initial-delay=PT24H`) no `@IntegrationTest` adia o job, e os testes chamam o envio direto, só para a própria reserva (`sendDueFor`). O `InventoryListenersQuiescence` passou a esperar também as publicações dos `FnrhSubmissionListeners` (`listener_id LIKE '%fnrh.application.FnrhSubmissionListeners%'`) antes de baixar `/api/v1/sync/changes`.
>
> A ARCHITECTURE §12 ganhou a regra "**Envio assíncrono por pedido**", que vale para toda integração (M7 e M8 a repetem):
>
> > **Envio assíncrono por pedido:** o evento só grava o pedido (idempotente por recurso, operação e evento); um job com ShedLock envia fora de transação, em ordem causal por recurso (a versão do agregado no evento), com retry de backoff limitado, e cada passo age sobre o estado atual, não sobre a ordem de chegada. Falha que o retry não resolve fica parada e visível, com reenvio e **encerramento manual** (o encerrado não segura a fila); o resultado é gravado mesmo se o alerta falhar.
>
> A regra "Resultado incerto" ganhou a escrita em curso: "Antes de cada escrita que cria recurso, a marca de **escrita em curso** é gravada em transação própria e só some quando o id remoto é gravado: uma queda entre a resposta e a gravação leva à conciliação, nunca a um segundo envio. A marca vale para o recurso, não só para o pedido que a ligou (qualquer pedido do mesmo recurso concilia antes de criar)." A tabela de jobs da §13 ganhou a linha do envio à FNRH (1 min).

*Nota para o curador:* o texto literal de [[ZenyHotelManager - Estado por marco]] diz que "no compose não há consumidor de produção de `ReservationCreated`, `ReservationChanged`, `ReservationCancelled`, `ReservationReactivated`, `ReservationConfirmed`". Desde a E08, isso vale só para `AvailabilityChanged`, `RatesChanged` e `RestrictionsChanged`.

---

### 3. `ZenyHotelManager - Segurança, autenticação e autorização`

**Complementa** a subseção "Permissões do `fnrh` e regras novas (M5 E07)" e **substitui** a frase "`fnrh.submissions.manage` virá na E08":

> - `fnrh.submissions.manage` (M5 E08, D-E08-12): **não sensível**, modelo de role só para o **Gerente**. Cobre `POST /api/v1/fnrh/submissions/{id}/retry` e `/dismiss` e define quem recebe o alerta `notifications.integration-failure` do envio. Decisão E08 (h), sem confirmação do usuário.
> - `fnrh.submissions.read` continua com Gerente e Recepcionista e passa a cobrir também `GET /api/v1/fnrh/submissions` (além de `GET /api/v1/fnrh/status`).

---

### 4. `ZenyHotelManager - Schemas, migrações e views de relatório`

**Complementa** "Atualizações por capturas" com uma subseção nova, e **complementa** a lista "Publicadas" das views com `fnrh.report_submissions` (M5 E08):

> ### Schema `fnrh`: fila de submissões e view (M5 E08, 2026-11-11)
>
> Migrações `fnrh/V2026_11_10_1000__create_fnrh_submissions.sql` e `fnrh/V2026_11_10_1100__create_fnrh_report_views.sql`. Nenhuma coluna guarda dado de hóspede, texto livre do Serpro, documento, raça/cor ou deficiência. `reservation_id` e `guest_id` são referências opacas, sem FK para outro schema.
>
> - `fnrh.submission`: `id`, `reservation_id`, `reservation_code`, `operation` (CHECK com as 6 operações), `operation_rank`, `event_key`, `causal_version` (≥ 0), `sequence` (`GENERATED ALWAYS AS IDENTITY`, cursor da API, único), `status` (CHECK com as 6 situações), `attempts`, `next_attempt_at`, `last_failure` (CHECK com os 10 códigos), `in_flight`, `performed_by`, `occurred_at`, `created_at`, `sent_at` e `version`. Chave única `submission_event_uk (reservation_id, operation, event_key)`. Índice parcial da fila `submission_queue_idx (reservation_id, causal_version, operation_rank, sequence) WHERE status IN ('PENDING','FAILED','INVALID')` e índice `submission_status_idx (status, sequence)`.
> - `fnrh.submission_error`: `(submission_id, guest_id, field, code)` como chave, com FK para `fnrh.submission` dentro do schema. Guarda o campo e o código, nunca o valor. O `retry` apaga essas linhas; o código não apaga as demais tabelas.
> - `fnrh.remote_reservation`: chave `(reservation_id, environment)`, com `remote_id`, `precheckin_link` (cifrado pelo `FieldCipher`, `v1:…`) e `cancelled`.
> - `fnrh.remote_guest`: chave `(reservation_id, guest_id, environment)`, com `person_id`, `guest_remote_id` e `checked_out`. Índice `(guest_id, environment)` para a pessoa já conhecida.
> - **Privilégios:** sem `GRANT` próprio. O `ALTER DEFAULT PRIVILEGES` de `V2026_11_04_1001` dá DML completo. Nenhuma das quatro é *append-only*.
> - **View `fnrh.report_submissions`:** uma linha por submissão, com `submission_id`, `reservation_id`, `operation`, `status`, `attempts`, `last_failure`, `created_at`, `sent_at` e `next_attempt_at` (este só vale enquanto `PENDING`). Ficam fora o código da reserva (quem precisa junta com `reservations.report_reservations` pelo `reservation_id`), os erros por campo, os ids e o link do Serpro, o cursor, a escrita em curso, o autor, a versão e todo dado de hóspede. Não há texto livre com valor de hóspede. Só `SELECT` para o papel da aplicação (`GRANT SELECT` e `REVOKE INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER`), provado por `FnrhReportViewsTest`. As pendências são `PENDING`, `FAILED` e `INVALID`, e o fechamento do M6 lê só a view.

---

### 5. `ZenyHotelManager - Docker, observabilidade e CI`

**Complementa** "Métricas" (o texto literal) com:

> `FnrhSubmissionMetrics` (`fnrh`, M5 E08, um `MeterBinder` à parte do `FnrhMetrics` da E07) publica o gauge `zeny_fnrh_submissions{status="pending|failed|invalid"}`: quantas submissões à FNRH estão em cada situação que pede atenção, lido do banco (`countByStatus`, um `GROUP BY`) a cada raspagem. Uma leitura que falha dá `NaN`, com log só da classe da exceção, e não derruba a raspagem. Testado em `FnrhSubmissionMetricsTest`. As métricas `zeny_fnrh_*` da E07 estão em [[ZenyHotelManager - Módulo fnrh]]. Nenhuma regra de alerta nova em `docker/prometheus/alerts.yaml` na E08.

---

### 6. `ZenyHotelManager - Estado por marco` e Estado do hub `ZenyHotelManager`

**Estado por marco: complementa** "Atualizações por capturas" com a subseção "M5 E08 (2026-11-11)", que **substitui** o estado do M5 da subseção "M5 E15" (próxima E08; E08 `#em-andamento` na nota do curador).

**Hub: substitui** o primeiro e o segundo itens de "Estado", o item "Concluir a E08…" de "Próximos passos" e a lista de decisões sem confirmação de "Perguntas abertas".

Texto para as duas notas:

> - M5 em andamento: **E01 a E08, E13, E14 e E15 concluídas**. A E08 foi concluída em 2026-11-11, com fechamento `2d07363`.
> - Próximas elegíveis: **E16, depois E10**. A E09 segue `#bloqueada` (Q-12) e depende de E08 e E16.
> - **Revisão humana pendente: E13, E07 e E08.** O lote parou na da E08. A E08 tem "Revisão humana: sim" porque fixa o padrão de envio assíncrono que M7 e M8 repetem.
> - **E15 e E08 estão só na branch `roadmap/m5-recepcao-fnrh`** (E15 fechada em `1d72325`, E08 em `2d07363`) até o usuário integrar. A `main` está em `ca9f9e2`. Segundo o orquestrador, a `main` tem mudanças do usuário sem commit, idênticas ao commit `340846c` da branch (revisão de arquitetura dos roadmaps, 2026-11-06).
> - A decisão E05 (f) foi aplicada na E08 (`8e6b677`): o `ReservationSearchApiTest` aceita `reservation_arrival_idx` ou `reservation_stay_period_idx` no filtro "period", porque era o único teste vermelho no gate da E08.
>
> Fatos da E08:
>
> - Plano `docs/superpowers/plans/2026-11-10-m5-recepcao-fnrh-e08.md`, com 13 tarefas e as decisões D-E08-1 a 17, executado em sequência pelas souls.
> - Revisão de arquitetura (`revisor-arquitetura`, opus): aprovado com notas em 2 rodadas. A inicial bloqueou com 1 Crítico (ordem de chegada dos eventos) e 7 Importantes.
> - Revisão final (`revisor-seguranca`, opus) sobre `1d72325..8e6b677`: "With fixes", com 0 Críticos, 3 Importantes (I-1, I-2 e I-3, corrigidos em `1df90ff`, `4d018cd` e `cf9d8e8`/`e6ac8eb`) e 6 Menores (M-1, M-2 e M-5 corrigidos; M-3, M-4 e M-6 diferidos). A re-revisão restrita (sonnet), sobre `8e6b677..e6ac8eb`, respondeu "all findings addressed".
> - `check_test_integrity.py --base 1d72325`: "OK: nenhum apontamento".
> - `./gradlew build` em `e6ac8eb`: BUILD SUCCESSFUL in 12m 18s, 2202 testes, 0 falhas. `.github/scripts/check-api-breaking.sh main`: nenhuma mudança `ERR`. Scanner: 0 Critical, 0 High, 2 Medium e 3 Low (os riscos aceitos na E14); nenhuma dependência mudou.
> - Documentos atualizados: SPEC §8.2.17 (`FnrhSubmission`, `FnrhRemoteReservation`, `FnrhRemoteGuest` e a porta `FnrhGateway` real), ARCHITECTURE §12 e §13, README (item "Envio à FNRH") e `docs/fnrh/api-fnrh-v2.4.md` (respostas de `GET /reservas/{id}/hospedes` e `GET /pessoas/documento/{tipo}/{numero}`). A SPEC diverge da forma antiga: uma submissão por evento, não por hóspede (D-E08-2).
>
> Decisões do lote E08 (a) a (n). Em 2026-11-10, o usuário delegou toda intervenção, salvo decisão de arquitetura. As decisões foram tomadas pela opção recomendada, em nome dele, pelo orquestrador, em 2026-11-10 e 2026-11-11. **Falta a confirmação dele.**
>
> - (a) Eventos: `Created` registra; `Changed`, `Confirmed` e `Reactivated` atualizam; `Cancelled` cancela; os três eventos de hospedagem fazem check-in, desfazer e check-out. A pré-reserva e a reserva sem documentos também são registradas no MTur, e a expiração vira cancelamento. `RoomMoved` não gera envio.
> - (b) Uma submissão por evento, com o progresso por hóspede em `fnrh.remote_guest`.
> - (c) Ordem causal por reserva. `FAILED` e `INVALID` seguram as seguintes.
> - (d) Retry: 8 tentativas, de 1 min a 1 h (cerca de 2 h), também em `UNAVAILABLE`. Falha permanente vira `FAILED` na hora. Os números são propriedade.
> - (e) Sem configuração, nada sai e nenhuma tentativa é gasta. Ao ligar, o acumulado sai inteiro (o corte fica para a E09 ou a M8 E13).
> - (f) Escrita em curso, conciliação antes de repetir, consulta por documento antes de criar a pessoa e reaproveitamento do `person_id` do ambiente.
> - (g) Desfazer check-in e reativação sem operação na API: `FAILED` (`NO_REMOTE_OPERATION` ou `REMOTE_CANCELLED`) com alerta, correção no portal e `dismiss`.
> - (h) `dismiss` leva a `DISMISSED`, que não segura a fila. `fnrh.submissions.manage` só para o Gerente.
> - (i) Link de pré-check-in cifrado em `fnrh.remote_reservation`, sem exposição na API.
> - (j) Alerta em transação própria: o alerta pode se perder, a submissão não.
> - (k) Trava do job `lockAtMostFor = PT1H`.
> - (l) Erro neutro dos dados sensíveis (`person.sensitiveData`/`INVALID_VALUE`).
> - (m) Revalidação de todos os hóspedes a cada tentativa do `CHECK_IN`. Recomendação: validar só os não enviados, numa manutenção do `fnrh`.
> - (n) Menor com responsável menor listado depois: `FAILED` com alerta, nunca `responsavel_id` errado.

Para "Perguntas abertas" do hub, **substitui** a frase das decisões sem confirmação por:

> - Sem confirmação do usuário, decididas pela opção recomendada: lotes M5 E04 a E06, E13 (a–f), E14 (a–c), E07 ((a) a (d), (f), (g), (h), (j)), E15 ((a) a (h)) e **E08 ((a) a (n); destaques: pré-reserva registrada no MTur, correção manual no portal para desfazer check-in e reativação, erro neutro dos dados sensíveis, revalidação de todos os hóspedes)**, mais a **revisão humana de E13, E07 e E08**, que o gate M8 E13 exige. Lista em [[ZenyHotelManager - Estado por marco]].

Para "Próximos passos" do hub, **substitui** "Concluir a E08 e executar E16 e E10…" por:

> - Revisão humana da E08 (e das pendentes E13 e E07). Integrar a branch `roadmap/m5-recepcao-fnrh` (E15 e E08) na `main`; o merge e o push são do usuário. Depois, executar E16 e E10 do M5 pelo `claude --agent orquestrador`.

---

## Contexto

O orquestrador do lote do roadmap M5 do ZenyHotelManager pediu esta captura no fechamento da E08 (protocolo "Second Brain" do roadmap: captura `ZenyHotelManager - atualização m5-recepcao-fnrh Eyy`). O lote parou na revisão humana da E08.

## Origem

- Projeto ZenyHotelManager, repositório `/home/caio/repos/ZenyHotelManager`, worktree `.claude/worktrees/roadmap-m5-recepcao-fnrh`, branch `roadmap/m5-recepcao-fnrh`, HEAD `2d07363` ("Conclui a E08 do M5 (envio assíncrono à FNRH) e preenche o handoff"). A `main` está em `ca9f9e2` (conferido por `git rev-parse`).
- Fontes lidas:
  - `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`, seção "E08 — Envio assíncrono e pendências da FNRH" e bloco "Decisões do lote E08";
  - `docs/superpowers/plans/2026-11-10-m5-recepcao-fnrh-e08.md`, tabela D-E08-1 a 17;
  - `git diff 1d72325 2d07363` de `docs/SPEC.md`, `docs/ARCHITECTURE.md`, `README.md` e `docs/fnrh/api-fnrh-v2.4.md`;
  - as migrações `fnrh/V2026_11_10_1000` e `V2026_11_10_1100`;
  - `FnrhSubmissionListeners.kt`, `FnrhSubmissionPorts.kt`, `FnrhSubmissionRecorder.kt`, o diff de `FnrhPermissions.kt`, `FnrhMetrics.kt`, `FnrhSubmissionJob.kt`, `FnrhErrorCodes.kt`, `FnrhAudit.kt` e `application.yaml`;
  - o diff de `IntegrationTest.kt`, `InventoryListenersQuiescence.kt` e `FnrhTestServer.kt`.

## Por que registrar

A E08 cria o padrão de envio assíncrono a provedores externos que M7 e M8 vão repetir, e ele tem revisão humana. As notas de tema do `fnrh`, dos eventos e jobs, da segurança, dos schemas, da observabilidade e do estado precisam refletir o código da branch para as próximas sessões (E16, E10, E09 e M6).

## Limitações e incertezas

- A E08 e a E15 **não estão na `main`**: o texto descreve a branch `roadmap/m5-recepcao-fnrh`.
- A afirmação de que a `main` tem mudanças do usuário sem commit, idênticas a `340846c`, vem do orquestrador. O escriba só conferiu que `340846c` existe (2026-11-06, "Aplica a revisão de arquitetura dos roadmaps M5 a M10 (decisões R1 a R16)"); não conferiu a árvore da `main`.
- Não li o código inteiro. Os nomes de classes e o comportamento vêm do handoff, do plano e dos arquivos citados em "Origem". As afirmações sobre `in_flight` "só via store" vêm das portas e do plano; não conferi toda a persistência.
- A frase "a última migração do projeto" não foi verificada nas pastas dos outros módulos. O plano exigia timestamp posterior a `V2026_11_06_1000`.
- As decisões (a) a (n) foram tomadas pelo orquestrador em nome do usuário, sem confirmação. Não são opinião do usuário.
- Nada foi copiado como anexo. A referência depende do worktree local, que pode ser removido depois da integração; os hashes de commit continuam valendo.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Módulo fnrh]]
- [[ZenyHotelManager - Eventos e jobs]]
- [[ZenyHotelManager - Segurança, autenticação e autorização]]
- [[ZenyHotelManager - Schemas, migrações e views de relatório]]
- [[ZenyHotelManager - Docker, observabilidade e CI]]
- [[ZenyHotelManager - Estado por marco]]
- [[2026-11-10 - ZenyHotelManager - atualização m5-recepcao-fnrh E15 - a22890e7]] (captura anterior do lote, arquivada)
- [[Decidir pendências do usuário por entrevista com opção recomendada]]
