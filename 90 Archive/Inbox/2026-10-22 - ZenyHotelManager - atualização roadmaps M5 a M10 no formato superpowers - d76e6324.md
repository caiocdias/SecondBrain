---
type: capture
status: archived
created: 2026-10-22
capture_id: d76e6324-2c69-45d7-b242-d274e8c8ac2e
---
# ZenyHotelManager - atualização roadmaps M5 a M10 no formato superpowers

## Conteúdo capturado

Fatos (sessão no repositório, 2026-10-22, depois de o usuário mudar o hook para o `load-brain.py` da skill `development-roadmap` e refazer a skill; pedido literal: "analise os marcos existentes e edit o que precisar para a nova metodologia do brain"):

- **Roadmaps migrados** para o formato da skill `development-roadmap` com o plugin superpowers: `docs/roadmaps/roadmap-m5-recepcao-fnrh.md` a `roadmap-m10-comercial-gestao.md`. Cada um tem agora um "Protocolo de execução" (papéis, branch `roadmap/<slug>`, um plano do `superpowers:writing-plans` por etapa, execução com `superpowers:subagent-driven-development`, bloco "Second Brain", paradas e fim do lote) e um "Prompt de execução" único; as etapas não concluídas perderam o prompt, a estratégia e os passos de implementação, e o que não é óbvio foi para "Notas para o plano". As etapas concluídas (M5 E01 a E03) ficaram como estavam, salvo a linha "Revisão humana". M0 a M4 (concluídos) ficaram no formato antigo. Os seis passam no `check_roadmap.py` sem erro (o M5 só com avisos dos handoffs antigos das etapas concluídas). Slugs: `m5-recepcao-fnrh`, `m6-operacao-fechamento`, `m7-pagamentos-fiscal`, `m8-restaurante-distribuicao`, `m9-suprimentos`, `m10-comercial-gestao`.
- **Decisões do usuário (entrevista com opção recomendada, 2026-10-22):**
  1. migrar M5 a M10 agora (não a recomendada, que deixava M6 a M10 para a sincronização de cada marco);
  2. a execução de roadmap roda na branch `roadmap/<slug>`, com os commits por tarefa do superpowers; merge, PR e push só com a decisão do usuário no fim do lote (`superpowers:finishing-a-development-branch`); fora do roadmap continua valendo "trabalhe na `main`, commit só a pedido" (recomendada). O `CLAUDE.md` (seção Git) e a regra 4 de `docs/roadmaps/README.md` foram ajustados;
  3. as capturas de atualização seguem o padrão da skill: `ZenyHotelManager - atualização <slug> Eyy` (por exemplo, `ZenyHotelManager - atualização m5-recepcao-fnrh E04`), publicadas pelo orquestrador no fechamento de cada etapa que muda algo descrito no brain, inclusive o estado (recomendada). Substitui o "ZenyHotelManager - atualização Mx Ey" da decisão anterior.
- Notas novas que os roadmaps propõem que as capturas futuras criem: `ZenyHotelManager - Módulo fnrh`, `Módulo printing` (M5), `Módulo housekeeping` e as de `maintenance`, `reporting` e `endofday` (M6), `Módulo fiscal` (M7), `Módulo pos` e `Módulo distribution` (M8), `Módulo inventory` e `Módulo linen` (M9) e `Módulo events` (M10).
- Os roadmaps M6 a M10 continuam escritos antes do código: cada um ainda precisa da sincronização com o código antes do primeiro lote (regra 2 de `docs/roadmaps/README.md`). Os agentes da migração apontaram divergências para essa sincronização (por exemplo, M10 E01 pede 409 onde o código usa `422 CASHIER_SHIFT_REQUIRED`; M5 "Contexto confirmado" descreve as APIs de antes da E01; M8 E05 pede erro acima do limite de crédito, que o `billing` não bloqueia), registradas nas "Notas para o plano".

## Contexto

Continua [[2026-10-22 - ZenyHotelManager - atualização migração do CLAUDE.md fase 2 - cad5c5ad]] e o hub [[ZenyHotelManager]].

## Origem

Sessão do Claude Code iniciada no repositório `/home/caio/repos/ZenyHotelManager` (agente externo), 2026-10-22; alterações sem commit em `CLAUDE.md`, `README.md`, `docs/roadmaps/README.md` e nos seis roadmaps.

## Por que registrar

O hub ainda diz "atualização Mx Ey" na seção "Atualização por capturas" e não registra como os roadmaps passaram a ser executados.

## Sugestão do agente para a integração

No hub: trocar o nome das capturas de atualização para `ZenyHotelManager - atualização <slug> Eyy`, dizer que quem publica é o orquestrador do lote, registrar no Estado que M5 a M10 estão no formato superpowers (M5 E04 é a próxima etapa, pelo "Prompt de execução" do roadmap) e a exceção de git da execução de roadmap. Manter o hub abaixo de ~8.000 caracteres.

## Limitações e incertezas

- Nenhum lote foi executado no formato novo ainda.
- As alterações no repositório não têm commit.

## Possíveis conexões

- [[ZenyHotelManager]]
