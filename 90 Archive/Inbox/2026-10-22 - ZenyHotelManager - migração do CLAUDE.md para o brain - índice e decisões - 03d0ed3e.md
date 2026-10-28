---
type: capture
status: archived
created: 2026-10-22
capture_id: 03d0ed3e-788d-43f3-b338-79e3077d799f
---
# ZenyHotelManager - migração do CLAUDE.md para o brain - índice e decisões

## Conteúdo capturado

### Pedido do usuário (citação literal, 2026-10-22)

"vamos liberar o claude.md deste projeto que esta grande, ele deve ser enxuto e guardar apenas o que for estritamente necessário que fique na raiz do projeto. vamos criar um projeto no /second-brain e passar as demais informações para lá. lá tudo que é necessário saber e ser acessado pelos agentes no futuro vai estar de forma estruturada, o claude.md da raiz vai instruir e exigir um hook que obrigue a sessão a ler o brain. pode usar quantos inbox forem necessários. qualquer duvida me entreviste conforme o brain"

### Decisões do usuário (entrevista com opção recomendada, 2026-10-22; as quatro escolhas foram as recomendadas)

1. **Ordem em duas fases.** Fase 1 (esta sessão, agente externo): capturas com todo o conteúdo e o hook e o `CLAUDE.md` enxuto preparados, sem ativar; o `CLAUDE.md` atual continua valendo. O usuário processa a Inbox numa sessão do vault. Fase 2 (sessão no repositório): ativar o `CLAUDE.md` enxuto e o hook apontando para a nota de projeto já criada. Assim nunca há um momento sem documentação.
2. **Atualização por capturas.** Cada etapa do roadmap que hoje atualiza o `CLAUDE.md` publica, ao fim, uma captura "ZenyHotelManager - atualização Mx Ey" com o texto novo ou alterado; o hook mostra o hub e lista as capturas pendentes do projeto, que o agente lê; o curador consolida ao processar a Inbox. Respeita o contrato do vault (alternativas descartadas: exceção no AGENTS.md para sessões do projeto editarem as próprias notas; manter a referência técnica no `docs/` do repositório).
3. **`CLAUDE.md` mínimo operacional** (~70 linhas): o projeto, onde ficam SPEC/ARCHITECTURE/roadmaps, idioma (D17), stack, a tabela de comandos oficiais (os roadmaps dizem que estão lá), Docker obrigatório, roadmaps, entrevista de decisões, git e a exigência do brain e do hook. Descartados: "mínimo + invariantes técnicas" e "só o brain".
4. **Uma captura por tema ou módulo** (25, tabela abaixo), cada uma com o texto literal das linhas correspondentes, para facilitar uma nota por tema.

### Capturas desta migração

Todas com o texto literal do `CLAUDE.md` no commit `a6c0f03`. As linhas 1–36, 586–592 e 626–638 (projeto, stack, comandos, roadmaps, decisões do usuário e git) não viraram captura: ficam, adaptadas, no `CLAUDE.md` enxuto. Um script conferiu que toda linha não vazia do arquivo está numa captura ou no que fica.

| Captura | capture_id | Nota sugerida (sugestão do agente) |
|---|---|---|
| [[2026-10-22 - ZenyHotelManager - Estado por marco - 00f871ac]] | `00f871ac-9fce-4291-9d71-47a67a2f69b7` | ZenyHotelManager - Estado por marco |
| [[2026-10-22 - ZenyHotelManager - Ambiente, banco, chaves e build - 2f6c86e6]] | `2f6c86e6-ed13-4195-b090-c2817117526b` | ZenyHotelManager - Ambiente, banco, chaves e build |
| [[2026-10-22 - ZenyHotelManager - Arquitetura e estrutura de módulos - a0fc3031]] | `a0fc3031-9923-4dfc-bfc7-44c8c88a6666` | ZenyHotelManager - Arquitetura e estrutura de módulos |
| [[2026-10-22 - ZenyHotelManager - Schemas e migrações - 877877fd]] | `877877fd-ab36-4aea-ad85-f3f152e7f81a` | ZenyHotelManager - Schemas, migrações e views de relatório |
| [[2026-10-22 - ZenyHotelManager - Tipos do kernel - 8406864a]] | `8406864a-13fc-4012-b915-4be15129ba49` | ZenyHotelManager - Tipos do kernel |
| [[2026-10-22 - ZenyHotelManager - Convenções de API - 3725663b]] | `3725663b-4521-4cf8-b38d-d48c710cbd48` | ZenyHotelManager - Convenções de API |
| [[2026-10-22 - ZenyHotelManager - Tempo real (SSE) - 52209457]] | `52209457-a598-432e-a841-ad4b3ccc8217` | ZenyHotelManager - Tempo real (SSE) |
| [[2026-10-22 - ZenyHotelManager - Sincronização offline - 53f0cae5]] | `53f0cae5-d102-4b44-9999-fba3bedaf95b` | ZenyHotelManager - Sincronização offline |
| [[2026-10-22 - ZenyHotelManager - Segurança, autenticação e autorização - 822ef2ab]] | `822ef2ab-cdc0-4a81-8c89-77c9af576a1f` | ZenyHotelManager - Segurança, autenticação e autorização |
| [[2026-10-22 - ZenyHotelManager - Auditoria - a4fe3210]] | `a4fe3210-4817-4e56-97e8-e9821d0b1ee1` | ZenyHotelManager - Auditoria |
| [[2026-10-22 - ZenyHotelManager - Módulo files (anexos) - 75ac07ef]] | `75ac07ef-246a-4da0-aeb3-478bc2c1412e` | ZenyHotelManager - Módulo files |
| [[2026-10-22 - ZenyHotelManager - Módulos hotel e staff - a0a42caf]] | `a0a42caf-113e-4308-986a-30775093e9cf` | ZenyHotelManager - Módulos hotel e staff |
| [[2026-10-22 - ZenyHotelManager - Módulo rooms - 91217936]] | `91217936-33cb-4729-bf6f-80ca33aa1658` | ZenyHotelManager - Módulo rooms |
| [[2026-10-22 - ZenyHotelManager - Módulo checklists - 7039deec]] | `7039deec-5120-42c1-baa7-0cbe1d8dd0b8` | ZenyHotelManager - Módulo checklists |
| [[2026-10-22 - ZenyHotelManager - Módulo notifications - 29724dad]] | `29724dad-1187-4a9a-8781-f2652c064c0d` | ZenyHotelManager - Módulo notifications |
| [[2026-10-22 - ZenyHotelManager - Módulo guests - e0352073]] | `e0352073-bfe8-4fc4-961a-3739a864fe04` | ZenyHotelManager - Módulo guests |
| [[2026-10-22 - ZenyHotelManager - Módulo billing - contas, roteamento e taxa de serviço - c6398a76]] | `c6398a76-eef1-4a2b-88bc-a7f9befa072c` | ZenyHotelManager - Módulo billing (contas, roteamento e taxa de serviço) |
| [[2026-10-22 - ZenyHotelManager - Módulo billing - caixa, pagamentos, caução e encerramento - 1da9ffd1]] | `1da9ffd1-f4d8-4ea9-8a65-700ce8cd0024` | ZenyHotelManager - Módulo billing (caixa, pagamentos, caução e encerramento) |
| [[2026-10-22 - ZenyHotelManager - Módulo rates - b515343e]] | `b515343e-b6d3-4b7f-9208-1a18564f0e3f` | ZenyHotelManager - Módulo rates |
| [[2026-10-22 - ZenyHotelManager - Módulo reservations - inventário, disponibilidade e reservas - 67a3b905]] | `67a3b905-b8e5-4470-98cd-a9fb4fb6b35c` | ZenyHotelManager - Módulo reservations (inventário, disponibilidade e reservas) |
| [[2026-10-22 - ZenyHotelManager - Módulo reservations - ciclo de vida, garantia, alocação, grupos e busca - 86bbb410]] | `86bbb410-dc7c-4c4a-b84d-e8588ad6592d` | ZenyHotelManager - Módulo reservations (ciclo de vida, alocação, grupos e busca) |
| [[2026-10-22 - ZenyHotelManager - Hospedagem e recepção (frontdesk) - 33c65c3f]] | `33c65c3f-ad04-4474-af45-ede81052e342` | ZenyHotelManager - Hospedagem e recepção |
| [[2026-10-22 - ZenyHotelManager - Docker, observabilidade e CI - ada44296]] | `ada44296-529e-4b1f-9386-ab1e5da05933` | ZenyHotelManager - Docker, observabilidade e CI |
| [[2026-10-22 - ZenyHotelManager - Eventos e jobs - 4e9ffb74]] | `4e9ffb74-b604-4a12-835d-89cb104e68f7` | ZenyHotelManager - Eventos e jobs |
| [[2026-10-22 - ZenyHotelManager - Testes de integração - e6d2c591]] | `e6d2c591-1c43-4288-83b5-6db569703ea7` | ZenyHotelManager - Testes de integração |

### Texto do `CLAUDE.md` sobre o projeto (literal, linhas 7–13, também mantido no `CLAUDE.md` enxuto)

Servidor do Zeny Hotel Manager: PMS e operações de **um único hotel** de até 30 UHs. Este repositório contém **só o servidor**. Os clientes (desktop, mobile, PDV, tela de produção e agente de impressão) ficam em outros repositórios e geram seus SDKs a partir do contrato OpenAPI.

- `docs/SPEC.md` diz **o quê**: requisitos `RF-<MÓDULO>-NN`, regras `RN-NN`, modelo de domínio (§8), fases (§9) e questões em aberto `Q-NN` (§10).
- `docs/ARCHITECTURE.md` diz **como**: decisões D1–D17 (§2), módulos e dependências (§3), convenções de API (§7), segurança (§8), offline (§9), persistência (§11) e integrações (§12).
- `docs/roadmaps/` traz o plano de execução: `README.md` com o mapa dos 11 marcos (M0–M10) e um `roadmap-mN-*.md` por marco.

Documentação, mensagens ao usuário e commits ficam em pt-BR. Código, API e banco ficam em inglês (D17); o glossário da SPEC §4 faz o mapeamento dos termos.

### Estrutura proposta ao curador (sugestão do agente, não decisão do usuário)

- **Hub:** uma nota `type: project` em `10 Projects/` cujo nome contenha `ZenyHotelManager` (ou com `ZenyHotelManager` nos `aliases`): é assim que o hook a encontra. O hook injeta o conteúdo do hub em toda sessão e subagente, e o Claude Code corta o contexto injetado em 10.000 caracteres (o script reserva ~9.500, incluindo a lista de capturas pendentes): **manter o hub abaixo de ~8.000 caracteres**. Conteúdo sugerido: objetivo e escopo (texto acima), repositório local e documentos de lá, estado atual em poucas linhas (marco e etapa correntes; o histórico completo fica na nota "Estado por marco"), um índice das notas de tema com uma linha cada dizendo quando lê-la, o fluxo de atualização por capturas e as perguntas abertas.
- **Notas de tema:** uma por captura acima (títulos sugeridos na tabela), ligadas pelo hub, com `projects` apontando para ele. O `type` é decisão do curador: são referência técnica de um código específico, mais próxima de documentação de projeto do que de conhecimento reutilizável. O texto técnico (caminhos, classes, códigos de erro, nomes de migrações) é usado pelos agentes ao editar o código e deve ser preservado, não resumido.
- **Capturas de atualização futuras:** integradas na nota de tema correspondente (e o estado no hub), com proveniência.

### Hook e fase 2 (preparados no repositório, ainda inativos)

- `.claude/brain/load-brain.py`: lê o vault (`ZENY_BRAIN_VAULT` ou o bloco *Second Brain* de `~/.claude/CLAUDE.md`), acha o hub e as capturas `status: inbox` que citam `ZenyHotelManager`, e devolve `hookSpecificOutput.additionalContext` com a linha `ZENY-BRAIN: carregado`, o caminho do hub, a lista das capturas pendentes e o conteúdo do hub; sem o vault, `ZENY-BRAIN: indisponível` com o motivo. Nunca derruba a sessão.
- `.claude/brain/settings.next.json`: os hooks `SessionStart` (todas as origens, inclusive depois de compactar) e `SubagentStart` (os subagentes não recebem o contexto do `SessionStart`).
- `.claude/brain/CLAUDE.next.md`: o `CLAUDE.md` enxuto, que exige a linha `ZENY-BRAIN: carregado` e manda parar sem ela.
- **Passos da fase 2** (depois de o curador criar o hub): conferir o hub e o tamanho dele; mover `CLAUDE.next.md` para `CLAUDE.md` e mesclar `settings.next.json` em `.claude/settings.json`; trocar, nos roadmaps (`docs/roadmaps/README.md`, item 3 das regras, e os prompts e o protocolo do `roadmap-m5-recepcao-fnrh.md` e dos seguintes), "atualize o CLAUDE.md" por "publique a captura de atualização"; conferir numa sessão nova e num subagente que o contexto traz `ZENY-BRAIN: carregado`. A skill `development-roadmap` (no vault) também cita o registro no CLAUDE.md; mudá-la depende de pedido explícito do usuário.

## Contexto

O `CLAUDE.md` do repositório tinha 638 linhas e ~435 KB, quase tudo referência técnica acumulada pelas etapas M0 E01 a M5 E03, e o protocolo dos roadmaps manda cada etapa atualizá-lo. A sessão que fez esta captura começou no repositório, então é agente externo do vault: só cria capturas. A nota de projeto e as notas de tema dependem do curador.

## Origem

- Projeto ZenyHotelManager, repositório local `/home/caio/repos/ZenyHotelManager`, `CLAUDE.md` no commit `a6c0f03` (branch `main`).
- Conversa com o usuário no Claude Code, sessão iniciada no repositório, 2026-10-22.
- Fatos sobre hooks conferidos por um subagente na documentação do Claude Code (code.claude.com/docs/en/hooks.md, memory.md, sub-agents.md): o `SessionStart` injeta contexto por `additionalContext` e roda também depois de compactar; o `SubagentStart` injeta contexto no subagente; o contexto injetado tem teto de 10.000 caracteres.

## Por que registrar

Orienta o curador a criar o projeto ZenyHotelManager no brain e a integrar as 25 capturas com uma estrutura que o hook consiga carregar, e registra as decisões do usuário sobre o fluxo.

## Limitações e incertezas

- O hook ainda não foi testado numa sessão real nem num subagente (só o script, por linha de comando). Não está confirmado se o teto de 10.000 caracteres também vale para o `SubagentStart`.
- Os títulos e a divisão das notas são sugestões do agente.
- Entre a fase 1 e a fase 2, etapas que rodarem no repositório ainda atualizarão o `CLAUDE.md` antigo; o que mudar nelas precisa entrar no brain antes da fase 2 (o agente da fase 2 compara o `CLAUDE.md` com `a6c0f03` e captura a diferença).
- Os arquivos de `.claude/brain/` estão no repositório sem commit.

## Possíveis conexões

- [[Decidir pendências do usuário por entrevista com opção recomendada]]: método usado na entrevista desta migração.
