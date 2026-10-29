---
name: development-roadmap
description: Cria ou atualiza um roadmap de desenvolvimento em Markdown, ancorado no código e na documentação reais do repositório, que divide um projeto ou fase em etapas com tags de estado (#pendente, #em-andamento, #concluida, #bloqueada), dependências, critérios de aceite, decisões em aberto e revisão humana. Cada etapa é planejada e executada pelo plugin superpowers (writing-plans e subagent-driven-development) numa branch do roadmap, um lote de etapas por vez, a partir de um único prompt de execução. Use sempre que o usuário pedir roadmap, plano de desenvolvimento em etapas ou fases, quebrar uma feature, spec ou sistema em várias sessões, ou atualizar/sincronizar o estado de um roadmap existente, mesmo sem dizer "roadmap". Use também para registrar um projeto no Second Brain ou enxugar o CLAUDE.md dele. Para um trabalho que cabe num único plano, use direto superpowers:brainstorming e superpowers:writing-plans. Não use para roadmaps só de produto/negócio nem para implementar as etapas.
---

# Development Roadmap

Um roadmap organiza um trabalho grande demais para um único plano em **etapas** executadas ao longo de várias sessões. Esta skill cuida da camada de cima: o que fazer, em que ordem, em que estado está cada etapa e o que depende do usuário. O plano detalhado e a execução de cada etapa ficam com o plugin **superpowers**:

- `superpowers:brainstorming`: descobrir o que o usuário quer, quando o pedido não traz spec ou design suficiente;
- `superpowers:writing-plans`: transformar uma etapa num plano de tarefas com arquivos, interfaces e testes exatos;
- `superpowers:subagent-driven-development`: executar o plano com revisão por tarefa e revisão final;
- `superpowers:using-git-worktrees` e `superpowers:finishing-a-development-branch`: isolar o trabalho numa branch e decidir com o usuário como integrá-la.

Se o superpowers não estiver instalado, avise o usuário (ele está registrado no Second Brain e é instalado pela configuração da máquina) e pare antes de escrever o roadmap.

A estrutura do documento está em `references/template.md`; leia-o antes de escrever. Ao final, valide com `scripts/check_roadmap.py`. O registro do projeto no Second Brain está em `references/brain.md`.

## Limite da tarefa

Produza ou atualize o arquivo de roadmap. Não planeje tarefas, não implemente, não faça commit e não altere outros arquivos, salvo pedido explícito do usuário. O valor do roadmap está em ser revisável antes de qualquer mudança de código.

Única exceção: o registro do projeto no Second Brain (§0), feito só depois do ok do usuário. Ele cria capturas na Inbox do vault, mescla o hook no `.claude/settings.json` e troca o `CLAUDE.md` pelo enxuto.

## 0. Projeto no Second Brain

O conhecimento técnico de todo projeto vive no Second Brain do usuário, e o `CLAUDE.md` fica enxuto. Em toda execução, antes de investigar, leia `references/brain.md` e faça a verificação de lá:

- **projeto registrado** (hub, hook, `CLAUDE.md` enxuto e hook respondendo): siga;
- **falta algo**: proponha o registro por entrevista com opção recomendada e, com o ok, faça a migração antes do roadmap;
- **usuário recusou ou vault inacessível**: siga só com o roadmap e diga isso na resposta final.

A sessão do repositório é agente externo do vault: só cria capturas em `00 Inbox/`, nunca edita notas. O hub e as notas de tema são criados pelo curador quando o usuário processa a Inbox.

## 1. Investigue o contexto antes de planejar

Um roadmap só é útil se os caminhos, comandos e interfaces citados existirem de fato. Faça inspeções somente leitura suficientes para ancorar o plano:

1. Identifique a raiz do projeto (ou subprojeto, num monorepo) e leia as instruções aplicáveis: `CLAUDE.md` na hierarquia relevante, `.claude/` e `AGENTS.md`, se existir. Num projeto registrado no brain, leia também o hub, as notas de tema ligadas ao escopo e as capturas pendentes do projeto: é lá que estão convenções, módulos e estado.
2. Leia `README`, manifestos de build, configuração de CI, documentação de arquitetura/especificação (inclusive `docs/superpowers/specs/`) e as áreas de código e testes relacionadas ao pedido.
3. Rode `git status`, `git branch -a` e `git log --oneline -n 20` para conhecer o estado atual, branches de roadmap existentes e mudanças do usuário.
4. Registre apenas stack, comandos, caminhos, interfaces e restrições confirmados. Comandos de build/teste só valem se aparecem em manifesto, CI, README ou instruções do projeto.
5. Separe **fatos confirmados**, **hipóteses** e **decisões em aberto**:
   - **hipótese**: existe um padrão razoável e mudar de ideia depois é barato. Registre-a com impacto e siga; a etapa afetada confere e se bloqueia se a hipótese cair.
   - **decisão em aberto**: sem ela a etapa não pode ser feita sem adivinhar, ou adivinhar errado é caro de desfazer (fornecedor externo, infraestrutura, contrato público, segurança/LGPD). Registre-a e marque a primeira etapa afetada como `#bloqueada`.

Leia o necessário, não tudo: em especificações longas, use o índice e leia a fundo só as seções do escopo pedido.

### Quando falta entender o pedido

Se o pedido não diz o que construir com clareza suficiente para dividir em etapas, conduza antes `superpowers:brainstorming` até haver um design aprovado pelo usuário (o documento fica em `docs/superpowers/specs/`). Esse design é a fonte do roadmap: cite-o no cabeçalho. Para trabalho que cabe num único plano, não crie roadmap; siga o fluxo normal do superpowers.

Decisões que cabem ao usuário (decisões em aberto que impedem o plano inteiro, duas leituras plausíveis do escopo) são resolvidas por **entrevista com opção recomendada**: perguntas de múltipla escolha, uma opção marcada como recomendada e justificada; no Claude Code, `AskUserQuestion` com a recomendada em primeiro lugar e o rótulo "(Recomendado)".

### Projeto sem código (greenfield)

Não invente comandos de validação. A primeira etapa estabelece o esqueleto do projeto, um `.gitignore` que cubra os artefatos do stack e os comandos oficiais de build, teste e lint, registrando-os em "Evidências e handoff", no README e na tabela de comandos do `CLAUDE.md` enxuto. Decisões de stack já tomadas nos documentos do projeto são fatos; versões e bibliotecas não citadas são hipóteses.

## 2. Dimensione o escopo

Um roadmap com dezenas de etapas raramente é executado até o fim: o código diverge do plano antes. Se o pedido cobrir um sistema inteiro ou várias fases, prefira um roadmap por fase ou marco:

- se o usuário indicou uma fase/escopo, planeje só ele e liste o restante em "Fora de escopo";
- se não indicou, planeje a primeira fase entregável e cite no cabeçalho os roadmaps futuros sugeridos.

Como referência, mais de ~12 etapas costuma indicar escopo grande demais para um único arquivo. Se a fase pedida realmente precisa de mais, agrupe as etapas em blocos no índice e ofereça a divisão em dois arquivos na resposta final, sem dividir por conta própria.

## 3. Escolha o arquivo de destino

Use o caminho indicado pelo usuário. Sem indicação:

1. Procure roadmaps existentes (`find . -iname '*roadmap*' -not -path '*/node_modules/*'`). Se já houver um para o mesmo escopo, **atualize-o** (§6).
2. Senão, siga a convenção existente de roadmaps/planos no projeto ou subprojeto.
3. Sem convenção, use `docs/roadmaps/` se existir, depois a pasta de documentação mais próxima do código afetado; num monorepo, não use a pasta `docs` de outro componente. Sem pasta de documentação, use a raiz do projeto ou subprojeto.

Nome: `roadmap-<slug-do-escopo>.md` (ex.: `docs/roadmap-autenticacao-oauth.md`). O mesmo slug nomeia a branch de execução, `roadmap/<slug>`. Nunca sobrescreva roadmap de outro escopo; em colisão, torne o slug mais específico.

## 4. Decomponha o trabalho em etapas

Cada etapa vira **um plano do superpowers**. Ela deve:

- ter objetivo único e entregar um resultado observável, do tamanho de um plano de poucas tarefas que roda numa sessão; se precisar de dois objetivos independentes, são duas etapas;
- descrever **o quê**, não o como: objetivo, escopo, fora de escopo, critérios de aceite binários e validação. Arquivos, assinaturas e passos ficam para o `writing-plans`, que lê o código no momento da execução; um roadmap que fixa esses detalhes envelhece antes de ser executado. "Notas para o plano" guarda só o que o planejador não descobriria sozinho (uma armadilha conhecida, uma convenção vinda de outra etapa);
- declarar dependências por ID e seguir a ordem das dependências técnicas, reduzindo risco cedo (integrações externas incertas, migrações, contratos públicos);
- trazer testes e documentação junto da mudança que os exige;
- terminar num estado integrável, com build e testes verdes.

As etapas de um lote rodam em sequência na mesma branch, então paralelismo entre etapas é só informativo ("independente de E03"): para rodar duas ao mesmo tempo, o usuário usa branches separadas.

Inclua etapa de descoberta (spike) só quando uma incógnita real impedir planejar responsavelmente; a entrega dela é uma decisão registrada, não código de produção. A última etapa (ou um gate final) valida a integração e a definição global de pronto.

Marque **Revisão humana: sim** nas etapas cujo erro se propagaria ou custaria caro: as que estabelecem convenções ou contratos que muitas etapas seguintes vão repetir, autenticação/autorização, migrações destrutivas e a primeira integração com cada sistema externo. A execução para depois delas; mantenha-as como minoria.

## 5. Tags de estado

Cada etapa exibe exatamente uma destas tags, idêntica no índice e no título da etapa:

| Tag | Significado |
|---|---|
| `#pendente` | ainda não iniciada |
| `#em-andamento` | plano criado ou execução em curso, com evidência registrada |
| `#concluida` | revisão final limpa e todos os critérios de aceite verificados, com evidência |
| `#bloqueada` | impedimento real impede iniciar ou aceitar a etapa |

Regras, e o motivo delas:

- Roadmap novo começa `#pendente`, exceto quando o repositório prova trabalho já feito, ou quando uma decisão em aberto já impede a etapa, que nasce `#bloqueada`. O estado deve refletir a realidade, não intenções.
- Dependência não concluída mantém a etapa `#pendente`; isso não é bloqueio. Bloqueio exige ação de fora da sequência (decisão do usuário, credencial, contrato com fornecedor, bug externo).
- No máximo uma etapa `#em-andamento` por branch.
- `#bloqueada` exige causa, evidência, impacto e ação concreta de desbloqueio, terminando com "registrar a decisão em Dn e trocar a tag para `#pendente`". Riscos hipotéticos ficam em "Riscos" e não mudam o estado.

## 6. Atualizando um roadmap existente

- Preserve estados, evidências e handoffs já registrados. Só mude uma tag com evidência verificável (arquivos, `git log` da branch do roadmap, testes executados agora); diga no handoff o que verificou.
- Não renumere etapas. Etapas novas recebem o próximo ID livre e entram na posição correta de dependência.
- Etapa cancelada ou substituída sai do índice e do corpo e é registrada no "Histórico de revisões" com o motivo; seu ID nunca é reutilizado. Etapas `#concluida` nunca são removidas.
- Se o código divergiu do plano, ajuste escopo e critérios das etapas pendentes afetadas.
- Mantenha um breve "Histórico de revisões" no fim do arquivo.
- Num projeto registrado no brain, troque nas etapas pendentes "atualize o `CLAUDE.md`" por "publique a captura de atualização do brain" e "seção X do `CLAUDE.md`" pela nota de tema correspondente, e acrescente ao protocolo a seção "Second Brain" do template, se faltar.
- **Roadmap no formato antigo** (com "Estratégia de execução", prompt por etapa, snapshot por `git write-tree` ou orquestrador próprio): migre para este formato. Troque o cabeçalho de execução pelo do template, remova estratégias e prompts das etapas não concluídas, preserve as evidências das concluídas e registre a migração no histórico.

## 7. Execução

O roadmap traz no cabeçalho a seção **"Protocolo de execução"** e a seção **"Prompt de execução"** (textos prontos no template; adapte caminho e slug). O protocolo mora no roadmap, e não só nesta skill, porque a sessão que executa não carrega esta skill: ela só tem o arquivo e o superpowers.

Decisões de desenho que o template incorpora (mantenha-as ao adaptar):

- **Branch do roadmap**: toda execução acontece no worktree/branch `roadmap/<slug>`, criado com `superpowers:using-git-worktrees` e nunca na branch principal. Um lote ainda não integrado é continuado na mesma branch; depois de integrado, o próximo lote parte da branch principal atualizada. O próprio roadmap é atualizado na branch, então integrar a branch integra também os estados.
- **Uma etapa, um plano**: a seção da etapa (mais o design citado no cabeçalho) é a spec do `writing-plans`; o plano fica em `docs/superpowers/plans/` e é executado com `subagent-driven-development`. O superpowers commita por tarefa na branch.
- **Integração só no fim do lote**: `finishing-a-development-branch` roda uma vez, ao fim do lote, e é o usuário quem decide merge, PR, manter ou descartar. Nada de push, merge ou deploy sem ele.
- **Decisões do usuário**: o superpowers decide ambiguidades sozinho e registra *rulings* no ledger. As que mudam contrato, escopo, segurança, dados ou algo caro de desfazer vão para "Decisões para o usuário" no handoff e, ao parar, são apresentadas como entrevista com opção recomendada.
- **Lote limitado**: para numa etapa com Revisão humana: sim (depois de concluí-la), numa etapa `#bloqueada` ou em divergência do plano, nas paradas do próprio superpowers (operação destrutiva, ação sensível de segurança, efeito fora da branch, plano sem caminho viável) e ao atingir o **limite de etapas por execução** (padrão 3, editável no prompt). Lotes pequenos mantêm o diff revisável.
- **Second Brain**: num projeto registrado, o orquestrador lê o hub e as notas de tema da etapa e, no fechamento de cada etapa que mudou algo descrito no brain (inclusive o estado), publica a captura `<Projeto> - atualização <slug> Eyy`. A referência técnica nunca volta para o `CLAUDE.md`.
- **Papéis e Souls**: o protocolo nomeia os papéis (orquestrador, planejador, implementador, testador, revisor de plano, revisor de tarefa, revisor final, captura no brain) e a soul de cada um: `orquestrador` (sessão principal, iniciada com `claude --agent orquestrador`), `desenvolvedor`, `testador`, `revisor-seguranca`, `revisor-arquitetura` (revisa o plano de cada etapa antes da execução) e `brain-escriba`. A execução exige as cinco primeiras e não tem fallback para os prompts padrão do superpowers nem para `superpowers:executing-plans`; o roteiro por tarefa e as regras de encaixe vivem só em `99 System/Souls/agents/orquestrador.md`, e o template apenas remete a ele. Roadmaps antigos mantêm o protocolo antigo até serem atualizados por esta skill. O desenho e o roadmap também podem ser feitos numa sessão iniciada com `claude --agent arquiteto` (ver `99 System/Souls/agents/arquiteto.md`); o registro no brain (§0, que edita `.claude/settings.json`) precisa de uma sessão normal. Não invente souls.

## 8. Antes de entregar

Rode o verificador estrutural e corrija tudo o que ele apontar como erro (no Windows, `python` no lugar de `python3`):

```bash
python3 ~/.claude/skills/development-roadmap/scripts/check_roadmap.py <caminho-do-roadmap>
```

Ele confere tags canônicas, sincronia índice ↔ etapas, IDs duplicados, dependências inexistentes ou posteriores (o que também exclui ciclos), seções obrigatórias, Revisão humana em cada etapa, protocolo e prompt de execução, formato antigo e placeholders. Avisos merecem leitura, mas podem ser legítimos.

Depois, revise o que o script não vê:

- toda parte do pedido está no escopo de alguma etapa ou explicitamente fora de escopo;
- critérios de aceite são binários e observáveis ("`GET /v1/rooms` retorna 200 com a lista paginada", não "funciona corretamente");
- validações correspondem ao stack real e cobrem regressão proporcional ao risco;
- nenhuma etapa fixa arquivos, assinaturas ou passos que o planejador deveria decidir lendo o código;
- bloqueios são acionáveis e não confundem dependência normal com impedimento;
- dependências respeitam a arquitetura documentada;
- o gate final depende das etapas-folha;
- nenhum fato inventado: cada caminho/comando citado foi visto no repositório ou está rotulado como hipótese/"a criar";
- num projeto registrado no brain, nenhuma etapa manda registrar referência técnica no `CLAUDE.md`.

## Resposta final

Se houve registro no brain, informe as capturas criadas, os arquivos alterados no repositório (sem commit) e que é preciso processar a Inbox numa sessão do vault. Se o projeto ficou fora do brain, diga isso. Depois, informe o caminho do roadmap, a quantidade de etapas, um resumo de uma linha por etapa (ou por grupo), as decisões em aberto (em forma de entrevista com opção recomendada, se puderem ser resolvidas agora) e como executar: colar o "Prompt de execução" numa sessão limpa na raiz do repositório, que roda até o limite de etapas na branch `roadmap/<slug>`. Lembre de liberar antes os comandos de build/teste do projeto nas permissões do Claude Code, se quiser que o lote rode sem interrupções. Não cole o documento inteiro na resposta.
