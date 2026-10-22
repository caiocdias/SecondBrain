---
name: development-roadmap
description: Cria ou atualiza um roadmap de desenvolvimento executável em Markdown, ancorado no código e na documentação reais do repositório, dividindo o trabalho em etapas com tags de estado (#pendente, #em-andamento, #concluida, #bloqueada), dependências, critérios de aceite, validação, estratégia de execução com subagentes (investigação, implementação paralela, verificação independente) e um prompt autocontido por etapa para colar numa sessão limpa do Claude Code, além de um prompt orquestrador que executa as etapas em sequência com um subagente por etapa. Use sempre que o usuário pedir roadmap, plano de implementação, plano de desenvolvimento, quebrar/dividir uma feature, spec ou sistema em etapas, fases ou sessões, gerar prompts para as próximas sessões, planejar execução com subagentes, ou atualizar/sincronizar o estado de um roadmap existente, mesmo que ele não diga "roadmap". Não use para roadmaps só de produto/negócio, listas de tarefas simples sem trabalho de código, ou para implementar as etapas.
---

# Development Roadmap

Crie um roadmap que permita ao Claude Code executar **uma etapa por vez**, sem depender do histórico da conversa que gerou o plano — seja numa sessão limpa aberta pelo usuário, seja por um subagente disparado pelo orquestrador do próprio roadmap. Quem executar a etapa terá apenas o repositório e o prompt — tudo o que precisa saber tem de estar no arquivo ou ser descobrível no código.

Este arquivo descreve o processo. A estrutura detalhada do documento, com exemplo de etapa e de prompt, está em `references/template.md`; leia-o antes de escrever o roadmap. Ao final, valide com `scripts/check_roadmap.py`.

## Limite da tarefa

Produza ou atualize o arquivo de roadmap. Não implemente etapas, não faça commit e não altere outros arquivos, salvo pedido explícito do usuário. O valor do roadmap está em ser revisável antes de qualquer mudança de código.

## 1. Investigue o contexto antes de planejar

Um roadmap só é útil se os caminhos, comandos e interfaces citados existirem de fato. Faça inspeções somente leitura suficientes para ancorar o plano:

1. Identifique a raiz do projeto (ou subprojeto, num monorepo) e leia as instruções aplicáveis: `CLAUDE.md` na hierarquia relevante, `.claude/` e também `AGENTS.md`, se existir.
2. Leia `README`, manifestos de build (`package.json`, `build.gradle.kts`, `pyproject.toml`, `Cargo.toml`…), configuração de CI, documentação de arquitetura/especificação e as áreas de código e testes relacionadas ao pedido.
3. Rode `git status` e `git log --oneline -n 20` para conhecer o estado atual e preservar mudanças do usuário.
4. Registre apenas stack, comandos, caminhos, interfaces e restrições confirmados. Comandos de build/teste só valem se aparecem em manifesto, CI, README ou instruções do projeto.
5. Separe **fatos confirmados**, **hipóteses** e **decisões em aberto**:
   - **hipótese** — existe um padrão razoável e mudar de ideia depois é barato (nome de pacote "a confirmar", biblioteca auxiliar, ferramentas instaladas na máquina do usuário). Registre-a com impacto e siga; a etapa afetada confere e se bloqueia se a hipótese cair.
   - **decisão em aberto** — sem ela a etapa não pode ser feita sem adivinhar, ou adivinhar errado é caro de desfazer (fornecedor externo, provedor de CI/infra, modelo de dados de contrato público, regra de segurança/LGPD). Registre-a e marque a primeira etapa afetada como `#bloqueada`.
   - se a lacuna impedir o plano inteiro, pergunte ao usuário antes de escrever.

Leia o necessário, não tudo: em especificações longas, use o índice e leia a fundo só as seções do escopo pedido.

### Projeto sem código (greenfield)

Quando o repositório ainda não tem código, não há comandos de validação para citar. Não os invente. Faça a primeira etapa estabelecer o esqueleto do projeto, um `.gitignore` que cubra os artefatos do stack (o snapshot do protocolo de execução depende dele) **e** os comandos oficiais de build, teste e lint, registrando-os em "Evidências e handoff" e no README/CLAUDE.md. Os prompts das etapas seguintes mandam ler esses comandos ali, em vez de repeti-los às cegas. Decisões de stack já tomadas nos documentos do projeto são fatos; versões e bibliotecas não citadas são hipóteses.

## 2. Dimensione o escopo

Um roadmap com dezenas de etapas raramente é executado até o fim: o código diverge do plano antes. Se o pedido cobrir um sistema inteiro ou várias fases (por exemplo, uma especificação com "Fase 1, 2, 3"), prefira um roadmap por fase ou marco:

- se o usuário indicou uma fase/escopo, planeje só ele e liste o restante em "Fora de escopo";
- se não indicou, planeje a primeira fase entregável e cite no cabeçalho os roadmaps futuros sugeridos;
- pergunte apenas se houver duas leituras igualmente plausíveis que mudem muito o resultado.

Como referência, mais de ~15 etapas costuma indicar escopo grande demais para um único arquivo. Se a fase que o usuário pediu realmente precisa de mais, mantenha um arquivo, agrupe as etapas em blocos no índice (ex.: "Plataforma", "Acesso", "Domínio") e ofereça a divisão em dois arquivos na resposta final — não divida sem perguntar, porque o usuário pediu aquela fase.

## 3. Escolha o arquivo de destino

Use o caminho indicado pelo usuário. Sem indicação, decida depois de inspecionar o repositório:

1. Procure roadmaps existentes (`find . -iname '*roadmap*' -not -path '*/node_modules/*'`) e compare título, objetivo e escopo. Se já houver um para o mesmo escopo, **atualize-o** (veja §6).
2. Senão, siga a convenção existente de roadmaps/planos no projeto ou subprojeto (nome, capitalização, diretório).
3. Sem convenção, use a pasta de documentação mais próxima do código afetado (`docs/roadmaps/`, depois `docs/`, `documentation/` ou equivalente). Num monorepo, não use a pasta `docs` de outro componente.
4. Sem pasta de documentação, use a raiz do projeto ou subprojeto. Não crie hierarquia nova só para o arquivo.

Nome: descritivo e estável, `roadmap-<slug-do-escopo>.md` (ex.: `docs/roadmap-autenticacao-oauth.md`, `roadmap-fase-1-hospedagem.md`). Evite o genérico `ROADMAP.md`, salvo pedido ou convenção. Nunca sobrescreva roadmap de outro escopo; em colisão, torne o slug mais específico.

## 4. Decomponha o trabalho

Crie quantas etapas o contexto exigir. Cada etapa deve:

- caber numa sessão do Claude Code e entregar um resultado observável — se o prompt precisar de dois objetivos independentes, são duas etapas;
- ter objetivo único e limites claros;
- declarar dependências por ID e o que pode correr em paralelo (e quais arquivos geram conflito de edição). Etapas paralelas só rodam ao mesmo tempo em worktrees git separados, cada uma em sua sessão; na mesma árvore de trabalho, o diff medido pelo verificador misturaria as duas e reprovaria ambas;
- seguir a ordem das dependências técnicas e reduzir risco cedo (integrações externas incertas, migrações, contratos públicos);
- trazer testes e documentação junto da mudança que os exige, não numa etapa genérica "testes" no fim;
- terminar num estado integrável, com build e testes verdes.

Inclua etapa de descoberta técnica (spike) só quando uma incógnita real impedir implementação responsável — e, nesse caso, a entrega dela é uma decisão registrada, não código de produção. Evite a sequência genérica análise → código → testes → documentação.

A última etapa (ou um gate final) valida a integração e a definição global de pronto.

## 5. Tags de estado

Cada etapa exibe exatamente uma destas tags, idêntica no índice e no título da etapa:

| Tag | Significado |
|---|---|
| `#pendente` | ainda não iniciada |
| `#em-andamento` | trabalho ativo, com evidência registrada |
| `#concluida` | todos os critérios de aceite e validações obrigatórias passaram, com evidência |
| `#bloqueada` | impedimento real impede iniciar ou aceitar a etapa |

Regras, e o motivo delas:

- Roadmap novo começa `#pendente`, exceto quando o repositório prova trabalho já feito, ou quando uma decisão em aberto (§1) já impede a etapa — essa nasce `#bloqueada`. O estado deve refletir a realidade, não intenções.
- Dependência não concluída mantém a etapa `#pendente`; isso não é bloqueio. Bloqueio é algo que exige ação de fora da sequência (decisão do usuário, credencial, contrato com fornecedor, bug externo).
- No máximo uma etapa `#em-andamento`, exceto paralelismo declarado sem conflito.
- `#concluida` exige evidência para cada critério e resultado dos comandos obrigatórios. Validação não executada impede conclusão.
- `#bloqueada` exige causa, evidência, impacto e ação concreta de desbloqueio — terminando com "registrar a decisão em Dn e trocar a tag para `#pendente`", para que a etapa volte ao fluxo normal. Riscos hipotéticos ficam em "Riscos" e não mudam o estado.

## 6. Atualizando um roadmap existente

Quando o pedido for atualizar, sincronizar ou ampliar um roadmap:

- Preserve estados, evidências e handoffs já registrados. Só mude uma tag com evidência verificável no repositório (arquivos, `git log`, testes executados agora); diga no handoff o que verificou.
- Não renumere etapas. Etapas novas recebem o próximo ID livre e entram na posição correta de dependência no documento, mesmo que o número fique fora de ordem.
- Etapa cancelada ou substituída sai do índice e do corpo, mas é registrada no "Histórico de revisões" com o motivo e a etapa substituta. Seu ID nunca é reutilizado, para que referências antigas não apontem para outra coisa. Etapas `#concluida` nunca são removidas.
- Se o código divergiu do plano, ajuste escopo, prompts e critérios das etapas pendentes afetadas.
- Mantenha um breve "Histórico de revisões" no fim do arquivo com data e o que mudou.
- Se o roadmap for anterior ao protocolo de execução (sem "Protocolo de execução", "Execução automática" ou "Estratégia de execução"), acrescente-os às etapas não concluídas.

## 7. Execução com subagentes

O roadmap inclui uma seção **"Protocolo de execução"** no cabeçalho (texto pronto em `references/template.md`, adapte só o caminho do roadmap) e, em cada etapa, um campo **"Estratégia de execução"**. O protocolo mora no roadmap, e não só nesta skill, porque a sessão que executa a etapa não carrega esta skill: ela só tem o arquivo.

O protocolo usa subagentes onde eles ajudam e os evita onde atrapalham:

- **Investigação delegada** (`Explore`, somente leitura): material extenso que será lido mas não editado — seções longas de especificação, convenções de outro módulo — é resumido por um subagente, preservando o contexto da sessão principal para a implementação. Os arquivos que serão editados são lidos pela própria sessão principal; editar a partir de um resumo produz erros.
- **Implementação na sessão principal**: uma única mente edita o código e o roadmap. Vários agentes editando os mesmos arquivos geram conflitos e decisões incoerentes.
- **Implementação paralela** (`general-purpose`), só quando a etapa tem partes substanciais com conjuntos de arquivos disjuntos, listados na etapa. Arquivos compartilhados (build, configuração, o roadmap) ficam com a sessão principal, que integra e roda a validação completa.
- **Verificação independente** (`general-purpose` novo): quem implementou tende a confirmar o próprio trabalho. Um subagente que não viu a implementação confere o diff da etapa contra os critérios de aceite, roda as validações e devolve APROVADO/REPROVADO com evidência. O diff da etapa é medido a partir de um snapshot da árvore de trabalho tirado no início (via `git write-tree` com índice temporário — sem commit e sem mexer no índice do usuário), porque o usuário pode não commitar entre etapas.

Escolha a estratégia de cada etapa:

| Estratégia | Quando usar |
|---|---|
| `direta` | mudança localizada e de baixo risco (configuração, documentação, ajuste coberto por testes existentes). Sem subagentes; a própria sessão valida. |
| `padrão` | o caso comum: etapa que cria ou muda comportamento. Investigação quando houver material extenso a ler + verificação independente obrigatória. |
| `paralela` | `padrão` + partes paralelas. Só quando há ≥2 partes substanciais com arquivos disjuntos que entregam juntas um resultado. Se as partes entregam resultados independentes, são etapas separadas, não uma etapa paralela. |

No campo, seja concreto: as perguntas que a investigação deve responder (não "explore o código"), as partes paralelas com seus arquivos e o **foco do verificador** — os riscos específicos da etapa que ele deve atacar (ex.: "escrita sem permissão", "migração reversível").

Marque também **Revisão humana: sim** nas etapas cujo erro se propagaria ou custaria caro: as que estabelecem convenções ou contratos que muitas etapas seguintes vão repetir (esqueleto, convenções de API, protocolos entre cliente e servidor), autenticação/autorização, migrações destrutivas de dados e a primeira integração com cada sistema externo. Uma etapa que só acrescenta endpoints seguindo convenções já revisadas não precisa. O orquestrador pausa nelas, então mantenha-as como minoria (cerca de uma em cada quatro, no máximo).

## 8. Prompts autocontidos

Cada etapa tem um bloco de código com um prompt que pode ser colado **sem edição** numa nova sessão do Claude Code aberta na raiz do projeto — e que o orquestrador repassa literalmente a um subagente. "Autocontido" significa independente **desta conversa** — quem executa não a viu, então "como combinamos" ou "a etapa acima" é informação perdida. O roadmap, porém, estará no disco: o prompt manda lê-lo e não precisa copiar o corpo inteiro da etapa. Copiar tudo duplica cada etapa e faz o arquivo crescer até ninguém revisá-lo.

O prompt deve:

- citar o caminho exato do arquivo de roadmap e o ID/título da etapa;
- dizer em 1–3 frases o objetivo concreto e repetir só os limites cuja violação seria cara (o que não tocar) e os critérios de aceite em forma resumida — é o que a sessão usa para decidir se terminou;
- mandar seguir o "Protocolo de execução" do roadmap com a estratégia da etapa, nomeando-a e citando o que for específico dela (perguntas da investigação, partes paralelas, foco do verificador);
- mandar ler antes de tudo: `CLAUDE.md`/`AGENTS.md`, o roadmap (cabeçalho, protocolo, a seção completa da etapa e handoffs das dependências), os arquivos relevantes e o `git status`;
- mandar verificar se as dependências estão de fato `#concluida` e se o código não divergiu do plano — e, se divergiu, parar e relatar antes de improvisar;
- mandar preservar mudanças preexistentes e não tocar fora do escopo;
- mandar tirar o snapshot inicial e trocar a tag para `#em-andamento` ao começar (no índice e no título);
- mandar implementar (testes primeiro quando os critérios descrevem comportamento verificável), criar/atualizar testes e rodar as validações da etapa;
- proibir declarar sucesso com validação obrigatória falhando ou não executada;
- mandar marcar `#concluida` só após o aceite — e, nas estratégias `padrão`/`paralela`, só com parecer APROVADO do verificador; diante de impedimento real, `#bloqueada` com causa, evidência e ação de desbloqueio;
- mandar preencher "Evidências e handoff" (snapshot, arquivos alterados, decisões, comandos e resultados, parecer do verificador, observações para a próxima etapa);
- pedir um resumo final curto de mudanças, validações e pendências;
- não autorizar commit, push, deploy ou outra ação externa — essas ficam a critério do usuário.

Sem placeholders (`<...>`, `TODO`, `TBD`) nos prompts. Use caminhos relativos ao repositório. Um bom prompt cabe em ~20–30 linhas.

## 9. Execução automática (orquestrador)

Inclua no cabeçalho a seção **"Execução automática"** com o prompt orquestrador do template, adaptado ao caminho do roadmap. Ele permite ao usuário colar um único prompt e ter as etapas executadas em sequência, cada uma por um subagente com contexto limpo — o mesmo isolamento de "uma sessão por etapa", sem colar prompt por prompt.

Decisões de desenho que o template já incorpora (mantenha-as ao adaptar):

- o orquestrador **coordena e não implementa**: lê o roadmap e os relatórios, não o código, para que seu contexto aguente várias etapas;
- o subagente implementador recebe o prompt da etapa **literalmente**, mais um adendo que prevalece sobre ele: usa o snapshot já tirado pelo orquestrador, não dispara subagentes (faz a investigação ele mesmo e implementa em sequência as partes de uma etapa `paralela` — subagentes podem não conseguir criar outros) e não marca `#concluida`; quem dispara o verificador e fecha a etapa é o orquestrador;
- no modo automático **toda** etapa passa pelo verificador, inclusive as `direta`: não há humano olhando entre etapas, e uma verificação de etapa pequena é barata;
- correções após reprovação voltam ao mesmo implementador quando for possível retomá-lo; senão, um implementador novo recebe o parecer do verificador, o handoff e o snapshot;
- etapas `#bloqueada` são puladas (e as que dependem delas esperam) e aparecem no relatório de parada;
- etapas rodam **em sequência**, nunca em paralelo, porque compartilham a mesma árvore de trabalho sem commits;
- para numa etapa `#bloqueada`, numa divergência do plano, após duas reprovações do verificador, numa etapa com **Revisão humana: sim** e ao atingir o **limite de etapas por execução** (padrão 3, editável no prompt). Lotes pequenos mantêm o diff revisável e dão ao usuário a chance de commitar entre lotes;
- nunca faz commit, push ou deploy.

Execução sem supervisão para em cada pedido de permissão (build, testes, Docker). Na resposta final, lembre o usuário de liberar antes os comandos de build/teste do projeto nas permissões do Claude Code (ou usar um modo de permissão mais autônomo), se quiser que o lote rode sem interrupções.

## 10. Antes de entregar

Rode o verificador estrutural e corrija tudo o que ele apontar como erro:

```bash
python3 ~/.claude/skills/development-roadmap/scripts/check_roadmap.py <caminho-do-roadmap>
```

Ele confere tags canônicas, sincronia índice ↔ etapas, IDs duplicados, dependências inexistentes ou posteriores (o que também exclui ciclos), prompts sem o caminho do roadmap ou o ID, seções obrigatórias, estratégia de execução, presença do protocolo e do orquestrador, e placeholders. Avisos merecem leitura, mas podem ser legítimos.

Depois, revise o que o script não vê:

- toda parte do pedido está no escopo de alguma etapa ou explicitamente fora de escopo;
- critérios de aceite são binários e observáveis ("`GET /v1/rooms` retorna 200 com a lista paginada", não "funciona corretamente");
- validações correspondem ao stack real e cobrem regressão proporcional ao risco;
- bloqueios são acionáveis e não confundem dependência normal com impedimento;
- dependências entre módulos/camadas planejadas respeitam a arquitetura documentada (uma etapa que obriga o módulo A a chamar o B, quando a arquitetura proíbe, vai parar a sessão que a executar);
- cada estratégia é proporcional à etapa: `paralela` só com partes de arquivos realmente disjuntos; `direta` só onde um erro seria barato e visível;
- o gate final depende das etapas-folha (as que nenhuma outra etapa tem como dependência), o que cobre transitivamente todas as demais;
- nenhum fato inventado: cada caminho/comando citado foi visto no repositório ou está rotulado como hipótese/"a criar".

## Resposta final

Informe o caminho do roadmap criado ou atualizado, a quantidade de etapas, um resumo de uma linha por etapa (ou por grupo), as decisões em aberto que o usuário precisa resolver e as duas formas de executar: colar o prompt de uma etapa numa sessão limpa, ou colar o prompt da seção "Execução automática" para rodar etapas em lote. Não cole o documento inteiro na resposta — o arquivo já está no repositório.
