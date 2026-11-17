---
type: knowledge
status: processed
created: 2026-11-17
projects:
  - "[[ZenyHotelManager-DesktopFront]]"
sources:
  - "[[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]]"
  - "[[2026-11-13 - ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão - 677b277a]]"
  - "[[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]]"
---
# ZenyHotelManager-DesktopFront - Arquitetura e decisões (ADRs 0001 a 0010)

Referência técnica do projeto [[ZenyHotelManager-DesktopFront]]: objetivo e restrições, decisões F1 a F6 (ADRs 0001 a 0006), chamadas do arquiteto e os ADRs 0007 a 0010. Os ADRs 0011 e 0012 tratam do processo de execução e estão em [[ZenyHotelManager-DesktopFront - Processo de execução (ADRs 0011 e 0012)]]. Leia antes de mexer em stack, contrato, ambiente do servidor, PDF e impressão ou em respostas `oneOf`.

Texto das capturas do `brain-escriba` (resumos do agente feitos a partir dos documentos do repositório), integrado sem resumo nem reescrita; cada bloco indica a captura de origem. A fonte da verdade são os arquivos do repositório `/home/caio/repos/ZenyHotelManager-DesktopFront`. As notas do curador estão marcadas como tal.

## Objetivo, restrições e não objetivos (2026-11-10)

Origem: [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]].

- Fato: o servidor do Zeny Hotel Manager (PMS de um único hotel, até 30 UHs) expõe 303 operações REST e ainda não tem nenhum cliente. O front desktop atende recepção e gerência e, para a demo, também a governança. É desenvolvido em paralelo ao servidor, que tem outro orquestrador.
- Objetivo: uma **demo em 17/11/2026** (terça, sete dias depois da sessão) para o gerente, que não é de TI e quer ver o máximo possível da aplicação rodando, com cara de produto. Amplitude vale mais que profundidade.
- Na demo, servidor e app rodam juntos na máquina Windows de 64 GB (com Docker Desktop; JDK 25 a instalar pelo usuário). Depois da demo, o front acompanha o servidor conforme ele avança.
- Decisão do usuário: o desktop é o **superconjunto** do mobile (tudo que o mobile faz o desktop também faz). Governança e checklists entram.
- Restrição do usuário: **sem Node**. Desenvolvimento num notebook Linux de 14 GB (JDK 25, Docker 29, sem Node, Rust nem Gradle global). O Windows só roda, nunca desenvolve.
- Não objetivos por ora: modo offline; PDV, tela de produção, agente de impressão e TEF; instalador nativo assinado e atualização automática; compartilhar código com o mobile; funcionalidades que o servidor ainda não tem.
- Anti-objetivos: tela com cara de teste (JSON cru, códigos em inglês, UUID ou `version` à vista); front que quebra quando o servidor faz merge, rebuild ou `down -v`; remendo no repositório do servidor a partir do front; dado pessoal real na demo ou dado de hóspede em log ou cache em disco.

## Decisões F1 a F6 (ADRs 0001 a 0006, 2026-11-10)

Origem: [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]]. Cada decisão traz quem decidiu, conforme os próprios documentos.

| # | Decisão | Quem decidiu | Alternativas descartadas | ADR |
|---|---|---|---|---|
| F1 | Stack: **Compose Multiplatform Desktop** em Kotlin sobre JDK 25, Gradle pelo wrapper, cliente da API gerado de `api/openapi.yaml` | Usuário, entre 3 opções | Web renderizada no servidor com HTMX (Ktor): segundo servidor para operar, complica TEF e impressão locais. Flutter (Dart): linguagem e SDK novos, cliente OpenAPI menos maduro. Tauri ou web SPA: exigiriam Node ou Rust no build | `docs/adr/0001-stack-compose-desktop.md` |
| F2 | Front **preso a um commit da `main` do servidor**, registrado em `api/server-pin.properties` (`commit`, `contract_sha256`, `synced_at`), com cópia byte a byte do contrato em `api/openapi.yaml`. Trocar o commit só no M0. Pré-voo `tools/server-drift.sh` (só leitura + oasdiff) em toda execução: igual segue; aditivo registra e segue; breaking change em operação usada para e recomenda o M0 | Proposta do arquiteto aprovada pelo usuário | `main` viva do servidor (quebraria a cada merge); submódulo Git (metadados apontando para o servidor, incentiva build pela árvore do servidor); baixar de `/v3/api-docs` de um servidor rodando (depende de servidor no ar e de profile, sem commit de referência) | `docs/adr/0002-servidor-fixado-e-contrato-copiado.md` |
| F3 | **Ambiente do servidor isolado**: `git archive` do commit fixado, projeto compose `-p zeny-front`, porta 8088, volumes próprios, imagem `zeny-hotel-manager:<commit curto>`, pacote para o Windows (`tools/server-env/package.sh`), `save-images.sh`, `up.sh` e `down.sh` | Proposta do arquiteto aprovada pelo usuário (servidor e app juntos no Windows: usuário) | Compose do servidor como está (conflito de nome, porta, imagem e volumes); `git worktree add` no servidor (escreve metadados no `.git` dele); registro de imagens ghcr (exige push, que é do usuário, e credenciais; fica como opção futura) | `docs/adr/0003-ambiente-do-servidor-isolado.md` |
| F4 | **Endereço do servidor configurável** sem rebuild: campo Servidor na tela de login, botão "testar" (`GET /api/v1/meta/version`), salvo nas preferências do usuário do SO. Precedência inicial: valor salvo, `ZENY_SERVER_URL` no ambiente, `ZENY_SERVER_URL` num `.env` ao lado do JAR, `http://localhost:8088` | Usuário pediu "ip no .env"; o campo na tela é chamada do arquiteto | Só o `.env` (abrir arquivo na frente do gerente); URL compilada no build (rebuild a cada mudança de rede); descoberta automática na LAN (custo alto e superfície de rede nova) | `docs/adr/0004-endereco-do-servidor-configuravel.md` |
| F5 | **Pedidos do front ao servidor pelo Second Brain**, com controle local em `docs/pedidos-servidor.md` | Usuário pediu o canal pelo brain; o desenho é do arquiteto | Issue no GitHub do servidor (fora do fluxo das souls, nenhum hook a injeta); arquivo no repositório do servidor escrito pelo front (viola a regra de só ler o servidor); avisar o usuário para repassar à mão (perde rastro e vínculo com etapas) | `docs/adr/0005-pedidos-ao-servidor-pelo-brain.md` |
| F6 | **Marcos por valor de demo**, com a configuração criada pela API por um `demo-seed` idempotente e dados fictícios | Usuário aprovou a ordem; marcos menores com um gate por dia também a pedido do usuário | Seguir as camadas do servidor, cadastros primeiro (a demo mostraria formulários de configuração se o tempo acabasse); um fluxo só, ponta a ponta (o usuário pediu amplitude) | `docs/adr/0006-marcos-por-valor-de-demo.md` |

## Chamadas do arquiteto registradas no design (2026-11-10)

Origem: [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]].

Decisões do arquiteto (não do usuário), conforme o design:

- **Check-out no M4**, e não na recepção do dia: o check-out do servidor exige saldo zero e contas encerradas, lança as diárias pendentes (hipótese H14 do roadmap do M5 do servidor) e o pagamento só entra com turno de caixa aberto. Sem conta e caixa, o check-out falharia na demo.
- **Imagem do servidor construída no Windows**: o `Dockerfile` do servidor roda `./gradlew bootJar` dentro do Docker e o notebook não tem memória para isso com o orquestrador do servidor rodando. Construir no notebook fica opcional.
- **Pacote com as 4 imagens**: `save-images.sh` grava com `docker save` as imagens `api`, `postgres:18`, `pgsty/minio:…` e a do `proxy`, para o dia da demo não depender de internet.
- **Recriação da demo na manhã de 17/11**: `down -v`, `up -d` e `demo-seed`, porque a data operacional só avança no M6 do servidor e fica presa ao dia de criação do ambiente. Requisitos: `demo-seed` em menos de 2 minutos, também como JAR executável no Windows, e todo roteiro de marco começa pela recriação. Dados criados à mão nos ensaios são descartáveis.
- **O servidor da demo pertence ao desktop**: só o tooling do desktop sobe, popula e recria o ambiente. O app mobile (repositório próprio) aponta para ele, mas não roda seed nem `down -v`.
- **Tokens só em memória**: access e refresh token nunca vão para disco (fechar o app pede novo login). Em disco ficam só o endereço do servidor, o último login e o id do dispositivo; nenhum dado de hóspede em log nem em cache de disco; documento sempre mascarado. Observação do agente: o design lista isto nas regras transversais (§6.2) e o ADR 0004 o cita como consequência; a atribuição "chamada do arquiteto" vem do pedido de quem acionou o escriba, não de um rótulo explícito nesse trecho do design.

## ADRs 0007 e 0008 — gerador do `sdk` e fronteira entre `core` e `sdk`

*Nota do curador (conferência por `git` em 2026-11-17, só leitura):* nenhuma captura traz o texto destes dois ADRs. Na `main` do front (`6ffc9f3`) existem `docs/adr/0007-gerador-do-sdk.md` ("Gerador do `sdk`: ogen com cliente Ktor"; estado: aceita · 2026-11-11 · decidida pelo construtor na M1 E01, na descoberta da Task 3, e confirmada pelo usuário na parada da etapa) e `docs/adr/0008-fronteira-core-sdk.md` ("Fronteira entre `core` e `sdk`"; estado: aceita · 2026-11-11 · opção (b) confirmada pelo usuário na parada da M1 E01, fechando a brecha: `io.ktor.client.*` e `de.quati.ogen.client.*` também passam a ser barrados em `app` e `design`). Só os cabeçalhos foram lidos; consulte os arquivos.

Atualizações de 2026-11-15 nos ADRs 0007 e 0009. Origem: [[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]].

- `docs/adr/0007-gerador-do-sdk.md`: item novo "`oneOf` sem discriminador" (desde `5e06f16d51ff`, o ogen entrega `JsonElement` segundo a ARCHITECTURE §7 do servidor; o `core` escolhe o ramo pelo ADR 0010; a M0 E03 caracteriza o tipo). Linha "Atualização de 2026-11-15" (pendência R4 da M0 E02): desde `57eb5fac5b8a` há um segundo esquema de segurança; nas 5 rotas `/api/v1/print-agents/me/*` o `ogenAuthAttr` é `printAgentToken`. O `core` atual põe o `Bearer` em qualquer `ogenAuthAttr` não vazio; o defeito está caracterizado por teste e registrado na M7 E12, e ninguém chama essas rotas no desktop. A regra correta é tratar como sessão de usuário só `bearerAuth` e falhar fechado em qualquer outro.
- `docs/adr/0009-documentos-pdf-e-impressao.md`: linha "Atualização de 2026-11-15": a M6 E15 do servidor está em `5e06f16d51ff`; a ficha mostra o rótulo do catálogo de domínios da FNRH, e "(código FNRH)" só aparece para código fora do catálogo. Vale a partir da M0 E03.

## ADR 0009 — documentos em PDF e impressão (2026-11-13)

Origem: [[2026-11-13 - ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão - 677b277a]].

Origem: `docs/adr/0009-documentos-pdf-e-impressao.md`. Estado no ADR: "aceita · 2026-11-13 · decidida pelo usuário em entrevista (as três opções recomendadas), na análise da rodada 2 do M0".

Contexto (fatos do contrato do servidor em `57eb5fac5b8a`, conforme o ADR):

- O servidor (M5 E10 e E11 dele) passou a gerar três documentos, cada um com um `GET …/pdf` e um `POST …/print`: ficha de registro (`/reservations/{id}/registration-card`, permissão `frontdesk.stays.checkin`), confirmação da reserva (`/reservations/{id}/confirmation`, `reservations.reservations.read`) e extrato da conta (`/folios/{id}/statement`, `billing.folios.read`).
- O `GET …/pdf` devolve `application/pdf`, sem cache no servidor; a ficha traz dados pessoais dos hóspedes com documentos mascarados.
- O `POST …/print` exige `Idempotency-Key` e uma impressora ativa, devolve `202` e põe o job na fila do servidor. Quem imprime é um agente de impressão em repositório próprio, que ainda não existe e que o design deixa fora do desktop.
- Listar impressoras exige `printing.jobs.read`; cadastrar agentes e impressoras exige `printing.agents.manage` (só Administrador).
- No servidor, o `GET` da ficha não deixa trilha e a impressão deixa (D-E11-10 do servidor).
- Restrição do design §6.2 do front: nenhum dado de hóspede em log nem em cache de disco.

Decisão do usuário (três pontos, todos pela opção recomendada):

1. **Ficha de registro no M2**, como etapa própria (M2 E07), depois do check-in e antes do gate. O visualizador nasce nela e é reaproveitado pela confirmação (M3 E03) e pelo extrato (M4 E02).
2. **Visualizador de PDF em memória**: o app baixa o PDF pelo `core` e renderiza numa janela ou painel do app, com biblioteca de PDF para a JVM (candidata Apache PDFBox; escolha final do construtor, registrada no handoff da M2 E07). Nada vai ao disco, salvo por **"Salvar como…"**, ação explícita do usuário com destino escolhido por ele. Sem arquivo temporário e sem abrir o leitor de PDF do sistema.
3. **Impressão local agora, fila do servidor depois**: "Imprimir" (desde a M2 E07) manda o PDF em memória para uma impressora do SO pelo diálogo de impressão da JVM, sem arquivo e sem trilha no servidor. "Enviar à impressora do hotel" (M7 E12) usa `POST …/print` com impressora ativa, nas três telas de documento, só com permissão efetiva e ao menos uma impressora ativa.

Alternativas descartadas (motivos do ADR):

- Ficha adiada para o M4, junto com o extrato: descartada porque a ficha fecha a história do check-in, que o gerente conhece em papel, e o ADR 0006 favorece amplitude.
- Ficha dentro da M2 E02: daria dois objetivos à etapa do check-in.
- Arquivo temporário aberto no leitor do sistema: abriria exceção ao §6.2 (arquivo pode sobrar no disco; o leitor guarda histórico).
- Só "Salvar como…": pareceria um download na demo.
- Só a fila do servidor: na demo nada sairia no papel, porque não há agente.
- Só a impressão local: deixaria sem tela as rotas `POST …/print` e o modelo de impressão central do servidor, que o mobile também usa.

Consequências registradas no ADR:

- Dependência nova de renderização de PDF; catálogo e lockfiles mudam no mesmo commit.
- Componente de visualização e impressão no módulo `design`; download como fachada do `core` (ADR 0008).
- Dois caminhos de impressão: o local sem trilha no servidor, o da fila com trilha.
- Rótulos de motivo de viagem e meio de transporte da ficha saem como "(código FNRH)" até a M6 E15 do servidor; o front não corrige conteúdo do PDF.
- Rotas `/api/v1/print-agents/me/*` (esquema `printAgentToken`) ficam fora do desktop na cobertura do M7.

## ADR 0010 — resposta que varia com a permissão (2026-11-15)

Origem: [[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]]. A regra do lado do servidor está em [[ZenyHotelManager - Convenções de API]] e em [[ZenyHotelManager - Módulo guests]].

Origem: `docs/adr/0010-resposta-que-varia-com-a-permissao.md` (arquivo novo). Estado no ADR: "aceita · 2026-11-15 · decidida pelo usuário em entrevista (a opção recomendada), na análise da rodada 3 do M0". Relacionadas: ADR 0007 e ADR 0008; design §6.1 e §6.2.

Contexto (fatos do contrato do servidor em `5e06f16d51ff`, conforme o ADR):

- Na M6 E17 do servidor, três escritas do `guests` (`restrictGuest`, `liftGuestRestriction`, `mergeGuests`) passaram a responder `200` com `oneOf: [GuestResponse, GuestWriteSummaryResponse]`. É o primeiro `oneOf` do contrato (não havia nenhum até `57eb5fac5b8a`). O `oasdiff` o classifica como `warning` (`response-body-wrapped-in-one-of-original-preserved`); o pré-voo dá "aditivo" (código 11).
- A regra é do servidor (`docs/ARCHITECTURE.md` §7 dele, linha "Resposta que varia com a permissão", decidida pelo usuário em 2026-11-15): com `guests.profiles.read` vem o perfil inteiro (`GuestResponse`); sem ela, o resumo `GuestWriteSummaryResponse` `{id, restricted}`, sem dado pessoal; a versão vai no `ETag`. O `oneOf` **não tem discriminador**: os ramos são disjuntos pelo `required` (o completo exige `fullName`; o reduzido exige `restricted`, que o completo não tem), sem `additionalProperties: false`. Segundo o servidor, com o ogen 0.16.1 os clientes gerados recebem essas operações como `JsonElement`. A regra vale para as próximas respostas que dependerem da permissão.
- O ADR 0008 não deixa as features usarem o `sdk` cru, e o design §6.2 proíbe JSON cru nas telas: um `JsonElement` não pode chegar ao `app`.

Decisão do usuário (opção recomendada): **quem decodifica é o `core`**. Numa operação cuja resposta é um `oneOf` sem discriminador, a fachada:

1. lê o corpo como o `sdk` o entrega (o `JsonElement`, se a M0 E03 confirmar esse tipo);
2. escolhe o ramo pelas propriedades obrigatórias exclusivas de um ramo (`fullName` presente indica o completo; `restricted` presente sem `fullName` indica o resumo);
3. decodifica o ramo escolhido com o serializer gerado, com o mesmo `Json` do `sdk`;
4. devolve às features um resultado tipado com os dois casos, cada um com o modelo gerado e o `ETag`;
5. falha fechado: nenhum ramo, os dois ramos ou falha de decodificação dão `ApiError.IncompatibleResponse`; sem palpite nem ramo padrão.

Nome do tipo, forma do resultado e local da função genérica de escolha ficam com o construtor da M5 E02 (primeira etapa consumidora).

Alternativas descartadas (motivos do ADR):

- Descartar o corpo e reler por `GET /api/v1/guests/{id}`: chamada a mais, corrida entre escrita e leitura (o `ETag` pode não ser o da escrita) e, sem `guests.profiles.read`, a releitura não serve.
- Entregar o `JsonElement` às features: fere o design §6.2 e o ADR 0008.
- Ajustar o `sdk` gerado ou trocar de gerador para ter tipo-soma: fere o ADR 0007 (sem código à mão no `sdk`; o ogen cumpre os quatro critérios).
- Pedir ao servidor um discriminador (`PF-NN`): o servidor já recusou na ARCHITECTURE §7 dele, porque exigiria propriedade nova no esquema completo de todas as operações da regra.
- Tentar `GuestResponse` e, se falhar, o resumo: funciona hoje, mas depende da ordem e não detecta resposta que case com os dois ramos.

Consequências registradas: `ETag` nos dois ramos (o `If-Match` seguinte funciona igual); a tela trata o resumo como sucesso sem perfil; a M0 E03 caracteriza por teste no `sdk` o tipo gerado, sem mudar o `core` (se não for `JsonElement`, ajusta-se o passo 1; se o ogen não gerar ou não compilar, a M0 E03 para, por ser decisão de arquitetura, ADR 0007 critério 1); a M5 E02 é a primeira a usar a regra; cada rodada do M0 passa a procurar `oneOf` novo no contrato e apontar a etapa consumidora.

## Limitações registradas nas capturas

Da captura de 2026-11-10:

- Os documentos-fonte não estão commitados. Não há hash de commit do front para citar, e o conteúdo pode mudar antes do primeiro commit. Nada foi copiado como anexo; a referência depende dos caminhos locais acima.
- O commit do servidor vem do texto do design; o escriba não o conferiu contra o repositório do servidor.
- Os roadmaps individuais (`roadmap-m0` a `roadmap-m7`) não foram lidos: a lista de marcos e a contagem de etapas vêm do `docs/roadmaps/README.md`.
- O pacote JAR multiplataforma (Linux x64 e Windows x64) é hipótese a confirmar na M1 E01; se falhar, a alternativa é `./gradlew run` num clone no Windows.

Da captura de 2026-11-13:

- O escriba não conferiu os números do contrato (303, 335, 32, 23) nem o commit do servidor contra o repositório do servidor; vêm do texto da análise.
- Os roadmaps M3, M4 e M5 não foram lidos diretamente: as ampliações de M3 E03, M4 E02 e M5 E01 vêm do bloco de contexto da M0 E02 e da tabela de `docs/roadmaps/README.md`.
- A biblioteca de PDF ainda não foi escolhida (hipótese H4 da M2); se nenhuma servir, a decisão volta ao usuário antes de cair para arquivo temporário.

Da captura de 2026-11-15:

- O escriba não conferiu contra o repositório do servidor os números (131 commits, 335 operações), o commit nem a regra da ARCHITECTURE §7; vêm do texto da análise.
- O tipo que o ogen gera para o `oneOf` (`JsonElement`) ainda não foi provado pelo front; é o que a M0 E03 vai caracterizar.

*Nota do curador (conferência por `git` em 2026-11-17, só leitura):* as capturas diziam "sem commit". Hoje os documentos estão na `main` do front: design e ADRs 0001 a 0006 no `abe64cd` (2026-11-10), ADR 0009 no `29cc674` (2026-11-13) e ADR 0010 no `ebfd468` (2026-11-15), com atualizações posteriores. O texto atual dos arquivos não foi comparado linha a linha com as capturas.

---

## Proveniência

- 2026-11-17 — [[2026-11-10 - ZenyHotelManager-DesktopFront - decisões de arquitetura e marcos do front desktop - 16d5b400]] (capture_id: 16d5b400-b2e5-490e-b063-b61b40c14257): objetivo e restrições, decisões F1 a F6, chamadas do arquiteto e limitações; nota criada pelo curador.
- 2026-11-17 — [[2026-11-13 - ZenyHotelManager-DesktopFront - análise da rodada 2 do M0 e ADR 0009 documentos PDF e impressão - 677b277a]] (capture_id: 677b277a-44a4-4da4-8214-4dfca2edc865): ADR 0009 (documentos em PDF e impressão) e limitações.
- 2026-11-17 — [[2026-11-15 - ZenyHotelManager-DesktopFront - análise da rodada 3 do M0 e ADR 0010 resposta que varia com a permissão - 5bba7217]] (capture_id: 5bba7217-6f3f-460d-8b80-ace44d5b8683): ADR 0010 (resposta que varia com a permissão), atualizações de 2026-11-15 nos ADRs 0007 e 0009 e limitações.
