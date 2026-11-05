---
type: capture
status: archived
created: 2026-10-28
capture_id: 7a6ce25a-b05d-40ab-88c0-e459a9c329ca
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E13

## Conteúdo capturado

Resumo do agente (publicado a pedido do orquestrador do lote M5, sessão externa no repositório `/home/caio/repos/ZenyHotelManager`): fechamento da etapa E13 do M5 (travamento de dependências do Gradle, decisão D3 do usuário). O texto abaixo é o novo ou alterado de cada nota afetada e diz o que substitui ou complementa. Os fatos vêm do handoff da E13 e do histórico de revisões de `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`.

Complementa a captura [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh integração E04 a E06 - b2046daa]] (capture_id: b2046daa-2cdb-4680-ae03-6f388769bca4), cuja linha do M5 no "Estado" esta captura substitui.

### 1. Hub `ZenyHotelManager` (seção "Estado") e [[ZenyHotelManager - Estado por marco]]: substitui o estado do M5

- M5 em andamento: E01 a E06 e E13 concluídas, na `main` e em `origin/main` até `bbe0150` (2026-10-28). CI do push da integração verde no run `40788327598`, nos três jobs (build, oasdiff e imagem).
- A E13 (travamento de dependências do Gradle, decisão D3 do usuário) foi executada pelas souls na branch `roadmap/m5-recepcao-fnrh`. A branch foi integrada por fast-forward e apagada, junto com o worktree, a pedido do usuário ausente.
- Nova etapa E14 (correção das vulnerabilidades High/Critical apontadas pelo scanner), `#pendente` e primeira da fila. Depois dela, ficam elegíveis a E07 e a E10. A E12 (gate) agora depende da E14 no lugar da E13.
- A revisão humana da E13 fica pendente até o usuário voltar.
- Obsoleta: a frase do hub (seção "Estado") de que o `osv-scanner` responde "No package sources found". Agora ele lê 415 pacotes de `gradle.lockfile` e 74 de `buildscript-gradle.lockfile`. Obsoleta também a indicação de "próximas elegíveis E07 e E10" sem a E14 na frente, e a menção à E13 como etapa ainda por fazer.

### 2. [[ZenyHotelManager - Ambiente, banco, chaves e build]]: complementa o parágrafo "Versões" com um parágrafo novo

**Travamento de dependências (M5 E13).**

- `build.gradle.kts` liga `dependencyLocking { lockAllConfigurations(); lockMode = LockMode.STRICT }` no projeto e o mesmo bloco dentro de `buildscript { }`, para o classpath dos plugins.
- Lockfiles versionados na raiz, gerados pelo Gradle e nunca editados à mão:
  - `gradle.lockfile`: todas as configurações, inclusive detekt, ktlint, kover e o compilador Kotlin (415 pacotes);
  - `buildscript-gradle.lockfile`: os plugins (74 pacotes);
  - `settings-gradle.lockfile`: hoje só `empty=incomingCatalogForLibs0`, versionado para a regeneração não sujar a árvore.
- **Convenção:** toda mudança no catálogo ou num plugin regrava os lockfiles no mesmo commit, com `./gradlew dependencies --write-locks`. Os revisores conferem catálogo, `build.gradle.kts` e lockfiles juntos.
- **Comportamento do modo estrito, medido** (numa cópia descartável, revertido). Falham o build:
  - versão maior que a travada (`{strictly X} … enforced by Dependency Locking`);
  - dependência nova fora do lockfile (`… is not part of the dependency lock state`);
  - lockfile ausente (`Locking strict mode: Configuration '…' is locked but does not have lock state`).
- **Limitação:** uma versão **menor** no catálogo é ignorada em silêncio, e o build usa a travada (o Gradle a aplica como `strictly`). A E14 acrescenta à CI o passo `./gradlew dependencies --write-locks` seguido de `git diff --exit-code -- '*.lockfile'`, que pega essa divergência.
- Os BOMs entram como `platform(...)` nativo, sem o plugin `io.spring.dependency-management`. Por isso as propriedades de versão do BOM do Spring Boot (`tomcat.version`) não valem; para fixar uma versão, use uma restrição de versão.
- **Scanner:** `osv-scanner scan source -r .` na raiz lê os lockfiles. Dentro de um worktree em `.claude/worktrees/`, ele não vê nada, porque o `.gitignore` do checkout principal ignora essa pasta. Rode-o no checkout principal, numa cópia (`git archive HEAD`) ou com `--no-ignore`.

### 3. [[ZenyHotelManager - Docker, observabilidade e CI]]: complementa

- O `.dockerignore` (lista de permissão) passa a deixar entrar `gradle.lockfile` e `buildscript-gradle.lockfile`, além dos itens que a nota já lista. O `docker/Dockerfile` os copia junto de `settings.gradle.kts` e `build.gradle.kts`, antes do `./gradlew --version`.
- Sem eles, a imagem falha no `COPY`; com um lockfile defasado, falha no modo estrito.
- O cache de dependências do BuildKit passa a ser refeito quando o catálogo ou um lockfile muda.
- A CI não mudou nesta etapa. O `osv-scanner` fica fora dela por decisão do lote; a E14 acrescenta o passo de conferência dos lockfiles (item 2).

### 4. Vulnerabilidades levantadas pelo scanner em 2026-10-28

Complementa [[ZenyHotelManager - Ambiente, banco, chaves e build]] (junto do parágrafo do travamento), por tratar do grafo de dependências do build. Fonte: `osv-scanner` numa cópia limpa do HEAD da E13: "Total 11 packages affected by 31 known vulnerabilities (5 Critical, 15 High, 8 Medium, 3 Low, 0 Unknown)". A lista muda com o tempo; rode o scanner de novo antes de agir.

No runtime de produção (`productionRuntimeClasspath`):

- `org.apache.tomcat.embed:tomcat-embed-core` 11.0.24: Critical 9,8 e 9,1, corrigida na 11.0.25;
- `tools.jackson.core:jackson-core`/`jackson-databind` 3.1.5: High 7,5, com DoS sem autenticação no parser das requisições, corrigida na 3.1.6/3.1.7;
- `com.fasterxml.jackson.core:jackson-core`/`jackson-databind` 2.22.1, usadas pelo springdoc: High 7,5, corrigida na 2.22.2/2.22.3;
- `io.opentelemetry:opentelemetry-api` 1.62.0: Medium.

Só no build:

- `org.freemarker:freemarker` 2.3.32, no classpath dos plugins: Critical 9,1, corrigida na 2.3.35;
- `tools.jackson.*` 3.1.5, no classpath dos plugins;
- `commons-lang3` 3.16.0, no plugin: Medium;
- `logback-core` 1.3.16, no ktlint: Low.

A correção é a E14 (caminho preferido: o patch do Spring Boot, plugin e BOM juntos, no catálogo; senão, uma restrição de versão com o advisory no comentário, removida quando o BOM alcançar a versão).

### 5. Decisões do lote E13, para as "Perguntas abertas" do hub

Complementa a pergunta aberta sobre a confirmação das decisões dos lotes anteriores. O usuário estava ausente e delegou ao orquestrador. Por isso, todas foram decididas pela opção recomendada em nome dele, depois de pesar prós e contras, e **falta a confirmação dele**:

- (a) as vulnerabilidades High/Critical numa etapa própria (E14), primeira da fila;
- (b) o rebaixamento silencioso no catálogo aceito como comportamento do Gradle, documentado, e fechado pelo passo de CI da E14;
- (c) o `osv-scanner` fora do CI por ora;
- (d) a verificação de checksums (`gradle/verification-metadata.xml`) para depois (indicada para o M8);
- (e) o `settings-gradle.lockfile` versionado;
- (f) a revisão humana da E13 pendente, com a branch já integrada a pedido do usuário.

## Fatos

- Revisão final da E13 pelo `revisor-seguranca`: "With fixes", sem Critical; os três Important (handoff vazio, critério 3 só para versão maior, `docker build` sem prova no HEAD) foram resolvidos no fechamento.
- `./gradlew build` na `main` integrada: "BUILD SUCCESSFUL in 8m 51s" (antes do push); no commit `c1acc86`, 1287 testes em 158 classes, 0 falhas. `checkOpenApi` verde, `api/openapi.yaml` sem mudança, oasdiff contra `94a24a9`: "No changes detected". `docker build -f docker/Dockerfile .` em `a5dc411`: exit 0.
- Antes da E13, na base `94a24a9`, `osv-scanner scan source -r .` respondia "No package sources found" (osv-scanner 2.7.0).
- Commits da etapa: `87c0b15`, `1a4b0ab`, `6ba3ac1`, `c1acc86`, `a5dc411`, o de fechamento (`11cacb0`) e o registro do run da CI (`bbe0150`).

## Decisão do usuário

- A integração da E13 na `main` no fim do lote foi pedida pelo usuário, ausente, segundo o handoff do roadmap. As decisões (a) a (f) acima não foram dele: foram tomadas pela opção recomendada, em nome dele, pelo orquestrador.

## Origem

- Repositório `/home/caio/repos/ZenyHotelManager`, `main` em `bbe0150` ("Registra o run da CI da integração da E13 do M5"), 2026-10-28.
- Roadmap `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`: seção "E13" (handoff preenchido), seção "E14", "Decisões do lote E13" e "Histórico de revisões" (entrada de 2026-10-28).

## Por que registrar

O Estado do M5 no brain ainda diz que a E13 é a primeira da fila e que o scanner não enxerga o projeto. A convenção dos lockfiles, o comportamento do modo estrito, a limitação do rebaixamento silencioso e a lista de vulnerabilidades são necessários a quem mexer em dependências, e a E14 depende deles.

## Limitações e incertezas

- Não li a seção "Decisões do lote E13" do roadmap em separado: a lista (a) a (f) vem do pedido do orquestrador, conferida com o handoff da E13 (itens a a e). No handoff, a decisão (d) diz apenas "a verificação de checksums fica para depois"; a indicação do M8 é do pedido do orquestrador.
- As versões vulneráveis e corrigidas são as do scanner em 2026-10-28; a lista muda com o tempo.
- A E14 ainda não foi executada: o passo de CI e as correções descritos são plano, não fato.
- A revisão humana da E13 e a confirmação das decisões (a) a (f) pelo usuário continuam pendentes.
- Caminhos de worktree e do checkout dependem da máquina local.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Estado por marco]]
- [[ZenyHotelManager - Ambiente, banco, chaves e build]]
- [[ZenyHotelManager - Docker, observabilidade e CI]]
- [[ZenyHotelManager - Segurança, autenticação e autorização]] (as vulnerabilidades de runtime também interessam à segurança; ficam registradas na nota de build)
