---
type: capture
status: archived
created: 2026-11-15
capture_id: c383eb2b-baa6-47c2-9eb7-545ebe5dfb34
---
# ZenyHotelManager - atualização m6-operacao-fechamento E18 (correção)

## Conteúdo capturado

Complemento da captura [[2026-11-15 - ZenyHotelManager - atualização m6-operacao-fechamento E18 - a68d398b]] (capture_id: a68d398b-2037-4b20-af27-8039b163ae0e). Corrige só o item 6 ("Schemas, migrações e views de relatório"), última linha da lista (linha 104 do arquivo), que diz que a última migração continua `printing/V2026_11_11_1001__grant_printing_to_app_role.sql`. **O curador deve ignorar essa frase.**

Texto correto (**substitui** a frase):

- A E18 **não tem migração**.
- A última migração do projeto é `V2026_11_14_1000__add_fnrh_no_show.sql` (M6 E14). Antes dela: `V2026_11_13_1000__add_reservation_no_show.sql` e `V2026_11_12_1001__grant_endofday_to_app_role.sql`.
- Toda migração nova precisa de timestamp posterior a `V2026_11_14_1000` (`outOfOrder` desligado).

O resto da captura a68d398b não muda.

## Origem

Conferência do orquestrador no worktree `/home/caio/repos/ZenyHotelManager/.claude/worktrees/roadmap-m6-operacao-fechamento` (`find src/main/resources -name 'V2026_*.sql'`), repassada ao escriba; o escriba não repetiu a conferência.

## Por que registrar

Evitar que o curador integre uma informação errada sobre a última migração.

## Limitações e incertezas

A lista de migrações vem do relato do orquestrador, não de leitura direta pelo escriba.

## Possíveis conexões

[[ZenyHotelManager - Schemas, migrações e views de relatório]], [[ZenyHotelManager - Estado por marco]]
