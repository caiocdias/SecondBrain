---
type: capture
status: archived
created: 2026-11-15
capture_id: cb3979d0-82db-4bb4-bf98-0a7b8630e398
---
# ZenyHotelManager - atualização m6-operacao-fechamento E17

## Conteúdo capturado

Captura de fechamento da etapa M6 E17 (corpo mínimo nas escritas de restrição e mesclagem do `guests`), `#concluida` em 2026-11-15 na branch `roadmap/m6-operacao-fechamento`, com gate em `bcb06f1`. Resumo do agente a partir do handoff da E17 no roadmap (seção "E17 — Corpo mínimo nas escritas de restrição e mesclagem do `guests` — #concluida"). Organizada por nota de tema, dizendo se **substitui** ou **complementa** cada trecho. **Complementa** as capturas da M6 E15 ([[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E15 - c139da21]]) e da M6 E16 ([[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E16 - f7e211bd]]) e as **substitui** onde dito.

**A decisão (a) do handoff (forma do contrato) é de arquitetura e está pendente na entrevista do usuário.** As decisões (b) a (d) foram tomadas pela opção recomendada do orquestrador, sem confirmação do usuário; não são opinião do usuário.

### 1. `ZenyHotelManager - Módulo guests`

**1.1 Substitui** a "Lacuna conhecida (E15 (h))", que diz que `restrict`, `lift-restriction` e `merge` devolvem o perfil inteiro com a permissão da escrita:

> **A lacuna está fechada na M6 E17.** `POST /api/v1/guests/{id}/restrict`, `POST …/lift-restriction` e `POST …/merge` continuam exigindo só a permissão da própria escrita, mas o corpo da resposta passa a depender de `guests.profiles.read`. Com ela, devolvem `GuestResponse` (o perfil inteiro, como antes). Sem ela, devolvem `GuestWriteSummaryResponse {id, restricted}`, sem nome, documento, contato, dado sensível, descrição de gênero nem restrição alimentar. A versão vai no `ETag` nos dois casos. No `merge`, os dois campos são do **sobrevivente**, e `restricted` inclui a restrição herdada do absorvido.

**1.2 Complementa** a "Lista de restrição" e a "Mesclar" com a mesma regra (corpo mínimo sem `guests.profiles.read`; perfil inteiro com ela). Para o conteúdo do mínimo: `status` (sempre `ACTIVE` num `200`) e `updatedAt` (sem consumidor) ficaram de fora, e acrescentar campo depois é aditivo. Consequências de uso: uma role só com `guests.profiles.merge` fica sabendo, pelo UUID, se o sobrevivente está restrito; e ela não obtém o `ETag` do sobrevivente pela API, porque o `GET` e o `duplicate-candidates` exigem leitura.

**1.3 Complementa** a "API" do módulo com a mecânica (ARCHITECTURE §8.2):

> A decisão fica no **caso de uso**. `GuestService.restrict`, `GuestService.liftRestriction` e `GuestMergeService.merge` devolvem `GuestWriteResult(id, restricted, version, profile: GuestView?)`. Depois do `require` da escrita, e na mesma transação, o helper `Guest.writeResult(authorization)` (`guests/application/GuestsSupport.kt`) pergunta `grantOrNull(guests.profiles.read)`. Sem a permissão, o `GuestView` nem é montado, e nada é decifrado. O controller (`guests/web/GuestsController.kt`) só traduz e não recebe `Authorization`. A escrita e a trilha não mudam (o `AuditAspect` não lê o retorno); um `lift` num perfil fora da lista devolve o corpo mínimo e não grava entrada de trilha. O helper ficou num 5º arquivo de produção, além dos 4 do plano (a revisão aceitou).

**1.4 Complementa** com os textos: a descrição de `genderDescription`, os KDocs (`GuestView`, `GuestsController`, `liftRestriction`) e o item "Hóspedes e empresas" do `README.md` do repositório deixaram de prometer o perfil inteiro nas escritas (o `README.md` não é nota do brain; fica só a menção de que a seção "API" já foi atualizada). O `GET /guests/{id}` e o `GuestResponse` não mudaram. A mudança de forma só vale para roles customizadas sem `guests.profiles.read`; os modelos de role padrão não mudam. Observação anterior à E17 (testador): a resposta das escritas traz `updatedAt` e `restriction.since` com nanossegundos (instante em memória), e o `GET` traz microssegundos (banco).

### 2. `ZenyHotelManager - Convenções de API`

**Complementa** com o **primeiro `oneOf` do contrato**: resposta que varia com a permissão.

> Nas três respostas `200 application/json` das escritas acima, `oneOf: [GuestResponse, GuestWriteSummaryResponse]`, **sem discriminador**. Os ramos são disjuntos pelo `required`: o mínimo exige `restricted`, que o `GuestResponse` não tem, e o inteiro exige `fullName`. Não há `additionalProperties: false` (ele quebraria a disjunção). Outro status ou outro media type dariam `ERR` no oasdiff.
>
> - O oasdiff dá `warning` `response-body-wrapped-in-one-of-original-preserved` (3 avisos), **não `ERR`**: "Nenhuma mudança incompatível (nível ERR) em /api/v1".
> - Com o **ogen 0.16.1** dos clientes (SDK de prova no front), as três operações saem como `HttpResponseTyped<JsonElement>`, sem tipo, para todo cliente gerado (desktop, mobile, PDV). O front não usa essas operações hoje.
> - **Decisão pendente na entrevista do usuário** (de arquitetura): `oneOf` sem discriminador (adotado provisoriamente, opção recomendada) ou a alternativa tipada, um discriminador, que pede uma propriedade nova no `GuestResponse` de todas as operações de perfil.
> - Se o `oneOf` ficar, o `arquiteto` registra na ARCHITECTURE §7 a regra "resposta que varia com a permissão: `oneOf` sem discriminador, ramos disjuntos pelo `required`, sem `additionalProperties: false`" (nota M-7 da revisão do plano).

### 3. `ZenyHotelManager - Testes de integração`

**Complementa** com:

- **`yamlScalarText`** (`GuestGenderDescriptionApiTest.kt`): decodificação fiel do escalar YAML do contrato gerado (`\` + quebra de linha + recuo; `\ ` é espaço; o gerador quebra até no meio de palavra). **Asserções sobre texto do `api/openapi.yaml` devem usá-la.** O testador provou que a normalização anterior comia o espaço e deixava a asserção negativa passar à toa. `yamlScalarText`, `schemaBlock` e `propertyBlock` são `internal` nesse arquivo e usados por outro teste; movê-los para um utilitário de teste compartilhado é só organização (menor restante).
- **Armadilha do laço `while pgrep -f`:** os testes (e comandos) de uma etapa não devem usar laço `while pgrep -f` com um trecho de comando, porque o padrão casa com a linha de comando do próprio laço e nunca termina.
- **Memória:** dois builds completos simultâneos (este repositório e o front) levaram a máquina de 14 GB à pressão de memória, e o Claude Code encerrou um build em segundo plano. Rode o gate numa janela sem outro build.
- Os testes da etapa: `GuestWriteBodyApiTest` (role customizada só com `guests.restrictions.manage` ou só com `guests.profiles.merge`; chaves exatas `{id, restricted}`; nenhum texto pessoal no corpo cru; perfil inteiro idêntico ao `GET` com a leitura; trilha igual com qualquer corpo; recusas 400/403/404/409/412/428 como `problem+json` sem dado de perfil; permissão retirada ou concedida entre chamadas) e o teste de que o contrato descreve os dois corpos só nas três escritas e os mantém disjuntos.

### 4. `ZenyHotelManager - Estado por marco` (e o "Estado" do hub `ZenyHotelManager`)

**Estado por marco: complementa** "Atualizações por capturas" com a subseção "M6 E17 (2026-11-15)", que **substitui** o estado do M6 da subseção "M6 E16" (captura da E16, item 5). **Hub: substitui** o item de estado do M6.

> - **M6 com E10, E11, E14, E15, E16 e E17 `#concluida`.** A E17 foi fechada em 2026-11-15, com gate em `bcb06f1`, na branch `roadmap/m6-operacao-fechamento`: `./gradlew build` BUILD SUCCESSFUL em 33m 44s, **4068 testes, 0 falhas, 0 ignorados**. O lote foi integrado na `main` por **merge local**, à espera do **push do usuário**.
> - **A E17 tem Revisão humana: sim, pendente** (muda a forma de uma resposta pública que os clientes consomem; inclui a decisão (a) do `oneOf`).
> - **Próximas elegíveis:** E18 (faixa do cursor, rollback em toda exceção, datas estritas e log dos jobs) e depois a E01. Substitui "Próxima elegível: E17" da captura da E16.
> - **Próxima migração:** sem mudança (a E17 não tem migração; só muda a resposta).
> - Fatos: plano `docs/superpowers/plans/2026-11-14-m6-operacao-fechamento-e17.md` (2 tarefas, ambas `Risco: alto`). Revisão de arquitetura aprovada com notas na rodada 2 (`revisor-arquitetura`, opus; bloqueada na rodada 0 com 5 Importantes e na 1 com 2). Commits de `829c256` (início) a `bcb06f1`: `6b1a022` e `d3aee24` (Task 1), `e105d7d`, `ba653d7`, `f975c8b` e `aa7c668` (Task 2), `2f7f314` e `bcb06f1` (onda final). Revisão final (`revisor-seguranca`, opus) sobre `b42ce6f..aa7c668`: "Ready to merge: Yes", 0 Critical e 0 Importante; re-revisão (sonnet) aprovada, 5/5 menores tratados.
> - oasdiff: 0 error, 3 warning `response-body-wrapped-in-one-of-original-preserved`. `check_test_integrity.py --base b42ce6f`: exit 0, sem apontamento.
> - **Decisões da E17:** (a) forma do contrato, **de arquitetura, vai à entrevista do usuário**; (b) conteúdo do mínimo `{id, restricted}`; (c) mudança de forma só para roles customizadas sem `guests.profiles.read`; (d) helper em 5º arquivo. As decisões (b) a (d) foram tomadas pela opção recomendada, sem confirmação do usuário. Para "Perguntas abertas" do hub, **complementa** a lista com **E17 ((b) a (d))** e registra a (a) como pendente.

### 5. `ZenyHotelManager - Ambiente, banco, chaves e build` (supply chain)

**Complementa** com:

- `io.opentelemetry:opentelemetry-api` **1.62.0** está no `productionRuntimeClasspath` com o **GHSA-ccrj-gw8r-854m** (DoS por regex no `W3CTraceContextPropagator` lendo `tracestate`), corrigido na **1.67.0**. Recomendação do handoff: subir numa **etapa de manutenção**, ou limitar o `tracestate` no proxy. Fora da E17; lockfiles e catálogo não mudaram nela.
- O **osv-scanner 2.7.0 não tem extrator para `settings-gradle.lockfile`** (que só tem `empty=…`): use `-L` nos outros dois (`gradle.lockfile`, 426 pacotes, e `buildscript-gradle.lockfile`, 74). Resultado na E17: 0 Critical/High, 2 Medium e 3 Low, todos pré-existentes. **Substitui**, onde houver, a instrução de rodar com `-L` nos "três lockfiles" (captura da E16).

### 6. Pendências para o curador e o arquiteto

- Para o usuário: a entrevista da decisão (a) (`oneOf` sem discriminador ou discriminador) e a Revisão humana da E17.
- Para o `arquiteto`: se o `oneOf` ficar, registrar a regra na ARCHITECTURE §7 (item 2).
- Para uma etapa de manutenção: subir o `opentelemetry-api` para 1.67.0 ou limitar o `tracestate` (item 5).
- O curador, ao integrar o item 1.1, deve **substituir** a "Lacuna conhecida (E15 (h))" na nota do `guests`, para não ficar duas versões.

## Contexto

Fechamento da etapa E17 do roadmap `roadmap-m6-operacao-fechamento` do ZenyHotelManager, publicado pelo `brain-escriba` a pedido do orquestrador de etapa, conforme a regra "Atualização por capturas" do hub. Não havia captura equivalente da E17 em `00 Inbox/` (conferido pela listagem do diretório); as capturas da E15 e da E16 são complementadas, não duplicadas.

## Origem

- Projeto: ZenyHotelManager; repositório `/home/caio/repos/ZenyHotelManager`, worktree `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m6-operacao-fechamento`, branch `roadmap/m6-operacao-fechamento`, gate em `bcb06f1`.
- Fonte lida: `docs/roadmaps/roadmap-m6-operacao-fechamento.md` (seção "E17 — Corpo mínimo nas escritas de restrição e mesclagem do `guests` — #concluida", com "Evidências e handoff"), além do pedido do orquestrador.
- Data: 2026-11-15.

## Por que registrar

Alimentar a consolidação do curador: fecha a lacuna do `guests` da M5 E15 (h), registra o primeiro `oneOf` do contrato e a decisão pendente sobre ele, a decodificação fiel do YAML nos testes de contrato, as armadilhas de processo, o estado do M6 e a pendência de supply chain.

## Limitações e incertezas

- Não li as notas do brain (`Módulo guests`, `Convenções de API`, `Testes de integração`, `Estado por marco`, `Ambiente, banco, chaves e build`) nem o plano e o código da E17; tudo vem do handoff e do pedido do orquestrador. Os nomes de seção das notas ("Lacuna conhecida (E15 (h))", "Lista de restrição", "Mesclar", "API") são os indicados no pedido, e o curador localiza o trecho. Em divergência entre handoff e código, vale o código.
- O número exato de testes e o tempo do gate (4068; 33m 44s) são do handoff.
- O merge local do lote na `main` e o push pendente do usuário vêm do pedido do orquestrador; não conferi o estado do Git.
- A decisão (a) não foi tomada pelo usuário; a forma `oneOf` sem discriminador é provisória. As decisões (b) a (d) não foram confirmadas pelo usuário.
- A mensagem de gate do handoff da E17 diz "Captura do brain: —" (ainda sem caminho); esta captura é essa publicação.
- Dependência local: o worktree pode desaparecer após o merge; o conteúdo útil está acima e os hashes de commit seguem valendo.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Módulo guests]]
- [[ZenyHotelManager - Convenções de API]]
- [[ZenyHotelManager - Testes de integração]]
- [[ZenyHotelManager - Estado por marco]]
- [[ZenyHotelManager - Ambiente, banco, chaves e build]]
- [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E15 - c139da21]]
- [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E16 - f7e211bd]]
