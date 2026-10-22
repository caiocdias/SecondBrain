# Schemas e properties

Documento principal sobre properties, valores de `type`, `subtype` e `status`, datas, `capture_id` e sintaxe de links. Entidades e pastas estão em [[99 System/AI/architecture]].

## Campos gerais

| Campo | Uso |
|---|---|
| `type` | Obrigatório nas notas de conteúdo. |
| `subtype` | Opcional. |
| `status` | Quando representar um estado útil. |
| `created` | Data de criação. |
| `updated` | Data de atualização substantiva, quando útil. |
| `topics` | Lista opcional de links para notas existentes. |
| `projects` | Lista opcional de links para projetos existentes. |
| `sources` | Lista opcional de notas que sustentam o conteúdo. |
| `aliases` | Lista opcional de nomes alternativos. |

Campo específico: `capture_id`, obrigatório em capturas (ver abaixo).

Notas de conteúdo são as notas fora de `99 System/` e dos arquivos de contrato da raiz. Protocolos, READMEs e templates não são notas de conteúdo.

Omitir campos sem valor nas notas reais. Evitar objetos YAML aninhados e listas extensas de campos vazios.

## `type`

Valores: `capture`, `source`, `knowledge`, `methodology`, `project`, `map`, `log`.

Inbox é uma localização e um estado: o `type` de uma captura é `capture`; não usar `type: inbox`. Uma nota arquivada mantém seu `type` original.

## `status`

| Valor | Significado |
|---|---|
| `inbox` | Captura pendente de avaliação. |
| `draft` | Elaboração inicial. |
| `processed` | Processamento inicial concluído. |
| `reviewed` | Conteúdo conscientemente revisado; processar não equivale a revisar. |
| `canonical` | Orientação pessoal explicitamente aprovada pelo usuário. |
| `archived` | Preservação histórica. |

Usar `status` somente onde fizer sentido:

- Captura: `inbox` enquanto pendente; `archived` depois de arquivada em `90 Archive/Inbox/`.
- Source, Knowledge e Methodology: `draft`, `processed`, `reviewed`; `canonical` somente para orientação pessoal (metodologia ou, por exemplo, um princípio) aprovada pelo usuário; `archived` quando preservada em `90 Archive/`.
- Project: estados próprios (ativo, pausado, concluído etc.) ficam no corpo da nota até existir necessidade real de consulta estruturada.
- Map e Log: normalmente sem `status`.

### Promoção a `canonical`

Uma metodologia produzida por um agente começa como `draft` ou `processed`. A promoção a `canonical` exige aprovação explícita do usuário; frequência de uso ou confiança do modelo não substituem essa decisão. Ao promover, registrar no histórico de revisão da nota a data e a aprovação do usuário. Rebaixar ou substituir uma orientação `canonical` também exige decisão do usuário.

## `subtype`

Recomendações, não obrigação de classificar artificialmente toda nota:

- `source`: `article`, `paper`, `book`, `game`, `video`, `podcast`, `documentation`, `web`, `course`, `other`.
- `knowledge`: `concept`, `claim`, `principle`, `model`, `question`, `comparison`, `insight`.

Outros tipos não têm subtypes recomendados; introduzi-los somente diante de necessidade observada.

## Datas

- Formato `YYYY-MM-DD`, com a data real no fuso local do usuário (por exemplo, `date +%F`; no PowerShell, `Get-Date -Format yyyy-MM-dd`).
- Não inventar datas de publicação ou de acesso; metadados desconhecidos ficam ausentes.
- Em templates, usar `{{date}}` e `{{title}}`, do recurso nativo Templates do Obsidian.

## `capture_id`

- Obrigatório em toda captura: identificador único gerado no momento da captura, como um UUID v4 em minúsculas (`uuidgen` ou `python3 -c "import uuid; print(uuid.uuid4())"`; no PowerShell, `[guid]::NewGuid().ToString()`).
- Identificador curto: os 8 primeiros caracteres, usados no nome do arquivo ([[99 System/AI/ingestion]]).
- Imutável e preservado durante todo o ciclo, inclusive após o arquivamento. Nunca reutilizar.
- Captura manual sem `capture_id` recebe um do curador antes do processamento ([[99 System/AI/processing]]).
- Permite rastrear integrações e evitar processar a mesma captura mais de uma vez.

## Links

### Em properties

Listas YAML de strings entre aspas:

```yaml
sources:
  - "[[Nome de uma fonte existente]]"
```

O exemplo é apenas sintaxe; não criar a nota indicada.

- Links apontam somente para notas existentes.
- `sources` pode apontar para uma Source ou outro registro que realmente sustente a informação, inclusive uma captura arquivada de experiência própria. Não fabricar uma fonte externa para justificar uma observação pessoal.

### No corpo das notas

- Notas de conteúdo: wikilinks pelo nome da nota, sem caminho (`[[Nome da nota]]`). Nomes únicos no vault mantêm os links válidos quando um arquivo muda de pasta, por exemplo ao arquivar uma captura.
- Anexos: `![[nome-do-arquivo.ext]]` para incorporar ou `[[nome-do-arquivo.ext]]` para referenciar.
- Protocolos e documentação em `99 System/` usam o caminho a partir da raiz, pois há nomes repetidos (como `README`).
- Links externos: `[texto](URL)`, somente com URL real.
- Temas sugeridos sem nota correspondente permanecem texto simples ([[99 System/AI/retrieval]]).

## Metadados de origem

Metadados bibliográficos e de origem podem ficar no corpo da nota. Acrescentar properties específicas somente quando resolverem uma necessidade concreta.

## Mudanças de schema

Mudanças globais de schema (novos campos ou valores de uso geral, renomeações, mudanças de significado) exigem aprovação ([[99 System/AI/mutation-policy]]). Campos novos devem atender a uma necessidade observada. Correções locais de properties claramente inconsistentes são permitidas ao curador dentro de uma tarefa solicitada.
