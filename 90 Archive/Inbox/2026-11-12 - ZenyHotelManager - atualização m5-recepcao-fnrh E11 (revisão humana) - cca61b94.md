---
type: capture
status: archived
created: 2026-11-12
capture_id: cca61b94-000c-4d38-9f81-59e12c1d9f99
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E11 (revisão humana)

## Conteúdo capturado

Complemento da captura [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E11 - d1100f5a]]. **Vale sobre ela** nos pontos abaixo. Origem das decisões: entrevista do usuário no fim do lote, em 2026-11-12, registrada no roadmap da branch `roadmap/m5-recepcao-fnrh` (commit `6c87b04`, já na `main` local).

### 1. Revisão humana da E11 feita (decisão do usuário)

**Decisão do usuário:** a revisão humana da E11 foi feita em 2026-11-12, na entrevista do fim do lote, todas pela opção recomendada:

- **D-E11-12:** a porta `FolioOwnerDescriber` no `billing` (implementada pelo `reservations`; M6 a M8 implementam `GROUP`, `EVENT` e `COMPANY`) é mantida. É o padrão para descrever o dono da conta.
- **D-E11-9:** o contrato das rotas de documentos fica aprovado como está: `GET …/pdf`, `POST …/print` com `@Idempotent` e `202`, `audience` padrão `GUEST` no PDF do extrato, impressão em qualquer impressora ativa por quem tem a permissão do documento.
- **D-E11-1:** openhtmltopdf (LGPL-2.1+), PDFBox 3 e Thymeleaf mantidos. O aviso da LGPL deve ser registrado na documentação de implantação do M8.
- **D-E11-7:** `FilesApi.readContent` serve só para anexo comum (emenda à H18). Quem precisar ler anexo sensível pelo servidor acrescenta a leitura com trilha na etapa que precisar.
- **D-E11-10:** a ficha fica sob `frontdesk.stays.checkin`, `GET` sem trilha. A descrição da permissão deve passar a dizer que ela abre a ficha.
- **D-E11-11:** os rótulos do motivo de viagem e do meio de transporte na ficha passarão a vir por uma porta do `frontdesk` implementada pelo `fnrh` (inversão por porta), numa etapa de manutenção que **ainda não existe** no roadmap. Cabe ao `arquiteto` criá-la.

**Complementa** as notas afetadas, cujas decisões do orquestrador passam a decisões do usuário:

- `ZenyHotelManager - Módulo printing`
- `ZenyHotelManager - Módulo billing (caixa, pagamentos, caução e encerramento)`
- `ZenyHotelManager - Hospedagem e recepção`
- `ZenyHotelManager - Módulo files`
- `ZenyHotelManager - Convenções de API`

### 2. Estado e próximos passos

- **Substitui**, na captura da E11 e no Estado do hub `10 Projects/ZenyHotelManager.md` e em `ZenyHotelManager - Estado por marco`, "Revisão humana da E11 pendente" por "feita em 2026-11-12". A revisão humana pendente volta a ser **só E13 e E07**.
- Próxima etapa do M5: o gate E12.
- Em "Próximos passos" do hub, acrescentar: o `arquiteto` cria a etapa de manutenção dos rótulos da FNRH na ficha (D-E11-11) e, já pendente desde a E15 (h), a do `guests`.

### 3. Decisões sem confirmação do usuário

**Substitui**, na lista da captura da E11, o trecho do lote E11: seguem revisáveis só (b) API de documentos, (c) texto sem fonte embutida e (i) execução em série por memória. As demais saem da lista por terem sido aprovadas.

### 4. Git

O lote da E11 foi integrado na `main` local pelo merge `5ed46c3` ("merge: E11 (M5)"), seguido de `6c87b04` ("Registra a revisão humana da E11 no roadmap do M5"). O push é do usuário. Isso preenche o hash que a captura da E11 deixou em aberto.

## Contexto

O orquestrador do lote do roadmap M5 pediu este complemento depois da entrevista de revisão humana do fim do lote, após a captura de fechamento da E11.

## Origem

- Projeto ZenyHotelManager, repositório `/home/caio/repos/ZenyHotelManager`, roadmap `docs/roadmaps/roadmap-m5-recepcao-fnrh.md` ("Decisões do lote E11" e handoff da E11), commits `5ed46c3` e `6c87b04`.
- Relato do orquestrador, em 2026-11-12, sobre as decisões do usuário.

## Limitações e incertezas

- O escriba não leu o roadmap nem os commits; o conteúdo vem do relato do orquestrador e do modelo do complemento da E10. Não reli a captura da E11 anterior nem as notas de tema; o curador localiza os trechos exatos a substituir.
- As referências a "Próximos passos" do hub seguem o relato e não foram conferidas no texto atual.

## Possíveis conexões

- [[2026-11-12 - ZenyHotelManager - atualização m5-recepcao-fnrh E11 - d1100f5a]]
- [[ZenyHotelManager]]
- [[ZenyHotelManager - Estado por marco]]
- [[ZenyHotelManager - Módulo printing]]
- [[ZenyHotelManager - Módulo billing (caixa, pagamentos, caução e encerramento)]]
- [[ZenyHotelManager - Hospedagem e recepção]]
- [[ZenyHotelManager - Módulo files]]
- [[ZenyHotelManager - Convenções de API]]
