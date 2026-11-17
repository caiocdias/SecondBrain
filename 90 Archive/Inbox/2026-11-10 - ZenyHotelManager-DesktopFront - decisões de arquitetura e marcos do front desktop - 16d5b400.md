---
type: capture
status: archived
created: 2026-11-10
capture_id: 16d5b400-b2e5-490e-b063-b61b40c14257
---

# ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop

## Conteúdo capturado

Resumo do agente (escriba), feito a partir do design e dos ADRs do repositório do front. Cada decisão traz quem decidiu, conforme os próprios documentos.

### Objetivo

- Fato: o servidor do Zeny Hotel Manager (PMS de um único hotel, até 30 UHs) expõe 303 operações REST e ainda não tem nenhum cliente. O front desktop atende recepção e gerência e, para a demo, também a governança. É desenvolvido em paralelo ao servidor, que tem outro orquestrador.
- Objetivo: uma **demo em 17/11/2026** (terça, sete dias depois da sessão) para o gerente, que não é de TI e quer ver o máximo possível da aplicação rodando, com cara de produto. Amplitude vale mais que profundidade.
- Na demo, servidor e app rodam juntos na máquina Windows de 64 GB (com Docker Desktop; JDK 25 a instalar pelo usuário). Depois da demo, o front acompanha o servidor conforme ele avança.
- Decisão do usuário: o desktop é o **superconjunto** do mobile (tudo que o mobile faz o desktop também faz). Governança e checklists entram.
- Restrição do usuário: **sem Node**. Desenvolvimento num notebook Linux de 14 GB (JDK 25, Docker 29, sem Node, Rust nem Gradle global). O Windows só roda, nunca desenvolve.
- Não objetivos por ora: modo offline; PDV, tela de produção, agente de impressão e TEF; instalador nativo assinado e atualização automática; compartilhar código com o mobile; funcionalidades que o servidor ainda não tem.
- Anti-objetivos: tela com cara de teste (JSON cru, códigos em inglês, UUID ou `version` à vista); front que quebra quando o servidor faz merge, rebuild ou `down -v`; remendo no repositório do servidor a partir do front; dado pessoal real na demo ou dado de hóspede em log ou cache em disco.

### Decisões F1 a F6

| # | Decisão | Quem decidiu | Alternativas descartadas | ADR |
|---|---|---|---|---|
| F1 | Stack: **Compose Multiplatform Desktop** em Kotlin sobre JDK 25, Gradle pelo wrapper, cliente da API gerado de `api/openapi.yaml` | Usuário, entre 3 opções | Web renderizada no servidor com HTMX (Ktor): segundo servidor para operar, complica TEF e impressão locais. Flutter (Dart): linguagem e SDK novos, cliente OpenAPI menos maduro. Tauri ou web SPA: exigiriam Node ou Rust no build | `docs/adr/0001-stack-compose-desktop.md` |
| F2 | Front **preso a um commit da `main` do servidor**, registrado em `api/server-pin.properties` (`commit`, `contract_sha256`, `synced_at`), com cópia byte a byte do contrato em `api/openapi.yaml`. Trocar o commit só no M0. Pré-voo `tools/server-drift.sh` (só leitura + oasdiff) em toda execução: igual segue; aditivo registra e segue; breaking change em operação usada para e recomenda o M0 | Proposta do arquiteto aprovada pelo usuário | `main` viva do servidor (quebraria a cada merge); submódulo Git (metadados apontando para o servidor, incentiva build pela árvore do servidor); baixar de `/v3/api-docs` de um servidor rodando (depende de servidor no ar e de profile, sem commit de referência) | `docs/adr/0002-servidor-fixado-e-contrato-copiado.md` |
| F3 | **Ambiente do servidor isolado**: `git archive` do commit fixado, projeto compose `-p zeny-front`, porta 8088, volumes próprios, imagem `zeny-hotel-manager:<commit curto>`, pacote para o Windows (`tools/server-env/package.sh`), `save-images.sh`, `up.sh` e `down.sh` | Proposta do arquiteto aprovada pelo usuário (servidor e app juntos no Windows: usuário) | Compose do servidor como está (conflito de nome, porta, imagem e volumes); `git worktree add` no servidor (escreve metadados no `.git` dele); registro de imagens ghcr (exige push, que é do usuário, e credenciais; fica como opção futura) | `docs/adr/0003-ambiente-do-servidor-isolado.md` |
| F4 | **Endereço do servidor configurável** sem rebuild: campo Servidor na tela de login, botão "testar" (`GET /api/v1/meta/version`), salvo nas preferências do usuário do SO. Precedência inicial: valor salvo, `ZENY_SERVER_URL` no ambiente, `ZENY_SERVER_URL` num `.env` ao lado do JAR, `http://localhost:8088` | Usuário pediu "ip no .env"; o campo na tela é chamada do arquiteto | Só o `.env` (abrir arquivo na frente do gerente); URL compilada no build (rebuild a cada mudança de rede); descoberta automática na LAN (custo alto e superfície de rede nova) | `docs/adr/0004-endereco-do-servidor-configuravel.md` |
| F5 | **Pedidos do front ao servidor pelo Second Brain**, com controle local em `docs/pedidos-servidor.md` | Usuário pediu o canal pelo brain; o desenho é do arquiteto | Issue no GitHub do servidor (fora do fluxo das souls, nenhum hook a injeta); arquivo no repositório do servidor escrito pelo front (viola a regra de só ler o servidor); avisar o usuário para repassar à mão (perde rastro e vínculo com etapas) | `docs/adr/0005-pedidos-ao-servidor-pelo-brain.md` |
| F6 | **Marcos por valor de demo**, com a configuração criada pela API por um `demo-seed` idempotente e dados fictícios | Usuário aprovou a ordem; marcos menores com um gate por dia também a pedido do usuário | Seguir as camadas do servidor, cadastros primeiro (a demo mostraria formulários de configuração se o tempo acabasse); um fluxo só, ponta a ponta (o usuário pediu amplitude) | `docs/adr/0006-marcos-por-valor-de-demo.md` |

### Chamadas do arquiteto registradas no design

Decisões do arquiteto (não do usuário), conforme o design:

- **Check-out no M4**, e não na recepção do dia: o check-out do servidor exige saldo zero e contas encerradas, lança as diárias pendentes (hipótese H14 do roadmap do M5 do servidor) e o pagamento só entra com turno de caixa aberto. Sem conta e caixa, o check-out falharia na demo.
- **Imagem do servidor construída no Windows**: o `Dockerfile` do servidor roda `./gradlew bootJar` dentro do Docker e o notebook não tem memória para isso com o orquestrador do servidor rodando. Construir no notebook fica opcional.
- **Pacote com as 4 imagens**: `save-images.sh` grava com `docker save` as imagens `api`, `postgres:18`, `pgsty/minio:…` e a do `proxy`, para o dia da demo não depender de internet.
- **Recriação da demo na manhã de 17/11**: `down -v`, `up -d` e `demo-seed`, porque a data operacional só avança no M6 do servidor e fica presa ao dia de criação do ambiente. Requisitos: `demo-seed` em menos de 2 minutos, também como JAR executável no Windows, e todo roteiro de marco começa pela recriação. Dados criados à mão nos ensaios são descartáveis.
- **O servidor da demo pertence ao desktop**: só o tooling do desktop sobe, popula e recria o ambiente. O app mobile (repositório próprio) aponta para ele, mas não roda seed nem `down -v`.
- **Tokens só em memória**: access e refresh token nunca vão para disco (fechar o app pede novo login). Em disco ficam só o endereço do servidor, o último login e o id do dispositivo; nenhum dado de hóspede em log nem em cache de disco; documento sempre mascarado. Observação do agente: o design lista isto nas regras transversais (§6.2) e o ADR 0004 o cita como consequência; a atribuição "chamada do arquiteto" vem do pedido de quem acionou o escriba, não de um rótulo explícito nesse trecho do design.

### Canal de pedidos front → servidor (F5)

- **Pedido**: captura nova em `00 Inbox/` chamada `ZenyHotelManager - pedido do front PF-NN <título>`, com motivo (tela ou fluxo), operação desejada (método, caminho, campos), etapa do front que espera por ela, commit fixado do contrato e prioridade. Publicada pelo `brain-escriba` ou pelo orquestrador do front no fechamento da etapa que encontrou a lacuna.
- **Controle local**: `docs/pedidos-servidor.md`, tabela `PF-NN | título | estado (aberto/aceito/entregue/recusado) | captura | etapa do front | commit de entrega`. A etapa dependente fica `#bloqueada` até "PF-NN entregue e sincronizado pelo M0".
- **Resposta**: a captura de fechamento da etapa do servidor cita "atende PF-NN"; a análise do M0 do front a encontra, junto com o contrato novo e o oasdiff.
- O hook `load-brain.py` lista o pedido nas sessões do servidor; depois que o curador processa a Inbox, o pedido e a resposta passam a viver numa nota do projeto do servidor.
- Antes de 17/11, nenhuma etapa da demo depende de pedido.

### Marcos e roadmaps

Mapa em `docs/roadmaps/README.md`; cada marco tem `docs/roadmaps/roadmap-mN-<slug>.md`.

| Marco | Nome | Etapas | Roadmap |
|---|---|---|---|
| M0 | Sincronização com o servidor (repete a cada avanço do servidor) | 1 por rodada | `roadmap-m0-sincronizacao.md` |
| M1 | Fundação e mapa de UHs ao vivo | 7 | `roadmap-m1-fundacao.md` |
| M2 | Recepção do dia | 6 | `roadmap-m2-recepcao-do-dia.md` |
| M3 | Reservas | 5 | `roadmap-m3-reservas.md` |
| M4 | Contas, caixa e check-out | 5 | `roadmap-m4-contas-caixa-checkout.md` |
| M5 | Hóspedes e empresas | 5 | `roadmap-m5-hospedes-empresas.md` |
| M6 | Governança e operação | 7 | `roadmap-m6-governanca-operacao.md` |
| M7 | Gestão e cadastros | 11 | `roadmap-m7-gestao-cadastros.md` |

- Cada marco termina numa build testável conectada ao servidor (JAR do app, `demo-seed` e roteiro de demo acumulado em `docs/demo/roteiro-mN.md`), com gate `Revisão humana: sim`; o usuário faz um gate por dia.
- O M0 tem duas partes: análise (`claude --agent arquiteto` com `development-roadmap` em modo atualização) e mecânica (etapa do orquestrador). A M0 E01 cria o mecanismo e vem antes da M1.
- Se 17/11 chegar no meio de um marco, a demo usa a build do último gate concluído. Risco declarado no design: M6 e M7 provavelmente não ficam prontos até 17/11.
- Regras gerais: um marco por vez; pré-voo em toda execução; repositório do servidor só leitura; push e deploy ficam com o usuário (execução commita em `roadmap/<slug>` e faz merge local na `main`).

### Pendências do usuário

1. **Registrar o projeto no brain** como `ZenyHotelManager-DesktopFront` (nome decidido pelo usuário), numa sessão comum (`/development-roadmap`), antes da primeira execução do orquestrador; depois, processar a Inbox no vault para criar o hub.
2. **Trocar o casamento do `load-brain.py` para prefixo do nome de arquivo** (decisão do usuário): na função `pending_captures` de `99 System/Skills/development-roadmap/scripts/load-brain.py`, casar por `<AAAA-MM-DD> - <Projeto> - ` em vez de substring sem diferenciar maiúsculas. Hoje "ZenyHotelManager" contido em "ZenyHotelManager-DesktopFront" faria as capturas do front entrarem nas sessões do servidor e ocuparem o espaço do hub (cortado em 9.500 caracteres).
3. **Regra de pedidos `PF-NN` no servidor**: uma linha no `CLAUDE.md` ou em `docs/roadmaps/README.md` do servidor dizendo que a sincronização de marco considera os pedidos pendentes e que a captura de fechamento cita "atende PF-NN". Edição numa sessão do servidor.
4. **Instalar o JDK 25 no Windows** e liberar a porta 8088 no firewall de lá.
5. Também listado em `docs/roadmaps/README.md`: commitar os documentos na `main` do front, porque o repositório ainda não tem commit e o orquestrador cria o worktree a partir do `HEAD`.

## Contexto

Sessão `claude --agent arquiteto` de 2026-11-10 no repositório novo do front desktop, que começou vazio. O design foi aprovado pelo usuário em 2026-11-10. O servidor de referência citado pelo design é `/home/caio/repos/ZenyHotelManager`, `main` em `ca9f9e2f9808c74c98154f1e8e60381fecbf1b5d` (M5 até a E07).

## Origem

- Projeto: ZenyHotelManager-DesktopFront (front-end desktop do Zeny Hotel Manager), repositório local `/home/caio/repos/ZenyHotelManager-DesktopFront`.
- **Sem commits**: os documentos abaixo existem só na árvore de trabalho, não commitados (em `git status`, `docs/` aparece como não rastreado).
- Documentos-fonte:
  - `docs/superpowers/specs/2026-11-10-front-desktop-design.md` (design aprovado pelo usuário em 2026-11-10)
  - `docs/adr/0001-stack-compose-desktop.md`
  - `docs/adr/0002-servidor-fixado-e-contrato-copiado.md`
  - `docs/adr/0003-ambiente-do-servidor-isolado.md`
  - `docs/adr/0004-endereco-do-servidor-configuravel.md`
  - `docs/adr/0005-pedidos-ao-servidor-pelo-brain.md`
  - `docs/adr/0006-marcos-por-valor-de-demo.md`
  - `docs/roadmaps/README.md` (mapa dos marcos M0 a M7)
- Sessão: `claude --agent arquiteto`, 2026-11-10. Captura publicada pelo escriba a pedido dessa sessão.

## Por que registrar

Guarda as decisões de arquitetura do front desktop, quem tomou cada uma e o canal de pedidos entre front e servidor. Isso serve às sessões futuras do front e do servidor e à criação do hub do projeto.

## Limitações e incertezas

- Os documentos-fonte não estão commitados. Não há hash de commit do front para citar, e o conteúdo pode mudar antes do primeiro commit. Nada foi copiado como anexo; a referência depende dos caminhos locais acima.
- O commit do servidor vem do texto do design; o escriba não o conferiu contra o repositório do servidor.
- Os roadmaps individuais (`roadmap-m0` a `roadmap-m7`) não foram lidos: a lista de marcos e a contagem de etapas vêm do `docs/roadmaps/README.md`.
- O pacote JAR multiplataforma (Linux x64 e Windows x64) é hipótese a confirmar na M1 E01; se falhar, a alternativa é `./gradlew run` num clone no Windows.
- Enquanto a pendência 2 não for feita, o hook atual casa por substring. Como o texto desta captura contém "ZenyHotelManager", ela pode aparecer na lista de pendentes das sessões do servidor.

## Observação para o curador

O projeto ZenyHotelManager-DesktopFront ainda não tem hub. O usuário vai registrá-lo pela skill `development-roadmap` numa sessão comum, e esse registro gera a captura-índice do projeto. Esta captura complementa aquela: ao processar, integre as duas juntas no hub do ZenyHotelManager-DesktopFront.

## Possíveis conexões

- [[ZenyHotelManager]]: nota de projeto do servidor, que é a fonte da verdade do contrato consumido pelo front e o destino dos pedidos PF-NN.
- [[Decidir pendências do usuário por entrevista com opção recomendada]]: metodologia de decidir pendências por entrevista. Interpretação do agente: as decisões F1 a F6 foram tomadas pelo usuário diante de opções e propostas do arquiteto; os documentos não dizem se a metodologia foi aplicada formalmente.
