---
type: knowledge
status: processed
created: 2026-10-22
projects:
  - "[[ZenyHotelManager]]"
sources:
  - "[[2026-10-22 - ZenyHotelManager - Eventos e jobs - 4e9ffb74]]"
  - "[[2026-11-06 - ZenyHotelManager - atualização revisão de arquitetura dos roadmaps - c889f886]]"
  - "[[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]]"
  - "[[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 (revisão humana) - 65d0d4ff]]"
  - "[[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E16 - 6095f729]]"
  - "[[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 - 4dd12e66]]"
  - "[[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]]"
  - "[[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 (revisão humana) - fa5b192f]]"
  - "[[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]]"
---
# ZenyHotelManager - Eventos e jobs

Referência técnica do projeto [[ZenyHotelManager]]: outbox, listeners de produção, jobs com ShedLock e o ciclo de uma publicação.

Texto literal do `CLAUDE.md` do repositório, linhas 564–577, no commit `a6c0f03` (2026-10-22), escrito pelos agentes que executaram as etapas M0 E01 a M5 E03; integrado sem resumo nem reescrita. Referências como "SPEC", "ARCHITECTURE §x", "RF-…", "RN-…", "Hn" e "Mx Ey" apontam para `docs/SPEC.md`, `docs/ARCHITECTURE.md` e `docs/roadmaps/` do repositório; menções a uma seção (por exemplo, seção "Transições de hospedagem") apontam para outra parte do antigo `CLAUDE.md`, hoje numa das notas de tema listadas no hub. Mudanças posteriores chegam por capturas "ZenyHotelManager - atualização Mx Ey" (fluxo no hub).

---

**Eventos e jobs** (ARCHITECTURE §5 e §13):

- Eventos publicados dentro da transação do caso de uso são gravados em `shared.event_publication` no mesmo commit. Listeners `@ApplicationModuleListener` rodam depois, assíncronos e em transação própria; se falharem, a publicação fica `FAILED`. O primeiro de produção é o `ChecklistRoutineListener` (`checklists`, M2 E07), idempotente pela geração por rotina e data; o segundo, o `PushDispatchListener` (`notifications`, M2 E09), idempotente pelo registro dos envios (`notifications.push_delivery`), que lança `PushDeliveryPostponed` na falha temporária do FCM para o outbox reenviar e trata dentro dele o que não deve ser reenviado (token inválido, sessão encerrada); o terceiro, o `PaymentSucceededListener` (`billing`, M3 E08), idempotente pela intenção (`billing.payment_intent_uk`): ignora a intenção cujo pagamento já está na conta e falha (publicação `FAILED`, visível no alerta de abandono) com uma intenção da conta sem pagamento, que só os provedores assíncronos do M7 criarão. O quarto e o quinto, os `InventoryListeners` (`reservations`, M4 E05) de `RoomRegistryChanged` e `OutOfOrderChanged`, idempotentes porque refazem os contadores a partir da `RoomsApi` (nunca somam deltas). O sexto, o `GuestsMergedListener` (`reservations`, M4 E07), idempotente porque reponta só o que ainda aponta para o absorvido. O sétimo, o `ReallocationListener` (`reservations`, M4 E10) de `OutOfOrderChanged`, idempotente porque refaz a marca "requer realocação" a partir da `RoomsApi` e só notifica a alocação marcada agora.
- Jobs do `shared`: `EventPublicationResubmissionJob` (`events-resubmit-failed`), `CompletedEventPublicationPurgeJob` (`events-purge-completed`, a cada hora; apaga as publicações concluídas há mais de `zeny.events.completed-retention`, 7 dias), `IdempotencyKeyPurgeJob` (`idempotency-keys-purge`) e `OfflineCommandPurgeJob` (`offline-commands-purge`, a cada hora; esvazia os resultados de comandos offline cuja retenção de 30 dias, contada de `retain_from`, venceu, e apaga os ids depois de 365 dias). Do `iam`: `RotatedRefreshTokenPurgeJob` (`iam-rotated-refresh-tokens-purge`, a cada 6h), que apaga os refresh tokens trocados há mais de 30 dias. Do `files`: `FileOrphanPurgeJob` (`files-orphans-purge`, a cada hora), que apaga os anexos órfãos há mais de 24 h, cada um auditado (`files.file.purge-orphan`). Do `guests`: `GuestDocumentRekeyJob` (`guests-documents-rekey`, a cada `zeny.guests.document-rekey.interval`, 1 h, depois de 10 min do boot), que re-cifra o número e recalcula o índice cego dos documentos gravados com uma chave que não é a ativa, um por transação com a linha travada, em lotes de 100 (até 10 por execução); escrita técnica, fora da trilha (o valor não muda, só a chave que o protege), com o falho só no log pelo id. Do `reservations`: `InventoryHorizonJob` (`reservations-inventory-horizon`, diário, depois de 2 min do boot), que cria as datas que faltam no horizonte de 730 dias de cada tipo de UH ativo e refaz o total e o OOO, um tipo por transação, auditado com ator sistema (`reservations.inventory.extend-horizon`), e, desde a E09, `ProvisionalExpiryJob` (`reservations-provisional-expiry`, a cada 5 min, depois de 1 min do boot), que cancela as pré-reservas vencidas sem multa, uma por transação, auditado com ator sistema (`reservations.reservation.expire`). Um método com `@SchedulerLock` não pode devolver tipo primitivo (o ShedLock recusa na chamada). Os expurgos de dados transitórios não vão para a trilha de auditoria (são escritas técnicas, em `infrastructure`).
- **Ciclo de uma publicação** (H13 do roadmap do M2, M2 E12; `shared/infrastructure/events/`, regra em `OutboxRetryPolicy`):
  - **Reenvio com backoff:** o `EventPublicationResubmissionJob` roda a cada minuto e reenvia só as `FAILED` cuja próxima tentativa venceu: depois de `n` reenvios (`completion_attempts` − 1; a entrega original grava 1), a espera é `zeny.events.resubmission.initial-backoff` × 2ⁿ até `max-backoff` (1, 2, 4, 8, 16, 32 min e depois 1 h), contada de `last_resubmission_date` (que o Modulith cria com a data da publicação e atualiza a cada reenvio), pelo `Clock` da aplicação, o mesmo que grava as datas. No máximo `batch-size` (100) reenvios por execução. A leitura das `FAILED` não tem `LIMIT` (o Modulith limita antes de filtrar, e as abandonadas esconderiam as vencidas); o evento só é desserializado se for reenviado.
  - **Abandono:** a `FAILED` cujo `last_resubmission_date` é `give-up-after` (24 h) ou mais depois da `publication_date` falhou numa tentativa já depois do prazo e está **abandonada** (com os padrões, no 29º reenvio, 24 h 3 min depois da publicação). Ela continua `FAILED` na tabela, nunca é apagada, sai do reenvio automático, conta como `state="abandoned"` no `OutboxMetrics` e dispara o alerta `ZenyOutboxAbandonedPublications` (com `for: 5m`, para não alarmar durante a última tentativa ainda em execução, que já conta como abandonada). A regra só olha as datas da linha, não o relógio, e nenhum caminho automático a desfaz: o staleness só passa paradas a `FAILED` e `republish-outstanding-events-on-restart` está **desligado**, porque reenviaria no boot todas as incompletas, sem filtro, inclusive as abandonadas. No boot, então, nada é reenviado de imediato: as `FAILED` voltam pelo job (primeira execução 1 min depois do boot) e as que o processo anterior deixou em andamento, pelo staleness (paradas há mais de 10 min viram `FAILED`, `spring.modulith.events.staleness.*`). O prazo conta da publicação: com a aplicação fora do ar, o tempo parado também conta, mas sempre há ao menos uma tentativa depois do prazo.
  - **Reenvio manual** (sem endpoint), depois de corrigir a causa: como o dono ou o papel da aplicação (no compose, `docker compose -f docker/compose.yaml exec db sh -c 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"'`), liste as abandonadas com `SELECT id, listener_id, event_type, publication_date, completion_attempts, last_resubmission_date FROM shared.event_publication WHERE status = 'FAILED' AND last_resubmission_date >= publication_date + interval '24 hours' ORDER BY publication_date;` e devolva uma ao reenvio com `UPDATE shared.event_publication SET last_resubmission_date = publication_date WHERE id = '<id>' AND status = 'FAILED' AND last_resubmission_date >= publication_date + interval '24 hours';` (sem o `id`, todas). Com `give-up-after` diferente de 24 h, troque o intervalo. O job a reenvia na execução seguinte (até 1 min); se falhar de novo, ela volta a ficar abandonada depois dessa única tentativa. Para desistir de vez de uma publicação (o efeito não será feito), marque-a como concluída: `UPDATE shared.event_publication SET status = 'COMPLETED', completion_date = now() WHERE id = '<id>' AND status = 'FAILED';` (o expurgo a apaga depois da retenção). `OutboxRetryTest` executa o reenvio manual.
  - **Expurgo:** o `CompletedEventPublicationPurgeJob` (ShedLock `events-purge-completed`, a cada hora) chama `CompletedEventPublications.deletePublicationsOlderThan(completed-retention)` do Modulith, que apaga só as linhas com `completion_date` anterior ao corte e `status` `COMPLETED`; as incompletas (pendentes, com falha ou abandonadas) nunca. O modo de conclusão continua o padrão (`spring.modulith.events.completion-mode: update`): `delete` apagaria na hora, sem retenção, e `archive` moveria para outra tabela, sem expurgo. Fora da trilha de auditoria (dado técnico).
  - Por tudo isso, todo listener precisa ser idempotente: um evento pode ser entregue mais de uma vez (inclusive pelo staleness, que pode passar a `FAILED` um reenvio ainda em execução).
  - **Testes:** `OutboxRetryTest` (com `MutableClockConfiguration` e o `ProbeListener`, que falha N vezes e conta as execuções em `ProbeState.invocationsOf`: backoff medido, abandono no 29º reenvio, métrica, job, staleness e reenvio manual), `OutboxRetryPolicyTest`, `CompletedEventPublicationPurgeTest` e `EventPublicationRegistryTest` (o boot de um segundo processo não reenvia nada). Nos testes, `RESUBMISSION_JOB_DEFERRED` e `OUTBOX_PURGE_DEFERRED` (`@IntegrationTest`) adiam os dois jobs: um contexto em cache com o relógio adiantado apagaria, no banco compartilhado, as publicações de outro teste.
- Jobs são `@Scheduled` com `@SchedulerLock(name = "<nome-único>")`; o ShedLock trava em `shared.shedlock` usando a hora do banco. Exceção: tarefa que só lê para a própria instância (como o `refresh` do `OutboxMetrics`) não trava. `@EnableScheduling` e o `LockProvider` ficam em `shared/infrastructure/scheduling/SchedulingConfiguration.kt`. *(Desde a M6 E18, a exceção que escapa de um job é logada só com o nome do job e as classes, pelo `JobErrorLoggingTaskScheduler`: subseção "Log das exceções dos jobs: `JobErrorLoggingTaskScheduler`" em "Atualizações por capturas".)*
- O `spring-modulith-moments` está excluído do build: a data operacional só avança no fechamento do dia (`hotel`, M1).

---

## Atualizações por capturas

Texto das capturas de atualização publicadas no repositório, integrado sem resumo nem reescrita. Vale sobre o texto literal acima quando trata do mesmo assunto.

### Padrão de integração e jobs previstos (revisão dos roadmaps, 2026-11-06)

Origem: [[2026-11-06 - ZenyHotelManager - atualização revisão de arquitetura dos roadmaps - c889f886]]. Detalhes da FNRH em [[ZenyHotelManager - Módulo fnrh]].

**Decisão do arquiteto (R8):** o padrão de integração passa a ser descrito pelo que o M5 E07 provou, e **não existe mecanismo genérico de falha**. Os roadmaps supunham um; a hipótese M7 H2 foi conferida como falsa no código: o M5 usa `NotificationsApi.notify` direto, `GET /fnrh/status` e `MeterBinder`, sem `HealthIndicator`. A extração para `shared` fica para a M7 E01 decidir, com a segunda integração à frente.

Citação literal de `docs/ARCHITECTURE.md` §12 (árvore de trabalho, sem commit na data da captura):

> Regras que a FNRH (M5 E07) provou e que valem para toda integração:
>
> - **Resultado incerto:** timeout de leitura numa escrita não diz se o provedor gravou. Nunca se repete às cegas: reenvio só com a mesma referência idempotente do provedor ou depois de conciliar pela consulta. A conciliação ambígua falha fechado.
> - **Registro de integração** em tabela *append-only* sem texto livre do provedor, porque ela não admite expurgo; a mensagem saneada vai só para o log e para a exceção, sem causa encadeada.
> - **Credencial** cifrada, nunca na trilha (nem o usuário), nunca devolvida na API e removível por uma ação com trilha. O administrador escolhe o ambiente, as URLs ficam em propriedade, e trocar de ambiente pede a credencial de novo.
> - **Falha** alerta por chamada direta a `notifications`, com o tipo `notifications.integration-failure` e sem dado pessoal. A readiness nunca depende de provedor externo.

Lista de jobs: a tabela da ARCHITECTURE §13 troca "Retenção LGPD (anonimização e expurgo)" por "Expurgo dos dados sensíveis da FNRH (M8 E16)" e "Anonimização de perfis por prazo (M10 E13)", ambos semanais. Nenhum deles existe ainda.

### Primeiros consumidores dos eventos de reserva e hospedagem e job do envio à FNRH (M5 E08, 2026-11-11)

- **`FnrhSubmissionListeners`** (`fnrh`, M5 E08) são os primeiros consumidores de produção de `ReservationCreated`, `ReservationChanged`, `ReservationConfirmed`, `ReservationReactivated` e `ReservationCancelled` (M4) e de `GuestCheckedIn`, `GuestCheckInUndone` e `GuestCheckedOut` (M5 E01). São 8 métodos `@ApplicationModuleListener` (9 desde a M6 E14, com `ReservationMarkedNoShow`; ver a subseção "M6 E14" abaixo), e o outbox passa a gravar essas publicações. Cada um **só grava** a `FnrhSubmission`, nunca envia. São idempotentes pela chave `(reservation_id, operation, event_key)`, com `INSERT … ON CONFLICT DO NOTHING`: a reentrega, inclusive fora de ordem ou com a submissão já `SENT`, não grava outra. A ordem entre eles não importa, porque a fila ordena pela versão causal. `RoomMoved` não tem listener no `fnrh`; `AvailabilityChanged`, `RatesChanged` e `RestrictionsChanged` seguem sem consumidor de produção (M8).
- **Job `FnrhSubmissionJob`** (ShedLock `fnrh-submissions-send`, a cada `zeny.fnrh.submissions.interval`, 1 min, depois de 1 min do boot): envia as cabeças vencidas da fila (até `batch-size`, 50) pelo `FnrhSubmissionSender`, que não é `@Transactional` e chama o Serpro fora de transação. O resultado é gravado pelo `FnrhSubmissionRecorder` (`@Audited`, ator sistema). `lockAtMostFor = PT1H` (decisão E08 (k)), porque uma execução pode levar muito mais que os 10 min dos outros jobs (50 submissões, várias chamadas de até 25 s). Custo: uma instância que morre com a trava atrasa o envio em até 1 h. Sem configuração da FNRH, não faz nada.
- **Testes:** `FNRH_SEND_DEFERRED` (`zeny.fnrh.submissions.initial-delay=PT24H`) no `@IntegrationTest` adia o job, e os testes chamam o envio direto, só para a própria reserva (`sendDueFor`). O `InventoryListenersQuiescence` passou a esperar também as publicações dos `FnrhSubmissionListeners` (`listener_id LIKE '%fnrh.application.FnrhSubmissionListeners%'`) antes de baixar `/api/v1/sync/changes`.

A ARCHITECTURE §12 ganhou a regra "**Envio assíncrono por pedido**", que vale para toda integração (M7 e M8 a repetem):

> **Envio assíncrono por pedido:** o evento só grava o pedido (idempotente por recurso, operação e evento); um job com ShedLock envia fora de transação, em ordem causal por recurso (a versão do agregado no evento), com retry de backoff limitado, e cada passo age sobre o estado atual, não sobre a ordem de chegada. Falha que o retry não resolve fica parada e visível, com reenvio e **encerramento manual** (o encerrado não segura a fila); o resultado é gravado mesmo se o alerta falhar.

Na revisão humana da E08 (2026-11-11, roadmap da branch `roadmap/m5-recepcao-fnrh`, commit `2185e41`), o usuário aprovou esse padrão: ele é **a referência para os envios assíncronos de M7 e M8**. As decisões (a) a (n) do lote E08 seguem revisáveis uma a uma.

A regra "Resultado incerto" ganhou a escrita em curso: "Antes de cada escrita que cria recurso, a marca de **escrita em curso** é gravada em transação própria e só some quando o id remoto é gravado: uma queda entre a resposta e a gravação leva à conciliação, nunca a um segundo envio. A marca vale para o recurso, não só para o pedido que a ligou (qualquer pedido do mesmo recurso concilia antes de criar)." A tabela de jobs da §13 ganhou a linha do envio à FNRH (1 min).

### Regra da credencial: a ação de limpar (M5 E16, 2026-11-11)

Origem: [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E16 - 6095f729]]. Complementa a regra "**Credencial**" da ARCHITECTURE §12 citada em "Padrão de integração e jobs previstos" acima, com o texto novo da linha "Credencial" (decisão D-E16-7, sem confirmação do usuário):

> Toda integração com credencial tem a ação `POST …/clear-credentials` com `If-Match`, sem `Idempotency-Key`; ela apaga a credencial e desliga a integração, mantendo o ambiente e o que não é credencial; repetir é `200` e mantém o `ETag`; religar exige credencial nova; a trilha fica sem segredo nem usuário. A M5 E16 é a primeira a seguir a regra, e os provedores de M7 e M8 nascem com ela (R6).

A implementação da FNRH está em [[ZenyHotelManager - Módulo fnrh]] ("Configuração cifrada, por ambiente").

### Job de manutenção da fila de impressão (M5 E10, 2026-11-11)

Origem: [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 - 4dd12e66]]. Complementa a lista de jobs do segundo marcador do texto literal ("Jobs do `shared`: …"), que não menciona o `printing`, e a subseção "Padrão de integração e jobs previstos" acima:

- Do `printing`: `PrintingJobsMaintenance` (ShedLock `printing-jobs-maintenance`, a cada `zeny.printing.maintenance-interval`, 1 min; `lockAtMostFor` PT10M; adiado nos testes por `PRINTING_MAINTENANCE_DEFERRED`). Reenvio dos `SENT` sem confirmação e limite de tentativas, validade dos `PENDING`, jobs de impressora inativa ou de agente desativado e expurgo do conteúdo, uma transação por job com a linha travada (regras em [[ZenyHotelManager - Módulo printing]]). Escrita técnica do ator sistema; sem alerta por `notifications` (o `printing` não depende dele).

### Fechamento do dia: gatilho e trava de execução (M6 E10, 2026-11-13)

Origem: [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]] (item 4), com o complemento [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 (revisão humana) - fa5b192f]], que vale sobre ela no risco abaixo. Módulo em [[ZenyHotelManager - Módulo endofday]].

- Jobs novos: `EndOfDayTriggerJob` (`end-of-day-trigger`, 1 min) e a trava de execução `end-of-day-run` (ShedLock com keep-alive, usada por execução manual, retomada e automático). ARCHITECTURE §13 atualizada.
- Risco registrado para a E11: o `tick()` espera o motor por até `lock-at-most-for` e o agendador do Spring tem uma thread por padrão; com etapas reais longas, os demais jobs ficariam parados. **Resolvido pela decisão do usuário** (revisão humana da E10, 2026-11-13, H12): na E11, o gatilho automático passa a só disparar o motor e voltar (espera curta), sem mudar o pool do agendador do Spring.

### Log das exceções dos jobs (decisão da M6 E18, 2026-11-13; implementada em 2026-11-15)

*Nota do curador (2026-11-16):* **implementada na M6 E18.** O comportamento atual, com os detalhes, está na subseção "Log das exceções dos jobs: `JobErrorLoggingTaskScheduler` (M6 E18, 2026-11-15)", no fim desta seção, que substitui esta. O título dizia "ainda não implementada".

Origem: [[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]] (item 5; ARCHITECTURE §13, primeiro parágrafo, que remete à §16). Quando esta subseção foi escrita, era decisão registrada na ARCHITECTURE, ainda fora do código (entrou com a M6 E18). O tratador único é decisão do `arquiteto` (H13).

- Exceção que escapa de um job, inclusive a falha da trava do ShedLock com o banco fora, é logada pelo tratador de erro do agendador do `shared` com o nome da tarefa e só a classe da exceção e das causas, **sem a mensagem**, que pode trazer valores do banco.
- O tratador de erro é único, o do agendador da aplicação, e não um por job. Alternativa descartada: `try/catch` por job.

### Fechamento do dia: gatilho que só dispara o motor e `ReservationMarkedNoShow` (M6 E11, 2026-11-14)

Origem: [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E11 - df23f14d]] (item 7). Implementa a decisão do usuário registrada na subseção "Fechamento do dia: gatilho e trava de execução (M6 E10)" acima. Etapas em [[ZenyHotelManager - Módulo endofday]].

- O `EndOfDayTriggerJob` (`end-of-day-trigger`, 1 min) só dispara o motor e volta (`zeny.endofday.trigger.wait`, padrão `PT5S`, até `PT1M`), sem bloquear o agendador de uma thread por `lock-at-most-for`. ARCHITECTURE §13 (etapas do fechamento) atualizada.
- Novo evento publicado: `ReservationMarkedNoShow` (campos e regras em [[ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)]], "M6 E11"); o primeiro consumidor de produção é o `fnrh` (M6 E14, subseção abaixo).
- O `ProvisionalExpiryJob` (5 min) continua existindo ao lado da etapa `provisional-expiry` do fechamento.

### Primeiro consumidor de `ReservationMarkedNoShow`: o `fnrh` (M6 E14, 2026-11-14)

Origem: [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E14 - 998156dc]] (item 3). Complementa a subseção "Primeiros consumidores dos eventos de reserva e hospedagem e job do envio à FNRH (M5 E08)" acima. Envio em [[ZenyHotelManager - Módulo fnrh]] ("No-show (M6 E14, 2026-11-14)").

- **`ReservationMarkedNoShow`** (publicado pelo `endofday` pelo outbox desde a M6 E11, sem dado pessoal) **ganha o primeiro consumidor de produção: o `fnrh`** (`FnrhSubmissionListeners`, M6 E14), que só grava a `FnrhSubmission` `NO_SHOW` (idempotente pela chave `(reservation_id, operation, event_key)`, `event_key = no-show:v<version>`). Os `FnrhSubmissionListeners` passam de 8 para **9** métodos `@ApplicationModuleListener`.
- O listener roda fora da transação do fechamento (outbox): a falha do Serpro nunca bloqueia o fechamento (RN-22). O envio sai no job `fnrh-submissions-send` (inalterado: 1 min, `lockAtMostFor = PT1H`).
- O `InventoryListenersQuiescence` já espera pelos `FnrhSubmissionListeners`; nada mudou nele.
- Com a E14, `ReservationMarkedNoShow` também deixa de estar sem consumidor (complementa a nota do curador da E08 sobre consumidores, em [[ZenyHotelManager - Estado por marco]], "M5 E08").

*Nota do curador (conferência por `git` em 2026-11-15, só leitura, no `ad970fc`):* o `FnrhSubmissionListeners.kt` tem 9 métodos `@ApplicationModuleListener` (a captura dava o número como dedução).

### Log das exceções dos jobs: `JobErrorLoggingTaskScheduler` (M6 E18, 2026-11-15)

Origem: [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E18 - a68d398b]] (item 4; fatos do handoff da E18, segundo a captura). Substitui a subseção "Log das exceções dos jobs (decisão da M6 E18, 2026-11-13)", acima: agora é comportamento atual, com os detalhes abaixo. Complementa o marcador "Jobs são `@Scheduled` com `@SchedulerLock`" do texto literal (que cita `SchedulingConfiguration.kt`). A etapa está na branch `roadmap/m6-operacao-fechamento`, ainda fora da `main` (ver [[ZenyHotelManager - Estado por marco]], "M6 E18"). As decisões (d) e (f) são do handoff, pela opção recomendada, **sem confirmação do usuário**.

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
- **Pendência:** quatro jobs ainda capturam e logam a própria falha com a mensagem, fora do tratador novo, que só vê o que escapa; lista em [[ZenyHotelManager - Docker, observabilidade e CI]] ("Mensagem do JDBC fora do log dos jobs").

*Nota do curador (conferência por `git` em 2026-11-16, só leitura, no `ed0f5ab`):* existe `shared/infrastructure/scheduling/ScheduledJobErrors.kt`; o `application.yaml` tem `spring.task.execution.mode: force` e o logger `net.javacrumbs.shedlock.provider.jdbctemplate.JdbcTemplateStorageAccessor: OFF`, com comentário que cita a perda do "Unlock failed after 10 attempts". O corpo do agendador, o número de `@Scheduled` e os testes não foram conferidos.

---

## Proveniência

- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - Eventos e jobs - 4e9ffb74]] (capture_id: 4e9ffb74-b604-4a12-835d-89cb104e68f7): texto literal do `CLAUDE.md` do repositório ZenyHotelManager (linhas 564–577, commit `a6c0f03`), integrado sem alteração; o tipo Knowledge em `20 Knowledge/` foi escolhido pelo usuário no processamento.
- 2026-11-09 — [[2026-11-06 - ZenyHotelManager - atualização revisão de arquitetura dos roadmaps - c889f886]] (capture_id: c889f886-0719-4f28-984e-f2ef23ed9520): padrão de integração (R8, ARCHITECTURE §12) e jobs previstos (§13), em "Atualizações por capturas".
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]] (capture_id: 8df87866-4285-4e24-8878-0fab70c9436c): primeiros consumidores dos eventos de reserva e hospedagem, job `fnrh-submissions-send` e regras "Envio assíncrono por pedido" e escrita em curso da ARCHITECTURE §12 (item 2 da captura).
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 (revisão humana) - 65d0d4ff]] (capture_id: 65d0d4ff-bc24-4f40-94ba-c062bdf2b9c1): aprovação do padrão de envio assíncrono pelo usuário como referência para M7 e M8.
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E16 - 6095f729]] (capture_id: 6095f729-34e7-4667-9c48-d112262c6212): regra da ação `POST …/clear-credentials` na linha "Credencial" da ARCHITECTURE §12 (item 2 da captura, D-E16-7).
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 - 4dd12e66]] (capture_id: 4dd12e66-191b-406d-a974-4ae7dca3e15f): job `printing-jobs-maintenance` do `printing` (item 4 da captura).
- 2026-11-15 — [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]] (capture_id: 1e4f709b-7bbd-4c39-9725-1926aef1ca98): job `end-of-day-trigger`, trava `end-of-day-run` e o risco do agendador para a E11 (item 4 da captura).
- 2026-11-15 — [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 (revisão humana) - fa5b192f]] (capture_id: fa5b192f-13a0-4e35-959a-3134613a24d8): risco do agendador resolvido pela decisão do usuário (gatilho só dispara o motor e volta).
- 2026-11-15 — [[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]] (capture_id: 009e3130-5bd9-4e8b-bd56-81c7fc440b81): log das exceções dos jobs só pela classe, pelo tratador do agendador do `shared` (decisão da M6 E18, item 5 da captura).
- 2026-11-15 — [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E11 - df23f14d]] (capture_id: df23f14d-ec3c-4fa2-aa75-462913ddaf5e): gatilho do fechamento que só dispara o motor (`zeny.endofday.trigger.wait`) e evento `ReservationMarkedNoShow` (item 7 da captura).
- 2026-11-15 — [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E14 - 998156dc]] (capture_id: 998156dc-c51d-47f2-ad9c-86f204f7236c): primeiro consumidor de produção de `ReservationMarkedNoShow` (o `fnrh`) e 9 listeners (item 3 da captura); nota do curador com o número conferido por `git`.
- 2026-11-16 — [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E18 - a68d398b]] (capture_id: a68d398b-2037-4b20-af27-8039b163ae0e): `JobErrorLoggingTaskScheduler`, formato do log, logger do ShedLock em `OFF`, `spring.task.execution.mode: force` e atenção ao upgrade do ShedLock (item 4 da captura), na subseção nova "Log das exceções dos jobs: `JobErrorLoggingTaskScheduler`", que substitui a da decisão de 2026-11-13 (mantida com marca); remissão no marcador dos jobs; nota do curador com a conferência por `git`.
