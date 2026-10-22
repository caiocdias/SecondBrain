---
type: project
created: 2026-10-22
aliases:
  - "Zeny Hotel Manager"
sources:
  - "[[2026-10-22 - ZenyHotelManager - migração do CLAUDE.md para o brain - índice e decisões - 03d0ed3e]]"
  - "[[2026-10-22 - ZenyHotelManager - atualização migração do CLAUDE.md fase 2 - cad5c5ad]]"
  - "[[2026-10-22 - ZenyHotelManager - hook compartilhado do brain - e26f9f6f]]"
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
- A referência técnica saiu do `CLAUDE.md` do repositório para as notas abaixo (decisão do usuário, 2026-10-22). Migração concluída em 2026-10-22, ainda sem commit no repositório: `CLAUDE.md` enxuto (59 linhas) e hook ativo em `.claude/settings.json` (`SessionStart` e `SubagentStart`), que roda o `load-brain.py` compartilhado da skill `development-roadmap` com o argumento `ZenyHotelManager` e exige a linha `BRAIN: carregado (ZenyHotelManager)`. Testado numa sessão real e num subagente.
- Os roadmaps M6 a M10 ainda citam o `CLAUDE.md`; até a sincronização de cada um, vale a regra de mapeamento de `docs/roadmaps/README.md` (regra 3): "seção X do `CLAUDE.md`" é a nota de tema e "atualizar o `CLAUDE.md`" é publicar a captura de atualização.

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

Decisão do usuário (2026-10-22). Sessões no repositório são agentes externos do vault: não editam estas notas. Ao fim de cada etapa do roadmap, publique em `00 Inbox/` uma captura "ZenyHotelManager - atualização Mx Ey" com o texto novo ou alterado, dizendo qual nota de tema ele afeta. O hook lista as capturas pendentes do projeto; leia-as, pois valem sobre estas notas quando tratam do mesmo assunto. O curador as integra nas notas de tema e no Estado deste hub.

## Próximos passos

- Commit das alterações da migração no repositório (`CLAUDE.md`, `README.md`, `.claude/settings.json` e roadmaps), a cargo do usuário.
- Na sincronização de cada roadmap de M6 a M10, trocar as menções ao `CLAUDE.md` pelas notas de tema e pela captura de atualização.

## Perguntas abertas

- O comando do hook (`python3` e shell POSIX) ainda não foi testado no Windows.

## Conhecimento relacionado

- [[Decidir pendências do usuário por entrevista com opção recomendada]]: método das decisões do projeto e desta migração.

## Proveniência

- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - migração do CLAUDE.md para o brain - índice e decisões - 03d0ed3e]] (capture_id: 03d0ed3e-788d-43f3-b338-79e3077d799f): objetivo do projeto (texto literal do `CLAUDE.md`, linhas 7–13), decisões do usuário sobre a migração, fluxo de atualização por capturas, passos da fase 2 e perguntas abertas. Nota criada a pedido do usuário ("vamos criar um projeto no /second-brain").
- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - Estado por marco - 00f871ac]] (capture_id: 00f871ac-9fce-4291-9d71-47a67a2f69b7): resumo do curador do estado atual; o texto completo está em [[ZenyHotelManager - Estado por marco]].
- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - atualização migração do CLAUDE.md fase 2 - cad5c5ad]] (capture_id: cad5c5ad-9bf0-4d98-890f-641ae8d1f7ca): fase 2 concluída (`CLAUDE.md` enxuto, hook ativo e testado em sessão e subagente, regra de mapeamento nos roadmaps); Estado, Próximos passos e Perguntas abertas atualizados.
- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - hook compartilhado do brain - e26f9f6f]] (capture_id: e26f9f6f-f541-4339-bc7d-b74de3e5599f): troca para o `load-brain.py` compartilhado da skill `development-roadmap` e a linha `BRAIN: carregado (ZenyHotelManager)`; retirada a pergunta aberta sobre a skill, já atendida.
