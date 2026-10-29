# Souls — documento de design

> Em 2026-10-29 a soul `orquestrador-etapa` foi renomeada para `orquestrador`.

Status: rascunho para aprovação do usuário. Criado em 2026-10-27, a partir de uma entrevista com o usuário (brainstorming do superpowers, com as decisões tomadas em perguntas com opção recomendada, conforme [[Decidir pendências do usuário por entrevista com opção recomendada]]).

Ao longo do texto, **[usuário]** marca o que o usuário decidiu, e **[agente]** marca uma escolha do agente que escreveu este design, que o usuário pode revisar.

## 1. Intenção

O usuário está deixando mais robusto o seu modelo de desenvolvimento de software com IA. Uma *soul* é a "alma" de um agente especialista: a forma de pensar, as prioridades, o que o agente recusa fazer e os limites que de fato se impõem a ele. Nenhuma dor concreta motivou as souls. Elas são um investimento preventivo.

O que conta como sucesso, nas palavras do usuário: **ter segurança de que cada parte de uma etapa foi bem conduzida, porque foi entregue ao especialista certo**. Exemplos dados por ele:

- a soul de testes é, *por definição*, incapaz de forjar testes, e outra soul confere isso dentro da etapa;
- uma soul de segurança acrescenta uma camada de proteção ao código que vai para produção, barrando dependências comprometidas e erros bobos de código;
- **contexto carregado sob demanda**: cada agente nasce sabendo como agir e carrega só o que é relevante para o seu papel, sem ler documentação enorme para entender o próprio jeito de trabalhar.

Isso concretiza a direção registrada em [[Souls - alma personalizada para cada agente de desenvolvimento]] e preenche o espaço reservado para souls na skill `development-roadmap` (§7 "Papéis e Souls" e tabela de papéis em `references/template.md`).

## 2. Objetivos, não-objetivos e anti-objetivos

**Objetivos**

1. Seis souls: `orquestrador-etapa`, `desenvolvedor`, `testador`, `revisor-seguranca`, `brain-curador` e `brain-escriba`. **[usuário]** escolheu os papéis e decidiu que o Second Brain tem duas souls. **[agente]** escolheu os nomes.
2. Cada soul tem duas camadas: **identidade** (como pensa, o que prioriza, o que recusa) e **travas reais** (ferramentas, permissões e hooks que o Claude Code aplica, e não apenas pedidos no prompt). **[usuário]** confirmou e quer que essas camadas se estendam a papéis futuros.
3. As souls de desenvolvimento valem para **qualquer execução de plano do superpowers**, com ou sem roadmap **[usuário]**. A sequência desenvolvedor → testador → verificação → revisora fica no `orquestrador-etapa`. A skill `development-roadmap` só acrescenta o próprio protocolo (tags, handoffs, decisões) e passa a exigir as souls.
4. As souls ficam versionadas no vault e disponíveis em qualquer projeto e em qualquer máquina configurada.

**Não-objetivos (desta versão)**

- Souls para outros papéis, como planejador, documentação ou deploy. O formato deve permitir criá-las depois.
- Reescrever os prompts do superpowers ou criar um fork deles.
- Atualizar os roadmaps que já existem em repositórios de projeto, como o ZenyHotelManager M5–M10. Eles passam a usar as souls quando forem atualizados pela skill `development-roadmap`.
- Tornar o vault independente do Claude Code. As souls são específicas do Claude Code, como as skills.

**Anti-objetivos (o que tornaria isto um fracasso, mesmo funcionando)**

- Uma soul que é só "personalidade": um texto de tom sem travas, que não muda o que o agente consegue fazer.
- Uma soul que repete regras do vault ou do superpowers e precisa ser atualizada à mão quando essas fontes mudam. A soul *aponta* para a fonte da verdade e não a copia.
- Mais contexto carregado do que hoje. O propósito é carregar menos e de forma mais certeira.
- Um testador ou revisor que "aprova" sem evidência.

## 3. Anatomia de uma soul

Cada soul é um **subagente do Claude Code**: um arquivo Markdown com frontmatter YAML seguido do corpo, que vira o system prompt. **[usuário]**

- **Frontmatter (travas e configuração):** `name`, `description`, `tools` e/ou `disallowedTools`, `model`, `hooks` (hooks restritos ao agente, como `PreToolUse` em `Edit|Write`), `skills` (skills injetadas ao iniciar) e, se for útil, `permissionMode`, `effort` e `color`. Referência: documentação de subagentes do Claude Code (code.claude.com/docs/en/sub-agents).
- **Corpo (identidade), em português** **[usuário]**. Termos técnicos ficam em inglês quando esse é o nome real (TDD, supply chain). Seções sugeridas **[agente]**:
  1. *Quem sou*: o papel em uma ou duas frases.
  2. *O que prezo*: prioridades e critérios de qualidade, com opiniões que possam ser testadas.
  3. *O que recuso*: a lista do que a soul nunca faz, coerente com as travas do frontmatter.
  4. *Como trabalho*: o procedimento mínimo do papel e quais skills ou documentos ele abre, *e quando*.
  5. *Como entrego*: formato do relatório de saída e qual evidência é obrigatória.
  6. *Quando paro e pergunto*: quando escalar para o orquestrador ou para o usuário.
- **Tamanho:** curto. A referência da comunidade para SOUL.md varia de 30–80 linhas a 500–1.500 palavras. Material longo, como checklists de segurança, fica em arquivos de referência que a soul abre só quando precisa. **[agente]**

A soul define **quem** é o agente. O prompt do superpowers (implementer, task-reviewer, re-review) continua definindo **o quê** fazer naquela tarefa: o orquestrador despacha a soul como `subagent_type` e passa o prompt do superpowers como tarefa. **[usuário]** Para o modelo, vale o padrão `model: inherit`, e o orquestrador escolhe um modelo mais capaz no momento do despacho quando o protocolo pede (revisão final, rodadas de correção a partir da 4ª). **[agente]**

## 4. As seis souls

| Soul | Onde roda | Responsabilidade | Travas (mínimo) |
|---|---|---|---|
| `orquestrador-etapa` | sessão principal, via `claude --agent orquestrador-etapa` | Lê o roadmap e o estado da etapa, **faz o plano** (`superpowers:writing-plans`; ele absorve o papel de planejador **[usuário]**), distribui o trabalho para as outras souls, roda a verificação mecânica e fecha a etapa só com evidência. | Não escreve código de produção nem teste. Pode editar apenas o roadmap, o plano, o ledger e documentos de etapa. `tools` com `Agent(desenvolvedor, testador, revisor-seguranca, brain-escriba)` limita quem ele pode despachar. |
| `desenvolvedor` | subagente, uma vez por tarefa | Implementa com TDD (`superpowers:test-driven-development`) seguindo o prompt implementer do superpowers. **[usuário]** | Não altera nem apaga testes acrescentados pelo testador. Se um deles falhar, corrige o código. Não mexe em dependências fora do que o plano pede. |
| `testador` | subagente, **depois de cada tarefa** **[usuário]** | Analisa o que o desenvolvedor entregou, ataca a implementação e **completa** a suíte com casos de borda, erros, regressões e critérios de aceite. Roda tudo e relata com saída real. **[usuário]** | Só acrescenta testes: não altera código de produção nem apaga, enfraquece ou pula testes que já existem. Encontrou teste errado? Aponta e não reescreve. Nunca forja resultado, como assert trivial, mock do próprio sistema testado ou teste que não roda. |
| `revisor-seguranca` | subagente, **em cada tarefa (como revisor de tarefa) e na revisão final da etapa** **[usuário]** | Revisa código e testes quanto a segurança, boas práticas, aderência ao plano e **integridade dos testes**. Na revisão final, olha o diff inteiro da etapa com ênfase em dependências e supply chain: pacotes novos, typosquatting, versões com CVE, scripts de instalação, lockfile e segredos. | Somente leitura **por ferramenta**: sem `Edit`, sem `Write` e **sem Bash** (ruling do construtor em 2026-10-27, depois de duas rodadas de revisão mostrarem que restringir Bash por argumentos sempre deixa brechas). Pode consultar bases públicas de vulnerabilidade pela rede (WebFetch/WebSearch). Os scanners de dependência e a verificação mecânica são executados pelo **orquestrador**, que anexa as saídas ao pacote de revisão. **A revisão final exige scanner [usuário]:** se o pacote não trouxer saída de scanner para o stack do projeto, a revisão final bloqueia a etapa e o relatório **recomenda qual scanner instalar para aquele stack, com o link da documentação oficial de instalação** **[usuário]**. A soul mantém uma tabela curta stack → scanner recomendado → URL de instalação, verificada pelo construtor e sem URLs inventadas. Não aprova sem evidência. |
| `brain-curador` | sessão principal no vault, via `claude --agent brain-curador` | Opera o vault em modo curador: processa a Inbox, integra capturas e faz manutenção, seguindo o `AGENTS.md` e `99 System/AI/`. | As da política de mutação: mudanças estruturais, de schema ou de regra exigem proposta e autorização. Sem `push`. |
| `brain-escriba` | subagente, em projetos fora do vault | Consulta o brain e publica capturas na Inbox (por exemplo, a captura de fechamento de etapa do roadmap), para que o orquestrador não precise carregar o contrato do vault. | Só lê o vault e só cria arquivos novos em `00 Inbox/`. Hooks bloqueiam qualquer escrita fora disso e qualquer sobrescrita. |

**[agente]** O `brain-curador` começa como opção que o usuário ativa (`--agent`). Torná-lo padrão das sessões no vault, com `"agent"` em `.claude/settings.json` do vault, fica para depois de validado. O motivo é que, como sessão principal, o corpo da soul *substitui* o system prompt padrão do Claude Code.

## 5. Fluxo de uma etapa do roadmap

0. **Pré-condição [usuário]:** o orquestrador confere se a sessão roda como `orquestrador-etapa` e se as souls `desenvolvedor`, `testador` e `revisor-seguranca` estão instaladas. Se faltar alguma, **para e avisa**, indicando como configurar a máquina ou iniciar com `claude --agent orquestrador-etapa`. Não existe fallback para os prompts padrão. Por isso, o caminho inline (`superpowers:executing-plans`, sem subagentes) deixa de valer para execuções com souls. Roadmaps antigos não quebram, porque guardam o protocolo antigo até serem atualizados pela skill.
1. O `orquestrador-etapa` escolhe a etapa (ou recebe o plano, fora de roadmap), confere o estado e faz o plano. Fora isso, segue o "Protocolo de execução" atual do roadmap: branch `roadmap/<slug>`, tags, handoffs e decisões para o usuário.
2. Para cada tarefa do plano (dentro de `superpowers:subagent-driven-development`):
   1. `desenvolvedor`, com o prompt implementer, faz TDD e commit.
   2. `testador` completa e ataca os testes, faz commit e relata.
   3. **Verificação mecânica de integridade dos testes** (ver §6), rodada pelo orquestrador.
   4. `revisor-seguranca`, com o prompt task-reviewer e o resultado da verificação mecânica, audita código e testes.
   5. Correções seguem o ciclo do superpowers: correção pelo `desenvolvedor` (ou pelo `testador`, se o problema for de teste) e depois re-revisão.
3. Revisão final da etapa: `revisor-seguranca` com um modelo mais capaz, sobre o diff inteiro, com ênfase em dependências.
4. Fechamento: o `brain-escriba` publica a captura de atualização no brain quando o bloco "Second Brain" do roadmap se aplica. O orquestrador atualiza tags e handoff.

A ordem *desenvolvedor → testador → revisor* dentro de cada tarefa é uma inserção nossa no ciclo do superpowers, que originalmente não tem o testador. O orquestrador precisa saber encaixá-la sem quebrar o resto do ciclo: ledger, rodadas de correção, re-revisão.

**Quando um teste novo do testador falha [agente].** Esse é o resultado esperado quando o testador acha um bug de verdade.

- O testador faz commit do teste vermelho, que documenta o bug, e relata a falha com a saída real.
- O orquestrador devolve a tarefa ao `desenvolvedor`, que corrige o **código** e nunca o teste.
- Esse ciclo conta dentro do limite de 5 rodadas de correção do superpowers.
- Depois de cada correção que mexe em código de produção, o testador roda de novo.
- A tarefa só vai para a revisora com a suíte inteira verde.
- Se o desenvolvedor achar que o teste está errado, ele não mexe no teste: aponta o problema e o orquestrador decide, consultando o testador.

**Revisão final [agente].** A `revisor-seguranca` *substitui* o revisor geral de código do superpowers na revisão final, em vez de rodar ao lado dele. O papel que o usuário pediu é "code review de segurança **e boas práticas**". Por isso, a soul recebe o prompt de revisão final do superpowers como tarefa (arquitetura e qualidade do branch inteiro) e acrescenta a lente de segurança e dependências. Assim nenhuma cobertura se perde e o `Agent(...)` do orquestrador continua fechado.

## 6. Verificação mecânica de integridade dos testes

A revisora não depende só do próprio julgamento. Um script determinístico compara o estado dos testes antes e depois de cada tarefa e aponta pelo menos: **[usuário]** (decidiu combinar a revisora com uma trava mecânica)

- testes removidos, renomeados ou marcados como skip/ignore/disabled;
- asserções removidas ou trocadas por asserções triviais;
- alterações em arquivos de teste feitas em commits do desenvolvedor sobre testes acrescentados pelo testador;
- alterações em código de produção feitas em commits do testador.

A saída do script entra no pacote de revisão da revisora. Um apontamento não reprova sozinho, mas obriga a revisora a justificá-lo.

Além disso, os hooks `PreToolUse` do `testador` e do `desenvolvedor` bloqueiam na hora as edições que violam suas travas, quando for possível decidir isso só pelo caminho do arquivo.

## 7. Instalação e sincronização

- **Local [usuário]:** `99 System/Souls/` no vault, como documentação de sistema, fora de buscas de conteúdo e do processamento da Inbox, igual a `99 System/Skills/`. A pasta nova é mudança estrutural, autorizada pelo usuário na entrevista.
- **Estrutura [agente]:**
  - `99 System/Souls/README.md`: guia do usuário, como o de Skills.
  - `99 System/Souls/DESIGN.md`: este documento.
  - `99 System/Souls/agents/<soul>.md`: só as souls.
  - `99 System/Souls/agents/references/` (ou equivalente): referências longas, se houver.

  As souls ficam numa subpasta porque o Claude Code varre `~/.claude/agents/` recursivamente e trataria README e DESIGN como agentes.
- **Ativação:** o `sync-skills.sh` / `sync-skills.ps1` passa a ligar as souls em `~/.claude/agents/`, como faz com as skills. Hooks de frontmatter vindos de `~/.claude/agents/` não exigem o diálogo de confiança do workspace.
- **Configuração da máquina:** `99 System/AI/setup.md` e a skill `configurar-maquina` passam a incluir e conferir os links das souls e a **instalar ou conferir scanners de dependência** exigidos pela revisora. O construtor escolhe quais: de preferência um multi-ecossistema, como o `osv-scanner`, e complementos por stack só se necessário.

## 8. Mudanças em documentos e skills existentes

Estas mudanças fazem parte do escopo. Elas mexem em `99 System/AI/` e, portanto, dependem da aprovação deste design.

- `99 System/AI/architecture.md`: linha de `99 System/Souls/` na tabela de pastas.
- `99 System/AI/setup.md`: links das souls e como conferi-los.
- `AGENTS.md`: uma linha em "Convenções rápidas" apontando para `99 System/Souls/`.
- Skill `development-roadmap`: §7 "Papéis e Souls" e tabela de papéis do protocolo em `references/template.md`, com a nova tabela papel → soul, o testador no ciclo de cada tarefa, a verificação mecânica e o prompt de execução orientando a iniciar com `claude --agent orquestrador-etapa`. O `check_roadmap.py` deve continuar passando, e precisa ser ajustado se conferir o texto do protocolo.
- `20 Knowledge/Souls - alma personalizada para cada agente de desenvolvimento.md`: registrar as respostas às perguntas em aberto (o que a soul contém, formato, local, escolha por papel, relação com o superpowers), com proveniência desta sessão.

## 9. Restrições

- Seguir a política de mutação do vault. Commit só com a concordância do usuário. Nunca fazer `push`.
- Funcionar em Linux, macOS e Windows, como o sync das skills já funciona.
- Não duplicar regras: as souls do brain apontam para `AGENTS.md` e `99 System/AI/`, e as de desenvolvimento apontam para as skills do superpowers.
- Hooks e scripts das travas não podem depender de caminho absoluto de uma máquina específica.

## 10. Deixado para o construtor

- O texto de cada soul, dentro da anatomia da §3 e das travas da §4.
- Ferramentas exatas por soul (`tools`/`disallowedTools`) e os scripts de hook.
- Linguagem, local e heurísticas do script de integridade de testes (§6), incluindo como identificar arquivos de teste nos diferentes stacks e como atribuir commits a um papel.
- Como o `sync-skills` liga as souls: link por arquivo ou pela pasta `agents/` inteira, considerando que no Windows só se usam junctions de diretório. O construtor deve **testar** se o Claude Code segue links e junctions em `~/.claude/agents/`, porque a documentação não diz.
- Como ensinar o orquestrador a inserir o testador e a verificação mecânica no ciclo do `subagent-driven-development` sem alterar o plugin.
- Quais scanners instalar e como a revisora detecta qual se aplica ao stack do projeto.
- Como validar cada soul antes de usá-la de verdade, por exemplo: tentar fazer o testador editar código de produção e confirmar o bloqueio.
