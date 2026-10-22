---
type: capture
status: archived
created: 2026-10-22
capture_id: a4fe3210-4817-4e56-97e8-e9821d0b1ee1
---
# ZenyHotelManager - Auditoria

## Conteúdo capturado

Texto **literal** do `CLAUDE.md` do repositório ZenyHotelManager, linhas 520–539, no commit `a6c0f03` (2026-10-22): @Audited, AuditContext, retratos mascarados, recusas e a trilha audit.audit_entry. Foi escrito pelos agentes que executaram as etapas do roadmap (M0 E01 a M5 E03); as decisões do usuário aparecem no próprio texto com a data e a indicação "decisão do usuário" (ou "decidida pela opção recomendada em nome do usuário (delegado ao orquestrador)"). Nada foi resumido nem reescrito.

---

- **Auditoria** (RF-ACS-11, RNF-11, ARCHITECTURE §5 e §8.3, M1 E04). A anotação e as portas ficam na raiz do `shared` (`Auditing.kt`); o aspecto, em `shared/infrastructure/audit/`; a trilha, no módulo `audit`.
  - **Regra:** todo caso de uso de escrita (método público `@Transactional` sem `readOnly` em `application`) leva `@Audited("<módulo>.<entidade>.<verbo>")`, com o código estável da ação em minúsculas e kebab-case (`iam.user.reset-password`). A regra ArchUnit `writeUseCasesAreAudited` (`LayerArchitectureTest`) barra o que faltar. Jobs de expurgo de dados transitórios em `infrastructure` (refresh tokens trocados, chaves de idempotência) ficam fora, como dados técnicos; o expurgo de anexos órfãos não é técnico (o anexo é dado de usuário) e passa por um caso de uso auditado, com ator sistema.
  - **Transação:** o aspecto roda **dentro** da transação do caso de uso. Ela fica por fora pela ordem fixada em `AuditOrdering` (o `@EnableTransactionManagement` do `shared` substitui o do Boot). As entradas vão pela porta `AuditTrail`, implementada pelo `audit` com `JdbcClient`, na mesma transação: rollback não deixa entrada, e falha ao montar ou gravar a entrada desfaz a escrita. Fora de uma transação de escrita, o método falha com `IllegalStateException` antes de executar.
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

## Contexto

Em 2026-10-22 o usuário pediu para enxugar o `CLAUDE.md` do repositório (638 linhas, ~435 KB) e passar o conteúdo para um projeto no Second Brain, de onde os agentes do projeto o leriam por um hook obrigatório. Esta captura é uma de várias, uma por tema. O plano, as decisões da entrevista e a estrutura proposta estão na captura-índice [[2026-10-22 - ZenyHotelManager - migração do CLAUDE.md para o brain - índice e decisões - 03d0ed3e]] (capture_id: 03d0ed3e-788d-43f3-b338-79e3077d799f).

## Origem

- Projeto: ZenyHotelManager (servidor do PMS Zeny Hotel Manager), repositório local `/home/caio/repos/ZenyHotelManager`.
- Arquivo: `CLAUDE.md`, linhas 520–539, commit `a6c0f03` (branch `main`).
- Sessão do Claude Code iniciada no repositório (agente externo), 2026-10-22.

## Por que registrar

É a referência técnica que os agentes do projeto precisam para trabalhar neste tema. Depois da integração, sai do `CLAUDE.md` e passa a viver no brain (decisão do usuário, 2026-10-22).

## Sugestão do agente para a integração

Sugestão, não decisão: uma nota `ZenyHotelManager - Auditoria`, ligada pela nota de projeto (hub) do ZenyHotelManager, com este texto (o curador decide o `type` e se divide ou funde com outra captura). Manter o texto técnico como está: caminhos, nomes de classes e códigos de erro são usados pelos agentes ao editar o código.

## Limitações e incertezas

- O texto descreve o código no commit `a6c0f03`; etapas seguintes publicarão capturas de atualização ("ZenyHotelManager - atualização Mx Ey").
- Referências como "SPEC", "ARCHITECTURE §x", "RF-…", "RN-…", "Hn" e "Mx Ey" apontam para `docs/SPEC.md`, `docs/ARCHITECTURE.md` e `docs/roadmaps/` do repositório, que não foram copiados.
- Valores como `zeny`/`zeny`, `zeny_app` e `zeny-app-dev-only`, quando aparecem, são padrões públicos de desenvolvimento local já versionados no repositório, não credenciais de um ambiente real.

## Possíveis conexões

- [[2026-10-22 - ZenyHotelManager - migração do CLAUDE.md para o brain - índice e decisões - 03d0ed3e]]
