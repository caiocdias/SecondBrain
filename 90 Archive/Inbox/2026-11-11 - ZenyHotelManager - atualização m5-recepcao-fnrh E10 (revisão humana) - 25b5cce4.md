---
type: capture
status: archived
created: 2026-11-11
capture_id: 25b5cce4-a919-4cf3-aaaf-99b5722239e8
---
# ZenyHotelManager - atualização m5-recepcao-fnrh E10 (revisão humana)

## Conteúdo capturado

Complemento da captura [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 - 4dd12e66]]. **Vale sobre ela** nos pontos abaixo. Origem das decisões: entrevista do usuário no fim do lote, em 2026-11-11, registrada no roadmap da branch `roadmap/m5-recepcao-fnrh` (commit `7aa2527`, já na `main` local).

### 1. Revisão humana da E10 feita (decisão do usuário)

**Decisão do usuário:** a revisão humana da E10 foi feita. O usuário aprovou as quatro decisões de arquitetura, cada uma com a opção recomendada:

- (a) A credencial de serviço fica como porta em `shared` (`ServiceCredentialRealm` mais uma segunda cadeia de segurança). É o **padrão para M7 e M8**.
- (b) O contrato com o repositório do agente é aprovado como está: token `zpa_`, esquema `printAgentToken`, evento SSE `job` com `id` = posição, `200 []` no long-poll, ack `{result, failureCode}`, e o agente deduplica por id.
- (c) Um stream por agente; a contrapressão por ack fica para depois.
- (d) Sem alerta de falha de impressão por enquanto. Um alerta pode vir pelo Prometheus/Alertmanager do M8 E18 (D19) sobre a métrica `zeny_printing_jobs`, sem aresta `printing` → `notifications`.

- **Substitui**, na captura anterior (seção Estado do hub `10 Projects/ZenyHotelManager.md` e `ZenyHotelManager - Estado por marco`), "Revisão humana da E10 … pendente" por "feita em 2026-11-11 (padrão aprovado)". A revisão humana pendente agora é **só E13 e E07**; ajuste também as frases correlatas do hub ("Próximos passos", "Perguntas abertas") nesse sentido.
- **Complementa** `ZenyHotelManager - Módulo printing` (nota nova proposta pela captura anterior) e `ZenyHotelManager - Segurança, autenticação e autorização`: as decisões (a) a (d) acima são do usuário, não mais só do orquestrador.

### 2. Lista de decisões sem confirmação do usuário

**Substitui**, na lista da captura anterior, o trecho do lote E10: ele mantém apenas (d) prazos e limites, (e) ack 409×404, e contato sem trilha de auditoria. As demais decisões do lote saem da lista por terem sido aprovadas.

### 3. Git

Lote E16 + E10 integrado na `main` local (merge `6a025d5`, mais `7aa2527` com a revisão humana). O push cabe ao usuário.

## Contexto

O orquestrador do lote do roadmap M5 pediu este complemento depois da entrevista de revisão humana do fim do lote, após a captura de fechamento da E10.

## Origem

- Projeto ZenyHotelManager, branch `roadmap/m5-recepcao-fnrh`, commits `6a025d5` (merge E16 e E10) e `7aa2527` ("Registra a revisão humana da E10 no roadmap do M5").
- Relato do orquestrador, em 2026-11-11, sobre as decisões do usuário.

## Limitações e incertezas

- O escriba não leu o roadmap nem os commits; o conteúdo vem do pedido do orquestrador e do modelo da captura da E08 (revisão humana). Não reli a captura da E10 anterior nem as notas de tema; o curador localiza o trecho exato a substituir.
- A referência a "Próximos passos" e "Perguntas abertas" do hub segue o padrão da captura da E08 e não foi conferida no texto atual.

## Possíveis conexões

- [[2026-11-11 - ZenyHotelManager - atualização m5-recepcao-fnrh E10 - 4dd12e66]]
- [[ZenyHotelManager]]
- [[ZenyHotelManager - Estado por marco]]
- [[ZenyHotelManager - Módulo printing]]
- [[ZenyHotelManager - Segurança, autenticação e autorização]]
