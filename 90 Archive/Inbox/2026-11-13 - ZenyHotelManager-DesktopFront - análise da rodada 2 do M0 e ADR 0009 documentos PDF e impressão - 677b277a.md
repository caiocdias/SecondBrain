---
type: capture
status: archived
created: 2026-11-13
capture_id: 677b277a-44a4-4da4-8214-4dfca2edc865
projects:
  - "[[ZenyHotelManager]]"
---

# ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão

## Conteúdo capturado

Resumo do agente (escriba), feito a partir dos documentos do repositório do front. Cada bloco indica o arquivo de origem.

### Decisão: ADR 0009, documentos em PDF e impressão

Origem: `docs/adr/0009-documentos-pdf-e-impressao.md`. Estado no ADR: "aceita · 2026-11-13 · decidida pelo usuário em entrevista (as três opções recomendadas), na análise da rodada 2 do M0".

Contexto (fatos do contrato do servidor em `57eb5fac5b8a`, conforme o ADR):

- O servidor (M5 E10 e E11 dele) passou a gerar três documentos, cada um com um `GET …/pdf` e um `POST …/print`: ficha de registro (`/reservations/{id}/registration-card`, permissão `frontdesk.stays.checkin`), confirmação da reserva (`/reservations/{id}/confirmation`, `reservations.reservations.read`) e extrato da conta (`/folios/{id}/statement`, `billing.folios.read`).
- O `GET …/pdf` devolve `application/pdf`, sem cache no servidor; a ficha traz dados pessoais dos hóspedes com documentos mascarados.
- O `POST …/print` exige `Idempotency-Key` e uma impressora ativa, devolve `202` e põe o job na fila do servidor. Quem imprime é um agente de impressão em repositório próprio, que ainda não existe e que o design deixa fora do desktop.
- Listar impressoras exige `printing.jobs.read`; cadastrar agentes e impressoras exige `printing.agents.manage` (só Administrador).
- No servidor, o `GET` da ficha não deixa trilha e a impressão deixa (D-E11-10 do servidor).
- Restrição do design §6.2 do front: nenhum dado de hóspede em log nem em cache de disco.

Decisão do usuário (três pontos, todos pela opção recomendada):

1. **Ficha de registro no M2**, como etapa própria (M2 E07), depois do check-in e antes do gate. O visualizador nasce nela e é reaproveitado pela confirmação (M3 E03) e pelo extrato (M4 E02).
2. **Visualizador de PDF em memória**: o app baixa o PDF pelo `core` e renderiza numa janela ou painel do app, com biblioteca de PDF para a JVM (candidata Apache PDFBox; escolha final do construtor, registrada no handoff da M2 E07). Nada vai ao disco, salvo por **"Salvar como…"**, ação explícita do usuário com destino escolhido por ele. Sem arquivo temporário e sem abrir o leitor de PDF do sistema.
3. **Impressão local agora, fila do servidor depois**: "Imprimir" (desde a M2 E07) manda o PDF em memória para uma impressora do SO pelo diálogo de impressão da JVM, sem arquivo e sem trilha no servidor. "Enviar à impressora do hotel" (M7 E12) usa `POST …/print` com impressora ativa, nas três telas de documento, só com permissão efetiva e ao menos uma impressora ativa.

Alternativas descartadas (motivos do ADR):

- Ficha adiada para o M4, junto com o extrato: descartada porque a ficha fecha a história do check-in, que o gerente conhece em papel, e o ADR 0006 favorece amplitude.
- Ficha dentro da M2 E02: daria dois objetivos à etapa do check-in.
- Arquivo temporário aberto no leitor do sistema: abriria exceção ao §6.2 (arquivo pode sobrar no disco; o leitor guarda histórico).
- Só "Salvar como…": pareceria um download na demo.
- Só a fila do servidor: na demo nada sairia no papel, porque não há agente.
- Só a impressão local: deixaria sem tela as rotas `POST …/print` e o modelo de impressão central do servidor, que o mobile também usa.

Consequências registradas no ADR:

- Dependência nova de renderização de PDF; catálogo e lockfiles mudam no mesmo commit.
- Componente de visualização e impressão no módulo `design`; download como fachada do `core` (ADR 0008).
- Dois caminhos de impressão: o local sem trilha no servidor, o da fila com trilha.
- Rótulos de motivo de viagem e meio de transporte da ficha saem como "(código FNRH)" até a M6 E15 do servidor; o front não corrige conteúdo do PDF.
- Rotas `/api/v1/print-agents/me/*` (esquema `printAgentToken`) ficam fora do desktop na cobertura do M7.

### Resultado da análise da rodada 2 do M0 (2026-11-13)

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

## Contexto

Sessão `claude --agent arquiteto` de 2026-11-13, com `development-roadmap` em modo atualização, fazendo a análise da rodada 2 do M0 (sincronização do front com o servidor). As três decisões do ADR 0009 foram tomadas pelo usuário em entrevista com opção recomendada durante essa análise. Captura publicada pelo escriba a pedido dessa sessão.

## Origem

- Projeto: ZenyHotelManager-DesktopFront, repositório local `/home/caio/repos/ZenyHotelManager-DesktopFront`, branch `main`, HEAD `83fd21fa48ac56d451fe80a872b97c04fec4654c`.
- **Sem commit**: todos os textos abaixo estão só na árvore de trabalho (o ADR 0009 é arquivo não rastreado; os demais aparecem modificados em `git status`).
- Arquivos lidos:
  - `docs/adr/0009-documentos-pdf-e-impressao.md` (integral)
  - `docs/roadmaps/roadmap-m0-sincronizacao.md`, seção E02 (rodada 2) e histórico de revisões
  - `docs/pedidos-servidor.md`, seção "Rodadas de análise do M0"
  - históricos de revisão de 2026-11-13 em `docs/roadmaps/README.md`, `docs/roadmaps/roadmap-m2-recepcao-do-dia.md`, `docs/roadmaps/roadmap-m6-governanca-operacao.md` e `docs/roadmaps/roadmap-m7-gestao-cadastros.md` (lidos pelo `git diff` contra o HEAD)
- Servidor de referência: `/home/caio/repos/ZenyHotelManager`, commit `57eb5fac5b8a18df01ed4f30e099ab1cd8dcb27b`, citado pelos documentos do front.

## Por que registrar

Guarda uma decisão de arquitetura do usuário (ADR 0009) e o resultado de uma rodada de sincronização front-servidor, com o destino de cada capacidade nova nos marcos. Serve às próximas sessões do front (M0 E02, M2 E07, M6 E08, M7 E10 e E12) e à criação do hub do projeto.

## Limitações e incertezas

- Nada commitado: o conteúdo pode mudar antes do commit, e não há hash do front que contenha estes textos. Nenhum anexo foi copiado; a referência depende dos caminhos locais acima.
- O escriba não conferiu os números do contrato (303, 335, 32, 23) nem o commit do servidor contra o repositório do servidor; vêm do texto da análise.
- Os roadmaps M3, M4 e M5 não foram lidos diretamente: as ampliações de M3 E03, M4 E02 e M5 E01 vêm do bloco de contexto da M0 E02 e da tabela de `docs/roadmaps/README.md`.
- A biblioteca de PDF ainda não foi escolhida (hipótese H4 da M2); se nenhuma servir, a decisão volta ao usuário antes de cair para arquivo temporário.

## Observação para o curador

O projeto ZenyHotelManager-DesktopFront ainda não tem hub no vault. Destino sugerido: o hub do ZenyHotelManager-DesktopFront (ou a nota de decisões dele) quando for criado, junto com a captura de registro pendente [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]] (`capture_id` 16d5b400-b2e5-490e-b063-b61b40c14257). Esta captura não corrige aquela; acrescenta o ADR 0009 (a anterior cobre F1 a F6, ADRs 0001 a 0006) e a rodada 2 do M0. Note que a contagem de etapas por marco da captura anterior (M2 6, M6 7, M7 11) mudou para M2 7, M6 8, M7 12.

## Possíveis conexões

- [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]]: decisões F1 a F6 e marcos do front, incluindo o mecanismo do M0 e o canal PF-NN.
- [[ZenyHotelManager]]: projeto do servidor, cujo contrato em `57eb5fac5b8a` foi analisado.
- [[ZenyHotelManager - Módulo fnrh]]: envio assíncrono e fila de submissões que entram na M7 E10 do front.
- [[ZenyHotelManager - Estado por marco]]: estado das etapas do servidor citadas (M5 E10 e E11, M6 E10, E11, E13 e E15).
- [[Decidir pendências do usuário por entrevista com opção recomendada]]: as três decisões do ADR 0009 foram tomadas em entrevista, todas pela opção recomendada.
