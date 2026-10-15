---
type: capture
status: archived
created: 2026-10-14
capture_id: 71c2334c-9c1d-4a87-b1a6-bc7a2446dcb4
---

# TCC — decodificação intracortical de cinemática: tema, decisões e lacuna

## Conteúdo capturado

**Fatos do projeto:**

- TCC de Engenharia da Computação do usuário, de out/2026 a dez/2027 (cerca de 14 meses).
- Repositório local: `/home/caio/repos/tcc`.
- Título de trabalho (v0.2): *Decodificação de cinemática de membro superior a partir de atividade neural intracortical: avaliação comparativa de desempenho e custo computacional entre métodos clássicos e redes neurais profundas*.
- O usuário já cursou Sistemas Inteligentes 1, 2 e 3, então o plano de leitura pula os fundamentos de ML.

**Decisões do usuário em 2026-10-14**, tomadas por entrevista com opção recomendada; as quatro escolhas foram as recomendadas:

- **Eixo central:** fronteira de Pareto entre desempenho (R²) e custo (latência, parâmetros, MACs, memória). A eficiência de dados entra como análise secundária.
- **Revisão de literatura:** revisão de escopo/estruturada no estilo PRISMA-ScR, de 2015 a 2026, em vez de uma revisão sistemática PRISMA 2020 completa.
- **Modelos:** um por família — Wiener, Kalman, MLP, GRU, TCN e um Transformer pequeno.
- **Hardware de medição:** CPU do PC e Raspberry Pi 4 ou 5.

**Resumo do agente (amadurecimento da ideia):**

- A lacuna da proposta inicial ("as comparações usam protocolos diferentes") é fraca. Glaser et al. (2020, eNeuro, DOI 10.1523/ENEURO.0506-19.2020) já comparou decodificadores clássicos e RNNs com pré-processamento padronizado.
- O NeuroBench (Yik et al., 2025, Nat Commun 16:1545, DOI 10.1038/s41467-025-56739-4) e o IEEE BioCAS 2024 Grand Challenge (DOI 10.21227/bp1f-te92) já medem custo nos dados do O'Doherty et al. (2017, Zenodo, DOI 10.5281/zenodo.583331). Esse custo é medido como *footprint* e número de operações, com foco em hardware neuromórfico e SNNs.
- O trabalho mais próximo encontrado é Hueber et al. (2024, Neuromorphic Computing and Engineering, DOI 10.1088/2634-4386/ad4411), que mede a acurácia e a latência de decodificadores em tempo real. Ainda não foi lido. É ele que define o que sobra de originalidade.
- O espaço provável do TCC é colocar clássicos e quatro famílias de redes convencionais na mesma fronteira de Pareto, com latência medida em CPU embarcada barata, mesmo orçamento de HPO e estatística em várias sessões. A revisão de escopo precisa confirmar isso.
- Erro corrigido em relação à proposta inicial: o Neural Data Transformer (Ye & Pandarinath, 2021) é um modelo de representação de atividade populacional avaliado também por decodificação, e não um decodificador de cinemática ponta a ponta.
- O dataset MC_RTT do Neural Latents Benchmark (DANDI 000129) vem do mesmo laboratório (Sabes) que os dados do O'Doherty. O MC_Maze está no DANDI 000128.
- A principal limitação da avaliação offline: o R² offline nem sempre prevê o desempenho em malha fechada (Koyama et al., 2010, J Comput Neurosci, DOI 10.1007/s10827-009-0196-9).

**Decisões técnicas provisórias** (padrões do agente, a revisar até jan/2027):

- *Threshold crossings* como entrada.
- Velocidade 2D da mão como alvo.
- Janela de 20 ms, variando em {10, 20, 50} ms.
- Divisão cronológica com intervalo de segurança.
- Friedman seguido de Wilcoxon com correção de Holm.
- Optuna com o mesmo número de *trials* por modelo.
- As 6 sessões do NeuroBench, para comparar com resultados publicados.

## Contexto

A sessão do Claude Code em `/home/caio/repos/tcc` foi iniciada com um pré-projeto (v0.1) gerado numa sessão anterior de brainstorming. O usuário pediu para estruturar o repositório, criar um plano de leitura de 14 meses, amadurecer a ideia e salvar no brain o que fosse útil, ressalvando que nada está fixado.

## Origem

- Projeto: TCC, `/home/caio/repos/tcc`. Sessão do Claude Code em 2026-10-14.
- Arquivos do projeto com os detalhes:
  - `docs/proposta.md` (v0.2)
  - `docs/decisoes.md` (D01–D04 e P01–P09)
  - `docs/plano-de-leitura.md` (66 itens em 9 blocos, com DOIs)
  - `docs/cronograma.md`
  - `revisao/protocolo.md`
- As referências foram verificadas por um subagente em 2026-10-14, consultando o Crossref, o arXiv, o Zenodo, o DANDI e as páginas dos veículos. Duas correções: o título do STNDT é "...with a Spatiotemporal Transformer" (singular), e o NeuroBench foi publicado em 2025 na Nat Commun, com outro título.

## Por que registrar

É o projeto acadêmico principal do usuário até dez/2027 e pode continuar num mestrado. O raciocínio sobre a originalidade (o que já existe e onde está a lacuna) e as decisões de escopo ajudam em sessões futuras, na conversa com o orientador e na escrita da justificativa.

## Limitações e incertezas

- A lacuna ainda não foi confirmada: depende da leitura de Hueber et al. (2024) e da revisão de escopo.
- Os trabalhos recentes sobre SNNs e hardware (Mohan et al., 2025; Krausse et al., 2025; Nazeer et al., 2025; Martis et al., 2024) foram verificados só quanto a título, autores e veículo.
- As datas de TCC1 e TCC2 do curso e o orientador ainda não são conhecidos. O cronograma usa meses relativos.
- O plano de leitura e o protocolo completos ficam só no repositório local; não foram copiados para o vault.

## Possíveis conexões

- [[Decidir pendências do usuário por entrevista com opção recomendada]] — o método foi usado para as decisões D01–D04.
- Temas sem nota no vault: interfaces cérebro-máquina, decodificação neural, benchmark de ML, revisão de escopo (PRISMA-ScR), medição de latência em embarcados.
