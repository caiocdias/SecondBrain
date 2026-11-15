---
type: knowledge
status: processed
created: 2026-11-15
projects:
  - "[[ZenyHotelManager]]"
sources:
  - "[[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 - 4dd12e66]]"
  - "[[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 (revisão humana) - 25b5cce4]]"
---
# ZenyHotelManager - Módulo printing

Referência técnica do projeto [[ZenyHotelManager]]. Impressão: cadastro de agentes e impressoras, fila de jobs, protocolo de entrega ao agente (SSE e long-poll) e a credencial de serviço do agente. Estado: M5 E10 concluída (2026-11-11); desde a M5 E11 (2026-11-12) o módulo também renderiza documentos (ficha, extrato e confirmação), ver "Documentos (M5 E11)". O agente de impressão em si fica em repositório próprio e segue o protocolo descrito aqui e em ARCHITECTURE §14.

Referências como "ARCHITECTURE §x", "SPEC §x", "D-E10-n" e "Hn" apontam para `docs/ARCHITECTURE.md`, `docs/SPEC.md` (§8.2.18), `docs/roadmaps/roadmap-m5-recepcao-fnrh.md` ("Decisões do lote E10") e `docs/superpowers/plans/2026-11-11-m5-recepcao-fnrh-e10.md` do repositório. Texto da captura de fechamento da E10, composto do rascunho do orquestrador e da ARCHITECTURE (§8.1, §8.3, §10, §12, §13 e §14), integrado sem resumo. O estado e as decisões do lote estão em [[ZenyHotelManager - Estado por marco]].

---

## Camada e dependências

- Camada Plataforma. Pacote `com.zeny.hotel.printing`, com `PrintingModule.kt` na raiz.
- `allowedDependencies` (M5 E11): o `printing` depende de `shared`, `hotel` e `files` (teste exato no `ModularityTest`; ARCHITECTURE §3.1), nunca escuta eventos (provado por ArchUnit no `DocumentsStageEndToEndTest`).
- Consumidores da `PrintingApi`: `billing` (extrato), `frontdesk` (ficha) e `reservations` (confirmação) (auditoria G4 da M5 E12).
- Não importa `iam` nem `notifications` (sem alerta de falha: o `FAILED` fica na lista e na métrica).

## Pacotes

- Raiz (API pública): `PrintingModule`, `PrintingApi` (`enqueue(NewPrintJob(printerId, documentType, content))`, conteúdo até 5 MiB, `zeny.printing.max-content-bytes`; **não confere permissão**, quem chama se autoriza; desde a E11 também `render` e `print`, ver "Documentos (M5 E11)"), `PrintingPermissions` e `PrintingTypes.kt` (`PrinterKind` `THERMAL_ESCPOS`/`A4_PDF`, cada um com o tipo de mídia; `PrintJobStatus`; `PrintingErrorCodes`).
- `domain`: `PrintAgent`, `Printer`, `PrintJob`. `application`: `PrintAgentsService`, `PrintJobsService`, `PrintAgentJobsService`, `PrintAgentConnections`, `PrintAgentStreams`, `PrintJobsMaintenance`, `PrintingAudit`. `infrastructure`: persistência, `PrintAgentRealm`, `PrintingProperties`, o job agendado e `PrintingMetrics`. `web`: administração, fila e rotas do agente.

## Schema `printing` e migrações

- `print_agent` (hash do token, `token_generation`, `active`, `last_seen_at`), `printer`, `print_job` (posição por sequence, `content` em `bytea` cifrado, `content_purged_at`, `delivered_to`, `failure_code`), com CHECKs de estado. Migrações `V2026_11_11_1000` e `V2026_11_11_1001` na pasta `printing/`.
- O conteúdo é cifrado pelo `ContentCipher`, com o id do job como dado associado, e fica só nessa coluna. A rotação de chave do anel ainda não o re-cifra (pendência da M8 E15); na prática ele dura até cerca de 48 h (ARCHITECTURE §8.3).

## Agente e token (D-E10-1 e D-E10-11)

- Token `zpa_` + 32 bytes de `SecureRandom` em base64url; no banco só o SHA-256 em hex. Aparece **uma vez**, na criação e na rotação (`Cache-Control: no-store`, sem `@Idempotent`, porque a resposta guardada teria o token em claro). A rotação invalida o anterior na hora; a desativação apaga o hash.
- `token_generation` sobe a cada emissão e é o `credentialStamp` do `ServicePrincipal`, conferido a cada chamada e a cada volta do stream. O realm recusa sem consulta o token sem o prefixo `zpa_`.
- **Realm do agente** (auditoria G4 da M5 E12): `PrintAgentRealm` (`printing/infrastructure/PrintAgentRealm.kt:19-44`): `name = "print-agent"`, `pathPrefix = "/api/v1/print-agents/me/"`, `openApiScheme = "printAgentToken"`; `authenticate` só consulta o banco se o token começa por `zpa_`, numa transação `REQUIRES_NEW`, e grava o contato (`recordContact`, no máximo uma vez por minuto, `printing/infrastructure/PrintingPersistence.kt:22`). Falha de banco propaga (`500`), nunca `401`.
- O contato (`last_seen_at`, no máximo uma vez por minuto) é gravado numa transação curta, fora do versionamento do cadastro e **sem trilha**, por ser registro técnico, como a sessão de dispositivo do `iam`.
- O mecanismo de autenticação em si está em [[ZenyHotelManager - Segurança, autenticação e autorização]] (subseção "Credencial de serviço e impressão (M5 E10, 2026-11-11)").

## Rotas e permissões

| Rota | Permissão e regras |
|---|---|
| Criar, alterar e desativar impressora e todo o cadastro de agentes | `printing.agents.manage` (só o Administrador) |
| `GET /api/v1/printers` e `GET /api/v1/printers/{id}` | `printing.jobs.read` (Gerente e Recepcionista; `PrintAgentsService.kt:199,205`) |
| `POST /api/v1/print-jobs` | `printing.jobs.manage` (Gerente), `@Idempotent`, conteúdo em base64 com preenchimento, até 700 KiB (`zeny.printing.max-manual-content-bytes`, abaixo do limite de corpo da idempotência) |
| `GET /api/v1/print-jobs` | cursor, **sem o conteúdo** |
| `/api/v1/print-agents/me/…` (identidade, `jobs/stream`, `jobs?wait=`, `jobs/{id}/content`, `jobs/{id}/ack`) | só o esquema `printAgentToken` |

- O `{id}` das rotas de administração aceita só `[0-9a-fA-F-]+`.
- As duas leituras de impressora são a exceção ao `printing.agents.manage` na administração (auditoria G4 da M5 E12).
- Códigos de problema em `PrintingErrorCodes` (entre eles `PRINT_JOB_NOT_ACKNOWLEDGEABLE`, `409`).

## Fila e entrega (ARCHITECTURE §14)

- Ciclo: `PENDING` → `SENT` → `PRINTED` ou `FAILED`. O job nasce `PENDING` com uma **posição** (sequence); a reivindicação por um agente o passa a `SENT` (`attempts + 1`, `sent_at`, `delivered_to`). Só entram na entrega os `PENDING` de impressoras **ativas** do agente autenticado, em ordem de posição e sem filtro de posição.
- Reivindicação atômica: `SELECT … FOR UPDATE SKIP LOCKED`, com `version`; duas conexões nunca levam o mesmo job. Consulta ao banco a cada 1 s (`zeny.printing.delivery-poll-interval`); não há sinal em memória nem `LISTEN/NOTIFY` (alternativas descartadas por terem dois caminhos de entrega ou peça nova de runtime).
- SSE em `GET /print-agents/me/jobs/stream`: evento `job`, `id` = posição, `data` com `id`, `printerId`, `documentType`, `mediaType`, `attempts` e `createdAt`; o conteúdo vem de `GET …/jobs/{id}/content` (só do job `SENT` entregue àquele agente e de impressora dele). `: heartbeat` a cada 15 s. Na conexão, reenvia os `SENT` sem confirmação de posição maior que o `Last-Event-ID` (todos, sem ele; valor não numérico vale como ausente) e reivindica os `PENDING`. Escreve `: ping` antes de cada reivindicação, reivindica **um job por vez** e, se a escrita falha, devolve o job a `PENDING` sem gastar tentativa (`printing.job.release`). Um stream por agente (o novo despeja o anterior); acaba em `stream-max-duration` (30 min), quando o agente deixa de ser válido (inativo ou token trocado) e na parada do servidor.
- Long-poll em `GET /print-agents/me/jobs?wait=` (0 a 30 s, padrão 25): `200 []` no vazio e quando despejado pelo limite de conexões ou pela parada do servidor (o agente não deve repetir sem pausa). `zeny.printing.max-connections-per-agent` (2) vale só para os long-polls. Se o servidor já fechou a resposta por tempo quando os jobs são reivindicados, devolve-os a `PENDING` sem gastar tentativa; a resposta perdida depois de enviada só volta pelo `ack-timeout`, gastando uma tentativa.
- Confirmação `POST …/jobs/{id}/ack`, corpo `{result: "PRINTED"|"FAILED", failureCode}`, `204`: `result` só como texto; `failureCode` opcional, `[A-Z][A-Z0-9_]{0,49}`, nunca texto livre. Job de impressora do agente que não está `SENT` entregue a ele: `409 PRINT_JOB_NOT_ACKNOWLEDGEABLE`; job de outro agente ou inexistente: `404`. O agente deduplica pelo id na reentrega e confirma de novo sem imprimir.

## Manutenção, validade e métrica

- Job `printing-jobs-maintenance` (1 min, ShedLock, `lockAtMostFor` PT10M, adiado nos testes por `PRINTING_MAINTENANCE_DEFERRED`; intervalo `zeny.printing.maintenance-interval`): `SENT` sem confirmação em `ack-timeout` (2 min) volta a `PENDING` com posição nova (passa do `Last-Event-ID`) e, na reivindicação de número `max-attempts` (3), vira `FAILED`/`ACK_TIMEOUT`; `PENDING` com mais de `pending-ttl` (24 h) vira `FAILED`/`EXPIRED`; `PENDING` e `SENT` de impressora inativa, ou de impressora ativa de agente desativado, viram `FAILED`/`PRINTER_INACTIVE`; o conteúdo é apagado (`NULL`, `content_purged_at`) `content-retention` (24 h) depois do fim (o expurgo repetido não move o instante). Uma transação por job, com `lockById`; confirmação e manutenção travam a linha, então quem chega depois vê o estado novo.
- Métrica `zeny_printing_jobs{status}` (gauge: `PENDING` e `SENT` da fila e `FAILED` só dos terminados dentro de `content-retention`). Sem alerta. A listagem e os candidatos da manutenção usam **projeção sem o conteúdo**.
- **Trilha** (auditoria G4 da M5 E12; `printing/application/PrintingAudit.kt:8-19`, `PrintJobsService.kt:251`): `printing.agent.create`, `printing.agent.rotate-token`, `printing.agent.deactivate`, `printing.printer.create`, `printing.printer.update`, `printing.printer.deactivate`, `printing.job.create` (rota manual e `PrintingApi.enqueue`/`print`), `printing.job.claim`, `printing.job.ack`, `printing.job.release` (as três últimas do ator sistema). O contato do agente não tem trilha.
- **Validação das propriedades** (auditoria G4): diferente do `fnrh`, `PrintingProperties` valida limites ("precisa ser positivo"; `max-manual-content-bytes` não passa de `max-content-bytes`) e a partida falha se violados (`PrintingProperties.kt:49,56`).

## Documentos (M5 E11)

Texto da captura de fechamento da E11 (2026-11-12), integrado sem resumo. Decisões D-E11-n no plano `docs/superpowers/plans/2026-11-11-m5-recepcao-fnrh-e11.md`; letras do lote em "Decisões do lote E11" do roadmap.

- **API pública** (`PrintingApi`, um único bean: a fachada `PrintingApiService` da `application`; o `PrintJobsService` deixou de implementá-la e mantém o `enqueue` auditado `printing.job.create`): `render(DocumentRequest, DocumentFormat): RenderedDocument` e `print(DocumentRequest, printerId): UUID` (id do job; formato pelo `PrinterKind`: `A4_PDF` → PDF, `THERMAL_ESCPOS` → ESC/POS; `documentType` do job = código do template). Não confere permissão: o dono confere a dele (D2). Tipos na raiz (`PrintingDocuments.kt`): `DocumentTemplate(code, title, xhtmlTemplate, textTemplate)`, `ModuleDocumentTemplates`, `DocumentRequest(templateCode, model)`, `DocumentFormat`, `RenderedDocument`, e os DTOs `PrintDocumentRequest {printerId}` e `PrintJobAccepted {printJobId}`, reaproveitados pelas rotas dos donos.
  - *Nota do curador (conferência em 2026-11-15, só leitura, no merge `5ed46c3`):* a interface `PrintingApi` continua declarando `enqueue(job: NewPrintJob): UUID` ao lado de `render` e `print`.
- **Como registrar um template e imprimir** (critério de aceite da E11):
  1. No arquivo do serviço do documento, na `application` do módulo dono, declare um `object` que implementa `ModuleDocumentTemplates` (`module = "<módulo>"`) com um `DocumentTemplate("<módulo>.<documento>", título, "templates/<módulo>/<nome>.xhtml", "templates/<módulo>/<nome>.txt")`, e publique-o num `@Bean` de uma `@Configuration` no mesmo arquivo. O `DocumentTemplateCatalog` recusa a partida com código repetido, prefixo de outro módulo, código fora de `[a-z][a-z0-9]*(\.[a-z][a-z0-9-]*)+`, caminho fora de `templates/<módulo>/` ou arquivo inexistente.
  2. Escreva o `.xhtml` (XHTML bem formado, `TemplateMode.XML`) com um fragmento `th:fragment="body"`, e o `.txt` (`TemplateMode.TEXT`; linha `---` vira régua; quebra em 48 colunas automática). Use só `document.*` (o modelo) e o utilitário `fmt` (`date`, `time`, `instant`, `money`, `percent`, `cnpj`). Nada de `<style>`: use as classes do `<head>` do layout (`table.lines`, `td.amount`, `.muted`, `.total`, `h1`, `h2`). Proibidos: `th:utext`, `[( … )]`, pré-processamento (`__${`, `__*{`, `__#{`, `__@{`, `__~{` e `__` em atributo `th:*` ou em `[[…]]`) e `th:insert`/`th:replace`/`th:include` com `${`; o `DocumentTemplatesSafetyTest` varre `templates/**`.
  3. No serviço: confira a permissão do dono antes de tudo; monte o modelo só com `Map`/`List` e folhas `String`, `Number`, `Boolean`, `LocalDate`, `LocalTime`, `Instant`, `Money`, `Percent` ou `null`, até 32 níveis (outro tipo, ciclo ou profundidade maior: `IllegalArgumentException`); chame `printing.render(...)` para o PDF e `printing.print(...)` no `print`, que é `@Audited` + `@Transactional` com retrato só de ids. Devolva o código do documento junto do PDF para o nome do arquivo.
  4. Rotas no `web` do dono: `GET …/<documento>/pdf` (`200 application/pdf`, `format: binary`, `Content-Disposition: attachment; filename="<doc>-<código>.pdf"`, `Cache-Control: no-store`) e `POST …/<documento>/print` (`@Idempotent`, corpo `PrintDocumentRequest`, `202 PrintJobAccepted`). Erro sai em `application/problem+json` mesmo com `Accept: application/pdf`.
- **Layout e contexto:** `templates/printing/layout.xhtml` (só PDF) com cabeçalho (nome fantasia, razão social, CNPJ, Cadastur, inscrição municipal, endereço, logotipo) e rodapé ("Emitido em dd/MM/yyyy HH:mm" no fuso do hotel, "Página X de Y"); o corpo entra por um único `th:insert="~{${bodyTemplate} :: body}"`. Contexto só com `document`, `hotel`, `logo`, `fmt`, `issuedAt`, `title`, `bodyTemplate` (o modelo não sombreia o resto). Hotel não configurado: "Hotel", sem logotipo.
- **Limpeza do texto:** toda `String` do modelo e do perfil do hotel em NFC; `Cc` (inclusive `\n`, `ESC`, `GS`) vira espaço, `Cf` (bidi, largura zero) é removido, espaços colapsam. PDF com fontes base-14 (WinAnsi; fora dele, `?`); ESC/POS em IBM850 (`ESC t 2`; o que não cabe é decomposto e, se sobrar, `?`). O modo TEXT escapa como HTML e a fachada desfaz as entidades numa passagem só antes da codificação. Sem fonte embutida (nome em escrita não latina sai com `?`).
- **Sem recurso externo:** `HtmlPdfRenderer` faz o parse com `DocumentBuilderFactory` seguro (sem DTD, sem entidade externa, sem XInclude) e entrega o DOM ao openhtmltopdf; o resolvedor de URI só aceita `data:`; o log do openhtmltopdf passa por um `RedactedXRLogger` que não registra a carga (a URI `data:` vazava em WARN).
- **ESC/POS:** `ESC @`, `ESC t 2`, cabeçalho centralizado só com texto (sem logotipo), corpo em 48 colunas (`ESC_POS_COLUMNS`, 80 mm), rodapé, 4 avanços e corte parcial (`GS V 66 0`), composto num só lugar (`EscPosDocument`).
- **Logotipo:** lido por `FilesApi.readContent` (finalidade `hotel.logo`, dono = id do hotel) num `TransactionTemplate` `REQUIRES_NEW` + `readOnly` (`HotelLogoReader`), para a falha não marcar a transação do dono como *rollback-only*; reduzido por `DocumentLogo.prepare` (PNG/JPEG até 2 MB e 50 MP, lado maior até 400 px, saída PNG). WEBP, ilegível, apagado, objeto ausente ou falha do armazenamento: documento sem logotipo + `WARN`. Custo: uma 2ª conexão do pool durante a leitura; sem cache. A leitura está em [[ZenyHotelManager - Módulo files]] e o perfil do hotel (`HotelApi.profile()`) em [[ZenyHotelManager - Módulos hotel e staff]].
- **Bibliotecas** (D-E11-1): `io.github.openhtmltopdf:openhtmltopdf-pdfbox` 1.1.110 (fork mantido; **LGPL-2.1+**), PDFBox 3.0.8, `thymeleaf-spring6` 3.1.5 do BOM (sem o starter, sem `ViewResolver`), `pdfbox` só em teste; o PDFBox subiu o `commons-logging` de 1.3.6 para 1.4.0 no lockfile; o `unbescape` é usado direto, mas só chega como transitivo do Thymeleaf. Imagem Docker: 171,5 MB → 178,0 MB (+6,6 MB; build de 115 s para 142 s).
- **Limites conhecidos:** logotipo sem cache; regra "sem `<style>` em template de dono" só por convenção (a varredura não a impõe); quem tem a permissão do dono imprime em qualquer impressora ativa.
- Documentos dos donos na E11: extrato em [[ZenyHotelManager - Módulo billing (caixa, pagamentos, caução e encerramento)]], ficha de registro em [[ZenyHotelManager - Hospedagem e recepção]], confirmação de reserva em [[ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)]]; convenção das rotas em [[ZenyHotelManager - Convenções de API]].
- **Templates dos donos** (auditoria G4 da M5 E12): `templates/billing/statement.{xhtml,txt}`, `templates/frontdesk/registration-card.{xhtml,txt}`, `templates/reservations/confirmation.{xhtml,txt}` e o layout `templates/printing/layout.xhtml` (só PDF).

## Decisões da revisão humana da E10 (decisão do usuário, 2026-11-11)

Origem: [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 (revisão humana) - 25b5cce4]] (entrevista do fim do lote, registrada no roadmap da branch `roadmap/m5-recepcao-fnrh`, commit `7aa2527`). O usuário aprovou as quatro decisões de arquitetura, cada uma com a opção recomendada:

- A credencial de serviço fica como porta em `shared` (`ServiceCredentialRealm` mais uma segunda cadeia de segurança). É o **padrão para M7 e M8**.
- O contrato com o repositório do agente é aprovado como está: token `zpa_`, esquema `printAgentToken`, evento SSE `job` com `id` = posição, `200 []` no long-poll, ack `{result, failureCode}`, e o agente deduplica por id.
- Um stream por agente; a contrapressão por ack fica para depois.
- Sem alerta de falha de impressão por enquanto. Um alerta pode vir pelo Prometheus/Alertmanager do M8 E18 (D19) sobre a métrica `zeny_printing_jobs`, sem aresta `printing` → `notifications`.

Seguem sem confirmação do usuário as decisões do lote E10 sobre prazos e limites, o ack `409`×`404` e o contato do agente sem trilha (lista em [[ZenyHotelManager - Estado por marco]]).

## Decisões da revisão humana da E11 (decisão do usuário, 2026-11-12)

Origem: [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E11 (revisão humana) - cca61b94]] (entrevista do fim do lote, registrada no roadmap da branch `roadmap/m5-recepcao-fnrh`, commit `6c87b04`, já na `main` local). Todas pela opção recomendada:

- **D-E11-1:** openhtmltopdf (LGPL-2.1+), PDFBox 3 e Thymeleaf mantidos. O aviso da LGPL deve ser registrado na documentação de implantação do M8.
- **D-E11-9:** o contrato das rotas de documentos fica aprovado como está: `GET …/pdf`, `POST …/print` com `@Idempotent` e `202`, `audience` padrão `GUEST` no PDF do extrato, impressão em qualquer impressora ativa por quem tem a permissão do documento.
- **D-E11-7:** `FilesApi.readContent` serve só para anexo comum (emenda à H18). Quem precisar ler anexo sensível pelo servidor acrescenta a leitura com trilha na etapa que precisar.
- **D-E11-12:** a porta `FolioOwnerDescriber` no `billing` é mantida e é o padrão para descrever o dono da conta.

Seguem revisáveis, sem confirmação do usuário, só as decisões do lote E11 (b) API de documentos no `printing` (D-E11-2 e 3) e (c) texto sem fonte embutida (D-E11-4), além da (i) execução em série por memória (lista em [[ZenyHotelManager - Estado por marco]]).

## Limites conhecidos

- Com a conexão meio aberta e o agente fora do ar, um job pode virar `FAILED`/`ACK_TIMEOUT` em cerca de 6 min.
- O registro de conexões (um stream por agente, limite de long-polls, despejo, encerramento na parada) é por instância; a entrega e a reivindicação valem com várias instâncias.
- `claimPending` e `unackedSent` ainda carregam o conteúdo; `PrintingProperties` fica em `infrastructure`.
- Fallback previsto na ARCHITECTURE §14: clientes desktop podem imprimir localmente o PDF devolvido pela API.

## Limitações

- A captura foi composta do rascunho do orquestrador e da ARCHITECTURE (§8.1, §8.3, §10, §12 a §14), que se confirmam entre si. O escriba não leu `docs/SPEC.md` §8.2.18, o parágrafo "Impressão" do README (seção "API"), o handoff da E10 nem o bloco "Decisões do lote E10" do roadmap.
- *Nota do curador (conferência no repositório em 2026-11-15, só leitura, no merge `6a025d5`):* as migrações são `V2026_11_11_1000__create_printing_tables.sql` e `V2026_11_11_1001__grant_printing_to_app_role.sql`, em `src/main/resources/db/migration/printing/`. `PrintingErrorCodes` (em `printing/PrintingTypes.kt`) declara `PRINT_AGENT_INACTIVE`, `PRINTER_INACTIVE`, `UNKNOWN_PRINT_AGENT`, `UNKNOWN_PRINTER`, `PRINT_AGENT_NOT_FOUND`, `PRINTER_NOT_FOUND`, `PRINT_JOB_NOT_FOUND`, `PRINT_JOB_NOT_ACKNOWLEDGEABLE`, `PRINT_CONTENT_TOO_LARGE`, `PRINT_CONTENT_EMPTY` e `PRINT_CONTENT_NOT_PDF`. Os nomes das colunas não foram conferidos.
- *Nota do curador (roadmap, commit `7aa2527`):* as notas da E10 para a próxima etapa sugerem, com PDFs reais, separar o conteúdo numa tabela própria lida só pela entrega do conteúdo e pelo expurgo; e listam como limpezas, além das de "Limites conhecidos", `PrintAgent.touch` e `tokenGeneration` redundantes no retrato da trilha, a coerção global do Jackson (número para enum ou texto), anterior à etapa, e testes de ataque grandes com algumas asserções frouxas.

---

## Proveniência

- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 - 4dd12e66]] (capture_id: 4dd12e66-191b-406d-a974-4ae7dca3e15f): nota criada com o texto proposto para o módulo (item 1 da captura), integrado sem resumo; notas do curador com a conferência das migrações, dos códigos de erro e das notas do roadmap.
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 (revisão humana) - 25b5cce4]] (capture_id: 25b5cce4-a919-4cf3-aaaf-99b5722239e8): decisões de arquitetura da E10 aprovadas pelo usuário na revisão humana.
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E11 - d1100f5a]] (capture_id: d1100f5a-58df-416a-b523-1db1d3eb3f19): dependências do módulo substituídas e seção "Documentos (M5 E11)" (item 1 da captura), sem resumo; nota do curador sobre o `enqueue`.
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E11 (revisão humana) - cca61b94]] (capture_id: cca61b94-000c-4d38-9f81-59e12c1d9f99): decisões da E11 aprovadas pelo usuário na revisão humana.
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 - 2c135bbf]] (capture_id: 2c135bbf-8248-4987-a617-dcb3fa94c0a5): complementos da auditoria G4 (consumidores da `PrintingApi`, realm do agente, leituras de impressora, trilha, validação das propriedades e templates dos donos); imagem e licença já constavam.
