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

- M0 a M4 concluídos. M5 concluído em 2026-11-12 (gate E12, merge `ab8b406`), salvo a E09 `#bloqueada` (Q-12, cobrada no M8 E13). M6 (18 etapas): E01, E10, E11 e E14 a E18 `#concluida`, demais `#pendente`; E18 e E01 só na branch do M6, sem merge na `main`. Detalhes em [[ZenyHotelManager - Estado por marco]].
- Referência técnica no brain desde 2026-10-22 (decisão do usuário), carregada pelo hook `load-brain.py`, que exige `BRAIN: carregado (ZenyHotelManager)`.
- Roadmaps M5 a M10 no formato da skill `development-roadmap`, executados com `claude --agent`: `arquiteto` desenha e revê, `orquestrador` planeja e executa.
- Dependências: lockfiles estritos e `osv-scanner` sem Critical/High; leia [[ZenyHotelManager - Ambiente, banco, chaves e build]] antes de mexer nelas.
- Git (decisão do usuário, 2026-11-06): roadmap na branch `roadmap/<slug>`; no fim do lote, com o gate verde, merge local na `main` pelo orquestrador. Push e deploy são sempre do usuário; fora do roadmap, commit só a pedido.

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
- [[ZenyHotelManager - Módulo fnrh]]: FNRH/Serpro: configuração, porta e adaptador, falhas, saneador, validador, envio assíncrono (E08, padrão de M7 e M8), no-show (M6 E14). Leia antes da E09.
- [[ZenyHotelManager - Módulo printing]]: agentes, impressoras, fila, token e documentos (E11). Leia antes de criar um documento.
- [[ZenyHotelManager - Módulo endofday]]: fechamento do dia: motor, as 8 etapas (E11), pendências, gatilho.
- [[ZenyHotelManager - Módulo housekeeping]]: governança: tipos de limpeza, créditos, faxinas programadas (M6 E01). Leia antes da E02.

## Atualização por capturas

Decisão do usuário (2026-10-22). Sessões no repositório são agentes externos do vault: não editam estas notas. No fechamento de cada etapa que muda algo descrito no brain, inclusive o estado, o orquestrador do lote publica em `00 Inbox/` a captura `ZenyHotelManager - atualização <slug> Eyy` com o texto novo ou alterado, dizendo qual nota de tema ele afeta. Módulos novos (housekeeping, fiscal, pos etc.) ganham nota `ZenyHotelManager - Módulo <nome>`. O hook lista as capturas pendentes do projeto; leia-as, pois valem sobre estas notas quando tratam do mesmo assunto. O curador as integra nas notas de tema e no Estado deste hub. Decisão do usuário (2026-11-17): o desenvolvimento segue em outra máquina a partir da `main`; em conflito de informação, as capturas vindas dela valem sobre o que estas notas trazem das branches locais antigas (M6 E18 e E01), que não foi retirado.

## Próximos passos

- Revisão humana da M6 E11 (usuário); M6 (`orquestrador`): E02 e demais; `arquiteto`: manutenção do `fnrh` e pendências da E14 a E16, da E18 e da E01 (Estado por marco).
- Avisar o front desktop (M6 E18): `""` em data ou instante opcional agora dá `400 INVALID_FORMAT`.
- Sincronizar M7 a M10 com o código antes do primeiro lote de cada um (regra 2 de `docs/roadmaps/README.md`; divergências nas "Notas para o plano").

## Perguntas abertas

- O comando do hook (`python3` e shell POSIX) ainda não foi testado no Windows.
- Sem confirmação do usuário (opção recomendada): decisões dos lotes do M5 e do M6, H10 e H13 do `arquiteto` e revisão humana de E13 e E07 do M5 (lista em [[ZenyHotelManager - Estado por marco]]). Risco aceito do `opentelemetry-api` 1.62.0: M8 E17. R7 a R13 e R16 do arquiteto: revisáveis.
- Dividir o M8 (18 etapas) em dois arquivos: oferecido, não aplicado.
- Pedidos abertos do front desktop ([[ZenyHotelManager-DesktopFront]]), sem decisão do servidor: PF-01 (setores para recados) e PF-02 (aprovação no histórico do desfazer check-in), em [[ZenyHotelManager - Hospedagem e recepção]]; PF-03 (trocar titular e hóspedes antes do check-in) e PF-04 (prévia da multa de cancelamento), em [[ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)]].
- Q-07 (retenção) no padrão da SPEC até confirmação; fornecedores e hospedagem (Q-05, Q-06, Q-02, Q-03, Q-13) seguem do usuário, com as etapas afetadas `#bloqueada`.

## Conhecimento relacionado

- [[Decidir pendências do usuário por entrevista com opção recomendada]]: método das decisões do projeto e desta migração.
- [[ZenyHotelManager-DesktopFront]]: front desktop, cliente do contrato; fixa um commit da `main` e pede pelo brain (`PF-NN`).

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
- 2026-11-10 — [[2026-11-10 - ZenyHotelManager - atualização m5-recepcao-fnrh E15 - a22890e7]] (capture_id: a22890e7-e6b1-4e99-97d7-747bfcdd5788): Estado do M5 após a E15, Próximos passos e decisões do lote (Perguntas abertas); conferência por `git` do curador.
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]] (capture_id: 8df87866-4285-4e24-8878-0fab70c9436c): Estado, Próximos passos e decisões do lote E08.
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 (revisão humana) - 65d0d4ff]] (capture_id: 65d0d4ff-bc24-4f40-94ba-c062bdf2b9c1): revisão humana da E08 feita e E15 (h) decidida pelo usuário.
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E16 - 6095f729]] (capture_id: 6095f729-34e7-4667-9c48-d112262c6212): Estado e decisões da E16.
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 - 4dd12e66]] (capture_id: 4dd12e66-191b-406d-a974-4ae7dca3e15f): Estado, Próximos passos, decisões do lote E10 e índice do `printing`.
- 2026-11-15 — [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 (revisão humana) - 25b5cce4]] (capture_id: 25b5cce4-a919-4cf3-aaaf-99b5722239e8): revisão humana da E10 e merge.
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E11 - d1100f5a]] (capture_id: d1100f5a-58df-416a-b523-1db1d3eb3f19): Estado e Próximos passos após a E11.
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E11 (revisão humana) - cca61b94]] (capture_id: cca61b94-000c-4d38-9f81-59e12c1d9f99): revisão humana da E11 e merge.
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 - 2c135bbf]] (capture_id: 2c135bbf-8248-4987-a617-dcb3fa94c0a5): gate E12 do M5.
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 (revisão humana) - 64ce6698]] (capture_id: 64ce6698-9d2c-4a1c-b4d0-af930d24bff5): decisões (e) e (f) da E12.
- 2026-11-15 — [[2026-11-12 - ZenyHotelManager - atualização arquitetura e sincronização do M6 - 3a747cdc]] (capture_id: 3a747cdc-6309-4bfa-bea2-3f6cd483a30f): M6 sincronizado.
- 2026-11-15 — [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]] (capture_id: 1e4f709b-7bbd-4c39-9725-1926aef1ca98): M6 E10 e índice do `endofday`.
- 2026-11-15 — [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 (revisão humana) - fa5b192f]] (capture_id: fa5b192f-13a0-4e35-959a-3134613a24d8): revisão humana da E10 (H12) e merge.
- 2026-11-15 — [[2026-11-13 - ZenyHotelManager - atualização roadmap M6 manutenção transversal - 009e3130]] (capture_id: 009e3130-5bd9-4e8b-bd56-81c7fc440b81): E18 do M6 (H13).
- 2026-11-15 — [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E11 - df23f14d]] (capture_id: df23f14d-ec3c-4fa2-aa75-462913ddaf5e): M6 E11.
- 2026-11-15 — [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E14 - 998156dc]] (capture_id: 998156dc-c51d-47f2-ad9c-86f204f7236c): M6 E14.
- 2026-11-15 — [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E15 - c139da21]] (capture_id: c139da21-4f16-40bc-8cae-9ee2dc4444c3): M6 E15.
- 2026-11-15 — [[2026-11-14 - ZenyHotelManager - atualização m6-operacao-fechamento E16 - f7e211bd]] (capture_id: f7e211bd-3d35-495d-87c3-33a791c87e48): M6 E16.
- 2026-11-15 — [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E17 - cb3979d0]] (capture_id: cb3979d0-82db-4bb4-bf98-0a7b8630e398): M6 E17.
- 2026-11-15 — [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E17 (revisão humana) - 4ab01eb7]] (capture_id: 4ab01eb7-f60b-483f-8ae1-66de5753d21c): revisão humana da E17.
- 2026-11-15 — [[2026-11-15 - ZenyHotelManager - atualização arquitetura §7 resposta que varia com a permissão - 77927cd7]] (capture_id: 77927cd7-51b9-4718-b108-048c262be5c7): `oneOf` na §7.
- 2026-11-15 — [[2026-11-15 - ZenyHotelManager - pedido do front PF-01 Setores dos recados legíveis com frontdesk.traces.manage - 324e0e8f]] (capture_id: 324e0e8f-f656-496a-b6a8-446fe491e384): PF-01.
- 2026-11-16 — [[2026-11-15 - ZenyHotelManager - pedido do front PF-02 Histórico do desfazer check-in com a aprovação do superior - b6c7bc32]] (capture_id: b6c7bc32-8f7c-4952-85c0-7e210f2b7f81): PF-02.
- 2026-11-16 — [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E18 - a68d398b]] (capture_id: a68d398b-2037-4b20-af27-8039b163ae0e): M6 E18.
- 2026-11-16 — [[2026-11-16 - ZenyHotelManager - atualização m6-operacao-fechamento E01 - dd5e01e3]] (capture_id: dd5e01e3-3041-431b-81f8-3b801eec3fff): M6 E01 e índice do `housekeeping`.
- 2026-11-17 — [[2026-11-17 - ZenyHotelManager - pedido do front PF-03 Trocar o titular e os hóspedes de uma reserva antes do check-in - 24803598]] (capture_id: 24803598-810b-4344-997b-c28c79463e5c): PF-03.
- 2026-11-17 — [[2026-11-17 - ZenyHotelManager - pedido do front PF-04 Prévia da multa de cancelamento da reserva - 8f737e26]] (capture_id: 8f737e26-5881-45fe-85ec-163b1285ac0a): PF-04.
