---
type: capture
status: archived
created: 2026-11-04
capture_id: 0aea531e-9018-4bf3-b469-0d80f3aa5011
---

# TCC - definição do tema e orientação-alvo no mestrado

## Conteúdo capturado

### Projeto

- TCC de Engenharia da Computação do Caio, com entrega até nov/2027.
- Depois de aprovado na disciplina, o trabalho será levado para um mestrado no IC/Unicamp (Instituto de Computação).
- Repositório central: cofre Obsidian do TCC em `/home/caio/repos/tcc`, publicado em [github.com/caiocdias/tcc](https://github.com/caiocdias/tcc) (branch `main`).

### Decisão: tema (tomada em 2026-11-04)

Título de trabalho: "Patrulha persistente com múltiplos drones de autonomia limitada sobre terrenos 2,5D: discretização geométrica e algoritmos exatos e heurísticos".

- Problema: k drones com bateria B (margem de segurança de Y%) patrulham continuamente um terreno com relevo e obstáculos prismáticos (2,5D), partindo de bases de recarga com posição dada.
- Sensor em cone, com faixa de altitude de voo [h_min, h_max].
- Objetivo: minimizar o maior intervalo entre visitas a um ponto (latência).
- Espinha dorsal (otimização): formulação inteira exata, mais heurística ou matheurística; como baseline, a política reativa "volta à base mais próxima".
- Diferencial (geometria): visibilidade em terreno (viewshed) e discretização dos pontos de observação.

### Decisão: fora do escopo do TCC (pauta do mestrado)

- Localização ótima das bases (location-routing).
- 3D completo (túneis, passarelas).
- Altitude x resolução como problema multiobjetivo.

### Orientação-alvo no mestrado

Grupo-alvo: LOCo (Laboratório de Otimização e Combinatória, IC/Unicamp).

- Orientador principal pretendido: Pedro H. D. B. Hokama (roteamento com drones). Vínculo atual com o IC ainda a confirmar: o LOCo o lista como docente, mas outras fontes o ligam à UFSCar ou à UNIFEI.
- Coorientação pretendida: Pedro J. de Rezende (geometria computacional, galeria de arte exata).
- Alternativas: Fábio Usberti (roteamento em arcos, cobertura) e Lehilton Pedrosa (algoritmos de aproximação; o LOCo teve um seminário sobre cobertura por varredura em 2026).
- Cid de Souza consta como ex-docente do LOCo.
- Hélio Pedrini foi considerado e descartado: o trabalho dele é majoritariamente deep learning, e o Caio prefere teoria e algoritmos a IA e redes neurais.

### Preferências do Caio reveladas na escolha

Relato repassado pela sessão de origem (não é inferência do escriba):

- Afinidade com geometria computacional e computação gráfica.
- Prefere teoria e algoritmos a problemas práticos de medição.
- Quer evitar a área de IA, que considera saturada.
- Tem também base em sistemas distribuídos e orientação a objetos.

### Próximo passo

- Montar um plano de estudo da fundamentação teórica de 2026-11-09 a 2027-03-28, com lista de leitura datada, no repositório do TCC (pasta `01 Planejamento/`).

## Contexto

O tema foi definido numa sessão de trabalho do Claude Code no repositório do TCC (`/home/caio/repos/tcc`), em 2026-11-04. Essa sessão despachou o escriba para registrar a decisão no brain. O conteúdo acima é o que a sessão repassou; o escriba não participou da discussão.

## Origem

- Projeto: TCC de Engenharia da Computação (Caio).
- Repositório local: `/home/caio/repos/tcc`.
- Repositório remoto: [github.com/caiocdias/tcc](https://github.com/caiocdias/tcc), branch `main`.
- Commit: não informado (o diretório local não foi identificado como repositório Git na sessão de origem).
- Referência de conversa: sessão do Claude Code iniciada em `/home/caio/repos/tcc`, 2026-11-04.

## Por que registrar

- É a primeira entrada sobre o TCC e o mestrado no brain. Fixa o tema, o escopo (o que fica para o mestrado) e os orientadores-alvo.
- Registra preferências de pesquisa do Caio que servem para decisões futuras de tema, disciplina e orientação.
- Serve de ponto de partida para uma eventual nota de projeto do TCC.

## Limitações e incertezas

- As informações sobre docentes (lotação, vínculo de Hokama com o IC, condição de ex-docente de Cid de Souza, seminário de 2026 sobre cobertura por varredura no LOCo) vieram da sessão de origem. O escriba não as verificou nem consultou as páginas do LOCo ou de outras instituições.
- O vínculo atual de Pedro H. D. B. Hokama com o IC/Unicamp está explicitamente em aberto.
- O título do tema é de trabalho e pode mudar.
- O planejamento detalhado só existe no repositório do TCC (`/home/caio/repos/tcc`), fora do vault, e não foi copiado.
- Não havia, no vault, nota de projeto "TCC" ou "mestrado Unicamp". A busca foi feita pelos nomes de arquivo em `10 Projects/`, `20 Knowledge/`, `30 Sources/`, `50 Logs/`, `80 Maps/`, `00 Inbox/` e `90 Archive/Inbox/`; o conteúdo das notas não foi pesquisado. Por isso a captura não tem link de projeto.

## Possíveis conexões

Temas sem nota no vault (texto simples): projeto TCC, mestrado no IC/Unicamp, patrulha persistente com drones, visibilidade em terreno (viewshed), problema da galeria de arte, location-routing, roteamento de veículos com restrição de autonomia.
