---
type: project
created: 2026-11-17
aliases:
  - "Zeny Hotel Manager Desktop Front"
sources:
  - "[[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]]"
  - "[[2026-11-13 - ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão - 677b277a]]"
  - "[[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]]"
  - "[[2026-11-16 - ZenyHotelManager-DesktopFront - ADR 0011 processo acelerado até a demo - 0cc1844e]]"
  - "[[2026-11-17 - ZenyHotelManager-DesktopFront - ADR 0012 revoga o processo acelerado e atualização dos roadmaps - 10b921ef]]"
---
# ZenyHotelManager-DesktopFront

## Objetivo

Front-end desktop do Zeny Hotel Manager (PMS de um único hotel, até 30 UHs): cliente em **Compose Multiplatform Desktop** (Kotlin, JDK 25, Gradle pelo wrapper) do servidor [[ZenyHotelManager]], com o cliente da API gerado do contrato `api/openapi.yaml`. Atende recepção e gerência e, por decisão do usuário, é o superconjunto do mobile (governança e checklists entram). Restrição do usuário: sem Node. Meta inicial: demo de 17/11/2026 para o gerente, com amplitude acima de profundidade; depois, o front acompanha o servidor.

Repositório local: `/home/caio/repos/ZenyHotelManager-DesktopFront`. O repositório do servidor é só leitura para as sessões do front.

- `docs/superpowers/specs/2026-11-10-front-desktop-design.md`: design aprovado pelo usuário em 2026-11-10.
- `docs/adr/`: ADRs 0001 a 0012.
- `docs/roadmaps/`: `README.md` (mapa, regras e listas acumuladas) e um `roadmap-mN-*.md` por marco (M0 a M7).
- `docs/pedidos-servidor.md`: controle dos pedidos `PF-NN` ao servidor.
- `CLAUDE.md`: módulos (`sdk`, `core`, `design`, `app`, `demo-seed`), comandos, `verificação rápida` e gate do projeto.

Documentação e commits em pt-BR; código e identificadores em inglês.

## Estado

Conferido pelo curador por `git` (só leitura) em 2026-11-17, na `main` em `6ffc9f3` ("merge: M3 E05 e início da E06"), igual à `origin/main`:

- Servidor fixado em `5e06f16d51ff` (`api/server-pin.properties`), a ponta da `main` do servidor nesta data.
- M1 concluído. M2: E01 a E05 e E07 `#concluida`; gate E06 `#em-andamento`, aguardando a validação no Windows. M0: E01 `#concluida`; E02 e E03 `#em-andamento`, aguardando o Windows.
- M3: E01 a E04 `#concluida`; gate E05 `#em-andamento` (aguardando o Windows); E06 (revisão adiada do processo acelerado) `#em-andamento`: falta a revisão final, e a dívida ainda não tem a marca de paga. O M4 só começa com a M3 E06 `#concluida`.
- M4 a M7: todas as etapas `#pendente`.
- Processo: ciclo padrão das souls desde 2026-11-17 (o ADR 0012 revogou o processo acelerado do ADR 0011).
- Pedidos ao servidor: PF-01 a PF-04 `aberto`.
- Git: trabalho em `roadmap/<slug>` e merge local na `main` no fim do lote; push e deploy são do usuário.

## Notas do projeto

Ficam em `20 Knowledge/` do vault (arquivo = nome do link + `.md`). Guardam o texto das capturas; a fonte da verdade são os documentos do repositório.

- [[ZenyHotelManager-DesktopFront - Arquitetura e decisões (ADRs 0001 a 0010)]]: objetivo e restrições, F1 a F6, chamadas do arquiteto, PDF e impressão (0009), `oneOf` sem discriminador (0010). Leia antes de mexer em stack, contrato, ambiente do servidor, PDF ou respostas `oneOf`.
- [[ZenyHotelManager-DesktopFront - Sincronização com o servidor (M0) e pedidos PF-NN]]: canal e controle dos pedidos, rodadas 2 e 3 do M0, commit fixado. Leia antes de uma rodada do M0 ou de abrir um pedido.
- [[ZenyHotelManager-DesktopFront - Marcos, roadmaps e demo]]: marcos M0 a M7 com as tags das etapas, recriação da demo (fechamento automático às 03:00), validações acumuladas no Windows, pendências do usuário. Leia antes de planejar ou rever etapas.
- [[ZenyHotelManager-DesktopFront - Processo de execução (ADRs 0011 e 0012)]]: processo acelerado, revogação e dívida de revisão (M3 E06). Leia antes de executar uma etapa.

## Atualização por capturas

O repositório não tem o hook `load-brain.py` (sem `.claude/settings.json` na `main`), então este hub não é injetado nas sessões do front. As capturas chegam pelo `brain-escriba`, a pedido do `arquiteto` ou do orquestrador, com o nome `ZenyHotelManager-DesktopFront - …`. Os pedidos ao servidor chegam como `ZenyHotelManager - pedido do front PF-NN …` e são integrados nas notas do servidor. O curador integra as capturas nas notas de tema e no Estado deste hub.

## Próximos passos

- Usuário: executar no Windows a lista "Validações acumuladas no Windows" (M0 E02, M2 E06, M0 E03 e M3 E05) com o `roteiro-m3.md` e o pacote mais recente.
- `orquestrador`: revisão final da M3 E06 e marca de paga na lista "Revisões de segurança adiadas"; depois, o M4.
- Antes de cada marco: rodada do M0 se a `main` do servidor avançou (regra 3 de `docs/roadmaps/README.md`).

## Perguntas abertas

- Registro do projeto pela skill `development-roadmap` e instalação do hook: não feitos. Este hub foi criado pelo curador em 2026-11-17, ao processar as capturas do front a pedido do usuário.
- O `load-brain.py` ainda casa as capturas pendentes por substring: capturas `ZenyHotelManager-DesktopFront - …` aparecem nas sessões do servidor. A troca por prefixo altera uma skill do vault e aguarda pedido do usuário.
- Regra dos pedidos `PF-NN` no servidor: nenhum documento do servidor cita "PF-NN".
- Aviso do servidor ainda fora da `main` dele (M6 E18, só na branch `roadmap/m6-operacao-fechamento`): `""` em data ou instante opcional passará a dar `400 INVALID_FORMAT`. Só chega ao front quando entrar na `main` do servidor e numa rodada do M0.
- Meta de 3 a 4 etapas em 4 a 6 horas por rodada no ciclo novo das souls: projeção, ainda não medida neste repositório.

## Conhecimento relacionado

- [[ZenyHotelManager]]: servidor, fonte da verdade do contrato e destino dos pedidos `PF-NN`.
- [[Decidir pendências do usuário por entrevista com opção recomendada]]: método das decisões dos ADRs 0009, 0010 e 0012.
- [[Souls - alma personalizada para cada agente de desenvolvimento]]: fluxo das souls que executa os roadmaps.
- [[ZenyProjectHandler - Execução acelerada do roadmap de leitura vetorial]]: outro caso de execução acelerada; a comparação é interpretação do agente da captura do ADR 0011.

## Proveniência

- 2026-11-17 — [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]] (capture_id: 16d5b400-b2e5-490e-b063-b61b40c14257): objetivo, repositório e índice; nota criada pelo curador ao processar a Inbox do front a pedido do usuário.
- 2026-11-17 — [[2026-11-13 - ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão - 677b277a]] (capture_id: 677b277a-44a4-4da4-8214-4dfca2edc865): ADR 0009 e rodada 2 do M0 (texto nas notas de tema).
- 2026-11-17 — [[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]] (capture_id: 5bba7217-6f3f-460d-8b80-ace44d5b8683): ADR 0010 e rodada 3 do M0 (texto nas notas de tema).
- 2026-11-17 — [[2026-11-16 - ZenyHotelManager-DesktopFront - ADR 0011 processo acelerado até a demo - 0cc1844e]] (capture_id: 0cc1844e-038a-4163-83d7-abbb4b4c6ffd): processo acelerado (texto na nota de processo).
- 2026-11-17 — [[2026-11-17 - ZenyHotelManager-DesktopFront - ADR 0012 revoga o processo acelerado e atualização dos roadmaps - 10b921ef]] (capture_id: 10b921ef-c99f-44a2-a0ac-77ac16591dbe): revogação, M3 E06 e Estado; conferência por `git` do curador.
