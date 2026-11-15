---
type: knowledge
status: processed
created: 2026-10-22
projects:
  - "[[ZenyHotelManager]]"
sources:
  - "[[2026-10-22 - ZenyHotelManager - Arquitetura e estrutura de módulos - a0fc3031]]"
  - "[[2026-11-06 - ZenyHotelManager - atualização revisão de arquitetura dos roadmaps - c889f886]]"
---
# ZenyHotelManager - Arquitetura e estrutura de módulos

Referência técnica do projeto [[ZenyHotelManager]]: a estrutura de um módulo, os testes de arquitetura e a "Arquitetura em uma página".

Texto literal do `CLAUDE.md` do repositório, linhas 66–81, 593–625, no commit `a6c0f03` (2026-10-22), escrito pelos agentes que executaram as etapas M0 E01 a M5 E03; integrado sem resumo nem reescrita. Referências como "SPEC", "ARCHITECTURE §x", "RF-…", "RN-…", "Hn" e "Mx Ey" apontam para `docs/SPEC.md`, `docs/ARCHITECTURE.md` e `docs/roadmaps/` do repositório; menções a uma seção (por exemplo, seção "Transições de hospedagem") apontam para outra parte do antigo `CLAUDE.md`, hoje numa das notas de tema listadas no hub. Mudanças posteriores chegam por capturas "ZenyHotelManager - atualização Mx Ey" (fluxo no hub).

---

**Estrutura de um módulo** (pacote base `com.zeny.hotel`):

```
com/zeny/hotel/<módulo>/
├── <Módulo>Api.kt, <Módulo>Events.kt   # raiz = API pública: interfaces, DTOs e eventos
├── domain/          # agregados e regras; sem Spring; de JPA só anotações (e seus enums)
├── application/     # casos de uso, transações, autorização
├── infrastructure/  # JPA, adaptadores, jobs
└── web/             # controllers; só fala com application (e com os DTOs da raiz)
```

- `ModularityTest` roda `ApplicationModules.verify()` (sem ciclos, sem acesso a internos de outro módulo) e gera a documentação dos módulos em `build/spring-modulith-docs/`.
- `LayerArchitectureTest` aplica as regras de `architecture/LayerRules.kt` (código de teste) ao código de produção: `domain` sem Spring, sem a API JPA/Hibernate e sem `application`/`infrastructure`/`web`; `web` sem `domain`/`infrastructure`; nenhum módulo usa `domain`/`application`/`infrastructure`/`web` de outro módulo; todo método público `@Transactional` sem `readOnly` (no método ou na classe) de `application` leva `@Audited` (`writeUseCasesAreAudited`).
- `LayerRulesTest` prova que cada regra falha diante de uma violação, usando as classes de exemplo em `src/test/kotlin/archfixtures/`. Ao mudar uma regra, mantenha ou acrescente o exemplo que a viola.
- `shared` é declarado em `shared/SharedModule.kt` (`@PackageInfo` + `@ApplicationModule`, o equivalente Kotlin do `package-info.java`) e como módulo compartilhado em `@Modulithic(sharedModules = ["shared"])`. Ele não pode depender de nenhum outro módulo (`allowedDependencies = []`). Um módulo novo segue o mesmo padrão quando precisar declarar metadados.
- Plugins `kotlin-spring`, `kotlin-jpa` e `allopen` já estão ligados: entidades `@Entity`, `@MappedSuperclass` e `@Embeddable` ficam abertas e com construtor sem argumentos.

## Arquitetura em uma página

- **Monólito modular** com Spring Modulith. Cada pacote de primeiro nível sob o pacote base (`com.zeny.hotel`, adotado no M0 E01) é um módulo, correspondente a um contexto da SPEC.
  - O que fica na raiz do pacote do módulo é a API pública: interfaces, DTOs e eventos.
  - Os subpacotes `domain/`, `application/`, `infrastructure/` e `web/` são internos.
  - `domain` não depende de Spring; `web` só fala com `application`.
- **Dependências entre módulos seguem a regra por camadas** (ARCHITECTURE §3.1 e §3.2).
  - Um módulo pode depender de qualquer módulo de camada inferior e de qualquer módulo da Plataforma, desde que sem ciclo. Ao criar uma dependência nova, acrescente-a à tabela da §3.1 na mesma mudança.
  - Para reagir a algo de uma camada acima, inverta a dependência com um evento ou com uma porta definida no módulo de baixo. Exemplos de porta: "Portas invertidas (M6 E15)", em "Atualizações por capturas".
  - `notifications` e `printing` nunca escutam eventos de módulos de negócio: quem gera o aviso, ou é dono do documento, chama esses módulos.
- **Fluxo de escrita** (ARCHITECTURE §5):
  1. O controller converte o DTO em comando.
  2. O caso de uso em `application` abre a transação e checa autorização (permissão, escopo `OWN`/`ALL`, limites, step-up).
  3. O agregado aplica as regras e registra eventos de domínio.
  4. No commit, os eventos vão para o *Event Publication Registry* (outbox) e a auditoria é gravada na mesma transação.
  5. Os listeners `@ApplicationModuleListener` rodam depois, de forma assíncrona e com reprocessamento.
- **Persistência:** um schema PostgreSQL por módulo, sem FK entre schemas. Migrações Flyway ficam numa pasta por módulo, com versão por timestamp (`V2026_10_09_1200__…`). Use JPA para escrita e `JdbcClient` para leitura. O módulo `reporting` lê só as views `report_*` publicadas pelos outros módulos.
- **Invariantes que o banco garante:**
  - Nunca há UH em dobro: `EXCLUDE USING gist` sobre as alocações.
  - A disponibilidade usa contadores por tipo e data com `SELECT … FOR UPDATE`.
  - Lançamentos e pagamentos são imutáveis (RN-03): o usuário da aplicação não tem `UPDATE` nem `DELETE` nessas tabelas, e a auditoria é *append-only*.
- **Tipos:**
  - IDs são UUIDv7 gerados na aplicação.
  - Dinheiro usa `Money` sobre `BigDecimal` / `numeric(14,2)`, nunca ponto flutuante.
  - Instantes ficam em `timestamptz` UTC; datas de negócio em `date`, seguindo a data operacional do hotel, que só avança no fechamento do dia.
- **API** (ARCHITECTURE §7):
  - Endpoints sob `/api/v1`, com erros RFC 9457 e `code` estável.
  - `Idempotency-Key` em operações financeiras e externas; `ETag`/`If-Match`; paginação por cursor.
  - O `api/openapi.yaml` é gerado no build e versionado. Nunca edite à mão: regenere com `./gradlew updateOpenApi` e commite junto da mudança.
- **Offline e tempo real:**
  - O app operacional sincroniza por `/api/v1/sync/changes` (cursor) e `/api/v1/sync/commands`, com idempotência por `commandId`. Cada módulo registra seus `OfflineCommandHandler`.
  - Mudanças de estado chegam aos clientes por SSE em `/api/v1/stream`.
- **Integrações** (FNRH, channel manager, PSP Pix, adquirente, middleware fiscal, FCM): porta no módulo e adaptador por provedor, com outbox, retry e log redigido, testados com WireMock. Os fornecedores ainda não foram escolhidos (Q-05).

---

## Atualizações por capturas

Texto das capturas de atualização publicadas no repositório, integrado sem resumo nem reescrita. Vale sobre o texto literal acima quando trata do mesmo assunto.

### Decisões D18 e D19 e regra por camadas (revisão dos roadmaps, 2026-11-06)

Origem: [[2026-11-06 - ZenyHotelManager - atualização revisão de arquitetura dos roadmaps - c889f886]]. Citações de `docs/ARCHITECTURE.md` na árvore de trabalho, sem commit na data da captura.

Linhas novas da tabela de decisões (§2):

> | D18 | Venda do PDV | A comanda paga no ponto de venda abre uma **conta `WALK_IN`** no `billing`, com lançamentos e pagamentos existentes (usuário, 2026-11-06) | O dinheiro entra no turno de caixa, na taxa de serviço e em `billing.report_postings` sem caminho novo; o A&B do snapshot tem uma só fonte | Livro financeiro próprio no `pos` (duplica taxa e conferência de caixa e cria duas fontes de receita) |

> | D19 | Alertas | **Prometheus e Alertmanager** no compose, sem porta pública, com destino de entrega configurável (usuário, 2026-11-06) | As regras já existem, e o caminho é o mesmo em nuvem ou no hotel; o monitor externo do host fica no checklist de inauguração | Monitor externo gerenciado (fornecedor novo e, no hotel, endpoint exposto); decidir só com a Q-06 (alertas sem destinatário até lá) |

- D18 e D19 são **decisões do usuário** (R14 e R15). Ambas ainda são desenho: a D18 entra na M8 E04 e a D19, na M8 E18.
- A regra por camadas da §3.1 ganhou uma frase, sem decisão R própria na spec. Citação literal: "as arestas de mesma camada já na tabela (como `billing` → `payments`, `reservations` → `rates` e `endofday` → `reporting`) são exceções registradas, e uma nova exige decisão." Complementa o item "Dependências entre módulos seguem a regra por camadas" acima. Desde 2026-11-12, `reservations` → `rates` deixou de ser exceção (ver "Ordem interna da camada Hospedagem" abaixo).


### Ordem interna da camada Hospedagem (decisão do usuário, 2026-11-12)

Origem: [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 (revisão humana) - 64ce6698]] (decisão do usuário na entrevista do fim do lote da M5 E12, "Decisões do lote E12" (e) do roadmap do M5) e [[2026-11-12 - ZenyHotelManager - atualização arquitetura e sincronização do M6 - 3a747cdc]] (aplicação na ARCHITECTURE pelo `arquiteto`, commit `0e58cf9`), que vale sobre ela.

- **Ordem interna da camada Hospedagem** (ARCHITECTURE §3.1 "Regra por camadas" e §3.2): `rates` < `reservations` < `frontdesk`. Um módulo da camada pode depender de quem vem antes dele na ordem, nunca de quem vem depois. As arestas `reservations` → `rates`, `frontdesk` → `reservations` e `frontdesk` → `rates` deixaram de ser "exceções registradas". O alcance de `frontdesk` → `rates` continua só os tipos públicos que a `ReservationsApi` usa (`RatePlanId`, `GuaranteeType`, `PackageId`, `PackageCharge`), porque preço e política chegam congelados na reserva, e ampliá-lo exige decisão. As exceções de mesma camada que continuam são `billing` → `payments` e `endofday` → `reporting`. O diagrama da §3.2 mostra a ordem dentro da Hospedagem. Edição só de documento, sem mudança de código; o `ModularityTest` continua exato.
- Conferido no código (`allowedDependencies`): `rates` = shared, rooms, billing, hotel; `reservations` = shared, hotel, rooms, rates, guests, billing, notifications, printing; `frontdesk` = shared, hotel, reservations, rooms, guests, billing, files, rates, staff, printing. Nenhuma aresta contrária à ordem e nenhum ciclo; o `ModularityTest` não mudou.
- **Aresta prevista, ainda não no código** (*atualização:* implementada pela M6 E15 em 2026-11-14, ver "Portas invertidas (M6 E15)" abaixo)**:** `fnrh` → `frontdesk`, só pela porta dos rótulos da ficha (M6 E15). Segue a regra por camadas, porque a "Integração governamental" fica acima da Hospedagem. Quando a E15 rodar, entra na tabela §3.1 e no teste do `fnrh`, cujo comentário "nunca frontdesk" muda. O `frontdesk` continua sem importar o `fnrh`.
- Nota de leitura: a tabela §3.1 ainda lista `hotel` entre as dependências do `fnrh`, e o código não usa (o código é subconjunto da tabela; não foi alterado).
- O diagrama Mermaid da §3.2 não foi renderizado para conferência (limitação registrada na captura).

### Portas invertidas (M6 E15, 2026-11-14)

Origem: [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E15 - c139da21]] (item 3). Complementa "Arquitetura em uma página", no item "Dependências entre módulos seguem a regra por camadas", na frase "Para reagir a algo de uma camada acima, inverta a dependência com um evento ou com uma porta definida no módulo de baixo".

- Exemplos de **portas invertidas** que a ARCHITECTURE §3.1 agora lista: `RegistrationCardLabels` (definida no `frontdesk`, implementada pelo `fnrh`, M6 E15; ver [[ZenyHotelManager - Hospedagem e recepção]] e [[ZenyHotelManager - Módulo fnrh]]) ao lado de `FolioOwnerDescriber` (definida no `billing`, implementada pelo `reservations`, M5 E11). A tabela da §3.1 ganhou, na linha do `fnrh`, "`frontdesk` (só a porta `RegistrationCardLabels`, M6 E15)".
- Uma aresta de módulo de **camada acima** para o de baixo (`fnrh` → `frontdesk`) é a direção permitida; o que não existe é o `frontdesk` importar o `fnrh`.
- Divergência **não corrigida** (apontada ao `arquiteto`, também registrada na captura da E14): a ARCHITECTURE §3.1 lista `hotel` entre as dependências do `fnrh`, e o `FnrhModule.kt` não o declara (previsão ou divergência).
- A lista de exemplos de inversão da §3.1 vem do plano e do handoff da E15, não da leitura de `docs/ARCHITECTURE.md` pela captura.

*Nota do curador (conferência por `git` em 2026-11-15, só leitura, no merge `b42ce6f`):* a linha do `fnrh` na tabela da §3.1 é "shared, hotel, reservations, guests, notifications, `frontdesk` (só a porta `RegistrationCardLabels`, M6 E15)", e o item da §3.1 sobre a `FolioOwnerDescriber` continua: "Do mesmo modo, a ficha de registro do `frontdesk` lê os rótulos dos códigos da FNRH pela porta `RegistrationCardLabels`, que o `frontdesk` define e o `fnrh` implementa (a única aresta `fnrh` → `frontdesk`)".

---

## Proveniência

- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - Arquitetura e estrutura de módulos - a0fc3031]] (capture_id: a0fc3031-9923-4dfc-bfc7-44c8c88a6666): texto literal do `CLAUDE.md` do repositório ZenyHotelManager (linhas 66–81, 593–625, commit `a6c0f03`), integrado sem alteração; o tipo Knowledge em `20 Knowledge/` foi escolhido pelo usuário no processamento.
- 2026-11-09 — [[2026-11-06 - ZenyHotelManager - atualização revisão de arquitetura dos roadmaps - c889f886]] (capture_id: c889f886-0719-4f28-984e-f2ef23ed9520): decisões D18 e D19 e frase nova da regra por camadas, em "Atualizações por capturas".
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 (revisão humana) - 64ce6698]] (capture_id: 64ce6698-9d2c-4a1c-b4d0-af930d24bff5): ordem interna da camada Hospedagem decidida pelo usuário.
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização arquitetura e sincronização do M6 - 3a747cdc]] (capture_id: 3a747cdc-6309-4bfa-bea2-3f6cd483a30f): ordem aplicada na ARCHITECTURE (§3.1 e §3.2, `0e58cf9`), dependências conferidas, aresta prevista `fnrh` → `frontdesk` e nota sobre o `hotel` na tabela do `fnrh`; frase das exceções da revisão de 2026-11-06 marcada como superada em parte.
- 2026-11-15 — [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E15 - c139da21]] (capture_id: c139da21-4f16-40bc-8cae-9ee2dc4444c3): portas invertidas da §3.1 (`RegistrationCardLabels` e `FolioOwnerDescriber`), aresta `fnrh` → `frontdesk` dada como implementada e divergência do `hotel` (item 3 da captura); nota do curador com a conferência por `git`.
