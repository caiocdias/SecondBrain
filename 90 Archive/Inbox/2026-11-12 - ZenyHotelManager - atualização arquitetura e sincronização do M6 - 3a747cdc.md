---
type: capture
status: archived
created: 2026-11-12
capture_id: 3a747cdc-6309-4bfa-bea2-3f6cd483a30f
---
# ZenyHotelManager - atualização arquitetura e sincronização do M6

## Conteúdo capturado

Complemento das capturas pendentes [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 - 2c135bbf]] (`capture_id` `2c135bbf-8248-4987-a617-dcb3fa94c0a5`) e [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 (revisão humana) - 64ce6698]] (`capture_id` `64ce6698-9d2c-4a1c-b4d0-af930d24bff5`). **Vale sobre elas** onde tratarem do mesmo trecho. Organizada por nota de tema; cada item diz se **substitui** ou **complementa** e qual trecho. Conteúdo relatado pela sessão `arquiteto` que fez as alterações (ver Origem).

### 1. `ZenyHotelManager - Arquitetura e estrutura de módulos` (complementa a regra por camadas)

- **Ordem interna da camada Hospedagem** (decisão do usuário, 2026-11-12; ARCHITECTURE §3.1 "Regra por camadas" e §3.2): `rates` < `reservations` < `frontdesk`. Um módulo da camada pode depender de quem vem antes dele na ordem, nunca de quem vem depois. As arestas `reservations` → `rates`, `frontdesk` → `reservations` e `frontdesk` → `rates` deixaram de ser "exceções registradas". O alcance de `frontdesk` → `rates` continua só os tipos públicos que a `ReservationsApi` usa (`RatePlanId`, `GuaranteeType`, `PackageId`, `PackageCharge`), porque preço e política chegam congelados na reserva, e ampliá-lo exige decisão. As exceções de mesma camada que continuam são `billing` → `payments` e `endofday` → `reporting`. O diagrama da §3.2 mostra a ordem dentro da Hospedagem.
- Conferido no código (`allowedDependencies`): `rates` = shared, rooms, billing, hotel; `reservations` = shared, hotel, rooms, rates, guests, billing, notifications, printing; `frontdesk` = shared, hotel, reservations, rooms, guests, billing, files, rates, staff, printing. Nenhuma aresta contrária à ordem e nenhum ciclo; o `ModularityTest` não mudou.
- **Aresta prevista, ainda não no código:** `fnrh` → `frontdesk`, só pela porta dos rótulos da ficha (M6 E15). Segue a regra por camadas, porque a "Integração governamental" fica acima da Hospedagem. Quando a E15 rodar, entra na tabela §3.1 e no teste do `fnrh`, cujo comentário "nunca frontdesk" muda. O `frontdesk` continua sem importar o `fnrh`.
- Nota de leitura: a tabela §3.1 ainda lista `hotel` entre as dependências do `fnrh`, e o código não usa (o código é subconjunto da tabela; não foi alterado).

### 2. `ZenyHotelManager - Módulo fnrh` (complementa a seção da configuração e encerra a divergência da E16)

- **ARCHITECTURE §12, item "Credencial"** (decisão do usuário, 2026-11-12): a credencial da integração (usuário e senha) fica cifrada em repouso (os dois campos de `FnrhSettings` usam `EncryptedStringConverter`), nunca na trilha nem nos logs (nem o usuário) e é removível pela ação com trilha (`POST …/clear-credentials`, padrão inalterado). **Na API, o segredo é a senha:** nunca é devolvida, e a resposta só traz `passwordSet`. O `username` volta em `GET` e `PUT /api/v1/fnrh/settings` (`FnrhSettingsResponse.username`), que só o Administrador lê (`fnrh.settings.manage`). Contrato e código não mudaram.
- Isso **substitui**, na captura E12 (`2c135bbf`, item 6) e na E12 (revisão humana, `64ce6698`), a divergência "username devolvido em claro contra a §12": está resolvida.
- Alternativa descartada: mascarar ou tirar o usuário da resposta, o que mudaria o contrato sem proteger segredo.
- **Planejado no M6:**
  - E14 acrescenta a operação de no-show (`FnrhOperation` com `rank`, migração no `submission_operation_ck` de `fnrh/V2026_11_10_1000__create_fnrh_submissions.sql`; no contrato a operação é `x-extensible-enum`).
  - E15 faz o `fnrh` implementar uma porta do `frontdesk` que traduz os códigos de motivo de viagem e de meio de transporte em rótulo, pelo catálogo de domínios já semeado (`FnrhDomainCatalog`, `TRAVEL_REASONS` e `TRANSPORT_MODES` em `fnrh/V2026_11_04_1030__create_fnrh_domain_values.sql`).
  - E16 apaga as duas cópias de `FnrhSubmissionDismissCompat.kt` em `src/test`.

### 3. `ZenyHotelManager - Estado por marco` e o Estado do hub `10 Projects/ZenyHotelManager.md`

- **Complementa** o estado do M5: as decisões de arquitetura E12 (e) e (f) estão aplicadas na ARCHITECTURE (`0e58cf9`); o roadmap do M5 registra onde cada decisão pendente foi parar (`b23958e`); nenhuma tag do M5 mudou (E09 segue `#bloqueada` pela Q-12).
- **Substitui** "sincronizar o roadmap do M6 com o código" (Próximos passos do hub e captura E12, item 5) por: **roadmap do M6 sincronizado em 2026-11-12** (`docs/roadmaps/roadmap-m6-operacao-fechamento.md`, `b23958e`), agora com **17 etapas**, todas `#pendente`.
  - Novas: **E15** (rótulos da FNRH na ficha e descrição de `frontdesk.stays.checkin`, decisões E11 (f) e (g) do M5), **E16** (dívidas de teste: o teste de índices das listas por situação da M5 E01 e o `FnrhSubmissionDismissCompat.kt` duplicado) e **E17** (corpo mínimo nas respostas de `restrict`, `lift-restriction` e `merge` do `guests` sem `guests.profiles.read`, decisão E15 (h) do M5, com Revisão humana: sim).
  - Elas ficam num bloco "Manutenção herdada do M5", depois do fechamento, e o gate E12 do M6 passou a depender delas.
  - Hipóteses novas: **H10** (testes que rodam o fechamento real usam um caminho próprio, banco ou contexto isolado criado na E10, porque o fechamento age sobre o hotel inteiro e avança a data; decidida pelo `arquiteto` pela opção recomendada e revisável) e **H11** (rótulos no catálogo da FNRH).
  - **H6 corrigida:** a `FilesApi` não grava conteúdo pelo servidor, e a E09 acrescenta a gravação.
  - `docs/roadmaps/README.md`: o M6 passa a ter 17 etapas.
- **Substitui**, em Próximos passos do hub, a lista do G14 "o `arquiteto` cria duas etapas de manutenção" (captura E12, item 1.12) por: as duas estão criadas (M6 E15 e E17). O próximo passo é o push do usuário (a `main` local está à frente da `origin/main`) e, depois, executar o M6 com `claude --agent orquestrador`; o primeiro lote começa pela E10 (Revisão humana: sim).

## Contexto

Sessão `claude --agent arquiteto` que aplicou na ARCHITECTURE as duas decisões de arquitetura da E12 do M5 tomadas pelo usuário (ordem da Hospedagem e credencial da FNRH) e sincronizou o roadmap do M6 com o código, criando as etapas de manutenção herdadas do M5. Publicada pelo `brain-escriba` a pedido dessa sessão.

## Origem

- Projeto: ZenyHotelManager; repositório `/home/caio/repos/ZenyHotelManager`, branch `main`.
- Sessão: `claude --agent arquiteto`, 2026-11-12.
- Commits: `0e58cf9` (ARCHITECTURE) e `b23958e` (roadmaps), sobre `3a42e35`; sem push (o push é do usuário).
- Arquivos: `docs/ARCHITECTURE.md` (§3.1, §3.2, §12), `docs/roadmaps/roadmap-m6-operacao-fechamento.md`, `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`, `docs/roadmaps/README.md`.
- Data: 2026-11-12.

## Por que registrar

Fechar no brain as duas decisões de arquitetura pendentes da E12 do M5, resolver a divergência do `username` da FNRH e atualizar o Estado e os Próximos passos do hub com o M6 sincronizado e pronto para execução.

## Limitações e incertezas

- O diagrama Mermaid da §3.2 não foi renderizado para conferência (não há `mmdc` na máquina).
- As notas de tema não foram relidas inteiras pelo arquiteto; o texto se apoia nas capturas pendentes E08 a E12 e no código.
- O escriba não conferiu os commits, a ARCHITECTURE nem os roadmaps; o conteúdo vem do relato da sessão `arquiteto`.
- H10 foi decidida pelo `arquiteto` pela opção recomendada, sem confirmação do usuário; é revisável.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Arquitetura e estrutura de módulos]]
- [[ZenyHotelManager - Módulo fnrh]]
- [[ZenyHotelManager - Estado por marco]]
- [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 - 2c135bbf]]
- [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E12 (revisão humana) - 64ce6698]]
- [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E11 (revisão humana) - cca61b94]]
