---
type: capture
status: archived
created: 2026-11-05
capture_id: 1ecf9413-8dda-4969-9487-6fbd3965658d
---

# ZenyProjectHandler - decisões D9 e D10 do roadmap leitura-vetorial-por-poste (orçamento de máquina e E17 na trilha C)

## Conteúdo capturado

Fonte de todas as linhas citadas: `docs/roadmap-leitura-vetorial-por-poste.md` do ZenyProjectHandler, working tree de 2026-11-05 (ver "Origem").

### D9: orçamento de máquina (decisão do arquiteto, revisável pelo usuário)

Citação literal (protocolo, "Orçamento de máquina", linha 168): "A máquina tem 20 núcleos lógicos, e trilhas, ondas e laboratório se somam. O teto é de ~4 agentes escrevendo código ao mesmo tempo, somando todas as trilhas."

Decisão (linha 94 da tabela "Hipóteses e decisões em aberto" e linhas 166–173 do protocolo). Resumo do agente:

- Problema: o paralelismo se empilha em três níveis (trilhas × ondas de tarefas × laboratório) numa máquina de 20 núcleos lógicos.
- Teto global: ~4 agentes escrevendo código ao mesmo tempo, somando todas as trilhas (linha 168).
- Trilhas ativas: as que têm etapa `#em-andamento` no roadmap da própria branch, contando a trilha que faz a conta (linha 169).
- Ondas: antes de abrir cada onda, o orquestrador recalcula o limite pelas trilhas ativas. Com 1 trilha ativa, até 3 tarefas; com 2, até 2; com 3, uma só, sem onda. Um número no prompt só baixa esse limite (linha 170). O prompt de execução passa a apontar para essa regra (linha 229).
- Laboratório: ocupa a cota da onda, e a trilha não abre onda de tarefas enquanto ele roda. O número de hipóteses é o da cota, entre 2 e 3. O mínimo de 2 vale mesmo com 3 trilhas, porque o desenvolvedor de laboratório não roda a suíte inteira (linha 171).
- Processos: a suíte inteira usa `-n` = 20 ÷ (trilhas ativas × suítes que a trilha roda ao mesmo tempo), arredondado para baixo, com mínimo de 2. Os scripts de corpus fazem a mesma conta em `--processos`. O `.bat` do fechamento continua com `-n auto`. Se um worker morrer nele com outras trilhas ativas, isso é tratado como defeito e a carga do momento vai para o handoff (linha 172).
- Os leitores visuais da curadoria ficam fora da conta (linha 173).

Alternativas descartadas (linha 94):

- limite fixo no prompt, porque a trilha longa ficaria sem ondas depois que as curtas fecham;
- nenhum teto, porque três trilhas com ondas de 3 dariam 9 agentes e ~54 workers do pytest em 20 núcleos. Isso fica perto da carga de 60 processos em que a E14 viu workers Qt morrerem (achado I-2, descrito no handoff da E14, linha 925).

Risco registrado (linha 94): um teto baixo demais deixa a E06 sem ondas enquanto E15 e E17 estão abertas. Um teto alto demais traz de volta a instabilidade do Qt sob carga. Nos dois casos, o roadmap manda ajustar a tabela do protocolo.

### D10: a E17 passa da trilha A para a trilha C (decisão do arquiteto, revisável pelo usuário)

Decisão (linha 95). Resumo do agente:

- A E17 é o fechamento do cliente com servidor lento. Entrega: fechar a janela nunca destrói `QThread` viva, sem o monkeypatch de 60 s no `conftest` (linha 283). Ela sai da trilha A e vai para a C.
- Motivo: a trilha C fica ociosa até a E07 ser integrada e já tem worktree com `.venv`. Assim a trilha A vai direto à E06, no caminho crítico E06 → E07 → E08 → E09.
- Descartadas: a E17 na A antes da E06, porque atrasaria o caminho crítico em uma etapa; e a E17 na B depois da E15, porque atrasaria em uma etapa o fim do lote da B, que integra a E15 de que a E07 precisa.
- Custo registrado: exige uma terceira sessão ao mesmo tempo na janela 2. Se o usuário preferir duas sessões, a E17 volta para a A depois da E06, sem mudar o escopo.

Reflexos no índice e na seção da etapa (resumo do agente):

- Tabela da Trilha C (linhas 278–285): o cabeçalho passa a ser "Trilha C — aprendizado, e a E17 enquanto a trilha espera a E07 (D10)". A E17 está `#pendente`, depende da E14 e fica entre a E11 (`#concluida`) e a E10.
- Tabela "Janelas" (linhas 287–296), antes chamada "Ondas". O nome "ondas" fica reservado às ondas de tarefas do `orquestrador` e às da curadoria (linha 287).
  - Janela 1 (E14 na A, E11 na C): concluída, com as duas etapas integradas em `main` (linha 291).
  - Janela 2: E06 (A), E15 (B) e E17 (C), mais a E16 (B) quando as folhas chegarem. São três sessões, e cada trilha começa com ondas de uma tarefa. A E06 recupera as ondas à medida que a E15 e a E17 fecham. Arquivos: a E06 mexe em `src/` de análise, a E15 em `scripts/benchmark_ficha_poste.py` e a E17 no cliente e em `tests/conftest.py` (linha 292).
- Seção da E17 (linha 975): roda na trilha C, ao mesmo tempo que a E06 e a E15, e nenhuma etapa depende dela.

### Outros ajustes da mesma revisão (resumo do agente)

- "Trilhas e branch", parágrafo de abertura (linha 127): o fim do lote integra a branch na `main` (fechamento do `orquestrador`), sem esperar o usuário. Em caso de dúvida vale o design de execução acelerada, menos na integração e nas propostas P1–P3, em que valem a D8 e as souls.
- Item "Retomada" (linha 135): fora do fechamento do lote, o orquestrador não faz merge da principal na branch da trilha nem rebase dela. Os rebases das branches de tarefa sobre a branch da trilha, nas ondas (passo 3a), são permitidos.
- O plano de cada etapa passa a trazer os campos por tarefa do `orquestrador` (`Estimativa`, `Depende de`, `Risco`), e a soma das estimativas decide se a etapa será dividida (linha 185).
- A última entrada do "Histórico de revisões" (linhas 1504–1509) registra a revisão: integração conforme a D8, "Orçamento de máquina" (D9), E17 na trilha C (D10), "Ondas" renomeadas para "Janelas" e campos por tarefa no plano.

### Aprendizado possivelmente reutilizável

Interpretação do agente, formulada pelo chamador (não é princípio registrado pelo usuário): quando o paralelismo se empilha em níveis (sessões paralelas × tarefas paralelas × hipóteses de laboratório), o limite precisa ser global à máquina e recalculado no momento de abrir cada nível, não fixo por sessão. Senão, a soma estoura os núcleos e os testes de GUI ficam instáveis sob carga.

## Contexto

O arquiteto (sessão `claude --agent arquiteto`) revisou o roadmap a pedido do usuário depois da reforma das souls no vault, a D8 (commit `93f0c68` do vault). A reforma trouxe: testador condicional, suíte por fase, tarefas de até ~45 min com `Estimativa`/`Depende de`/`Risco`, ondas paralelas de até 3 tarefas por etapa, decisões pela opção recomendada e lote que termina com merge local na `main`. A revisão alinhou o roadmap a essas regras e trouxe duas decisões novas do arquiteto, D9 e D10, que o usuário pode rever.

Relação com a captura anterior [[2026-11-05 - ZenyProjectHandler - decisão execução acelerada leitura-vetorial-por-poste - df5912d5]] (`capture_id` df5912d5-1f3e-48b4-9f24-fbb0f3e7a419, D6–D8): esta captura não a corrige; registra decisões novas. Dois pontos daquela captura estão superados pelo roadmap atual, o que interessa ao curador:

- "D8 pendente do usuário": a D8 foi decidida pelo usuário em 2026-11-05 (linha 93, já no HEAD `10191eb`).
- "O orquestrador nunca faz merge nem rebase": agora o fechamento do lote faz merge local na `main`, e os rebases das branches de tarefa nas ondas são permitidos (linhas 127 e 135).

## Origem

- Projeto: ZenyProjectHandler, repositório local `C:\Users\Caio\Desktop\repos\ZenyProjectHandler`. O projeto não tem hub no brain; esta é uma captura avulsa.
- Arquivo: `C:\Users\Caio\Desktop\repos\ZenyProjectHandler\docs\roadmap-leitura-vetorial-por-poste.md`
  - "Hipóteses e decisões em aberto": linhas 94 (D9) e 95 (D10); D8 na linha 93;
  - "Protocolo de execução" → "Trilhas e branch": linhas 127 (abertura) e 135 (Retomada);
  - "Protocolo de execução" → "Orçamento de máquina": linhas 166–173;
  - prompt de execução: linha 229;
  - "Índice de etapas" → tabela da Trilha C: linhas 278–285;
  - "Índice de etapas" → tabela "Janelas": linhas 287–296;
  - seção da E17: linha 975;
  - handoff da E14, achado I-2: linha 925;
  - "Histórico de revisões", última entrada: linhas 1504–1509.
- Commit: nenhum. A mudança está na working tree do branch `main`, HEAD `10191eb` (1 commit à frente de `origin/main`). Segundo o `git diff --stat`, o roadmap é o único arquivo alterado, com 38 inserções e 18 remoções.
- Data da captura: 2026-11-05.

## Por que registrar

Registra duas decisões de processo do projeto, que mudam quantas sessões e agentes rodam ao mesmo tempo e em que trilha fica a E17. Registra também um aprendizado sobre limitar o paralelismo de agentes por máquina, que pode valer em outros projetos com orquestração de subagentes e git worktrees.

## Limitações e incertezas

- A mudança não estava commitada no momento da captura; os números de linha valem para a working tree de 2026-11-05 e podem mudar até o commit. O roadmap não foi copiado para o vault.
- D9 e D10 são decisões do arquiteto, revisáveis pelo usuário. Não há registro de aprovação do usuário.
- O commit `93f0c68` do vault foi informado pelo chamador e também aparece no roadmap (linha 21); não o conferi no Git do vault.
- A carga de 60 processos e o achado I-2 vêm do texto do handoff da E14 (linha 925), que considera o caso "provavelmente resolvido", com risco residual aberto. Não reproduzi nada.
- O teto de ~4 agentes e a tabela 3/2/1 ainda não foram testados sob carga real; a primeira validação será a janela 2.

## Possíveis conexões

- [[ZenyProjectHandler - Leitura vetorial por poste e detector local]]
- [[2026-11-05 - ZenyProjectHandler - decisão execução acelerada leitura-vetorial-por-poste - df5912d5]]
- Temas sem nota no vault (texto simples): ZenyProjectHandler; orquestração de subagentes; paralelismo com git worktrees; souls do Claude Code.
