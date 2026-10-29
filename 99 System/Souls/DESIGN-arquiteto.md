# Soul arquiteto — documento de design

Status: rascunho para aprovação do usuário. Criado em 2026-10-29 numa entrevista com o usuário no modelo do brain ([[Decidir pendências do usuário por entrevista com opção recomendada]]), a pedido dele. Complementa o [design das seis souls](DESIGN.md); tudo o que lá vale para as souls (anatomia, travas, sincronização, testes) vale aqui, salvo o que este documento muda.

Marcadores: **[usuário]** indica decisão do usuário; **[agente]** indica escolha do agente que escreveu o design, revisável pelo usuário.

## 1. Intenção

Hoje o desenho e o planejamento acontecem numa sessão comum, e o plano de cada etapa é escrito pelo `orquestrador-etapa` e executado logo em seguida, sem que ninguém confira se ele respeita a arquitetura. A soul `arquiteto` cobre essas duas lacunas, em continuidade com o princípio das souls ("cada parte entregue ao especialista certo, e um confere o outro"):

1. **Sessão de desenho com travas:** um especialista em system design conduz descoberta, desenho e roadmap, carregando sob demanda o contexto de arquitetura do projeto e do brain, sem conseguir escrever código.
2. **Revisão de plano antes da execução:** um erro de arquitetura achado no plano custa uma rodada de revisão; achado na revisão final, custa refazer a etapa.

## 2. Objetivos, não-objetivos e anti-objetivos

**Objetivos**

1. Soul com **dois usos e uma identidade** [usuário]: sessão principal de desenho e revisor do plano de cada etapa.
2. Orquestrador escreve o plano e o arquiteto revisa [usuário], no mesmo princípio de "um faz, outro confere" do desenvolvedor e do testador.
3. Revisão de plano **bloqueante** [usuário]: achados Críticos ou Importantes bloqueiam a execução; o orquestrador corrige o plano e o arquiteto revisa de novo, até 2 rodadas; se ainda divergirem, vira entrevista com o usuário. Achados Menores vão como notas do plano.
4. Decisões de arquitetura registradas no repositório (spec ou ADR) e capturadas no brain pelo `brain-escriba` [usuário].

**Não-objetivos**

- Substituir o processo do `superpowers:brainstorming` ou do `/development-roadmap`: a soul define *quem pensa*; as skills continuam definindo *o processo* (inclusive as perguntas abertas do brainstorming na descoberta).
- Escrever o plano das etapas (continua com o orquestrador) ou revisar código (continua com a `revisor-seguranca`).
- Registrar projeto novo no brain (§0 do `/development-roadmap`), que exige editar `.claude/settings.json`: continua numa sessão comum (ver §5).

**Anti-objetivos**

- Uma soul só de "personalidade de arquiteto", sem trava nem papel no fluxo.
- Repetir regras da ARCHITECTURE, dos ADRs ou das skills dentro da soul em vez de apontar para elas.
- Revisão que aprova sem citar o trecho do plano e a decisão de arquitetura que o sustentam.

## 3. Lente (o que o arquiteto prioriza) [usuário]

1. **Limites e contratos:** fronteiras entre módulos, dependências permitidas, contratos públicos (API, eventos, schema).
2. **Irreversíveis primeiro:** migrações, formatos de dados, integrações externas — decidir e validar cedo o que é caro de desfazer.
3. **Não funcionais:** segurança, LGPD, offline e sincronização, desempenho, observabilidade, operação.
4. **Aderência a decisões:** coerência com a ARCHITECTURE, os ADRs e as notas do brain; decisão nova registrada com as alternativas descartadas.

## 4. Implementação: dois arquivos, uma identidade [agente]

No Claude Code cada soul tem um único conjunto de ferramentas e hooks, e os dois usos precisam de travas diferentes. Por isso viram dois arquivos em `99 System/Souls/agents/`:

| Soul | Onde roda | Ferramentas e travas |
|---|---|---|
| `arquiteto` | sessão principal, `claude --agent arquiteto` | Escreve só documentos e diagramas: `.md`, `.mmd`, `.puml`, `.drawio` e o contrato OpenAPI (`api/**/*.yaml`/`.yml`) [usuário]; nunca código nem nada sob `.claude/` ou nas souls (mesma proteção do orquestrador). Bash livre para leitura. Despacha só o `brain-escriba` (`Agent(brain-escriba)`). Usa `Skill` (brainstorming, `/development-roadmap`), `AskUserQuestion`, `WebFetch`/`WebSearch`. Hook novo de papel `arquiteto` no `soul_guard.py`. Commits com `Soul: arquiteto`. |
| `revisor-arquitetura` | subagente do orquestrador | Só leitura, sem Bash [usuário]: `Read`, `Grep`, `Glob`. Hook `soul_guard.py revisor` (bloqueia qualquer Bash, defesa em profundidade). Sempre despachado no modelo mais capaz [usuário]. |

A identidade (quem sou, lente, o que recuso) mora **só** em `arquiteto.md`. O corpo do `revisor-arquitetura` é curto: diz o papel de revisor, o formato do parecer e manda ler `arquiteto.md` (seções da lente e do que recusa) antes de revisar — contexto sob demanda, sem duplicar.

## 5. Fluxos

**Sessão de desenho** (`claude --agent arquiteto`, no repositório):

1. Descoberta e desenho com `superpowers:brainstorming`, gravando o design em `docs/superpowers/specs/`. O arquiteto lê o contexto confirmado do projeto (ARCHITECTURE, ADRs, hub e notas de tema do brain quando o projeto é registrado) antes de propor qualquer coisa.
2. Decisões de arquitetura viram ADR (ou seção da spec, conforme a convenção do projeto) com contexto, decisão, alternativas descartadas e consequências; o arquiteto despacha o `brain-escriba` para capturar a decisão na Inbox.
3. Trabalho grande: `/development-roadmap` gera o roadmap. Pequeno: o design já é suficiente para o orquestrador planejar.
4. O registro de projeto novo no brain (que mexe em `.claude/settings.json`) não é feito nesta sessão: o arquiteto avisa e o usuário roda o `/development-roadmap` numa sessão comum para essa parte, ou registra antes.
5. **Branch e commit [agente]:** a sessão de desenho segue as regras de git do projeto fora de roadmap (no ZenyHotelManager, trabalhar na branch atual e commitar só a pedido do usuário); não cria worktree. Commits levam `Soul: arquiteto`.
6. **Sem plano de etapa [agente]:** quando o `superpowers:brainstorming` encaminhar para `superpowers:writing-plans`, o arquiteto para na spec (ou no roadmap) e diz ao usuário para executar com `claude --agent orquestrador-etapa`, que escreve o plano — o arquiteto nunca escreve o plano que ele mesmo revisaria.
7. **Leitura do brain [agente]:** leitura direta do vault (o caminho vem do bloco *Second Brain* de `~/.claude/CLAUDE.md`; o acesso é dado pela configuração da máquina, e nos projetos registrados o hook injeta o hub). Consultas não passam pelo `brain-escriba`, que só é usado para capturar.

**Revisão de plano** (dentro da execução, para cada etapa):

1. O `orquestrador-etapa` escreve o plano (`superpowers:writing-plans`), como hoje.
2. **Passo novo, em todo plano que o orquestrador executa** [usuário] (com ou sem roadmap, inclusive nos roadmaps cujo protocolo ainda não cita a revisão — a regra vive na soul do orquestrador): despacha o `revisor-arquitetura` (modelo mais capaz) com o plano, a spec ou a seção da etapa, a ARCHITECTURE e os ADRs aplicáveis como arquivos. Projeto sem ARCHITECTURE nem ADRs: o revisor julga contra a spec e as convenções do código e registra a ausência como nota, sem bloquear por isso [usuário].
3. Parecer: achados Críticos/Importantes/Menores, cada um com o trecho do plano e a decisão de arquitetura que o sustenta, e veredito (aprovado / aprovado com notas / bloqueado).
4. Bloqueado: o orquestrador corrige o plano e despacha a re-revisão; até 2 rodadas, cada rodada = uma correção do plano seguida de uma re-revisão, retomando o mesmo revisor (SendMessage) [agente]. Divergência persistente vira pergunta ao usuário na entrevista com opção recomendada, e a etapa espera.
5. Aprovado: o plano ganha a seção **"Revisão de arquitetura"** (veredito, rodadas, modelo usado e as notas Menores) e uma linha no ledger; só então a execução segue pelo ciclo das souls.
6. **Conferência cruzada [usuário]:** na revisão final da etapa, a `revisor-seguranca` confere que o plano tem a seção "Revisão de arquitetura" com veredito aprovado; sem ela, bloqueia. Sem script novo: quem garante é outra soul.

## 6. Mudanças em arquivos existentes

- `orquestrador-etapa.md`: passo de revisão de plano entre "plano" e "execução"; `revisor-arquitetura` no `Agent(...)` e na pré-condição (exigido, como as três souls de desenvolvimento).
- `soul_guard.py`: papel `arquiteto` (escrita só nos tipos da §4, mesma proteção de `.claude/`/souls, mesma regra de worktree nativo; Bash sem restrição de escrita, como o orquestrador; `git push` liberado só com decisão do usuário? — ver §8).
- `check_test_integrity.py`: `arquiteto` e `revisor-arquitetura` em `KNOWN_SOULS`; commit `Soul: arquiteto` que toca algo fora dos tipos da §4 vira apontamento (como `ORQUESTRADOR_CODIGO`).
- `tests/test_souls_files.py`, `tests/smoke_souls.sh`: entradas e casos novos (arquiteto bloqueado ao escrever código; revisor-arquitetura sem Bash).
- `revisor-seguranca.md`: conferência da seção "Revisão de arquitetura" do plano na revisão final (o orquestrador inclui o plano no pacote).
- `development-roadmap`: template (papel "Revisor de plano" na tabela de papéis e na pré-condição) e `check_roadmap.py` (exigir `revisor-arquitetura` no protocolo, como aviso); SKILL.md §7.
- Roadmaps M5–M10 do ZenyHotelManager: protocolo atualizado para incluir a revisão de plano (pedido separado ao usuário depois desta soul pronta, via `/development-roadmap`).
- Documentação: `99 System/Souls/README.md`, `DESIGN.md` (uma linha apontando para este documento) e a nota "Souls" em `20 Knowledge/`.

## 7. Restrições

Iguais às do design das souls: português, corpos ≤ 120 linhas, apontar para as fontes da verdade, nenhuma URL inventada, scripts só com a biblioteca padrão, testes `unittest`, commits só dos arquivos da tarefa, sem push sem pedido.

## 8. Deixado para o construtor

- O texto das duas souls, dentro da anatomia e da lente.
- Lista exata de extensões de diagrama e o padrão do caminho do contrato OpenAPI (o ZenyHotelManager usa `api/openapi.yaml`).
- Se o papel `arquiteto` bloqueia `git push` (recomendação do agente: bloquear, como nos papéis de subagente; o usuário faz push).
- Formato de ADR quando o projeto não tem convenção (sugestão: `docs/adr/NNNN-titulo.md`, contexto/decisão/alternativas/consequências).
- Como o orquestrador empacota os arquivos para o `revisor-arquitetura`.
