---
type: capture
status: archived
created: 2026-11-10
capture_id: a22890e7-e6b1-4e99-97d7-747bfcdd5788
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E15

Fechamento da E15 (descrição de gênero) do M5. Cada item abaixo traz o texto novo ou alterado e diz qual nota do brain ele substitui ou complementa. O curador consolida quando o usuário processar a Inbox.

## Conteúdo capturado

### 1. Hub `ZenyHotelManager` ("Estado") e `ZenyHotelManager - Estado por marco`

Substitui o trecho do Estado sobre M5 e sobre a E15 (antes: E15 `#em-andamento`, interrompida; ordem E15, E08, E16, E10). Texto novo:

- M5 E15 `#concluida` em 2026-11-10 (commit de fechamento `1d72325`, branch `roadmap/m5-recepcao-fnrh`).
- M5 com E01 a E07, E13, E14 e E15 concluídas. Próxima elegível: E08 (revisão humana: sim), depois E16 e E10. E09 segue `#bloqueada` (Q-12), dependente de E08 e E16.
- Decisões do lote E15 (a) a (h) tomadas pela opção recomendada, sem confirmação do usuário (mesmo regime dos lotes E04 a E06, E13, E14 e E07; entram na lista de decisões sem confirmação do hub e do Estado por marco). Destaques:
  - D-E15-4: o módulo Financeiro lê a descrição de gênero.
  - D-E15-6: o eco curto não é mascarado (ver item 3).
  - E15 (h): lacuna conhecida herdada do M3 (ver item 2).

### 2. `ZenyHotelManager - Módulo guests` (complementa)

Descrição de gênero (`genderDescription`):

- Coluna `guests.guest.gender_description`, cifrada (`EncryptedStringConverter`).
- Até 100 caracteres, sem `pattern`.
- Só é aceita com gênero `OTHER`: regra no agregado e `CHECK guest_gender_description_ck`; erro `400 GENDER_DESCRIPTION_REQUIRES_OTHER_GENDER`.
- Volta em toda resposta de perfil (`GuestResponse`); fica fora do `GuestSummary`.
- Anda com o gênero na mesclagem (`merge`).
- Entra na exportação do titular.
- Sai na anonimização, inclusive da cadeia de absorvidos; o `guest_anonymized_ck` ganhou a coluna.
- Trilha de auditoria registra só o nome do campo, não o valor.
- Lacuna conhecida (E15 (h), herdada do M3): `restrict`, `lift-restriction` e `merge` devolvem o perfil inteiro conferindo só a permissão da escrita.

### 3. `ZenyHotelManager - Módulo fnrh`

Substitui a frase "Na M5 E15, o mapeador passa a levar a descrição de gênero" por: o `FnrhGuestData` tem `genderDescription` e o `FnrhPersonMapper` a envia como `GeneroDescricao` somente com `OUTRO`.

Complementa o saneador:

- Desde o commit `8d6203a`, o controle Unicode é normalizado também nos valores enviados (antes, um valor com controle não casava com o eco devolvido).
- Risco aceito D-E15-6: valor de 1 ou 2 caracteres ecoado não é mascarado (`MIN_VALUE_LENGTH = 3`).
- Notas para a E09: confirmar o limite real e o eco de `GeneroDescricao` na homologação.

### 4. `ZenyHotelManager - Ambiente, banco, chaves e build` (complementa)

O `osv-scanner scan source -r .` rodado de dentro de um worktree sob `.claude/worktrees/` não lê nada ("No package sources found"), porque esse caminho está no `.gitignore` do checkout principal. Usar `--no-ignore`.

### 5. Nota para E10 e E11 (em `Estado por marco`, junto das etapas, ou onde o curador achar melhor)

O texto livre do perfil do hóspede aceita caracteres de controle e de formatação Unicode. A renderização da ficha e dos PDFs precisa tratá-los.

## Contexto

Etapa E15 do roadmap `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`, executada pelo orquestrador no worktree `.claude/worktrees/roadmap-m5-recepcao-fnrh`. Captura de fechamento de etapa prevista no `CLAUDE.md` do projeto.

## Origem

- Projeto: ZenyHotelManager, `/home/caio/repos/ZenyHotelManager`, branch `roadmap/m5-recepcao-fnrh`, commit de fechamento `1d72325`.
- Fontes no repositório: seções "E15" e "Decisões do lote E15" de `docs/roadmaps/roadmap-m5-recepcao-fnrh.md`; plano `docs/superpowers/plans/2026-11-06-m5-recepcao-fnrh-e15.md`; `README.md` (seção API, hóspedes).
- Data da etapa: 2026-11-10.

## Por que registrar

Manter o hub, o Estado por marco e as notas de guests, fnrh e ambiente alinhados ao código após a E15, e deixar visíveis as decisões tomadas sem confirmação do usuário.

## Limitações e incertezas

- Resumo do agente escriba a partir do briefing do orquestrador; as fontes do repositório não foram relidas por mim, então detalhes finos (por exemplo, o texto exato de D-E15-4, D-E15-6 e E15 (h)) devem ser conferidos no roadmap.
- As decisões (a) a (h) não passaram por confirmação do usuário.
- Os arquivos do repositório citados existem só no caminho local do projeto.
- Busca por captura equivalente em `00 Inbox/` (vazia) e `90 Archive/Inbox/` (por nome): nenhuma de E15.

## Possíveis conexões

[[ZenyHotelManager]], [[ZenyHotelManager - Estado por marco]], [[ZenyHotelManager - Módulo guests]], [[ZenyHotelManager - Módulo fnrh]], [[ZenyHotelManager - Ambiente, banco, chaves e build]].
