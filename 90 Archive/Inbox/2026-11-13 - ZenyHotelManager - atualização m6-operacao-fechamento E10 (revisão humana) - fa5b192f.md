---
type: capture
status: archived
created: 2026-11-13
capture_id: fa5b192f-13a0-4e35-959a-3134613a24d8
---
# ZenyHotelManager - atualização m6-operacao-fechamento E10 (revisão humana)

## Conteúdo capturado

Complemento da captura [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]]. **Vale sobre ela** nos pontos abaixo. Origem das decisões: entrevista do usuário em 2026-11-13, todas pela opção recomendada, registrada no roadmap `docs/roadmaps/roadmap-m6-operacao-fechamento.md` como **H12**, no commit `9e65b3a` da `main` do repositório.

### 1. Decisões do usuário sobre a E10

1. **Contrato do `POST /api/v1/end-of-day/runs`:** continua `201` síncrono, com espera limitada (`zeny.endofday.manual-wait`) e a execução devolvida no estado em que estiver. **Decisão do usuário.** **Substitui** a "decisão revisável" do item 2 da seção 6 da captura da E10.
2. **Unicidade:** uma execução por data (`run_business_date_uk`), com reconciliação na retomada. **Decisão do usuário.** **Substitui** o item 1 da seção 6 da captura da E10.
3. **Problemas transversais:** os quatro encontrados na E10 viram uma **etapa de manutenção do M6**, a acrescentar pelo `arquiteto` ao roadmap antes do gate do M6. **Complementa** a lista de "Pendências transversais" da seção 6 da captura da E10:
   - faixa do `PageCursor.instant` no `shared` (usado sem faixa por 9 consultas de outros módulos);
   - `rollbackOn = ALL_EXCEPTIONS` global;
   - Jackson estrito em campos `format: date`;
   - log do ShedLock com a mensagem do JDBC.
4. **Gatilho automático na E11:** passa a só disparar o motor e voltar (espera curta), sem mudar o pool do agendador do Spring. **Decisão do usuário.** **Substitui** a obrigação "decidir pool ou espera curta" da seção 7 da captura da E10 e o "risco registrado para a E11" da seção 4 (o risco fica resolvido por esta decisão).

### 2. O que continua revisável

Dos itens da seção 6 da captura da E10, só os itens 1 e 2 foram confirmados pelo usuário. Os demais (3 a 7: janela de 24 h, regra do horário devido, `FAILED` só com retomada manual, recálculo ao trocar fuso ou `endOfDayTime`, banco de teste isolado H10) seguem como decisões do orquestrador, sem confirmação, segundo o relato.

### 3. Estado e próximos passos do hub

**Complementa** o Estado e os Próximos passos de `10 Projects/ZenyHotelManager.md` e **substitui** o estado de integração da captura da E10:

- A E10 do M6 foi integrada na `main` pelo merge local `01c6f0e` em 2026-11-13. A `main` local está 48 commits à frente de `origin/main`; o push é do usuário.
- A revisão humana da E10 foi feita nesta entrevista para as decisões de arquitetura.
- Próximos passos, em ordem: push pelo usuário; o `arquiteto` cria a etapa de manutenção do M6 (item 1.3); novo lote do orquestrador começando pela E11.

## Contexto

O orquestrador do lote do roadmap M6 pediu este complemento depois da entrevista de revisão humana da E10, posterior à captura de fechamento da etapa.

## Origem

- Projeto ZenyHotelManager, repositório `/home/caio/repos/ZenyHotelManager`, `docs/roadmaps/roadmap-m6-operacao-fechamento.md` (H12), commit `9e65b3a` na `main`; merge da E10 `01c6f0e`.
- Relato do orquestrador, em 2026-11-13, sobre a entrevista com o usuário.

## Limitações e incertezas

- O escriba não leu o roadmap nem o código; o conteúdo vem do relato do orquestrador e da captura da E10. O curador localiza os trechos exatos a substituir.
- O número de commits à frente de `origin/main` (48) e os hashes seguem o relato e não foram conferidos.

## Possíveis conexões

- [[2026-11-13 - ZenyHotelManager - atualização m6-operacao-fechamento E10 - 1e4f709b]]
- [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 (revisão humana) - 64ce6698]]
- [[ZenyHotelManager]]
- [[ZenyHotelManager - Estado por marco]]
- [[ZenyHotelManager - Eventos e jobs]]
