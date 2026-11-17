---
type: capture
status: archived
created: 2026-11-17
capture_id: 10b921ef-c99f-44a2-a0ac-77ac16591dbe
---

# ZenyHotelManager-DesktopFront - ADR 0012 revoga o processo acelerado e atualização dos roadmaps

Sucede a captura [[2026-11-16 - ZenyHotelManager-DesktopFront - ADR 0011 processo acelerado até a demo - 0cc1844e]] (`capture_id: 0cc1844e-038a-4163-83d7-abbb4b4c6ffd`). Aquela registra a exceção de processo; esta registra a revogação dela e o que mudou nos documentos do projeto.

## Conteúdo capturado

Decisão: em 2026-11-17 o usuário aceitou o ADR 0012 do ZenyHotelManager-DesktopFront ("Revoga o processo acelerado: volta o ciclo padrão das souls"). O ADR 0011 fica revogado a partir do commit que registra o ADR 0012, e nenhuma etapa nova entra pelo processo acelerado.

Decisão do usuário, por entrevista, em 2026-11-17, pela opção recomendada: a dívida de revisão do processo acelerado (`a300a23..HEAD`) é paga antes do M4, numa etapa nova, a M3 E06 ("Revisão adiada do processo acelerado"). O M4 só começa com a M3 E06 `#concluida`.

O restante desta seção é resumo do agente, a partir dos arquivos listados em "Origem".

### Motivo da revogação (o que o ADR 0012 registra)

- O ADR 0011 valia "até segunda ordem" do usuário. O ADR 0012 é essa segunda ordem.
- Em 2026-11-17 as souls mudaram no Second Brain (`99 System/Souls/DESIGN-desempenho.md`), e o ciclo padrão passou a trazer o que o ADR 0011 buscava:
  - o `testador` roda por tarefa só em `Risco: alto`, e `alto` virou uma lista fechada: autenticação ou autorização; dado pessoal ou segredo; cálculo de valor monetário; migração ou escrita destrutiva de dados; concorrência; parsing de entrada externa não confiável. Ele roda uma vez por etapa, sobre o diff inteiro;
  - o plano traz a seção `## Ondas`, e `Depende de:` só vale quando a tarefa usa símbolo ou arquivo que a outra cria;
  - o gate do projeto sai de dentro de cada agente e passa a rodar com o orquestrador, nos pontos de integração ("gate de integração"). Desenvolvedor e testador rodam a verificação da tarefa, pela linha `verificação rápida` do `CLAUDE.md`.
- A medição que sustentou a mudança das souls mostrou que a `revisor-seguranca` não era a causa da lentidão: ela custa de 1 a 2 minutos por despacho, de 3% a 5% da sessão. O tempo ia para o gate completo rodado dentro do laço de cada agente (227 execuções de `./gradlew build` numa sessão de 37 tarefas) e para o testador em quase toda tarefa.
- A sessão deste repositório sob o ADR 0011 (16/11) fez a M3 E03 em 2,5 h e a M3 E04 em 2,0 h. É o dado real que o desenho novo usa como referência.
- Pré-condição que o ADR diz ter conferido: o `orquestrador.md` instalado traz o "Gate de integração" (passo 3a), e o `osv-scanner` está no `PATH` da máquina.

### O que o ADR 0012 decide (seis itens)

1. O ADR 0011 está revogado.
2. Vale o ciclo padrão do orquestrador, inteiro: a `revisor-seguranca` em cada tarefa e na revisão final, o scanner de dependências, o testador por tarefa na lista fechada de `Risco: alto` e uma vez por etapa, os planos com `## Ondas` e o gate de integração. A etapa só fecha `#concluida` com a revisão final limpa e a evidência de cada critério de aceite.
3. `CLAUDE.md`: sai a seção "Processo acelerado (até segunda ordem)", e a tabela de comandos ganha a linha `verificação rápida`. A linha `gate do projeto` não muda.
4. Roadmaps: a seção "Prompt acelerado" sai de todos. O "Protocolo de execução" e o "Prompt de execução" não mudam, porque já remetem ao orquestrador para o ciclo por tarefa. A regra 8 de `docs/roadmaps/README.md` fica encerrada.
5. M3 E05, iniciada no processo acelerado: não é reescrita. O restante segue o processo normal, e o trecho já commitado (`830f296..920dcd2`) entra na lista "Revisões de segurança adiadas".
6. Dívida de revisão: paga antes do M4, na M3 E06 (decisão do usuário acima). Este item substitui o parágrafo "Dívida de revisão" do ADR 0011, que deixava o pagamento para um marco final de análise do projeto.

Do ADR 0011 ficam, como registro, as linhas `Revisão de segurança: adiada (ADR 0011)` nos handoffs das etapas que fecharam por ele e a lista "Revisões de segurança adiadas" do README, que é o escopo da dívida até a M3 E06 marcá-la como paga.

### Alternativas descartadas (do ADR 0012)

- Manter o ADR 0011 até o fim do M3: a E05 é o gate do marco e a build de demo. Fechá-la sem revisão aumentaria a dívida sem ganho de tempo relevante.
- Manter só a parte "sem `revisor-seguranca`": a medição mostrou que ela não era a causa da lentidão.
- Replanejar a M3 E05 pelo ciclo novo: o plano é do orquestrador, e a etapa já tem trabalho commitado e trabalho guardado no workspace. O orquestrador novo aceita plano sem `## Ondas` (cada tarefa restante vira uma onda de uma tarefa só).
- Dar a dívida por paga com as revisões finais das próximas etapas: a revisão final de uma etapa cobre só o intervalo dela. O código da M3 E03 e da M3 E04 nunca foi lido por uma revisora.
- Dívida no marco final de análise (o que o ADR 0011 previa): o intervalo `a300a23..HEAD` cresceria com o M4 ao M7, e um achado em reservas custaria mais depois que contas e check-out dependessem dele.
- Dívida num roadmap próprio entre o M3 e o M4: daria um arquivo e uma rodada só para uma etapa. A etapa cabe no roadmap do M3, onde está o código devido.

### Consequências (do ADR 0012)

- Cada tarefa volta a ter revisão de código antes de ser integrada, e cada etapa volta a ter scanner e revisão final. A rodada fica mais lenta do que sob o ADR 0011. A meta do desenho novo (rodada de 3 a 4 etapas em 4 a 6 horas) é projeção e ainda não foi medida neste repositório.
- A verificação rápida usa `ktlintCheck` e `detekt`. O `detektMain` e o `detektTest`, com resolução de tipos, rodam só no `check`, isto é, no gate de integração: um achado deles aparece no gate da onda, não dentro da tarefa.
- O plano da M3 E05 continua com todas as tarefas `Risco: normal` e sem `## Ondas`. Rever o risco ou acrescentar as ondas fica com o orquestrador.
- O M3 passa a ter seis etapas. A E06 pode mudar código depois do pacote do gate (E05) e, nesse caso, gera o pacote de novo.
- A E06 é uma etapa incomum: a revisão vem antes do plano, e o tamanho da correção só se conhece depois dela. Se os achados não couberem num plano, o orquestrador para e relata, e as etapas de correção que faltarem são criadas numa sessão do arquiteto.
- Os planos já escritos em `docs/superpowers/plans/` citam o ADR 0011 e ficam como estão.

### Atualização dos documentos do projeto

**`CLAUDE.md`**

- Removida a seção "Processo acelerado (até segunda ordem)".
- Linha nova na tabela de comandos, `verificação rápida` (citação literal do comando):

  ```
  ./gradlew :<módulo>:test --tests '<filtro>' :<módulo>:ktlintCheck :<módulo>:detekt
  ```

  `<módulo>` é `sdk`, `core`, `design`, `app` ou `demo-seed`, e `<filtro>` é a classe ou o padrão dos testes do que a tarefa tocou. Roda-se um trio por módulo tocado e por módulo que usa o que mudou (`sdk` → `core` → `design`, `app` e `demo-seed`; `design` → `app`). Para script de `tools/` ou `tests/`: `bash tests/run.sh tests/<arquivo>.sh`. O ADR diz que a forma foi validada com `./gradlew -m` nos cinco módulos.
- A linha `gate do projeto` (`./gradlew build` + `bash tests/run.sh`) não mudou.

**`docs/adr/0011-processo-acelerado-ate-a-demo.md`**

- Só a linha de estado mudou: de "aceita · 2026-11-16 · decidida pelo usuário, vale até segunda ordem dele" para "revogada em 2026-11-17 pelo ADR 0012".

**`docs/roadmaps/README.md`**

- Regra 8 reescrita como "Processo acelerado (revogado)": valeu de 2026-11-16 a 2026-11-17. Desde a revogação, nenhuma etapa nova entra por ela, toda execução segue o ciclo completo do orquestrador, e a dívida é paga antes do M4, na M3 E06.
- Mapa dos marcos: o M3 passa a ter 6 etapas, e o M4 depende de "M3, com a E06".
- Lista "Revisões de segurança adiadas": a M3 E06 paga a lista inteira. Ela tem quatro itens:
  1. M3 E02, `b6aafa9..2ad4b09`, integridade exit 1;
  2. M3 E03, `5cbac31..87f03cb`, integridade exit 1;
  3. M3 E04, `fc7a0b3..72e4316`, integridade exit 1;
  4. M3 E05, só o trecho anterior à revogação, `830f296..920dcd2`, integridade exit 0 e nenhum apontamento (item novo). Só a Task 1 tem código (`e8a1542..920dcd2`: o `FutureSeeder` e a porta `FutureGateway`, no `demo-seed`), sem revisão de código nem testador.
- "Histórico de revisões": entrada de 2026-11-17 com a revogação.

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

## Contexto

Surgiu no ZenyHotelManager-DesktopFront, o cliente desktop em Compose Multiplatform do Zeny Hotel Manager, numa sessão da soul `arquiteto` em 2026-11-17, logo depois do fim do lote do M3 executado pelo processo acelerado (E02, E03 e E04 concluídas; E05 em andamento, com a Task 1 integrada). No mesmo dia, o usuário aprovou o design de desempenho das souls no vault, que mudou o ciclo padrão do orquestrador.

## Origem

- Projeto: ZenyHotelManager-DesktopFront, repositório local `/home/caio/repos/ZenyHotelManager-DesktopFront`, branch `main`.
- Quem pediu a captura: a soul `arquiteto`, em sessão de 2026-11-17.
- Arquivos lidos:
  - `docs/adr/0012-revoga-o-processo-acelerado.md` (inteiro);
  - `docs/adr/0011-processo-acelerado-ate-a-demo.md` (inteiro);
  - `docs/roadmaps/README.md` (inteiro);
  - `CLAUDE.md` (inteiro);
  - `docs/roadmaps/roadmap-m0-sincronizacao.md` a `roadmap-m7-gestao-cadastros.md`, pelo diff do commit abaixo.
- Contexto no vault: `99 System/Souls/DESIGN-desempenho.md` (nota de implementação e §1 a §5.3 lidas).
- Commit:
  - o pedido dizia que o commit ainda não existia e seria feito na `main` logo depois da captura, a partir do HEAD `3d9b272`, com o trailer `Soul: arquiteto`;
  - no começo da captura, o `git status` mostrava as mudanças sem commit sobre o HEAD `3d9b27274b8f859c2f5484a56c07f1df08742248`;
  - durante a captura, apareceu na `main` o commit `3c7c9def150e0c3399cfec9f6a1c501e74a1eaad`, "Revoga o processo acelerado e adequa os roadmaps ao ciclo novo das souls (ADR 0012)", de 2026-11-17 02:55:43 -0300, com o pai `3d9b272` e o trailer `Soul: arquiteto`. Ele toca 12 arquivos (o `CLAUDE.md`, os dois ADRs, o README dos roadmaps e os oito roadmaps). Conferi o hash e o conteúdo com `git log` e `git show`. Os diffs citados nesta captura são os desse commit.

## Por que registrar

Fecha o ciclo aberto pela captura do ADR 0011: a exceção de processo acabou, e a dívida de revisão que ela deixou tem etapa e momento definidos (M3 E06, antes do M4). Registra também a linha `verificação rápida`, que o ciclo novo das souls espera encontrar no `CLAUDE.md` de cada projeto.

Interpretação do agente: é o primeiro repositório registrado na Inbox a adotar o ciclo novo das souls (gate de integração, `## Ondas`, lista fechada de `Risco: alto`). O ADR 0011 tinha descartado "mudar as souls"; a revogação veio justamente porque elas mudaram. A meta de 4 a 6 horas por rodada continua sendo projeção.

## Limitações e incertezas

- Os arquivos não foram copiados para o vault. Só existem no repositório local, nos caminhos acima.
- O commit `3c7c9de` é local: o `git status` mostrava a `main` um commit à frente de `origin/main`. Não sei se houve push.
- Não li o corpo atual dos roadmaps M0 a M2 e M4 a M7, só os diffs do commit. Li o diff inteiro do M3.
- A lista de etapas do M4 ao M7 que ganharam notas vem do histórico de cada roadmap e bate com os trechos do diff que li. Não conferi se as partes apontadas como independentes de fato o são no contrato do servidor.
- As medições (227 execuções de `./gradlew build`, 1 a 2 minutos por despacho da revisora, 2,5 h e 2,0 h) são do ADR 0012 e do `DESIGN-desempenho.md`. Não as verifiquei nos transcritos.
- Não conferi a soul `orquestrador` instalada nem a presença do `osv-scanner`. O ADR afirma os dois.
- A entrevista em que o usuário decidiu a dívida não me foi mostrada. O registro dela está no ADR 0012 (item 6), no README (regra 8 e histórico) e no pedido.
- Diferença em relação à captura do ADR 0011: aquela descreve a dívida como paga "na primeira execução do orquestrador" depois da revogação. O texto atual do ADR 0011 diz que o usuário a paga "num marco final de análise do projeto". O commit `3c7c9de` só mudou a linha de estado do ADR 0011, então o parágrafo mudou antes, entre a captura de 2026-11-16 (quando o ADR ainda não tinha commit) e o HEAD `3d9b272`. Não rastreei em que commit.
- A M3 E06 está `#pendente`, e a dívida ainda não foi paga.

## Possíveis conexões

- [[2026-11-16 - ZenyHotelManager-DesktopFront - ADR 0011 processo acelerado até a demo - 0cc1844e]]: a decisão que esta revoga.
- [[Souls - alma personalizada para cada agente de desenvolvimento]]: fluxo das souls e do orquestrador. O design de desempenho que motivou a revogação está em `99 System/Souls/DESIGN-desempenho.md`.
- [[ZenyProjectHandler - Execução acelerada do roadmap de leitura vetorial]]: outro caso de execução acelerada.
- [[Decidir pendências do usuário por entrevista com opção recomendada]]: a decisão da dívida foi tomada por entrevista, pela opção recomendada.
- [[ZenyHotelManager]]: projeto relacionado (o servidor). O DesktopFront não tem nota própria no vault.
- Capturas anteriores do DesktopFront na Inbox: [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]], [[2026-11-13 - ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão - 677b277a]], [[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]].
- Temas sem nota (texto simples): ZenyHotelManager-DesktopFront; dívida de revisão; gate de integração; verificação rápida por módulo; ondas paralelas de tarefas.
