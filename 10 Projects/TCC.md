---
type: project
created: 2026-11-04
aliases:
  - "TCC de Engenharia da Computação"
sources:
  - "[[2026-11-04 - TCC - definição do tema e orientação-alvo no mestrado - 0aea531e]]"
---
# TCC

## Objetivo

TCC de Engenharia da Computação do Caio, com entrega até nov/2027. Depois de aprovado na disciplina, o trabalho será levado para um mestrado no IC/Unicamp (Instituto de Computação).

Repositório central: cofre Obsidian do TCC em `/home/caio/repos/tcc`, publicado em [github.com/caiocdias/tcc](https://github.com/caiocdias/tcc) (branch `main`). O planejamento detalhado vive lá, não no vault.

## Tema

Decisão de 2026-11-04. Título de trabalho (pode mudar): "Patrulha persistente com múltiplos drones de autonomia limitada sobre terrenos 2,5D: discretização geométrica e algoritmos exatos e heurísticos".

- Problema: k drones com bateria B (margem de segurança de Y%) patrulham continuamente um terreno com relevo e obstáculos prismáticos (2,5D), partindo de bases de recarga com posição dada.
- Sensor em cone, com faixa de altitude de voo [h_min, h_max].
- Objetivo: minimizar o maior intervalo entre visitas a um ponto (latência).
- Espinha dorsal (otimização): formulação inteira exata, mais heurística ou matheurística; como baseline, a política reativa "volta à base mais próxima".
- Diferencial (geometria): visibilidade em terreno (viewshed) e discretização dos pontos de observação.

Fora do escopo do TCC (pauta do mestrado):

- Localização ótima das bases (location-routing).
- 3D completo (túneis, passarelas).
- Altitude x resolução como problema multiobjetivo.

## Orientação-alvo no mestrado

Grupo-alvo: LOCo (Laboratório de Otimização e Combinatória, IC/Unicamp).

- Orientador principal pretendido: Pedro H. D. B. Hokama (roteamento com drones).
- Coorientação pretendida: Pedro J. de Rezende (geometria computacional, galeria de arte exata).
- Alternativas: Fábio Usberti (roteamento em arcos, cobertura) e Lehilton Pedrosa (algoritmos de aproximação; o LOCo teve um seminário sobre cobertura por varredura em 2026).
- Cid de Souza consta como ex-docente do LOCo.
- Hélio Pedrini foi considerado e descartado: o trabalho dele é majoritariamente deep learning, e o Caio prefere teoria e algoritmos a IA e redes neurais.

As informações sobre docentes vieram da sessão de origem e não foram verificadas nas páginas do LOCo ou de outras instituições.

## Preferências de pesquisa do Caio

Relato da sessão de origem, revelado na escolha do tema:

- Afinidade com geometria computacional e computação gráfica.
- Prefere teoria e algoritmos a problemas práticos de medição.
- Quer evitar a área de IA, que considera saturada.
- Tem também base em sistemas distribuídos e orientação a objetos.

## Estado

- Tema e escopo definidos em 2026-11-04; orientação-alvo escolhida, sem contato registrado com os docentes.

## Próximos passos

- Montar um plano de estudo da fundamentação teórica de 2026-11-09 a 2027-03-28, com lista de leitura datada, no repositório do TCC (pasta `01 Planejamento/`).

## Perguntas abertas

- Vínculo atual de Pedro H. D. B. Hokama com o IC/Unicamp: o LOCo o lista como docente, mas outras fontes o ligam à UFSCar ou à UNIFEI.
- Título definitivo do tema.

## Conhecimento relacionado

Temas ainda sem nota no vault: patrulha persistente com drones, visibilidade em terreno (viewshed), problema da galeria de arte, location-routing, roteamento de veículos com restrição de autonomia.

## Proveniência

- 2026-11-04 — [[2026-11-04 - TCC - definição do tema e orientação-alvo no mestrado - 0aea531e]] (capture_id: 0aea531e-9018-4bf3-b469-0d80f3aa5011): tema, escopo, orientação-alvo, preferências de pesquisa e próximo passo; nota de projeto criada a pedido do usuário no processamento.
