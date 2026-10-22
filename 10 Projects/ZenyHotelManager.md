---
type: project
created: 2026-10-22
aliases:
  - "Zeny Hotel Manager"
sources:
  - "[[2026-10-22 - ZenyHotelManager - migração do CLAUDE.md para o brain - índice e decisões - 03d0ed3e]]"
  - "[[2026-10-22 - ZenyHotelManager - atualização migração do CLAUDE.md fase 2 - cad5c5ad]]"
  - "[[2026-10-22 - ZenyHotelManager - hook compartilhado do brain - e26f9f6f]]"
  - "[[2026-10-22 - ZenyHotelManager - atualização roadmaps M5 a M10 no formato superpowers - d76e6324]]"
---
# ZenyHotelManager

## Objetivo

Servidor do Zeny Hotel Manager: PMS e operações de **um único hotel** de até 30 UHs. O repositório contém **só o servidor**. Os clientes (desktop, mobile, PDV, tela de produção e agente de impressão) ficam em outros repositórios e geram seus SDKs a partir do contrato OpenAPI.

Repositório local: `/home/caio/repos/ZenyHotelManager`.

- `docs/SPEC.md`: **o quê** (requisitos `RF-<MÓDULO>-NN`, regras `RN-NN`, domínio §8, fases §9, questões `Q-NN` §10).
- `docs/ARCHITECTURE.md`: **como** (decisões D1–D17 §2, módulos §3, API §7, segurança §8, offline §9, persistência §11, integrações §12).
- `docs/roadmaps/`: `README.md` com os 11 marcos (M0–M10) e um `roadmap-mN-*.md` por marco.

Documentação, mensagens ao usuário e commits em pt-BR; código, API e banco em inglês (D17).

## Estado

- M0 a M4 concluídos. M5 em andamento: E01 a E03 concluídas (até o walk-in, commit `a6c0f03`, 2026-10-22). Histórico completo em [[ZenyHotelManager - Estado por marco]].
- Referência técnica no brain desde 2026-10-22 (decisão do usuário), ainda sem commit no repositório: `CLAUDE.md` enxuto e hook em `.claude/settings.json` (`SessionStart` e `SubagentStart`) com o `load-brain.py` da skill `development-roadmap`, que exige `BRAIN: carregado (ZenyHotelManager)`. Testado em sessão real e em subagente.
- Roadmaps M5 a M10 no formato da skill `development-roadmap` com o superpowers (protocolo, bloco "Second Brain" e um "Prompt de execução" por roadmap); M0 a M4 ficaram no formato antigo. Próxima etapa: M5 E04, pelo prompt de `roadmap-m5-recepcao-fnrh.md`. Nenhum lote rodou ainda no formato novo.
- Git (decisão do usuário): a execução de roadmap roda na branch `roadmap/<slug>`, com commits por tarefa do superpowers; merge, PR e push só com a decisão do usuário no fim do lote. Fora do roadmap: trabalhar na `main`, commit só a pedido.

## Notas do projeto

Ficam em `20 Knowledge/` do vault (arquivo = nome do link + `.md`). Leia a nota do tema antes de mexer no código dele. Menções a uma "seção" do antigo `CLAUDE.md` estão nestas notas (busque o título).

Base e plataforma:

- [[ZenyHotelManager - Arquitetura e estrutura de módulos]]: estrutura de um módulo, testes de arquitetura e a arquitetura em uma página. Leia antes de criar módulo ou dependência.
- [[ZenyHotelManager - Ambiente, banco, chaves e build]]: profiles, papéis do banco, chaves JWT e de cifragem, administrador inicial, Gradle.
- [[ZenyHotelManager - Schemas, migrações e views de relatório]]: schemas, migrações Flyway, privilégios, append-only, views `report_*`.
- [[ZenyHotelManager - Tipos do kernel]]: Money, Percent, IDs, CPF/CNPJ, cifragem, índice cego, ator corrente, Clock.
- [[ZenyHotelManager - Convenções de API]]: controllers, erros RFC 9457, paginação, concorrência, idempotência, OpenAPI.
- [[ZenyHotelManager - Segurança, autenticação e autorização]]: `iam`, permissões, escopos, limites, aprovação de superior.
- [[ZenyHotelManager - Auditoria]]: `@Audited`, retratos mascarados, trilha.
- [[ZenyHotelManager - Eventos e jobs]]: outbox, listeners, ShedLock.
- [[ZenyHotelManager - Tempo real (SSE)]]: `/api/v1/stream`, tópicos e protocolo.
- [[ZenyHotelManager - Sincronização offline]]: cursor, tombstones, comandos por `commandId`.
- [[ZenyHotelManager - Testes de integração]]: `@IntegrationTest`, containers, relógio.
- [[ZenyHotelManager - Docker, observabilidade e CI]]: imagem, compose, actuator, logs, métricas, CI.

Módulos:

- [[ZenyHotelManager - Módulos hotel e staff]]: hotel, data operacional, políticas, escala.
- [[ZenyHotelManager - Módulo files]]: anexos, upload, download assinado, expurgo.
- [[ZenyHotelManager - Módulo rooms]]: UHs, áreas, status, OOO/OOS.
- [[ZenyHotelManager - Módulo checklists]]: modelos, execução, rotinas, fotos.
- [[ZenyHotelManager - Módulo notifications]]: `notify`, preferências, painel, FCM.
- [[ZenyHotelManager - Módulo guests]]: perfis, documentos, dados sensíveis, LGPD, empresas.
- [[ZenyHotelManager - Módulo billing (contas, roteamento e taxa de serviço)]]: contas, lançamentos, roteamento, taxa de serviço.
- [[ZenyHotelManager - Módulo billing (caixa, pagamentos, caução e encerramento)]]: caixa, `payments`, caução, encerramento, extrato.
- [[ZenyHotelManager - Módulo rates]]: planos, políticas, preços, temporadas, restrições.
- [[ZenyHotelManager - Módulo reservations (inventário, disponibilidade e reservas)]]: inventário, calendário, cotação, criação.
- [[ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)]]: alteração, cancelamento, garantia, alocação, grupos, busca.
- [[ZenyHotelManager - Hospedagem e recepção]]: transições de hospedagem e `frontdesk` (check-in, walk-in).

## Atualização por capturas

Decisão do usuário (2026-10-22). Sessões no repositório são agentes externos do vault: não editam estas notas. No fechamento de cada etapa que muda algo descrito no brain, inclusive o estado, o orquestrador do lote publica em `00 Inbox/` a captura `ZenyHotelManager - atualização <slug> Eyy` (ex.: `atualização m5-recepcao-fnrh E04`) com o texto novo ou alterado, dizendo qual nota de tema ele afeta. Módulos novos (fnrh, printing, housekeeping, fiscal, pos etc.) ganham nota `ZenyHotelManager - Módulo <nome>`. O hook lista as capturas pendentes do projeto; leia-as, pois valem sobre estas notas quando tratam do mesmo assunto. O curador as integra nas notas de tema e no Estado deste hub.

## Próximos passos

- Commit das alterações no repositório (`CLAUDE.md`, `README.md`, `.claude/settings.json` e roadmaps), a cargo do usuário.
- Sincronizar cada roadmap de M6 a M10 com o código antes do primeiro lote (regra 2 de `docs/roadmaps/README.md`); divergências já vistas estão nas "Notas para o plano".

## Perguntas abertas

- O comando do hook (`python3` e shell POSIX) ainda não foi testado no Windows.

## Conhecimento relacionado

- [[Decidir pendências do usuário por entrevista com opção recomendada]]: método das decisões do projeto e desta migração.

## Proveniência

- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - migração do CLAUDE.md para o brain - índice e decisões - 03d0ed3e]] (capture_id: 03d0ed3e-788d-43f3-b338-79e3077d799f): objetivo do projeto (texto literal do `CLAUDE.md`, linhas 7–13), decisões do usuário sobre a migração, fluxo de atualização por capturas, passos da fase 2 e perguntas abertas. Nota criada a pedido do usuário ("vamos criar um projeto no /second-brain").
- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - Estado por marco - 00f871ac]] (capture_id: 00f871ac-9fce-4291-9d71-47a67a2f69b7): resumo do curador do estado atual; o texto completo está em [[ZenyHotelManager - Estado por marco]].
- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - atualização migração do CLAUDE.md fase 2 - cad5c5ad]] (capture_id: cad5c5ad-9bf0-4d98-890f-641ae8d1f7ca): fase 2 concluída e testada (Estado, Próximos passos, Perguntas abertas).
- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - hook compartilhado do brain - e26f9f6f]] (capture_id: e26f9f6f-f541-4339-bc7d-b74de3e5599f): hook compartilhado da skill `development-roadmap` e linha `BRAIN: carregado`.
- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - atualização roadmaps M5 a M10 no formato superpowers - d76e6324]] (capture_id: d76e6324-2c69-45d7-b242-d274e8c8ac2e): roadmaps M5 a M10 no formato superpowers, decisões sobre branch e nome das capturas, próxima etapa.
