---
type: knowledge
status: processed
created: 2026-11-17
projects:
  - "[[ZenyHotelManager-DesktopFront]]"
sources:
  - "[[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]]"
  - "[[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]]"
  - "[[2026-11-17 - ZenyHotelManager-DesktopFront - ADR 0012 revoga o processo acelerado e atualização dos roadmaps - 10b921ef]]"
---
# ZenyHotelManager-DesktopFront - Marcos, roadmaps e demo

Referência do projeto [[ZenyHotelManager-DesktopFront]]: marcos M0 a M7, regras dos roadmaps que afetam a demo, mudanças por rodada e pendências do usuário. O estado resumido fica no hub; a fonte da verdade é `docs/roadmaps/` do repositório. Leia antes de planejar ou rever etapas.

Texto das capturas do `brain-escriba` (resumos do agente feitos a partir dos documentos do repositório), integrado sem resumo nem reescrita; cada bloco indica a captura de origem. A fonte da verdade são os arquivos do repositório `/home/caio/repos/ZenyHotelManager-DesktopFront`. As notas do curador estão marcadas como tal.

## Marcos e roadmaps (2026-11-10)

Origem: [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]]. A contagem de etapas desta tabela é a de 2026-11-10; a atual está em "Mapa atual", abaixo.

Mapa em `docs/roadmaps/README.md`; cada marco tem `docs/roadmaps/roadmap-mN-<slug>.md`.

| Marco | Nome | Etapas | Roadmap |
|---|---|---|---|
| M0 | Sincronização com o servidor (repete a cada avanço do servidor) | 1 por rodada | `roadmap-m0-sincronizacao.md` |
| M1 | Fundação e mapa de UHs ao vivo | 7 | `roadmap-m1-fundacao.md` |
| M2 | Recepção do dia | 6 | `roadmap-m2-recepcao-do-dia.md` |
| M3 | Reservas | 5 | `roadmap-m3-reservas.md` |
| M4 | Contas, caixa e check-out | 5 | `roadmap-m4-contas-caixa-checkout.md` |
| M5 | Hóspedes e empresas | 5 | `roadmap-m5-hospedes-empresas.md` |
| M6 | Governança e operação | 7 | `roadmap-m6-governanca-operacao.md` |
| M7 | Gestão e cadastros | 11 | `roadmap-m7-gestao-cadastros.md` |

- Cada marco termina numa build testável conectada ao servidor (JAR do app, `demo-seed` e roteiro de demo acumulado em `docs/demo/roteiro-mN.md`), com gate `Revisão humana: sim`; o usuário faz um gate por dia.
- O M0 tem duas partes: análise (`claude --agent arquiteto` com `development-roadmap` em modo atualização) e mecânica (etapa do orquestrador). A M0 E01 cria o mecanismo e vem antes da M1.
- Se 17/11 chegar no meio de um marco, a demo usa a build do último gate concluído. Risco declarado no design: M6 e M7 provavelmente não ficam prontos até 17/11.
- Regras gerais: um marco por vez; pré-voo em toda execução; repositório do servidor só leitura; push e deploy ficam com o usuário (execução commita em `roadmap/<slug>` e faz merge local na `main`).

## Mapa atual dos marcos

*Nota do curador (conferência por `git` em 2026-11-17, só leitura, na `main` do front em `6ffc9f3`; tabela de `docs/roadmaps/README.md` e tags dos títulos das etapas em cada roadmap):*

| Marco | Nome | Etapas | Depende de | Tags das etapas |
|---|---|---|---|---|
| M0 | Sincronização com o servidor | 1 por rodada | — | E01 `#concluida`; E02 e E03 `#em-andamento` (aguardando o Windows) |
| M1 | Fundação e mapa de UHs | 7 | M0 E01 | E01 a E07 `#concluida` |
| M2 | Recepção do dia | 7 | M1 e M0 E02 | E01 a E05 e E07 `#concluida`; E06 (gate) `#em-andamento` (aguardando o Windows) |
| M3 | Reservas | 6 | M2 e M0 E03 | E01 a E04 `#concluida`; E05 (gate) e E06 (revisão adiada) `#em-andamento` |
| M4 | Contas, caixa e check-out | 5 | M3, com a E06 | todas `#pendente` |
| M5 | Hóspedes e empresas | 5 | M4 | todas `#pendente` |
| M6 | Governança e operação | 8 | M5 | todas `#pendente` |
| M7 | Gestão e cadastros | 12 | M6 | todas `#pendente` |

- Regra 7 do README (validação no Windows acumulada, decisão do usuário de 2026-11-13, estendida em 2026-11-15): a lista "Validações acumuladas no Windows" tem M0 E02, M2 E06, M0 E03 e M3 E05, executadas juntas no gate do M3 com o `roteiro-m3.md` (que acumula o do M2 e o do M1) e o pacote mais recente (`build/demo-package/`, `VERSAO.txt` com `front_commit=a800b25`, gerado em 2026-11-17 com as correções da M3 E06). Cada aprovação fecha a etapa `#concluida`; uma reprovação a reabre com uma rodada de correção.
- A branch local `roadmap/gate-rapido` (`5887995`) não está na `main` e nenhuma captura trata dela.

## Regra 5 revista: recriar a demo (2026-11-15)

Origem: [[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]].

Origem: `docs/roadmaps/README.md`, regra 5 e última linha do histórico (2026-11-15).

- Num banco novo, a data operacional é o dia da recriação. Desde o servidor em `5e06f16d51ff` (M0 E03), ela avança sozinha: o servidor fecha o dia às 03:00 do dia seguinte (`endOfDayTime` padrão), com no-show das chegadas confirmadas sem check-in (com multa), lançamento das diárias e avanço da data.
- A recriação vale só para o dia em que é feita: recriar no mesmo dia do roteiro ou da demo, depois das 03:00, nunca na véspera. O seed não muda o horário do fechamento. O fechamento manual só entra num roteiro a partir do M6 (E08), por último ou seguido de nova recriação.
- A tabela de marcos do README passa a dar o M3 como dependente de "M2 e M0 E03", e o M6 com o fechamento do dia "desbloqueado pela rodada 3 do M0".

## Desbloqueio da M6 E08, fechamento do dia (2026-11-15)

Origem: [[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]].

Origem: `docs/roadmaps/roadmap-m6-governanca-operacao.md`, E08, H3 e último histórico.

- A E08 saiu de `#bloqueada` para `#pendente`: a M6 E11 do servidor (8 etapas e avanço da data) está no commit que a M0 E03 fixa. Dependência: gate do M5 e servidor fixado em `5e06f16d51ff` ou depois.
- H3 marcada **confirmada (2026-11-15)**.
- Escopo revisto: a E11 do servidor não mudou o contrato do fechamento (nenhuma operação nem código de erro novo; `kind` e `stepName` das pendências são texto livre). Entrou um critério de no-show (chegada confirmada sem check-in aparece como "Não compareceu", ou como pendência se o servidor recusou a multa) e notas com decisões da E11 do servidor (multa recusada impede o no-show inteiro; etapa que falha não avisa as pendências gravadas; avanço que esgota o prazo fica `FAILED` até retomada manual). Risco novo: a M6 E13 do servidor (snapshot e PDFs) pode trazer etapas antes do avanço; a tela mostra as etapas como o servidor lista.

## Notas novas em outros marcos na rodada 3 (2026-11-15)

Origem: [[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]].

Origem: últimas linhas do histórico de cada roadmap.

- M3 (`roadmap-m3-reservas.md`): E04 ganhou a nota da reativação de no-show (o `reactivate` vale também para no-show; o seed não cria no-show, coberto por teste do *state holder*); E05 a da recriação no mesmo dia. O marco passa a exigir a M0 E03 antes da E01.
- M5 (`roadmap-m5-hospedes-empresas.md`): E02 ganhou dois critérios (teste da fachada do `core` nas três escritas, incluindo `IncompatibleResponse`; tela conclui a ação com o resumo sem tentar mostrar o perfil) e notas sobre o ADR 0010.
- M7 (`roadmap-m7-gestao-cadastros.md`): E10 ganhou a nota do no-show na fila da FNRH (rótulos pt-BR para `NO_SHOW` e `REMOTE_NO_SHOW`).
- Nenhuma tag mudou nesses três roadmaps.

## Roadmaps M0 a M7 na revogação do processo acelerado (2026-11-17)

Origem: [[2026-11-17 - ZenyHotelManager-DesktopFront - ADR 0012 revoga o processo acelerado e atualização dos roadmaps - 10b921ef]] (diffs do commit `3c7c9de` do front). A decisão está em [[ZenyHotelManager-DesktopFront - Processo de execução (ADRs 0011 e 0012)]].

**Roadmaps M0 a M7 (`docs/roadmaps/roadmap-m*.md`)**

- A seção "Prompt acelerado" foi removida dos oito. O protocolo e o prompt de execução não mudaram. Cada roadmap ganhou uma entrada de 2026-11-17 no histórico.
- M0, M1 e M2: nenhuma etapa mudou.
- M3:
  - a E05 continua `#em-andamento` e não foi reescrita. O handoff registra que, desde 2026-11-17, o restante segue o processo normal, e traz a linha `Revisão de segurança: adiada (ADR 0011) — commits 830f296..920dcd2, integridade exit 0`. Registra também que a branch `roadmap/m3-reservas` precisa receber a `main` antes de a etapa ser retomada (fast-forward) e que o workspace da etapa fica só no worktree dela e não pode ser apagado;
  - entra a E06, "Revisão adiada do processo acelerado", `#pendente`, dependente da E05. Escopo: a `revisor-seguranca` com o prompt `code-reviewer.md` sobre `a300a23..HEAD`, com a saída do scanner, de `check_test_integrity.py --base a300a23` e do gate do projeto; correção de cada achado Crítico ou Importante pelo ciclo normal; destino registrado de cada achado; marca de paga em cada entrada da lista do README; pacote de demo gerado de novo se a etapa mudar código de produção. Revisão humana: não;
  - o escopo e a definição de pronto do marco ganharam o item da revisão adiada paga (E06).
- M4: o pré-requisito passa a exigir também a M3 E06 `#concluida`. A E02 e a E03 ganharam, em "Notas para o plano", as partes independentes.
- M5: a E01, a E02 e a E03 ganharam as partes independentes.
- M6: a E01, a E04 e a E05 ganharam as partes independentes.
- M7: as etapas E01 a E07, a E10 e a E12 ganharam as partes independentes. O histórico do roadmap diz que as relações entre cadastros foram conferidas no contrato fixado (`api/openapi.yaml`).
- Nas etapas do M4 ao M7, objetivo, escopo e critérios de aceite não mudaram, e nenhuma tag mudou. As notas de partes independentes servem para o plano de cada etapa formar ondas.

## Pendências do usuário (2026-11-10)

Origem: [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]].

1. **Registrar o projeto no brain** como `ZenyHotelManager-DesktopFront` (nome decidido pelo usuário), numa sessão comum (`/development-roadmap`), antes da primeira execução do orquestrador; depois, processar a Inbox no vault para criar o hub.
2. **Trocar o casamento do `load-brain.py` para prefixo do nome de arquivo** (decisão do usuário): na função `pending_captures` de `99 System/Skills/development-roadmap/scripts/load-brain.py`, casar por `<AAAA-MM-DD> - <Projeto> - ` em vez de substring sem diferenciar maiúsculas. Hoje "ZenyHotelManager" contido em "ZenyHotelManager-DesktopFront" faria as capturas do front entrarem nas sessões do servidor e ocuparem o espaço do hub (cortado em 9.500 caracteres).
3. **Regra de pedidos `PF-NN` no servidor**: uma linha no `CLAUDE.md` ou em `docs/roadmaps/README.md` do servidor dizendo que a sincronização de marco considera os pedidos pendentes e que a captura de fechamento cita "atende PF-NN". Edição numa sessão do servidor.
4. **Instalar o JDK 25 no Windows** e liberar a porta 8088 no firewall de lá.
5. Também listado em `docs/roadmaps/README.md`: commitar os documentos na `main` do front, porque o repositório ainda não tem commit e o orquestrador cria o worktree a partir do `HEAD`.

*Nota do curador (conferência em 2026-11-17, só leitura):* a pendência 5 está cumprida (os documentos estão na `main` desde o `abe64cd`). A 1 não foi feita pela skill `development-roadmap`: o repositório não tem `.claude/settings.json` com o hook, e o hub [[ZenyHotelManager-DesktopFront]] foi criado pelo curador ao processar a Inbox. A 2 não foi feita: `pending_captures` do `load-brain.py` ainda casa por substring. A 3 não aparece feita: nenhum documento do servidor cita "PF-NN". A 4 não foi conferida. A lista continua em "Pendências do usuário antes da primeira execução" de `docs/roadmaps/README.md`.

---

## Proveniência

- 2026-11-17 — [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]] (capture_id: 16d5b400-b2e5-490e-b063-b61b40c14257): marcos e roadmaps, regras gerais e pendências do usuário; nota criada pelo curador.
- 2026-11-17 — [[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]] (capture_id: 5bba7217-6f3f-460d-8b80-ace44d5b8683): regra 5 revista, desbloqueio da M6 E08 e notas novas no M3, no M5 e no M7.
- 2026-11-17 — [[2026-11-17 - ZenyHotelManager-DesktopFront - ADR 0012 revoga o processo acelerado e atualização dos roadmaps - 10b921ef]] (capture_id: 10b921ef-c99f-44a2-a0ac-77ac16591dbe): mudanças nos roadmaps M0 a M7 do commit `3c7c9de` (M3 E06, pré-requisito do M4, partes independentes).
