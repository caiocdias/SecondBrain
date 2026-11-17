---
type: log
created: 2026-11-16
---
# Processamento da Inbox — 2026-11-16 21:51

Estado do lote: concluído

## Capturas

### b6c7bc32-8f7c-4952-85c0-7e210f2b7f81
- Captura: [[2026-11-15 - ZenyHotelManager - pedido do front PF-02 Histórico do desfazer check-in com a aprovação do superior - b6c7bc32]] (preservada em 90 Archive/Inbox/)
- Ação: integrada como pedido aberto do front desktop ao servidor, sem decisão do servidor, na forma do PF-01: subseção nova "Pedido do front PF-02" em Hospedagem e recepção (motivo, operação desejada, contorno, etapa que espera, commit fixado, prioridade, limitação), remissão no item "Desfazer" do texto literal e bullet de Perguntas abertas do hub (fundido com o do PF-01).
- Notas criadas: nenhuma
- Notas enriquecidas: [[ZenyHotelManager]], [[ZenyHotelManager - Hospedagem e recepção]]
- Normalizações: status alterado para archived ao mover para 90 Archive/Inbox/ (arquivo não rastreado pelo git: movido com `mv -n`)
- Conferência: por `git` (só leitura), na `main` (`5e06f16`) `StayTransitions.undoCheckIn` chama `history.record(ReservationHistoryKind.UNDO_CHECK_IN, …, null, now)`; o arquivo é igual na ponta da branch do M6 (`adba5e3`) e não foi tocado desde o `57eb5fa`; nenhum documento do servidor cita "PF-01" ou "PF-02". A assinatura de `history.record` e os documentos do front não foram lidos.
- Pendências: decisão do servidor sobre o PF-02, a cargo do usuário e do `arquiteto`.
- Estado: concluída

### a68d398b-2037-4b20-af27-8039b163ae0e
- Captura: [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E18 - a68d398b]] (preservada em 90 Archive/Inbox/)
- Ação: integrada, com a correção c383eb2b aplicada por cima (vale sobre ela na frase da última migração) e antes da dd5e01e3 (por `git`, a E18 fecha em `2471691`, 2026-11-15 21:58, e a E01 começa depois dele). Item 1, "Decisões para o usuário", item 9 e os menores de `src/main` do item 8 em Estado por marco (subseção nova "M6 E18", marcas de substituição em "M6 E17" e "M6 E18 no roadmap", lista consolidada); item 2 em Convenções de API (subseção nova "Cursor e datas estritos: comportamento atual"); item 3 em Auditoria (subseção nova "Rollback em toda exceção: comportamento atual"); item 4 em Eventos e jobs (subseção nova "Log das exceções dos jobs: `JobErrorLoggingTaskScheduler`"); item 5 em Docker, observabilidade e CI (subseção nova "Mensagem do JDBC fora do log dos jobs"; o achado do MDC da E16 não foi duplicado); item 6 em Schemas (subseção nova "Piso efetivo do driver"); item 7 e os menores de teste do item 8 em Testes de integração (subseção nova "M6 E18"); saída da validação local do cursor e do `rollbackFor` local em Módulo endofday; Estado e Próximos passos do hub, já na forma que a dd5e01e3 deixa. As três subseções "ainda não implementada" (Convenções de API, Auditoria, Eventos e jobs) e a remissão de Docker foram **mantidas com marca do curador** e título trocado para "implementada em 2026-11-15", em vez de apagadas: guardam a lista das 15 consultas e as decisões H13; remissões curtas foram postas nos marcadores do texto literal ("Paginação", "Contrato", "Transação", jobs, "Valores do banco fora do log").
- Notas criadas: nenhuma
- Notas enriquecidas: [[ZenyHotelManager]], [[ZenyHotelManager - Estado por marco]], [[ZenyHotelManager - Convenções de API]], [[ZenyHotelManager - Auditoria]], [[ZenyHotelManager - Eventos e jobs]], [[ZenyHotelManager - Docker, observabilidade e CI]], [[ZenyHotelManager - Schemas, migrações e views de relatório]], [[ZenyHotelManager - Testes de integração]], [[ZenyHotelManager - Módulo endofday]]
- Normalizações: status alterado para archived ao mover para 90 Archive/Inbox/ (`mv -n`); títulos de quatro subseções trocados de "ainda não implementada" para "implementada em 2026-11-15" (nenhum link apontava para esses títulos).
- Conferência: por `git` (só leitura): de `a5b0902` (2026-11-15 12:36) a `ed0f5ab` (20:43) são 24 commits, com todos os hashes citados pela captura e o `5d0dd27`; fechamento `2471691` (21:58), em que o roadmap dá a E18 `#concluida`. No `ed0f5ab`: `StorableRange.kt` com os quatro extremos da captura, `StrictDateTimeJson.kt`, `ScheduledJobErrors.kt`, `KernelProbes.kt`, `rollbackOn = RollbackOn.ALL_EXCEPTIONS` em `AuditAspect.kt`, `spring.task.execution.mode: force` e o logger do ShedLock em `OFF` no `application.yaml`. A `main` local segue em `5e06f16`, igual à `origin/main`: a E18 só existe na branch `roadmap/m6-operacao-fechamento`, como a captura diz. Registrado como notas do curador. Números do gate, das revisões, do oasdiff e do `osv-scanner`, inventário das exceções checked, corpo das regras e dos testes não foram conferidos.
- Pendências: decisões (a) a (f) da E18 sem confirmação do usuário, acrescentadas à lista consolidada; etapa de manutenção sugerida ao `arquiteto` (item 9), registrada em Estado por marco e resumida em Próximos passos do hub; **aviso ao usuário**: o front desktop deve saber que `""` em data ou instante opcional agora dá `400 INVALID_FORMAT` (registrado em Próximos passos do hub, Convenções de API e Estado por marco).
- Estado: concluída

### c383eb2b-baa6-47c2-9eb7-545ebe5dfb34
- Captura: [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E18 (correção) - c383eb2b]] (preservada em 90 Archive/Inbox/)
- Ação: integrada sobre a a68d398b: a frase "a última migração continua `printing/V2026_11_11_1001…`" do item 6 não entrou como fato; a subseção "Piso efetivo do driver" de Schemas diz que a E18 não tem migração e que a última era `V2026_11_14_1000`, e a subseção "M6 E18" de Estado por marco a cita na origem.
- Notas criadas: nenhuma
- Notas enriquecidas: [[ZenyHotelManager - Schemas, migrações e views de relatório]], [[ZenyHotelManager - Estado por marco]]
- Normalizações: status alterado para archived ao mover para 90 Archive/Inbox/ (`mv -n`)
- Conferência: por `git` (só leitura), no `0d3eba1` a migração anterior às do `housekeeping` é `fnrh/V2026_11_14_1000__add_fnrh_no_show.sql`, o que casa com a correção.
- Pendências: nenhuma.
- Estado: concluída

### dd5e01e3-3041-431b-81f8-3b801eec3fff
- Captura: [[2026-11-16 - ZenyHotelManager - atualização m6-operacao-fechamento E01 - dd5e01e3]] (preservada em 90 Archive/Inbox/)
- Ação: integrada depois da E18. Item 1 na nota nova Módulo housekeeping; item 2 em Módulo checklists (seção "Atualizações por capturas" criada, remissão no marcador "API pública"); item 3 em Convenções de API (subseção nova do NUL e da coerção do Jackson, remissão no marcador "Paginação"); item 4 em Schemas (subseção nova "Schema `housekeeping`", marca na subseção do no-show da FNRH); item 5 em Segurança (subseção nova "Permissões do `housekeeping`"); item 6 em Estado por marco (subseção nova "M6 E01", lista consolidada) e no hub (Estado, linha do `housekeeping` no índice "Módulos", Próximos passos).
- Notas criadas: [[ZenyHotelManager - Módulo housekeeping]]
- Notas enriquecidas: [[ZenyHotelManager]], [[ZenyHotelManager - Estado por marco]], [[ZenyHotelManager - Módulo checklists]], [[ZenyHotelManager - Convenções de API]], [[ZenyHotelManager - Schemas, migrações e views de relatório]], [[ZenyHotelManager - Segurança, autenticação e autorização]]
- Normalizações: status alterado para archived ao mover para 90 Archive/Inbox/ (`mv -n`)
- Conferência: por `git` (só leitura): de `2471691` (exclusivo) a `0d3eba1` (2026-11-16 11:55) são 19 commits; fechamento `e2a8e65` (12:25), em que o roadmap dá a E01 `#concluida`. No `0d3eba1`: os onze arquivos de `housekeeping/`, as duas migrações, `allowedDependencies = ["shared", "hotel", "rooms", "checklists"]`, os 18 códigos de erro, as duas permissões, a carga inicial dos seis tipos, os arquivos de teste citados, `ChecklistsApi.template(id)` com `ChecklistTemplateInfo` e a constante `NUL` em `Pagination.kt` conferem com a captura. A captura pedia checar duplicação nos itens 3 a 5: nenhuma das três notas tratava de NUL no cursor, do schema `housekeeping` ou das permissões dele. Registrado como notas do curador. Corpo dos casos de uso, travas, testes, coerção do Jackson e números do gate não foram conferidos.
- Pendências: decisões D1, D5 e D8, o limite de 200 créditos e a reativação que mantém o vencimento, sem confirmação do usuário, acrescentadas à lista consolidada; pauta do `arquiteto` (D8, dois testes endurecíveis, coerção do Jackson) em Estado por marco. Na ponta da branch (`adba5e3`), a **M6 E02 já está `#em-andamento`** ("lote parado na onda de correção final"), com `reservations` nas dependências do `housekeeping`, migrações `V2026_11_16_1000` e `V2026_11_16_1001` e permissões de tarefas, ainda sem captura; registrado como nota do curador em Módulo housekeeping, Schemas, Segurança e Estado por marco, sem mudar o Estado do hub.
- Estado: concluída

### 16d5b400-b2e5-490e-b063-b61b40c14257
- Captura: [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]] (mantida na Inbox)
- Ação: mantida na Inbox
- Notas criadas: nenhuma
- Notas enriquecidas: nenhuma
- Pendências: mesma dos lotes [[2026-11-10 - Processamento da Inbox - 1705]] e [[2026-11-15 - Processamento da Inbox - 1907]]: o projeto ZenyHotelManager-DesktopFront não tem hub, e a captura-índice do registro pela skill `development-roadmap` (que vale como pedido de criação da nota de projeto) ainda não existe. Conferido em 2026-11-16: o repositório do front não tem `.claude/settings.json` com o hook, e o `load-brain.py` ainda casa as capturas pendentes por substring (a troca por prefixo altera uma skill do vault e aguarda pedido explícito do usuário).
- Estado: mantida na Inbox

### 677b277a-44a4-4da4-8214-4dfca2edc865
- Captura: [[2026-11-13 - ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão - 677b277a]] (mantida na Inbox)
- Ação: mantida na Inbox
- Notas criadas: nenhuma
- Notas enriquecidas: nenhuma
- Pendências: destino indicado pela própria captura é o hub do ZenyHotelManager-DesktopFront, que não existe; integrar junto com a 16d5b400.
- Estado: mantida na Inbox

### 5bba7217-6f3f-460d-8b80-ace44d5b8683
- Captura: [[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]] (mantida na Inbox)
- Ação: mantida na Inbox
- Notas criadas: nenhuma
- Notas enriquecidas: nenhuma
- Pendências: destino indicado pela própria captura é o hub do ZenyHotelManager-DesktopFront, que não existe; integrar junto com a 16d5b400 e a 677b277a. Do lado do servidor, o que ela cita (regra do `oneOf`, PF-01, PF-02, M6 E11 a E17) já está nas notas do ZenyHotelManager.
- Estado: mantida na Inbox

### 0cc1844e-038a-4163-83d7-abbb4b4c6ffd
- Captura: [[2026-11-16 - ZenyHotelManager-DesktopFront - ADR 0011 processo acelerado até a demo - 0cc1844e]] (mantida na Inbox)
- Ação: mantida na Inbox
- Notas criadas: nenhuma
- Notas enriquecidas: nenhuma
- Pendências: decisão de processo do ZenyHotelManager-DesktopFront (exceção local ao fluxo das souls, com dívida de revisão sobre `a300a23..HEAD`); o destino natural é o hub do front, que não existe. Não foi promovida a nota de conhecimento própria: é uma decisão específica do projeto, e a comparação com [[ZenyProjectHandler - Execução acelerada do roadmap de leitura vetorial]] vem rotulada como interpretação do agente. Integrar junto com as outras três.
- Estado: mantida na Inbox

## Observações

- Nenhum lote anterior em andamento ou interrompido. Oito capturas pendentes, sem `capture_id` duplicado; nenhum deles aparecia em `90 Archive/Inbox/` nem em seções de proveniência (16d5b400 e 677b277a apareciam só nos logs de 2026-11-10 e 2026-11-15, como mantidas na Inbox). Nenhuma captura mudou nem chegou durante o lote.
- As quatro capturas do servidor foram integradas em sequência, na ordem real conferida por `git` (só leitura): PF-02, E18 com a correção, E01.
- Verificação final: quatro capturas em `90 Archive/Inbox/` com `status: archived`; os quatro `capture_id` aparecem nas seções de proveniência das notas de destino e neste log; YAML válido e wikilinks resolvidos nos 14 arquivos alterados ou criados.
- Hub [[ZenyHotelManager]] com 14.786 caracteres (13.876 no início do lote), acima da meta de ~8.000 de [[99 System/AI/processing]]: cresceu 910, dos quais cerca de 560 são as três linhas de proveniência novas e o resto, a linha do `housekeeping` no índice, o aviso ao front e o PF-02. Nada foi retirado do hub neste lote. Reduzir mais depende de decidir a forma da proveniência no hub (mudança de regra, do usuário), pendência já registrada no lote de 2026-11-15.
- As quatro capturas do ZenyHotelManager-DesktopFront seguem na Inbox pela terceira vez (a primeira é de 2026-11-10). Decisão do usuário: registrar o projeto pela skill `development-roadmap` (caminho previsto na 16d5b400) ou pedir explicitamente ao curador a criação do hub a partir dessas quatro capturas.
