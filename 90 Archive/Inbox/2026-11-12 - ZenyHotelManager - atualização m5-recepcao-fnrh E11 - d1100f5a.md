---
type: capture
status: archived
created: 2026-11-12
capture_id: d1100f5a-58df-416a-b523-1db1d3eb3f19
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E11

## Conteúdo capturado

Captura de fechamento da etapa M5 E11 (documentos: ficha de registro, extrato e confirmação), concluída em 2026-11-12 na branch `roadmap/m5-recepcao-fnrh`. O texto abaixo vem do rascunho do orquestrador, organizado por nota de tema; em cada nota diz se **substitui**, **complementa** ou **acrescenta**. As decisões D-E11-1 a 14 foram tomadas pelo orquestrador pela opção recomendada, **sem confirmação do usuário**; a E11 tem "Revisão humana: sim" e ela está **pendente**.

Esta captura vale sobre as capturas `2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 - 4dd12e66` (capture_id `4dd12e66-191b-406d-a974-4ae7dca3e15f`) e `2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 (revisão humana) - 25b5cce4` onde tratarem do mesmo trecho, em especial a nota nova proposta `ZenyHotelManager - Módulo printing` (dependências do módulo) e o Estado do M5. A nota `Módulo printing` ainda não existe no vault: é a proposta da captura da E10, que o curador cria; os itens abaixo a complementam.

### 1. `ZenyHotelManager - Módulo printing` (complementa a nota proposta pela captura da E10)

**Substitui** "`allowedDependencies`: só `shared` … A E11 acrescenta `hotel` (e `files`, H18)" por: o `printing` depende de `shared`, `hotel` e `files` (teste exato no `ModularityTest`; ARCHITECTURE §3.1), nunca escuta eventos (provado por ArchUnit no `DocumentsStageEndToEndTest`).

**Acrescenta** a seção "Documentos (M5 E11)":

- **API pública** (`PrintingApi`, um único bean: a fachada `PrintingApiService` da `application`; o `PrintJobsService` deixou de implementá-la e mantém o `enqueue` auditado `printing.job.create`): `render(DocumentRequest, DocumentFormat): RenderedDocument` e `print(DocumentRequest, printerId): UUID` (id do job; formato pelo `PrinterKind`: `A4_PDF` → PDF, `THERMAL_ESCPOS` → ESC/POS; `documentType` do job = código do template). Não confere permissão: o dono confere a dele (D2). Tipos na raiz (`PrintingDocuments.kt`): `DocumentTemplate(code, title, xhtmlTemplate, textTemplate)`, `ModuleDocumentTemplates`, `DocumentRequest(templateCode, model)`, `DocumentFormat`, `RenderedDocument`, e os DTOs `PrintDocumentRequest {printerId}` e `PrintJobAccepted {printJobId}`, reaproveitados pelas rotas dos donos.
- **Como registrar um template e imprimir** (critério de aceite da E11):
  1. No arquivo do serviço do documento, na `application` do módulo dono, declare um `object` que implementa `ModuleDocumentTemplates` (`module = "<módulo>"`) com um `DocumentTemplate("<módulo>.<documento>", título, "templates/<módulo>/<nome>.xhtml", "templates/<módulo>/<nome>.txt")`, e publique-o num `@Bean` de uma `@Configuration` no mesmo arquivo. O `DocumentTemplateCatalog` recusa a partida com código repetido, prefixo de outro módulo, código fora de `[a-z][a-z0-9]*(\.[a-z][a-z0-9-]*)+`, caminho fora de `templates/<módulo>/` ou arquivo inexistente.
  2. Escreva o `.xhtml` (XHTML bem formado, `TemplateMode.XML`) com um fragmento `th:fragment="body"`, e o `.txt` (`TemplateMode.TEXT`; linha `---` vira régua; quebra em 48 colunas automática). Use só `document.*` (o modelo) e o utilitário `fmt` (`date`, `time`, `instant`, `money`, `percent`, `cnpj`). Nada de `<style>`: use as classes do `<head>` do layout (`table.lines`, `td.amount`, `.muted`, `.total`, `h1`, `h2`). Proibidos: `th:utext`, `[( … )]`, pré-processamento (`__${`, `__*{`, `__#{`, `__@{`, `__~{` e `__` em atributo `th:*` ou em `[[…]]`) e `th:insert`/`th:replace`/`th:include` com `${`; o `DocumentTemplatesSafetyTest` varre `templates/**`.
  3. No serviço: confira a permissão do dono antes de tudo; monte o modelo só com `Map`/`List` e folhas `String`, `Number`, `Boolean`, `LocalDate`, `LocalTime`, `Instant`, `Money`, `Percent` ou `null`, até 32 níveis (outro tipo, ciclo ou profundidade maior: `IllegalArgumentException`); chame `printing.render(...)` para o PDF e `printing.print(...)` no `print`, que é `@Audited` + `@Transactional` com retrato só de ids. Devolva o código do documento junto do PDF para o nome do arquivo.
  4. Rotas no `web` do dono: `GET …/<documento>/pdf` (`200 application/pdf`, `format: binary`, `Content-Disposition: attachment; filename="<doc>-<código>.pdf"`, `Cache-Control: no-store`) e `POST …/<documento>/print` (`@Idempotent`, corpo `PrintDocumentRequest`, `202 PrintJobAccepted`). Erro sai em `application/problem+json` mesmo com `Accept: application/pdf`.
- **Layout e contexto:** `templates/printing/layout.xhtml` (só PDF) com cabeçalho (nome fantasia, razão social, CNPJ, Cadastur, inscrição municipal, endereço, logotipo) e rodapé ("Emitido em dd/MM/yyyy HH:mm" no fuso do hotel, "Página X de Y"); o corpo entra por um único `th:insert="~{${bodyTemplate} :: body}"`. Contexto só com `document`, `hotel`, `logo`, `fmt`, `issuedAt`, `title`, `bodyTemplate` (o modelo não sombreia o resto). Hotel não configurado: "Hotel", sem logotipo.
- **Limpeza do texto:** toda `String` do modelo e do perfil do hotel em NFC; `Cc` (inclusive `\n`, `ESC`, `GS`) vira espaço, `Cf` (bidi, largura zero) é removido, espaços colapsam. PDF com fontes base-14 (WinAnsi; fora dele, `?`); ESC/POS em IBM850 (`ESC t 2`; o que não cabe é decomposto e, se sobrar, `?`). O modo TEXT escapa como HTML e a fachada desfaz as entidades numa passagem só antes da codificação. Sem fonte embutida (nome em escrita não latina sai com `?`).
- **Sem recurso externo:** `HtmlPdfRenderer` faz o parse com `DocumentBuilderFactory` seguro (sem DTD, sem entidade externa, sem XInclude) e entrega o DOM ao openhtmltopdf; o resolvedor de URI só aceita `data:`; o log do openhtmltopdf passa por um `RedactedXRLogger` que não registra a carga (a URI `data:` vazava em WARN).
- **ESC/POS:** `ESC @`, `ESC t 2`, cabeçalho centralizado só com texto (sem logotipo), corpo em 48 colunas (`ESC_POS_COLUMNS`, 80 mm), rodapé, 4 avanços e corte parcial (`GS V 66 0`), composto num só lugar (`EscPosDocument`).
- **Logotipo:** lido por `FilesApi.readContent` (finalidade `hotel.logo`, dono = id do hotel) num `TransactionTemplate` `REQUIRES_NEW` + `readOnly` (`HotelLogoReader`), para a falha não marcar a transação do dono como *rollback-only*; reduzido por `DocumentLogo.prepare` (PNG/JPEG até 2 MB e 50 MP, lado maior até 400 px, saída PNG). WEBP, ilegível, apagado, objeto ausente ou falha do armazenamento: documento sem logotipo + `WARN`. Custo: uma 2ª conexão do pool durante a leitura; sem cache.
- **Bibliotecas** (D-E11-1): `io.github.openhtmltopdf:openhtmltopdf-pdfbox` 1.1.110 (fork mantido; **LGPL-2.1+**), PDFBox 3.0.8, `thymeleaf-spring6` 3.1.5 do BOM (sem o starter, sem `ViewResolver`), `pdfbox` só em teste; o PDFBox subiu o `commons-logging` de 1.3.6 para 1.4.0 no lockfile; o `unbescape` é usado direto, mas só chega como transitivo do Thymeleaf. Imagem Docker: 171,5 MB → 178,0 MB (+6,6 MB; build de 115 s para 142 s).
- **Limites conhecidos:** logotipo sem cache; regra "sem `<style>` em template de dono" só por convenção (a varredura não a impõe); quem tem a permissão do dono imprime em qualquer impressora ativa.

### 2. `ZenyHotelManager - Módulos hotel e staff`

**Complementa** a API pública do `hotel`: `HotelApi.profile(): CurrentHotelProfile?` (`hotelId` + o `HotelProfile` existente: razão social, nome fantasia, CNPJ, inscrição municipal, Cadastur, endereço, fuso, regime, `logoFileId`); `null` enquanto o hotel não está configurado; somente leitura, sem permissão. O id do hotel é o dono do vínculo do logotipo.

### 3. `ZenyHotelManager - Módulo files`

**Complementa** a API pública: `FilesApi.readContent(id, purpose, ownerEntityId): FileContent` (`FileContent(summary, content)`, `toString` sem o conteúdo) devolve o conteúdo de um anexo **comum**, não apagado, da finalidade e vinculado ao dono informados (`404 FILE_NOT_FOUND`; `422 FILE_PURPOSE_MISMATCH`; outro dono ou órfão `409 FILE_ALREADY_ATTACHED`), conferindo o SHA-256 (divergente: `IllegalStateException`). Anexo **sensível** é recusado com `IllegalArgumentException` antes de ler o objeto (mais estreito que a H18, que previa decifrar; decisão D-E11-7, revisável). Sem trilha (leitura de anexo comum). Único consumidor: o logotipo do `printing`.

### 4. `ZenyHotelManager - Módulo guests`

**Complementa** `GuestsApi.identification`: `GuestIdentification` ganhou `address: Address?` (do perfil corrente; num mesclado, do sobrevivente; anonimizado, nulo), fora do `toString`. Usado pela ficha de registro.

### 5. `ZenyHotelManager - Módulo billing (caixa, pagamentos, caução e encerramento)`

**Substitui**, no item do extrato, "o PDF é do M5 pelo `printing`" por: **Extrato em PDF e ESC/POS (M5 E11):** `GET /api/v1/folios/{id}/statement/pdf?audience=` e `POST /api/v1/folios/{id}/statement/print?audience=` (`billing.folios.read`; `audience` padrão **`GUEST`** nas duas, ao contrário do JSON, que segue `INTERNAL`; `extrato-<número>.pdf`). O corpo vem do `FolioStatementService` (no `GUEST`, nada interno: usuário, motivo, aprovação, NSU, autorização, turno, reaberturas). Trilha do `print`: `billing.statement.print`, só ids. **Porta nova** na raiz: `FolioOwnerDescriber { ownerType; describe(ownerId): FolioOwnerDescription? }` e `FolioOwnerDescription(label, guestName?, roomNumber?, arrival?, departure?)` (`toString` sem o nome); um descritor por `FolioOwnerType` (dois recusam a partida); dono sem descritor mostra só o tipo; descritor que lança derruba o extrato. O `reservations` implementa `RESERVATION`; M6 a M8 implementam `GROUP`, `EVENT` e `COMPANY`. A aresta `billing` → `printing` foi acrescentada ao `ModularityTest`.

### 6. `ZenyHotelManager - Hospedagem e recepção`

**Acrescenta** o item **Ficha de registro (M5 E11):** `GET /api/v1/reservations/{id}/registration-card/pdf` e `POST …/registration-card/print` (`frontdesk.stays.checkin` nas duas; `ficha-<código>.pdf`; trilha `frontdesk.registration-card.print`). Situações `CONFIRMED`, `IN_HOUSE`, `CHECKED_OUT`; outras `409 REGISTRATION_CARD_UNAVAILABLE`. Mostra a estadia (código, UH, chegada, saída, entrada efetiva no fuso do hotel, adultos, crianças) e, por hóspede, o nome social (ou o civil), nacionalidade e nascimento (linhas só quando há), endereço, documentos **mascarados** (`identification`), motivo de viagem e meio de transporte como códigos FNRH "(código FNRH)" e a linha de assinatura. Todos os dados do hóspede vêm do mesmo perfil corrente (`identification(id).id` antes do nome). Nunca `fnrhData`, número inteiro, raça/cor nem deficiência. Aresta `frontdesk` → `printing` no `ModularityTest`.

### 7. `ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)`

**Acrescenta** o item **Confirmação de reserva (M5 E11):** `GET /api/v1/reservations/{id}/confirmation/pdf` e `POST …/confirmation/print` (`reservations.reservations.read`; `confirmacao-<código>.pdf`; trilha `reservations.confirmation.print`). Situações `PROVISIONAL`, `CONFIRMED`, `IN_HOUSE`, `CHECKED_OUT`; `CANCELLED`/`NO_SHOW` → `409 CONFIRMATION_UNAVAILABLE`. Traz código, situação, titular (social ou civil, perfil corrente), tipo de UH, plano, datas, noites, adultos, idades das crianças, diária por noite e total, os termos de cancelamento e garantia **copiados na reserva** (RN-15) e, da `HotelApi.policy()`, horários, janela de arrumação, early/late com preço ou "não oferecido" e os dois textos (RN-11). **Acrescenta** o `ReservationFolioOwnerDescriber` (`RESERVATION`: "Reserva <código>", titular, UH alocada atual, chegada, saída). Aresta `reservations` → `printing` no `ModularityTest`.

### 8. `ZenyHotelManager - Convenções de API`

**Acrescenta** em "Atualizações por capturas": **Documentos (M5 E11):** documento gerado é subrecurso próprio do dono, `GET …/<documento>/pdf` (resposta binária `Content(mediaType = "application/pdf", schema = Schema(type = "string", format = "binary"))`, modelo `FilesController.content`) e `POST …/<documento>/print` (`@Idempotent`, `202 PrintJobAccepted`); negociação por `Accept` no mesmo caminho foi descartada. O erro sai em problem+json mesmo com `Accept: application/pdf`; `Accept: application/json` na rota do PDF devolve o PDF (sem 406). Parâmetro de query repetido é aceito como no resto da API.

### 9. `ZenyHotelManager - Testes de integração`

**Complementa** com as lições da E11:

- A máquina de desenvolvimento tem 14 GB: mais de um `./gradlew` com Testcontainers ao mesmo tempo (mais o daemon do Kotlin) esgotou a memória, o kernel matou um Java e a sessão caiu duas vezes. Rode um Gradle por vez e `./gradlew --stop` entre tarefas.
- A data operacional do banco compartilhado é avançada por outros testes: não compare datas exibidas com `currentBusinessDate()` lido depois; use o valor gravado (ex.: `checked_in_at` no fuso do hotel) ou as datas da própria reserva.
- `PdfText.kt` (`pdfText`, `pdfPageCount`, `pdfImageCount`, pelo PDFBox) em `src/test/kotlin/com/zeny/hotel/testsupport/`. Exemplos de templates de teste em `src/test/kotlin/printingexample/` e `src/test/resources/templates/printingexample/`.
- Testes que gravam o perfil do hotel devolvem o original no `finally` (e devem conferir o `.ok()` da restauração).

### 10. `ZenyHotelManager - Estado por marco` e o hub `ZenyHotelManager`

**Substitui** a linha de estado do M5 por: M5 em andamento: E01 a E08, E10, E11, E13, E14, E15 e E16 concluídas (E11 em 2026-11-12). Próxima: o gate **E12**. E09 `#bloqueada` só pela Q-12. **Revisão humana da E11 pendente** (decisões D-E11-1, 4, 7, 9, 10, 11 e 12). Revisão humana de E13 e E07 também pendente.

**Acrescenta** ao "Estado por marco": desde o M5 E11 o `printing` renderiza documentos (API de render e print, templates por dono) e existem a ficha de registro (`frontdesk`), o extrato em PDF (`billing`, com a porta `FolioOwnerDescriber`) e a confirmação de reserva (`reservations`), com `HotelApi.profile()` e `FilesApi.readContent` (nota `ZenyHotelManager - Módulo printing`, proposta pela captura da E10).

**Hub:** "Próximos passos" passa a "Executar o gate E12 do M5 pelo `claude --agent orquestrador`, depois da revisão humana da E11". Em "Perguntas abertas", acrescenta o lote E11 (D-E11-1 a 14 e as rulings da execução) como decidido pela opção recomendada, sem confirmação do usuário; a lista está em "Decisões do lote E11" no roadmap.

**Git:** o lote da E11 será integrado na `main` por merge local, logo depois desta captura; o hash do merge não estava disponível na publicação, e o push é do usuário.

## Contexto

Fechamento da etapa E11 do roadmap `roadmap-m5-recepcao-fnrh` do ZenyHotelManager, publicado pelo orquestrador de etapa por pedido do `brain-escriba`, conforme a regra do projeto de publicar `ZenyHotelManager - atualização <slug> Eyy` ao fim de cada etapa que muda algo descrito no brain.

## Origem

- Projeto: ZenyHotelManager; repositório `/home/caio/repos/ZenyHotelManager`.
- Worktree: `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m5-recepcao-fnrh`; branch `roadmap/m5-recepcao-fnrh`.
- Commits da etapa: `7aa2527..c431a16` (fechamento `c431a16`). O gate completo rodou em `933b3ee`: BUILD SUCCESSFUL, 3220 testes, 0 falhas.
- Plano: `docs/superpowers/plans/2026-11-11-m5-recepcao-fnrh-e11.md` (D-E11-1 a 14).
- Roadmap: `docs/roadmaps/roadmap-m5-recepcao-fnrh.md` (handoff da E11 e "Decisões do lote E11").
- Documentação: `docs/ARCHITECTURE.md` §3.1, §7 e §14; `README.md`, seção "API" ("Documentos impressos (M5 E11)").
- Rascunho do orquestrador: `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m5-recepcao-fnrh/.superpowers/sdd/2026-11-11-m5-recepcao-fnrh-e11/captura-e11.md`.
- Data: 2026-11-12.

## Por que registrar

Alimentar a consolidação do curador nas notas de tema do projeto: a E11 muda a API do `printing`, do `hotel`, do `files`, do `guests`, do `billing`, do `frontdesk` e do `reservations`, as convenções de API, as lições de teste e o Estado do M5.

## Limitações e incertezas

- As decisões D-E11-1 a 14 foram tomadas pela opção recomendada, sem confirmação do usuário; a revisão humana da E11 está pendente e pode revertê-las (em especial D-E11-1, 4, 7, 9, 10, 11 e 12).
- O hash do merge na `main` não estava disponível na publicação (o merge local é feito logo depois); a referência de código são os commits `7aa2527..c431a16` na branch.
- Os caminhos do repositório, do worktree e do rascunho são locais; o worktree e o rascunho (`.superpowers/sdd/`) podem desaparecer após o merge. O rascunho não foi copiado como anexo; o conteúdo dele está integralmente acima.
- O texto vem do rascunho do orquestrador; o escriba não conferiu o código, o roadmap nem os documentos do repositório, só a existência das notas do vault e das capturas citadas.
- A nota `ZenyHotelManager - Módulo printing` ainda não existe no vault (é proposta pela captura da E10).

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Estado por marco]]
- [[ZenyHotelManager - Módulos hotel e staff]]
- [[ZenyHotelManager - Módulo files]]
- [[ZenyHotelManager - Módulo guests]]
- [[ZenyHotelManager - Módulo billing (caixa, pagamentos, caução e encerramento)]]
- [[ZenyHotelManager - Hospedagem e recepção]]
- [[ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)]]
- [[ZenyHotelManager - Convenções de API]]
- [[ZenyHotelManager - Testes de integração]]
- [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 - 4dd12e66]]
- [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 (revisão humana) - 25b5cce4]]
