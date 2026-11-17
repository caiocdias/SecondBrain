---
type: capture
status: archived
created: 2026-11-15
capture_id: 5bba7217-6f3f-460d-8b80-ace44d5b8683
projects:
  - "[[ZenyHotelManager]]"
---

# ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão

## Conteúdo capturado

Resumo do agente (escriba), feito a partir dos documentos do repositório do front. Cada bloco indica o arquivo de origem. Continua a captura anterior [[2026-11-13 - ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão - 677b277a]] (`capture_id` 677b277a-44a4-4da4-8214-4dfca2edc865); não a corrige, só acrescenta a rodada 3.

### Decisão: ADR 0010, resposta que varia com a permissão

Origem: `docs/adr/0010-resposta-que-varia-com-a-permissao.md` (arquivo novo). Estado no ADR: "aceita · 2026-11-15 · decidida pelo usuário em entrevista (a opção recomendada), na análise da rodada 3 do M0". Relacionadas: ADR 0007 e ADR 0008; design §6.1 e §6.2.

Contexto (fatos do contrato do servidor em `5e06f16d51ff`, conforme o ADR):

- Na M6 E17 do servidor, três escritas do `guests` (`restrictGuest`, `liftGuestRestriction`, `mergeGuests`) passaram a responder `200` com `oneOf: [GuestResponse, GuestWriteSummaryResponse]`. É o primeiro `oneOf` do contrato (não havia nenhum até `57eb5fac5b8a`). O `oasdiff` o classifica como `warning` (`response-body-wrapped-in-one-of-original-preserved`); o pré-voo dá "aditivo" (código 11).
- A regra é do servidor (`docs/ARCHITECTURE.md` §7 dele, linha "Resposta que varia com a permissão", decidida pelo usuário em 2026-11-15): com `guests.profiles.read` vem o perfil inteiro (`GuestResponse`); sem ela, o resumo `GuestWriteSummaryResponse` `{id, restricted}`, sem dado pessoal; a versão vai no `ETag`. O `oneOf` **não tem discriminador**: os ramos são disjuntos pelo `required` (o completo exige `fullName`; o reduzido exige `restricted`, que o completo não tem), sem `additionalProperties: false`. Segundo o servidor, com o ogen 0.16.1 os clientes gerados recebem essas operações como `JsonElement`. A regra vale para as próximas respostas que dependerem da permissão.
- O ADR 0008 não deixa as features usarem o `sdk` cru, e o design §6.2 proíbe JSON cru nas telas: um `JsonElement` não pode chegar ao `app`.

Decisão do usuário (opção recomendada): **quem decodifica é o `core`**. Numa operação cuja resposta é um `oneOf` sem discriminador, a fachada:

1. lê o corpo como o `sdk` o entrega (o `JsonElement`, se a M0 E03 confirmar esse tipo);
2. escolhe o ramo pelas propriedades obrigatórias exclusivas de um ramo (`fullName` presente indica o completo; `restricted` presente sem `fullName` indica o resumo);
3. decodifica o ramo escolhido com o serializer gerado, com o mesmo `Json` do `sdk`;
4. devolve às features um resultado tipado com os dois casos, cada um com o modelo gerado e o `ETag`;
5. falha fechado: nenhum ramo, os dois ramos ou falha de decodificação dão `ApiError.IncompatibleResponse`; sem palpite nem ramo padrão.

Nome do tipo, forma do resultado e local da função genérica de escolha ficam com o construtor da M5 E02 (primeira etapa consumidora).

Alternativas descartadas (motivos do ADR):

- Descartar o corpo e reler por `GET /api/v1/guests/{id}`: chamada a mais, corrida entre escrita e leitura (o `ETag` pode não ser o da escrita) e, sem `guests.profiles.read`, a releitura não serve.
- Entregar o `JsonElement` às features: fere o design §6.2 e o ADR 0008.
- Ajustar o `sdk` gerado ou trocar de gerador para ter tipo-soma: fere o ADR 0007 (sem código à mão no `sdk`; o ogen cumpre os quatro critérios).
- Pedir ao servidor um discriminador (`PF-NN`): o servidor já recusou na ARCHITECTURE §7 dele, porque exigiria propriedade nova no esquema completo de todas as operações da regra.
- Tentar `GuestResponse` e, se falhar, o resumo: funciona hoje, mas depende da ordem e não detecta resposta que case com os dois ramos.

Consequências registradas: `ETag` nos dois ramos (o `If-Match` seguinte funciona igual); a tela trata o resumo como sucesso sem perfil; a M0 E03 caracteriza por teste no `sdk` o tipo gerado, sem mudar o `core` (se não for `JsonElement`, ajusta-se o passo 1; se o ogen não gerar ou não compilar, a M0 E03 para, por ser decisão de arquitetura, ADR 0007 critério 1); a M5 E02 é a primeira a usar a regra; cada rodada do M0 passa a procurar `oneOf` novo no contrato e apontar a etapa consumidora.

### Resultado da análise da rodada 3 do M0 (2026-11-15)

Origem: `docs/roadmaps/roadmap-m0-sincronizacao.md`, seção "E03 — Sincronizar com o servidor em `5e06f16d51ff` (rodada 3)", bloco "Contexto (análise de 2026-11-15, `claude --agent arquiteto`)", e a última linha do "Histórico de revisões".

- Servidor analisado: `main` em `5e06f16d51ff9913f0da09df8f62639996cd6c52`; pin anterior `57eb5fac5b8a`, 131 commits atrás. Pré-voo: aditivo (código 11), sem `ERR` em `/api/v1`; 3 `warning` de `oneOf`, um por operação.
- Contrato (diff de `api/openapi.yaml` entre os dois commits):
  - 335 operações nos dois; nenhuma entrou ou saiu;
  - um schema novo, `GuestWriteSummaryResponse` `{id, restricted}`;
  - o `oneOf` sem discriminador em `restrictGuest`, `liftGuestRestriction` e `mergeGuests` (ADR 0010);
  - valores novos de `x-extensible-enum`: `ReservationHistoryResponse.kind` `NO_SHOW`; `RoomAssignmentResponse.releaseReason` `RESERVATION_NO_SHOW`; `FnrhSubmissionResponse.operation` `NO_SHOW`; `FnrhSubmissionResponse.lastFailure` `REMOTE_NO_SHOW`;
  - só descrições mudaram na ficha de registro (rótulo do catálogo de domínios da FNRH no motivo da viagem e no meio de transporte, M6 E15 do servidor) e em `GuestResponse.genderDescription`;
  - nenhum código de erro novo.
- Servidor: entraram as M6 E11, E14, E15, E16 e E17 dele. A E11 traz as 8 etapas do fechamento do dia (`no-show`, `pending-departures`, `room-charges`, `block-release`, `provisional-expiry`, `card-pre-authorizations` como `NOT_APPLICABLE`, `occupied-rooms-dirty`, `advance-business-date`). A E18 dele (cursor, rollback, datas estritas) **não** está neste pin.
- `docker/` do servidor: diff vazio. O `application.yaml` só ganhou `zeny.endofday.trigger.wait` (padrão `PT5S`); nenhuma variável de ambiente nova.
- Fechamento automático: o `EndOfDayTriggerJob` roda a cada minuto; num banco novo a data operacional é hoje no fuso do hotel; o `endOfDayTime` padrão é 03:00 e, antes do meio-dia, vence no dia seguinte; o gatilho só age até 24 h depois do vencimento. Um ambiente no ar até as 03:00 do dia seguinte à criação é fechado sozinho (chegadas confirmadas sem check-in viram `NO_SHOW` com multa, diárias lançadas, saídas pendentes viram pendências, data avança).

### Regra 5 revista: recriar a demo

Origem: `docs/roadmaps/README.md`, regra 5 e última linha do histórico (2026-11-15).

- Num banco novo, a data operacional é o dia da recriação. Desde o servidor em `5e06f16d51ff` (M0 E03), ela avança sozinha: o servidor fecha o dia às 03:00 do dia seguinte (`endOfDayTime` padrão), com no-show das chegadas confirmadas sem check-in (com multa), lançamento das diárias e avanço da data.
- A recriação vale só para o dia em que é feita: recriar no mesmo dia do roteiro ou da demo, depois das 03:00, nunca na véspera. O seed não muda o horário do fechamento. O fechamento manual só entra num roteiro a partir do M6 (E08), por último ou seguido de nova recriação.
- A tabela de marcos do README passa a dar o M3 como dependente de "M2 e M0 E03", e o M6 com o fechamento do dia "desbloqueado pela rodada 3 do M0".

### Desbloqueio da M6 E08 (fechamento do dia)

Origem: `docs/roadmaps/roadmap-m6-governanca-operacao.md`, E08, H3 e último histórico.

- A E08 saiu de `#bloqueada` para `#pendente`: a M6 E11 do servidor (8 etapas e avanço da data) está no commit que a M0 E03 fixa. Dependência: gate do M5 e servidor fixado em `5e06f16d51ff` ou depois.
- H3 marcada **confirmada (2026-11-15)**.
- Escopo revisto: a E11 do servidor não mudou o contrato do fechamento (nenhuma operação nem código de erro novo; `kind` e `stepName` das pendências são texto livre). Entrou um critério de no-show (chegada confirmada sem check-in aparece como "Não compareceu", ou como pendência se o servidor recusou a multa) e notas com decisões da E11 do servidor (multa recusada impede o no-show inteiro; etapa que falha não avisa as pendências gravadas; avanço que esgota o prazo fica `FAILED` até retomada manual). Risco novo: a M6 E13 do servidor (snapshot e PDFs) pode trazer etapas antes do avanço; a tela mostra as etapas como o servidor lista.

### Pedidos ao servidor

Origem: `docs/pedidos-servidor.md`, linha da rodada 3.

- **PF-01 e PF-02 seguem `aberto`**; nenhuma captura do brain nem documento do servidor (`main` e branches `roadmap/m5-recepcao-fnrh` e `roadmap/m6-operacao-fechamento`) cita "atende PF-NN". Nenhum pedido novo.
- Chegaram sem pedido os dois itens que a rodada 2 deixara esperando (M6 E11 e M6 E15 do servidor), além do no-show na FNRH (M6 E14) e do corpo mínimo das escritas de restrição e mesclagem (M6 E17).

### Notas novas em outros marcos

Origem: últimas linhas do histórico de cada roadmap.

- M3 (`roadmap-m3-reservas.md`): E04 ganhou a nota da reativação de no-show (o `reactivate` vale também para no-show; o seed não cria no-show, coberto por teste do *state holder*); E05 a da recriação no mesmo dia. O marco passa a exigir a M0 E03 antes da E01.
- M5 (`roadmap-m5-hospedes-empresas.md`): E02 ganhou dois critérios (teste da fachada do `core` nas três escritas, incluindo `IncompatibleResponse`; tela conclui a ação com o resumo sem tentar mostrar o perfil) e notas sobre o ADR 0010.
- M7 (`roadmap-m7-gestao-cadastros.md`): E10 ganhou a nota do no-show na fila da FNRH (rótulos pt-BR para `NO_SHOW` e `REMOTE_NO_SHOW`).
- Nenhuma tag mudou nesses três roadmaps.

### Atualizações nos ADRs 0007 e 0009

- `docs/adr/0007-gerador-do-sdk.md`: item novo "`oneOf` sem discriminador" (desde `5e06f16d51ff`, o ogen entrega `JsonElement` segundo a ARCHITECTURE §7 do servidor; o `core` escolhe o ramo pelo ADR 0010; a M0 E03 caracteriza o tipo). Linha "Atualização de 2026-11-15" (pendência R4 da M0 E02): desde `57eb5fac5b8a` há um segundo esquema de segurança; nas 5 rotas `/api/v1/print-agents/me/*` o `ogenAuthAttr` é `printAgentToken`. O `core` atual põe o `Bearer` em qualquer `ogenAuthAttr` não vazio; o defeito está caracterizado por teste e registrado na M7 E12, e ninguém chama essas rotas no desktop. A regra correta é tratar como sessão de usuário só `bearerAuth` e falhar fechado em qualquer outro.
- `docs/adr/0009-documentos-pdf-e-impressao.md`: linha "Atualização de 2026-11-15": a M6 E15 do servidor está em `5e06f16d51ff`; a ficha mostra o rótulo do catálogo de domínios da FNRH, e "(código FNRH)" só aparece para código fora do catálogo. Vale a partir da M0 E03.

### Etapa a executar: M0 E03 (`#pendente`, revisão humana: sim)

Origem: `docs/roadmaps/roadmap-m0-sincronizacao.md`, seção E03. Executada pelo orquestrador.

- Pin e contrato em `5e06f16d51ff`; SDK regenerado com as 335 operações; teste de caracterização no `sdk` do tipo gerado para as três escritas, provando que os dois ramos passam íntegros pelo cliente gerado; o `core` não muda por causa do `oneOf` (fachada é da M5 E02).
- Rótulos pt-BR próprios para `NO_SHOW` (histórico) e `RESERVATION_NO_SHOW` (alocação) no detalhe da reserva da M2 E01; os dois valores da FNRH ficam para a M7 E10.
- Revisão de `tools/server-env/` arquivo por arquivo; `zeny-front` recriado do zero (`down.sh -v`) em `5e06f16d51ff`; pacote regenerado; `smokeTest` verde.
- `LEIA-ME` (fluxo 3) e início de `docs/demo/roteiro-m1.md` e `roteiro-m2.md` avisam do fechamento automático às 03:00; no passo da ficha do `roteiro-m2.md`, "(código FNRH)" vira exceção.
- Fora de escopo: telas de restrição e mesclagem, tela do fechamento, fila da FNRH, mudar o `endOfDayTime` no seed, disparar fechamento manual, escrever no servidor.
- Notas: se o ogen falhar no `oneOf`, parar e relatar (ADR 0007, critério 1); não disparar fechamento manual; um Gradle por vez no notebook (o orquestrador do servidor está ativo); a validação no Windows entra na lista acumulada (regra 7).

## Contexto

Sessão `claude --agent arquiteto` de 2026-11-15, com `development-roadmap` em modo atualização, fazendo a análise da rodada 3 do M0 (sincronização do front com o servidor). A decisão do ADR 0010 foi tomada pelo usuário em entrevista, pela opção recomendada. Captura publicada pelo escriba a pedido dessa sessão.

## Origem

- Projeto: ZenyHotelManager-DesktopFront, repositório local `/home/caio/repos/ZenyHotelManager-DesktopFront`, branch `main`, HEAD `42d58111598292dafe927b8e16b98c78e76cb490`.
- **Sem commit**: o ADR 0010 é arquivo não rastreado; os demais aparecem modificados em `git status`. O commit fica pendente com o usuário.
- Arquivos lidos (ADR 0010 integral; os demais pelo `git diff` contra o HEAD):
  - `docs/adr/0010-resposta-que-varia-com-a-permissao.md`
  - `docs/roadmaps/roadmap-m0-sincronizacao.md` (seção E03 e histórico)
  - `docs/roadmaps/README.md` (regra 5, tabela de marcos e histórico)
  - `docs/pedidos-servidor.md` (linha da rodada 3)
  - `docs/roadmaps/roadmap-m6-governanca-operacao.md` (E08, H3, contexto e histórico)
  - `docs/roadmaps/roadmap-m3-reservas.md`, `roadmap-m5-hospedes-empresas.md`, `roadmap-m7-gestao-cadastros.md` (notas e históricos)
  - `docs/adr/0007-gerador-do-sdk.md` e `docs/adr/0009-documentos-pdf-e-impressao.md` (linhas de 2026-11-15)
- Servidor de referência: `/home/caio/repos/ZenyHotelManager`, commit `5e06f16d51ff9913f0da09df8f62639996cd6c52`, citado pelos documentos do front.

## Por que registrar

Guarda uma decisão de arquitetura do usuário (ADR 0010, que define o padrão do front para toda resposta `oneOf` sem discriminador) e o resultado da rodada 3 de sincronização: mudança de comportamento da demo (data operacional que avança às 03:00), desbloqueio da M6 E08 e a etapa M0 E03 a executar. Serve às próximas sessões do front (M0 E03, M3, M5 E02, M6 E08, M7 E10) e à criação do hub do projeto.

## Limitações e incertezas

- Nada commitado: o conteúdo pode mudar antes do commit, e nenhum hash do front contém estes textos. Nenhum anexo foi copiado; a referência depende dos caminhos locais acima.
- O escriba não conferiu contra o repositório do servidor os números (131 commits, 335 operações), o commit nem a regra da ARCHITECTURE §7; vêm do texto da análise.
- O tipo que o ogen gera para o `oneOf` (`JsonElement`) ainda não foi provado pelo front; é o que a M0 E03 vai caracterizar.
- O diff também alterou `docs/superpowers/specs/2026-11-10-front-desktop-design.md` (linhas "Atualização de 2026-11-15" em não-objetivos e em "A data mostrada como hoje"), fora da lista pedida; não foi resumido aqui além desta menção.

## Observação para o curador

O projeto ZenyHotelManager-DesktopFront ainda não tem hub no vault. Destino sugerido: o hub do ZenyHotelManager-DesktopFront quando for criado, e a nota de estado e decisões do projeto (ADRs, rodadas do M0, estado por marco), junto com as capturas pendentes [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]] e [[2026-11-13 - ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão - 677b277a]]. Na captura da rodada 2, a M6 E08 aparece `#bloqueada`; esta a dá como `#pendente`. A regra 5 do README também mudou desde então.

## Possíveis conexões

- [[2026-11-13 - ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão - 677b277a]]: rodada anterior do M0 e ADR 0009.
- [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]]: decisões F1 a F6 e marcos do front.
- [[2026-11-15 - ZenyHotelManager - atualização arquitetura §7 resposta que varia com a permissão - 77927cd7]]: a regra do `oneOf` do lado do servidor (arquivada).
- [[2026-11-15 - ZenyHotelManager - pedido do front PF-01 Setores dos recados legíveis com frontdesk.traces.manage - 324e0e8f]] e [[2026-11-15 - ZenyHotelManager - pedido do front PF-02 Histórico do desfazer check-in com a aprovação do superior - b6c7bc32]]: os dois pedidos que seguem abertos.
- [[ZenyHotelManager]]: projeto do servidor, cujo contrato em `5e06f16d51ff` foi analisado.
- [[ZenyHotelManager - Módulo guests]]: escritas de restrição e mesclagem com resposta que varia com a permissão.
- [[ZenyHotelManager - Módulo endofday]]: etapas do fechamento e gatilho automático.
- [[ZenyHotelManager - Módulo fnrh]]: no-show na fila de submissões e rótulos da ficha.
- [[ZenyHotelManager - Estado por marco]]: estado das etapas do servidor citadas (M6 E11, E13, E14, E15, E16, E17, E18).
- [[Decidir pendências do usuário por entrevista com opção recomendada]]: a decisão do ADR 0010 foi tomada em entrevista, pela opção recomendada.
