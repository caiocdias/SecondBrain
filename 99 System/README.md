# Guia do Second Brain

Este vault é um Second Brain pessoal em Markdown, para qualquer área da vida. Funciona no Obsidian, em qualquer editor de texto e com agentes de IA de diferentes fornecedores. As regras para agentes estão em [[AGENTS]] e em `99 System/AI/`; este guia resume o essencial para você.

## Filosofia

- Cada nota, com suas relações, é a unidade de organização.
- Pastas indicam função (Inbox, conhecimento, fontes…), não assunto.
- Properties guardam atributos estruturados; links expressam relações; Maps explicam como as notas se conectam; Bases oferecem consultas e visualizações.
- Tudo continua legível sem Obsidian, sem IA e sem plugins comunitários.

## Pastas e entidades

| Pasta | O que guarda |
|---|---|
| `00 Inbox/` | Capturas pendentes (`type: capture`) e seus anexos |
| `10 Projects/` | Projetos reais (`type: project`) |
| `20 Knowledge/` | Conhecimento reutilizável (`knowledge`) e metodologias (`methodology`) |
| `30 Sources/` | Registros de fontes (`source`); arquivos de referência em `Attachments/` |
| `50 Logs/` | Notas diárias e registros de processamento (`log`) |
| `80 Maps/` | Maps de curadoria (`map`) |
| `90 Archive/` | Material histórico; capturas processadas em `Inbox/` |
| `99 System/` | Documentação, protocolos, templates e consultas |

Detalhes em [[99 System/AI/architecture]] e [[99 System/AI/schemas]].

## Inbox central: captura e integração

Tudo o que um agente registra entra primeiro em `00 Inbox/`, uma única Inbox para todas as origens. **Capturar** é registrar rapidamente, com a origem e o contexto. **Integrar** é decidir o que aquilo se torna (fonte, conhecimento, metodologia, atualização de projeto ou apenas histórico), evitar duplicatas e criar conexões. Depois de integrada, a captura é preservada em `90 Archive/Inbox/`.

## Agentes externos e sessão curadora

- **Agente externo**: um agente trabalhando em outro projeto, com acesso ao vault como diretório adicional (no Claude Code, por exemplo, `--add-dir`). Ele pode consultar o vault e criar novas capturas na Inbox, nada além disso.
- **Sessão curadora**: um agente iniciado na raiz do vault (por exemplo, `cd` para a pasta do vault e então `claude`). É nela que você pede processamento da Inbox e manutenção.

## Registrar informação manualmente

- Crie uma nota em `00 Inbox/` com o template Capture e escreva livremente; o `capture_id` pode ficar vazio, pois o curador o atribui ao processar.
- Você também pode criar notas permanentes diretamente nas pastas de conteúdo, usando o template correspondente.
- Omita seções vazias. Use datas `YYYY-MM-DD`.

## Templates

Os templates ficam em `99 System/Templates/` e usam apenas o recurso nativo Templates do Obsidian (`{{date}}`, `{{title}}`):

- Nas configurações do plugin nativo Templates, defina a pasta de templates (*Template folder location*) como `99 System/Templates`.
- Para notas diárias, nas configurações do plugin nativo Daily notes, defina a pasta das novas notas (*New file location*) como `50 Logs` e o template (*Template file location*) como `99 System/Templates/Daily`.
- Insira um template com o comando *Templates: Insert template*.

Templates não são conhecimento e são ignorados por buscas e pelo processamento. Registros na nota diária não precisam virar capturas separadas, a menos que você queira integrá-los a outras notas.

## Metodologias canonical

Uma metodologia é um procedimento ou critério pessoal (`type: methodology`, em `20 Knowledge/`). Ela nasce como `draft`. Só se torna `canonical`, uma orientação que os agentes seguem como regra sua, quando você aprova explicitamente.

- **Reconhecer**: `status: canonical` no frontmatter e a aprovação registrada no "Histórico de revisão".
- **Aprovar**: leia a metodologia e diga ao curador, por exemplo, "Aprovo esta metodologia como canonical", ou altere o status você mesmo e registre a data no histórico.

Uso frequente ou confiança de um agente nunca substituem sua aprovação.

## Recuperar e aplicar conhecimento

Pergunte em linguagem natural. O agente busca progressivamente, lê as notas pertinentes e informa quais notas sustentam a resposta, separando o que foi recuperado do que foi inferido. Ao aplicar uma metodologia, ele procura primeiro orientações `canonical` e informa adaptações. Detalhes em [[99 System/AI/retrieval]] e [[99 System/AI/application]].

## Fontes bibliográficas

Se você usa um gerenciador de referências (por exemplo, Zotero), ele mantém o registro bibliográfico completo; o vault mantém a síntese e as relações intelectuais. Uma Source pode citar a chave ou o link do item no gerenciador, sem duplicar todos os metadados.

## Exemplos de pedidos

- "Salve este aprendizado no meu brain."
- "Capture esta referência na Inbox."
- "O que já existe no meu brain sobre este assunto?"
- "Consulte minha metodologia antes de executar esta tarefa."
- "Processe minha Inbox."
- "Quais notas e fontes sustentam esta conclusão?"
- "Revise possíveis duplicatas sem alterar os arquivos."

Os dois primeiros pedidos podem ser usados a partir de outros projetos, por um agente externo, assim como as consultas (terceiro, quarto e sexto). Processamento e manutenção pertencem à sessão dedicada ao vault.

## Integração com Claude Code

- **Skill global `second-brain`** (`~/.claude/skills/second-brain/`): consulta e captura a partir de qualquer projeto. Fora do vault, só cria novas capturas em `00 Inbox/`. O vault está liberado para leitura em todas as sessões por `permissions.additionalDirectories` em `~/.claude/settings.json`, e um bloco curto em `~/.claude/CLAUDE.md` aponta para a skill.
- **Skill de projeto `processar-inbox`** (`.claude/skills/` do vault): disponível somente em sessões iniciadas na raiz do vault, para o curador incorporar a Inbox (`/processar-inbox` ou "processe minha Inbox").
- As skills são apenas portas de entrada: os protocolos em `99 System/AI/` continuam sendo a fonte da verdade. Os arquivos em `~/.claude/` ficam fora do repositório do vault.

## Bases e Git

- Consultas recomendadas para o recurso Bases: [[99 System/Bases/README]].
- O vault é versionado com Git local. Agentes oferecem commits locais ao final das tarefas, mas nunca fazem push.
