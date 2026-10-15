---
type: knowledge
subtype: claim
status: draft
created: 2026-10-14
aliases:
  - "R2 offline vs malha fechada"
  - "Avaliação offline vs closed-loop em BCI"
projects:
  - "[[TCC - Decodificação intracortical de cinemática]]"
sources:
  - "[[2026-10-14 - TCC decodificação intracortical - tema, decisões e lacuna - 71c2334c]]"
---
# R² offline nem sempre prevê o desempenho de decodificadores em malha fechada

## Ideia central

Em interfaces cérebro-máquina, um decodificador com melhor R² em avaliação offline (sobre dados gravados) não necessariamente tem melhor desempenho em malha fechada, quando o usuário controla o dispositivo em tempo real.

## Explicação

Referência indicada: Koyama et al. (2010), J Comput Neurosci, DOI 10.1007/s10827-009-0196-9.

Resumo do agente na sessão do TCC; o artigo não foi lido diretamente, e a referência foi verificada apenas bibliograficamente.

Interpretação do curador (não verificada na fonte): em malha fechada, o usuário recebe realimentação e adapta sua atividade neural ao decodificador, condição que a avaliação offline não reproduz.

## Limites e implicações

- Comparações offline de decodificadores (por exemplo, benchmarks sobre datasets públicos) devem declarar essa limitação ao interpretar ganhos de R².
- Confirmar o alcance e as condições da afirmação lendo Koyama et al. (2010) antes de usá-la como argumento central.

## Relações

- [[TCC - Decodificação intracortical de cinemática]] — limitação principal da avaliação offline adotada no TCC.

## Proveniência

- 2026-10-14 — [[2026-10-14 - TCC decodificação intracortical - tema, decisões e lacuna - 71c2334c]] (capture_id: 71c2334c-9c1d-4a87-b1a6-bc7a2446dcb4): afirmação e referência registradas pelo agente como principal limitação da avaliação offline; extraída como Knowledge a pedido do usuário.
