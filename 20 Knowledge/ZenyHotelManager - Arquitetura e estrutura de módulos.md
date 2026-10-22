---
type: knowledge
status: processed
created: 2026-10-22
projects:
  - "[[ZenyHotelManager]]"
sources:
  - "[[2026-10-22 - ZenyHotelManager - Arquitetura e estrutura de módulos - a0fc3031]]"
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
  - Para reagir a algo de uma camada acima, inverta a dependência com um evento ou com uma porta definida no módulo de baixo.
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

## Proveniência

- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - Arquitetura e estrutura de módulos - a0fc3031]] (capture_id: a0fc3031-9923-4dfc-bfc7-44c8c88a6666): texto literal do `CLAUDE.md` do repositório ZenyHotelManager (linhas 66–81, 593–625, commit `a6c0f03`), integrado sem alteração; o tipo Knowledge em `20 Knowledge/` foi escolhido pelo usuário no processamento.
