---
type: knowledge
subtype: insight
status: processed
created: 2026-11-09
aliases:
  - "ZenyProjectHandler - decisões de processo do roadmap leitura-vetorial-por-poste"
sources:
  - "[[2026-11-05 - ZenyProjectHandler - decisão execução acelerada leitura-vetorial-por-poste - df5912d5]]"
  - "[[2026-11-05 - ZenyProjectHandler - decisões D9 e D10 leitura-vetorial-por-poste - 1ecf9413]]"
  - "[[2026-11-05 - ZenyProjectHandler - decisão D11 um orquestrador por vez e revisão de D9 e D10 leitura-vetorial-por-poste - d3c635af]]"
  - "[[2026-11-08 - ZenyProjectHandler - decisões D16 a D20 janela de release 0.6.0 - 731fe7d4]]"
---
# ZenyProjectHandler - Execução acelerada do roadmap de leitura vetorial

Decisões de processo (D6 a D11 e D16 a D20) que mudaram como o roadmap `docs/roadmap-leitura-vetorial-por-poste.md` do ZenyProjectHandler é executado por subagentes: trilhas, laboratório, orçamento de máquina, orquestrador único e a janela de release 0.6.0. As decisões técnicas do analisador estão em [[ZenyProjectHandler - Leitura vetorial por poste e detector local]].

Esta nota traz o estado vigente de cada decisão. As versões anteriores e os números de linha ficam nas capturas de origem. Em caso de divergência, vale o roadmap do repositório (`C:\Users\Caio\Desktop\repos\ZenyProjectHandler`).

Autoria: **[usuário]** = decisão do usuário; **[arquiteto]** = decisão ou desenho da soul `arquiteto`, revisável pelo usuário e sem registro de aprovação dele.

## Problema (fatos medidos, segundo o design)

- Cada etapa levava de 5h a 15h. Pelo `git log`: E05 15h16, E04 5h, E03 11h20 (com operação e amostra humana).
- Na E05, a Task 6 levou cerca de 7h45, com 5 rodadas de correção da tabela real, cada uma pelo ciclo completo desenvolvedor → testador → verificação → revisora.
- A suíte tinha 5330 testes e levava 1578 s (26 min) com cobertura, em série, numa máquina de 20 núcleos lógicos.
- Três custos dominantes, segundo o design: a suíte inteira em série a cada commit e rodada; a calibração contra folhas reais dentro do ciclo de produção; e etapas independentes encadeadas em série.

## Decisões vigentes

### D6: execução acelerada (por entrevista com o usuário, 2026-11-04)

- **Trilhas A/B/C**: A = analisador, B = medição, C = aprendizado, cada uma com worktree e branch próprios (`roadmap/leitura-vetorial-por-poste`, `-b`, `-c`). Duas trilhas nunca editam o mesmo arquivo versionado ao mesmo tempo, exceto as seções do próprio roadmap. Dependência entre trilhas só vale com a etapa `#concluida` e integrada na `main`. A sessão por trilha caiu com a D11.
- **Gate paralelo (E14) antes da E06**: `pytest-xdist` sem perder teste nem cobertura (mínimo de 85,01%). Asserções de tempo de parede viram contagem de trabalho. Meta do arquiteto: passo pytest em até 8 min.
- **Laboratório paralelo** para tarefas calibradas contra folhas reais: 2 a 3 hipóteses, métrica, comando, critério de vitória (leitura errada afirmada = 0 é obrigatório), critério de parada e caixa de 60 min por hipótese. Um `desenvolvedor` por hipótese, em worktree descartável, sem commit e sem a suíte inteira. O orquestrador escolhe a vencedora pela métrica, e a tarefa passa uma vez pelo ciclo completo a partir do patch vencedor.
- **Orçamento de ~3h por etapa**, do commit `#em-andamento` ao `#concluida`, sem contar espera. Plano estimado acima de ~3h é dividido antes em subetapas. Ao passar de 4h30, o lote para e o orquestrador propõe dividir, estacionar ou continuar.
- **E15 e E16 como etapas próprias** na trilha B. A E16 (avaliação cega) fica `#bloqueada` até o usuário entregar folhas novas, e nenhuma etapa lê `examples/avaliacao-cega/` antes da comparação da E09.
- Descartadas: E14 em paralelo com a E06; seguir sem xdist; suíte inteira em toda rodada; teto de 2 rodadas de calibração no ciclo em vez do laboratório; sessão única sequencial; E15 dentro da E07; E16 dentro da E09; orçamento de ~5h ou nenhum.

### D7: worktrees de laboratório (2026-11-04)

São descartáveis, e o orquestrador os remove no fechamento da tarefa sem pedir confirmação.

### D8: reforma das souls (**[usuário]**, 2026-11-05)

Texto do roadmap, conferido pelo curador; as regras vivem na soul `orquestrador`.

- P1 adotada: testes da área por commit e suíte inteira uma vez por tarefa e por rodada devolvida.
- P2 adotada como ondas paralelas: tarefas sem dependência e com arquivos disjuntos, até 3 por onda, cada uma em worktree próprio, integradas em série com a suíte inteira por onda.
- P3 descartada, porque a revisão é ~8% do tempo dos subagentes.
- Junto: testador condicional, tarefas de até ~45 min (com `Estimativa`, `Depende de` e `Risco` no plano), intervenções decididas pela opção recomendada (só arquitetura espera o usuário) e lote que termina com merge local na `main`, sem push.
- Fora do fechamento do lote, o orquestrador não faz merge da principal na branch da trilha nem rebase dela; os rebases das branches de tarefa nas ondas são permitidos.

### D9: orçamento de máquina (**[arquiteto]**, 2026-11-05, revisto com a D11)

Citação literal do protocolo: "A máquina tem 20 núcleos lógicos, e etapas simultâneas, ondas e laboratório se somam. O teto da sessão é de ~4 desenvolvedores ativos ao mesmo tempo."

- Ondas: com uma etapa aberta, até 3 tarefas; com duas, até 2 em cada. O orquestrador recalcula antes de abrir cada onda, e um número no prompt só baixa o limite.
- Laboratório: ocupa a cota da etapa dele, que não abre onda enquanto ele roda. De 2 a 3 hipóteses; 2 quando há duas etapas abertas.
- Processos: `-n` = 20 ÷ suítes simultâneas da sessão, arredondado para baixo, com mínimo de 2; `--processos` usa a mesma conta nos scripts de corpus.
- O `.bat` usa `-n auto`; enquanto ele roda, a sessão não despacha suíte nem benchmark novos da outra etapa aberta.
- Leitores visuais da curadoria ficam fora da conta.
- Descartadas: limite fixo de ondas (a etapa longa ficaria sem ondas depois que a curta fecha); nenhum teto (duas etapas com ondas de 3 dariam 6 desenvolvedores e ~36 workers do pytest em 20 núcleos, rumo à carga de 60 processos em que a E14 viu workers Qt morrerem, achado I-2).
- Risco: teto baixo deixa a E06 com ondas de 2; teto alto traz de volta a instabilidade do Qt. Nos dois casos, ajustar a tabela do protocolo.

### D10: E17 na trilha C (**[arquiteto]**, 2026-11-05)

A E17 (fechar a janela nunca destrói `QThread` viva, sem o monkeypatch de 60 s no `conftest`) sai da trilha A para a C, ociosa até a E07 e já com worktree e `.venv`. Assim a A vai direto à E06, no caminho crítico E06 → E07 → E08 → E09.

- Descartadas: E17 na A antes da E06 (atrasaria o caminho crítico em uma etapa); E17 na B depois da E15 (misturaria cliente e medição na mesma branch, sem ganho de tempo).
- Impacto se errada: uma branch a mais no fim do lote; a E17 pode voltar para a A depois da E06 sem mudar o escopo.
- O nome "ondas" fica reservado às ondas de tarefas e às da curadoria; a tabela de etapas por período passou a se chamar "Janelas".

### D11: um orquestrador aberto por vez (**[usuário]**, 2026-11-05)

Frase do usuário, repassada pela sessão que pediu a captura: "nao quero trabalhar com mais de um orquestrador aberto por vez, o paralelismo subsequente tem que ser feito pelo mesmo orquestrador".

Desenho **[arquiteto]**:

- As trilhas continuam como agrupamento, com os mesmos worktrees e branches, mas uma sessão executa todas.
- Até 2 etapas `#em-andamento` ao mesmo tempo, de trilhas diferentes, cada uma com plano, ledger e workspace próprios.
- Havendo vaga, abre a primeira `#pendente` elegível de uma trilha sem etapa aberta: ordem A, B, C entre trilhas e a do documento dentro da trilha.
- Duas etapas abertas nunca editam o mesmo arquivo versionado; a "File Structure" dos planos é comparada antes da revisão do segundo plano. Exceção: o roadmap, em que cada etapa edita só o que é seu.
- Depois de compactação, valem os ledgers e o roadmap de cada branch, não a lembrança da sessão.
- Com outra etapa aberta, parar significa não abrir etapa nova, terminar a aberta e fechar o lote.
- Fim do lote: merge local na `main` de cada branch de trilha, uma por vez, na ordem A, B, C, com gate e `merge --no-ff`. O push fica com o usuário.
- Descartadas: uma sessão por trilha (recusada pelo usuário); uma sessão sem etapas simultâneas (perderia a E15 e a E17 em paralelo com a E06); 3 etapas abertas (três planos, ledgers e revisões no mesmo contexto aumentam a compactação e o risco de confusão).
- Risco: se a sessão se confundir entre as etapas, baixar para 1 etapa aberta no prompt; as ondas continuam.

## Janela de release 0.6.0

Decisões de 2026-11-08 para uma execução com prazo fixo.

- **D16** **[usuário; desenho do arquiteto]**: parada às 10:00 de 2026-11-09 com os arquivos da 0.6.0 prontos. A execução é limitada pelo relógio, não pelo número de etapas. O prazo corta escopo, nunca revisão ou gate. Etapa que não fecha até o corte fica fora da versão e continua na branch dela. Descartadas: limite de 3 etapas; build só no fim (uma falha às 8h perderia a entrega); cortar revisões.
- **D17** **[usuário, por entrevista]**: a leitura vetorial nova segue desligada por padrão (`ZENY_SERVER_SYMBOL_COMPOSITION=false`), opcional por configuração; sem ligar a opção, a leitura de símbolos é igual à da 0.5.0. Descartada: kit com a opção ligada, sem prova cega.
- **D18** **[usuário, por entrevista]**: a revisão humana da E07 fica para depois da release. Em troca, com a opção desligada, E07 e E08 não podem mudar a saída da análise padrão. Se a revisão reprovar, as duas são corrigidas numa versão seguinte.
- **D19** **[arquiteto]**: a E07 depende da E06.3.3.2.2 e abre sem esperar E06.3.4 e E06.3.5, que vão para a trilha B. Descartada: fila única, que gastaria cerca de 7 h da janela antes de abrir a E07.
- **D20** **[arquiteto, após builder check]**: cada etapa ou subetapa integra na `main` ao fechar. A release final é gerada em pasta separada e só troca a oficial depois de conferida. Toda parada, exceto push, deploy e segredo, estaciona a etapa. Descartadas: integrar tudo no corte; build direto na pasta oficial (`build_release` apaga o destino antes de mover o novo, e uma interrupção nesse ponto eliminaria a candidata).
- Etapas novas: E18 (versão 0.6.0 e candidata de segurança) e E19 (release final gerada da `main` integrada).

Marcos planejados (horário de Brasília):

| Quando | Marco |
|---|---|
| 22:00 de 08/11 | Conferência da candidata |
| 05:00 de 09/11 | Não abre etapa nova |
| 06:30 de 09/11 | Corte de trabalho |
| 07:15 de 09/11 | Limite de fechamento |
| 07:45 de 09/11 | Início da E19 |
| 09:00 de 09/11 | Corte do build |
| 09:30 de 09/11 | Sessão encerrada |
| 10:00 de 09/11 | Prazo |

O roadmap prevê recalcular os marcos de 05:00 a 07:45 pelo tempo de build medido na E18, se 1,25 vez esse tempo passar de 75 min.

## Conferência do curador em 2026-11-09

Leitura do repositório do projeto (branch `main`, working tree limpa):

- O roadmap marca E18 e E19 como `#concluida`. O commit `fe2c672`, "docs: E19 concluida com a release final 0.6.0", é de 2026-11-09 07:24 -03:00.
- O roadmap data D6 e D7 de 2026-11-04, o mesmo dia que o design atribui à entrevista. A divergência apontada na captura df5912d5 não aparece mais.
- Não conferi os arquivos da release nem se os marcos foram recalculados.

## Incertezas

- O teto de ~4 desenvolvedores, a tabela 3/2 e as 2 etapas simultâneas não tinham sido testados sob carga real quando foram capturados; não há registro no vault do resultado.
- O ganho do `pytest-xdist` (estimativa de 26 min para 3–6 min) não foi medido nas capturas.
- A carga de 60 processos e o achado I-2 vêm do handoff da E14, que considera o caso "provavelmente resolvido", com risco residual aberto.
- A explicação de D12 e D13, citadas pela D17, está no roadmap e não foi capturada.

## Padrões possivelmente reutilizáveis

Interpretações de agentes, não princípios registrados pelo usuário e ainda não testadas fora deste projeto.

- **Separar exploração de produção** (agente que registrou a captura): calibração contra dado real não deve passar pelo ciclo completo de qualidade a cada iteração. Explorar em laboratório paralelo, descartável e sem commit, e passar o vencedor uma vez pelo ciclo. Condição: existir métrica objetiva para escolher a vencedora.
- **Limitar paralelismo empilhado na origem** (agentes que registraram as capturas): quando sessões, tarefas e hipóteses se multiplicam, o limite precisa valer para a máquina e ser recalculado ao abrir cada nível. Com um único orquestrador, a sessão conhece todas as suítes que dispara e o limite da sessão coincide com o da máquina; o custo é o contexto da sessão, e por isso o número de etapas simultâneas fica baixo.
- **Execução limitada por relógio** (curador, a partir do "Por que registrar" da captura 731fe7d4): o prazo corta escopo e nunca revisão ou gate, uma candidata de segurança sai cedo, a `main` fica sempre pronta para o build e a release final só substitui a oficial depois de conferida. Condição: etapas que integram sozinhas ao fechar.

## Relações

- [[ZenyProjectHandler - Leitura vetorial por poste e detector local]]: decisões técnicas executadas por este processo.
- [[Souls - alma personalizada para cada agente de desenvolvimento]]: as souls `orquestrador`, `arquiteto` e `desenvolvedor` citadas aqui.
- [[Decidir pendências do usuário por entrevista com opção recomendada]]: D6, D17 e D18 foram decididas por entrevista.

## Proveniência

- 2026-11-09 — [[2026-11-05 - ZenyProjectHandler - decisão execução acelerada leitura-vetorial-por-poste - df5912d5]] (capture_id: df5912d5-1f3e-48b4-9f24-fbb0f3e7a419): problema medido, D6, D7, propostas da D8, alternativas e aprendizado sobre laboratório.
- 2026-11-09 — [[2026-11-05 - ZenyProjectHandler - decisões D9 e D10 leitura-vetorial-por-poste - 1ecf9413]] (capture_id: 1ecf9413-8dda-4969-9487-6fbd3965658d): D10, regras de retomada e aprendizado sobre paralelismo; a versão original da D9 foi substituída pela captura d3c635af.
- 2026-11-09 — [[2026-11-05 - ZenyProjectHandler - decisão D11 um orquestrador por vez e revisão de D9 e D10 leitura-vetorial-por-poste - d3c635af]] (capture_id: d3c635af-659c-46d8-ae82-bb5cc92a32e6): D11, D9 e D10 revistas e indicação dos trechos substituídos.
- 2026-11-09 — [[2026-11-08 - ZenyProjectHandler - decisões D16 a D20 janela de release 0.6.0 - 731fe7d4]] (capture_id: 731fe7d4-6520-486e-8b7c-59f403040bac): D16 a D20, etapas E18 e E19 e marcos da janela; o padrão de execução limitada por relógio é interpretação do curador.
- 2026-11-09 — sessão curadora: desfecho da D8, datas de D6 e D7 e estado de E18 e E19, lidos no roadmap do projeto.
