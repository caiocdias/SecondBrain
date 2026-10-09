# Política de mutação

Documento principal sobre o que cada papel pode alterar no vault e o que exige autorização explícita do usuário.

## Agente externo

- Leitura pertinente.
- Criação de novas capturas e anexos em `00 Inbox/`.
- Nenhuma outra mutação do vault. Detalhes em [[99 System/AI/external-agents]].

## Curador

No contexto de uma tarefa solicitada pelo usuário, o curador:

- Pode criar e complementar notas, acrescentar links pertinentes e corrigir formatação e properties claramente inconsistentes.
- Pode integrar capturas e arquivá-las seguindo [[99 System/AI/processing]].
- Pode atualizar Maps existentes quando a relação intelectual for justificável.
- Deve conferir referências e backlinks antes de renomear, mover ou consolidar notas.
- Pode usar operações nativas do Obsidian que preservem links, quando disponíveis.

O curador não age sem solicitação: não há manutenção nem reorganização por iniciativa própria.

## Exigem autorização explícita que cubra a mudança

- Exclusão substancial ou definitiva.
- Reorganização estrutural ampla, inclusive criar, renomear ou remover pastas.
- Mudança global de schema ([[99 System/AI/schemas]]).
- Movimentações, renomeações ou fusões em massa, isto é, além das notas diretamente envolvidas na tarefa em curso.
- Substituição de convenções centrais ou da filosofia arquitetural, inclusive mudanças de regra em `AGENTS.md` ou em `99 System/AI/`.
- Perda de histórico ou proveniência.
- Promoção de conteúdo pessoal a `canonical`.

## Proposta de mudança

Quando precisar dessa decisão, o agente prepara uma proposta concreta: o que muda e por quê, os arquivos afetados (lista ou contagem), os riscos e como reverter. A aprovação cobre apenas o escopo descrito.

Mudanças locais já autorizadas pela tarefa prosseguem sem confirmações repetitivas.

## Git

- O curador pode mostrar `git status` e `git diff` e oferecer um commit local; o commit é feito somente com a concordância do usuário.
- Nunca fazer push, configurar remotes ou reescrever o histórico sem pedido explícito.
- Nunca registrar credenciais, tokens ou segredos.

## Preservação

Exclusão definitiva não é destino padrão: material dispensável é arquivado com a razão correspondente. Histórico e proveniência são preservados em todas as operações.
