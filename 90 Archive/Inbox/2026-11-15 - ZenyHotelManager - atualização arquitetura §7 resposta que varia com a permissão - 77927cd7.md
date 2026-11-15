---
type: capture
status: archived
created: 2026-11-15
capture_id: 77927cd7-51b9-4718-b108-048c262be5c7
---
# ZenyHotelManager - atualização arquitetura §7 resposta que varia com a permissão

## Conteúdo capturado

Complemento das capturas [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E17 - cb3979d0]] (`capture_id` cb3979d0-82db-4bb4-bf98-0a7b8630e398) e [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E17 (revisão humana) - 4ab01eb7]] (`capture_id` 4ab01eb7-f60b-483f-8ae1-66de5753d21c). Registra a regra do `oneOf` que a soul `arquiteto` gravou na `docs/ARCHITECTURE.md` §7 (commit `5e06f16`). Organizada por nota, dizendo se **substitui** ou **complementa**.

Decisão (do usuário, 2026-11-15, revisão humana da M6 E17, H14 do roadmap do M6): resposta que varia com a permissão usa `oneOf` sem discriminador. O texto abaixo é a redação do `arquiteto` para a regra, já registrada na ARCHITECTURE.

### 1. `ZenyHotelManager - Convenções de API`

**Complementa** a nota com a regra abaixo, que agora está na `docs/ARCHITECTURE.md` §7, linha "Resposta que varia com a permissão" (commit `5e06f16`).

- **Substitui** o texto provisório do `oneOf` do item 2 da captura cb3979d0.
- **Fecha** a "Pendência com o `arquiteto`" da captura 4ab01eb7.
- **Corrige** o parêntese "(ele quebraria a disjunção)" do item 2 da cb3979d0: o motivo de não usar `additionalProperties: false` é **preservar a evolução aditiva**; a disjunção vem do `required`.

Texto proposto para a nota:

> - **Resposta que varia com a permissão** (ARCHITECTURE §7; decisão do usuário em 2026-11-15, revisão humana da M6 E17, H14): quando o corpo de sucesso depende da permissão de quem chama, a resposta declara `oneOf` com o esquema completo e o reduzido, **sem discriminador**. Os ramos são disjuntos pelo `required`: o reduzido exige ao menos uma propriedade que o completo não tem, e o completo exige uma que o reduzido não tem. Nenhum ramo usa `additionalProperties: false`, para preservar a evolução aditiva. O media type de sucesso não muda (trocá-lo é `ERR` no oasdiff). Qual corpo devolver é decidido no caso de uso (camada `application`, ARCHITECTURE §8.2): depois do `require` da escrita, na mesma transação, ele pergunta `Authorization.grantOrNull` e, sem a permissão, não monta o objeto completo; o controller só traduz. No springdoc: `@ApiResponse(content = [Content(mediaType = APPLICATION_JSON_VALUE, schema = Schema(oneOf = [Completo::class, Reduzido::class]))])` e retorno `ResponseEntity<Any>`. Consequências: o oasdiff acusa `warning` `response-body-wrapped-in-one-of-original-preserved`, não `ERR`; com o ogen 0.16.1, os clientes gerados recebem essas operações como `JsonElement`, e cabe ao cliente distinguir os ramos pelo `required`. Alternativa descartada: o discriminador, que pede uma propriedade nova no esquema completo de todas as operações que o usam. Primeiro uso: `restrictGuest`, `liftGuestRestriction` e `mergeGuests` do `guests` (M6 E17), `oneOf: [GuestResponse, GuestWriteSummaryResponse]`; o reduzido é `{id, restricted}` (exige `restricted`), o completo exige `fullName`; helper `Guest.writeResult(authorization)` em `guests/application/GuestsSupport.kt`.

### 2. Roadmap do M6 (`docs/roadmaps/roadmap-m6-operacao-fechamento.md`)

Fato relatado pelo `arquiteto`: a H14 deixou de dizer "Pendente com o `arquiteto`" e aponta para o registro na ARCHITECTURE §7 (2026-11-15). Validado com `check_roadmap.py`: OK, sem problema estrutural. Se alguma nota do brain (por exemplo, `ZenyHotelManager - Estado por marco`) citar a H14 como pendente, **substitui** pela situação acima.

### 3. Hub `ZenyHotelManager` ("Perguntas abertas" ou "Estado")

**Substitui**, onde houver menção: a regra do `oneOf` **não está mais pendente** com o `arquiteto`; está registrada na ARCHITECTURE §7 (commit `5e06f16`).

### Conferências

- **Conferido pelo `arquiteto` antes da captura (relato dele):** em `api/openapi.yaml` as três operações têm `oneOf` sem `discriminator` e nenhum `additionalProperties: false`; `GuestWriteSummaryResponse` exige `id` e `restricted`; `GuestResponse` exige `fullName` e não tem a propriedade `restricted` (tem `restriction`); `Authorization.grantOrNull` existe em `shared/Authorization.kt`.
- **Não verificado pelo `arquiteto`:** o comportamento do SDK do ogen (`JsonElement`) e o resultado do oasdiff (`warning`, não `ERR`); ambos vêm do handoff da E17.
- **Conferido pelo escriba:** o commit `5e06f16` existe na `main` local ("Registra na ARCHITECTURE §7 a regra da resposta que varia com a permissão", 2026-11-15, Soul: arquiteto) e altera só `docs/ARCHITECTURE.md` (1 linha adicionada) e `docs/roadmaps/roadmap-m6-operacao-fechamento.md` (1 linha trocada).

## Contexto

Pedido da soul `arquiteto` em 2026-11-15, depois de registrar na ARCHITECTURE §7 a regra decidida pelo usuário na revisão humana da M6 E17. Publicado pelo `brain-escriba` conforme a regra "Atualização por capturas" do hub. Contém só o que é novo em relação às capturas cb3979d0 e 4ab01eb7.

## Origem

- Projeto: ZenyHotelManager; repositório `/home/caio/repos/ZenyHotelManager`, branch `main`, commit `5e06f16` (sem push; o push é do usuário).
- Arquivos: `docs/ARCHITECTURE.md` §7 (linha "Resposta que varia com a permissão") e `docs/roadmaps/roadmap-m6-operacao-fechamento.md` (H14).
- Fonte da decisão: decisão do usuário de 2026-11-15 na revisão humana da M6 E17 (H14 do roadmap do M6).
- Data: 2026-11-15.

## Por que registrar

Fechar a pendência do `oneOf` aberta nas capturas da E17, dar ao curador o texto final da regra para a nota de Convenções de API e corrigir o motivo dado para não usar `additionalProperties: false`.

## Limitações e incertezas

- Não li a `docs/ARCHITECTURE.md`, o roadmap, o `api/openapi.yaml` nem o código; o texto da regra e as conferências vêm do relato do `arquiteto`. Conferi só o `git show --stat` do commit `5e06f16`.
- Não li as notas permanentes do brain (`Convenções de API`, hub, `Estado por marco`); o curador localiza os trechos a substituir.
- O comportamento do ogen 0.16.1 e o resultado do oasdiff não foram reverificados nesta etapa.
- O commit `5e06f16` está só na `main` local até o push do usuário.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Convenções de API]]
- [[ZenyHotelManager - Módulo guests]]
- [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E17 - cb3979d0]]
- [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E17 (revisão humana) - 4ab01eb7]]
