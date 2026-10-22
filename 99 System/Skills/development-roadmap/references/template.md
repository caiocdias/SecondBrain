# Template do roadmap

Estrutura de referência. Adapte títulos ao idioma do usuário e omita seções opcionais que não se aplicam, mas mantenha as tags canônicas, o formato do título das etapas, a tabela de índice e as seções de execução: o verificador `scripts/check_roadmap.py` depende deles.

Formatos que o verificador reconhece:

- título de etapa: `## E01 — Nome conciso — #pendente` (separador `—`, `–` ou `-`);
- índice: tabela Markdown cuja primeira coluna contém o ID puro (`E01`, sem link de âncora: a âncora inclui a tag e quebraria a cada mudança de estado), com uma coluna de estado contendo a tag e uma coluna de dependências contendo IDs ou `—`. Não cite IDs de outras etapas nas demais colunas do índice;
- dentro de uma etapa, use `###` ou rótulos em negrito; um `##` encerra a etapa para o verificador;
- seções de cabeçalho `## Protocolo de execução` e `## Prompt de execução` (esta com o prompt em bloco de código citando o arquivo do roadmap);
- em cada etapa, a linha `**Revisão humana:** sim` ou `não`;
- texto como `db/migration/<módulo>` é sinalizado como possível placeholder (aviso). Prefira escrever o padrão por extenso.

Para muitas etapas, agrupe o índice em blocos com uma linha de título entre as tabelas, repetindo o cabeçalho da tabela em cada bloco.

---

## Esqueleto

````markdown
# Roadmap — <título específico do projeto ou mudança>

> Arquivo: `<caminho/relativo/roadmap-slug.md>` · branch de execução: `roadmap/<slug>` · criado em AAAA-MM-DD · última revisão AAAA-MM-DD

## Como usar

Cole o "Prompt de execução" numa sessão limpa do Claude Code, na raiz do repositório. Ele executa até 3 etapas em sequência na branch `roadmap/<slug>`, cada uma planejada e executada pelo plugin superpowers, e para para revisão. No fim do lote você decide como integrar a branch (merge, PR, manter ou descartar). Para não parar em cada pedido de permissão, libere antes os comandos de build/teste do projeto nas permissões do Claude Code.

## Objetivo

<Resultado esperado em 2–4 frases, observável.>

## Contexto confirmado

- Stack: <linguagem, framework, versões vistas em manifestos>
- Estrutura relevante: `<caminho>` — <papel>
- Comandos confirmados: `<comando>` (fonte: `<arquivo>`)
- Design e documentos de referência: `<docs/superpowers/specs/AAAA-MM-DD-tema-design.md>`, `<SPEC.md §x>`
- Conhecimento do projeto no Second Brain: hub `<Projeto>` e notas de tema `<Projeto> - <Tema>` usadas pelo escopo (omita se o projeto não está registrado no brain)

## Escopo

**Incluído:** …

**Fora de escopo:** … (inclua aqui fases futuras e roadmaps sugeridos)

## Restrições e invariantes

Regras que toda etapa deve preservar (contratos públicos, convenções de código, segurança, compatibilidade, LGPD etc.). O planejador as copia para as "Global Constraints" de cada plano.

## Hipóteses e decisões em aberto

| # | Hipótese ou decisão | Impacto se errada / sem decisão | Etapa afetada |
|---|---|---|---|
| H1 | … | … | E03 |
| D1 | … (decisão em aberto) | … | E05 (bloqueada até decidir) |

## Definição global de pronto

- [ ] …

## Protocolo de execução

Vale para toda execução deste roadmap. O planejamento e a execução de cada etapa são feitos pelo plugin superpowers; este protocolo diz como encadear as etapas e manter o roadmap em dia.

**Papéis**

| Papel | Quem | Usa |
|---|---|---|
| Orquestrador | a sessão que recebeu o prompt de execução | este protocolo; atualiza tags e handoffs |
| Planejador | o orquestrador | `superpowers:writing-plans` |
| Implementador | subagente por tarefa | `superpowers:subagent-driven-development` (ou `superpowers:executing-plans`, sem subagentes) |
| Revisor de tarefa | subagente novo por tarefa | revisão da `subagent-driven-development` |
| Revisor final | subagente novo, modelo mais capaz | revisão final da `subagent-driven-development` |

Souls: nenhuma definida para estes papéis. Quando existir uma soul para um papel, ela se aplica a esse papel; até lá, valem os prompts padrão do superpowers.

**Branch**

- Toda execução acontece no worktree/branch `roadmap/<slug>`, criado ou retomado com `superpowers:using-git-worktrees`. Nunca execute na branch principal.
- Se a branch já existir com trabalho não integrado, continue nela. Se o lote anterior já foi integrado, crie a branch de novo a partir da branch principal atualizada.
- Este roadmap é atualizado dentro da branch: tags e handoffs viajam com o código.

**Por etapa**

1. **Escolha:** a primeira etapa, na ordem do documento, marcada `#pendente` e com todas as dependências `#concluida`. Etapas `#bloqueada` e as que dependem delas ficam para trás.
2. **Conferência:** leia a seção da etapa, os handoffs das dependências e o código que eles citam. Se o código divergiu do que a etapa supõe, pare e relate.
3. **Início:** troque a tag para `#em-andamento` (índice e título).
4. **Plano:** use `superpowers:writing-plans`. A spec é a seção desta etapa mais o design citado em "Contexto confirmado"; as "Restrições e invariantes" entram como Global Constraints. Salve em `docs/superpowers/plans/AAAA-MM-DD-<slug>-eNN.md`. A execução já está definida (abaixo): não pergunte ao usuário o método, apenas siga.
5. **Execução:** use `superpowers:subagent-driven-development` com esse plano, incluindo a revisão final da etapa. Não invoque `superpowers:finishing-a-development-branch` ao fim da etapa: ele roda uma vez, no fim do lote.
6. **Fechamento:** publique a captura de atualização do brain, se o bloco "Second Brain" se aplica. Marque `#concluida` (índice e título) só com a revisão final limpa e cada critério de aceite verificado com evidência. Diante de impedimento real, marque `#bloqueada` e preencha "Bloqueios" com causa, evidência, impacto e ação de desbloqueio. Preencha "Evidências e handoff". Rulings do ledger que mudam contrato, escopo, segurança, dados ou algo caro de desfazer vão para "Decisões para o usuário".

**Second Brain**

Vale se o `CLAUDE.md` tiver a seção "Conhecimento do projeto no Second Brain"; senão, ignore este bloco.

- O contexto da sessão precisa trazer a linha `BRAIN: carregado (<Projeto>)`, injetada pelo hook. Sem ela, pare e relate.
- Na conferência de cada etapa, leia as notas de tema do brain ligadas a ela e as capturas pendentes do projeto que tratem do assunto: são a referência técnica do projeto.
- No fechamento de cada etapa que mudou algo descrito no brain (inclusive o estado do roadmap), o orquestrador publica em `00 Inbox/` do vault a captura `<Projeto> - atualização <slug> Eyy`, com o texto novo ou alterado de cada nota afetada e qual nota ele substitui ou complementa, conforme o contrato de agente externo do vault. Nunca edite notas do brain nem registre referência técnica no `CLAUDE.md`.

**Paradas**

O lote para ao concluir uma etapa com **Revisão humana: sim**, diante de etapa `#bloqueada` ou divergência do plano, nas paradas do próprio superpowers (operação destrutiva, ação sensível de segurança, efeito fora da branch, plano sem caminho viável) e ao atingir o limite de etapas do prompt.

**Fim do lote**

1. Use `superpowers:finishing-a-development-branch`: o usuário decide merge, PR, manter ou descartar a branch. Nunca faça push, merge ou deploy sem essa decisão.
2. Apresente as "Decisões para o usuário" acumuladas como entrevista: perguntas de múltipla escolha, cada uma com uma opção recomendada e justificada (no Claude Code, `AskUserQuestion` com a recomendada em primeiro lugar e o rótulo "(Recomendado)"). Registre as respostas no handoff das etapas e em "Hipóteses e decisões em aberto".

## Prompt de execução

```text
Execute o roadmap <caminho/relativo/roadmap-slug.md> deste repositório seguindo a seção "Protocolo de execução" dele, com o plugin superpowers.

Limite desta execução: no máximo 3 etapas concluídas.

1. Leia CLAUDE.md (e AGENTS.md, se existir) e, no roadmap, o cabeçalho inteiro, o protocolo e o índice. Se o CLAUDE.md exigir o Second Brain, confira a linha BRAIN: carregado no contexto e leia o hub. Rode git status e git branch -a.
2. Se alguma etapa estiver #em-andamento, retome-a a partir do ledger do superpowers e do handoff; não recomece tarefas já commitadas.
3. Crie ou retome o worktree/branch roadmap/<slug> com superpowers:using-git-worktrees. Não trabalhe na branch principal.
4. Repita, uma etapa por vez: escolha a próxima etapa elegível, marque #em-andamento, planeje com superpowers:writing-plans (spec = seção da etapa + design citado), execute com superpowers:subagent-driven-development, feche a etapa e preencha o handoff conforme o protocolo.
5. Pare nas paradas do protocolo ou ao atingir o limite.
6. No fim, rode superpowers:finishing-a-development-branch e deixe a decisão de integração comigo. Depois, apresente as decisões para o usuário como entrevista com opção recomendada.

Nunca faça push, merge ou deploy sem minha decisão. Não altere tags de etapas que não executou.

Ao parar, responda com: etapas concluídas e o resultado da revisão final de cada uma, a etapa atual e seu estado, o motivo da parada, as etapas #bloqueada com a ação de desbloqueio, a branch e os commits do lote e o próximo passo sugerido.
```

## Índice de etapas

| ID | Etapa | Estado | Dependências | Entrega principal |
|---|---|---|---|---|
| E01 | … | #pendente | — | … |
| E02 | … | #pendente | E01 | … |
| E03 | … | #pendente | E01 | … |

---

## E01 — <Nome conciso> — #pendente

**Objetivo:** …

**Por que agora:** …

**Dependências:** nenhuma. / E01.

**Escopo:** comportamento e áreas do sistema afetadas; caminhos citados só se confirmados, ou rotulados "(a criar)".

**Fora de escopo:** …

**Critérios de aceite:**

- [ ] …

**Validação obrigatória:**

- `<comando>` → resultado esperado.
- Inspeção manual: …

**Revisão humana:** não

**Notas para o plano:** só o que o planejador não descobriria lendo o código (armadilha conhecida, convenção vinda de outra etapa) — ou "nenhuma".

**Bloqueios:** Nenhum bloqueio conhecido.

**Riscos e mitigação:**

- …

**Rollback / migração:** (só para mudanças destrutivas, de dados, de contrato público, infraestrutura ou implantação)

**Evidências e handoff:**

- Plano: —
- Commits: —
- Revisão final: —
- Critérios verificados: —
- Decisões para o usuário: —
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

## Exemplo de etapa

Note que a etapa diz o quê e como saber que terminou; arquivos, assinaturas e passos ficam para o plano.

```markdown
## E03 — Cadastro de unidades habitacionais (UHs) — #pendente

**Objetivo:** CRUD de UHs em `/v1/rooms`, persistido, com a permissão `rooms:manage` exigida para escrita.

**Por que agora:** reservas (E05) e disponibilidade (E07) dependem de UHs cadastradas.

**Dependências:** E01, E02.

**Escopo:** API REST de UHs no módulo de hospedagem, migração do banco e contrato OpenAPI. Regras de status de UH em SPEC.md §5.4.

**Fora de escopo:** tarifas (E05), disponibilidade (E07), alterações no módulo de autenticação.

**Critérios de aceite:**

- [ ] endpoints de `/v1/rooms` no contrato OpenAPI e cobertos por testes de integração;
- [ ] número de UH duplicado → 409 no formato de erro padrão;
- [ ] escrita sem `rooms:manage` → 403.

**Validação obrigatória:**

- build, testes e lint com os comandos registrados no handoff de E01 → todos passam.

**Revisão humana:** não

**Notas para o plano:** o padrão de testes de integração com banco foi definido em E01 (ver handoff).
```
