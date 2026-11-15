---
type: capture
status: archived
created: 2026-11-14
capture_id: 998156dc-c51d-47f2-ad9c-86f204f7236c
---
# ZenyHotelManager - atualização m6-operacao-fechamento E14

## Conteúdo capturado

Captura de fechamento da etapa M6 E14 (no-show na FNRH), `#concluida` em 2026-11-14 na branch `roadmap/m6-operacao-fechamento`. Resumo do agente a partir do handoff da E14 no roadmap, do plano da etapa (D-E14-1 a D-E14-7), da migração e do código (`LogMessages.kt`). Organizada por nota de tema, dizendo se **substitui** ou **complementa** cada trecho. **Complementa** a captura da E08 ([[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]]) e a da E11 ([[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E11 - df23f14d]]) e as **substitui** onde dito. Vale sobre as notas e sobre essas capturas quando tratarem do mesmo assunto.

**As decisões (a) a (e) do handoff foram tomadas pelo orquestrador pela opção recomendada, sem confirmação do usuário** (nenhuma é de arquitetura). Não são opinião do usuário.

### 1. `ZenyHotelManager - Módulo fnrh`

**1.1 Complementa** a tabela "Porta `FnrhGateway` e operações" com uma linha, e **substitui** a frase "O no-show vai pela M6 E14, com operação nova na porta; o gate M8 E13 pede o no-show executado na homologação ou registrado como risco aceito pelo usuário" (item "Fora da porta") e a frase "O no-show fica para a M6 E14 (H15)" (seção "Envio assíncrono", da captura da E08) por: "O no-show entrou na M6 E14 (ver 'No-show' abaixo); o gate M8 E13 pede o no-show executado na homologação ou registrado como risco aceito pelo usuário."

> | `markNoShow` | `POST /reservas/{reserva_id}/noshow`, sem corpo (no-show **em lote, da reserva**; D-E14-1). Só leva o id remoto da reserva, que já guardamos. O corpo da resposta não é lido: qualquer `2xx` é sucesso. Falhas seguem a classificação da E07 (timeout de leitura num `POST` é `UNKNOWN_OUTCOME`). Sem `cpf_solicitante`. Operação `markNoShow` no `fnrh.integration_call` |

Na lista "Fora da porta" da nota, o no-show deixa de estar fora: continua fora o no-show **individual** (`PATCH /hospedes/{id}/no-show` ou `/noshow`).

**1.2 Complementa** a seção "Envio assíncrono (M5 E08)" (texto da captura da E08) com a subseção:

> ### No-show (M6 E14, 2026-11-14)
>
> **Evento e submissão (D-E14-2).** O `ReservationMarkedNoShow` (M6 E11) grava **uma** `FnrhSubmission` com `operation = NO_SHOW`, `event_key = no-show:v<version>` e `causal_version = ReservationMarkedNoShow.version`, idempotente pela chave `(reservation_id, operation, event_key)`: a reentrega do evento (inclusive depois de `SENT`, `FAILED` ou `DISMISSED`) não grava outra. O posto de `NO_SHOW` na ordem causal é **6**, anexo ao fim (a lista passa a `REGISTER_RESERVATION` 0 < `UPDATE_RESERVATION` 1 < `CANCEL_RESERVATION` 2 < `CHECK_IN` 3 < `UNDO_CHECK_IN` 4 < `CHECK_OUT` 5 < `NO_SHOW` 6); o posto só desempata dentro da mesma `causal_version`. Como o registro tem `causal_version` 0 e o no-show tem `version` maior ou igual a 1, o no-show sai sempre depois do registro da reserva. **Substitui** a lista de postos 0 a 5 da captura da E08. O mapeamento evento → operação da E08 ganha a linha `ReservationMarkedNoShow` → `NO_SHOW`.
>
> **Caminho (D-E14-1; decisão (a) do handoff).** Escolhido o no-show em lote da reserva, `POST /reservas/{reserva_id}/noshow`, e não um dos individuais. O critério de aceite formulava a escolha entre os dois individuais; este é um terceiro caminho. Motivo: no nosso fluxo (D-E07-2) a reserva é registrada na criação sem hóspedes e os hóspedes só entram no check-in; uma reserva no-show nunca teve check-in, então não há `hospede_id` remoto para o caminho individual. O caminho da reserva só precisa do id remoto que já guardamos, é o único sem divergência no PDF e alcança também os hóspedes de pré-check-in criados pelo próprio hóspede pelo link. É barato de desfazer (fica no adaptador, sem migração nem contrato). Alternativa descartada: o individual, que exigiria registrar hóspedes sem check-in.
>
> **Passo do envio, pelo estado atual (D-E14-3, D-E08-9).**
>
> - Reserva que **não está mais `NO_SHOW` aqui** (reativada antes do envio): `SENT` sem chamada, antes de qualquer conciliação, porque o no-show remoto é irreversível (decisão (b); ruling do orquestrador na revisão da Task 4). Resíduo: uma reativação entre a leitura e o `POST` ainda envia o no-show; o `UPDATE` seguinte fica `FAILED REMOTE_NO_SHOW` com alerta.
> - Remota guardada, não cancelada e não no-show: `markNoShow`; no sucesso grava `no_show = true` em `fnrh.remote_reservation` (preservando o link e `cancelled = false`) e a submissão fica `SENT`.
> - Sem remota guardada: com escrita em curso na reserva, concilia (o mesmo caminho do `cancel`); achada, segue acima; não achada, `SENT` sem chamada (a reserva no-show nunca é registrada: `NOT_REGISTERED`).
> - Remota já cancelada ou já no-show: `SENT` sem chamada.
> - **Repetição (decisão (c)):** o `POST …/noshow` é repetido no `retry` depois de `UNKNOWN_OUTCOME`, como o cancelamento da E08 (o no-show não cria recurso, então não há conciliação antes de repetir). Uma repetição recusada (`VALIDATION`) fica `FAILED` com alerta, e a remota local continua sem `no_show`; depois do `dismiss`, um `UPDATE` de reativação faria o `PUT` numa reserva `NOSHOW` no Serpro.
>
> **Estado remoto: a remota é cancelada ou no-show, nunca as duas (D-E14-4).** A API não desfaz no-show.
>
> - `UPDATE_RESERVATION` (inclusive o da reativação) com a remota `no_show` e a reserva ativa aqui: `FailedLocally(REMOTE_NO_SHOW)` com alerta, sem chamada (correção no portal e `dismiss`, como o `REMOTE_CANCELLED`). Com a reserva cancelada ou no-show aqui: `SENT` sem chamada.
> - `CANCEL_RESERVATION` com a remota `no_show`: `SENT` sem chamada.
> - **Não coberto (decisão (d)):** `CHECK_IN` e `CHECK_OUT` sobre uma remota no-show (ou cancelada, já na E08) não têm guarda local. Depois de reativação, `dismiss` e novo check-in, o envio cadastra a pessoa e recebe `4xx` (`FAILED` com alerta). Recomendação do handoff: numa manutenção do `fnrh`, `remote.closed` leva a `FailedLocally(REMOTE_CANCELLED | REMOTE_NO_SHOW)` sem chamada.
> - **Lacuna anterior, da E08 (decisão (e)):** um `CANCEL_RESERVATION` pendente sai mesmo depois da reativação, e a remota é cancelada sem volta com a reserva ativa aqui. Recomendação: a mesma guarda pelo estado local (`status != CANCELLED`, sem chamada), numa etapa de manutenção do `fnrh` a criar pelo `arquiteto` (a E16 é só de teste).
> - Fora de alcance, registrado também na lista da E09: check-in enviado, desfeito (`UNDO_CHECK_IN` `FAILED NO_REMOTE_OPERATION`, `dismiss`) e depois no-show; o Serpro tem um hóspede `CHECKIN_REALIZADO` e o lote pode ser recusado ou corrigir o hóspede.
>
> **Códigos novos (D-E14-5).** `FnrhOperation.NO_SHOW` (posto 6), `FnrhSubmissionFailure.REMOTE_NO_SHOW` (`temporary = false`) e os espelhos da web `FnrhSubmissionOperationView.NO_SHOW` e `FnrhSubmissionFailureView.REMOTE_NO_SHOW`. Rótulo do alerta `integration-failure`: `no-show`. No contrato, `operation` e `lastFailure` das submissões já eram `x-extensible-enum`, então acrescentar não quebra (oasdiff sem `ERR`). **Complementa** a lista de falhas da E08 (`REMOTE_CANCELLED`, `NO_REMOTE_OPERATION`) com `REMOTE_NO_SHOW`.
>
> **Resiliência (RN-22).** Com o Serpro fora do ar durante o fechamento, o fechamento conclui `COMPLETED` e a submissão fica `PENDING` com a tentativa contada (`attempts = 1`, `SERVER_ERROR`); credenciais recusadas também não travam o fechamento. `FAILED` e `INVALID` seguram a fila da reserva até `retry` ou `dismiss`.
>
> **Dependências do módulo.** Inalteradas: `shared`, `guests`, `reservations` e `notifications` (o `ModularityTest` não mudou). A ARCHITECTURE §3.1 lista `hotel` entre as dependências do `fnrh`, mas o `FnrhModule.kt` não o declara: divergência apontada ao `arquiteto` (ver 'Pendências para o curador e o arquiteto').

**1.3 Complementa** "Notas para a E09" com quatro pontos novos (confirmar na homologação, M5 E09, ainda `#bloqueada` pela Q-12, e cobrados pelo gate M8 E13):

> - O **código de resposta** do `POST /reservas/{id}/noshow` numa reserva **sem hóspedes** (o Serpro pode recusar o lote com `4xx`; hoje isso vira `FAILED` com alerta).
> - A **situação da reserva depois do lote**: um `200` com `dados` vazio pode deixar a remota em `CRIADA` (o `no_show = true` local ficaria falso em relação ao Serpro).
> - A **resposta à repetição** do `POST …/noshow` numa reserva já `NOSHOW` (depois de um `UNKNOWN_OUTCOME`, uma recusa viraria um `FAILED` falso).
> - O **lote numa reserva com hóspede `CHECKIN_REALIZADO`** (check-in desfeito: o lote pode ser recusado ou corrigir o hóspede).
>
> **Substitui** o item "Confirmar o formato do `400`, o caminho do no-show (`/no-show` ou `/noshow`), …" por "Confirmar o formato do `400`, a ordem de `dados_hospedes` e o limite de 200 caracteres da senha; e o no-show (os quatro itens acima, mais o caminho individual `/no-show` ou `/noshow`, que o PDF da API deixa divergente e que só importa se o caminho em lote for recusado)". O critério de aceite da E09 ("o no-show, se o M6 já o publicar") passa a valer: o M6 publica.

**1.4 Complementa** "Estado:" da abertura da nota (e da captura da E08): "E14 do M6 concluída (no-show na FNRH, 2026-11-14); a homologação real segue sendo a E09, `#bloqueada`."

**1.5 Complementa** a lista de migrações do item "Endpoints e permissões": `V2026_11_14_1000__add_fnrh_no_show.sql` (ver item 2 desta captura). Última migração do projeto: ver item 6.

### 2. `ZenyHotelManager - Schemas, migrações e views de relatório`

**Complementa** a subseção "Schema `fnrh`: fila de submissões e view (M5 E08)" com:

> ### Schema `fnrh`: no-show (M6 E14, 2026-11-14)
>
> Migração única `fnrh/V2026_11_14_1000__add_fnrh_no_show.sql` (D-E14-6), posterior a `V2026_11_13_1000` (a última, em `reservations`). Troca CHECKs com `DROP CONSTRAINT` e `ADD CONSTRAINT` (a migração antiga, aplicada, não se edita):
>
> - `submission_operation_ck` aceita as 6 operações da E08 mais `'NO_SHOW'` (**substitui** "CHECK com as 6 operações" da captura da E08: agora são 7).
> - `submission_last_failure_ck` aceita `NULL` ou os 10 códigos de antes mais `'REMOTE_NO_SHOW'` (**substitui** "CHECK com os 10 códigos": agora são 11).
> - `fnrh.remote_reservation` ganha a coluna `no_show boolean NOT NULL DEFAULT false` e a CHECK **`remote_reservation_closed_ck CHECK (NOT (cancelled AND no_show))`**: a remota é cancelada ou no-show, nunca as duas (o passo do no-show não chama numa cancelada e o do cancelamento não chama numa no-show). **Complementa** a descrição de `fnrh.remote_reservation` (chave `(reservation_id, environment)`, `remote_id`, `precheckin_link`, `cancelled`).
> - **Contrato da view `fnrh.report_submissions`:** a definição da view **não muda**, mas a nota do contrato (cabeçalho de comentário da `V2026_11_10_1100`, já aplicada e que não se edita) ganha complemento no **cabeçalho de comentário da migração nova**: a coluna `operation` passa a incluir `NO_SHOW` e a coluna `last_failure` passa a incluir `REMOTE_NO_SHOW`. Quem lê o contrato da view precisa ler os cabeçalhos das **duas** migrações (o teste `FnrhReportViewsAttackTest` "the migration comment names every…" passou a ler os dois e continua exigindo cada operação e cada situação).
> - A convenção para colunas publicadas que crescem em valores (a coluna não muda de sentido, só ganha valores) fica: a migração que acrescenta o valor repete a nota do contrato no próprio cabeçalho.
>
> Testes: `FnrhNoShowMigrationTest` (aceita `NO_SHOW` e `REMOTE_NO_SHOW`, recusa `BOGUS`, `no_show` falso por padrão, recusa `cancelled` e `no_show` juntos, cabeçalho documenta o contrato da view); `MigrationConventionTest` e `DatabaseMigrationsTest` passam.

### 3. `ZenyHotelManager - Eventos e jobs`

**Complementa** a subseção "Primeiros consumidores dos eventos de reserva e hospedagem e job do envio à FNRH (M5 E08)" (texto da captura da E08):

> - **`ReservationMarkedNoShow`** (publicado pelo `endofday` pelo outbox desde a M6 E11, sem dado pessoal) **ganha o primeiro consumidor de produção: o `fnrh`** (`FnrhSubmissionListeners`, M6 E14), que só grava a `FnrhSubmission` `NO_SHOW` (idempotente pela chave `(reservation_id, operation, event_key)`, `event_key = no-show:v<version>`). Os `FnrhSubmissionListeners` passam de 8 para **9** métodos `@ApplicationModuleListener`. **Substitui** "a E14 o escuta" da captura da E11.
> - O listener roda fora da transação do fechamento (outbox): a falha do Serpro nunca bloqueia o fechamento (RN-22). O envio sai no job `fnrh-submissions-send` (inalterado: 1 min, `lockAtMostFor = PT1H`).
> - O `InventoryListenersQuiescence` já espera pelos `FnrhSubmissionListeners`; nada mudou nele.
> - **Complementa** a nota do curador da E08 sobre consumidores: com a E14, `ReservationMarkedNoShow` também deixa de estar sem consumidor.

### 4. `ZenyHotelManager - Testes de integração`

**Complementa** a nota com:

> - **Helper `messagesOf`** (`src/test/kotlin/com/zeny/hotel/testsupport/LogMessages.kt`, commit `1b4a0bb`): devolve só a parte de mensagem de cada linha do console do Spring Boot (o texto depois do ` : ` do logger), sem data, PID e thread; linhas sem prefixo (continuação, pilha) ficam inteiras.
> - **Armadilha do PID no prefixo do log:** asserção de ausência sobre **valores curtos** (`100`, `1990`) não pode olhar a saída inteira do console. O PID da JVM de testes (`3010000`, que contém `"100"`) e os milissegundos do carimbo entram no prefixo e variam por execução. O primeiro gate da E14 (em `6ad73ab`) falhou num teste **pré-existente** do M5 (`SerproFnrhGatewayRound3Test`) por isso; o testador passou a procurar os valores só na mensagem, via `messagesOf` (`1b4a0bb`). Use `messagesOf(log)` em toda prova "o log não contém dado sensível" com valores curtos.
> - **Limite do helper:** só entende o log de **console**. Com o log em ECS JSON (contextos com o profile `prod` na mesma JVM), uma linha inteira, com `pid` e `@timestamp`, ainda pode bater num valor curto. Sugestão do handoff para a E16: capturar pelo appender do logger ou ler o campo `message` do JSON.
> - **Fechamento com a FNRH no banco isolado (H10):** `EndOfDayFnrhNoShowTest` roda o fechamento real (`@EndOfDayIntegrationTest` com as etapas reais) com a FNRH ligada contra o `FnrhTestServer` e prova: no-show enviado no fechamento; com o Serpro fora do ar, fechamento `COMPLETED` e submissão `PENDING` com `attempts = 1` e `SERVER_ERROR`. Termina com `EndOfDayTestRuns.settle(context)`, devolve o relógio e a configuração da FNRH, e conta só os pedidos da própria reserva no WireMock compartilhado. `EndOfDayFnrhNoShowAttackTest` cobre credenciais recusadas.
> - **Custo:** esse teste sobe **um contexto Spring a mais** no banco isolado. Os no-shows dos outros testes do fechamento agora também gravam `NO_SHOW` (inofensivo com a FNRH desligada).
> - **Dívidas de teste menores** (revisões por tarefa; sem etapa própria): `FnrhRemoteId("")` é aceito por todas as operações (pré-existente; sugerido `require(isNotBlank())`); algumas asserções contam o `FnrhTestServer` inteiro em vez dos pedidos da própria reserva; provas de ausência com `await().during(1s)`; `FnrhAlertTestBase.submit` não limpa as linhas.
> - **Testes que fixam a lista de operações** foram atualizados na E14 (D-E14-7), sem afrouxar exigência: `FnrhReportViewsAttackTest` (lê os cabeçalhos das duas migrações), `FnrhSubmissionTest` (postos `0..5` viram `0..6`) e `FnrhFailureAlertAttackTest` (rótulo `no-show`). Quem acrescentar outra operação deve atualizar os três.
> - Outros testes novos: `FnrhNoShowMigrationTest`, `FnrhNoShowCodesTest`, `SerproFnrhGatewayNoShowTest` (sem Spring), `FnrhNoShowListenerTest` e `FnrhNoShowListenerAttackTest` (reentrega depois de `SENT`, `FAILED` e `DISMISSED`; 8 threads), `FnrhNoShowSendTest`, `FnrhNoShowQueueAttackTest`.

### 5. `ZenyHotelManager - Estado por marco` e Estado do hub `ZenyHotelManager`

**Estado por marco: complementa** "Atualizações por capturas" com a subseção "M6 E14 (2026-11-14)", que **substitui** o estado do M6 da subseção "M6 E11" (captura da E11, item 1). **Hub: substitui** o item de estado do M6.

> - **M6 com E10, E11 e E14 `#concluida`.** A E14 foi concluída em 2026-11-14, com fechamento `ad970fc` ("Conclui a E14 do M6 (no-show na FNRH) e preenche o handoff"), na branch `roadmap/m6-operacao-fechamento`. Demais etapas seguem `#pendente` (E15 aparece `#em-andamento` no arquivo do roadmap).
> - **Próximas elegíveis: E15 e E16** (independentes; a E17 e a E18 também não dependem de outras etapas do marco, e as de governança, manutenção e relatórios seguem a ordem do roadmap). **Substitui** "Próxima elegível: E14" da captura da E11.
> - **A E14 ainda não está integrada na `main`**: a `main` está em `3eeef98` (a conferir no momento da leitura) e a E14 só existe na branch `roadmap/m6-operacao-fechamento`, até o merge local no fim do lote (sem push; o push é do usuário). A E14 tem "Revisão humana: não".
> - **Próxima migração** do projeto: versão posterior a **`V2026_11_14_1000`** (`fnrh/V2026_11_14_1000__add_fnrh_no_show.sql`). **Substitui** "posterior a `V2026_11_13_1000`" da captura da E11.
> - Fatos da E14: plano `docs/superpowers/plans/2026-11-14-m6-operacao-fechamento-e14.md` (6 tarefas, as 5 de código `Risco: alto`); revisão de arquitetura aprovada com notas na rodada 1 (`revisor-arquitetura`, opus; a rodada 0 bloqueou com 2 Importantes, corrigidos: testes existentes que fixam a lista de operações e a nota do contrato da view, e a Task 1 grande demais). Commits: `31b9f10` (início) a `1b4a0bb` sobre `3eeef98`, mais o fechamento `ad970fc`. A Task 4 teve uma rodada de correção (`398d88a`): a revisão achou que um `NO_SHOW` pendente saía mesmo depois da reativação da reserva, e o passo passou a agir pelo estado atual. Revisão final (`revisor-seguranca`, opus) sobre `3eeef98..1b4a0bb`: "With fixes", 0 Critical e nenhum Importante de código; os dois Importantes eram decisões para o usuário (itens (d) e (e) acima) e o resto foi documentação.
> - Gate: `./gradlew build` em `1b4a0bb`, BUILD SUCCESSFUL em 23m 19s, **3962 testes, 0 falhas, 0 ignorados** (inclui `ModularityTest`, ArchUnit, detekt, ktlint, `checkOpenApi` e `koverVerify`). O gate anterior, em `6ad73ab`, falhou num teste pré-existente do M5 por causa do PID no prefixo do log (item 4). `.github/scripts/check-api-breaking.sh main`: nenhuma mudança `ERR` em `/api/v1`. `osv-scanner` 2.7.0 com `-L` nos três lockfiles: 0 Critical/High, 2 Medium e 3 Low pré-existentes; lockfiles e catálogo sem mudança. `check_test_integrity.py --base 3eeef98`: exit 1 com dois apontamentos julgados justificados pela revisão final (`DEV_TESTE_DO_TESTADOR` em `398d88a`, teste do testador invertido pela ruling da guarda; `ASSERCAO_REMOVIDA` em `FnrhSubmissionTest`, postos `0..5` para `0..6`, D-E14-7).
> - Documentos atualizados no repositório pela etapa: SPEC §8.2.17, README ("Envio à FNRH"), `docs/fnrh/api-fnrh-v2.4.md` e a lista da M5 E09.
> - **Decisões da E14 (a) a (e), tomadas pela opção recomendada do orquestrador, sem confirmação do usuário, revisáveis:** (a) caminho em lote da reserva; (b) no-show de reserva reativada antes do envio não vai ao Serpro, pelo estado atual; (c) `POST …/noshow` repetido no `retry` depois de `UNKNOWN_OUTCOME`; (d) `CHECK_IN` e `CHECK_OUT` sem guarda local sobre remota no-show ou cancelada; (e) `CANCEL_RESERVATION` pendente sai mesmo depois da reativação (lacuna da E08). Detalhes no item 1.2. Para "Perguntas abertas" do hub, **complementa** a lista de decisões sem confirmação do usuário com **E14 ((a) a (e))**.
> - **Próximos passos do hub:** além do que a captura da E11 já pede (revisão humana da E10 e da E11), acrescentar: avaliar com o `arquiteto` uma etapa de manutenção do `fnrh` com as guardas (d) e (e) e a validação só dos hóspedes ainda não enviados (decisão E08 (m)).

### 6. Pendências para o curador e o arquiteto

- **`ZenyHotelManager - Arquitetura e estrutura de módulos`** (não é nota afetada por texto novo, mas aponta divergência): a ARCHITECTURE §3.1 lista `hotel` entre as dependências do `fnrh`, e o `FnrhModule.kt` não o declara. O handoff pede ao `arquiteto` conferir; não foi corrigida.
- O critério 3 da E14 e o critério de aceite da M5 E09 ("o no-show, se o M6 já o publicar") pedem ajuste de texto do `arquiteto`, porque o caminho escolhido não é nenhum dos dois formulados.
- O README, a SPEC §8.2.17 e `docs/fnrh/api-fnrh-v2.4.md` já foram atualizados no repositório pela etapa.

## Contexto

Fechamento da etapa E14 do roadmap `roadmap-m6-operacao-fechamento` do ZenyHotelManager, publicado pelo `brain-escriba` a pedido do orquestrador, conforme a regra "Atualização por capturas" do hub. Não havia captura equivalente da E14 em `00 Inbox/` nem em `90 Archive/Inbox/` (busca por nome); as capturas da E08 e da E11 são complementadas, não duplicadas.

## Origem

- Projeto: ZenyHotelManager; repositório `/home/caio/repos/ZenyHotelManager`, worktree `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m6-operacao-fechamento`, branch `roadmap/m6-operacao-fechamento`, fechamento `ad970fc`.
- Fontes lidas: `docs/roadmaps/roadmap-m6-operacao-fechamento.md`, seção "E14 — No-show na FNRH — #concluida" (Evidências e handoff); plano `docs/superpowers/plans/2026-11-14-m6-operacao-fechamento-e14.md` (D-E14-1 a D-E14-7, Global Constraints e Review Focus; Tasks 1 a 3 lidas, as demais pelo handoff); migração `src/main/resources/db/migration/fnrh/V2026_11_14_1000__add_fnrh_no_show.sql`; `src/test/kotlin/com/zeny/hotel/testsupport/LogMessages.kt`. Notas e capturas do vault lidas: `20 Knowledge/ZenyHotelManager - Módulo fnrh.md`, captura da E08 (`8df87866`) e captura da E11 (`df23f14d`).
- Data: 2026-11-14.

## Por que registrar

Alimentar a consolidação do curador: tira da nota do `fnrh` e da captura da E08 a afirmação de que o no-show fica para a M6 E14, documenta o fluxo real e as decisões (a) a (e), as CHECKs e a coluna nova no schema `fnrh`, o primeiro consumidor de `ReservationMarkedNoShow`, a armadilha de teste do PID no log, e fixa o estado do M6 e a próxima migração.

## Limitações e incertezas

- Não li o código de produção do `fnrh` (`FnrhGateway.kt`, `FnrhSubmissionSender.kt`, `FnrhSubmissionListeners.kt`, `domain/FnrhSubmission.kt`): a tentativa de busca no código foi bloqueada pelas restrições do escriba. Nomes de classes, passos e testes vêm do handoff, do plano e da migração; só a migração e `LogMessages.kt` foram lidos por inteiro. Em divergência entre plano, handoff e código, vale o código.
- O número de métodos do `FnrhSubmissionListeners` (9) é dedução (8 da captura da E08 mais o do no-show), não conferida no código.
- A afirmação de que a E15 aparece `#em-andamento` no arquivo do roadmap vem da leitura do título dela no arquivo do worktree; as demais ficam `#pendente`. Para E15 e E16 como "próximas elegíveis" vale a indicação do orquestrador.
- A `main` em `3eeef98` e a não integração da E14 vêm do pedido do orquestrador e do estado do git informado; o merge do lote acontece depois desta captura.
- As decisões (a) a (e) não foram confirmadas pelo usuário. Os resultados do Serpro para o lote só a M5 E09 confirma (sem credencial, Q-12): o caminho em lote é hipótese baseada em `docs/fnrh/api-fnrh-v2.4.md`.
- Dependência local: o worktree pode desaparecer após o merge; o conteúdo útil está acima e os hashes de commit seguem valendo.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Módulo fnrh]]
- [[ZenyHotelManager - Schemas, migrações e views de relatório]]
- [[ZenyHotelManager - Eventos e jobs]]
- [[ZenyHotelManager - Testes de integração]]
- [[ZenyHotelManager - Estado por marco]]
- [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]]
- [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E11 - df23f14d]]
