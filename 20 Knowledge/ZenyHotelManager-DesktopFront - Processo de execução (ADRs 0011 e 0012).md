---
type: knowledge
status: processed
created: 2026-11-17
projects:
  - "[[ZenyHotelManager-DesktopFront]]"
sources:
  - "[[2026-11-16 - ZenyHotelManager-DesktopFront - ADR 0011 processo acelerado até a demo - 0cc1844e]]"
  - "[[2026-11-17 - ZenyHotelManager-DesktopFront - ADR 0012 revoga o processo acelerado e atualização dos roadmaps - 10b921ef]]"
---
# ZenyHotelManager-DesktopFront - Processo de execução (ADRs 0011 e 0012)

Referência do projeto [[ZenyHotelManager-DesktopFront]]: a exceção de processo ao fluxo das souls aceita em 2026-11-16 (ADR 0011), a revogação dela em 2026-11-17 (ADR 0012) e a dívida de revisão que ficou. **Vale hoje o ciclo padrão do orquestrador**; o ADR 0011 fica como registro. Decisão específica deste repositório, não uma regra geral das souls. Leia antes de executar uma etapa ou de tratar a M3 E06.

Texto das capturas do `brain-escriba` (resumos do agente feitos a partir dos documentos do repositório), integrado sem resumo nem reescrita; cada bloco indica a captura de origem. A fonte da verdade são os arquivos do repositório `/home/caio/repos/ZenyHotelManager-DesktopFront`. As notas do curador estão marcadas como tal.

## ADR 0011 — processo acelerado até a demo (2026-11-16; revogado em 2026-11-17)

Origem: [[2026-11-16 - ZenyHotelManager-DesktopFront - ADR 0011 processo acelerado até a demo - 0cc1844e]].

Decisão: em 2026-11-16 o usuário aceitou o ADR 0011 do ZenyHotelManager-DesktopFront ("Processo acelerado: testador por etapa, mais paralelismo e revisão de segurança adiada"). Vale só neste repositório, a partir do commit `a300a23` e até o usuário revogar. É uma exceção local ao fluxo das souls. As souls não mudam.

Resumo do agente, a partir do ADR:

### Contexto (fatos que o ADR registra)

- A demo é em 17/11 (ADR 0006 do projeto, marcos por valor de demo).
- Na M0 E03, três tarefas pequenas levaram cerca de 1h30 (22:34 a 00:05 de 15/11, segundo o `git log` de `a300a23^1..a300a23^2`). Quase todo esse tempo foi custo fixo por tarefa: desenvolvedor, testador, verificação mecânica e `revisor-seguranca`, tudo em série. No fim da etapa ainda entram o testador de etapa, o scanner e a revisão final.
- O sistema roda só localmente, sem dado real e sem exposição externa até a demo.

### Decisão (três pontos)

1. **Testador só por etapa.** O orquestrador planeja toda tarefa como `Risco: normal`, então o `testador` não roda por tarefa (passo 3.2 do orquestrador). Roda uma vez por etapa, sobre `MERGE_BASE..HEAD` (passo 5).
2. **Mais paralelismo.** O plano é escrito para formar ondas: tarefas com arquivos disjuntos (contando testes, configuração de build e lockfiles) e `Depende de:` só quando a dependência é real. O limite continua em 3 tarefas por onda, porque a memória da máquina é curta ("daemon disappeared") e o `~/.gradle` é compartilhado com o servidor.
3. **Sem `revisor-seguranca` e sem scanner.** A revisora não é despachada nem por tarefa (passo 3.5) nem na revisão final (passo 5). O scanner de dependências também fica adiado, porque julga o estado do HEAD e vai rodar uma vez só, na revisão futura.

### O que continua valendo

- A revisão do plano pelo `revisor-arquitetura` (passo 2).
- A conferência de cada despacho (trailers e `git status` limpo).
- A `check_test_integrity.py` por tarefa e por etapa, com a saída guardada no workspace. Exit 2 para tudo. Apontamentos e avisos não bloqueiam: vão para o ledger e o handoff, à espera da revisão futura.
- Suíte verde por tarefa e por onda, e o gate do projeto antes do merge na principal.
- A evidência de cada critério de aceite, que o orquestrador confere sozinho, já que não há revisora para conferir a conformidade com a spec.

### Fechamento da etapa

No lugar da "revisão limpa", a etapa exige suíte verde, gate verde e a evidência de cada critério de aceite. Pode fechar `#concluida`, e o handoff registra "revisão de segurança adiada (ADR 0011)" e o intervalo de commits da etapa.

### Dívida de revisão

Quando o usuário revogar a decisão, a primeira execução do orquestrador despacha a `revisor-seguranca` com o prompt `code-reviewer.md` sobre `a300a23..HEAD` da principal, junto com o scanner e a `check_test_integrity.py --base a300a23`. Os achados viram uma etapa de correção no roadmap.

### Alternativas descartadas

- Manter o processo completo: não cabe no prazo da demo.
- Manter a revisora só na revisão final da etapa: corta menos tempo do que o usuário pediu, e o risco de adiar é baixo enquanto tudo roda localmente.
- Subir o limite de onda acima de 3: builds Gradle paralelos em vários worktrees esbarram na memória. O ganho vem de planos com tarefas mais independentes, não de um limite maior.
- Mudar as souls: elas são globais e servem a outros projetos. A exceção é deste repositório e fica no ADR.

### Consequências registradas no ADR

- Cada tarefa vira desenvolvedor, suíte, verificação mecânica e integração. Ninguém revisa o código até a dívida ser paga.
- A conformidade de cada tarefa com a spec depende da evidência que o orquestrador confere. Desvios podem aparecer só na demo ou na revisão futura.
- A revisão futura cobre um intervalo grande de uma vez e tende a gerar uma etapa de correção maior.
- O texto da soul `orquestrador` recusa fechar uma etapa sem "revisão limpa". A decisão depende de o orquestrador aceitar o `CLAUDE.md` do projeto como instrução do usuário. O prompt da execução deve citar o ADR. Se o orquestrador recusar, a saída é mudar a soul numa sessão comum.

## ADR 0012 — revoga o processo acelerado (2026-11-17)

Origem: [[2026-11-17 - ZenyHotelManager-DesktopFront - ADR 0012 revoga o processo acelerado e atualização dos roadmaps - 10b921ef]].

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

As mudanças nos roadmaps M0 a M7 do mesmo commit estão em [[ZenyHotelManager-DesktopFront - Marcos, roadmaps e demo]].

## Estado da dívida de revisão

*Nota do curador (conferência por `git` em 2026-11-17, só leitura):* na `main` do front (`6ffc9f3`, "merge: M3 E05 e início da E06"), a M3 E06 está `#em-andamento`. O histórico de `docs/roadmaps/README.md` registra que o pacote de `a800b25` foi gerado na E06 com as correções da revisão adiada, que falta a revisão final e que a lista "Revisões de segurança adiadas" ainda não tem a marca de paga. A lista tem os quatro itens que a captura descreve (M3 E02, E03, E04 e o trecho `830f296..920dcd2` da E05). O M4 só começa com a M3 E06 `#concluida`.

## Interpretações do agente das capturas

- Da captura de 2026-11-16: é o segundo caso registrado de execução acelerada com as souls. O primeiro é a do ZenyProjectHandler (2026-11-05). Lá o paralelismo veio de trilhas e laboratório, e as mudanças nas souls ficaram como proposta pendente (D8). Aqui o corte é de cerimônia de revisão, e a mudança nas souls foi descartada de propósito.
- Da captura de 2026-11-17: é o primeiro repositório registrado na Inbox a adotar o ciclo novo das souls (gate de integração, `## Ondas`, lista fechada de `Risco: alto`). O ADR 0011 tinha descartado "mudar as souls"; a revogação veio justamente porque elas mudaram. A meta de 4 a 6 horas por rodada continua sendo projeção.

## Limitações registradas nas capturas

Da captura de 2026-11-16:

- O ADR estava sem commit no momento da captura e pode mudar antes do commit. Não foi copiado para o vault; só existe no caminho local acima.
- Não consegui confirmar o HEAD nem o `git status` por conta própria (a trava do escriba bloqueou `git -C`). Os dados vêm do pedido e do snapshot da sessão.
- Não li o diff do `CLAUDE.md` do projeto e não sei se ele já cita o ADR 0011.
- A medição de ~1h30 para três tarefas é do ADR. Não a verifiquei no `git log`.
- Os passos da soul `orquestrador` são citados como o ADR os numera. Não conferi a soul.
- Não se sabe se o orquestrador aceita fechar etapas sem "revisão limpa" com base neste ADR. O próprio ADR trata isso como risco.

Da captura de 2026-11-17:

- Os arquivos não foram copiados para o vault. Só existem no repositório local, nos caminhos acima.
- O commit `3c7c9de` é local: o `git status` mostrava a `main` um commit à frente de `origin/main`. Não sei se houve push.
- Não li o corpo atual dos roadmaps M0 a M2 e M4 a M7, só os diffs do commit. Li o diff inteiro do M3.
- A lista de etapas do M4 ao M7 que ganharam notas vem do histórico de cada roadmap e bate com os trechos do diff que li. Não conferi se as partes apontadas como independentes de fato o são no contrato do servidor.
- As medições (227 execuções de `./gradlew build`, 1 a 2 minutos por despacho da revisora, 2,5 h e 2,0 h) são do ADR 0012 e do `DESIGN-desempenho.md`. Não as verifiquei nos transcritos.
- Não conferi a soul `orquestrador` instalada nem a presença do `osv-scanner`. O ADR afirma os dois.
- A entrevista em que o usuário decidiu a dívida não me foi mostrada. O registro dela está no ADR 0012 (item 6), no README (regra 8 e histórico) e no pedido.
- Diferença em relação à captura do ADR 0011: aquela descreve a dívida como paga "na primeira execução do orquestrador" depois da revogação. O texto atual do ADR 0011 diz que o usuário a paga "num marco final de análise do projeto". O commit `3c7c9de` só mudou a linha de estado do ADR 0011, então o parágrafo mudou antes, entre a captura de 2026-11-16 (quando o ADR ainda não tinha commit) e o HEAD `3d9b272`. Não rastreei em que commit.
- A M3 E06 está `#pendente`, e a dívida ainda não foi paga.

---

## Proveniência

- 2026-11-17 — [[2026-11-16 - ZenyHotelManager-DesktopFront - ADR 0011 processo acelerado até a demo - 0cc1844e]] (capture_id: 0cc1844e-038a-4163-83d7-abbb4b4c6ffd): ADR 0011 (processo acelerado), interpretação do agente e limitações; nota criada pelo curador.
- 2026-11-17 — [[2026-11-17 - ZenyHotelManager-DesktopFront - ADR 0012 revoga o processo acelerado e atualização dos roadmaps - 10b921ef]] (capture_id: 10b921ef-c99f-44a2-a0ac-77ac16591dbe): ADR 0012 (revogação), atualização do `CLAUDE.md`, do ADR 0011 e do README dos roadmaps, interpretação do agente e limitações.
