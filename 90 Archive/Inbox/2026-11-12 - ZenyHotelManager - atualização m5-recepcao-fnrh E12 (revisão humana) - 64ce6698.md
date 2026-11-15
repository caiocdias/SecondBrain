---
type: capture
status: archived
created: 2026-11-12
capture_id: 64ce6698-9d2c-4a1c-b4d0-af930d24bff5
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E12 (revisão humana)

## Conteúdo capturado

Complemento da captura [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 - 2c135bbf]]. **Vale sobre ela** nos pontos abaixo. Origem das decisões: entrevista do usuário no fim do lote, em 2026-11-12, registrada no roadmap `docs/roadmaps/roadmap-m5-recepcao-fnrh.md` ("Decisões do lote E12", itens (e) e (f), e handoff da E12), na `main` do repositório.

### 1. Duas decisões de arquitetura da E12 (decisão do usuário)

Em 2026-11-12 o usuário tomou as duas decisões de arquitetura da E12, ambas pela opção recomendada:

1. **Ordem interna da camada Hospedagem:** a ARCHITECTURE §3.2 passa a registrar `rates` < `reservations` < `frontdesk` como regra da camada. Um módulo pode depender de quem vem antes, nunca do contrário, e as três arestas deixam de ser exceções. A edição fica com o `arquiteto`, sem mudança de código; o `ModularityTest` continua exato. **Complementa** `ZenyHotelManager - Arquitetura e estrutura de módulos`.
2. **Usuário da FNRH na API:** a ARCHITECTURE §12 é corrigida. Na API, o segredo é a senha; o `username` do Serpro continua no `GET`/`PUT /api/v1/fnrh/settings`, que só o Administrador lê, e fica fora da trilha e dos logs. O contrato e o código não mudam, e a edição fica com o `arquiteto`. **Complementa** `ZenyHotelManager - Módulo fnrh` (seção da configuração) e encerra a divergência registrada desde a E16.

### 2. O que substitui na captura da E12 (`2c135bbf`)

**Substitui**, na lista "Decisões de arquitetura que esperam o usuário" das Perguntas abertas: as duas decisões acima passam de pendentes a decididas. As decisões da E12 (a) a (d) (gate versionado, defeito no gate, imagem do mock, WARN e `--stop`) continuam revisáveis.

### 3. Estado e próximos passos do hub

**Complementa** o Estado e os Próximos passos de `10 Projects/ZenyHotelManager.md`: além da sincronização do roadmap do M6, o `arquiteto` aplica na ARCHITECTURE (§3.2 e §12) as duas decisões acima e cria a etapa de manutenção pedida na revisão humana da E11 (rótulos da FNRH na ficha e a descrição de `frontdesk.stays.checkin`).

## Contexto

O orquestrador do lote do roadmap M5 pediu este complemento depois da entrevista de revisão humana do fim do lote, após a captura de fechamento da E12.

## Origem

- Projeto ZenyHotelManager, repositório `/home/caio/repos/ZenyHotelManager`, `docs/roadmaps/roadmap-m5-recepcao-fnrh.md` ("Decisões do lote E12" (e) e (f) e handoff da E12), na `main`.
- Relato do orquestrador, em 2026-11-12, sobre as decisões do usuário.

## Limitações e incertezas

- O escriba não leu o roadmap nem a captura da E12; o conteúdo vem do relato do orquestrador. O curador localiza os trechos exatos a substituir.
- As referências ao Estado e aos Próximos passos do hub seguem o relato e não foram conferidas no texto atual.

## Possíveis conexões

- [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 - 2c135bbf]]
- [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E11 (revisão humana) - cca61b94]]
- [[ZenyHotelManager]]
- [[ZenyHotelManager - Arquitetura e estrutura de módulos]]
- [[ZenyHotelManager - Módulo fnrh]]
