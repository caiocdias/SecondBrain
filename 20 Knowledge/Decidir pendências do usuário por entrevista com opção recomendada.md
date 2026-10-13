---
type: methodology
status: draft
created: 2026-10-13
aliases:
  - "Entrevista de decisões com opção recomendada"
sources:
  - "[[2026-10-13 - Decisões pendentes em forma de entrevista com opção recomendada - ca8d829f]]"
---
# Decidir pendências do usuário por entrevista com opção recomendada

## Objetivo

Reduzir o esforço do usuário ao decidir pontos em aberto: o agente traz cada decisão como pergunta, já com uma recomendação justificada, e o usuário só confirma ou ajusta.

## Condições de uso

- Qualquer agente de IA, em qualquer projeto, que chegue a pontos cuja decisão cabe ao usuário.
- Exemplos: hipóteses não confirmadas, trade-offs, escolha de versão ou ferramenta, itens de revisão humana.

## Princípios

- Opinião do usuário (declarada em 2026-10-13): decisões que cabem ao usuário devem ser tomadas por meio de uma entrevista, e cada pergunta deve ter uma opção recomendada.
- Pontos em aberto não ficam apenas listados num relatório final; viram perguntas.

## Procedimento

1. Reunir os pontos que dependem de decisão do usuário.
2. Formular cada um como pergunta de múltipla escolha, com poucas opções claras.
3. Marcar uma opção como recomendada e explicar o motivo. O usuário continua podendo responder livremente.
4. No Claude Code, usar a ferramenta de perguntas interativas (AskUserQuestion), com a opção recomendada em primeiro lugar e o rótulo "(Recomendado)".
5. Depois da entrevista, registrar as decisões onde o projeto as documenta.

## Critérios

- Perguntas com poucas opções, claras e mutuamente distinguíveis.
- Toda pergunta tem exatamente uma recomendação, acompanhada de justificativa.

## Exceções

Em aberto (não definido pelo usuário):

- Quantas perguntas cabem no máximo numa entrevista.
- Como tratar decisões urgentes surgidas no meio de uma tarefa.

## Limites

- A preferência foi declarada uma vez, a partir de um caso concreto: o fim de uma execução orquestrada do roadmap M0, etapa E01, no projeto ZenyHotelManager, cujo relatório listou como texto os pontos de revisão humana (pacote base, detekt em versão alpha, aplicação que não encerra sozinha, lacunas de testes).
- A generalização para todos os projetos foi feita pelo agente que registrou a captura, a pedido do usuário ("de uma maneira mais genérica").
- A regra específica daquele projeto está no `CLAUDE.md` do repositório ZenyHotelManager, fora do vault.

## Histórico de revisão

- 2026-10-13 — criada como draft a partir de captura.

## Proveniência

- 2026-10-13 — [[2026-10-13 - Decisões pendentes em forma de entrevista com opção recomendada - ca8d829f]] (capture_id: ca8d829f-fad1-4d7d-8026-4afb40f857f2): preferência de trabalho declarada pelo usuário e procedimento genérico resumido pelo agente, com contexto de origem e lacunas.
