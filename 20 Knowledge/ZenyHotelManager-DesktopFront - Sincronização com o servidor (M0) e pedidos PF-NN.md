---
type: knowledge
status: processed
created: 2026-11-17
projects:
  - "[[ZenyHotelManager-DesktopFront]]"
sources:
  - "[[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]]"
  - "[[2026-11-13 - ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão - 677b277a]]"
  - "[[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]]"
---
# ZenyHotelManager-DesktopFront - Sincronização com o servidor (M0) e pedidos PF-NN

Referência técnica do projeto [[ZenyHotelManager-DesktopFront]]: o canal de pedidos `PF-NN` do front ao servidor, o controle dos pedidos e as rodadas do M0 (análise e etapa mecânica de sincronização com a `main` do servidor [[ZenyHotelManager]]). Leia antes de uma rodada do M0 ou de abrir um pedido.

Texto das capturas do `brain-escriba` (resumos do agente feitos a partir dos documentos do repositório), integrado sem resumo nem reescrita; cada bloco indica a captura de origem. A fonte da verdade são os arquivos do repositório `/home/caio/repos/ZenyHotelManager-DesktopFront`. As notas do curador estão marcadas como tal.

## Canal de pedidos front → servidor (F5, ADR 0005)

Origem: [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]].

- **Pedido**: captura nova em `00 Inbox/` chamada `ZenyHotelManager - pedido do front PF-NN <título>`, com motivo (tela ou fluxo), operação desejada (método, caminho, campos), etapa do front que espera por ela, commit fixado do contrato e prioridade. Publicada pelo `brain-escriba` ou pelo orquestrador do front no fechamento da etapa que encontrou a lacuna.
- **Controle local**: `docs/pedidos-servidor.md`, tabela `PF-NN | título | estado (aberto/aceito/entregue/recusado) | captura | etapa do front | commit de entrega`. A etapa dependente fica `#bloqueada` até "PF-NN entregue e sincronizado pelo M0".
- **Resposta**: a captura de fechamento da etapa do servidor cita "atende PF-NN"; a análise do M0 do front a encontra, junto com o contrato novo e o oasdiff.
- O hook `load-brain.py` lista o pedido nas sessões do servidor; depois que o curador processa a Inbox, o pedido e a resposta passam a viver numa nota do projeto do servidor.
- Antes de 17/11, nenhuma etapa da demo depende de pedido.

## Controle dos pedidos

*Nota do curador (conferência por `git` em 2026-11-17, só leitura):* na `main` do front (`6ffc9f3`), a tabela "Controle" de `docs/pedidos-servidor.md` tem quatro pedidos, todos `aberto` e sem commit de entrega. Nenhum documento do servidor (`main` e branches `roadmap/m5-recepcao-fnrh` e `roadmap/m6-operacao-fechamento`) cita "PF-NN". O texto de cada pedido está na nota do servidor indicada.

| PF-NN | Título | Estado | Etapa do front | Nota do servidor |
|---|---|---|---|---|
| PF-01 | Setores dos recados legíveis com `frontdesk.traces.manage` | aberto (2026-11-15) | M2 E05 (não depende; tira a role extra do seed quando entregue) | [[ZenyHotelManager - Hospedagem e recepção]] |
| PF-02 | Histórico do desfazer check-in com a aprovação do superior | aberto (2026-11-15) | M2 E06 (não depende; o roteiro do M2 deixa de prometer "Com aprovação de superior" nessa linha do histórico até a entrega) | [[ZenyHotelManager - Hospedagem e recepção]] |
| PF-03 | Trocar o titular e os hóspedes de uma reserva antes do check-in | aberto (2026-11-17) | M3 E03 (não depende; a tela de alteração ganha a troca quando entregue) | [[ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)]] |
| PF-04 | Prévia da multa de cancelamento da reserva | aberto (2026-11-17) | M3 E04 (não depende; o diálogo passa a mostrar o valor e o prazo antes de confirmar quando entregue) | [[ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)]] |

## Rodada 2 do M0 (2026-11-13, servidor em `57eb5fac5b8a`)

Origem: [[2026-11-13 - ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão - 677b277a]].

Origem: `docs/roadmaps/roadmap-m0-sincronizacao.md`, seção "E02 — Sincronizar com o servidor em `57eb5fac5b8a` (rodada 2)", bloco "Contexto (análise de 2026-11-13, `claude --agent arquiteto`)", e histórico de revisões do mesmo arquivo.

- Servidor analisado: `main` em `57eb5fac5b8a18df01ed4f30e099ab1cd8dcb27b`; pin anterior `ca9f9e2f9808`, 271 commits atrás. Pré-voo: aditivo (código 11), sem breaking change em `/api/v1`.
- Contrato: de **303 para 335 operações**, nenhuma removida e nenhuma existente alterada. 23 schemas novos, um esquema de segurança novo (`printAgentToken`) e 4 schemas alterados (`GuestProfileRequest`, `GuestResponse`, `MergeGuestRequest`, `OperationalSettingsDto`), só com `genderDescription` e descrições.
- As 32 operações novas por tag: `end-of-day` 5; `FNRH` 4; `Printing` 17 (5 delas em `/print-agents/me/*`); documentos em PDF e impressão 6 (tags `frontdesk`, `reservations`, `billing`).
- `docker/` do servidor: compose, `.env.example`, `Dockerfile` e demais pastas iguais; mudaram só `docker/gate/` (compose isolado do gate do servidor, com WireMock no papel da FNRH) e `docker/prometheus/alerts.yaml`.

Onde cada capacidade nova entrou (origem: mesmo bloco do M0 e históricos de 2026-11-13 em `docs/roadmaps/README.md` e nos roadmaps M2, M6 e M7):

| Capacidade | Etapa do front | Natureza |
|---|---|---|
| Ficha de registro e visualizador de PDF | M2 E07 | etapa nova; o gate M2 E06 passa a depender dela |
| Confirmação da reserva em PDF | M3 E03 | etapa existente ampliada |
| Extrato da conta em PDF | M4 E02 | etapa existente ampliada |
| `genderDescription` (FNRH) no perfil | M5 E01 | etapa existente ampliada |
| Fechamento do dia | M6 E08 | etapa nova, `#bloqueada`: o motor do servidor não tem etapas (M6 E11 do servidor pendente; o disparo manual responde `409 END_OF_DAY_NOT_CONFIGURED`). O gate M6 E07 depende dela |
| Fila de envio à FNRH (`retry`, `dismiss`) e limpeza da credencial | M7 E10 | etapa existente ampliada |
| Impressoras, agentes e fila de impressão, com "Enviar à impressora do hotel" | M7 E12 | etapa nova; o gate M7 E11 depende dela |

- **Etapa mecânica criada: M0 E02** (`#pendente`): trocar pin e contrato para `57eb5fac5b8a`, regenerar o SDK com 335 operações, consertar o que quebrar sem funcionalidade nova, rever `tools/server-env/` diante de `docker/gate/`, regenerar o pacote e passar `smokeTest` e o roteiro do M1 contra o servidor novo. Revisão humana: sim. O M2 passa a exigir a M0 E02 concluída (`docs/roadmaps/README.md` e pré-requisito do roadmap M2).
- **Nenhum `PF-NN`**: não havia pedido registrado, nenhum foi aberto e nenhuma captura do brain cita "atende PF-NN" (origem: `docs/pedidos-servidor.md`, seção "Rodadas de análise do M0", linha da rodada 2). A mesma linha registra que ficam aguardando o roadmap do próprio servidor, sem pedido: as etapas do fechamento (M6 E11 dele), que desbloqueiam a M6 E08 do front, e os rótulos da FNRH na ficha (M6 E15 dele).
- **Ruling: não adotar por ora o WireMock da FNRH (`docker/gate/fnrh-mock`) no `zeny-front`.** Motivo registrado no "Fora de escopo" da M0 E02: sem tela da FNRH antes da M7 E10, ele só acrescentaria uma imagem ao pacote; sem credencial, as submissões ficam `PENDING` e não atrapalham o check-in. A M7 E10 reavalia se a demo deve mostrar submissões `SENT` (origem: M0 E02 e histórico de 2026-11-13 do roadmap M7).
- Contagem de etapas por marco após a análise (`docs/roadmaps/README.md`): M2 7, M6 8, M7 12 (no limite de referência, segundo o histórico do M7).
- Hipóteses novas: M2 H4 (biblioteca de PDF renderiza e imprime em memória no Linux e no Windows dentro do JAR multiplataforma) e H5 (Recepcionista do seed tem `frontdesk.stays.checkin`); M6 H3 (próxima rodada do M0 já terá a M6 E11 do servidor); M7 H3 (fila de impressão demonstrável sem agente real).

## Rodada 3 do M0 (2026-11-15, servidor em `5e06f16d51ff`)

Origem: [[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]].

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

### Pedidos ao servidor na rodada 3

Origem: `docs/pedidos-servidor.md`, linha da rodada 3.

- **PF-01 e PF-02 seguem `aberto`**; nenhuma captura do brain nem documento do servidor (`main` e branches `roadmap/m5-recepcao-fnrh` e `roadmap/m6-operacao-fechamento`) cita "atende PF-NN". Nenhum pedido novo.
- Chegaram sem pedido os dois itens que a rodada 2 deixara esperando (M6 E11 e M6 E15 do servidor), além do no-show na FNRH (M6 E14) e do corpo mínimo das escritas de restrição e mesclagem (M6 E17).

### Etapa M0 E03

Origem: `docs/roadmaps/roadmap-m0-sincronizacao.md`, seção E03. Executada pelo orquestrador.

- Pin e contrato em `5e06f16d51ff`; SDK regenerado com as 335 operações; teste de caracterização no `sdk` do tipo gerado para as três escritas, provando que os dois ramos passam íntegros pelo cliente gerado; o `core` não muda por causa do `oneOf` (fachada é da M5 E02).
- Rótulos pt-BR próprios para `NO_SHOW` (histórico) e `RESERVATION_NO_SHOW` (alocação) no detalhe da reserva da M2 E01; os dois valores da FNRH ficam para a M7 E10.
- Revisão de `tools/server-env/` arquivo por arquivo; `zeny-front` recriado do zero (`down.sh -v`) em `5e06f16d51ff`; pacote regenerado; `smokeTest` verde.
- `LEIA-ME` (fluxo 3) e início de `docs/demo/roteiro-m1.md` e `roteiro-m2.md` avisam do fechamento automático às 03:00; no passo da ficha do `roteiro-m2.md`, "(código FNRH)" vira exceção.
- Fora de escopo: telas de restrição e mesclagem, tela do fechamento, fila da FNRH, mudar o `endOfDayTime` no seed, disparar fechamento manual, escrever no servidor.
- Notas: se o ogen falhar no `oneOf`, parar e relatar (ADR 0007, critério 1); não disparar fechamento manual; um Gradle por vez no notebook (o orquestrador do servidor está ativo); a validação no Windows entra na lista acumulada (regra 7).

## Estado da sincronização

*Nota do curador (conferência por `git` em 2026-11-17, só leitura):* na `main` do front (`6ffc9f3`), `api/server-pin.properties` traz `commit=5e06f16d51ff9913f0da09df8f62639996cd6c52`, `contract_sha256=6c0512fdd91e805b6a67664b6881080707eaea820b3425ae92884250daeebdc9` e `synced_at=2026-11-16T01:45:36Z`. No roadmap do M0, a E01 está `#concluida` e a E02 e a E03 estão `#em-andamento`, na lista "Validações acumuladas no Windows" de `docs/roadmaps/README.md` (regra 7). A `main` do servidor está em `5e06f16`, igual ao commit fixado: não há avanço a sincronizar nesta data. As M6 E18, E01 e E02 do servidor existem só na branch `roadmap/m6-operacao-fechamento` dele, fora da `main`.

## Limitações registradas nas capturas

Da captura de 2026-11-13:

- O escriba não conferiu os números do contrato (303, 335, 32, 23) nem o commit do servidor contra o repositório do servidor; vêm do texto da análise.
- Os roadmaps M3, M4 e M5 não foram lidos diretamente: as ampliações de M3 E03, M4 E02 e M5 E01 vêm do bloco de contexto da M0 E02 e da tabela de `docs/roadmaps/README.md`.

Da captura de 2026-11-15:

- O escriba não conferiu contra o repositório do servidor os números (131 commits, 335 operações), o commit nem a regra da ARCHITECTURE §7; vêm do texto da análise.
- O tipo que o ogen gera para o `oneOf` (`JsonElement`) ainda não foi provado pelo front; é o que a M0 E03 vai caracterizar.

---

## Proveniência

- 2026-11-17 — [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]] (capture_id: 16d5b400-b2e5-490e-b063-b61b40c14257): canal de pedidos `PF-NN` (F5); nota criada pelo curador.
- 2026-11-17 — [[2026-11-13 - ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão - 677b277a]] (capture_id: 677b277a-44a4-4da4-8214-4dfca2edc865): resultado da análise da rodada 2 do M0 e etapa M0 E02.
- 2026-11-17 — [[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]] (capture_id: 5bba7217-6f3f-460d-8b80-ace44d5b8683): resultado da análise da rodada 3 do M0, pedidos na rodada e etapa M0 E03.
