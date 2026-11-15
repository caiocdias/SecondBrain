---
type: capture
status: archived
created: 2026-11-14
capture_id: f7e211bd-3d35-495d-87c3-33a791c87e48
---
# ZenyHotelManager - atualização m6-operacao-fechamento E16

## Conteúdo capturado

Captura de fechamento da etapa M6 E16 (dívidas de teste herdadas do M5), `#concluida` em 2026-11-14 na branch `roadmap/m6-operacao-fechamento`, fechamento `d83022b` ("Conclui a E16 do M6 (dívidas de teste herdadas do M5) e preenche o handoff"). Resumo do agente a partir do handoff da E16 no roadmap, do plano (D-E16-1 a D-E16-7) e do código de teste lido (`ReservationPlanAssertions.kt`, `LogMessages.kt`). Organizada por nota de tema, dizendo se **substitui** ou **complementa** cada trecho. **Complementa** as capturas da M5 E05 e E11, da M6 E14 ([[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E14 - 998156dc]]) e da M6 E15 ([[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E15 - c139da21]]) e as **substitui** onde dito.

**As decisões (a) a (c) do handoff da E16 foram tomadas pelo orquestrador pela opção recomendada, sem confirmação do usuário** (nenhuma é de arquitetura). Não são opinião do usuário.

A etapa é **só código de teste**: nenhum arquivo de `src/main` mudou (diff vazio de `src/main`).

### 1. `ZenyHotelManager - Testes de integração`

**1.1 Substitui**, na subseção "M5 E05" (e na captura da E05), o item do `ReservationSearchApiTest` ("é intermitente… A sugestão, ainda não aplicada, é aceitar os dois índices nesse filtro") por:

> O teste "every search filter and every list is served by an index…" **não é mais intermitente** desde o `ANALYZE` antes dos `EXPLAIN` (M5 E01) e o filtro "period" segue aceitando os dois índices (`shouldUseOneOf`; decisão E05 (f) do M5, que fica como está). **M6 E16:** nas listas por situação (`IN_HOUSE` e `EXPECTED_NO_SHOWS`, nas duas datas) e na busca só por situação, o teste deixou de aceitar "qualquer índice" e exige que `reservation r` seja lida por um nó de índice com **condição útil** (D-E16-1): **(a)** uma linha `Index Cond:` no próprio nó (ou no `Bitmap Index Scan` filho direto do `Bitmap Heap Scan on reservation r`; num `BitmapAnd` basta um ramo útil, num `BitmapOr` todos precisam ser); **ou (b)** o índice usado é **parcial e o predicado dele cita `status`** (lido em `pg_index`, pelo nome do índice). Nunca `Seq Scan on reservation r`. Qualquer índice que cumpra (a) ou (b) serve, sem nome fixo. O motivo do (b): a busca só por situação não tem predicado de data e nenhum índice tem `status` como coluna-chave, então o melhor plano é o parcial sem `Index Cond`.

**1.2 Complementa** com o apoio de leitura de `EXPLAIN` (`src/test/kotlin/com/zeny/hotel/reservations/ReservationPlanAssertions.kt`, de nível superior e `internal`):

> `reservationIndexNode(plan): ReservationIndexRead?` (índice e se o nó tem `Index Cond`) e a asserção `String.shouldReadReservationsUsefully(isStatusPartial: (String) -> Boolean)`. Só contam as linhas de detalhe do **próprio nó**, antes do primeiro filho (outro nó, `InitPlan`, `SubPlan` ou `CTE`): um `Index Cond` de outra tabela (junção com `reservation_guest` ou `booking`) ou de subplano **não** conta para `reservation r`, e o `Recheck Cond` do heap não é condição de índice. Cobertura por testes de unidade com planos fixos (`ReservationPlanAssertionsTest`, sem Spring). Duas correções vieram dos testes vermelhos do testador: o apoio contava `Index Cond` de `InitPlan`/`SubPlan` e lia só o primeiro ramo do bitmap.

**1.3 Complementa** com a guarda dos índices parciais (D-E16-2), teste `the status lists keep their partial indexes when the date indexes are gone` no `ReservationSearchApiTest`:

> Numa **só conexão e transação do papel dono** (`flyway.configuration.dataSource`), com `SET LOCAL lock_timeout = '2s'` e `SET LOCAL enable_seqscan = off`, o teste faz `DROP INDEX` dos índices de data que competem (`reservation_arrival_idx`, `reservation_departure_idx` e, num laço de no máximo 5 voltas, outro índice não parcial que o `EXPLAIN` ainda mostre; só índices que não sustentam constraint, por `pg_constraint.conindid`), roda os `EXPLAIN` na mesma conexão e exige para `IN_HOUSE`, `EXPECTED_NO_SHOWS` e a busca só por situação o parcial da situação (`reservation_in_house_idx`, `reservation_confirmed_arrival_idx`), com `Index Cond` nas listas com data. **Termina sempre em `ROLLBACK`.** Um parcial apagado ou com predicado errado fica vermelho sem depender das estatísticas. Não reaproveite o `explain()` pela conexão da aplicação: ele esperaria a trava da própria transação. A consulta ao catálogo usa o nome qualificado (`'reservations.<nome>'::regclass`), porque o `EXPLAIN` mostra o nome sem schema. Custo aceito (decisão (b)): um `ACCESS EXCLUSIVE` de milissegundos em `reservations.reservation` no banco compartilhado a cada build, com falha rápida em 2 s (nunca build preso).

**1.4 Complementa** com o `messagesOf` (`src/test/kotlin/com/zeny/hotel/testsupport/LogMessages.kt`), que **substitui** o que a captura da E14 disse dele (só log de console):

> `messagesOf(log)` devolve só a parte de mensagem de cada linha, sem data, PID, thread e nível, para que asserções sobre números curtos não olhem o ruído. **Console do Spring Boot:** fica o texto depois do ` : ` do logger; a linha com o prefixo (data, nível, PID) mas **sem o separador ` : `** não é mais apagada inteira (fica o texto depois do prefixo exato: aplicação opcional, thread e correlação `[…,…]`, sem comer grupos `[..]` do texto, correção do testador). **Linha ECS JSON do logback (profile `prod`):** saem **só** `@timestamp`, `process` (pid e thread), `ecs`, `service` e `log.level`; **todos os demais valores ficam** (`message`, `log.logger`, `error.*`, campos de MDC e pares chave-valor), para que um dado pessoal em qualquer um deles continue visível às asserções negativas (nada de afrouxar o que a asserção enxerga). Linhas sem prefixo (pilha de exceção) e JSON inválido ficam inteiras. Fixture: a linha real do formato `ecs` capturada no gate da E14. Testes em `LogMessagesTest` e `LogMessagesAttackTest`.

**1.5 Complementa** com a armadilha do PID e do logback reinicializado (do handoff, achado do testador):

> Os testes que sobem o profile `prod` (`ProductionProfileApiTest` e dois do `LogMessagesAttackTest`) **reinicializam o logback da JVM inteira** (ECS e `root: INFO`) até o próximo contexto; uma asserção negativa sobre linha DEBUG pode passar à toa, conforme a ordem. Sugestão registrada (não aplicada): restaurar a configuração de log no fim desses testes ou isolá-los num fork.

**1.6 Complementa** com as **dívidas menores de teste** abertas (sem etapa própria; do handoff): o teste "a BOM before the brace…" de `LogMessagesAttackTest` não tem o BOM no literal (usar o escape `﻿`); `messagesOf` trata qualquer objeto JSON como ECS, aceita tokens depois do JSON e chave duplicada (só tratar como ECS com `ecs.version` ou `@timestamp` no topo; ligar `FAIL_ON_TRAILING_TOKENS` e `STRICT_DUPLICATE_DETECTION`); as asserções negativas do teste do MDC `service`/`process` passam também sem linha logada; a guarda dos parciais olha só o primeiro ramo do bitmap, descarta ramo desconhecido num `BitmapOr` e lê a data operacional pelo pool da aplicação enquanto segura a trava (seguro hoje, porque lê só o schema `hotel`); o `LIKE '%status%'` do catálogo é largo; um `Index Cond` parametrizado pela junção conta como útil. (Observação do agente: os dois primeiros pontos sobre `messagesOf` não valem para a versão lida do arquivo em todos os aspectos; o arquivo lido já trata o JSON só como ECS quando é objeto e ignora campos de ruído; o handoff é a fonte da lista, e a conferência fica com o curador.)

**1.7 Complementa** com o apoio de teste do `fnrh` (do handoff e do plano, D-E16-4): as duas cópias de `FnrhSubmissionDismissCompat.kt` (`src/test/kotlin/com/zeny/hotel/fnrh/` e `…/fnrh/domain/`) **saíram**; os testes chamam `FnrhSubmission.dismiss()` de produção, sem instante. Nenhuma chamada de `dismiss` com instante existe mais em `src/test`. Helpers de teste com o mesmo nome (como `FnrhNoShowSendAttackTest.dismiss(submission: UUID)`) ficam.

### 2. `ZenyHotelManager - Docker, observabilidade e CI`

**Complementa** a parte de logs/ECS com o risco achado pelo testador (**Interpretação do agente a partir do handoff**, ainda sem teste de produção): em `prod`, uma chave de MDC chamada `service` ou `process` (ou com esses prefixos e ponto) **faz o escritor ECS do Spring Boot falhar, e a linha de log some**. As chaves de hoje (`userId`, `deviceSessionId`, `traceId`, `spanId`) não colidem. Recomendação do handoff, para o `arquiteto`: registrar a regra "**chave de MDC nunca usa raiz reservada do ECS**" e, numa etapa que possa mexer em `src/main`, um teste que suba o log `prod` com cada constante de MDC.

### 3. `ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)`

**Complementa** a parte de busca e listas (índices das listas por situação): o teste de índices das listas `IN_HOUSE` e `EXPECTED_NO_SHOWS` e da busca só por situação **voltou a guardar os índices parciais** (`reservation_in_house_idx`, `reservation_confirmed_arrival_idx`): exige condição útil sobre `reservation r` (ver itens 1.1 a 1.3) e prova, derrubando os índices de data numa transação desfeita, que os parciais continuam servindo as listas. **Nenhum índice nem consulta de produção mudou.** Fato de produção que o teste agora documenta: a busca só por situação é servida por índice **parcial sem `Index Cond`** (não há predicado de data e nenhum índice tem `status` na chave); se o projeto quiser `Index Cond` também nela, precisa de índice com `status` na chave (mudança de produção, fora desta etapa).

### 4. `ZenyHotelManager - Módulo fnrh`

**Complementa** a armadilha do `FnrhSubmissionDismissCompat.kt` (aberta desde o gate da M5): **foi paga**. As duas cópias de teste saíram e os testes usam o `FnrhSubmission.dismiss()` de produção; o handoff da E16 registra dois `ASSERCAO_REMOVIDA` no `FnrhSubmissionTransitionsTest` (só o argumento ignorado de `dismiss` saiu). **Complementa** também "Estado:" da abertura da nota: "E16 do M6 concluída (dívidas de teste, 2026-11-14); a homologação real segue sendo a E09, `#bloqueada`."

Textos da E15 corrigidos nesta etapa (D-E16-5; nenhuma asserção mudou): o comentário do `ModularityTest` do `fnrh` passou a dizer "Nunca iam nem tabela de outro schema; do `frontdesk`, só a porta dos rótulos (M6 E15)", e o KDoc e o nome de um teste de `RegistrationCardApiTest` passaram a falar em **rótulos** da FNRH, não "códigos FNRH". Isso **fecha** a dívida que a captura da E15 (item 5, "Para a E16") deixou aberta.

### 5. `ZenyHotelManager - Estado por marco` e Estado do hub `ZenyHotelManager`

**Estado por marco: complementa** "Atualizações por capturas" com a subseção "M6 E16 (2026-11-14)", que **substitui** o estado do M6 da subseção "M6 E15" (captura da E15, item 6). **Hub: substitui** o item de estado do M6.

> - **M6 com E10, E11, E14, E15 e E16 `#concluida`.** A E16 foi concluída em 2026-11-14, com fechamento `d83022b`, na branch `roadmap/m6-operacao-fechamento`. Demais etapas seguem `#pendente`. **Substitui** "Próxima elegível: E16" da captura da E15.
> - **Próxima elegível: E17** (corpo mínimo nas escritas de restrição e mesclagem do `guests`; **revisão humana: sim**). Não depende de outras etapas do marco.
> - **Integração na `main`:** o lote E14 a E16 será integrado na `main` por **merge local logo depois desta captura** (o push fica com o usuário). Até o merge, as três etapas só existem na branch `roadmap/m6-operacao-fechamento`.
> - **Próxima migração** do projeto: sem mudança (a E16 só mexe em teste; `git diff --stat` de `src/main` vazio).
> - Fatos da E16: plano `docs/superpowers/plans/2026-11-14-m6-operacao-fechamento-e16.md` (3 tarefas; 1 e 3 `Risco: alto`, 2 `normal`). Revisão de arquitetura aprovada com notas na rodada 1 (`revisor-arquitetura`, opus; a rodada 0 bloqueou com 1 Crítico, a busca só por situação não ter `Index Cond` possível, e 4 Importantes, todos corrigidos). Commits `72a5d11` (início) a `559e25f`, mais o fechamento `d83022b`. As Tasks 1 e 3 tiveram uma rodada de correção cada, pelos testes vermelhos do testador. Revisão final (`revisor-seguranca`, opus) sobre `72a5d11..559e25f`: "Ready to merge: Yes", 0 Critical e 0 Importante.
> - Gate: `./gradlew build` em `559e25f`, BUILD SUCCESSFUL em 21m 25s, **4049 testes, 0 falhas, 0 ignorados**. oasdiff sem `ERR` em `/api/v1`. `osv-scanner` 2.7.0 com `-L` nos três lockfiles: 0 Critical/High, 2 Medium e 3 Low pré-existentes. `check_test_integrity.py --base 72a5d11`: exit 1, tudo julgado justificado pela revisão final (três `ASSERCAO_REMOVIDA` no `ReservationSearchApiTest`, mais fortes no conjunto; dois no `FnrhSubmissionTransitionsTest`; e `SEM_SOUL` em `6689f13`, commit do testador cujo `Soul: testador` ficou colado ao corpo da mensagem, histórico não reescrito).
> - Provas: mutação (consulta de no-shows previstos trocada para forma não indexável: o plano `Index Scan using reservation_arrival_idx on reservation r` só com `Filter`, que passava no teste antigo, fica vermelho; derrubar `reservation_in_house_idx` dentro da guarda também), desfeitas; três rodadas seguidas do `ReservationSearchApiTest` verdes e uma cópia temporária rodada depois do `StayTransitionsApiTest` (ordem conferida pelos carimbos do XML), apagada antes do commit.
> - **Decisões da E16 (a) a (c), tomadas pela opção recomendada do orquestrador, sem confirmação do usuário, revisáveis:** (a) "condição útil" inclui o índice parcial da situação sem `Index Cond`; (b) a guarda dos parciais faz DDL numa transação desfeita a cada build, no banco compartilhado, com `lock_timeout` de 2 s; (c) escopo acrescentado (textos da E15 e `messagesOf` em ECS), com origem nos handoffs da E14 e da E15. Para "Perguntas abertas" do hub, **complementa** a lista de decisões sem confirmação do usuário com **E16 ((a) a (c))**, ao lado de E14 ((a) a (e)) e E15 ((a) e (b)).

### 6. Pendências para o curador e o arquiteto

- Para o `arquiteto`: registrar a regra "chave de MDC nunca usa raiz reservada do ECS" (item 2) e decidir se a lista das dívidas menores do item 1.6 vira etapa de manutenção.
- O curador, ao integrar o item 1.1, deve **substituir** na nota "Testes de integração" a frase de que o `ReservationSearchApiTest` é intermitente e de que a sugestão "ainda não foi aplicada", para não ficar duas versões.

## Contexto

Fechamento da etapa E16 do roadmap `roadmap-m6-operacao-fechamento` do ZenyHotelManager, publicado pelo `brain-escriba` a pedido do orquestrador de etapa, conforme a regra "Atualização por capturas" do hub. Não havia captura equivalente da E16 em `00 Inbox/` (conferido pela listagem do diretório); as capturas da E14 e da E15 são complementadas, não duplicadas.

## Origem

- Projeto: ZenyHotelManager; repositório `/home/caio/repos/ZenyHotelManager`, worktree `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m6-operacao-fechamento`, branch `roadmap/m6-operacao-fechamento`, fechamento `d83022b`.
- Fontes lidas: `docs/roadmaps/roadmap-m6-operacao-fechamento.md` (seção "E16 — Dívidas de teste herdadas do M5 — #concluida", com "Evidências e handoff"); plano `docs/superpowers/plans/2026-11-14-m6-operacao-fechamento-e16.md` (D-E16-1 a D-E16-7, Global Constraints, Review Focus, Tasks 1 a 3); `src/test/kotlin/com/zeny/hotel/reservations/ReservationPlanAssertions.kt` e `src/test/kotlin/com/zeny/hotel/testsupport/LogMessages.kt`.
- Notas e capturas do vault lidas: `20 Knowledge/ZenyHotelManager - Testes de integração.md` (primeiras 50 linhas) e a captura da M6 E15 (`c139da21`).
- Data: 2026-11-14.

## Por que registrar

Alimentar a consolidação do curador: tira a intermitência da lista de problemas dos testes, documenta o critério de "condição útil" do teste de índices e a guarda dos parciais por DDL desfeito, o novo comportamento do `messagesOf` com ECS, o risco de MDC `service`/`process` em `prod`, a dívida do `FnrhSubmissionDismissCompat` paga, as decisões (a) a (c) e o estado do M6.

## Limitações e incertezas

- Não li as notas `Docker, observabilidade e CI`, `Módulo reservations (ciclo de vida…)`, `Módulo fnrh`, `Estado por marco` nem o hub inteiro; nos itens 2 a 5 a "seção" é indicada pela descrição do assunto e o curador localiza o trecho.
- Do código li só `ReservationPlanAssertions.kt` e `LogMessages.kt`; `ReservationSearchApiTest`, `LogMessagesTest`, `LogMessagesAttackTest` e os testes do `fnrh` não foram lidos: o que se diz deles vem do plano e do handoff. Em divergência entre plano, handoff e código, vale o código. O item 1.6 repete a lista de dívidas do handoff; alguns pontos sobre o `messagesOf` talvez já estejam parcialmente tratados no arquivo lido, e não os verifiquei um a um.
- O risco do MDC `service`/`process` em `prod` é achado do testador relatado no handoff, não reproduzido por mim.
- Os números do gate (4049 testes, 21m 25s) são do handoff e foram medidos em `559e25f`; o fechamento `d83022b` só edita o roadmap.
- O merge do lote E14 a E16 na `main` e a E17 como próxima elegível vêm do pedido do orquestrador; o merge acontece depois desta captura.
- As decisões (a) a (c) não foram confirmadas pelo usuário.
- Dependência local: o worktree pode desaparecer após o merge; o conteúdo útil está acima e os hashes de commit seguem valendo.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Testes de integração]]
- [[ZenyHotelManager - Docker, observabilidade e CI]]
- [[ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)]]
- [[ZenyHotelManager - Módulo fnrh]]
- [[ZenyHotelManager - Estado por marco]]
- [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E14 - 998156dc]]
- [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E15 - c139da21]]
