---
type: capture
status: archived
created: 2026-11-11
capture_id: 65d0d4ff-bc24-4f40-94ba-c062bdf2b9c1
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E08 (revisão humana)

## Conteúdo capturado

Complemento da captura [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]]. **Vale sobre ela** nos pontos abaixo. Origem das decisões: entrevista do usuário no fim do lote, em 2026-11-11, registrada no roadmap da branch `roadmap/m5-recepcao-fnrh` (commit `2185e41`).

### 1. Revisão humana da E08 feita (decisão do usuário)

**Decisão do usuário:** a revisão humana da E08 foi feita. O usuário aprovou o padrão de envio assíncrono como **padrão para M7 e M8**: uma submissão por evento, ordem causal por reserva, escrita em curso e conciliação antes de repetir, 8 tentativas, e `FAILED`/`INVALID` segurando a fila até `retry` ou `dismiss`. As decisões (a) a (n) do lote E08 **seguem revisáveis uma a uma**.

- **Substitui**, na captura anterior (seção 6) e, quando o curador integrar, em `ZenyHotelManager - Estado por marco` (subseção "M5 E08") e no Estado do hub `10 Projects/ZenyHotelManager.md`, o item "Revisão humana pendente: E13, E07 e E08" e o trecho "O lote parou na da E08": a revisão humana pendente agora é **só E13 e E07**. Na "Perguntas abertas" do hub, a frase "mais a revisão humana de E13, E07 e E08" passa a "mais a revisão humana de E13 e E07, que o gate M8 E13 exige". As decisões (a) a (n) da E08 continuam na lista de decisões sem confirmação individual, pois o aval foi ao padrão, e elas seguem revisáveis.
- **Substitui**, no "Próximos passos" do hub (texto da seção 6 da captura anterior), "Revisão humana da E08 (e das pendentes E13 e E07)" por "Revisão humana das pendentes E13 e E07".
- **Complementa** `ZenyHotelManager - Módulo fnrh` (seção "Envio assíncrono (M5 E08)") e `ZenyHotelManager - Eventos e jobs` (subseção "Primeiros consumidores…" e a regra "Envio assíncrono por pedido" da ARCHITECTURE §12): o padrão é aprovado pelo usuário e é **a referência para os envios assíncronos de M7 e M8**.

### 2. E15 (h) decidida (decisão do usuário)

**Decisão do usuário:** numa etapa de manutenção do `guests`, o corpo completo das respostas de `restrict`, `lift-restriction` e `merge` passa a exigir `guests.profiles.read`; sem essa permissão, a resposta traz um corpo mínimo. A etapa **ainda não existe em roadmap**; cabe ao `claude --agent arquiteto` criá-la.

- **Complementa** `ZenyHotelManager - Módulo guests` (seções de restrição, levantamento de restrição e mesclagem de perfis; e a lacuna de leitura nas escritas do `guests` registrada pela captura da E15) e `ZenyHotelManager - Segurança, autenticação e autorização` (regras de leitura de `guests.profiles.read`): decisão **pendente de implementação**, não vale ainda no código.
- **Substitui**, em "Perguntas abertas" do hub (e na lista de decisões sem confirmação da seção 6 da captura anterior), a sigla "E15 ((a) a (h))" por "E15 ((a) a (g))": a E15 (h) saiu da lista porque o usuário a decidiu. Em `ZenyHotelManager - Estado por marco`, a E15 (h) deixa de ser decisão sem confirmação.

## Contexto

O orquestrador do lote do roadmap M5 pediu este complemento depois da entrevista de revisão humana do fim do lote, após a captura de fechamento da E08.

## Origem

- Projeto ZenyHotelManager, branch `roadmap/m5-recepcao-fnrh`, commit `2185e41` ("Registra a revisão humana da E08 e a decisão da E15 (h) no roadmap do M5").
- Arquivo `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m5-recepcao-fnrh/docs/roadmaps/roadmap-m5-recepcao-fnrh.md`.
- Relato do orquestrador, em 2026-11-11, sobre as decisões do usuário.

## Limitações e incertezas

- O escriba não leu o roadmap nem o commit `2185e41`; o conteúdo vem do pedido do orquestrador. A única leitura foi da captura anterior.
- Não conferi o texto atual das notas de tema `guests` e Segurança; os pontos de "complementa" indicam a seção provável, e o curador localiza o trecho exato.
- A frase "E15 ((a) a (g))" supõe que as demais decisões (a) a (g) da E15 seguem sem confirmação, como na captura anterior.
- O caminho do worktree é local e pode desaparecer após a integração; o hash do commit continua valendo.

## Possíveis conexões

- [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E08 - 8df87866]]
- [[ZenyHotelManager]]
- [[ZenyHotelManager - Estado por marco]]
- [[ZenyHotelManager - Módulo fnrh]]
- [[ZenyHotelManager - Eventos e jobs]]
- [[ZenyHotelManager - Módulo guests]]
- [[ZenyHotelManager - Segurança, autenticação e autorização]]
