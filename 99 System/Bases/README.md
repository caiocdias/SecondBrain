# Bases — consultas recomendadas

O recurso nativo Bases do Obsidian cria visualizações a partir de properties. Este arquivo documenta os filtros recomendados; nenhum arquivo `.base` foi criado ainda. As visualizações podem ser configuradas quando houver uso real, e os arquivos `.base` resultantes ficam nesta pasta.

Todas as consultas excluem `99 System/`, para que templates e protocolos não apareçam como conteúdo. Campos e valores seguem [[99 System/AI/schemas]].

## Inbox

- Pasta: `00 Inbox/`.
- Arquivos Markdown (extensão `md`).
- `type` igual a `capture` e `status` igual a `inbox`.
- Colunas sugeridas: nome do arquivo, `created`, `capture_id`.
- Ordenação: `created` crescente (mais antigas primeiro).
- Capturas manuais ainda sem properties não aparecem nesta visualização; uma lista simples dos arquivos de `00 Inbox/` as revela.

## Sources

- `type` igual a `source`, fora de `99 System/`.
- Colunas sugeridas: nome, `subtype`, `status`, `created`, `topics`.
- Opcional: agrupar por `subtype`; excluir `90 Archive/`.

## Knowledge

- `type` igual a `knowledge` ou `type` igual a `methodology`, fora de `99 System/`.
- Filtro opcional: `status` igual a `canonical`, para ver apenas orientações aprovadas pelo usuário.
- Colunas sugeridas: nome, `type`, `subtype`, `status`, `updated`.
- Opcional: excluir `90 Archive/`.

## Projects

- `type` igual a `project`, fora de `99 System/`.
- O estado detalhado de cada projeto fica na própria nota; não há property de estado por enquanto.
- Colunas sugeridas: nome, `created`, `updated`.
