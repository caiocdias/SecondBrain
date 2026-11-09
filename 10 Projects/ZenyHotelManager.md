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
- `docs/ARCHITECTURE.md`: **como** (decisões D1–D19 §2, módulos §3, API §7, segurança §8, offline §9, persistência §11, integrações §12).
- `docs/roadmaps/`: `README.md` com os 11 marcos (M0–M10) e um `roadmap-mN-*.md` por marco.

Documentação, mensagens ao usuário e commits em pt-BR; código, API e banco em inglês (D17).

## Estado

- M0 a M4 concluídos, registro histórico (não se executam e seguem acusando erro de formato no verificador). M5 em andamento, 16 etapas: E01 a E07, E13 e E14 concluídas. Ordem seguinte: E15, E08, E16 e E10; E09 `#bloqueada` (Q-12), depende de E08 e E16. Revisão humana de E13 e E07 pendente. M6 a M10 replanejados em 2026-11-06. Detalhes em [[ZenyHotelManager - Estado por marco]].
- Conferido por `git` em 2026-11-09, sem captura: **E15 `#em-andamento`, interrompida** na branch `roadmap/m5-recepcao-fnrh` (ponta `e718190`, ponto de retomada no roadmap dessa branch). `main` local em `ca9f9e2` (E14 e E07); `origin/main` em `15bbcdb` pela referência local (push do usuário).
- Referência técnica no brain desde 2026-10-22 (decisão do usuário), ainda sem commit no repositório: `CLAUDE.md` enxuto e hook em `.claude/settings.json` (`SessionStart` e `SubagentStart`) com o `load-brain.py` da skill `development-roadmap`, que exige `BRAIN: carregado (ZenyHotelManager)`. Testado em sessão real e em subagente.
- Roadmaps M5 a M10 no formato da skill `development-roadmap` com o superpowers, revistos em 2026-11-06 (`docs/superpowers/specs/2026-11-06-revisao-arquitetura-roadmaps-design.md`, ainda sem commit). Executam pelas souls do Second Brain: `claude --agent arquiteto` desenha e revê (spec, ARCHITECTURE, roadmaps), sem código nem plano; `claude --agent orquestrador` escreve o plano de cada etapa, submete-o ao `revisor-arquitetura` e executa: `desenvolvedor` → `testador` (por risco) → verificação mecânica → `revisor-seguranca` e captura pelo `brain-escriba`.
- Dependências travadas por lockfiles em modo estrito (E13), conferidos pela CI, e 0 Critical/High no `osv-scanner` (E14): ver [[ZenyHotelManager - Ambiente, banco, chaves e build]] antes de mexer em dependências.
- Git (decisão do usuário, 2026-11-06): a execução de roadmap roda na branch `roadmap/<slug>`; no fim do lote, com o gate verde, o orquestrador faz o merge local na `main` e deixa pronto o `git push origin main`. Push e deploy são sempre do usuário. Fora do roadmap, commit só a pedido.

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
- [[ZenyHotelManager - Hospedagem e recepção]]: transições de hospedagem e `frontdesk` (check-in, walk-in, check-out, troca de UH, early, recados).
- [[ZenyHotelManager - Módulo fnrh]]: FNRH/Serpro: configuração, porta e adaptador, falhas, saneador, validador. Leia antes das E08 e E09.

## Atualização por capturas

Decisão do usuário (2026-10-22). Sessões no repositório são agentes externos do vault: não editam estas notas. No fechamento de cada etapa que muda algo descrito no brain, inclusive o estado, o orquestrador do lote publica em `00 Inbox/` a captura `ZenyHotelManager - atualização <slug> Eyy` (ex.: `atualização m5-recepcao-fnrh E04`) com o texto novo ou alterado, dizendo qual nota de tema ele afeta. Módulos novos (fnrh, printing, housekeeping, fiscal, pos etc.) ganham nota `ZenyHotelManager - Módulo <nome>`. O hook lista as capturas pendentes do projeto; leia-as, pois valem sobre estas notas quando tratam do mesmo assunto. O curador as integra nas notas de tema e no Estado deste hub.

## Próximos passos

- Commit das alterações no repositório (`CLAUDE.md`, `README.md`, `.claude/settings.json` e roadmaps) e das da revisão de 2026-11-06, a cargo do usuário.
- Executar E15, E08, E16 e E10 do M5 pelo `claude --agent orquestrador`.
- M6 começa pelas E10 e E11: fechamento com a chave do check-out (nota obrigatória em [[ZenyHotelManager - Módulo billing (contas, roteamento e taxa de serviço)]]).
- Homologação da FNRH (M5 E09): fora do gate do M5, cobrada pelo gate de inauguração (M8 E13).
- Sincronizar cada roadmap de M6 a M10 com o código antes do primeiro lote (regra 2 de `docs/roadmaps/README.md`); divergências já vistas estão nas "Notas para o plano".

## Perguntas abertas

- O comando do hook (`python3` e shell POSIX) ainda não foi testado no Windows.
- Sem confirmação do usuário, decididas pela opção recomendada: lotes M5 E04 a E06 (lista em [[ZenyHotelManager - Hospedagem e recepção]]), E13 (a–f), E14 (a–c) e E07 ((a) a (d), (f), (g), (h), (j)), mais a revisão humana de E13 e E07, que o gate M8 E13 exige. Lista em [[ZenyHotelManager - Estado por marco]]. O risco aceito do `opentelemetry-api` 1.62.0 tem etapa dona, a M8 E17.
- Decisões do arquiteto R7 a R13 e R16: revisáveis, não passaram pela entrevista.
- Dividir o M8 (18 etapas) em dois arquivos: oferecido, não aplicado.
- Q-07 (retenção) no padrão da SPEC até confirmação; fornecedores e hospedagem (Q-05, Q-06, Q-02, Q-03, Q-13) seguem do usuário, com as etapas afetadas `#bloqueada`.

## Conhecimento relacionado

- [[Decidir pendências do usuário por entrevista com opção recomendada]]: método das decisões do projeto e desta migração.

## Proveniência

- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - migração do CLAUDE.md para o brain - índice e decisões - 03d0ed3e]] (capture_id: 03d0ed3e-788d-43f3-b338-79e3077d799f): objetivo (literal do `CLAUDE.md`), decisões da migração e fluxo por capturas; nota criada a pedido do usuário.
- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - Estado por marco - 00f871ac]] (capture_id: 00f871ac-9fce-4291-9d71-47a67a2f69b7): resumo do estado; texto completo em [[ZenyHotelManager - Estado por marco]].
- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - atualização migração do CLAUDE.md fase 2 - cad5c5ad]] (capture_id: cad5c5ad-9bf0-4d98-890f-641ae8d1f7ca): fase 2 concluída e testada (Estado, Próximos passos, Perguntas abertas).
- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - hook compartilhado do brain - e26f9f6f]] (capture_id: e26f9f6f-f541-4339-bc7d-b74de3e5599f): hook compartilhado da skill `development-roadmap` e linha `BRAIN: carregado`.
- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - atualização roadmaps M5 a M10 no formato superpowers - d76e6324]] (capture_id: d76e6324-2c69-45d7-b242-d274e8c8ac2e): roadmaps M5 a M10 no formato superpowers e regras de branch e capturas.
- 2026-10-23 — [[2026-10-23 - ZenyHotelManager - atualização m5-recepcao-fnrh integração E04 a E06 - b2046daa]] (capture_id: b2046daa-2cdb-4680-ae03-6f388769bca4): Estado do M5 após E04 a E06 (as capturas dessas etapas estão nas notas de tema).
- 2026-11-04 — [[2026-10-28 - ZenyHotelManager - atualização m5-recepcao-fnrh E13 - 7a6ce25a]] (capture_id: 7a6ce25a-b05d-40ab-88c0-e459a9c329ca): Estado do M5 após a E13 e decisões do lote (Perguntas abertas).
- 2026-11-04 — [[2026-11-04 - ZenyHotelManager - atualização m5-recepcao-fnrh E14 - f8103233]] (capture_id: f8103233-d5b2-48b1-b302-c9360ff5b66b): Estado do M5 após a E14 e decisões do lote (Perguntas abertas).
- 2026-11-09 — [[2026-11-05 - ZenyHotelManager - atualização m5-recepcao-fnrh E07 - 9f02405c]] (capture_id: 9f02405c-a73b-44f0-8f8c-5fb75860aa05): Estado do M5 após a E07, índice do módulo `fnrh` e decisões do lote.
- 2026-11-09 — [[2026-11-06 - ZenyHotelManager - atualização revisão de arquitetura dos roadmaps - c889f886]] (capture_id: c889f886-0719-4f28-984e-f2ef23ed9520): Estado, Git, Próximos passos e Perguntas abertas após a revisão dos roadmaps.
