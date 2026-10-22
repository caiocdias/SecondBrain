---
type: capture
status: archived
created: 2026-10-22
capture_id: 52209457-a598-432e-a841-ad4b3ccc8217
---
# ZenyHotelManager - Tempo real (SSE)

## Conteúdo capturado

Texto **literal** do `CLAUDE.md` do repositório ZenyHotelManager, linhas 130–137, no commit `a6c0f03` (2026-10-22): o canal /api/v1/stream: tópicos, publicação, inscrição, protocolo, encerramento e testes. Foi escrito pelos agentes que executaram as etapas do roadmap (M0 E01 a M5 E03); as decisões do usuário aparecem no próprio texto com a data e a indicação "decisão do usuário" (ou "decidida pela opção recomendada em nome do usuário (delegado ao orquestrador)"). Nada foi resumido nem reescrito.

---

- **Tempo real** (SSE, ARCHITECTURE §10, D10, RNF-04, M2 E04; API pública em `shared/Realtime.kt`, implementação em `shared/application/realtime/` — `RealtimeHub`, `RealtimeHistory`, `StreamService` — e `shared/web/StreamController.kt`):
  - **Registrar um tópico:** o módulo declara, na raiz do pacote, `RealtimeTopic("<nome>", XPermissions.Y_READ)` (nome em minúsculas, dígitos e hífen; a permissão de leitura que a inscrição exige) e o publica como bean numa `@Configuration` de `application` (`@Bean fun xRealtimeTopic(): RealtimeTopic = XRealtime.TOPIC`; o do `rooms` fica ao lado do bean das permissões). O boot recusa nome repetido ou permissão que nenhum `ModulePermissions` declara. **Tópico pessoal** (M2 E09): `RealtimeTopic("<nome>")`, sem permissão, aceita qualquer usuário autenticado, que recebe só as mensagens de que é dono (como com `OWN`; publique sempre com `owners`); o único é o `notifications`. Declare também os `type` das mensagens (`<módulo>.<recurso>` em kebab-case, como `rooms.room-status`), que não mudam depois de publicados.
  - **Publicar:** injete `RealtimePublisher` e, **dentro da transação de escrita** do caso de uso que mudou o registro, chame `publish(topic, RealtimeMessage(type, id, version, owners))`. A mensagem só sai no `afterCommit` (sincronização da transação, não o outbox: o buffer é em memória) e a transação desfeita não envia nada; fora de uma transação de escrita, `IllegalStateException`. `owners` (os `UserId` donos do registro) serve só ao escopo `OWN` e nunca vai ao cliente; vazio, só quem tem `ALL` recebe. O payload é só `type`, `id` e `version` (nada de dado pessoal, RN-13): o cliente aplica a mudança ou rebusca o recurso. Publique só quando algo mudou.
  - **Inscrição:** `GET /api/v1/stream?topics=a,b` com o mesmo `Authorization: Bearer` (H8) e, na reconexão, `Last-Event-ID`. Sem tópico, `400 VALIDATION_FAILED`; tópico não registrado, `400 UNKNOWN_STREAM_TOPIC` (campo `topics`); sessão revogada (o access token ainda não venceu), `401 UNAUTHENTICATED`; sem a permissão de algum tópico, `403 PERMISSION_DENIED`. A permissão e o escopo são avaliados na inscrição e guardados na conexão: uma permissão retirada só vale na reconexão. A transação da inscrição (só leitura) termina antes do stream; a conexão não segura conexão de banco.
  - **Protocolo:** cada mensagem é um evento SSE com `event: <tópico>`, `id: <época>-<sequência>` (sequência global crescente; a época é sorteada a cada boot) e `data: {"type":…,"id":…,"version":…}`. A conexão começa por `event: ready` (sem `Last-Event-ID`, ou depois de repor em ordem as mensagens perdidas dos tópicos inscritos que o escopo alcança) ou por `event: reset` (o `Last-Event-ID` é de outro boot, ilegível, à frente da posição ou anterior a uma mensagem que já saiu do buffer de algum tópico inscrito: o cliente recarrega o estado), os dois com `data: {}` e a posição corrente no `id`. O cliente abre o stream, espera o `ready` e só então carrega o estado pela API. Comentários `: heartbeat` a cada `zeny.realtime.heartbeat-interval` (15 s) mantêm a conexão viva nos proxies e fazem o servidor notar o cliente que sumiu.
  - **Encerramento:** no `exp` do access token (o cliente renova e reconecta com o `Last-Event-ID`); na revogação da sessão ou desativação do usuário, depois do commit, pelo evento `DeviceSessionsRevoked` (escutado em processo por `@EventListener`, sem outbox: o efeito é só em memória); quando a sessão abre mais de `zeny.realtime.max-connections-per-session` (3) conexões, sai a mais antiga; quando a fila de envio de uma conexão passa de `buffer-size × tópicos + 64` quadros (cliente que não acompanha); na falha de escrita; e na parada do servidor (o hub é um `SmartLifecycle` que para antes do *graceful shutdown* do Tomcat). O envio de cada conexão roda numa *virtual thread*, então quem publica nunca espera a rede de um cliente lento. A segurança libera o despacho `ASYNC` (o fim da resposta assíncrona), porque a requisição original já foi autorizada.
  - **Configuração** (`zeny.realtime.*`): `buffer-size` (1000 mensagens por tópico, H5), `heartbeat-interval` (PT15S) e `max-connections-per-session` (3). Instância única: o buffer é em memória e o reinício responde `reset` a todos; com mais de uma instância, o caminho é `LISTEN/NOTIFY` (ARCHITECTURE §10). Métrica `zeny_realtime_connections` (conexões abertas). No compose, o Caddy repassa `/api/v1/stream` com `flush_interval -1`.
  - **Testes:** `RealtimeStreamTest` (contexto próprio com `webEnvironment = RANDOM_PORT`, porque o `@IntegrationTest` é servlet simulado, e um cliente SSE de verdade, `testsupport/SseTestClient`; buffer de 8, *heartbeat* de 1 s e 2 conexões por sessão), com o tópico só de teste `example-notes` (`src/test/kotlin/realtimeexample/`, permissão com `OWN`) e o `rooms`; `SessionRevocationEventsTest` confere o evento em cada revogação do `iam` e que só a `SessionRevocations` revoga uma sessão (ArchUnit).

---

## Contexto

Em 2026-10-22 o usuário pediu para enxugar o `CLAUDE.md` do repositório (638 linhas, ~435 KB) e passar o conteúdo para um projeto no Second Brain, de onde os agentes do projeto o leriam por um hook obrigatório. Esta captura é uma de várias, uma por tema. O plano, as decisões da entrevista e a estrutura proposta estão na captura-índice [[2026-10-22 - ZenyHotelManager - migração do CLAUDE.md para o brain - índice e decisões - 03d0ed3e]] (capture_id: 03d0ed3e-788d-43f3-b338-79e3077d799f).

## Origem

- Projeto: ZenyHotelManager (servidor do PMS Zeny Hotel Manager), repositório local `/home/caio/repos/ZenyHotelManager`.
- Arquivo: `CLAUDE.md`, linhas 130–137, commit `a6c0f03` (branch `main`).
- Sessão do Claude Code iniciada no repositório (agente externo), 2026-10-22.

## Por que registrar

É a referência técnica que os agentes do projeto precisam para trabalhar neste tema. Depois da integração, sai do `CLAUDE.md` e passa a viver no brain (decisão do usuário, 2026-10-22).

## Sugestão do agente para a integração

Sugestão, não decisão: uma nota `ZenyHotelManager - Tempo real (SSE)`, ligada pela nota de projeto (hub) do ZenyHotelManager, com este texto (o curador decide o `type` e se divide ou funde com outra captura). Manter o texto técnico como está: caminhos, nomes de classes e códigos de erro são usados pelos agentes ao editar o código.

## Limitações e incertezas

- O texto descreve o código no commit `a6c0f03`; etapas seguintes publicarão capturas de atualização ("ZenyHotelManager - atualização Mx Ey").
- Referências como "SPEC", "ARCHITECTURE §x", "RF-…", "RN-…", "Hn" e "Mx Ey" apontam para `docs/SPEC.md`, `docs/ARCHITECTURE.md` e `docs/roadmaps/` do repositório, que não foram copiados.
- Valores como `zeny`/`zeny`, `zeny_app` e `zeny-app-dev-only`, quando aparecem, são padrões públicos de desenvolvimento local já versionados no repositório, não credenciais de um ambiente real.

## Possíveis conexões

- [[2026-10-22 - ZenyHotelManager - migração do CLAUDE.md para o brain - índice e decisões - 03d0ed3e]]
