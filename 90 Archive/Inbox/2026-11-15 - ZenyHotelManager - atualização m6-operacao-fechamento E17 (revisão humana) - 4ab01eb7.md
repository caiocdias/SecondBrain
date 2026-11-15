---
type: capture
status: archived
created: 2026-11-15
capture_id: 4ab01eb7-f60b-483f-8ae1-66de5753d21c
---
# ZenyHotelManager - atualização m6-operacao-fechamento E17 (revisão humana)

## Conteúdo capturado

Complemento da captura [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E17 - cb3979d0]] (`capture_id` cb3979d0-82db-4bb4-bf98-0a7b8630e398). Registra a revisão humana da E17 do M6 e as decisões do usuário. **Substitui** na captura anterior: a decisão (a) "pendente na entrevista" e a decisão (b) "sem confirmação do usuário"; o `oneOf` deixa de ser provisório.

### Decisões do usuário em 2026-11-15

Tomadas na entrevista do fim do lote da E17, ambas pela opção recomendada (H14 do roadmap do M6):

- **(a) Forma do contrato.** As escritas `restrict`, `lift-restriction` e `merge` do `guests` **mantêm** `oneOf: [GuestResponse, GuestWriteSummaryResponse]` sem discriminador. Com o ogen 0.16.1, os clientes gerados recebem `JsonElement` nessas três operações e decodificam pelo campo `fullName`. Alternativa descartada: o discriminador tipado, que pediria uma propriedade nova no `GuestResponse` de todas as operações de perfil.
- **(b) Corpo mínimo.** O corpo mínimo `{id, restricted}` está **aprovado**, com a versão no `ETag`.

### Efeito nas notas

- **`ZenyHotelManager - Convenções de API`: substitui** o texto provisório do `oneOf` (item 2 da captura anterior). O `oneOf` vira regra do projeto: resposta que varia com a permissão usa `oneOf` sem discriminador, com ramos disjuntos pelo `required` e sem `additionalProperties: false`. Some a linha "decisão pendente na entrevista do usuário".
- **`ZenyHotelManager - Módulo guests`: complementa** com a confirmação da decisão (b): o corpo mínimo `{id, restricted}` está aprovado pelo usuário.
- **`ZenyHotelManager - Estado por marco`: complementa** a subseção "M6 E17 (2026-11-15)": a revisão humana da E17 está **feita** (substitui "Revisão humana: sim, pendente"). As decisões (a) e (b) são do usuário; (c) e (d) seguem pela opção recomendada do orquestrador, sem confirmação separada. No "Perguntas abertas" do hub, a (a) não fica mais pendente.

### Pendência com o `arquiteto`

Registrar a regra do `oneOf` na ARCHITECTURE §7 (resposta que varia com a permissão: `oneOf` sem discriminador, ramos disjuntos pelo `required`, sem `additionalProperties: false`).

### Estado do repositório

Lote integrado na `main` local (`merge: E17 (M6)`, `6d7cdd9`, mais o commit deste registro), à espera do `git push origin main` pelo usuário. Próximas etapas elegíveis do M6: E18, depois E01.

## Contexto

Fechamento da revisão humana da E17 do roadmap `roadmap-m6-operacao-fechamento` do ZenyHotelManager, publicado pelo `brain-escriba` a pedido do orquestrador de etapa, conforme a regra "Atualização por capturas" do hub. Complemento da captura cb3979d0; contém só o que é novo.

## Origem

- Projeto: ZenyHotelManager; repositório `/home/caio/repos/ZenyHotelManager`, branch `roadmap/m6-operacao-fechamento` (lote integrado na `main` local, `6d7cdd9`).
- Fonte: pedido do orquestrador, que relata a entrevista do usuário de 2026-11-15 (H14 do roadmap do M6), e a captura cb3979d0 lida como contexto.
- Data: 2026-11-15.

## Por que registrar

Fecha a decisão pendente da captura anterior, para o curador consolidar o `oneOf` como regra em Convenções de API e marcar a revisão humana da E17 como feita.

## Limitações e incertezas

- As decisões vêm do relato do orquestrador; não li o roadmap (H14) nem o código, e não conferi o estado do Git.
- Não li as notas permanentes do brain; os nomes de seção seguem a captura anterior.

## Possíveis conexões

- [[ZenyHotelManager]]
- [[ZenyHotelManager - Módulo guests]]
- [[ZenyHotelManager - Convenções de API]]
- [[ZenyHotelManager - Estado por marco]]
- [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E17 - cb3979d0]]
