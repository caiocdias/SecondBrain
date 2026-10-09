# Manutenção

Documento principal sobre a revisão do vault. Executada somente sob solicitação do usuário, em uma sessão curadora; não há execução periódica automática.

## Modo de execução

- Fazer apenas correções locais seguras dentro da solicitação. Se o pedido for apenas de revisão ("sem alterar os arquivos"), produzir somente um relatório.
- Apresentar propostas para mudanças amplas ([[99 System/AI/mutation-policy]]) e preservar o histórico.
- Usar recuperação progressiva ([[99 System/AI/retrieval]]); verificar somente o necessário ao pedido.

## Verificações

| Verificação | Sinais | Ação típica |
|---|---|---|
| Inbox acumulada | Capturas com `status: inbox` antigas ou numerosas | Relatar e sugerir processamento |
| Duplicatas potenciais | Títulos ou aliases semelhantes, mesma URL ou DOI, mesmo `capture_id` em mais de um arquivo | Propor consolidação |
| Links quebrados | Wikilinks, no corpo ou em properties, sem nota correspondente | Corrigir se o alvo correto for inequívoco; senão relatar |
| Properties inconsistentes | `type` ausente ou fora do schema, `status` inválido, datas fora do formato, `type: inbox`, links em properties sem aspas | Corrigir o que for claramente inconsistente |
| Origens ausentes | Source sem referência verificável; Knowledge sem proveniência ou `sources` | Relatar |
| Sources não examinadas | Sources com referência pendente ou em `draft` há tempo | Relatar |
| Maps desatualizados | Notas relevantes ausentes, links para notas arquivadas | Propor atualização |
| Projetos concluídos | Estado concluído no corpo da nota, ainda fora do arquivo | Propor arquivamento |
| Contradições `canonical` | Orientações aprovadas que se contradizem | Relatar e pedir decisão; nunca resolver sozinho |
| Nomes não portáveis | Violações da regra de [[99 System/AI/ingestion]] | Propor renomeação, conferindo backlinks |
| Tamanho e fragmentação | Notas longas que misturam ideias; várias notas curtas sobre a mesma ideia | Propor divisão ou fusão |
| Resíduos | Temporários `.tmp` antigos na Inbox; anexos não referenciados | Relatar |

Uma nota sem links não é automaticamente um problema. A avaliação considera o uso e o valor intelectual da nota.

## Resultado

- Relatório curto: verificações feitas, alcance, achados com links, correções realizadas e propostas pendentes.
- Quando a manutenção alterar arquivos, registrar um log curto em `50 Logs/` (`YYYY-MM-DD - Manutenção - HHMM.md`, `type: log`).
- Ao final, mostrar `git status` e oferecer um commit local. Não fazer push.
