---
type: capture
status: archived
created: 2026-11-04
capture_id: f8103233-d5b2-48b1-b302-c9360ff5b66b
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E14

## Conteúdo capturado

Resumo do agente (publicado a pedido do orquestrador do lote M5, sessão externa no repositório `/home/caio/repos/ZenyHotelManager`): fechamento da etapa E14 do M5 (correção das vulnerabilidades High/Critical apontadas pelo scanner). O texto abaixo é o novo ou alterado de cada nota afetada e diz o que substitui ou complementa. Os fatos vêm do handoff da E14 e da seção "Decisões do lote E14" de `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`.

Complementa e em parte substitui a captura [[2026-10-28 - ZenyHotelManager - atualização m5-recepcao-fnrh E13 - 7a6ce25a]] (capture_id: 7a6ce25a-b05d-40ab-88c0-e459a9c329ca), indicada em cada item abaixo.

### 1. Hub `ZenyHotelManager` (seção "Estado") e [[ZenyHotelManager - Estado por marco]]: substitui a linha do M5 da captura da E13

- M5 em andamento: E01 a E06, E13 e E14 concluídas.
- A E14 está na branch `roadmap/m5-recepcao-fnrh` (commits `be152b2` a `2c72294` e o commit de fechamento) e ainda **não** está em `origin/main`. O usuário pediu para deixar a `main` local pronta para `git push origin main` no fim do lote; o push é dele.
- Próximas elegíveis: E07 e depois E10. A E14 deixa de ser "primeira da fila".
- A revisão humana da E13 continua pendente.
- Obsoleta: a indicação da E14 como `#pendente` e primeira da fila (captura da E13, item 1).

### 2. [[ZenyHotelManager - Ambiente, banco, chaves e build]]: complementa o parágrafo do travamento

- **Spring Boot 4.1.2** (plugin e BOM, no catálogo `gradle/libs.versions.toml`). Arrasta Tomcat 11.0.27, Jackson 3.1.7, Spring Framework 7.0.10, Spring Security 7.1.2, Hibernate 7.4.13, Micrometer 1.17.2, PostgreSQL JDBC 42.7.14 e, no classpath dos plugins, httpclient5 5.6.5. Os lockfiles continuam com 415 e 74 pacotes.
- **Inventário das duas restrições de versão** (cada uma traz no catálogo o motivo, os GHSA e a condição de saída):

| Restrição | Por quê | Sai quando |
|---|---|---|
| Plataforma do Jackson 2 na 2.22.4 (`jackson2 = "2.22.4"`, lib `jackson2-bom`, `implementation(platform(libs.jackson2.bom))`) | o springdoc 3.1.1 puxa a 2.22.1, e o BOM do Boot 4.1.2 fica na 2.21.7 | o springdoc ou o BOM do Boot trouxer o Jackson 2 ≥ 2.22.3 (conferir as 7 GHSA no scanner) |
| freemarker 2.3.35 no classpath dos plugins (`freemarker = "2.3.35"`) | vem do kover 0.9.11 (`kover-features-jvm` → `intellij-coverage-reporter`), o último publicado | o kover trouxer o freemarker ≥ 2.3.35 |

- A restrição do freemarker fica em `buildscript { dependencies { constraints { classpath(libs.freemarker) { because(…) } } } }`. O acessor `libs` compila dentro do `buildscript {}`.
- **A restrição é piso de versão.** O passo da CI não acusa uma restrição que sobrou (BOM já alcançou a versão), mas acusa a **remoção** dela, porque o lockfile voltaria para a versão vulnerável. Numa subida futura do Boot ou do kover, confira a condição de saída de cada restrição.
- **Substitui o item 4 da captura da E13 (vulnerabilidades):** com o scanner numa cópia limpa (`git archive`), o resultado antes (base `15bbcdb`) era "Total 11 packages affected by 31 known vulnerabilities (5 Critical, 15 High, 8 Medium, 3 Low, 0 Unknown)". Depois (lockfiles de `2c72294`) é "Total 3 packages affected by 5 known vulnerabilities (0 Critical, 0 High, 2 Medium, 3 Low, 0 Unknown)", sobre os mesmos 415 + 74 pacotes. Agora há **0 Critical e 0 High**. Resíduos:
  - `io.opentelemetry:opentelemetry-api` 1.62.0 (GHSA-ccrj-gw8r-854m, Medium 5,3, runtime): CPU quadrática no `tracestate`, alcançável sem autenticação porque a propagação W3C está ligada em toda requisição em `application.yaml`. Sai quando o Boot trouxer ≥ 1.67.0;
  - `org.apache.commons:commons-lang3` 3.16.0 (GHSA-j288-q9x7-2f5v, Medium 6,5): só no classpath dos plugins;
  - `ch.qos.logback:logback-core` 1.3.16 (três Low): só na configuração `ktlint`.
- **Torna obsoleta** a frase da captura da E13, item 2: "A E14 acrescenta à CI o passo `./gradlew dependencies --write-locks` seguido de `git diff --exit-code -- '*.lockfile'`". Agora é fato (item 3). A limitação do rebaixamento silencioso no catálogo passa a ser coberta pela CI, não só documentada.
- A convenção continua: toda mudança de dependência ou plugin regrava os lockfiles no mesmo commit; agora a CI recusa o lockfile defasado.
- Scanner da revisão final: rode-o fora do worktree (cópia por `git archive` ou `--no-ignore`). Neste ambiente, `osv-scanner -r <diretório>` equivale a `scan source -r`.

### 3. [[ZenyHotelManager - Docker, observabilidade e CI]]: complementa

- O job `build` de `.github/workflows/ci.yml` ganhou o passo **"Lockfiles em dia com o catálogo"**, antes do build completo.
  - O que roda: `./gradlew dependencies --write-locks`.
  - Quando falha: com `::error::`, se `git diff --exit-code -- '*.lockfile'` acusar mudança ou se `git status --porcelain -- '*.lockfile'` não sair vazio (lockfile novo não rastreado).
  - Por que fica dentro de um `if`: para a mensagem de erro sair mesmo sob `bash -e`.
- Verificado localmente, com o bloco `run` extraído do YAML e rodado com `bash --noprofile --norc -eo pipefail` em clones descartáveis: árvore em dia dá exit 0 (duas vezes, sem sujar a árvore); `shedlock = "7.10.0"` no catálogo, dependência nova (`commons-pool2`), lockfile novo não rastreado e restrição do freemarker removida dão exit 1. Sem o passo, o build estrito não falharia no rebaixamento nem na remoção da restrição, porque o Gradle aplica a versão travada como `strictly`.
- A ARCHITECTURE §17 cita a conferência dos lockfiles; o README e o comentário do `build.gradle.kts` também foram atualizados.
- **O primeiro run no GitHub ainda não existe** (depende do push, que é do usuário).

### 4. "Perguntas abertas" do hub: decisões do lote E14, a confirmar

O usuário delegou a escolha em 2026-11-04. As decisões abaixo foram tomadas pela opção recomendada, em nome dele, pelo orquestrador, depois de pesar prós e contras. **Falta a confirmação dele.** Complementa a pergunta sobre as decisões (a) a (f) do lote E13.

- (a) `opentelemetry-api` 1.62.0 aceito como risco registrado até o Boot trazer ≥ 1.67.0. **Tem prazo: resolver antes da operação real (M8)**; cada revisão final reavalia o caso. A favor: o sistema ainda não opera, a correção pelo BOM evita uma subida de minor fora do escopo e o scanner volta a mostrar o risco. Contra: o risco fica aberto até lá. Descartadas: plataforma `opentelemetry-bom` 1.67.0 agora (minor de toda a família, à frente do BOM do Boot e sem teste da ponte do Micrometer) e limpar o `tracestate` no proxy (mexe no compose e perde o contexto de trace dos clientes).
- (b) `commons-lang3` 3.16.0 (Medium, plugins) e `logback-core` 1.3.16 (Low, `ktlint`) aceitos: só rodam no build e não são alcançáveis por entrada externa. Descartadas: restrições próprias, que dariam manutenção sem ganho no servidor.
- (c) Jackson 2 na 2.22.4 (último patch da linha), em vez do piso 2.22.3: fecha as mesmas 7 GHSA e evita ficar um patch atrás.

## Fatos

- Scanner (`osv-scanner -r` em cópias limpas por `git archive`): antes, 31 vulnerabilidades (5 Critical, 15 High); depois, 5 vulnerabilidades (0 Critical, 0 High, 2 Medium, 3 Low), sobre 415 + 74 pacotes.
- `./gradlew build` no HEAD `2c72294`: "BUILD SUCCESSFUL in 7m 38s", 1287 testes em 158 classes, 0 falhas e 0 erros (a base `15bbcdb` também tinha 1287 e 0 falhas). `checkOpenApi` verde, `api/openapi.yaml` sem mudança. `.github/scripts/check-api-breaking.sh 15bbcdb`: "No changes detected". `docker build -f docker/Dockerfile .`: exit 0. `./gradlew lint`: verde.
- Revisão de arquitetura do plano: aprovado com notas, em 1 rodada (a revisão inicial bloqueou por dois Importantes, já corrigidos no plano). Revisões das duas tarefas: "Approved", 0 Critical e 0 Important. Revisão final (`revisor-seguranca`): "With fixes", sem Critical; o Important era o handoff vazio, resolvido no fechamento; Minors M1 e M3 na onda `2c72294`; M2 (imagem e oasdiff provados só em `fa08f85`) refeito no HEAD `2c72294`. Verificação mecânica (`check_test_integrity.py --base 15bbcdb`): "OK: nenhum apontamento".
- Commits da etapa: `be152b2`, `b09be76`, `2eefa28`, `fa08f85` (Boot 4.1.2, plataforma Jackson 2, restrição do freemarker, lockfiles), `3f47b39` (passo da CI, README, comentário do build, ARCHITECTURE §17), `2c72294` (comentários das restrições) e o commit de fechamento.

## Decisão do usuário

- O usuário pediu que a `main` local fique pronta para `git push origin main` no fim do lote; o push e a decisão sobre merge são dele.
- As decisões (a), (b) e (c) acima **não** foram do usuário: foram tomadas pela opção recomendada, em nome dele (delegação de 2026-11-04).

## Origem

- Repositório `/home/caio/repos/ZenyHotelManager`, branch `roadmap/m5-recepcao-fnrh`, commit `2c72294` ("Ajusta os comentários das restrições de versão (revisão final da E14)"), 2026-11-04.
- Roadmap `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`: seção "E14" (handoff preenchido) e "Decisões do lote E14". Plano: `docs/superpowers/plans/2026-11-04-m5-recepcao-fnrh-e14.md`.

## Por que registrar

O brain ainda diz que a E14 é a primeira da fila e que o grafo tem Critical e High. Quem mexer em dependências precisa do inventário das duas restrições (e de saber que a CI não acusa a sobra), do passo novo da CI e do risco aceito do OpenTelemetry, que tem prazo no M8.

## Limitações e incertezas

- O run da CI com o passo novo só existe depois do push; a verificação do passo foi local, com o bloco `run` extraído do YAML.
- A análise de alcance do OpenTelemetry (alcançável sem autenticação pelo `tracestate`) vem do advisory e do `application.yaml`, sem teste prático.
- Não li a entrada mais recente do "Histórico de revisões" do roadmap; os fatos vêm do handoff e das decisões do lote, conforme o pedido do orquestrador. O hash do commit de fechamento não consta na fonte lida.
- A lista de vulnerabilidades é a do scanner em 2026-11-04 e muda com o tempo; rode o scanner de novo antes de agir.
- A E14 está só na branch local; o estado em `origin/main` muda após o push do usuário.
- A confirmação das decisões (a) a (c) e a revisão humana da E13 continuam pendentes. Caminhos de worktree dependem da máquina local.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Estado por marco]]
- [[ZenyHotelManager - Ambiente, banco, chaves e build]]
- [[ZenyHotelManager - Docker, observabilidade e CI]]
- [[ZenyHotelManager - Hospedagem e recepção]] (lista das decisões de lotes anteriores do M5)
