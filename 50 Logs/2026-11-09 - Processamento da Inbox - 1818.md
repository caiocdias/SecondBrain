---
type: log
created: 2026-11-09
---
# Processamento da Inbox — 2026-11-09 18:18

Estado do lote: concluído

## Capturas

### 9f02405c-a73b-44f0-8f8c-5fb75860aa05
- Captura: [[2026-11-05 - ZenyHotelManager - atualização m5-recepcao-fnrh E07 - 9f02405c]] (preservada em 90 Archive/Inbox/)
- Ação: integrada, com os trechos que a captura c889f886 declara substituídos trocados nas notas de tema e mantidos, com nota do curador, em Estado por marco
- Notas criadas: [[ZenyHotelManager - Módulo fnrh]]
- Notas enriquecidas: [[ZenyHotelManager]], [[ZenyHotelManager - Estado por marco]], [[ZenyHotelManager - Segurança, autenticação e autorização]], [[ZenyHotelManager - Convenções de API]], [[ZenyHotelManager - Módulo guests]]
- Normalizações: status alterado para archived ao mover para 90 Archive/Inbox/
- Pendências: decisões (a) a (d), (f), (g), (h) e (j) do lote E07 sem confirmação do usuário; revisão humana de E07 e E13; comportamento real do Serpro só na E09.
- Estado: concluída

### c889f886-0719-4f28-984e-f2ef23ed9520
- Captura: [[2026-11-06 - ZenyHotelManager - atualização revisão de arquitetura dos roadmaps - c889f886]] (preservada em 90 Archive/Inbox/)
- Ação: integrada
- Notas criadas: nenhuma
- Notas enriquecidas: [[ZenyHotelManager]], [[ZenyHotelManager - Estado por marco]], [[ZenyHotelManager - Módulo fnrh]], [[ZenyHotelManager - Arquitetura e estrutura de módulos]], [[ZenyHotelManager - Módulo guests]], [[ZenyHotelManager - Docker, observabilidade e CI]], [[ZenyHotelManager - Ambiente, banco, chaves e build]], [[ZenyHotelManager - Eventos e jobs]]
- Normalizações: status alterado para archived ao mover para 90 Archive/Inbox/
- Pendências: decisões do arquiteto R7 a R13 e R16 revisáveis; oferta de dividir o M8 em dois arquivos sem resposta; o `revisor-arquitetura` não releu o resultado da revisão; alterações sem commit no repositório na data da conferência.
- Estado: concluída

## Observações

- 2 capturas pendentes, ambas do ZenyHotelManager; nenhum capture_id aparecia em logs, proveniências ou em `90 Archive/Inbox/`. Nenhum lote anterior em andamento.
- Substituições feitas no texto literal, como as capturas indicam: em Módulo guests, a frase do expurgo; em Ambiente, banco, chaves e build, as referências E11 da dívida das migrações e do passo 3 das chaves; no hub, D1–D17 passou a D1–D19 e as linhas do M5 e do Git. Registradas em nota do curador ou na Proveniência de cada nota.
- Referência conferida fora do vault, só leitura, por `git` em `/home/caio/repos/ZenyHotelManager`: `main` em `ca9f9e2`, `origin/main` em `15bbcdb` (referência local, sem fetch) e as alterações da revisão ainda sem commit, tudo como a captura c889f886 diz.
- Divergência em relação à captura c889f886: ela diz que a branch `roadmap/m5-recepcao-fnrh` não existe mais; hoje a branch existe em worktree próprio, 19 commits à frente da `main`, ponta `e718190` (2026-11-06 21:07, "Registra o ponto de retomada da E15"), e seu roadmap marca a E15 `#em-andamento`. A branch foi recriada depois da captura (publicada às 17:45). Não há captura dessa execução; o fato está registrado como conferência do curador no hub e em Estado por marco.
- Não conferidos pelo curador: código, `docs/fnrh/api-fnrh-v2.4.md`, o conteúdo da spec da revisão e os resíduos de linha citados na captura c889f886.
- O hub [[ZenyHotelManager]] tem 11.042 caracteres, acima do limite de ~8.000 de `processing.md` (era 9.311 antes deste lote). O excesso já estava registrado no lote de 2026-11-04. Reduzi-lo exige encurtar a Proveniência (2.315 caracteres) ou o índice de notas, o que fica como proposta ao usuário.
- Validação: nenhum link interno quebrado nas notas alteradas, nas capturas arquivadas e neste log (conferido antes do fechamento deste log; seus links são os mesmos das notas). O frontmatter foi conferido por expressão regular linha a linha, não por um parser YAML.
- `.obsidian/graph.json` já estava modificado antes do lote e não faz parte dele.
