---
type: capture
status: archived
created: 2026-11-16
capture_id: 0cc1844e-038a-4163-83d7-abbb4b4c6ffd
---

# ZenyHotelManager-DesktopFront - ADR 0011 processo acelerado até a demo

## Conteúdo capturado

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

## Contexto

Surgiu no ZenyHotelManager-DesktopFront, o cliente desktop em Compose Multiplatform do Zeny Hotel Manager, logo depois do merge da M0 E03 (`a300a23`, "merge: M0 E03 (roadmap/m0-sincronizacao)"). O roadmap é executado com as souls `orquestrador`, `desenvolvedor`, `testador`, `revisor-seguranca` e `revisor-arquitetura`. A decisão foi tomada pelo usuário para caber no prazo da demo de 17/11.

## Origem

- Projeto: ZenyHotelManager-DesktopFront, repositório local `/home/caio/repos/ZenyHotelManager-DesktopFront`.
- Arquivo: `docs/adr/0011-processo-acelerado-ate-a-demo.md` (seções "Contexto", "Decisão", "Alternativas descartadas", "Consequências").
- Soul citada pelo ADR: `~/.claude/agents/second-brain-souls/orquestrador.md`, passos 2, 3, 3.2, 3a, 3.5 e 5.
- Commit: o ADR ainda não tinha commit. Segundo o snapshot do `git status` da sessão que me chamou, o arquivo estava não rastreado e o `CLAUDE.md` do projeto estava modificado, com HEAD em `a300a23` no branch `main`.

## Por que registrar

Registra uma exceção de processo ao fluxo das souls: o que foi cortado, o que continua valendo e a dívida de revisão que fica pendente. Serve para lembrar de pagar a dívida (`a300a23..HEAD`) quando a decisão for revogada e para comparar com outras execuções aceleradas.

Interpretação do agente: é o segundo caso registrado de execução acelerada com as souls. O primeiro é a do ZenyProjectHandler (2026-11-05). Lá o paralelismo veio de trilhas e laboratório, e as mudanças nas souls ficaram como proposta pendente (D8). Aqui o corte é de cerimônia de revisão, e a mudança nas souls foi descartada de propósito.

## Limitações e incertezas

- O ADR estava sem commit no momento da captura e pode mudar antes do commit. Não foi copiado para o vault; só existe no caminho local acima.
- Não consegui confirmar o HEAD nem o `git status` por conta própria (a trava do escriba bloqueou `git -C`). Os dados vêm do pedido e do snapshot da sessão.
- Não li o diff do `CLAUDE.md` do projeto e não sei se ele já cita o ADR 0011.
- A medição de ~1h30 para três tarefas é do ADR. Não a verifiquei no `git log`.
- Os passos da soul `orquestrador` são citados como o ADR os numera. Não conferi a soul.
- Não se sabe se o orquestrador aceita fechar etapas sem "revisão limpa" com base neste ADR. O próprio ADR trata isso como risco.

## Possíveis conexões

- [[Souls - alma personalizada para cada agente de desenvolvimento]]: fluxo das souls e do orquestrador.
- [[ZenyProjectHandler - Execução acelerada do roadmap de leitura vetorial]]: caso anterior de execução acelerada.
- [[ZenyHotelManager]]: projeto relacionado. O DesktopFront não tem nota própria no vault.
- [[Decidir pendências do usuário por entrevista com opção recomendada]]: a decisão foi tomada por entrevista, conforme o `CLAUDE.md` do projeto.
- Capturas anteriores do DesktopFront na Inbox: [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]], [[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]].
- Temas sem nota (texto simples): ZenyHotelManager-DesktopFront; dívida de revisão; ondas paralelas de tarefas.
