---
type: capture
status: archived
created: 2026-11-11
capture_id: 6095f729-34e7-4667-9c48-d112262c6212
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E16

## Conteúdo capturado

Captura de fechamento da etapa M5 E16 (limpar a credencial da FNRH), concluída em 2026-11-11. O texto abaixo é o rascunho do orquestrador, organizado por nota de tema. Em cada nota, a captura indica se o texto **substitui** ou **complementa** uma seção. Os rótulos "Decisão" marcam o que o orquestrador decidiu pela opção recomendada, em nome do usuário e **sem confirmação dele**.

Esta captura vale sobre a captura `2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866` onde tratarem do mesmo trecho (em especial a frase "Estado:" da abertura da nota do módulo fnrh, item 1.1 daquela captura, que o item 1 abaixo atualiza).

---

### 1. `ZenyHotelManager - Módulo fnrh`

**1.1 Substitui** o item "**Limpar a credencial:** no código da E07 não há como apagá-la…" da seção "Configuração cifrada, por ambiente (D-E07-1)" por:

> - **Limpar a credencial (M5 E16):** `POST /api/v1/fnrh/settings/clear-credentials`, sem corpo, com `If-Match` obrigatório (`428` sem ele, `412` com versão velha) e `fnrh.settings.manage`, sem `Idempotency-Key`. Apaga usuário, senha e CPF padrão (as três colunas ficam `NULL`) e desliga a integração; responde `200` com a configuração e o `ETag` novo. **Mantém** o ambiente, o CPF por usuário (`fnrh.requester`, que tem `deactivate` próprio), os ids remotos, o link de pré-check-in cifrado e o `fnrh.integration_call`, que não são credencial. Repetir sobre a configuração já vazia é `200`, mantém o `ETag` e **não grava entrada na trilha** (o `AuditScopes` descarta retrato igual, como no `PUT` sem mudança). Trilha `fnrh.settings.clear-credentials` com o retrato `FnrhSettingsAuditState` (sem usuário, senha nem CPF em claro) e o autor em `audit.audit_entry.user_id`. Religar sem nova credencial dá `422 FNRH_SETTINGS_INCOMPLETE`; a recuperação é informar a credencial de novo. Caso de uso `FnrhSettingsService.clearCredentials(expectedVersion)` sobre `FnrhSettings.clearCredentials()`.
> - **Depois da limpeza, nada sai ao Serpro:** a conexão é relida a cada chamada, e o envio para (`NOT_CONFIGURED` → `STOP`, sem gravar resultado nem gastar tentativa); as submissões ficam `PENDING` (D-E08-5). A limpeza no meio de uma rodada para antes da chamada seguinte, inclusive entre duas chamadas do mesmo `CHECK_IN`; a marca de escrita em curso leva à conciliação quando a integração volta, sem pessoa nem hóspede duplicado (testado).

**1.2 Acrescenta** à tabela "Endpoints e permissões": `POST /api/v1/fnrh/settings/clear-credentials` (`If-Match` obrigatório) -> `fnrh.settings.manage`.

**1.3 Substitui**, na seção "Status e métricas", depois da descrição de `GET /api/v1/fnrh/status`, a lacuna corrigida:

> - Até a M5 E16, o status respondia `500` em qualquer ambiente sem chamada bem-sucedida registrada (instalação nova ou a primeira troca para `PRODUCTION`), e a métrica `zeny_fnrh_last_success_seconds` passava pelo mesmo caminho: `JdbcFnrhCallHistory.lastSuccessAt` fazia `.single()` sobre um `max()` nulo. Corrigido em `6f4e60b` (consulta com a forma da do `lastFailure`, `ORDER BY … LIMIT 1`); teste de regressão `FnrhCallHistoryEmptyTest`.

**1.4 Substitui**, no texto de abertura (Estado), "E07 concluída … e E15 concluída …; o envio por eventos é a E08 e a homologação real é a E09" por:

> E07, E15, E08 e E16 concluídas (configuração, domínios, porta e adaptador, validação local, descrição de gênero, envio assíncrono e a limpeza da credencial); a homologação real é a E09, bloqueada só pela Q-12.

**1.5 Substitui**, em "Notas para a E09", o item "A E09 segue `#bloqueada` (Q-12) e depende de E08 e E16" por:

> A E09 segue `#bloqueada` só pela Q-12: E08 e E16 estão concluídas.

**1.6 Acrescenta** a "Limitações":

> O `FnrhSettingsResponse` devolve o `username` em claro (E07), o que diverge da ARCHITECTURE §12 ("nunca devolvida na API"); a E16 não mudou isso (depois da limpeza ele vem nulo).

---

### 2. Notas `ZenyHotelManager - Eventos e jobs` (regras que a FNRH provou para toda integração) e `ZenyHotelManager - Segurança, autenticação e autorização`

**2.1 Complementa** a regra de credencial de integração com o texto novo da ARCHITECTURE §12 (linha "Credencial"), decisão D-E16-7:

> Toda integração com credencial tem a ação `POST …/clear-credentials` com `If-Match`, sem `Idempotency-Key`; ela apaga a credencial e desliga a integração, mantendo o ambiente e o que não é credencial; repetir é `200` e mantém o `ETag`; religar exige credencial nova; a trilha fica sem segredo nem usuário. A M5 E16 é a primeira a seguir a regra, e os provedores de M7 e M8 nascem com ela (R6).

---

### 3. Nota `ZenyHotelManager - Estado por marco` e Estado do hub `10 Projects/ZenyHotelManager.md`

**3.1 Substitui** o estado do M5:

> E01 a E08, E13, E14, E15 e **E16** concluídas (E16 em 2026-11-11). Próxima: **E10** (revisão humana: sim; cria o segundo mecanismo de autenticação, o token do agente de impressão), depois E11 e o gate E12. E09 `#bloqueada` só pela Q-12. Revisão humana pendente: E13 e E07.

**3.2 Acrescenta**, à lista das decisões sem confirmação do usuário:

> Lote E16 ((a) a (d)), decididas pela opção recomendada em nome do usuário em 2026-11-11: (a) forma da ação `POST …/clear-credentials` como regra de toda integração; (b) o que fica (ambiente, CPF por usuário, ids remotos, link, registro de chamadas); (c) repetição `200` sem entrada nova na trilha; (d) a correção do `500` do status (defeito da E07) dentro da E16.

**3.3 Git:** a E16 está na branch `roadmap/m5-recepcao-fnrh`; o lote E16 + E10 será integrado na `main` por merge local no fim do lote (push do usuário).

---

### 4. Hub `10 Projects/ZenyHotelManager.md`, "Próximos passos"

**Substitui** "Depois, executar E16 e E10 do M5" (e o trecho equivalente "Concluir a E08 e executar E16 e E10 do M5") por:

> Executar a E10 do M5 (revisão humana: sim) e, depois, E11 e o gate E12.

## Contexto

Fechamento da etapa E16 do roadmap M5 (recepção e FNRH) do servidor ZenyHotelManager, executada pelo orquestrador na branch `roadmap/m5-recepcao-fnrh`. Resumo do agente: a etapa acrescentou a ação de limpar a credencial da FNRH, testes de ataque a ela e ao envio depois da limpeza, e corrigiu um `500` do status herdado da E07.

## Origem

- Projeto: ZenyHotelManager, repositório `/home/caio/repos/ZenyHotelManager`; worktree `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m5-recepcao-fnrh`, branch `roadmap/m5-recepcao-fnrh`.
- Handoff: seção E16 de `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`.
- Plano: `docs/superpowers/plans/2026-11-11-m5-recepcao-fnrh-e16.md`.
- Rascunho do orquestrador: `.superpowers/sdd/2026-11-11-m5-recepcao-fnrh-e16/captura-e16.md` (no worktree).
- Commits: `7eac7d0..67c721a` e o fechamento da etapa (hash do fechamento não informado no rascunho); correção do status em `6f4e60b`.
- Data: 2026-11-11.

## Por que registrar

O hub e as notas de tema ainda descrevem a limpeza da credencial como inexistente e a E16 como pendente; o curador deve consolidar estes trechos ao processar a Inbox.

## Limitações e incertezas

- Conteúdo transcrito do rascunho do orquestrador; os trechos citados das notas atuais não foram conferidos um a um pelo escriba, e o curador deve localizar cada seção pelo título citado.
- O código, o handoff e o plano ficam no worktree do repositório; nada foi copiado para a Inbox.
- As decisões (a) a (d) da E16 não tiveram confirmação do usuário.
- A revisão humana de E13 e E07 segue pendente (conforme o rascunho).

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Módulo fnrh]]
- [[ZenyHotelManager - Eventos e jobs]]
- [[ZenyHotelManager - Segurança, autenticação e autorização]]
- [[ZenyHotelManager - Estado por marco]]
- [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]]
