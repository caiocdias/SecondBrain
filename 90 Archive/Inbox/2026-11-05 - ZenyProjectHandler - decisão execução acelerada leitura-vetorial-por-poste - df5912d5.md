---
type: capture
status: archived
created: 2026-11-05
capture_id: df5912d5-1f3e-48b4-9f24-fbb0f3e7a419
---

# ZenyProjectHandler - decisão execução acelerada leitura-vetorial-por-poste

## Conteúdo capturado

### Problema (fatos medidos, segundo o design)

- No roadmap "leitura vetorial por poste", cada etapa leva de 5h a 15h. Medido no `git log`: E05 levou 15h16 (07:22 → 22:38), E04 5h, E03 11h20 (essa com operação e amostra humana).
- Na E05, a Task 6 levou cerca de 7h45 (12:55 → 20:40), com 5 rodadas de correção da tabela real. Cada rodada passou pelo ciclo completo: desenvolvedor → testador com ataques → verificação → revisora. A revisão final e a correção que veio depois levaram mais ~2h.
- A suíte tem 5330 testes e leva 1578 s (26 min) com cobertura, em série, sem `pytest-xdist`, numa máquina de 20 núcleos lógicos. As souls `desenvolvedor` e `testador` rodam a suíte inteira antes de cada commit e no fim de cada tarefa. A E05 teve 25 commits do desenvolvedor e 20 do testador.
- O `main` reprova hoje por um teste que mede tempo de parede (29,7 s contra o limite de 20 s).
- Diagnóstico do design (três custos dominantes): a suíte inteira em série repetida a cada commit e a cada rodada; a calibração contra folhas reais feita dentro do ciclo de produção, uma passada completa por hipótese; e etapas encadeadas estritamente em série, mesmo as que não dependem umas das outras.

### Decisões (registradas no roadmap como D6, D7, D8)

Decisão D6 (execução acelerada, por entrevista com o usuário):
- **Trilhas paralelas A/B/C**: A = analisador, B = medição, C = aprendizado. Cada uma roda numa sessão `claude --agent orquestrador` própria, com worktree e branch próprios (`roadmap/leitura-vetorial-por-poste`, `-b`, `-c`). Duas trilhas nunca editam ao mesmo tempo o mesmo arquivo versionado; a exceção são as seções do roadmap de cada trilha. Uma dependência entre trilhas só vale com a etapa `#concluida` e integrada em `main`. O orquestrador nunca faz merge nem rebase.
- **Gate paralelo em etapa curta (E14) antes da E06**: `pytest-xdist` no lock de desenvolvimento e no `.bat`, sem perder teste nem cobertura (mínimo de 85,01%). As asserções de tempo de parede viram contagem de trabalho. Meta do arquiteto: passo pytest em até 8 min. Para descartar teste intermitente, 3 execuções paralelas seguidas verdes e 1 serial verde.
- **Laboratório paralelo** para tarefas calibradas contra folhas reais. O plano marca a tarefa `Laboratório: sim` e traz de 2 a 3 hipóteses, a métrica, o comando, o critério de vitória (leitura errada afirmada = 0 é obrigatório), o critério de parada e uma caixa de tempo de 60 min por hipótese. Um `desenvolvedor` por hipótese trabalha em worktree descartável, sem commit e sem a suíte inteira. O orquestrador escolhe a vencedora pela métrica e registra a decisão no ledger. A tarefa passa então uma vez pelo ciclo completo, partindo do patch vencedor.
- **Orçamento de ~3h por etapa**: o relógio vai do commit `#em-andamento` ao commit `#concluida` e não conta a espera pelo usuário nem por outra trilha. Se o plano estimar mais de ~3h, a etapa é dividida antes em subetapas `Eyy.1`, `Eyy.2`…, cada uma completa. Ao passar de 4h30, o lote para e o orquestrador relata e propõe dividir, estacionar ou continuar.
- **E15 e E16 como etapas próprias**: a E15 (ficha predita a partir das propostas, trilha B) sai da E07. A E16 (conjunto de avaliação cego, trilha B) sai da E09 e fica `#bloqueada` até o usuário entregar folhas novas. Nenhuma etapa lê `examples/avaliacao-cega/` antes da comparação da E09.

Decisão D7: os worktrees de laboratório são descartáveis, e o orquestrador os remove no fechamento da tarefa sem pedir confirmação.

D8 (pendente do usuário, fora do roadmap, numa sessão comum): propostas de mudança nas souls.
- P1, suíte por fase: testes da área a cada commit, suíte inteira antes do DONE ou de cada revisão. A política de suíte que o usuário escolheu depende de P1; até lá vale a regra atual das souls, que a E14 deve tornar barata.
- P2, tarefas paralelas na etapa: tarefas de arquivos disjuntos, cada uma em worktree próprio, integradas em série. Contraria `subagent-driven-development/SKILL.md:282` e exigiria uma exceção explícita na soul `orquestrador`.
- P3, revisão final repartida por área entre revisoras em paralelo, mais uma revisora de integração.

### Alternativas descartadas (tabela "Decisões" do design)

- E14 em paralelo com a E06 (a E06 pagaria o gate lento e disputaria `pyproject.toml`/`tests/`); seguir sem xdist.
- Manter a suíte inteira em toda rodada (situação atual).
- Teto de 2 rodadas de calibração dentro do ciclo, em vez do laboratório; ou manter como está.
- Sessão única sequencial, em vez das trilhas.
- E15 dentro da E07 ou não confirmar D5; E16 dentro da E09.
- Orçamento de ~5h ou sem orçamento.
- Aplicar já as tarefas paralelas na etapa (o arquiteto não edita souls) ou descartá-las.

### Aprendizado reutilizável

Interpretação do agente, formulada pelo chamador a partir do design (não registrada pelo usuário como princípio): calibração contra dado real não deve passar pelo ciclo completo dev → testador → revisora a cada iteração. Explore em laboratório paralelo e passe o vencedor uma vez pelo ciclo.

Pode valer além deste projeto, para qualquer fluxo de agentes com cerimônia de qualidade por iteração: separar a exploração (barata, paralela, descartável, sem commit) da produção (uma passagem completa pelo ciclo de qualidade). Outros custos do mesmo tipo: suíte inteira em série repetida a cada commit, e etapas independentes encadeadas em série.

## Contexto

Surgiu no projeto ZenyProjectHandler (interpretação de projetos de expansão da rede CEMIG a partir de PDFs), durante a execução do roadmap de leitura vetorial por poste com as souls `orquestrador`, `desenvolvedor`, `testador`, `revisor-seguranca` e `revisor-arquitetura`. O usuário pediu que as etapas avancem mais rápido sem perder qualidade. O design de execução acelerada foi escrito pelo arquiteto e revisado por `revisor-arquitetura`. As decisões do builder check (por exemplo, a E15 fora da onda 1 porque o `main` está vermelho) são do arquiteto, e o usuário pode revê-las.

## Origem

- Projeto: ZenyProjectHandler, repositório local `C:\Users\Caio\Desktop\repos\ZenyProjectHandler`.
- Design: `C:\Users\Caio\Desktop\repos\ZenyProjectHandler\docs\superpowers\specs\2026-11-04-execucao-acelerada-leitura-vetorial-design.md` (seções "Evidência", "Decisões", "Trilhas", "Laboratório", "Orçamento", "Propostas para as souls").
- Roadmap: `C:\Users\Caio\Desktop\repos\ZenyProjectHandler\docs\roadmap-leitura-vetorial-por-poste.md` (seção "Hipóteses e decisões em aberto", linhas D5–D8; "Protocolo de execução" → "Trilhas e branch", "Laboratório", "Orçamento"; "Índice de etapas").
- Commit: ainda não commitado. Os dois arquivos estão na working tree do branch `main`, HEAD `6a6c506`: o roadmap modificado e o design não rastreado.

## Por que registrar

Registra uma decisão de processo do projeto, que muda como as etapas são encadeadas e medidas, e um aprendizado sobre fluxos de agentes que pode valer em outros projetos.

## Limitações e incertezas

- O projeto ainda não tem hub no brain; esta é uma captura avulsa.
- Os arquivos de origem não estavam commitados no momento da captura e podem mudar ou sumir antes do commit. Não foram copiados para o vault.
- As datas divergem: o design atribui as decisões à "entrevista de 2026-11-04", e o roadmap diz "Decidido em 2026-11-05" em D5–D8. Não verifiquei qual está certa.
- O ganho do `pytest-xdist` (estimativa de 26 min para 3–6 min) não foi medido; a E14 deve medir. O design também não mediu quantas vezes a suíte rodou por inteiro na E05.
- D8 (P1–P3) segue pendente do usuário.

## Possíveis conexões

Temas sem nota no vault (texto simples): ZenyProjectHandler; orquestração de subagentes; souls do Claude Code; paralelismo com git worktrees; calibração contra dado real; orçamento de tempo por etapa.
