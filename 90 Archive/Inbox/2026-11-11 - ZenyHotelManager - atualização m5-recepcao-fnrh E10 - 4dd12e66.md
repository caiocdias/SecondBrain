---
type: capture
status: archived
created: 2026-11-11
capture_id: 4dd12e66-191b-406d-a974-4ae7dca3e15f
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E10

## Conteúdo capturado

Captura de fechamento da etapa M5 E10 (impressão: agentes, impressoras, fila e token do agente), concluída em 2026-11-11. O texto abaixo vem do rascunho do orquestrador e de `docs/ARCHITECTURE.md` (§8.1, §8.3, §10, §12, §13, §14), organizado por nota de tema. Em cada nota, a captura diz se o texto **substitui**, **complementa** ou **cria**. Os pontos "Decisão" (D-E10-1 a 11 e o lote (a) a (f)) foram tomados pelo orquestrador pela opção recomendada, em nome do usuário e **sem confirmação dele**.

Esta captura vale sobre as capturas `E08 - 8df87866`, `E08 (revisão humana) - 65d0d4ff` e `E16 - 6095f729` onde tratarem do mesmo trecho (em especial o Estado do M5 e a frase de "Próximos passos" do hub, que o item 6 e o item 7 abaixo atualizam depois da E16).

---

### 1. Nota NOVA `ZenyHotelManager - Módulo printing` (texto proposto, no modelo da nota do módulo fnrh)

> Referência técnica do projeto [[ZenyHotelManager]]. Impressão: cadastro de agentes e impressoras, fila de jobs, protocolo de entrega ao agente (SSE e long-poll) e a credencial de serviço do agente. Estado: M5 E10 concluída (2026-11-11); a E11 (documentos: ficha, extrato e confirmação) é a primeira consumidora da `PrintingApi`. O agente de impressão em si fica em repositório próprio e segue o protocolo descrito aqui e em ARCHITECTURE §14.
>
> Referências como "ARCHITECTURE §x", "SPEC §x", "D-E10-n" e "Hn" apontam para `docs/ARCHITECTURE.md`, `docs/SPEC.md` (§8.2.18), `docs/roadmaps/roadmap-m5-recepcao-fnrh.md` ("Decisões do lote E10") e `docs/superpowers/plans/2026-11-11-m5-recepcao-fnrh-e10.md` do repositório.
>
> #### Camada e dependências
>
> - Camada Plataforma. Pacote `com.zeny.hotel.printing`, com `PrintingModule.kt` na raiz.
> - `allowedDependencies`: só `shared` (teste exato no `ModularityTest`). A E11 acrescenta `hotel` (e `files`, H18).
> - Nunca escuta eventos de negócio, não importa `iam` nem `notifications` (sem alerta de falha: o `FAILED` fica na lista e na métrica).
>
> #### Pacotes
>
> - Raiz (API pública): `PrintingModule`, `PrintingApi` (`enqueue(NewPrintJob(printerId, documentType, content))`, conteúdo até 5 MiB, `zeny.printing.max-content-bytes`; **não confere permissão**, quem chama se autoriza), `PrintingPermissions` e `PrintingTypes.kt` (`PrinterKind` `THERMAL_ESCPOS`/`A4_PDF`, cada um com o tipo de mídia; `PrintJobStatus`; `PrintingErrorCodes`).
> - `domain`: `PrintAgent`, `Printer`, `PrintJob`. `application`: `PrintAgentsService`, `PrintJobsService`, `PrintAgentJobsService`, `PrintAgentConnections`, `PrintAgentStreams`, `PrintJobsMaintenance`, `PrintingAudit`. `infrastructure`: persistência, `PrintAgentRealm`, `PrintingProperties`, o job agendado e `PrintingMetrics`. `web`: administração, fila e rotas do agente.
>
> #### Schema `printing` e migrações
>
> - `print_agent` (hash do token, `token_generation`, `active`, `last_seen_at`), `printer`, `print_job` (posição por sequence, `content` em `bytea` cifrado, `content_purged_at`, `delivered_to`, `failure_code`), com CHECKs de estado. Migrações `V2026_11_11_1000` e `V2026_11_11_1001` na pasta `printing/`.
> - O conteúdo é cifrado pelo `ContentCipher`, com o id do job como dado associado, e fica só nessa coluna. A rotação de chave do anel ainda não o re-cifra (pendência da M8 E15); na prática ele dura até cerca de 48 h (ARCHITECTURE §8.3).
>
> #### Agente e token (D-E10-1 e D-E10-11)
>
> - Token `zpa_` + 32 bytes de `SecureRandom` em base64url; no banco só o SHA-256 em hex. Aparece **uma vez**, na criação e na rotação (`Cache-Control: no-store`, sem `@Idempotent`, porque a resposta guardada teria o token em claro). A rotação invalida o anterior na hora; a desativação apaga o hash.
> - `token_generation` sobe a cada emissão e é o `credentialStamp` do `ServicePrincipal`, conferido a cada chamada e a cada volta do stream. O realm recusa sem consulta o token sem o prefixo `zpa_`.
> - O contato (`last_seen_at`, no máximo uma vez por minuto) é gravado numa transação curta, fora do versionamento do cadastro e **sem trilha**, por ser registro técnico, como a sessão de dispositivo do `iam`.
> - O mecanismo de autenticação em si está em [[ZenyHotelManager - Segurança, autenticação e autorização]] (item 2 desta captura).
>
> #### Rotas e permissões
>
> | Rota | Permissão e regras |
> |---|---|
> | Administração de agentes e impressoras | `printing.agents.manage` (só o Administrador) |
> | `GET /api/v1/printers` | `printing.jobs.read` (Gerente e Recepcionista) |
> | `POST /api/v1/print-jobs` | `printing.jobs.manage` (Gerente), `@Idempotent`, conteúdo em base64 com preenchimento, até 700 KiB (`zeny.printing.max-manual-content-bytes`, abaixo do limite de corpo da idempotência) |
> | `GET /api/v1/print-jobs` | cursor, **sem o conteúdo** |
> | `/api/v1/print-agents/me/…` (identidade, `jobs/stream`, `jobs?wait=`, `jobs/{id}/content`, `jobs/{id}/ack`) | só o esquema `printAgentToken` |
>
> - O `{id}` das rotas de administração aceita só `[0-9a-fA-F-]+`.
> - Códigos de problema em `PrintingErrorCodes` (entre eles `PRINT_JOB_NOT_ACKNOWLEDGEABLE`, `409`).
>
> #### Fila e entrega (ARCHITECTURE §14)
>
> - Ciclo: `PENDING` → `SENT` → `PRINTED` ou `FAILED`. O job nasce `PENDING` com uma **posição** (sequence); a reivindicação por um agente o passa a `SENT` (`attempts + 1`, `sent_at`, `delivered_to`). Só entram na entrega os `PENDING` de impressoras **ativas** do agente autenticado, em ordem de posição e sem filtro de posição.
> - Reivindicação atômica: `SELECT … FOR UPDATE SKIP LOCKED`, com `version`; duas conexões nunca levam o mesmo job. Consulta ao banco a cada 1 s (`zeny.printing.delivery-poll-interval`); não há sinal em memória nem `LISTEN/NOTIFY` (alternativas descartadas por terem dois caminhos de entrega ou peça nova de runtime).
> - SSE em `GET /print-agents/me/jobs/stream`: evento `job`, `id` = posição, `data` com `id`, `printerId`, `documentType`, `mediaType`, `attempts` e `createdAt`; o conteúdo vem de `GET …/jobs/{id}/content` (só do job `SENT` entregue àquele agente e de impressora dele). `: heartbeat` a cada 15 s. Na conexão, reenvia os `SENT` sem confirmação de posição maior que o `Last-Event-ID` (todos, sem ele; valor não numérico vale como ausente) e reivindica os `PENDING`. Escreve `: ping` antes de cada reivindicação, reivindica **um job por vez** e, se a escrita falha, devolve o job a `PENDING` sem gastar tentativa (`printing.job.release`). Um stream por agente (o novo despeja o anterior); acaba em `stream-max-duration` (30 min), quando o agente deixa de ser válido (inativo ou token trocado) e na parada do servidor.
> - Long-poll em `GET /print-agents/me/jobs?wait=` (0 a 30 s, padrão 25): `200 []` no vazio e quando despejado pelo limite de conexões ou pela parada do servidor (o agente não deve repetir sem pausa). `zeny.printing.max-connections-per-agent` (2) vale só para os long-polls. Se o servidor já fechou a resposta por tempo quando os jobs são reivindicados, devolve-os a `PENDING` sem gastar tentativa; a resposta perdida depois de enviada só volta pelo `ack-timeout`, gastando uma tentativa.
> - Confirmação `POST …/jobs/{id}/ack`, corpo `{result: "PRINTED"|"FAILED", failureCode}`, `204`: `result` só como texto; `failureCode` opcional, `[A-Z][A-Z0-9_]{0,49}`, nunca texto livre. Job de impressora do agente que não está `SENT` entregue a ele: `409 PRINT_JOB_NOT_ACKNOWLEDGEABLE`; job de outro agente ou inexistente: `404`. O agente deduplica pelo id na reentrega e confirma de novo sem imprimir.
>
> #### Manutenção, validade e métrica
>
> - Job `printing-jobs-maintenance` (1 min, ShedLock, `lockAtMostFor` PT10M, adiado nos testes por `PRINTING_MAINTENANCE_DEFERRED`; intervalo `zeny.printing.maintenance-interval`): `SENT` sem confirmação em `ack-timeout` (2 min) volta a `PENDING` com posição nova (passa do `Last-Event-ID`) e, na reivindicação de número `max-attempts` (3), vira `FAILED`/`ACK_TIMEOUT`; `PENDING` com mais de `pending-ttl` (24 h) vira `FAILED`/`EXPIRED`; `PENDING` e `SENT` de impressora inativa, ou de impressora ativa de agente desativado, viram `FAILED`/`PRINTER_INACTIVE`; o conteúdo é apagado (`NULL`, `content_purged_at`) `content-retention` (24 h) depois do fim (o expurgo repetido não move o instante). Uma transação por job, com `lockById`; confirmação e manutenção travam a linha, então quem chega depois vê o estado novo.
> - Métrica `zeny_printing_jobs{status}` (gauge: `PENDING` e `SENT` da fila e `FAILED` só dos terminados dentro de `content-retention`). Sem alerta. A listagem e os candidatos da manutenção usam **projeção sem o conteúdo**.
>
> #### Limites conhecidos
>
> - Com a conexão meio aberta e o agente fora do ar, um job pode virar `FAILED`/`ACK_TIMEOUT` em cerca de 6 min.
> - O registro de conexões (um stream por agente, limite de long-polls, despejo, encerramento na parada) é por instância; a entrega e a reivindicação valem com várias instâncias.
> - `claimPending` e `unackedSent` ainda carregam o conteúdo; `PrintingProperties` fica em `infrastructure`.
> - Fallback previsto na ARCHITECTURE §14: clientes desktop podem imprimir localmente o PDF devolvido pela API.
>
> #### Proveniência (sugestão ao curador)
>
> Esta captura, com o texto de ARCHITECTURE §8.1, §8.3, §10, §12, §13 e §14 e o rascunho do orquestrador.

---

### 2. Nota `ZenyHotelManager - Segurança, autenticação e autorização`

**Complementa**, na seção "Atualizações por capturas" (nova subseção, depois de "Permissões do `fnrh` e regras novas (M5 E07, 2026-11-05)"), e vale sobre o primeiro marcador "**Segurança e autenticação**" do texto literal, que diz que todo `/api/**` exige o JWT de usuário e que não há Basic nem formulário. O texto novo (ARCHITECTURE §8.1, D-E10-1):

> - **Credencial de serviço (M5 E10):** o agente de impressão e as integrações de entrada usam uma segunda forma de autenticação, uma porta do `shared`: cada módulo implementa um `ServiceCredentialRealm` (`name`, `pathPrefix`, `openApiScheme`, `authenticate(token): ServicePrincipal?`), e o `ServicePrincipal(realm, id, credentialStamp)` leva um carimbo opaco que muda quando a credencial é trocada. A `SecurityConfiguration` monta sempre a cadeia `serviceSecurityFilterChain` (`@Order(1)`, antes da de usuário), com um matcher por prefixo de realm (`PathPatternRequestMatcher`, o mesmo do MVC; sem realm, nunca casa). O filtro lê só `Authorization: Bearer` e, sem token ou com token recusado, responde `401 UNAUTHENTICATED` pelo `ProblemWriter` (RFC 9457, `WWW-Authenticate: Bearer`); sem sessão, CSRF, Basic nem formulário. Um JWT de usuário num caminho de realm é recusado; um token de realm fora do prefixo cai na cadeia de usuário e também é recusado. O prefixo é validado como literal na partida (sem `?`, `..`, `#`, espaço ou curinga) e a partida falha se dois prefixos se sobrepõem. Falha de infraestrutura ao autenticar vira `500` genérico, nunca `401`. O `CurrentActor` do `iam` não reconhece o principal de serviço (as escritas do agente são do ator sistema). O `OpenApiConfiguration` aplica o esquema do realm às operações do prefixo. Alternativa descartada: a cadeia dentro do `printing` (duplicaria o `ProblemWriter`, interno do `shared`, e espalharia segurança por módulo de plataforma).
> - **Token do agente de impressão** (`printAgentToken`, só em `/api/v1/print-agents/me/`): `zpa_` + 32 bytes, só o SHA-256 guardado, exibido uma vez; detalhes no item 1 desta captura. O endpoint de realm novo **não** é público: ele não entra na lista `PUBLIC_API_ENDPOINTS` do `ApiSecurityTest` e leva o esquema `printAgentToken` no contrato, não `security: []`.
> - **Permissões novas:** `printing.agents.manage` (Administrador), `printing.jobs.read` (Gerente e Recepcionista) e `printing.jobs.manage` (Gerente). Nenhuma é sensível.
> - **Regra para M7 e M8:** toda credencial de serviço (webhooks, channel manager etc.) entra como realm, não como mais um caso na cadeia de usuário.

Também **complementa** a seção sobre cifragem (ARCHITECTURE §8.3, citada no hub): o conteúdo dos jobs de impressão está entre os valores cifrados que ainda não têm job de rotação (pendência da M8 E15); ver item 1.

---

### 3. Nota `ZenyHotelManager - Tempo real (SSE)`

**Complementa**, em nova seção "Atualizações por capturas" (a nota ainda não a tem), depois do marcador "**Tempo real**" do texto literal, com o que a ARCHITECTURE §10 diz:

> - **Segundo SSE, o do agente de impressão (M5 E10):** `GET /api/v1/print-agents/me/jobs/stream`, autenticado pelo token do agente, **fora do `RealtimeHub`**: sem broadcaster em processo e sem buffer circular. O `Last-Event-ID` é a posição persistida do job; cada conexão consulta a fila no banco a cada 1 s (`zeny.printing.delivery-poll-interval`); heartbeat `: heartbeat` a cada 15 s; duração máxima 30 min; um stream por agente (o novo despeja o anterior). A reivindicação (`FOR UPDATE SKIP LOCKED`) vale com uma ou várias instâncias, mas o registro de conexões é em memória e vale por instância. O encerramento na parada do servidor é de um `SmartLifecycle` próprio (`PrintAgentConnections`), que para antes do *graceful shutdown*. Protocolo completo em [[ZenyHotelManager - Módulo printing]].
> - **Testes:** no modelo do `RealtimeStreamTest` (contexto com `webEnvironment = RANDOM_PORT` e cliente SSE real); o `SseTestClient` ganhou `openPath` para abrir um caminho qualquer com um cabeçalho de autorização próprio.

---

### 4. Nota `ZenyHotelManager - Eventos e jobs`

**Complementa** a lista de jobs do segundo marcador do texto literal ("Jobs do `shared`: …"), que não menciona o `printing`, e a subseção "Padrão de integração e jobs previstos (revisão dos roadmaps, 2026-11-06)" de "Atualizações por capturas":

> - Do `printing`: `PrintingJobsMaintenance` (ShedLock `printing-jobs-maintenance`, a cada `zeny.printing.maintenance-interval`, 1 min; `lockAtMostFor` PT10M; adiado nos testes por `PRINTING_MAINTENANCE_DEFERRED`). Reenvio dos `SENT` sem confirmação e limite de tentativas, validade dos `PENDING`, jobs de impressora inativa ou de agente desativado e expurgo do conteúdo, uma transação por job com a linha travada (regras no item 1). Escrita técnica do ator sistema; sem alerta por `notifications` (o `printing` não depende dele).

---

### 5. Nota `ZenyHotelManager - Testes de integração`

**Complementa** o parágrafo "**Testes de integração:**" do texto literal (onde estão `@IntegrationTest` e a lista dos jobs adiados) e a seção "Atualizações por capturas":

> - O `@IntegrationTest` (e um contexto montado à mão) passa a adiar também `PRINTING_MAINTENANCE_DEFERRED`, o job `printing-jobs-maintenance`.
> - **Lição da Task 10:** o `InitialAdminTest` troca a senha do administrador semente no banco compartilhado; teste que faz login real deve criar um administrador próprio e não usar o `TestAdmin`.
> - **Lição da Task 2:** o `ktlintFormat` converte `\uXXXX` em literal no fonte; para um caractere invisível num teste, use `0x200B.toChar()` (um U+FEFF se perdeu assim).
> - Testes do SSE do agente de impressão seguem o `RealtimeStreamTest` (item 3).

---

### 6. `ZenyHotelManager - Estado por marco` e Estado do hub

**Substitui** a linha de estado do M5 (a mais recente é a da captura E16, item 3.1) por:

> M5 em andamento: E01 a E08, E10, E13, E14, E15 e E16 concluídas (E16 e E10 em 2026-11-11). Próxima: **E11** (documentos: ficha, extrato e confirmação), depois o gate E12. E09 `#bloqueada` só pela Q-12. **Revisão humana da E10:** feita na entrevista do fim do lote de 2026-11-11, cujo resultado vai, se o usuário responder, num complemento desta captura; enquanto isso, **pendente**. Revisão humana de E13 e E07 também pendente.

**Acrescenta** ao "Estado por marco" a descrição da E10 (formato das linhas "Desde a E…"):

> Desde o M5 E10 existe o módulo `printing` (camada Plataforma; depende só de `shared`): agentes de impressão e impressoras em `/api/v1/print-agents` e `/api/v1/printers`, fila de jobs (`PrintingApi.enqueue`, `POST /api/v1/print-jobs`, `GET /api/v1/print-jobs`), o segundo mecanismo de autenticação do projeto (token de serviço do agente, realm em `/api/v1/print-agents/me/`), a entrega por SSE ou long-poll com confirmação, o reenvio e o expurgo pelo job `printing-jobs-maintenance` e a métrica `zeny_printing_jobs` (nota [[ZenyHotelManager - Módulo printing]]).

**Acrescenta** à lista das decisões sem confirmação do usuário (Perguntas abertas do hub):

> Lote E10 ((a) a (f), mais D-E10-1 a 11 do plano), decididas pela opção recomendada em nome do usuário em 2026-11-11; ver "Decisões do lote E10" em `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`. As decisões (a) a (f) não estão reproduzidas aqui: o curador as lê no roadmap.

**Git:** o lote E16 + E10 foi integrado na `main` por merge local em 2026-11-11 (o hash vem no relatório do orquestrador, não informado no rascunho); o push é do usuário. Esta captura vale sobre o item 3.3 da captura E16 ("será integrado").

---

### 7. Hub `10 Projects/ZenyHotelManager.md`

- **Acrescenta**, em "Notas do projeto", subseção "Módulos", depois de [[ZenyHotelManager - Módulo fnrh]]: `- [[ZenyHotelManager - Módulo printing]]: agentes, impressoras, fila de impressão e o token do agente. Leia antes da E11.`
- **Substitui**, em "Próximos passos", "Executar a E10 do M5 (revisão humana: sim) e, depois, E11 e o gate E12" (texto da captura E16) por: "Executar a E11 do M5 e o gate E12 pelo `claude --agent orquestrador`."
- **Substitui**, no "Estado" do hub, a frase da próxima etapa e a lista das concluídas conforme o item 6.
- **Acrescenta** a "Atualização por capturas": `printing` já tem nota de módulo (o hub previa a nota nova para o módulo).

## Contexto

Fechamento da etapa M5 E10 do servidor ZenyHotelManager, executada pelo orquestrador na branch `roadmap/m5-recepcao-fnrh`. Resumo do agente: a etapa criou o módulo `printing`, o realm de credencial de serviço do `shared` e o token do agente de impressão, a fila com entrega por SSE e long-poll, a manutenção agendada e a métrica, com ajustes de revisão final (projeção sem conteúdo, devolução do long-poll, documentação).

## Origem

- Projeto: ZenyHotelManager, repositório `/home/caio/repos/ZenyHotelManager`; worktree `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m5-recepcao-fnrh`, branch `roadmap/m5-recepcao-fnrh`.
- Rascunho do orquestrador: `.superpowers/sdd/2026-11-11-m5-recepcao-fnrh-e10/captura-e10.md` (no worktree).
- Plano: `docs/superpowers/plans/2026-11-11-m5-recepcao-fnrh-e10.md` (D-E10-1 a 11). Handoff e "Decisões do lote E10": `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`.
- Texto de referência: `docs/ARCHITECTURE.md` §8.1, §8.3, §10, §12 (linha "Impressão" da tabela), §13 (job `printing-jobs-maintenance`) e §14; `docs/SPEC.md` §8.2.18; `README.md`, seção "API".
- Commits da etapa: `3d25de0..538d408` e o fechamento (hash do fechamento não informado). Data: 2026-11-11.
- Notas do vault lidas: `ZenyHotelManager - Módulo fnrh` (modelo), `Segurança, autenticação e autorização`, `Tempo real (SSE)`, `Eventos e jobs`, `Testes de integração`, `Estado por marco`, o hub e a captura E16.

## Por que registrar

O hub e as notas de tema não conhecem o módulo `printing`, o realm de credencial de serviço, o segundo SSE nem o job de manutenção da fila; o hub ainda lista a E10 como próxima. O curador consolida estes trechos ao processar a Inbox; a E11 depende do módulo.

## Limitações e incertezas

- O texto da nota nova foi composto a partir do rascunho do orquestrador e da ARCHITECTURE (§8.1, §8.3, §10, §12 a §14), que se confirmam entre si. O escriba **não leu** `docs/SPEC.md` §8.2.18, o parágrafo "Impressão" do README (seção "API"), o handoff da E10 nem o bloco "Decisões do lote E10" do roadmap: nomes de colunas, códigos de erro além dos citados, números das migrações e as decisões (a) a (f) seguem o rascunho e a ARCHITECTURE, e o curador deve conferi-los no repositório.
- A referência às seções das notas existentes foi feita pelos títulos e marcadores que o escriba leu (no `Estado por marco`, só até a abertura de "Atualizações por capturas"; no hub, o trecho entregue pelo hook, cortado antes do fim).
- As decisões do lote E10 não tiveram confirmação do usuário; a revisão humana da E10 está pendente e a de E13 e E07 também.
- O hash do merge na `main` não consta do rascunho. Código, plano e handoff ficam só no worktree; nada foi copiado para a Inbox.
- O item 2 afirma que as rotas do realm não entram em `PUBLIC_API_ENDPOINTS`: é inferência do agente a partir da ARCHITECTURE (esquema aplicado às operações do prefixo), não verificada no `ApiSecurityTest`.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Módulo fnrh]]
- [[ZenyHotelManager - Segurança, autenticação e autorização]]
- [[ZenyHotelManager - Tempo real (SSE)]]
- [[ZenyHotelManager - Eventos e jobs]]
- [[ZenyHotelManager - Testes de integração]]
- [[ZenyHotelManager - Estado por marco]]
- [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E16 - 6095f729]]
- [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]]
