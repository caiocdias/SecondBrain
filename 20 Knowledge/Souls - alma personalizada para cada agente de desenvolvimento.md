---
type: knowledge
subtype: question
status: draft
created: 2026-10-22
sources:
  - "[[2026-10-22 - Souls - alma personalizada para cada agente do desenvolvimento - 2a56505b]]"
aliases:
  - "Souls"
---
# Souls - alma personalizada para cada agente de desenvolvimento

## Ideia central

Opinião do usuário (2026-10-22), citação literal: "no futuro o conceito de Souls será implementado com uma "alma" personalizada para cada agente do desenvolvimento e o desenvolvimento via roadmap ira abraçar isso".

É uma direção futura declarada, não um conceito definido. Deve orientar a evolução da skill `development-roadmap` e possivelmente de outras skills de desenvolvimento.

## Explicação

Decisão tomada na mesma conversa: a skill `development-roadmap` passou a nomear os papéis de agente de cada execução (orquestrador, planejador, implementador, revisor de tarefa, revisor final) e reserva um ponto de encaixe para uma soul por papel. Enquanto nenhuma soul estiver definida, valem os prompts padrão do plugin superpowers. A skill instrui a não inventar souls (`99 System/Skills/development-roadmap/SKILL.md`, §7 "Papéis e Souls", e a tabela de papéis do "Protocolo de execução" em `references/template.md`).

Implementação (2026-10-27): as souls foram implementadas como subagentes do Claude Code em `99 System/Souls/agents/`, seis ao todo: `orquestrador-etapa`, `desenvolvedor`, `testador`, `revisor-seguranca`, `brain-escriba` e `brain-curador`. Cada uma tem identidade (corpo em português, com seis seções) e travas reais (`tools` e um hook `PreToolUse` que falha fechado), além de uma verificação mecânica da integridade dos testes rodada pelo orquestrador. O `orquestrador-etapa` e o `brain-curador` rodam como sessão principal (`claude --agent ...`); as demais são despachadas como subagentes. As souls valem para qualquer execução de plano do superpowers, com ou sem roadmap, e a skill `development-roadmap` passou a exigi-las. Guia: `99 System/Souls/README.md`; design e justificativas: `99 System/Souls/DESIGN.md`.

## Limites e implicações

Perguntas em aberto (o usuário ainda não definiu):

- O que uma soul contém: personalidade, regras, conhecimento, modelo?
- Em que formato e onde fica armazenada?
- É escolhida por papel, por projeto ou por agente?
- Como se relaciona com os prompts do superpowers?
- "Cada agente do desenvolvimento" coincide com os cinco papéis nomeados na skill? A lista de papéis foi escolha do agente.

Respostas (2026-10-27; **[usuário]** = decisão do usuário, **[agente]** = escolha do agente, que o usuário pode revisar):

- Conteúdo: identidade (como pensa, o que prioriza, o que recusa) mais travas reais (ferramentas, permissões e hooks aplicados pelo Claude Code), e não só personalidade. **[usuário]**. A divisão do corpo em seis seções e o tamanho curto são **[agente]**; conhecimento longo fica em referências abertas sob demanda.
- Formato e local: cada soul é um subagente do Claude Code (Markdown com frontmatter), em português **[usuário]**, versionado no vault em `99 System/Souls/agents/` **[usuário]**; o link `~/.claude/agents/second-brain-souls`, feito pelo sync para a pasta inteira, é **[agente]**.
- Escolha: por papel **[usuário]**; o orquestrador as despacha como `subagent_type`. O `model: inherit` e a escolha de modelo mais capaz em revisão final e rodadas de correção avançadas são **[agente]**.
- Relação com o superpowers: a soul define quem é o agente; o prompt do superpowers (implementer, task-reviewer, code-reviewer) continua definindo o que fazer na tarefa e é passado como tarefa **[usuário]**. O testador rodando depois de cada tarefa e a revisora combinada com uma verificação mecânica dos testes são **[usuário]**; como o orquestrador os insere no ciclo sem alterar o plugin é **[agente]**, assim como a substituição do revisor geral pela `revisor-seguranca` na revisão final.
- Os cinco papéis da skill versus os papéis das souls: não coincidem. O usuário escolheu os papéis: o orquestrador absorveu o planejador, entraram o testador e a revisora de segurança, e o Second Brain ganhou duas souls (`brain-curador` e `brain-escriba`) **[usuário]**; os nomes são **[agente]**. O usuário decidiu apenas que a revisão final exige scanner de dependências, com recomendação do scanner e link oficial de instalação **[usuário]**; a revisora ser somente leitura por ferramenta, sem Bash, com o orquestrador rodando os scanners, foi um ruling do agente **[agente]**.
- Opt-in do `brain-curador`: começa como opção (`--agent`); torná-lo padrão do vault fica para depois **[agente]**.

## Relações

- [[Decidir pendências do usuário por entrevista com opção recomendada]]: a resposta sobre Souls veio de uma entrevista com opção recomendada.

## Proveniência

- 2026-10-22 — [[2026-10-22 - Souls - alma personalizada para cada agente do desenvolvimento - 2a56505b]] (capture_id: 2a56505b-41ee-42d8-9935-bd73090533c7): opinião literal do usuário sobre Souls, decisão de reservar o ponto de encaixe na skill `development-roadmap` e perguntas em aberto.
- 2026-10-27 — sessão curadora; design em 99 System/Souls/DESIGN.md: implementação das seis souls, respostas às perguntas em aberto e marcação do que foi decisão do usuário ou escolha do agente (entrevista com opção recomendada).
