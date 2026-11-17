---
type: knowledge
status: processed
created: 2026-10-22
projects:
  - "[[ZenyHotelManager]]"
sources:
  - "[[2026-10-22 - ZenyHotelManager - Auditoria - a4fe3210]]"
  - "[[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]]"
---
# ZenyHotelManager - Auditoria

Referência técnica do projeto [[ZenyHotelManager]]: @Audited, AuditContext, retratos mascarados, recusas e a trilha audit.audit_entry.

Texto literal do `CLAUDE.md` do repositório, linhas 520–539, no commit `a6c0f03` (2026-10-22), escrito pelos agentes que executaram as etapas M0 E01 a M5 E03; integrado sem resumo nem reescrita. Referências como "SPEC", "ARCHITECTURE §x", "RF-…", "RN-…", "Hn" e "Mx Ey" apontam para `docs/SPEC.md`, `docs/ARCHITECTURE.md` e `docs/roadmaps/` do repositório; menções a uma seção (por exemplo, seção "Transições de hospedagem") apontam para outra parte do antigo `CLAUDE.md`, hoje numa das notas de tema listadas no hub. Mudanças posteriores chegam por capturas "ZenyHotelManager - atualização Mx Ey" (fluxo no hub).

---

- **Auditoria** (RF-ACS-11, RNF-11, ARCHITECTURE §5 e §8.3, M1 E04). A anotação e as portas ficam na raiz do `shared` (`Auditing.kt`); o aspecto, em `shared/infrastructure/audit/`; a trilha, no módulo `audit`.
  - **Regra:** todo caso de uso de escrita (método público `@Transactional` sem `readOnly` em `application`) leva `@Audited("<módulo>.<entidade>.<verbo>")`, com o código estável da ação em minúsculas e kebab-case (`iam.user.reset-password`). A regra ArchUnit `writeUseCasesAreAudited` (`LayerArchitectureTest`) barra o que faltar. Jobs de expurgo de dados transitórios em `infrastructure` (refresh tokens trocados, chaves de idempotência) ficam fora, como dados técnicos; o expurgo de anexos órfãos não é técnico (o anexo é dado de usuário) e passa por um caso de uso auditado, com ator sistema.
  - **Transação:** o aspecto roda **dentro** da transação do caso de uso. Ela fica por fora pela ordem fixada em `AuditOrdering` (o `@EnableTransactionManagement` do `shared` substitui o do Boot). As entradas vão pela porta `AuditTrail`, implementada pelo `audit` com `JdbcClient`, na mesma transação: rollback não deixa entrada, e falha ao montar ou gravar a entrada desfaz a escrita. Fora de uma transação de escrita, o método falha com `IllegalStateException` antes de executar. *(Desde a M6 E18, exceção checked também desfaz a transação, `rollbackOn = ALL_EXCEPTIONS`: subseção "Rollback em toda exceção: comportamento atual" em "Atualizações por capturas".)*
  - **Descrever a mudança:** injete `AuditContext` e, dentro do método, descreva cada entidade:
    - `track(tipo, id) { retrato }` para uma que já existe: o retrato de agora é o "antes" e o do fim do método, o "depois"; sem mudança, não há entrada;
    - `created(tipo, id) { retrato }` para uma criada;
    - `record(tipo, id, antes, depois)` com os valores prontos;
    - `attributeTo(usuário, sessão)` quando a requisição não traz o ator (login, refresh);
    - `approval(id)` para a aprovação de superior (a porta `Authorization` já o chama ao consumir o token);
    - `noChanges()` quando nada foi escrito.

    Sem nenhuma descrição, grava-se uma entrada só com a ação.
  - **Retratos:** data classes ou mapas com só o que interessa a quem audita (os do `iam` estão em `iam/application/IamAudit.kt`), nunca hash de senha ou PIN, token nem valor decifrado. A trilha ainda mascara como `"***"`, em qualquer nível do JSON:
    - a propriedade anotada com `@AuditMasked`;
    - a propriedade cujo nome tem `password`, `pin`, `token`, `secret`, `hash`, `salt`, `credential`, `cipher` ou `encrypted` (exceto valor booleano, como `hasPin`);
    - o texto com formato de valor cifrado pelo `FieldCipher` (`v1:<chave>:…`), de token selado pelo `TokenSealer` (`t1:<chave>:…`, com ao menos os 38 caracteres de nonce e tag), hash Argon2/bcrypt ou JWT.
  - **Recusas:** `@Audited(…, recordRejections = true)` grava também a recusa por `DomainException` (resultado `REJECTED` com o `code`), com as entidades já descritas. Ela só fica se a transação confirmar (`noRollbackFor`, como a falha de login). Recusa sem entidade descrita (login inexistente, refresh desconhecido) não gera entrada.
  - **Tabela e consulta:** a tabela é `audit.audit_entry`: quem (usuário e sessão; nulos = o sistema), quando, ação, resultado e código do erro, tipo e id da entidade, `before_state`/`after_state` em `jsonb` e `approval_id`. O papel da aplicação só tem `SELECT, INSERT` nela. `GET /api/v1/audit-entries` (`userId`, `entityType`, `entityId`, `from` inclusive e `to` exclusive, cursor, das mais recentes para as mais antigas) exige `audit.read` (`AuditPermissions`), que só o Administrador recebe de saída.
  - **Testes:** o caso de uso só de teste `src/test/kotlin/auditexample/` (`AuditProbeConfiguration`) exercita o aspecto; `IamAuditTest` confere cada escrita do `iam`.

---

## Atualizações por capturas

Texto das capturas de atualização publicadas pelo orquestrador dos lotes no repositório, integrado sem resumo nem reescrita. Vale sobre o texto literal acima quando trata do mesmo assunto. As notas do curador estão marcadas como tal.

### Rollback em toda exceção (decisão da M6 E18, 2026-11-13; implementada em 2026-11-15)

*Nota do curador (2026-11-16):* **implementada na M6 E18.** O comportamento atual e o inventário estão na subseção "Rollback em toda exceção: comportamento atual (M6 E18, 2026-11-15)", abaixo, que substitui esta. O título dizia "ainda não implementada".

Origem: [[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]] (item 4; ARCHITECTURE §5 item 6). Quando esta subseção foi escrita, era decisão registrada na ARCHITECTURE, ainda fora do código (entrou com a M6 E18). Complementa o marcador "**Transação**" do texto literal acima.

- O `@EnableTransactionManagement` do `shared` passa a usar `rollbackOn = RollbackOn.ALL_EXCEPTIONS`: exceção *checked* que escapa de um caso de uso passa a desfazer a escrita, e a escrita nunca fica confirmada sem trilha.
- O `noRollbackFor` explícito de quem grava a recusa (`recordRejections`, como login com falha) continua valendo.
- Alternativa descartada (ARCHITECTURE §5 item 6): `rollbackFor = Throwable` em cada caso de uso.
- A E18 também prevê que o inventário dos caminhos com exceção *checked* dentro de `@Transactional` saia no handoff; ainda não existe. *(Saiu no handoff da E18: subseção abaixo.)*

### Rollback em toda exceção: comportamento atual (M6 E18, 2026-11-15)

Origem: [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E18 - a68d398b]] (item 3, parte de transações; fatos do handoff da E18, segundo a captura). Substitui a subseção "Rollback em toda exceção (decisão da M6 E18, 2026-11-13)", acima: agora é comportamento atual. Complementa o marcador "**Transação**" do texto literal. A etapa está na branch `roadmap/m6-operacao-fechamento`, ainda fora da `main` (ver [[ZenyHotelManager - Estado por marco]], "M6 E18"). As sondas de teste estão em [[ZenyHotelManager - Testes de integração]] ("M6 E18").

- `@EnableTransactionManagement(..., rollbackOn = RollbackOn.ALL_EXCEPTIONS)` em `TransactionOrderingConfiguration` (`shared/infrastructure/audit/AuditAspect.kt`). Exceção *checked* que escapa de um caso de uso `@Transactional` desfaz a escrita, e a escrita não fica mais confirmada sem trilha (o `AuditAspect` só grava em sucesso ou em `DomainException`).
- **`noRollbackFor` seguem valendo**, porque a regra explícita é mais específica que a de `Exception`: login e refresh com falha, aprovação recusada (`Authentication` ×2, `TokenRefreshService`, `Approvals`) e `files` (`FilesService.download`, `recordRejections`). Teste: "an explicit noRollbackFor still commits with ALL_EXCEPTIONS", com ataques (subclasse da listada, *checked* não listada, `Error`, ouvinte `REQUIRES_NEW`, transação unida).
- **Efeito novo, provado em teste:** uma *checked* que um chamador **engole** dentro de uma transação unida (REQUIRED) faz o commit externo falhar com `UnexpectedRollbackException`. KDoc sugerido em `TransactionOrderingConfiguration` (ainda não escrito).
- **`endofday`:** as três transições (`EndOfDayRunTransitions`) perderam o `rollbackFor = Throwable` local; o comportamento não mudou (o teste `a checked exception from the work undoes the complete like any other` segue verde).
- **`TransactionTemplate` programático** desfaz em qualquer `Throwable`, independente do atributo (conferido no bytecode do `spring-tx` 7.0.10). Proxies de repositório do Spring Data têm fonte de atributos própria e não herdam o `rollbackOn`; é inofensivo, porque entram na transação do caso de uso, que decide.
- **Inventário dos caminhos com exceção *checked* dentro de `@Transactional`** (critério da etapa): **nenhum caminho dependia do commit**. Onde havia escrita antes do ponto que lança, o commit antigo era o defeito.
  - `printing`: `HtmlPdfRenderer.render` (`SAXException`/`IOException`) via `PrintingApiService.render`/`print`; os `pdf(...)` são `readOnly` e os `print(...)` renderizam antes da única escrita (`jobs.enqueue`): antes confirmava uma transação vazia, agora desfaz uma vazia.
  - `shared`: `StreamController`/`RealtimeHub` fora de transação; `IdempotencyFilter` fora de proxy, grava por `TransactionTemplate`; as cifras capturam `GeneralSecurityException` na decifragem; `OfflineCommandService` já aplicava o handler num `TransactionTemplate`.
  - `files`: o `presigned.url().toURI()` (`URISyntaxException`, `S3FileStorage.kt:183`) é alcançado por `FilesService.downloadUrl` (não por `download`, como dizia o plano), sem escrita antes. No `upload`, o reencode roda antes das escritas e um rollback agora também apaga o objeto do S3 (`removeOnRollback`), como no caminho de `RuntimeException`.
  - `MessageDigest.getInstance("SHA-256")` (`PrintAgent`, `OfflineChanges`, `RefreshTokens`, `PushDevice`, `FileContentRules`, `IdempotencyFilter`): inalcançável.
  - `fnrh`: `RestClient` converte `IOException` em `ResourceAccessException`; envio fora de transação.
  - `notifications`: `FcmPushGateway` captura as exceções; **achado**: `SignedJWT.sign` declara `JOSEException`, não capturada em `requestAccessToken` (virou pendência para o `arquiteto`: [[ZenyHotelManager - Estado por marco]], "M6 E18"). O ouvinte de push não tem escrita própria.
  - `endofday`, `reservations`, `guests` e jobs (`ProvisionalExpiry`, `InventoryHorizonJob`, `GuestDocumentRekeyJob`, `FileOrphanPurgeJob`): transação própria por item ou `TransactionTemplate`, sem transação externa. `iam`: `JwtEncodingException` é não-checada.
  - Dos 83 `catch`/`runCatching` amplos de `src/main`, nenhum engole uma *checked* vinda de um proxy que compartilhe a transação (conferência por amostragem da revisora nos cinco `noRollbackFor` e nos `catch` dos casos de uso).
- **Teste do critério:** `RollbackOnAllExceptionsTest` "a checked exception from an audited use case leaves neither the write nor the trail entry", vermelho antes (`expected:<0> but was:<1>`).

*Nota do curador (conferência por `git` em 2026-11-16, só leitura, no `ed0f5ab`):* `shared/infrastructure/audit/AuditAspect.kt` tem `rollbackOn = RollbackOn.ALL_EXCEPTIONS` (linha 101). O inventário, os `noRollbackFor` e os testes não foram conferidos.

---

## Proveniência

- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - Auditoria - a4fe3210]] (capture_id: a4fe3210-4817-4e56-97e8-e9821d0b1ee1): texto literal do `CLAUDE.md` do repositório ZenyHotelManager (linhas 520–539, commit `a6c0f03`), integrado sem alteração; o tipo Knowledge em `20 Knowledge/` foi escolhido pelo usuário no processamento.
- 2026-11-15 — [[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]] (capture_id: 009e3130-5bd9-4e8b-bd56-81c7fc440b81): `rollbackOn = RollbackOn.ALL_EXCEPTIONS` no `@EnableTransactionManagement` do `shared` (decisão para a M6 E18, item 4 da captura), em "Atualizações por capturas" (seção criada).
- 2026-11-16 — [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E18 - a68d398b]] (capture_id: a68d398b-2037-4b20-af27-8039b163ae0e): `rollbackOn = ALL_EXCEPTIONS` como comportamento atual, `noRollbackFor`, efeito da checked engolida e inventário dos caminhos com exceção checked (item 3 da captura), na subseção nova "Rollback em toda exceção: comportamento atual", que substitui a da decisão de 2026-11-13 (mantida com marca); remissão no marcador "Transação"; nota do curador com a conferência por `git`.
