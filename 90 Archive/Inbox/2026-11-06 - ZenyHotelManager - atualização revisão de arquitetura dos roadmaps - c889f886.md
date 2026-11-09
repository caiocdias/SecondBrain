---
type: capture
status: archived
created: 2026-11-06
capture_id: c889f886-0719-4f28-984e-f2ef23ed9520
---
# ZenyHotelManager - atualização revisão de arquitetura dos roadmaps

## Conteúdo capturado

Resumo do agente (publicado a pedido da sessão `claude --agent arquiteto`, agente externo no repositório `/home/caio/repos/ZenyHotelManager`): em 2026-11-06 os roadmaps M5 a M10 foram revistos pela lente do arquiteto e alinhados ao modelo atual de execução. **Nenhum código mudou e as alterações ainda não têm commit.** O texto abaixo diz, para cada nota afetada, o que muda e se substitui ou complementa.

Complementa e em parte substitui a captura pendente [[2026-11-05 - ZenyHotelManager - atualização m5-recepcao-fnrh E07 - 9f02405c]] (capture_id: 9f02405c-a73b-44f0-8f8c-5fb75860aa05). Substitui nela: "Próximas elegíveis" e a localização da E07 (item 1), o "Limite conhecido" da credencial (item 2), a recomendação sobre a descrição do gênero (item 5) e as decisões (e) e (i) (item 6). O restante dela continua valendo e continua pendente de integração.

Como ler a autoria: **decisão do usuário** é o que a spec marca como `[usuário]`, decidido na entrevista daquela sessão; **decisão do arquiteto** é o que ela marca como `[arquiteto]` e diz ser revisável. A autoria segue a spec; não presenciei a entrevista.

### 1. Hub `ZenyHotelManager`: "Estado", "Próximos passos" e "Perguntas abertas"

**"Estado": substitui a linha do M5 e a linha do Git; complementa as demais.**

- **M5, 16 etapas (novas E15 e E16).** E01 a E07, E13 e E14 concluídas. Próximas elegíveis, na ordem do índice: **E15, depois E08, E16 e E10**. A E08 depende da E15, por isso vem depois dela. A E09 segue `#bloqueada` (Q-12) e passa a depender de E08 e E16. O gate E12 passa a depender também da E16. A E08 passa a ter revisão humana, por fixar o padrão de envio que M7 e M8 repetem.
- **M6, 14 etapas (novas E13 e E14), começando pelo fechamento:** E10 (motor) e E11 (etapas financeiras e operacionais) vêm antes da governança, e a E11 deixa de depender de E02 e E09. A E02 passa a depender da E11. O snapshot e os PDFs saem para a E13, e o no-show na FNRH para a E14. O gate E12 passa a depender de E06, E13 e E14.
- **M8, 18 etapas (novas E14 a E18):** quatro trilhas (restaurante E01 a E06, distribuição E07 a E09, prontidão para operação real E10 e E14 a E18, implantação E11), mais o gate E13. A E11 passa a depender de E10, E14, E15 e E18. O gate E13 passa a depender de E09, E11, E12, E16 e E17 e exige a homologação real da FNRH (M5 E09). A E10 passa a ter revisão humana.
- **M9 e M10** trazem a restrição de sistema em produção: migração só aditiva ou em duas fases, backup e procedimento de implantação antes de cada versão.
- **Fim do lote (decisão do usuário, 2026-11-06, que substitui a regra de 2026-10-22):** a execução continua na branch `roadmap/<slug>`; no fim do lote, com o gate verde, o orquestrador faz o **merge local na `main`** e deixa pronto o `git push origin main`. **Push e deploy são sempre do usuário.** Fora do roadmap, commit só a pedido.
- **M0 a M4 são registro histórico (decisão do usuário):** concluídos, não se executam e continuam acusando erro de formato no verificador.
- **Quem faz o quê:** `claude --agent arquiteto` desenha e revê (spec, ARCHITECTURE, roadmaps) e não escreve código nem plano; `claude --agent orquestrador` escreve o plano de cada etapa, submete-o ao `revisor-arquitetura` e executa.
- **Protocolo dos roadmaps** alinhado ao template de 2026-11-05: ondas paralelas, testador por risco e decisões pela opção recomendada, salvo as de arquitetura; etapa `#bloqueada` não para o lote.
- Referência de documentos: a seção "Objetivo" do hub cita "decisões D1–D17"; passa a **D1–D19**. A referência da revisão é `docs/superpowers/specs/2026-11-06-revisao-arquitetura-roadmaps-design.md`.
- Localização do código (fato, conferido com `git`): `HEAD` da `main` local em `ca9f9e2`, com E14 e E07; a referência local `origin/main` está em `15bbcdb` (sem `fetch` nesta sessão); a branch `roadmap/m5-recepcao-fnrh` não existe mais. Substitui "A E07 está na branch" da captura da E07.

Acréscimo meu ao pedido: a mesma linha do M5 vale para [[ZenyHotelManager - Estado por marco]], que recebeu a linha do M5 nas capturas anteriores.

**"Próximos passos": complementa.**

- Commit das alterações desta revisão, só a pedido do usuário (item "Origem" lista os arquivos).
- Executar E15, E08, E16 e E10 do M5 pelo `claude --agent orquestrador`.
- M6 começa pelas E10 e E11. A nota sobre a chave do check-out continua valendo.
- A homologação da FNRH (M5 E09) continua fora do gate do M5 e passa a ser cobrada pelo gate de inauguração (M8 E13).
- A regra 2 de `docs/roadmaps/README.md` continua: sincronizar cada roadmap com o código antes do primeiro lote do marco.

**"Perguntas abertas": substitui e complementa.**

- **Resolvidas pelo usuário, saem da lista:**
  - E07 (e), descrição de gênero: etapa própria antes do envio, M5 E15 (R5).
  - E07 (i), limpar a credencial do Serpro: antes de existir credencial real, M5 E16, pré-requisito da E09 (R6). Antes a recomendação era "antes do M8".
- **Continuam sem confirmação do usuário:** as decisões dos lotes M5 E04 a E06, E13, E14 e E07 (as demais, (a) a (d), (f), (g), (h) e (j)), tomadas pela opção recomendada, e a **revisão humana de E13 e E07**. O gate M8 E13 passa a exigir que tenham sido revistas e concluídas.
- **Nova, em aberto:** a oferta de dividir o M8 em dois arquivos. Ele ficou com 18 etapas, acima da referência de cerca de 12 da skill; as etapas ficam em blocos no índice e a divisão foi oferecida ao usuário, não aplicada.
- **Revisáveis:** as decisões do arquiteto (R7 a R13 e R16, abaixo) não passaram pela entrevista.
- **Q-07 (prazos de retenção):** segue no padrão da SPEC (30 dias e 5 anos) até o usuário confirmar; a revisão humana da M8 E16 cobre o prazo.
- **Fornecedores e hospedagem** (Q-05, Q-06, Q-02, Q-03, Q-13) seguem como decisões do usuário, e as etapas afetadas, `#bloqueada`.
- O hub diz que o risco do `opentelemetry-api` 1.62.0 tem prazo "antes do M8". A captura da E14 diz "antes da operação real (M8)", e agora a etapa dona é a M8 E17. Sugiro alinhar o hub a isso.

### 2. [[ZenyHotelManager - Arquitetura e estrutura de módulos]]: complementa

Citação literal de `docs/ARCHITECTURE.md` §2, linhas novas da tabela de decisões (árvore de trabalho, sem commit):

> | D18 | Venda do PDV | A comanda paga no ponto de venda abre uma **conta `WALK_IN`** no `billing`, com lançamentos e pagamentos existentes (usuário, 2026-11-06) | O dinheiro entra no turno de caixa, na taxa de serviço e em `billing.report_postings` sem caminho novo; o A&B do snapshot tem uma só fonte | Livro financeiro próprio no `pos` (duplica taxa e conferência de caixa e cria duas fontes de receita) |

> | D19 | Alertas | **Prometheus e Alertmanager** no compose, sem porta pública, com destino de entrega configurável (usuário, 2026-11-06) | As regras já existem, e o caminho é o mesmo em nuvem ou no hotel; o monitor externo do host fica no checklist de inauguração | Monitor externo gerenciado (fornecedor novo e, no hotel, endpoint exposto); decidir só com a Q-06 (alertas sem destinatário até lá) |

- D18 e D19 são **decisões do usuário** (R14 e R15). Ambas ainda são desenho: a D18 entra na M8 E04 e a D19, na M8 E18.
- A regra por camadas da §3.1 ganhou uma frase, sem decisão R própria na spec. Citação literal: "as arestas de mesma camada já na tabela (como `billing` → `payments`, `reservations` → `rates` e `endofday` → `reporting`) são exceções registradas, e uma nova exige decisão." Complementa o item "Dependências entre módulos seguem a regra por camadas" da nota.

### 3. [[ZenyHotelManager - Módulo guests]]: substitui uma frase e complementa

- **Substitui** a frase "A anonimização automática por prazo e o expurgo dos dados sensíveis da FNRH são do M10." por: a anonimização automática por prazo e a retenção da trilha são da M10 E13; o **expurgo dos dados sensíveis da FNRH é da M8 E16**, exigido no gate de inauguração (decisão do usuário, R4). Ainda não existe no código.
- **Complementa com a M8 E16:**
  - Expurgo de raça/cor e deficiência no prazo da Q-07 (padrão: 30 dias após o check-out, configurável), por job semanal. Quem guarda o dado é o `guests` (`sensitive_data`); o `fnrh` não guarda (hipótese M10 H6 resolvida na spec).
  - O job fica no `guests`, com uma porta implementada por `reservations` (data do último check-out) e outra por `fnrh` (submissão pendente); o `guests` não depende de nenhum dos dois.
  - Hóspede hospedado, ou com submissão a enviar ou em nova tentativa, não é expurgado. **Decisão do arquiteto (R16):** submissão `FAILED` ou `INVALID` segura o expurgo só até um teto configurável; passado o teto, o dado sai e o caso fica nas pendências da FNRH.
  - Modo simulação, trilha só com contagens, métrica e alerta do expurgo retido. Expurgo é irreversível: a primeira execução real só depois da simulação revisada pelo usuário.
  - Ficam para decidir no plano, com registro: hóspede com reserva futura, e se a descrição de gênero segue o mesmo prazo.
- **Complementa com a M5 E15 (decisão do usuário, R5):**
  - Descrição de gênero no perfil e no `FnrhGuestData`, opcional no cadastro e recusada quando o gênero não é `OTHER`. Ainda não existe no código.
  - Hóspede `OTHER` com descrição passa na validação local da FNRH; sem ela, continua `person.genderDescription`/`REQUIRED`.
  - A descrição não aparece em log, trilha, `toString`, notificação nem view; entra na exportação do titular e sai na anonimização.
  - O plano decide, com registro, se o valor fica cifrado.
  - Substitui a recomendação pendente do item 5 da captura da E07. O caso do menor só com RG (E07 f) não muda.

### 4. [[ZenyHotelManager - Docker, observabilidade e CI]] e [[ZenyHotelManager - Ambiente, banco, chaves e build]]

Todas as etapas abaixo estão `#pendente`. As notas descrevem o estado atual do código, que continua valendo até cada etapa ser executada; muda o dono e o critério das pendências.

| Etapa | Entrega | Nota e parte afetada | Efeito | Autoria |
|---|---|---|---|---|
| M8 E14 | Migrações num container de uso único; `api` sem `ZENY_DB_MIGRATION_*` e sem Flyway no `prod`; o dono dos schemas deixa de ser o superusuário do container onde o modelo permitir | Ambiente: "Dívida para o M8 (E11)". Docker: lista de variáveis da `api` | **Substitui** a referência à E11 pela E14. A dívida não depende da Q-06. | Arquiteto (R9); a dívida em si é decisão do usuário de 2026-10-14 |
| M8 E15 | Job de re-cifragem para cada valor cifrado; teste que falha se um uso do cifrador não tiver job nem exceção registrada; procedimento em `docs/operacao/` | Ambiente: "Chaves de cifragem", passo 3 ("pendência do M8 (E11)") | **Substitui** a referência pela E15 e **complementa** a lista: além dos valores citados na nota, `guests.guest.dietary_restrictions`, `fnrh.settings`, `fnrh.requester`, o conteúdo de impressão da M5 E10 e as credenciais de M7 e M8 | Arquiteto (R10) |
| M8 E17 | `opentelemetry-api` ≥ 1.67.0 no `productionRuntimeClasspath`, pelo Boot ou por restrição; 0 Critical e 0 High no scanner, salvo risco aceito; checksums e `osv-scanner` na CI ligados ou recusados com registro | Ambiente: resíduos da E14. Docker: passos da CI | **Complementa:** dá etapa dona às decisões E14 (a), E13 (c) e (d), que não tinham uma | Arquiteto (R10) |
| M8 E18 | Serviços `prometheus` e `alertmanager` no compose, sem porta pública; destino por variável, obrigatório no profile de produção; alerta entregue a um receptor de teste | Docker: "Métricas", regras em `docker/prometheus/alerts.yaml` | **Complementa:** hoje o compose não sobe coletor, e as regras não têm quem as avalie | Usuário (R15, D19) |

Também **complementa** a nota Docker:

- Serviço `backup` (M8 E10): a criar, pois hoje é só um comentário em `docker/compose.yaml`. A E10 ganhou critério de restauração utilizável (valor cifrado lido, anexos baixados do espelho, local das chaves fora do servidor) e revisão humana.
- M8 E11: `idle_in_transaction_session_timeout` definido e logs de acesso sem query string, com teste; um alerta de teste chega ao destino real.
- "Health" na ARCHITECTURE §16: liveness e readiness, com a saúde de cada integração por endpoint de status e métricas, sem `HealthIndicator`. Coerente com o que a nota já descreve do actuator.

A ARCHITECTURE §8.3 lista os valores sem job de forma mais curta que a M8 E15 (não cita `dietary_restrictions` nem `fnrh.requester`). A etapa manda obter a lista completa na execução.

### 5. [[ZenyHotelManager - Eventos e jobs]] e a futura `ZenyHotelManager - Módulo fnrh`: complementa

**Decisão do arquiteto (R8):** o padrão de integração passa a ser descrito pelo que o M5 E07 provou, e **não existe mecanismo genérico de falha**. Os roadmaps supunham um; a hipótese M7 H2 foi conferida como falsa no código: o M5 usa `NotificationsApi.notify` direto, `GET /fnrh/status` e `MeterBinder`, sem `HealthIndicator`. A extração para `shared` fica para a M7 E01 decidir, com a segunda integração à frente.

Citação literal de `docs/ARCHITECTURE.md` §12 (árvore de trabalho, sem commit):

> Regras que a FNRH (M5 E07) provou e que valem para toda integração:
>
> - **Resultado incerto:** timeout de leitura numa escrita não diz se o provedor gravou. Nunca se repete às cegas: reenvio só com a mesma referência idempotente do provedor ou depois de conciliar pela consulta. A conciliação ambígua falha fechado.
> - **Registro de integração** em tabela *append-only* sem texto livre do provedor, porque ela não admite expurgo; a mensagem saneada vai só para o log e para a exceção, sem causa encadeada.
> - **Credencial** cifrada, nunca na trilha (nem o usuário), nunca devolvida na API e removível por uma ação com trilha. O administrador escolhe o ambiente, as URLs ficam em propriedade, e trocar de ambiente pede a credencial de novo.
> - **Falha** alerta por chamada direta a `notifications`, com o tipo `notifications.integration-failure` e sem dado pessoal. A readiness nunca depende de provedor externo.

Na nota `Eventos e jobs`, complementa também a lista de jobs: a tabela da ARCHITECTURE §13 troca "Retenção LGPD (anonimização e expurgo)" por "Expurgo dos dados sensíveis da FNRH (M8 E16)" e "Anonimização de perfis por prazo (M10 E13)", ambos semanais. Nenhum deles existe ainda.

Na futura `Módulo fnrh`, complementa o texto proposto no item 2 da captura da E07:

- **Substitui o "Limite conhecido" da credencial:** continua verdadeiro no código de hoje, mas passa a ter etapa, a M5 E16 (decisão do usuário, R6). Ação com trilha, `If-Match` e `fnrh.settings.manage`, sem `DELETE`, que apaga usuário, senha e CPF padrão e desliga a integração; religar sem nova credencial dá `422 FNRH_SETTINGS_INCOMPLETE`.
- **M5 E15:** o mapeador passa a levar a descrição de gênero.
- **M5 E08:** `UNKNOWN_OUTCOME` concilia antes de repetir, e a escolha para o `registerPerson` fica no handoff. A SPEC §8.2.17 passa a descrever a porta real da E07. O nome previsto da view é `fnrh.report_submissions`, não `report_pending_submissions`.
- **No-show:** vai pela M6 E14, com operação nova na porta. O gate M8 E13 pede o no-show executado na homologação ou registrado como risco aceito pelo usuário.

### Decisões da revisão

Texto literal de `docs/superpowers/specs/2026-11-06-revisao-arquitetura-roadmaps-design.md`, seção "Decisões", reagrupado por autoria.

**Decisões do usuário**

| # | Decisão | Alternativas descartadas |
|---|---|---|
| R1 | Manter os IDs e revisar o conteúdo: protocolo novo, hipóteses conferidas no código, dependências reordenadas e etapas novas com ID novo. | Só o protocolo (não aplica a lente); reescrever do zero com IDs novos (quebra as referências cruzadas e perde as armadilhas anotadas). |
| R2 | M0 a M4 ficam como registro histórico: concluídos, não se executam e continuam acusando erro de formato no verificador. | Migrar 1,5 MB de documentos sem efeito em execução futura. |
| R3 | No fim do lote, merge local na `main` com gate verde; o push continua com o usuário. `CLAUDE.md` e `docs/roadmaps/README.md` alinhados. | Reservar o merge ao usuário, o que exigiria instrução própria em cada prompt. |
| R4 | Expurgo dos dados sensíveis da FNRH (RN-19, Q-07) antes da inauguração: M8 E16, exigido no gate; a SPEC §9 passa a dizer isso. Anonimização de perfis e retenção da trilha seguem no M10 E13. | Manter tudo na Fase 4, com o hotel retendo dado sensível além do prazo por todo o intervalo M8–M10; expurgo manual, para o qual não há caminho hoje. |
| R5 | Descrição de gênero do hóspede em etapa própria antes do envio: M5 E15, dependência da E08. Resolve a decisão E07 (e). | Embutir na E08, já a mais carregada do marco; aceitar a limitação, o que força falsear o dado para cumprir a obrigação de registro. |
| R6 | Limpar credencial de integração antes de existir credencial real: M5 E16, pré-requisito da homologação E09; a regra vale para M7 e M8 desde a primeira linha. Resolve a decisão E07 (i). | Deixar para a prontidão do M8, com as credenciais reais de homologação entrando sem caminho de remoção. |
| R14 | A comanda paga abre uma conta `WALK_IN` no `billing` (ARCHITECTURE D18, M8 E04). | Livro financeiro próprio no `pos`, que duplica taxa e conferência de caixa e cria duas fontes de receita. |
| R15 | Prometheus e Alertmanager no compose entregam os alertas (ARCHITECTURE D19, M8 E18). | Monitor externo gerenciado; decidir só com a Q-06, com alertas sem destinatário até lá. |

**Decisões do arquiteto (revisáveis)**

| # | Decisão | Alternativas descartadas |
|---|---|---|
| R7 | M6 começa pelo fechamento: E10 e E11 antes da governança, com a E11 sem depender de E02 nem de E09. O snapshot e os PDFs saem para a E13, e o no-show na FNRH para a E14. | Manter a ordem original, com o único caminho que grava dinheiro imutável (RN-03) e faz a data andar no fim do marco; manter a E11 única, com três objetivos independentes. |
| R8 | Padrão de integração descrito pelo que o M5 E07 provou: resultado incerto, log sem texto livre, credencial fora da trilha, ambiente em vez de URL livre e status e métricas sem `HealthIndicator`. Falha alerta por chamada direta a `notifications`; o "mecanismo genérico de falha" que os roadmaps supunham não existe. ARCHITECTURE §12 e §16 corrigidas. | Criar o mecanismo genérico antes da segunda integração, sem evidência de que seja necessário. A extração para `shared` fica para a M7 E01 decidir, com a segunda integração à frente. |
| R9 | Migrações fora da `api` saem da M8 E11, bloqueada pela Q-06, para a M8 E14: a dívida não depende de nuvem ou hotel. | Deixar a dívida de segurança presa a uma decisão de hospedagem que não a afeta. |
| R10 | Pendências "antes da operação real" viram etapas com critério: re-cifragem (M8 E15) e cadeia de dependências (M8 E17), ambas exigidas no gate. | Mantê-las como notas: a re-cifragem constava como "decidir se entra", e o prazo do `opentelemetry-api` não tinha etapa dona. |
| R11 | O gate de inauguração (M8 E13) passa a exigir a homologação real da FNRH (M5 E09). Ela ficou fora do gate do M5 por exceção, e nenhum gate posterior a cobrava. | Só o checklist de inauguração, que não é critério de aceite. |
| R12 | M9 e M10 ganham a restrição de sistema em produção: migração só aditiva ou em duas fases, backup e procedimento de implantação antes de cada versão. | Tratar M9 e M10 como desenvolvimento sem dados, embora rodem depois da inauguração. |
| R13 | Decisões novas ficam nesta spec, na ARCHITECTURE e nos roadmaps. O projeto não tem `docs/adr/`; a convenção é a tabela de decisões da ARCHITECTURE §2 e os "Decisões" dos roadmaps. | Criar `docs/adr/` paralelo às duas fontes. |
| R16 | O expurgo da M8 E16 fica retido por submissão `FAILED` ou `INVALID` só até um teto configurável; passado o teto, o dado sai e o caso fica nas pendências da FNRH. | Reter sem limite, o que descumpre a RN-19 com um `INVALID` esquecido; não reter, o que pode perder dado de um reenvio ainda possível. |

### Hipóteses conferidas no código

Texto literal da spec, seção "Hipóteses conferidas no código (`ca9f9e2`)". Conferência feita pelo arquiteto; não a repeti.

| Hipótese | Resultado |
|---|---|
| M6 H2: base offline e execução de checklist | Confirmada, com outra assinatura: `ChecklistsApi.startExecution` e `completeExecution`. |
| M6 H3: comandos de status em `rooms` | Parcial: `markClean`, `markInspected`, `rejectInspection`, `markDirty`, `setServiceFlag` e OOO existem na `RoomsApi`; a discrepância (RF-UH-08) não está na API pública. |
| M6 H4: consultas por data e `markNoShow` | Falsa: a `ReservationsApi` não tem no-show nem listas por data (só endpoints); `releaseUnused` e `blocksDueForRelease` existem. |
| M6 H5: idempotência em `billing` | Confirmada por `NewPosting.sourceReference` (M5 E04), com chave definida para o fechamento usar. Não há conceito de data fechada: `post` grava na data corrente. |
| M6 H6: aresta `endofday` → `files` "já listada" | Falsa: a tabela §3.1 não a lista. Os PDFs ficam com `reporting`, que tem a aresta. |
| M6: `fnrh.report_pending_submissions` "já existe" | Falsa: o nome previsto na M5 E08 é `fnrh.report_submissions`, ainda a criar. |
| M7 H2: "evento genérico de falha" e indicador de saúde no actuator | Falsa: o M5 usa `NotificationsApi.notify` direto, `GET /fnrh/status` e `MeterBinder`, sem `HealthIndicator`. |
| M8: serviço `backup` "reservado no compose" | Parcial: só um comentário em `docker/compose.yaml`; o serviço é a criar. |
| M8: `opentelemetry-api` | Confirmado na 1.62.0 no `gradle.lockfile`, com Spring Boot 4.1.2; segue o risco aceito com prazo (M5 E14 a). |
| M10 H6: dono dos dados sensíveis da FNRH | Resolvida: `guests` guarda (`sensitive_data`); `fnrh` não guarda, por critério da M5 E08. |

### Etapas novas

Texto literal da spec, seção "Etapas novas". Nenhuma etapa foi cancelada ou renumerada.

| Etapa | Objetivo | Depende de |
|---|---|---|
| M5 E15 | Descrição de gênero no perfil e nos dados da FNRH | E07 |
| M5 E16 | Limpar a credencial do Serpro | E07 |
| M6 E13 | Snapshot e arquivo do fechamento | E09, E11 |
| M6 E14 | No-show na FNRH | E11 |
| M8 E14 | Migrações fora da `api` | — |
| M8 E15 | Re-cifragem de todos os valores cifrados | — |
| M8 E16 | Expurgo dos dados sensíveis da FNRH | — |
| M8 E17 | Cadeia de dependências pronta para produção | — |
| M8 E18 | Coleta e entrega de alertas | E10 |

## Contexto

O usuário pediu, na sessão do arquiteto: "Refaça os roadmaps deste projeto com base no novo modelo de arquiteto e no descrito em /second-brain" (citação da spec). Os roadmaps M5 a M10 eram de 2026-10-13, anteriores ao código e à soul `arquiteto`. O escopo foi alinhar a execução ao template da skill `development-roadmap` e ao `orquestrador` de 2026-11-05 e reler as etapas pendentes. Planos de etapa, código, testes e execução ficaram fora.

## Origem

- Projeto ZenyHotelManager, repositório `/home/caio/repos/ZenyHotelManager`, sessão `claude --agent arquiteto` de 2026-11-06, a partir do `HEAD` `ca9f9e2` na `main`.
- `docs/superpowers/specs/2026-11-06-revisao-arquitetura-roadmaps-design.md` (não rastreado pelo Git): decisões R1 a R16, hipóteses, etapas novas, revisão independente e limites.
- `docs/roadmaps/README.md`: mapa dos marcos, regra 4 e histórico de revisões.
- `docs/ARCHITECTURE.md`: D18, D19, §3.1, §8.3, §12, §13, §15.1 e §16, lidos pelo `git diff` da árvore de trabalho.
- Conferidos para os detalhes das etapas, pelo `git diff` e por leitura parcial: `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`, `roadmap-m6-operacao-fechamento.md` e `roadmap-m8-restaurante-distribuicao.md`; `CLAUDE.md` e `docs/SPEC.md` pelo `git diff`.
- Arquivos alterados sem commit: `CLAUDE.md`, `docs/ARCHITECTURE.md`, `docs/SPEC.md`, `docs/roadmaps/README.md` e os roadmaps de M5 a M10. Novo e não rastreado: `docs/superpowers/specs/`.

## Por que registrar

O hub e as notas de tema ainda indicam a ordem antiga do M5 e do M6, a regra de Git de 2026-10-22, o expurgo no M10 e as migrações na M8 E11. O próximo orquestrador lê essas notas antes de agir, e esta captura vale sobre elas até o curador integrá-la.

## Limitações e incertezas

- **As alterações ainda NÃO têm commit.** Tudo está na árvore de trabalho do repositório local, e a spec nem está rastreada: as citações e os caminhos dependem dessa árvore até o usuário commitar. A spec não foi copiada como anexo; suas decisões, hipóteses e etapas novas estão transcritas acima.
- **Nenhum código foi alterado nem executado** nesta revisão. Etapas novas, D18, D19 e as regras de expurgo são desenho, não estado do sistema.
- **Revisão independente incompleta.** O `revisor-arquitetura` devolveu **"bloqueado": 0 Críticos, 10 Importantes e 9 Menores**. Os achados foram corrigidos (dois viraram as decisões do usuário R14 e R15; os demais, correção de dependência ou de critério), mas **ele não releu o resultado**. A lista dos 19 achados não está nas fontes que li.
- **M7 E03, E04, E05, E07 e E09 a E12 ficaram fora do pedido feito ao revisor.**
- **Hipóteses que dependem de código ainda inexistente (M5 a M8) seguem como hipóteses.** A sincronização antes de cada marco continua valendo.
- Os roadmaps de M7, M9 e M10 não foram lidos para esta captura; o que os afeta vem da spec e do `README.md`. O roadmap do M6 foi lido só no início do `git diff` (índice, hipóteses e parte da E10).
- Não conferi o código nem repeti os achados do arquiteto. Não verifiquei se `WALK_IN` já existe como tipo de dono de conta no `billing`.
- O estado de `origin/main` vem da referência local, sem `fetch`.
- **Resíduos observados na árvore de trabalho, não corrigidos** (interpretação minha, a conferir pelo autor antes do commit):
  - `docs/roadmaps/roadmap-m5-recepcao-fnrh.md` ainda aponta o expurgo para o M10 nas linhas 21, 57 e 77, o que contradiz a R4; a seção da E08 já diz M8 E16.
  - `docs/roadmaps/roadmap-m8-restaurante-distribuicao.md`, linha 29, ainda diz "com o serviço `backup` reservado", o que a conferência da spec corrigiu para "só um comentário".
  - O mesmo roadmap do M8, nas notas da E11, tem dois itens de lista colados numa só linha (`` `ZenyHotelManager - Docker, observabilidade e CI`).- Pontos de atenção ``).
  - Os números de linha citados são os da árvore de trabalho em 2026-11-06.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Estado por marco]]
- [[ZenyHotelManager - Arquitetura e estrutura de módulos]]
- [[ZenyHotelManager - Módulo guests]]
- [[ZenyHotelManager - Docker, observabilidade e CI]]
- [[ZenyHotelManager - Ambiente, banco, chaves e build]]
- [[ZenyHotelManager - Eventos e jobs]]
- [[ZenyHotelManager - Módulo billing (caixa, pagamentos, caução e encerramento)]] (D18, conta `WALK_IN`)
- [[Decidir pendências do usuário por entrevista com opção recomendada]]
- [[2026-11-05 - ZenyHotelManager - atualização m5-recepcao-fnrh E07 - 9f02405c]]
- `ZenyHotelManager - Módulo fnrh` (nota ainda inexistente; texto proposto na captura da E07)
