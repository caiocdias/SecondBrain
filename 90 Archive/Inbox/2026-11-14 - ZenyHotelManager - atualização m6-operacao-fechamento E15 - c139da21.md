---
type: capture
status: archived
created: 2026-11-14
capture_id: c139da21-4f16-40bc-8cae-9ee2dc4444c3
---
# ZenyHotelManager - atualização m6-operacao-fechamento E15

## Conteúdo capturado

Captura de fechamento da etapa M6 E15 (rótulos da FNRH na ficha de registro e descrição da permissão do check-in), `#concluida` em 2026-11-14 na branch `roadmap/m6-operacao-fechamento`, fechamento `99d9e99` ("Conclui a E15 do M6 (rótulos da FNRH na ficha) e preenche o handoff"). Resumo do agente a partir do handoff da E15 no roadmap, do plano (D-E15-1 a D-E15-7) e do código (`RegistrationCardLabels.kt`, `FnrhRegistrationCardLabels.kt`, `FnrhModule.kt`, `FrontdeskPermissions.kt`, `RegistrationCardService.kt`, todos lidos). Organizada por nota de tema, dizendo se **substitui** ou **complementa** cada trecho. **Complementa** a captura da M5 E11 ([[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E11 - d1100f5a]]) e a da M6 E14 ([[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E14 - 998156dc]]) e as **substitui** onde dito. Vale sobre as notas e sobre essas capturas quando tratarem do mesmo assunto.

**As decisões (a) e (b) do handoff da E15 foram tomadas pelo orquestrador pela opção recomendada, sem confirmação do usuário** (nenhuma é de arquitetura). Não são opinião do usuário. A E15 cumpre as decisões (f) e (g) que o usuário tomou em 2026-11-12 ao revisar a M5 E11 (D-E11-10 e D-E11-11, inversão por porta), e essas sim são do usuário.

### 1. `ZenyHotelManager - Hospedagem e recepção`

**1.1 Substitui**, no item "Ficha de registro (M5 E11)" da captura da E11 (seção "6."), a frase "motivo de viagem e meio de transporte como códigos FNRH "(código FNRH)"" por:

> Motivo de viagem e meio de transporte pelo **rótulo do catálogo de domínios da FNRH** (por exemplo `LAZER_FERIAS` sai "Lazer/Férias" e `AUTOMOVEL` sai "Automóvel"), sem "(código FNRH)". Se o código **não consta do catálogo** (letras de caixa diferente, espaço a mais, código removido pelo `refresh`), sai cru como `<código> (código FNRH)` e a ficha é gerada sem erro. Código nulo continua sem a linha. O texto final de cada campo é montado no `RegistrationCardService` (`guestModel`) e os templates `registration-card.xhtml` e `.txt` só o mostram (D-E15-3). Vale para o PDF e para o ESC/POS; um rótulo acentuado sai correto nos dois, e um caractere fora do IBM850 sai pela limpeza de texto do `printing` (D-E11-4).

**1.2 Complementa** o mesmo item com a porta nova:

> **Porta `RegistrationCardLabels`** (M6 E15; D-E15-1, D-E11-11), na raiz do `frontdesk` (`com.zeny.hotel.frontdesk`): `fun travelReason(code: String): String?` e `fun transportMode(code: String): String?`, que devolvem o rótulo do catálogo ou `null` se o código não está nele. Exatamente **uma** implementação no contexto, só leitura. O `RegistrationCardService` a recebe por construtor. O `frontdesk` continua **sem importar o `fnrh`**: quem a implementa é o `fnrh` (ver item 2). Sem cache e sem trilha (D-E15-2): a ficha lê o catálogo a cada geração, então um `refresh` dos domínios aparece na ficha seguinte; custo de duas consultas pequenas por hóspede (decisão (b) do handoff).

**1.3 Complementa** a permissão `frontdesk.stays.checkin` descrita no item "Permissões" do check-in orquestrado ("`frontdesk.stays.checkin` (Gerente e Recepcionista; não sensível)") com a descrição nova, que **substitui** a anterior (D-E15-5):

> "Fazer o check-in de uma reserva confirmada (com a caução opcional) e abrir a ficha de registro (PDF e impressão)". Código, sensibilidade (não), escopos (`ALL`), modelos de role (Gerente e Recepcionista) e concessões **não mudam**. A sincronização do catálogo no boot (`PermissionCatalogSynchronizer`) leva a descrição ao banco; a troca de descrição muda a versão das autorizações (triggers do `iam`), e o teste prova que as sessões abertas continuam válidas e que as concessões ficam iguais.

**1.4 Complementa** o item "Ficha de registro" com a descrição do endpoint no contrato (D-E15-7): a descrição de `GET /api/v1/reservations/{id}/registration-card/pdf` (`@Operation` no `RegistrationCardController`) deixou de dizer "o motivo de viagem e o meio de transporte como os códigos FNRH guardados" e passa a dizer que a ficha traz o rótulo do catálogo de domínios da FNRH, ou o código com "(código FNRH)" quando fora dele. O `api/openapi.yaml` foi regenerado com `./gradlew updateOpenApi`; o diff é **só essa descrição**, sem mudança estrutural nem breaking change (oasdiff sem `ERR`). O README ("Documentos impressos") foi ajustado no mesmo sentido.

### 2. `ZenyHotelManager - Módulo fnrh`

**2.1 Substitui**, na seção "Camada e dependências", o trecho "`allowedDependencies` hoje: `shared` e `guests` … A **E08 acrescenta `reservations` e `notifications`**" e a frase "Nunca importa `iam`, `frontdesk` nem lê tabela de outro schema. `frontdesk` não pode chamar `fnrh` (camada acima)" por:

> `allowedDependencies` (`FnrhModule.kt`): `shared`, `guests`, `reservations`, `notifications` e **`frontdesk`** (M6 E15; D-E15-4). A aresta `fnrh` → `frontdesk` existe **só pela porta `RegistrationCardLabels`**. Nunca importa `iam` nem lê tabela de outro schema. O `frontdesk` continua **sem** depender do `fnrh` (camada acima, ARCHITECTURE §3.1 e §3.2): a inversão é por porta definida no módulo de baixo, no mesmo padrão da `FolioOwnerDescriber` (`billing`, implementada pelo `reservations`). O `ModularityTest` do `fnrh` exige exatamente esses cinco módulos (dependências diretas e `allowedDependencies`) e há um teste novo, `fnrh uses only the registration card labels port from frontdesk`, que compara o conjunto dos `targetType` das dependências diretas do `fnrh` dentro de `com.zeny.hotel.frontdesk.` com exatamente `{com.zeny.hotel.frontdesk.RegistrationCardLabels}` (prova o "só" e o "usa"); o teste do `frontdesk` segue sem `fnrh`. Descartada a named interface do Spring Modulith (`@NamedInterface`): o repositório não a usa e ela mudaria o modelo de API pública do `frontdesk` por uma aresta.

**2.2 Complementa** a seção "Pacotes" (`application`) com `FnrhRegistrationCardLabels` (`@Component`, `com.zeny.hotel.fnrh.application`), que implementa a porta lendo `FnrhDomainCatalog.values(FnrhDomain.TRAVEL_REASONS | FnrhDomain.TRANSPORT_MODES)` e buscando o código **exato** (maiúsculas e espaços contam, como em `contains`): `automovel` e `AUTOMOVEL ` não casam com `AUTOMOVEL` e saem crus na ficha. Só leitura: **sem Serpro, sem chamada de rede e sem trilha**. Um `refresh` dos domínios (rótulo novo ou código removido) vale na ficha seguinte. A implementação é a única do contexto (teste: `getBeansOfType(RegistrationCardLabels)` tem uma entrada, do tipo `FnrhRegistrationCardLabels`).

**2.3 Complementa** "Estado:" da abertura da nota (e das capturas da E08 e da E14): "E15 do M6 concluída (rótulos da FNRH na ficha, 2026-11-14); a homologação real segue sendo a E09, `#bloqueada`."

### 3. `ZenyHotelManager - Arquitetura e estrutura de módulos`

**Complementa** "Arquitetura em uma página", no item "Dependências entre módulos seguem a regra por camadas", na frase "Para reagir a algo de uma camada acima, inverta a dependência com um evento ou com uma porta definida no módulo de baixo", com os exemplos de **portas invertidas** que a ARCHITECTURE §3.1 agora lista: `RegistrationCardLabels` (definida no `frontdesk`, implementada pelo `fnrh`, M6 E15) ao lado de `FolioOwnerDescriber` (definida no `billing`, implementada pelo `reservations`, M5 E11). A tabela da §3.1 ganhou, na linha do `fnrh`, "`frontdesk` (só a porta `RegistrationCardLabels`, M6 E15)". **Complementa** a frase sobre as arestas de camada acima: uma aresta de módulo de **camada acima** para o de baixo (`fnrh` → `frontdesk`) é a direção permitida; o que não existe é o `frontdesk` importar o `fnrh`.

Divergência **não corrigida** (apontada ao `arquiteto`, também registrada na captura da E14): a ARCHITECTURE §3.1 lista `hotel` entre as dependências do `fnrh`, e o `FnrhModule.kt` não o declara (previsão ou divergência).

### 4. `ZenyHotelManager - Segurança, autenticação e autorização`

**Complementa** a lista de permissões do `frontdesk` (onde a nota descreve `frontdesk.stays.checkin`) com a descrição nova do item 1.3 desta captura: a permissão que faz o check-in **também abre a ficha de registro** (PDF e impressão), o que já valia desde a M5 E11 (D-E11-10: nenhuma permissão nova para a ficha) e agora está dito no catálogo `GET /api/v1/permissions`. Código, sensibilidade, escopos, modelos de role e concessões iguais aos de antes. Uma mudança só de descrição troca a versão das autorizações mas **não derruba sessões abertas nem muda concessões** (provado por `FrontdeskCheckInPermissionDescriptionTest` e `FrontdeskCheckInPermissionAttackTest`, com o token de recepcionista anterior ainda abrindo o PDF da ficha com `200`).

### 5. `ZenyHotelManager - Testes de integração`

**Complementa** a nota com o que a E15 mostrou (do handoff e do plano; testes não lidos por inteiro):

> - O teste que troca rótulo em `fnrh.domain_value` (banco compartilhado) **devolve o original no `finally`**: `FnrhRegistrationCardLabelsTest` e `RegistrationCardLabelsApiTest` (`NEGOCIOS`, `SAUDE`).
> - Para provar sessão aberta com a descrição trocada, rode `PermissionCatalogSynchronizer.synchronize(declarações)` com a **lista inteira** de `ModulePermissions` do contexto (só o `frontdesk` com a descrição antiga), e depois o `synchronize()` real num `finally` (passar só o `frontdesk` tornaria obsoletas todas as outras permissões do banco compartilhado); precedente: `iam/AuthorizationTest.kt`.
> - O ESC/POS da ficha se verifica decodificando em IBM850, como os testes da M5 E11. O texto do PDF se extrai com `PdfText`.
> - **Teste existente alterado (D-E15-6):** `RegistrationCardApiTest` afirmava `"AUTOMOVEL (código FNRH)"`; passou a `"Automóvel"` mais a ausência de `"AUTOMOVEL (código FNRH)"`. `LAZER` continua cru com "(código FNRH)" (o código semeado é `LAZER_FERIAS`, então `LAZER` cobre o código fora do catálogo). Nenhuma asserção de RN-19 nem de documento mascarado mudou.
> - Testes novos: `FnrhRegistrationCardLabelsTest`, `FnrhRegistrationCardLabelsAttackTest`, `RegistrationCardLabelsApiTest`, `RegistrationCardLabelsAttackApiTest`, `FrontdeskCheckInPermissionDescriptionTest`, `FrontdeskCheckInPermissionAttackTest` e o teste novo do `ModularityTest`.
> - **Dívidas menores** (sem etapa própria): marcas bidi e zero-width cruas em literais de teste (melhor como escapes); SQL interpolado com constantes nos apoios de teste; contagem exata de códigos semeados no ataque da porta; apoios duplicados entre os dois testes da permissão. Para a E16: o comentário do `ModularityTest` do `fnrh` ainda diz "Nunca iam, frontdesk…" logo acima de "M6 E15: frontdesk, só pela porta", e o KDoc e o nome de um teste de `RegistrationCardApiTest` ainda falam em "códigos FNRH".

### 6. `ZenyHotelManager - Estado por marco` e Estado do hub `ZenyHotelManager`

**Estado por marco: complementa** "Atualizações por capturas" com a subseção "M6 E15 (2026-11-14)", que **substitui** o estado do M6 da subseção "M6 E14" (captura da E14, item 5). **Hub: substitui** o item de estado do M6.

> - **M6 com E10, E11, E14 e E15 `#concluida`.** A E15 foi concluída em 2026-11-14, com fechamento `99d9e99`, na branch `roadmap/m6-operacao-fechamento`. Demais etapas seguem `#pendente`. **Substitui** "Demais etapas seguem `#pendente` (E15 aparece `#em-andamento` …)" da captura da E14.
> - **Próxima elegível: E16** (dívidas de teste herdadas do M5; independente das demais). A E17 e a E18 também não dependem de outras etapas do marco; as de governança, manutenção e relatórios seguem a ordem do roadmap. **Substitui** "Próximas elegíveis: E15 e E16" da captura da E14.
> - **A E14 e a E15 ainda não estão integradas na `main`**: a `main` está em `3eeef98` (a conferir no momento da leitura) e as duas só existem na branch `roadmap/m6-operacao-fechamento`, até o merge local no fim do lote (sem push; o push é do usuário). A E15 tem "Revisão humana: não".
> - **Próxima migração** do projeto: sem mudança, continua posterior a `V2026_11_14_1000` (a E15 não tem migração nem estado novo).
> - Fatos da E15: plano `docs/superpowers/plans/2026-11-14-m6-operacao-fechamento-e15.md` (3 tarefas, todas `Risco: alto`); revisão de arquitetura aprovada com notas na rodada 1 (`revisor-arquitetura`, opus; a rodada 0 bloqueou com 1 Importante: a descrição do endpoint da ficha no contrato ficaria falsa, corrigido pela D-E15-7). Commits `dc52ff8` (início) a `c842f2a`, mais o fechamento `99d9e99`. A Task 2 teve duas rodadas de correção: o `detektTest` do teste novo (`8fbab68`) e uma linha de KDoc com mais de 120 colunas (refluída dentro do commit da Task 3, `f74657d`). Revisão final (`revisor-seguranca`, opus) sobre `dc52ff8..c842f2a`: "Ready to merge: Yes", 0 Critical e 0 Importante de código.
> - Gate: `./gradlew build` em `c842f2a`, BUILD SUCCESSFUL em 19m 36s, **3998 testes, 0 falhas, 0 ignorados**. `.github/scripts/check-api-breaking.sh main`: nenhuma mudança `ERR` em `/api/v1`. `osv-scanner` 2.7.0 com `-L` nos três lockfiles: 0 Critical/High, 2 Medium e 3 Low pré-existentes; lockfiles sem mudança. `check_test_integrity.py --base dc52ff8`: exit 0, sem apontamentos (a única asserção existente alterada, em `RegistrationCardApiTest`, foi julgada justificada pela revisão final).
> - Documentos atualizados no repositório pela etapa: ARCHITECTURE §3.1 (linha do `fnrh` e exemplos de inversão), `README.md` ("Documentos impressos"), KDoc do `FrontdeskModule`, `api/openapi.yaml` (só a descrição da operação da ficha).
> - **Decisões da E15 (a) e (b), tomadas pela opção recomendada do orquestrador, sem confirmação do usuário, revisáveis:** (a) o critério 7 ("`api/openapi.yaml` não muda") foi lido como "sem mudança estrutural nem breaking change", e a descrição do endpoint da ficha foi atualizada e o contrato regenerado (alternativa: manter o contrato descrevendo um comportamento que não existe mais); (b) a porta lê o catálogo a cada ficha, sem cache. Para "Perguntas abertas" do hub, **complementa** a lista de decisões sem confirmação do usuário com **E15 ((a) e (b))**, ao lado de E14 ((a) a (e)).
> - O check-in recusa códigos de motivo e meio com caracteres fora de letras, dígitos, `_`, `.` e `-` (achado do testador, regra da M5 E01 já descrita na nota "Hospedagem e recepção"): caracteres especiais só chegam à ficha pelo rótulo do catálogo, que o `refresh` também filtra.
> - **Pendências do hub:** as decisões (f) e (g) da revisão humana da M5 E11 (rótulos na ficha e descrição da permissão) estão atendidas por esta etapa; a revisão humana da E11 como um todo segue como a captura da E11 a registrou.

### 7. Pendências para o curador e o arquiteto

- Para o `arquiteto`: ajustar o texto do critério 7 da E15 (D-E15-7) e conferir se `hotel` entre as dependências do `fnrh` na §3.1 é previsão ou divergência.
- O curador, ao integrar o item 1.1, deve **substituir** a menção a "códigos FNRH (código FNRH)" da ficha na nota "Hospedagem e recepção" e no que a captura da E11 (item 6) disse, para não ficar duas versões.

## Contexto

Fechamento da etapa E15 do roadmap `roadmap-m6-operacao-fechamento` do ZenyHotelManager, publicado pelo `brain-escriba` a pedido do orquestrador de etapa, conforme a regra "Atualização por capturas" do hub. Não havia captura equivalente da E15 em `00 Inbox/` (conferido pela lista do diretório; busca por nome); as capturas da M5 E11 e da M6 E14 são complementadas, não duplicadas.

## Origem

- Projeto: ZenyHotelManager; repositório `/home/caio/repos/ZenyHotelManager`, worktree `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m6-operacao-fechamento`, branch `roadmap/m6-operacao-fechamento`, fechamento `99d9e99`.
- Fontes lidas: `docs/roadmaps/roadmap-m6-operacao-fechamento.md` (seção "E15 — Rótulos da FNRH na ficha e descrição da permissão do check-in — #concluida", com "Evidências e handoff"); plano `docs/superpowers/plans/2026-11-14-m6-operacao-fechamento-e15.md` (D-E15-1 a D-E15-7, Global Constraints, Review Focus, Tasks 1 a 3); código `src/main/kotlin/com/zeny/hotel/frontdesk/RegistrationCardLabels.kt`, `…/fnrh/application/FnrhRegistrationCardLabels.kt`, `…/fnrh/FnrhModule.kt`, `…/frontdesk/FrontdeskPermissions.kt` e `…/frontdesk/application/RegistrationCardService.kt`.
- Notas e capturas do vault lidas: `20 Knowledge/ZenyHotelManager - Hospedagem e recepção.md`, `…Módulo fnrh.md` (primeiras 40 linhas), `…Arquitetura e estrutura de módulos.md`, captura da M5 E11 (`d1100f5a`) e captura da M6 E14 (`998156dc`).
- Data: 2026-11-14.

## Por que registrar

Alimentar a consolidação do curador: troca na ficha o "(código FNRH)" pelo rótulo do catálogo, documenta a porta `RegistrationCardLabels` e a aresta nova `fnrh` → `frontdesk` (que muda a afirmação da nota do `fnrh` de que o `fnrh` nunca importa o `frontdesk`), a descrição nova de `frontdesk.stays.checkin`, as decisões (a) e (b) e o estado do M6.

## Limitações e incertezas

- Não li a nota `ZenyHotelManager - Segurança, autenticação e autorização` nem a `Estado por marco`; no item 4 a "seção" é indicada pela descrição ("onde a nota descreve `frontdesk.stays.checkin`") e o curador localiza o trecho. No item 3, o trecho da nota de arquitetura foi lido, mas a lista de exemplos de inversão da ARCHITECTURE §3.1 vem do plano e do handoff, não do arquivo `docs/ARCHITECTURE.md`.
- Do código li só a porta, a implementação, o `FnrhModule`, `FrontdeskPermissions` e o `RegistrationCardService`; templates, testes e `RegistrationCardController` não foram lidos: o que se diz deles vem do plano e do handoff. Em divergência entre plano, handoff e código, vale o código.
- A leitura do `FrontdeskPermissions.kt` confirma a descrição nova em `STAYS_CHECK_IN`; `ModularityTest` e o contrato não foram conferidos por mim.
- As decisões (a) e (b) não foram confirmadas pelo usuário.
- A `main` em `3eeef98` e a não integração da E14 e da E15 vêm do pedido do orquestrador e do estado do git informado; o merge do lote acontece depois desta captura.
- A afirmação de que a E16 é a próxima elegível vem do pedido do orquestrador.
- Dependência local: o worktree pode desaparecer após o merge; o conteúdo útil está acima e os hashes de commit seguem valendo.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Hospedagem e recepção]]
- [[ZenyHotelManager - Módulo fnrh]]
- [[ZenyHotelManager - Arquitetura e estrutura de módulos]]
- [[ZenyHotelManager - Segurança, autenticação e autorização]]
- [[ZenyHotelManager - Testes de integração]]
- [[ZenyHotelManager - Estado por marco]]
- [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E11 - d1100f5a]]
- [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E14 - 998156dc]]
