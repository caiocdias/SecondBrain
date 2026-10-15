---
type: project
created: 2026-10-14
aliases:
  - "TCC"
  - "TCC decodificação intracortical"
sources:
  - "[[2026-10-14 - TCC decodificação intracortical - tema, decisões e lacuna - 71c2334c]]"
---
# TCC - Decodificação intracortical de cinemática

## Objetivo

TCC de Engenharia da Computação, de out/2026 a dez/2027 (cerca de 14 meses). Pode continuar num mestrado.

Título de trabalho (v0.2): *Decodificação de cinemática de membro superior a partir de atividade neural intracortical: avaliação comparativa de desempenho e custo computacional entre métodos clássicos e redes neurais profundas*.

Repositório local: `/home/caio/repos/tcc`. Os detalhes completos ficam lá e não foram copiados para o vault:

- `docs/proposta.md` (v0.2)
- `docs/decisoes.md` (D01–D04 e P01–P09)
- `docs/plano-de-leitura.md` (66 itens em 9 blocos, com DOIs; pula fundamentos de ML, já cursados em Sistemas Inteligentes 1, 2 e 3)
- `docs/cronograma.md` (meses relativos)
- `revisao/protocolo.md`

## Estado

Em andamento desde 2026-10-14: repositório estruturado, proposta v0.2, plano de leitura e cronograma criados. Nada está fixado; o usuário ressalvou que o escopo ainda pode mudar.

### Decisões do usuário (2026-10-14)

Tomadas por [[Decidir pendências do usuário por entrevista com opção recomendada|entrevista com opção recomendada]]; as quatro escolhas foram as recomendadas.

- **Eixo central:** fronteira de Pareto entre desempenho (R²) e custo (latência, parâmetros, MACs, memória). Eficiência de dados como análise secundária.
- **Revisão de literatura:** revisão de escopo/estruturada no estilo PRISMA-ScR, de 2015 a 2026, em vez de revisão sistemática PRISMA 2020 completa.
- **Modelos:** um por família — Wiener, Kalman, MLP, GRU, TCN e um Transformer pequeno.
- **Hardware de medição:** CPU do PC e Raspberry Pi 4 ou 5.

### Decisões técnicas provisórias

Padrões propostos pelo agente, a revisar até jan/2027:

- *Threshold crossings* como entrada; velocidade 2D da mão como alvo.
- Janela de 20 ms, variando em {10, 20, 50} ms.
- Divisão cronológica com intervalo de segurança.
- Friedman seguido de Wilcoxon com correção de Holm.
- Optuna com o mesmo número de *trials* por modelo.
- As 6 sessões do NeuroBench, para comparar com resultados publicados.

### Originalidade e lacuna (hipótese em aberto)

Resumo do agente na sessão de 2026-10-14; referências verificadas bibliograficamente por um subagente, conteúdo não lido diretamente salvo indicação:

- A lacuna inicial ("as comparações usam protocolos diferentes") é fraca: Glaser et al. (2020, eNeuro, DOI 10.1523/ENEURO.0506-19.2020) já comparou decodificadores clássicos e RNNs com pré-processamento padronizado.
- NeuroBench (Yik et al., 2025, Nat Commun 16:1545, DOI 10.1038/s41467-025-56739-4) e o IEEE BioCAS 2024 Grand Challenge (DOI 10.21227/bp1f-te92) já medem custo nos dados de O'Doherty et al. (2017, Zenodo, DOI 10.5281/zenodo.583331), como *footprint* e número de operações, com foco em hardware neuromórfico e SNNs.
- Trabalho mais próximo: Hueber et al. (2024, Neuromorphic Computing and Engineering, DOI 10.1088/2634-4386/ad4411), que mede acurácia e latência de decodificadores em tempo real. Ainda não lido; é ele que define o que sobra de originalidade.
- Espaço provável (interpretação do agente, a confirmar pela revisão de escopo): clássicos e quatro famílias de redes convencionais na mesma fronteira de Pareto, com latência medida em CPU embarcada barata, mesmo orçamento de HPO e estatística em várias sessões.

### Notas técnicas registradas na sessão

- O Neural Data Transformer (Ye & Pandarinath, 2021) é um modelo de representação de atividade populacional avaliado também por decodificação, não um decodificador de cinemática ponta a ponta (correção da proposta inicial).
- O MC_RTT do Neural Latents Benchmark (DANDI 000129) vem do mesmo laboratório (Sabes) que os dados de O'Doherty; o MC_Maze está no DANDI 000128.
- Correções bibliográficas: o título do STNDT é "...with a Spatiotemporal Transformer" (singular); o NeuroBench foi publicado em 2025 na Nat Commun, com outro título.

## Próximos passos

- Ler Hueber et al. (2024) para confirmar ou ajustar a lacuna.
- Conduzir a revisão de escopo conforme `revisao/protocolo.md`.
- Revisar as decisões técnicas provisórias até jan/2027.

## Perguntas abertas

- A lacuna se sustenta depois de Hueber et al. (2024) e da revisão de escopo?
- Datas de TCC1 e TCC2 do curso e orientador ainda desconhecidos.
- Trabalhos recentes sobre SNNs e hardware (Mohan et al., 2025; Krausse et al., 2025; Nazeer et al., 2025; Martis et al., 2024) verificados só quanto a título, autores e veículo.

## Conhecimento relacionado

- [[R² offline nem sempre prevê o desempenho de decodificadores em malha fechada]] — principal limitação de uma avaliação offline como a do TCC.
- [[Decidir pendências do usuário por entrevista com opção recomendada]] — método usado nas decisões D01–D04.

## Resultados

## Proveniência

- 2026-10-14 — [[2026-10-14 - TCC decodificação intracortical - tema, decisões e lacuna - 71c2334c]] (capture_id: 71c2334c-9c1d-4a87-b1a6-bc7a2446dcb4): fatos do projeto, decisões do usuário D01–D04, decisões técnicas provisórias e raciocínio do agente sobre originalidade e lacuna. Nota criada a pedido do usuário no processamento da Inbox.
