---
type: capture
status: archived
created: 2026-11-08
capture_id: 731fe7d4-6520-486e-8b7c-59f403040bac
---

# ZenyProjectHandler - decisões D16 a D20 janela de release 0.6.0

## Conteúdo capturado

Decisões registradas em 2026-11-08 no roadmap de leitura vetorial por poste do ZenyProjectHandler. Todas as decisões abaixo são fatos do roadmap; a autoria de cada uma está indicada.

**Decisão D16 (usuário; desenho da execução pelo arquiteto).** A próxima execução do orquestrador faz o máximo possível e tem de estar parada às 10:00 de 2026-11-09, com os arquivos da versão 0.6.0 do cliente e do servidor prontos. A execução é limitada pelo relógio, não pelo número de etapas. O prazo corta escopo, nunca revisão ou gate. Consequência registrada: etapa que não fecha até o corte fica fora da 0.6.0 e continua na branch dela.
- Descartadas: limite de 3 etapas (deixaria horas ociosas); build só no fim (uma falha às 8h perderia a entrega); cortar revisões para caber mais etapas.

**Decisão D17 (usuário, por entrevista).** Na 0.6.0 a leitura vetorial nova segue desligada por padrão (`ZENY_SERVER_SYMBOL_COMPOSITION=false`), opcional por configuração. Confirma a D12. Consequência registrada: sem ligar a opção, a leitura de símbolos da 0.6.0 é igual à da 0.5.0.
- Descartada: kit com a opção ligada, sem prova cega (anteciparia a E09, encareceria cada análise, invalidaria caches e deixaria "Suportado" superestimado).

**Decisão D18 (usuário, por entrevista).** A revisão humana da E07 fica para depois da release, sem parar a execução. Em troca, com a opção da D17 desligada, E07 e E08 não podem mudar a saída da análise padrão. Consequência registrada: a E08 se apoia numa E07 ainda não revisada; se a revisão reprovar, as duas são corrigidas numa versão seguinte.
- Descartadas: E07 fora da release até a revisão (a versão sairia sem a ficha do poste); parar na E07 (horas ociosas de madrugada).

**Decisão D19 (arquiteto).** A E07 passa a depender da E06.3.3.2.2 (já na `main`) e abre sem esperar E06.3.4 e E06.3.5, que vão para a trilha B. Consequência registrada: a E07 mede sem as duas classes novas.
- Descartada: fila única E06.3.4, E06.3.5, E07, que gastaria cerca de 7 h da janela antes de abrir a E07.

**Decisão D20 (arquiteto, após builder check).** Cada etapa ou subetapa integra na `main` ao fechar. A release final é gerada em pasta separada e só troca a oficial depois de conferida. Toda parada, exceto push, deploy e segredo, estaciona a etapa.
- Descartadas: integrar tudo no corte (a branch da trilha teria etapa fechada e etapa pela metade juntas, sem commit de corte definido); build final direto na pasta oficial (`build_release` apaga o destino antes de mover o novo, e uma interrupção nesse ponto eliminaria a candidata).

**Etapas novas do roadmap.**
- E18: versão 0.6.0 e candidata de segurança.
- E19: release final 0.6.0, gerada da `main` integrada.

**Marcos da janela** (horário de Brasília, -03:00, conforme o roadmap).

| Quando | Marco |
|---|---|
| 22:00 de 08/11 | Conferência da candidata |
| 05:00 de 09/11 | Não abre etapa nova |
| 06:30 de 09/11 | Corte de trabalho |
| 07:15 de 09/11 | Limite de fechamento |
| 07:45 de 09/11 | Início da E19 |
| 09:00 de 09/11 | Corte do build |
| 09:30 de 09/11 | Sessão encerrada |
| 10:00 de 09/11 | Prazo |

O roadmap prevê recalcular os marcos de 05:00, 06:30, 07:15 e 07:45 conforme o tempo de build medido na E18, se 1,25 vez esse tempo passar de 75 min.

## Contexto

O ZenyProjectHandler interpreta projetos de expansão da rede de distribuição CEMIG a partir de PDFs (cliente Windows e servidor em container). O roadmap de leitura vetorial por poste é executado em etapas por um orquestrador de subagentes. Estas decisões preparam uma execução com prazo fixo para gerar a versão 0.6.0.

Referência das etapas citadas, segundo o roadmap: E06.3.3.2.2 é a gramática de transformador (concluída); E06.3.4, a de estai; E06.3.5, a de equipamento de interrupção; E07, a ficha do poste (associação de texto, símbolo e vão ao poste); E08, a conferência UTM.

## Origem

- Projeto: ZenyProjectHandler (sem nota de projeto no vault).
- Arquivo: `C:\Users\Caio\Desktop\repos\ZenyProjectHandler\docs\roadmap-leitura-vetorial-por-poste.md`.
- Trechos: linhas D16 a D20 de "Hipóteses e decisões em aberto" e bloco "Janela de release 0.6.0" da seção "Protocolo de execução".
- Base Git: `fe42976`, na `main`. A alteração do roadmap ainda não foi commitada.
- Pedido de registro: sessão do orquestrador do projeto, em 2026-11-08.

## Por que registrar

Guarda o raciocínio de uma execução limitada por relógio (o que o prazo pode cortar, o que não pode, e como manter uma entrega de segurança), com as alternativas descartadas e seus motivos.

## Limitações e incertezas

- O conteúdo foi conferido contra o roadmap em sua versão não commitada; o hash `fe42976` não contém estas decisões.
- Dependência de caminho local: o roadmap não foi copiado para o vault e só existe no repositório acima.
- Em 2026-11-08 as decisões eram planos; esta captura não informa se a janela foi cumprida nem se a 0.6.0 foi gerada.
- A explicação das decisões D12 e D13, citadas pela D17, não está nesta captura; consta no mesmo roadmap.

## Possíveis conexões

- [[ZenyProjectHandler - Leitura vetorial por poste e detector local]]
- [[2026-11-05 - ZenyProjectHandler - decisão execução acelerada leitura-vetorial-por-poste - df5912d5]]
- [[2026-11-05 - ZenyProjectHandler - decisão D11 um orquestrador por vez e revisão de D9 e D10 leitura-vetorial-por-poste - d3c635af]]
- [[2026-11-05 - ZenyProjectHandler - decisões D9 e D10 leitura-vetorial-por-poste - 1ecf9413]]
