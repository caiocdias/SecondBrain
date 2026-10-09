# Captura

Documento principal sobre a criação de capturas: nome, frontmatter, corpo, anexos e publicação segura. É também o documento principal da regra de nomes portáveis, válida para todo arquivo novo no vault.

## Escopo

- Todas as novas capturas de agentes entram em `00 Inbox/`.
- Agente externo: ver também [[99 System/AI/external-agents]].
- Curador: um pedido de registro também gera uma captura na Inbox; se o usuário pedir, o curador pode processá-la em seguida conforme [[99 System/AI/processing]].
- O usuário pode editar manualmente o vault e criar notas permanentes quando desejar.

Capture texto, referência, URL, observação, pergunta, aprendizado ou arquivo com a menor estrutura suficiente.

## Antes de publicar

1. Obter a data real (`date +%F`).
2. Gerar o `capture_id` ([[99 System/AI/schemas]]).
3. Fazer uma busca breve por registro equivalente, sem carregar o vault inteiro: termos-chave, URL ou nome do projeto em `00 Inbox/`, e títulos e aliases das notas permanentes. Havendo equivalente, seguir "Capturas equivalentes" em [[99 System/AI/external-agents]].

## Nome do arquivo

```text
YYYY-MM-DD - Título descritivo - identificador-curto.md
```

- Data real da captura.
- Identificador curto: os 8 primeiros caracteres do `capture_id`, para reduzir colisões.
- Título curto e descritivo.

### Regra de nomes portáveis

O vault pode ser sincronizado entre Linux, Windows, macOS e Android. Em qualquer arquivo novo (capturas, notas, anexos):

- Não usar os caracteres `\ / : * ? " < > |`.
- Evitar também `# ^ [ ]`, que interferem em links do Obsidian.
- Não terminar o nome com ponto ou espaço.
- Manter o título curto.
- Não usar nomes reservados do Windows (`CON`, `PRN`, `AUX`, `NUL`, `COM1`…`COM9`, `LPT1`…`LPT9`).
- Não distinguir arquivos apenas por maiúsculas e minúsculas.

Letras acentuadas são permitidas (UTF-8).

## Frontmatter mínimo

```yaml
---
type: capture
status: inbox
created: DATA_REAL
capture_id: IDENTIFICADOR_UNICO_REAL
---
```

Os valores acima são placeholders de documentação e devem ser substituídos antes da publicação de uma captura real. Outros campos de [[99 System/AI/schemas]] entram somente com valor real e links para notas existentes.

## Corpo

Estrutura recomendada, omitindo seções sem conteúdo:

```markdown
# Título

## Conteúdo capturado
## Contexto
## Origem
## Por que registrar
## Limitações e incertezas
## Possíveis conexões
```

- **Conteúdo capturado**: o material em si, com a natureza de cada parte identificada (ver "Fidelidade").
- **Contexto**: a situação ou o trabalho em que surgiu.
- **Origem**: somente informações disponíveis: projeto, caminho, arquivo, trecho, URL, commit, referência de conversa ou data de acesso. Um projeto externo não precisa ter uma nota própria no vault; nesse caso, registrar o nome e a referência em texto.
- **Por que registrar**: a utilidade esperada.
- **Limitações e incertezas**: o que não foi verificado, referências pendentes e dependências de caminhos locais.
- **Possíveis conexões**: links para notas existentes; ideias de temas sem nota permanecem texto simples.

## Fidelidade

- Separar conteúdo original, resumo do agente, interpretação, decisão tomada e opinião explícita do usuário, com rótulos claros (por exemplo, "Resumo do agente:", "Interpretação:", "Decisão:", "Opinião do usuário:").
- Um aprendizado inferido pelo agente não deve ser apresentado como convicção já estabelecida do usuário.
- Citações precisam ser literais e rastreáveis até sua localização. Paráfrases são identificadas como resumo ou interpretação.
- Uma URL não consultada permanece uma referência pendente, sem resumo presumido.
- Nunca inventar fontes, autores, datas, DOI, URLs ou resultados.
- Não registrar credenciais, tokens ou outros segredos como parte do contexto.

## Anexos

- Copiar para `00 Inbox/` somente os arquivos necessários para preservar o material, sem subpastas.
- Nome único associado à captura: `identificador-curto - nome-descritivo.ext`, seguindo a regra de nomes portáveis.
- Referenciar na captura com link interno: `![[identificador-curto - nome-descritivo.ext]]` ou `[[...]]`.
- Confirmar que a cópia existe e não está vazia antes de afirmar que o material foi preservado.
- Um anexo nunca é uma captura por si só; precisa ser referenciado por uma captura.

## Dependências locais

Evitar depender apenas de um arquivo temporário ou de um caminho que desaparecerá após o projeto. Quando só houver uma referência local, explicitar essa dependência em "Limitações e incertezas" (por exemplo: arquivo não copiado; disponível apenas no caminho X do projeto Y).

## Publicação segura

- Publicar arquivos completos, de uma só vez.
- Não sobrescrever capturas concorrentes: verificar que o nome final não existe e preferir criação exclusiva.
- Publicação atômica, quando as ferramentas permitirem: escrever primeiro um temporário em `00 Inbox/` com nome iniciado por ponto e terminado em `.tmp` (por exemplo, `.identificador-curto.md.tmp`), renomeá-lo para o nome final sem sobrescrever e verificar o resultado.
- Arquivos iniciados por ponto ou terminados em `.tmp` não são capturas prontas e são ignorados pelo processamento. Se a publicação falhar, o agente remove o próprio temporário.
- Após publicar, confirmar que o arquivo existe, que o frontmatter contém o `capture_id` correto e que os anexos referenciados existem.

## Encerramento

Um agente externo encerra a captura neste ponto e informa o caminho criado. Não converte a entrada em conhecimento permanente durante a tarefa do projeto.

## Captura manual

O usuário pode criar capturas com `99 System/Templates/Capture.md`, com qualquer nome que siga a regra de nomes portáveis. O `capture_id` pode ficar vazio; o curador o atribui antes de processar.
