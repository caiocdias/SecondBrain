# Contrato para agentes externos

Documento principal sobre o uso do vault por agentes que trabalham em outros projetos: sessões cujo diretório principal está fora do vault ([[AGENTS]]).

## Procedimento

1. Confirmar o caminho e a disponibilidade do vault: o diretório existe, está acessível e contém `AGENTS.md`. Se não estiver disponível, informar o usuário; não criar estrutura substituta em outro lugar.
2. Ler `AGENTS.md`, este contrato e o protocolo correspondente à tarefa: [[99 System/AI/ingestion]] para capturar; [[99 System/AI/retrieval]] e [[99 System/AI/application]] para consultar e aplicar.
3. Consultar apenas conhecimento pertinente, com recuperação progressiva. Não carregar o vault inteiro.
4. Criar capturas novas em `00 Inbox/` quando o usuário solicitar registro.
5. Preservar a referência ao projeto, arquivo, conversa ou fonte de origem.
6. Encerrar após confirmar que o arquivo criado existe e está completo, informando seu caminho. A integração fica com o curador.

## Permissões

Permitido:

- Ler notas pertinentes em todo o vault.
- Criar novos arquivos de captura e seus anexos em `00 Inbox/`.
- Criar ou editar skills em `99 System/Skills/` (inclusive pelos links em `~/.claude/skills/`) quando o usuário pedir explicitamente. Skills não são conteúdo do brain; o hook de sincronização também move para lá skills novas criadas em qualquer sessão ([[99 System/AI/setup]]).

Não permitido:

- Modificar, mover ou apagar capturas anteriores da Inbox, inclusive as próprias já publicadas.
- Modificar notas permanentes, Maps, templates, protocolos, `AGENTS.md`, `CLAUDE.md`, a configuração do Obsidian (`.obsidian/`) ou a pasta `.claude/` do vault.
- Alterar o índice ou o histórico Git do vault (por exemplo, `add`, `commit`, `reset`, `checkout`).
- Promover conteúdo a `canonical`.
- Processar a fila, arquivar capturas ou executar manutenção estrutural.

Se uma captura já publicada contiver erro ou omissão, criar um complemento (ver abaixo) em vez de editá-la.

## Projeto atual e regras do vault

O projeto atual determina seu próprio contexto. O vault determina suas regras de organização. Uma configuração de projeto (instruções, arquivos de agente, convenções locais) não autoriza reorganizar o Second Brain. O conhecimento do vault orienta o trabalho no projeto somente dentro do escopo da tarefa ([[99 System/AI/application]]).

## Capturas equivalentes

Antes de publicar, fazer a busca breve prevista em [[99 System/AI/ingestion]].

- Se encontrar uma captura equivalente, informar o usuário sobre sua existência.
- Se houver contexto novo relevante, criar um complemento: uma nova captura que referencia a anterior pelo link e pelo `capture_id`, contendo apenas o que é novo.
- Se encontrar uma nota permanente equivalente, informar o usuário; a captura, se ainda for útil, pode citá-la em "Possíveis conexões".

A consolidação cabe ao curador.

## Pedidos fora do escopo

Pedidos de processar a Inbox, integrar capturas, revisar, reorganizar ou manter o vault feitos em uma sessão externa devem ser encaminhados para uma sessão dedicada ao vault (iniciada na raiz do vault). O agente não assume esse papel por iniciativa própria.

## Limite técnico

A configuração de diretórios adicionais concede acesso aos arquivos. A separação entre papéis é uma regra operacional do sistema; ela não constitui, por si só, isolamento técnico de escrita. Cabe ao agente respeitá-la.
