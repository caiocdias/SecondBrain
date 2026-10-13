---
type: capture
status: archived
created: 2026-10-13
capture_id: ca8d829f-fad1-4d7d-8026-4afb40f857f2
---

# Decisões pendentes em forma de entrevista com opção recomendada

## Conteúdo capturado

Opinião do usuário (preferência declarada em 2026-10-13, em pt-BR): sempre que um agente chegar a pontos que cabem ao usuário decidir, ele quer decidir por meio de uma entrevista, e cada pergunta deve ter uma opção recomendada.

Resumo do agente, em forma genérica e válida para qualquer projeto:

- Se um trabalho termina com pontos em aberto para o usuário decidir, o agente não deve apenas listá-los num relatório. Ele conduz uma entrevista: hipóteses não confirmadas, trade-offs, escolhas de versão ou ferramenta, itens de revisão humana etc.
- Cada pergunta é de múltipla escolha, com poucas opções claras. Uma delas vem marcada como recomendada, junto com o motivo. O usuário continua podendo responder livremente.
- No Claude Code, isso é feito com a ferramenta de perguntas interativas (AskUserQuestion), pondo a opção recomendada em primeiro lugar e com o rótulo "(Recomendado)".
- Depois da entrevista, o agente registra as decisões tomadas onde o projeto as documenta.

## Contexto

Surgiu no projeto Zeny Hotel Manager, ao fim de uma execução orquestrada do roadmap M0, etapa E01. O relatório final listou como texto os pontos para a revisão humana: confirmar o pacote base, usar o detekt em versão alpha, a aplicação não encerrar sozinha e lacunas de testes. O usuário pediu que pontos assim passem a ser decididos por entrevista.

## Origem

- Projeto: ZenyHotelManager (`/home/caio/repos/ZenyHotelManager`), sessão do Claude Code em 2026-10-13.
- A regra específica do projeto foi registrada no `CLAUDE.md` do repositório.

## Por que registrar

É uma preferência de trabalho que vale para qualquer agente e qualquer projeto. Reduz o esforço de decidir, porque o agente traz a recomendação pronta e o usuário só confirma ou ajusta.

## Limitações e incertezas

- A preferência foi declarada uma vez, a partir de um caso concreto. A generalização para todos os projetos é do agente, a pedido do usuário ("de uma maneira mais genérica").
- Não foi definido quantas perguntas no máximo cabem numa entrevista nem como tratar decisões urgentes no meio de uma tarefa.

## Possíveis conexões

Preferências de trabalho com agentes de IA; revisão humana em fluxos automatizados.
