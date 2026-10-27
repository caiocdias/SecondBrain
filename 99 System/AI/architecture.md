# Arquitetura

Documento principal sobre a finalidade das pastas, as entidades do vault, os princípios de organização e a separação entre agente externo e curador. Ponto de entrada: [[AGENTS]].

## Princípios

- A nota e suas relações são a unidade de organização intelectual.
- Pastas representam função operacional, não tema.
- Properties representam atributos estruturados.
- Links representam relações semânticas.
- Maps representam curadoria intelectual.
- Bases representam consultas e visualizações.

O vault deve continuar compreensível fora do Obsidian e utilizável sem IA ou plugins comunitários. O conteúdo se adapta à arquitetura aprovada; mudanças na arquitetura dependem de decisão explícita do usuário ([[99 System/AI/mutation-policy]]).

## Pastas

| Pasta | Função |
|---|---|
| `00 Inbox/` | Fila única de capturas pendentes e seus anexos. A origem é registrada dentro de cada captura, nunca por subpasta. |
| `10 Projects/` | Projetos reais com objetivo concreto, criados somente quando o usuário solicita. |
| `20 Knowledge/` | Knowledge Notes e metodologias (`type: methodology`). |
| `30 Sources/` | Registros de origens consultáveis. |
| `30 Sources/Attachments/` | Arquivos de referência permanentes integrados pelo curador. |
| `50 Logs/` | Registros temporais: notas diárias, lotes de processamento, manutenção e decisões. |
| `80 Maps/` | Maps que explicam relações entre notas existentes. |
| `90 Archive/` | Preservação histórica de notas que saíram de uso ativo. |
| `90 Archive/Inbox/` | Capturas processadas, com os anexos exclusivamente históricos. |
| `99 System/` | Documentação do sistema; não é conhecimento pessoal. |
| `99 System/AI/` | Protocolos normativos para agentes. |
| `99 System/Templates/` | Modelos de preenchimento; excluídos de buscas de conteúdo e do processamento. |
| `99 System/Bases/` | Consultas recomendadas e futuras visualizações do recurso Bases. |
| `99 System/Skills/` | Repositório oficial das skills pessoais do Claude Code, ligadas a `~/.claude/skills/`; excluídas de buscas de conteúdo e do processamento. Ver [[99 System/Skills/README]]. |
| `99 System/Souls/` | Repositório oficial das souls (subagentes especialistas do Claude Code), ligadas a `~/.claude/agents/second-brain-souls`; excluídas de buscas de conteúdo e do processamento. Ver [[99 System/Souls/README]]. |

Na raiz ficam `AGENTS.md` (contrato) e `CLAUDE.md` (ponto de entrada do Claude Code, que apenas importa o contrato).

Não criar subpastas por tema, disciplina, mídia ou projeto. Novas pastas ou subpastas são mudança estrutural e exigem decisão explícita. Arquivos `.gitkeep` apenas permitem ao Git representar pastas vazias e são ignorados pelas rotinas.

## Entidades

| Entidade | `type` | Local | Descrição |
|---|---|---|---|
| Capture | `capture` | `00 Inbox/` → `90 Archive/Inbox/` | Registro ainda não integrado; pode conter uma ideia própria, referência externa, experiência ou contexto de projeto. |
| Source | `source` | `30 Sources/` | Registro de uma origem consultável, com contexto e referência verificável. |
| Knowledge | `knowledge` | `20 Knowledge/` | Compreensão, afirmação, modelo, pergunta ou síntese reutilizável. |
| Methodology | `methodology` | `20 Knowledge/` | Procedimento ou critério pessoal para orientar trabalho futuro. Torna-se orientação `canonical` somente com aprovação explícita do usuário. |
| Project | `project` | `10 Projects/` | Objetivo concreto; criado somente quando houver um projeto real solicitado. |
| Log | `log` | `50 Logs/` | Registro temporal de trabalho, processamento ou decisões. |
| Map | `map` | `80 Maps/` | Curadoria que explica relações entre notas existentes; não é uma simples listagem. |
| Archive | mantém o `type` original | `90 Archive/` | Preservação de registros históricos e capturas concluídas, com `status: archived` quando útil. |

Inbox e Archive são localizações e estados, não tipos. Valores e campos estão em [[99 System/AI/schemas]].

### Distinções

- **Captura e integração**: capturar é registrar com a menor estrutura suficiente; integrar é avaliar, deduplicar, decidir o destino e conectar. Só o curador integra.
- **Source e Knowledge**: a Source descreve uma origem e o que ela diz; a Knowledge expressa uma compreensão reutilizável, que pode se apoiar em várias Sources ou em experiência própria.
- **Knowledge e Methodology**: a Knowledge descreve ou explica; a Methodology orienta como agir.
- **Projeto externo e Project**: um projeto em que um agente externo trabalha não precisa ter nota em `10 Projects/`; basta registrar seu nome e referência na captura.
- **Nota diária e captura**: registros feitos no Daily (`type: log`) não precisam gerar capturas separadas sem uma finalidade concreta de integração.

### Da captura ao destino

Uma captura, inclusive de contexto de projeto, pode originar uma Source, uma Knowledge Note, uma metodologia em elaboração, uma atualização de projeto ou apenas um registro histórico, isoladamente ou em combinação. Nenhum destino é automático: o curador decide conforme [[99 System/AI/processing]].

## Papéis

O curador é um papel operacional definido por estes documentos. Não há serviço, processo em segundo plano ou agendamento. A única automação instalada é a sincronização de skills nos hooks de sessão do Claude Code ([[99 System/AI/setup]]), que não toca no conteúdo das notas.

- **Agente externo**: sessão cujo diretório principal está fora do vault. Trabalha em outro projeto, consulta conhecimento pertinente e publica novas capturas em `00 Inbox/`. Contrato: [[99 System/AI/external-agents]].
- **Curador**: sessão iniciada na raiz do vault ou em um diretório interno. Segue o protocolo do vault e executa as tarefas de processamento, integração e manutenção solicitadas pelo usuário.
- **Usuário**: pode editar o vault manualmente e criar notas permanentes diretamente, sem passar pela Inbox. Os protocolos orientam agentes; para o usuário, são convenções recomendadas.

O diretório principal da sessão determina o papel; executar `cd` para dentro do vault em um comando de shell não transforma um agente externo em curador.

### Inbox única

Todo material novo capturado por um agente, externo ou curador, entra primeiro na mesma `00 Inbox/`. A distinção entre origens (projeto, conversa, leitura, experiência) pertence ao conteúdo de cada captura, não à hierarquia de pastas.

### Sessão dedicada para integração

A integração de capturas acontece somente em uma sessão dedicada ao vault. Pedidos de processamento feitos em uma sessão externa são encaminhados para essa sessão.

A configuração de diretórios adicionais concede acesso aos arquivos do vault. A separação entre papéis é uma regra operacional; ela não constitui, por si só, isolamento técnico de escrita.
