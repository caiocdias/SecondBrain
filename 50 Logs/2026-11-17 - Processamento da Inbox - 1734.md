---
type: log
created: 2026-11-17
---
# Processamento da Inbox — 2026-11-17 17:34

Estado do lote: concluído

Escopo pedido pelo usuário: processar o que for relativo à `main` do ZenyHotel (servidor e front); o que for relativo a outras branches locais pode ser descartado, porque outra máquina desenvolve a partir do HEAD da `main`.

## Capturas

### 24803598-810b-4344-997b-c28c79463e5c
- Captura: [[2026-11-17 - ZenyHotelManager - pedido do front PF-03 Trocar o titular e os hóspedes de uma reserva antes do check-in - 24803598]] (preservada em 90 Archive/Inbox/)
- Ação: integrada como pedido aberto do front desktop ao servidor, sem decisão do servidor, na forma do PF-01 e do PF-02: subseção nova "Pedido do front PF-03" em "Atualizações por capturas" de Módulo reservations (ciclo de vida), remissão no item "Alteração" do texto literal e bullet de Perguntas abertas do hub do servidor (fundido com o dos outros pedidos).
- Notas criadas: nenhuma
- Notas enriquecidas: [[ZenyHotelManager]], [[ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)]]
- Normalizações: status alterado para archived ao mover para 90 Archive/Inbox/ (arquivo não rastreado pelo git: movido com `mv -n`)
- Conferência: por `git` (só leitura), na `main` do servidor (`5e06f16`) o `changeReservation` recebe `ReservationChangeRequest` sem titular nem hóspedes, e o contrato não tem `/reservations/{id}/guests`; nenhum documento do servidor cita "PF-03"; na `main` do front (`6ffc9f3`), `docs/pedidos-servidor.md` traz o PF-03 `aberto`. O código do caso de uso não foi lido.
- Pendências: decisão do servidor sobre o PF-03, a cargo do usuário e do `arquiteto`.
- Estado: concluída

### 8f737e26-5881-45fe-85ec-163b1285ac0a
- Captura: [[2026-11-17 - ZenyHotelManager - pedido do front PF-04 Prévia da multa de cancelamento da reserva - 8f737e26]] (preservada em 90 Archive/Inbox/)
- Ação: integrada como pedido aberto, na mesma forma: subseção nova "Pedido do front PF-04" em Módulo reservations (ciclo de vida), remissão no item "Cancelamento" do texto literal e o mesmo bullet de Perguntas abertas do hub do servidor.
- Notas criadas: nenhuma
- Notas enriquecidas: [[ZenyHotelManager]], [[ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca)]]
- Normalizações: status alterado para archived ao mover para 90 Archive/Inbox/ (`mv -n`)
- Conferência: por `git` (só leitura), na `main` do servidor (`5e06f16`) o contrato tem `CancellationTermsResponse` e `CancellationPenaltyResponse` com os campos citados e nenhuma rota `cancellation-preview`; nenhum documento do servidor cita "PF-04"; `docs/pedidos-servidor.md` do front traz o PF-04 `aberto`.
- Pendências: decisão do servidor sobre o PF-04, a cargo do usuário e do `arquiteto`.
- Estado: concluída

### 16d5b400-b2e5-490e-b063-b61b40c14257
- Captura: [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]] (preservada em 90 Archive/Inbox/)
- Ação: integrada. Mantida na Inbox em três lotes por falta de hub; o pedido do usuário de processar também o front foi tomado como pedido de criação da nota de projeto. Hub novo com objetivo, repositório, estado, índice e pendências; objetivo, F1 a F6 e chamadas do arquiteto em Arquitetura e decisões; canal de pedidos em Sincronização; marcos, regras gerais e pendências do usuário em Marcos, roadmaps e demo. Texto da captura levado sem resumo.
- Notas criadas: [[ZenyHotelManager-DesktopFront]], [[ZenyHotelManager-DesktopFront - Arquitetura e decisões (ADRs 0001 a 0010)]], [[ZenyHotelManager-DesktopFront - Sincronização com o servidor (M0) e pedidos PF-NN]], [[ZenyHotelManager-DesktopFront - Marcos, roadmaps e demo]]
- Notas enriquecidas: [[ZenyHotelManager]] (link para o hub do front em Conhecimento relacionado e no bullet dos pedidos)
- Normalizações: status alterado para archived ao mover para 90 Archive/Inbox/ (`mv -n`)
- Conferência: por `git` (só leitura), design e ADRs 0001 a 0006 estão na `main` do front desde o `abe64cd` (2026-11-10). O texto atual dos arquivos não foi comparado linha a linha com a captura.
- Pendências: registro pela skill `development-roadmap` e hook no repositório do front; troca do casamento do `load-brain.py` por prefixo; regra `PF-NN` no servidor (todas do usuário, registradas em Perguntas abertas do hub do front).
- Estado: concluída

### 677b277a-44a4-4da4-8214-4dfca2edc865
- Captura: [[2026-11-13 - ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão - 677b277a]] (preservada em 90 Archive/Inbox/)
- Ação: integrada: ADR 0009 em Arquitetura e decisões; resultado da rodada 2 e M0 E02 em Sincronização.
- Notas criadas: nenhuma além das da 16d5b400
- Notas enriquecidas: [[ZenyHotelManager-DesktopFront]], [[ZenyHotelManager-DesktopFront - Arquitetura e decisões (ADRs 0001 a 0010)]], [[ZenyHotelManager-DesktopFront - Sincronização com o servidor (M0) e pedidos PF-NN]]
- Normalizações: status alterado para archived ao mover para 90 Archive/Inbox/ (`mv -n`)
- Conferência: por `git` (só leitura), o ADR 0009 está na `main` do front desde o `29cc674` (2026-11-13). Números do contrato não conferidos.
- Pendências: nenhuma.
- Estado: concluída

### 5bba7217-6f3f-460d-8b80-ace44d5b8683
- Captura: [[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]] (preservada em 90 Archive/Inbox/)
- Ação: integrada: ADR 0010 e atualizações dos ADRs 0007 e 0009 em Arquitetura e decisões; resultado da rodada 3, pedidos e M0 E03 em Sincronização; regra 5 revista, desbloqueio da M6 E08 e notas novas nos marcos em Marcos, roadmaps e demo.
- Notas criadas: nenhuma além das da 16d5b400
- Notas enriquecidas: [[ZenyHotelManager-DesktopFront]], [[ZenyHotelManager-DesktopFront - Arquitetura e decisões (ADRs 0001 a 0010)]], [[ZenyHotelManager-DesktopFront - Sincronização com o servidor (M0) e pedidos PF-NN]], [[ZenyHotelManager-DesktopFront - Marcos, roadmaps e demo]]
- Normalizações: status alterado para archived ao mover para 90 Archive/Inbox/ (`mv -n`)
- Conferência: por `git` (só leitura), o ADR 0010 está na `main` do front desde o `ebfd468` (2026-11-15); `api/server-pin.properties` fixa `5e06f16d51ff…`, que é a ponta da `main` do servidor.
- Pendências: nenhuma.
- Estado: concluída

### 0cc1844e-038a-4163-83d7-abbb4b4c6ffd
- Captura: [[2026-11-16 - ZenyHotelManager-DesktopFront - ADR 0011 processo acelerado até a demo - 0cc1844e]] (preservada em 90 Archive/Inbox/)
- Ação: integrada na nota Processo de execução, como registro de decisão revogada (o ADR 0012 a sucede). Não foi promovida a princípio geral: é decisão específica do repositório, e a comparação com o ZenyProjectHandler segue rotulada como interpretação do agente.
- Notas criadas: [[ZenyHotelManager-DesktopFront - Processo de execução (ADRs 0011 e 0012)]]
- Notas enriquecidas: [[ZenyHotelManager-DesktopFront]]
- Normalizações: status alterado para archived ao mover para 90 Archive/Inbox/ (`mv -n`)
- Conferência: por `git` (só leitura), o ADR 0011 entrou na `main` do front no `66adced` (2026-11-16) e mudou no `69a93d4` e no `3c7c9de`.
- Pendências: nenhuma (a dívida de revisão está na 10b921ef).
- Estado: concluída

### 10b921ef-c99f-44a2-a0ac-77ac16591dbe
- Captura: [[2026-11-17 - ZenyHotelManager-DesktopFront - ADR 0012 revoga o processo acelerado e atualização dos roadmaps - 10b921ef]] (preservada em 90 Archive/Inbox/)
- Ação: integrada: ADR 0012 e atualização do `CLAUDE.md`, do ADR 0011 e do README dos roadmaps em Processo de execução; mudanças nos roadmaps M0 a M7 em Marcos, roadmaps e demo; Estado do hub.
- Notas criadas: nenhuma além das anteriores
- Notas enriquecidas: [[ZenyHotelManager-DesktopFront]], [[ZenyHotelManager-DesktopFront - Processo de execução (ADRs 0011 e 0012)]], [[ZenyHotelManager-DesktopFront - Marcos, roadmaps e demo]]
- Normalizações: status alterado para archived ao mover para 90 Archive/Inbox/ (`mv -n`)
- Conferência: por `git` (só leitura), o `3c7c9de` está na `main` do front; a ponta é o `6ffc9f3` (2026-11-17 12:01, igual à `origin/main`), em que a M3 E05 e a M3 E06 estão `#em-andamento` e a lista de revisões adiadas ainda não tem a marca de paga. Registrado como notas do curador.
- Pendências: M3 E06 por concluir (dívida de revisão), validações acumuladas no Windows (usuário).
- Estado: concluída

## Observações

- Nenhum lote anterior em andamento ou interrompido. Sete capturas pendentes, sem `capture_id` duplicado; nenhum aparecia em `90 Archive/Inbox/` nem em seções de proveniência. Nenhuma captura mudou nem chegou durante o lote.
- Triagem do escopo, por `git` (só leitura): as sete capturas tratam de conteúdo que está na `main`. No front, a `main` (`6ffc9f3`) contém os ADRs 0001 a 0012, os roadmaps e `docs/pedidos-servidor.md` com PF-01 a PF-04; as branches `roadmap/m0` a `roadmap/m3` estão todas contidas na `main`. No servidor, PF-03 e PF-04 foram conferidos contra a `main` (`5e06f16`). **Nenhuma captura era relativa só a outra branch local; nada foi descartado.**
- Fora da `main` e sem captura: `roadmap/gate-rapido` (`5887995`) no front; `roadmap/m6-operacao-fechamento` (`adba5e3`) e `roadmap/m5-recepcao-fnrh` (`3a42e35`) no servidor.
- As notas do servidor já descrevem a M6 E18 e a M6 E01 (integradas no lote [[2026-11-16 - Processamento da Inbox - 2151]]), que só existem na branch `roadmap/m6-operacao-fechamento`, fora da `main`. Elas estão marcadas como tal no Estado do hub e em Estado por marco. Não foram tocadas: o pedido de descarte tratava da Inbox, e retirar conteúdo já integrado é decisão do usuário.
- Criação do hub do front: o pedido explícito do usuário de processar a Inbox do front foi tomado como pedido de criação da nota de projeto, pendência registrada nos três lotes anteriores. O hub tem 7.744 bytes, abaixo da meta de ~8.000 caracteres. As notas de tema levam o texto das capturas por faixas de linhas, sem reescrita.
- Hub [[ZenyHotelManager]] com 15.973 bytes (15.197 no início do lote), acima da meta de ~8.000 de [[99 System/AI/processing]] e do corte de 9.500 do hook: cresceu com as duas linhas de proveniência, o bullet dos pedidos e o link para o front. A redução depende de decidir a forma da proveniência no hub, pendência dos lotes anteriores.
- Decisão do usuário ao fechar o lote (2026-11-17): o conteúdo da branch do M6 já integrado não precisa ser retirado; em conflito de informação, as capturas vindas da outra máquina (desenvolvimento a partir da `main`) têm prioridade. Registrado em "Atualização por capturas" do hub [[ZenyHotelManager]].
- Verificação final: sete capturas em `90 Archive/Inbox/` com `status: archived`; os sete `capture_id` aparecem nas seções de proveniência das notas de destino e neste log; frontmatter presente e wikilinks resolvidos nos 14 arquivos alterados, criados ou movidos; `00 Inbox/` só com `.gitkeep`.
