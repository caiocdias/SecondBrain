---
type: capture
status: archived
created: 2026-11-13
capture_id: 009e3130-5bd9-4e8b-bd56-81c7fc440b81
---
# ZenyHotelManager - atualização roadmap M6 manutenção transversal

## Conteúdo capturado

Mudança de roadmap e de arquitetura feita pela sessão `claude --agent arquiteto` em 2026-11-13, no commit `57eb5fa` da `main` (sem push). Cumpre o item 3 das decisões do usuário da E10 do M6 (H12), registrado na captura [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 (revisão humana) - fa5b192f]]. As regras dos itens 3 a 6 são **decisões registradas na ARCHITECTURE, ainda não implementadas**: entram no código com a M6 E18.

### 1. Estado do M6 (complementa `ZenyHotelManager - Estado por marco` e Estado/Próximos passos do hub `ZenyHotelManager`)

- O M6 passa a ter **18 etapas** (`docs/roadmaps/README.md`).
- Etapa nova **E18 "Faixa do cursor, rollback em toda exceção, datas estritas e log dos jobs"**: `#pendente`, Revisão humana: não, sem dependências dentro do roadmap (exige o gate do M5), no bloco novo **"Manutenção transversal"**, depois da E17 e antes da governança (E01). Motivo, segundo o roadmap: corrigir as regras no `shared` antes que a governança, a manutenção e os relatórios (E01 a E09) criem muitos casos de uso, listas por cursor e campos de data.
- O gate **E12 passa a depender também da E18** (E06, E13, E14, E15, E16, E17, E18). A definição global de pronto do M6 ganhou o item da E18.
- Fecha o próximo passo "o `arquiteto` cria a etapa de manutenção do M6" da captura fa5b192f.
- Próximos passos: push pelo usuário; novo lote do orquestrador começando pela E11.
- Conferido pelo escriba em 2026-11-13 com `git status`: a `main` local está 49 commits à frente de `origin/main`.

### 2. Decisões (H13 do roadmap M6)

**Decisão do usuário** (entrevista do `arquiteto`, 2026-11-13, todas pela opção recomendada):

- (a) A faixa do cursor vale para as chaves de **instante e de data** (`PageCursor.instant` e `PageCursor.localDate`), cobrindo 15 consultas:
  - 9 por instante: `AuditQueries`, `ChecklistReports`, `ChecklistExecutions`, `ReservationLifecycle`, `ProvisionalReservations`, `CardPreAuthorizationService`, `PaymentService`, `FolioService`, `RoomStatusService`;
  - 6 por data: `EndOfDayQueries` (lista de execuções), `ReservationQueries`, `RoomAssignments`, `TraceService`, `OutOfOrderService`, `Scheduling`.
- (b) A leitura estrita vale para `format: date` **e** `format: date-time`.
- (c) Mapeador único: os payloads dos comandos offline também ficam estritos; comando fora do formato vira `REJECTED` com código, registrado e não descartado (RN-22).

**Decisão do `arquiteto`:** a faixa vive no `PageCursor` (`shared`), e a validação local do `endofday` (`EndOfDayQueries.requireStorable` e as constantes dela) sai; o tratador de erro é único, o do agendador da aplicação, e não um por job.

### 3. `ZenyHotelManager - Convenções de API` (complementa; implementação na M6 E18)

- **Paginação:** o cursor é opaco e não assinado, e as chaves são entrada não confiável. Cursor ilegível ou com chave de data ou de instante fora do alcance do `date` ou do `timestamptz` do PostgreSQL dá `400 INVALID_CURSOR`, recusado pelo próprio `PageCursor` do `shared`, não por consulta (ARCHITECTURE §7, linha "Paginação").
- **Datas e valores:** leitura estrita. Numa data (`format: date`) só vale o texto `YYYY-MM-DD`; num instante (`format: date-time`) só o texto ISO-8601. Número (epoch) ou data-hora numa data, e número num instante, dão `400 VALIDATION_FAILED` com o erro no campo. Vale para os corpos JSON da API e para os payloads dos comandos offline, pelo mesmo mapeador (ARCHITECTURE §7, linha "Datas e valores").

### 4. `ZenyHotelManager - Auditoria` (complementa; implementação na E18)

- O `@EnableTransactionManagement` do `shared` passa a usar `rollbackOn = RollbackOn.ALL_EXCEPTIONS`: exceção *checked* que escapa de um caso de uso passa a desfazer a escrita, e a escrita nunca fica confirmada sem trilha.
- O `noRollbackFor` explícito de quem grava a recusa (`recordRejections`, como login com falha) continua valendo.
- Alternativa descartada (ARCHITECTURE §5 item 6): `rollbackFor = Throwable` em cada caso de uso.

### 5. `ZenyHotelManager - Eventos e jobs` e `ZenyHotelManager - Docker, observabilidade e CI` (complementam; implementação na E18)

- Exceção que escapa de um job, inclusive a falha da trava do ShedLock com o banco fora, é logada pelo tratador de erro do agendador do `shared` com o nome da tarefa e só a classe da exceção e das causas, **sem a mensagem**, que pode trazer valores do banco (ARCHITECTURE §13, primeiro parágrafo; remete à §16).
- Alternativa descartada: `try/catch` por job.

### 6. `ZenyHotelManager - Schemas, migrações e views de relatório` (complementa)

ARCHITECTURE §11 "Identificadores e tipos" registra o alcance do PostgreSQL, menor que o do Java: `timestamptz` de 4714-11-24 a.C. (ano ISO −4713) a 294276 d.C.; `date` do mesmo início a 5874897 d.C. Valor de fora que chega a uma consulta sem passar por regra de negócio (ex.: a chave do cursor) é recusado antes do banco.

## Contexto

Na E10 do M6 apareceram quatro problemas transversais (nenhum introduzido por ela). O usuário decidiu (H12) tratá-los numa etapa de manutenção do M6, criada pelo `arquiteto` antes do gate. Ao criá-la, o `arquiteto` entrevistou o usuário e ampliou o escopo (H13). O pedido desta captura veio da sessão que fez a mudança.

## Origem

- Projeto ZenyHotelManager, repositório `/home/caio/repos/ZenyHotelManager`, commit `57eb5fa` na `main` ("Acrescenta a E18 do M6 (manutenção transversal) e registra as decisões", 2026-11-13), sem push.
- Arquivos: `docs/roadmaps/roadmap-m6-operacao-fechamento.md` (H12, H13, índice, seção "E18", última entrada do "Histórico de revisões"), `docs/ARCHITECTURE.md` (§5 item 6, §7 linhas "Paginação" e "Datas e valores", §11 "Identificadores e tipos", §13 primeiro parágrafo) e `docs/roadmaps/README.md`.
- O escriba conferiu o conteúdo no diff do commit (`git show 57eb5fa`).

## Limitações e incertezas

- As regras dos itens 3 a 6 são decisões ainda não implementadas; entram com a E18. As notas de tema devem registrá-las como decididas, não como comportamento atual.
- O 500 nas 6 consultas por data é provável e não foi reproduzido; o plano da E18 deve confirmá-lo com teste vermelho (o roadmap exige teste vermelho em pelo menos uma consulta por instante e uma por data).
- Fora do escopo da E18: datas e instantes em query string e path, e datas fora do alcance do banco no corpo de outros endpoints. O plano da E18 só confere e registra o achado.
- A E18 também prevê que o inventário dos caminhos com exceção *checked* dentro de `@Transactional` saia no handoff; ainda não existe.

## Possíveis conexões

- [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 (revisão humana) - fa5b192f]]
- [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]]
- [[ZenyHotelManager]]
- [[ZenyHotelManager - Estado por marco]]
- [[ZenyHotelManager - Convenções de API]]
- [[ZenyHotelManager - Auditoria]]
- [[ZenyHotelManager - Eventos e jobs]]
- [[ZenyHotelManager - Docker, observabilidade e CI]]
- [[ZenyHotelManager - Schemas, migrações e views de relatório]]
