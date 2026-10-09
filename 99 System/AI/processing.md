# Processamento da Inbox

Documento principal sobre a integração de capturas pelo curador: avaliação, destinos, proveniência, arquivamento, logs, idempotência e concorrência. Executado somente em uma sessão dedicada ao vault, quando o usuário solicita (por exemplo, "processe minha Inbox").

## Leitura prévia

`AGENTS.md`, [[99 System/AI/schemas]], [[99 System/AI/ingestion]], este documento e [[99 System/AI/mutation-policy]]. Em dúvida sobre entidades: [[99 System/AI/architecture]].

## Procedimento

1. Ler os documentos acima.
2. Procurar lotes interrompidos em `50 Logs/` (ver "Idempotência e retomada").
3. Enumerar as capturas pendentes: arquivos `.md` diretamente em `00 Inbox/`. Ignorar `.gitkeep`, arquivos iniciados por ponto, arquivos `.tmp` e templates. Arquivos não Markdown são anexos e nunca são tratados como notas.
4. Identificar cada entrada pelo `capture_id`. Uma captura manual sem `capture_id` recebe um UUID v4 antes de qualquer integração; se faltarem `type` ou `status`, acrescentar `type: capture` e `status: inbox`; se faltar `created`, usar a data indicada no nome ou no conteúdo e, na ausência, a data de modificação do arquivo, registrando no log que é aproximada. Registrar essas normalizações no log.
5. Procurar o `capture_id` nos logs, nas seções de proveniência e em `90 Archive/Inbox/` antes de integrar.
6. Ler a captura integralmente e conferir as referências necessárias à avaliação (anexos, notas citadas e, quando necessário e acessível, URLs). Uma URL não consultada continua pendente; não resumir seu conteúdo presumido.
7. Buscar notas equivalentes por títulos, aliases, properties e conteúdo (termos-chave, URLs, DOI, nomes), em `10 Projects/`, `20 Knowledge/`, `30 Sources/`, `80 Maps/` e `90 Archive/`.
8. Escolher e executar a menor integração útil.
9. Registrar os destinos no log à medida que forem produzidos e incluir proveniência nas notas de destino.
10. Validar: as notas criadas ou enriquecidas existem, o frontmatter é válido, os links internos resolvem e os anexos movidos continuam referenciados corretamente.
11. Concluir a captura somente após verificar a integração: arquivá-la ou mantê-la na Inbox com pendência registrada.
12. Fechar o lote no log, apresentar um resumo, mostrar `git status` e oferecer um commit local. Não fazer push.

## Destinos

- Criar ou enriquecer uma **Source** quando a origem consultável for relevante.
- Criar ou enriquecer **Knowledge** quando houver uma ideia reutilizável distinta.
- Registrar uma **metodologia em elaboração** (`status: draft` ou `processed`) quando houver um procedimento útil. Nunca `canonical` ([[99 System/AI/schemas]]).
- Vincular a um **projeto real existente** (property `projects` ou atualização da nota do projeto) ou criar um projeto explicitamente solicitado pelo usuário.
- **Arquivar** como registro histórico, duplicata ou material sem utilidade permanente, registrando a razão no log.
- **Manter na Inbox** quando faltar informação essencial, registrando a pendência no log.

Uma captura pode gerar uma Source e uma Knowledge Note quando ambas forem úteis. A quantidade de notas é determinada pelo valor de recuperação e aplicação, não pelo número de frases ou ideias da captura.

## Critérios de integração

- Preferir enriquecer a nota que já representa a mesma ideia.
- Knowledge deve ser compreensível isoladamente e ter tamanho proporcional ao raciocínio.
- Títulos declarativos são úteis para afirmações; conceitos e perguntas podem manter títulos apropriados à sua função.
- Novos nomes de notas seguem a regra de nomes portáveis de [[99 System/AI/ingestion]] e devem ser únicos no vault (verificar antes de criar). Notas permanentes não precisam de data nem identificador no nome.
- Não promover uma decisão específica de projeto a princípio universal sem examinar as condições em que ela se aplica. Preservar contexto, alternativas, justificativa e limites quando existirem.
- Manter a separação entre evidência, interpretação e opinião vinda da captura; identificar como tal as inferências do curador.
- Acrescentar somente conexões justificadas, para notas existentes, explicando a relação quando ela não for óbvia.
- Atualizar Maps existentes somente quando a relação intelectual for justificável. A criação de um novo Map é proposta ao usuário.
- Na Source, metadados desconhecidos ficam ausentes; nunca completar autor, data, DOI ou URL por suposição.

## Proveniência

Toda nota que recebe uma integração registra, em uma seção `## Proveniência` ao final, a data, o link para a captura, o `capture_id` e a natureza do que foi integrado. Formato:

```markdown
## Proveniência

- YYYY-MM-DD — [[YYYY-MM-DD - Título da captura - identificador-curto]] (capture_id: UUID completo): natureza do que foi integrado.
```

O exemplo é apenas sintaxe, com placeholders. O link continua válido após o arquivamento porque o nome da captura não muda. Quando a captura arquivada for o registro que sustenta a informação (por exemplo, uma experiência própria), ela também pode entrar em `sources`.

## Arquivamento da captura

- Concluída e verificada a integração, mover a captura para `90 Archive/Inbox/`, mantendo o nome do arquivo.
- Preservar o conteúdo original. Alterações permitidas: `status: archived` e ajustes de links necessários ao movimento. Ambas ficam rastreáveis no log.
- A associação entre a captura e suas saídas fica no log e nas seções de proveniência das notas de destino (visíveis como backlinks da captura).
- Anexos aproveitados como referência permanente podem ser movidos para `30 Sources/Attachments/`, com nomes estáveis. Anexos exclusivamente históricos acompanham a captura em `90 Archive/Inbox/`.
- Após mover capturas ou anexos, conferir todos os links afetados (busca pelo nome do arquivo). Wikilinks pelo nome continuam válidos; links com caminho precisam ser ajustados.
- Se o nome já existir no destino, não sobrescrever: relatar ou renomear acrescentando o identificador curto e ajustar os links.
- Exclusão definitiva não é um destino padrão. Material dispensável é arquivado com a razão correspondente.

## Log do lote

Cada lote tem um log em `50 Logs/`, nomeado `YYYY-MM-DD - Processamento da Inbox - HHMM.md` (hora local de início, sem dois-pontos). O log é curto e factual:

```markdown
---
type: log
created: YYYY-MM-DD
---
# Processamento da Inbox — YYYY-MM-DD HH:MM

Estado do lote: em andamento

## Capturas

### capture_id
- Captura: link para a captura (preservada em 90 Archive/Inbox/ ou mantida na Inbox)
- Ação: integrada | arquivada sem integração (razão) | mantida na Inbox
- Notas criadas: links
- Notas enriquecidas: links
- Normalizações: capture_id atribuído, campos acrescentados, links ajustados
- Pendências: o que falta e por quê
- Estado: em andamento | concluída

## Observações
```

Estados do lote: `em andamento` (definido ao iniciar), `concluído` (somente após as verificações) e `interrompido` (encerrado deliberadamente com capturas por concluir).

## Idempotência e retomada

- Registrar o início do lote antes da primeira escrita de integração e as saídas conforme forem produzidas; marcar a conclusão depois das verificações.
- Antes de processar uma captura, procurar seu `capture_id` nos logs, nas seções de proveniência e em `90 Archive/Inbox/`:
  - integração registrada como concluída e captura ainda na Inbox: verificar as saídas e apenas concluir o arquivamento;
  - integração em andamento: conferir os artefatos existentes e continuar a partir deles, sem recriá-los;
  - captura com o mesmo `capture_id` já arquivada: tratar como duplicata e não integrar novamente;
  - dois arquivos pendentes com o mesmo `capture_id`: não processar nenhum dos dois e relatar.
- Antes de acrescentar conteúdo ou proveniência a uma nota, verificar se o trecho correspondente já existe.
- Uma segunda execução não deve repetir conteúdo nem gerar novas cópias da mesma integração.
- Ao retomar um lote interrompido, continuar no mesmo log, acrescentando a linha `Retomado em YYYY-MM-DD HH:MM`.

## Concorrência

- A escrita do curador é sequencial: uma captura por vez e um único curador escrevendo.
- Um log com `Estado do lote: em andamento` pode indicar um lote interrompido ou outro processamento ativo. Informar o usuário e retomar somente se ele confirmar que não há outra sessão curadora em andamento.
- Se uma captura mudar entre a leitura e o arquivamento, não arquivá-la: preservar o estado e registrar a pendência.
- Agentes externos podem continuar criando capturas com nomes únicos durante o lote. Capturas surgidas depois da enumeração ficam para o próximo lote, salvo pedido do usuário.

## Encerramento

Apresentar ao usuário: capturas processadas e seus destinos, pendências, `git status` e a oferta de um commit local. Não fazer push nem configurar remotes.
