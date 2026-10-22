# Template do roadmap

Estrutura de referência. Adapte títulos ao idioma do usuário e omita seções opcionais que não se aplicam, mas mantenha as tags canônicas, o formato do título das etapas e a tabela de índice — o verificador `scripts/check_roadmap.py` depende deles.

Formatos que o verificador reconhece:

- título de etapa: `## E01 — Nome conciso — #pendente` (separador `—`, `–` ou `-`);
- índice: tabela Markdown cuja primeira coluna contém o ID puro (`E01` — não use link de âncora: a âncora inclui a tag e quebraria a cada mudança de estado), com uma coluna de estado contendo a tag e uma coluna de dependências contendo IDs ou `—`. Não cite IDs de outras etapas nas demais colunas do índice;
- prompt: o primeiro bloco de código cercado (```` ``` ````) após o rótulo da etapa que contém "Prompt" (`**Prompt…**` ou `### Prompt…`);
- dentro de uma etapa, use `###` ou rótulos em negrito; um `##` encerra a etapa para o verificador;
- seções de cabeçalho "Protocolo de execução" e "Execução automática" (esta com o prompt do orquestrador em bloco de código citando o arquivo do roadmap) e, em cada etapa, o rótulo "Estratégia de execução" com `direta`, `padrão` ou `paralela`;
- texto como `db/migration/<módulo>` é sinalizado como possível placeholder (aviso). Prefira escrever o padrão por extenso ("uma pasta por módulo em `db/migration/`").

Para muitas etapas, agrupe o índice em blocos com uma linha de título entre as tabelas (ex.: `**Plataforma**` antes da tabela de E01–E05), repetindo o cabeçalho da tabela em cada bloco.

---

## Esqueleto

````markdown
# Roadmap — <título específico do projeto ou mudança>

> Arquivo: `<caminho/relativo/roadmap-slug.md>` · criado em AAAA-MM-DD · última revisão AAAA-MM-DD

## Como usar

Duas formas, ambas na raiz do repositório:

- **Manual:** cole o prompt de uma etapa numa sessão limpa do Claude Code. Uma etapa por sessão.
- **Automática:** cole o prompt da seção "Execução automática" numa sessão limpa; ela executa até 3 etapas em sequência, um subagente por etapa mais um verificador, e para para revisão. Para não parar em cada pedido de permissão, libere antes os comandos de build/teste do projeto nas permissões do Claude Code.

Etapas marcadas como paralelizáveis só devem rodar ao mesmo tempo em worktrees git separados; na mesma pasta, rode-as uma de cada vez.

Em ambas, quem executa segue o "Protocolo de execução", atualiza a tag da etapa e preenche "Evidências e handoff". Não pule dependências. Revise e faça commit entre etapas ou lotes — nenhuma sessão faz commit por conta própria.

## Objetivo

<Resultado esperado em 2–4 frases, observável.>

## Contexto confirmado

- Stack: <linguagem, framework, versões vistas em manifestos>
- Estrutura relevante: `<caminho>` — <papel>
- Comandos confirmados: `<comando>` (fonte: `<arquivo>`)
- Documentos de referência: `<SPEC.md §x>`, `<ARCHITECTURE.md §y>`

## Escopo

**Incluído:** …

**Fora de escopo:** … (inclua aqui fases futuras e roadmaps sugeridos)

## Restrições e invariantes

Regras que toda sessão deve preservar (contratos públicos, convenções de código, segurança, compatibilidade, LGPD etc.).

## Hipóteses e decisões em aberto

| # | Hipótese ou decisão | Impacto se errada / sem decisão | Etapa afetada |
|---|---|---|---|
| H1 | … | … | E03 |
| D1 | … (decisão em aberto) | … | E05 (bloqueada até decidir) |

## Definição global de pronto

- [ ] …

## Protocolo de execução

Vale para toda etapa, executada manualmente ou pelo orquestrador. Cada etapa declara sua estratégia em "Estratégia de execução".

**Papéis**

- **Sessão principal** (no modo automático, o subagente implementador): a única que edita código e este roadmap. Implementa, testa, atualiza tags e handoff.
- **Investigação** (subagente `Explore`, somente leitura): para material extenso que será lido mas não editado. Recebe as perguntas listadas na etapa e devolve um resumo com caminhos e linhas. Arquivos que serão editados são lidos diretamente pela sessão principal.
- **Implementação paralela** (subagentes `general-purpose`, só na estratégia `paralela`): cada um recebe uma parte com os arquivos listados na etapa, disjuntos dos demais; roda só os testes focados da sua parte; não toca arquivos compartilhados (build, configuração, este roadmap).
- **Verificação independente** (subagente `general-purpose` novo, que não participou da implementação): confere a etapa contra os critérios de aceite. Não edita nada.

**Estratégias:** `direta` — sem subagentes, a sessão principal valida · `padrão` — investigação quando indicada + verificação independente obrigatória · `paralela` — `padrão` + partes paralelas.

**Passo a passo**

1. **Preparação:** leia CLAUDE.md (e AGENTS.md, se existir), o cabeçalho deste roadmap, a seção da etapa e o handoff das dependências; rode `git status`. Confirme que as dependências estão `#concluida`, que a etapa não está `#bloqueada` e que o código bate com o handoff das dependências; se não, pare e relate.
2. **Snapshot inicial:** registre o estado da árvore de trabalho, sem commit e sem alterar o índice do git:

   ```bash
   idx=$(mktemp -u); cp "$(git rev-parse --git-path index)" "$idx" 2>/dev/null; GIT_INDEX_FILE="$idx" git add -A && GIT_INDEX_FILE="$idx" git write-tree; rm -f "$idx"
   ```

   Anote o hash impresso como "Snapshot inicial" no handoff da etapa (no modo automático, use o hash recebido do orquestrador em vez de tirar outro). Para ver tudo o que a etapa mudou, rode o mesmo comando de novo e compare: `git diff HASH_INICIAL HASH_ATUAL`. Se `git status` mostrar artefatos de build não ignorados, corrija o `.gitignore` antes do snapshot — senão o diff fica lento e poluído.
3. **Início:** troque a tag da etapa para `#em-andamento` no índice e no título.
4. **Investigação** (se a etapa listar perguntas): dispare um subagente `Explore` com essas perguntas.
5. **Implementação:** quando os critérios descrevem comportamento verificável, escreva os testes primeiro e confirme que falham. Implemente em passos pequenos; na estratégia `paralela`, dispare as partes paralelas e integre-as. Rode as validações obrigatórias da etapa.
6. **Verificação independente** (`padrão` e `paralela`): dispare um subagente `general-purpose` novo com o "Prompt do verificador" abaixo, trocando ETAPA pelo ID da etapa e HASH_INICIAL pelo snapshot. Se o parecer for REPROVADO, corrija e verifique de novo com um verificador novo. Após duas reprovações, pare e relate, mantendo `#em-andamento`.
7. **Fechamento:** marque `#concluida` (índice e título) só com todos os critérios atendidos e, quando houver verificação, parecer APROVADO. Diante de impedimento real, marque `#bloqueada` e preencha "Bloqueios" com causa, evidência, impacto e ação de desbloqueio. Preencha "Evidências e handoff" e responda com um resumo curto. Não faça commit, push ou deploy.

**Prompt do verificador**

```text
Você é o verificador independente da etapa ETAPA do roadmap <caminho/relativo/roadmap-slug.md>. Você não participou da implementação e não deve editar nenhum arquivo.
1. Leia CLAUDE.md, o cabeçalho do roadmap e a seção ETAPA inteira (objetivo, escopo, fora de escopo, estratégia, critérios de aceite, validação obrigatória).
2. Veja o que mudou desde o início da etapa: gere um snapshot do estado atual com o comando da seção "Protocolo de execução" e rode git diff --stat HASH_INICIAL seguido do hash gerado; depois leia o diff completo dos arquivos relevantes.
3. Rode todos os comandos da validação obrigatória da etapa e guarde a saída relevante.
4. Para cada critério de aceite, decida APROVADO ou REPROVADO com evidência concreta (arquivo:linha, nome do teste, saída de comando). Critério sem evidência é REPROVADO.
5. Ataque os pontos listados em "Foco do verificador" na etapa e aponte também: mudanças fora do escopo, testes que não exercitam o comportamento (passariam mesmo com o código errado), segredos ou dados pessoais expostos e violações das restrições do roadmap.
Responda com: parecer geral (APROVADO só se todos os critérios forem APROVADO e não houver problema grave), tabela critério → resultado → evidência, problemas por gravidade e comandos executados.
```

## Execução automática

Cole o prompt abaixo numa sessão limpa do Claude Code, na raiz do repositório. Ajuste o limite de etapas se quiser.

```text
Você é o orquestrador do roadmap <caminho/relativo/roadmap-slug.md> neste repositório. Seu papel é coordenar subagentes, não implementar: não edite código e mantenha seu contexto enxuto (leia o roadmap e os relatórios dos subagentes, não o código).

Limite desta execução: no máximo 3 etapas concluídas.

Preparação:
1. Leia CLAUDE.md (e AGENTS.md, se existir) e, no roadmap, o cabeçalho, o "Protocolo de execução" e o índice.
2. Rode git status. Se alguma etapa estiver #em-andamento, pare e pergunte ao usuário como prosseguir — provavelmente é uma execução interrompida.

Repita, uma etapa por vez (nunca em paralelo):
1. Escolha a primeira etapa, na ordem do documento, marcada #pendente e com todas as dependências #concluida. Etapas #bloqueada e as que dependem delas ficam para trás. Se não houver candidata, pare.
2. Gere o snapshot inicial com o comando do protocolo e guarde o hash.
3. Dispare um subagente general-purpose com o prompt da etapa copiado literalmente da seção dela, acrescido deste adendo: "Você está rodando como subagente do orquestrador; este adendo prevalece sobre o prompt acima. O snapshot inicial já foi tirado: use HASH e não tire outro. Não dispare subagentes: faça a investigação você mesmo, implemente em sequência as partes paralelas, se houver, e pule a verificação independente, que o orquestrador fará. Não marque a etapa como #concluida: ao terminar, deixe-a #em-andamento com 'Evidências e handoff' preenchido e relate o resultado das validações. Diante de bloqueio real, marque #bloqueada como o prompt manda." Substitua HASH pelo hash do passo 2.
4. Se o subagente relatar bloqueio, divergência do plano ou validação falhando que não conseguiu resolver, pare.
5. Qualquer que seja a estratégia, dispare um subagente general-purpose novo com o "Prompt do verificador" do protocolo (ETAPA e HASH_INICIAL preenchidos). Se REPROVADO, mande os problemas ao mesmo implementador, se puder retomá-lo; senão, dispare um implementador novo com o prompt da etapa, o adendo, o parecer do verificador e o handoff atual. Verifique de novo com um verificador novo; após duas reprovações, pare.
6. Com o aceite, troque a tag da etapa para #concluida no índice e no título e acrescente ao handoff o parecer do verificador.
7. Se a etapa tiver "Revisão humana: sim", pare para o usuário revisar.

Pare também ao atingir o limite desta execução. Nunca faça commit, push ou deploy e não altere tags de etapas que não executou.

Ao parar, responda com: etapas concluídas e seus pareceres, a etapa atual e seu estado, o motivo da parada, as etapas #bloqueada com a ação de desbloqueio de cada uma, os arquivos alterados (git status --short) e o próximo passo sugerido — normalmente revisar e fazer commit antes da próxima execução.
```

## Índice de etapas

| ID | Etapa | Estado | Dependências | Entrega principal |
|---|---|---|---|---|
| E01 | … | #pendente | — | … |
| E02 | … | #pendente | E01 | … |
| E03 | … | #pendente | E01 | … (paralelizável com E02) |

---

## E01 — <Nome conciso> — #pendente

**Objetivo:** …

**Por que agora:** …

**Dependências e paralelismo:** nenhuma. / E01. Pode correr em paralelo com E03 (em worktree separado); conflito de edição em `<arquivo>`.

**Escopo:** caminhos e interfaces confirmados; caminhos prováveis rotulados como "(a criar)" ou "(provável)".

**Fora de escopo:** …

**Passos de implementação:**

1. …

**Estratégia de execução:** `padrão` · Revisão humana: não

- Investigação (`Explore`): perguntas objetivas, ex.: "quais regras de transição de status de UH a SPEC.md §5.4 define?" — ou "nenhuma".
- Partes paralelas: só na estratégia `paralela`, cada uma com seus arquivos — ou "nenhuma".
- Foco do verificador: riscos específicos desta etapa, ex.: "escrita sem permissão", "migração reversível". Em etapas `direta`, o verificador só atua no modo automático; mantenha um foco curto mesmo assim.

**Prompt para uma sessão limpa:**

```text
<prompt autocontido — ver exemplo abaixo>
```

**Critérios de aceite:**

- [ ] …

**Validação obrigatória:**

- `<comando>` → resultado esperado.
- Inspeção manual: …

**Bloqueios:** Nenhum bloqueio conhecido.

**Riscos e mitigação:**

- …

**Rollback / migração:** (só para mudanças destrutivas, de dados, de contrato público, infraestrutura ou implantação)

**Evidências e handoff:**

- Snapshot inicial: —
- Arquivos alterados: —
- Decisões: —
- Validações executadas: —
- Parecer do verificador: —
- Notas para a próxima etapa: —

---

## Histórico de revisões

- AAAA-MM-DD — roadmap criado.
````

(Os `<...>` acima são campos do template; o roadmap entregue não pode conter nenhum.)

---

## Exemplo de bloqueio real

```markdown
**Bloqueios:**

- **Causa:** o contrato com o middleware fiscal ainda não foi assinado; não há credenciais de homologação.
- **Evidência:** SPEC.md §7.2 lista o fornecedor como "a definir"; não há variáveis de ambiente fiscais em `application.yml`.
- **Impacto:** impede testar a emissão de NFS-e ponta a ponta (critérios 3 e 4).
- **Ação de desbloqueio:** usuário escolhe o fornecedor e fornece credenciais de homologação; registrar a decisão em D2 e trocar a tag desta etapa para `#pendente` (índice e título).
```

Contraexemplo: "E04 ainda não foi concluída" **não** é bloqueio de E05 — é dependência, e E05 fica `#pendente`.

---

## Exemplo de prompt autocontido

Note que o prompt não copia escopo, passos nem o protocolo: manda lê-los. Repete só o objetivo, o limite caro de violar, os critérios de aceite e o que é específico da estratégia desta etapa.

```text
Execute a etapa E03 — "Cadastro de unidades habitacionais (UHs)" do roadmap docs/roadmap-fase-1-hospedagem.md, neste repositório.

Antes de alterar qualquer coisa, leia CLAUDE.md (e AGENTS.md, se existir), o cabeçalho do roadmap — incluindo o "Protocolo de execução" —, a seção E03 inteira e o "Evidências e handoff" de E01 e E02. Rode git status e preserve mudanças preexistentes que não sejam suas. Confirme que E01 e E02 estão #concluida e que o código bate com o handoff delas; se não, ou se o código divergiu do plano, pare e relate sem implementar.

Objetivo: CRUD de UHs em /v1/rooms, persistido via migração Flyway, com a permissão rooms:manage exigida para escrita. Não altere o módulo de autenticação; tarifas e disponibilidade ficam para E05 e E07.

Siga o Protocolo de execução com a estratégia padrão:
- tire o snapshot inicial e troque a tag de E03 para #em-andamento no índice e no título;
- investigação: um subagente Explore resume as regras de status de UH em SPEC.md §5.4 e o padrão de testes de integração registrado no handoff de E01;
- escreva os testes de integração primeiro, implemente e rode build, testes e lint (comandos registrados no handoff de E01);
- verificação independente com o Prompt do verificador, com foco em escrita sem rooms:manage e em número de UH duplicado.

Critérios de aceite (detalhes na seção E03):
- endpoints de /v1/rooms no contrato OpenAPI e cobertos por testes de integração;
- número de UH duplicado → 409 no formato de erro padrão; escrita sem rooms:manage → 403;
- build, testes e lint passam.

Não declare sucesso com validação falhando ou não executada. Marque #concluida só com todos os critérios atendidos e parecer APROVADO do verificador; diante de impedimento real, marque #bloqueada e registre causa, evidência, impacto e ação de desbloqueio em "Bloqueios".

No fim, preencha "Evidências e handoff" de E03 (snapshot, arquivos alterados, decisões, comandos e resultados, parecer do verificador, notas para a próxima etapa) e responda com um resumo curto de mudanças, validações e pendências. Não faça commit, push ou deploy.
```
