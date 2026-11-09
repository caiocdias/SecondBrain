---
type: capture
status: archived
created: 2026-11-05
capture_id: d3c635af-659c-46d8-ae82-bb5cc92a32e6
---

# ZenyProjectHandler - decisão D11 (um orquestrador por vez) e revisão de D9/D10 do roadmap leitura-vetorial-por-poste

Complementa [[2026-11-05 - ZenyProjectHandler - decisões D9 e D10 leitura-vetorial-por-poste - 1ecf9413]] (`capture_id` 1ecf9413-8dda-4969-9487-6fbd3965658d) e [[2026-11-05 - ZenyProjectHandler - decisão execução acelerada leitura-vetorial-por-poste - df5912d5]] (`capture_id` df5912d5-1f3e-48b4-9f24-fbb0f3e7a419). Aqui só entra o que é novo. A seção "Trechos substituídos" diz o que deixa de valer nas duas.

## Conteúdo capturado

Fonte de todas as linhas citadas: `docs/roadmap-leitura-vetorial-por-poste.md` do ZenyProjectHandler, na working tree de 2026-11-05 (ver "Origem").

### D11: um orquestrador aberto por vez

Decisão do usuário, em 2026-11-05. Frase literal do usuário, repassada pela sessão que pediu esta captura (ela não aparece no roadmap): "nao quero trabalhar com mais de um orquestrador aberto por vez, o paralelismo subsequente tem que ser feito pelo mesmo orquestrador".

Registro no roadmap (linha 96, citação literal): "Decidido em 2026-11-05 pelo usuário: um orquestrador aberto por vez, e o paralelismo entre etapas é feito por ele. Isso substitui as sessões paralelas por trilha da D6."

O desenho que implementa a decisão é do arquiteto (linha 96: "Desenho do arquiteto: ..."). Segundo o chamador, o usuário pode revê-lo. Resumo do agente:

- **Trilhas como agrupamento:** as trilhas A/B/C continuam agrupando as etapas por cadeia de dependência e por arquivos, com os mesmos worktrees e branches (`roadmap/leitura-vetorial-por-poste`, `-b`, `-c`), mas um único orquestrador executa todas (linhas 128–135). Não se abre uma segunda sessão `claude --agent orquestrador` deste roadmap enquanto houver uma aberta (linhas 7 e 128).
- **Etapas simultâneas:** até 2 etapas abertas (`#em-andamento`) ao mesmo tempo, de trilhas diferentes. Cada uma fica no worktree da sua trilha, com plano, ledger e workspace do SDD próprios. Uma trilha nunca tem duas etapas abertas, e as duas etapas correm em paralelo, com despachos em segundo plano (linha 136).
- **Escolha:** sempre que houver vaga e nenhuma parada em curso, a sessão abre a primeira etapa `#pendente` elegível de uma trilha sem etapa aberta. A ordem é A, B, C entre as trilhas (a A é o caminho crítico) e a do documento dentro da trilha (linha 179).
- **Dependência de outra trilha:** só vale se a etapa estiver `#concluida` e integrada na `main` (`git merge-base --is-ancestor`). Se não estiver, a etapa dependente fica para o próximo lote (linha 138).
- **Arquivos disjuntos:** duas etapas abertas nunca editam o mesmo arquivo versionado. Antes da revisão do plano da segunda etapa, a "File Structure" dele é comparada com a do plano da etapa aberta. Se cruzar, o plano é ajustado ou a etapa espera, com ruling. A exceção é o próprio roadmap: cada etapa edita só a sua seção, a sua linha no índice e as hipóteses que fecha (linhas 139, 182 e 187).
- **Depois de compactação:** valem os ledgers dos planos abertos e o `git show <branch>:docs/roadmap-leitura-vetorial-por-poste.md` de cada trilha, não a lembrança da sessão (linha 140).
- **Paradas:** com outra etapa aberta, parar significa não abrir etapa nova, terminar a aberta e então fechar o lote. A sessão não abre etapa nova se as concluídas mais as abertas já somam o limite (linhas 209 e 214; prompt, linha 236).
- **Fim do lote:** merge local na `main` de cada branch de trilha com trabalho no lote, uma por vez, na ordem A, B, C. Cada branch é atualizada com a `main`, que já traz as anteriores, passa no gate e entra com `merge --no-ff`. O push fica com o usuário (linha 220; prompt, linha 237).
- **Prompt de execução** (linhas 225–242): perde o parâmetro de trilha. Citação literal da linha 228: "Esta é a única sessão de orquestrador deste roadmap: execute aqui todas as trilhas, com até 2 etapas abertas ao mesmo tempo, de trilhas diferentes, cada uma no worktree da sua trilha." O limite continua em 3 etapas concluídas (linha 229).
- **"Como usar"** (linha 7) passa a descrever a sessão única com até 2 etapas abertas.

Alternativas descartadas (linha 96):

- uma sessão por trilha (a D6 original), recusada pelo usuário;
- uma sessão sem etapas simultâneas, só com ondas de tarefas, que perderia a E15 e a E17 em paralelo com a E06;
- 3 etapas abertas, porque três planos, três ledgers e três revisões finais no mesmo contexto aumentam a compactação e o risco de confundir etapas, e o teto de ~4 desenvolvedores já não comporta ondas em três etapas.

Risco registrado (linha 96): se a sessão se confundir entre as etapas abertas (despacho no worktree errado, ledger trocado), baixa-se para 1 etapa aberta no prompt, e as ondas de tarefas continuam.

### D9 revista: o orçamento de máquina passa a ser da sessão

A linha 94 agora diz "Decidido em 2026-11-05 pelo arquiteto, revisto com a D11". Citação literal do protocolo (linha 170): "A máquina tem 20 núcleos lógicos, e etapas simultâneas, ondas e laboratório se somam. O teto da sessão é de ~4 desenvolvedores ativos ao mesmo tempo."

Resumo do agente (linhas 94 e 170–175):

- **Teto:** ~4 desenvolvedores ativos na sessão, sem somar sessões. A contagem de "trilhas ativas" entre sessões deixou de existir.
- **Ondas:** com uma etapa aberta, até 3 tarefas por onda (limite da soul); com duas, até 2 em cada. O orquestrador recalcula o limite antes de abrir cada onda, e um número no prompt só baixa esse limite (linha 171; prompt, linha 230).
- **Laboratório:** ocupa a cota da etapa dele, e essa etapa não abre onda de tarefas enquanto ele roda. São de 2 a 3 hipóteses, e 2 quando há duas etapas abertas (linha 172).
- **Processos:** `-n` = 20 ÷ suítes que a sessão roda ao mesmo tempo, arredondado para baixo, com mínimo de 2. O orquestrador informa esse número em cada despacho, e os scripts de corpus usam a mesma conta em `--processos` (linha 173).
- **`.bat`:** usa `-n auto`. Enquanto ele roda, a sessão não despacha suíte nem benchmark novos da outra etapa aberta (linha 174).
- **Leitores visuais:** continuam fora da conta (linha 175).

Alternativas descartadas, reescritas (linha 94):

- limite fixo de ondas, porque a etapa longa ficaria sem ondas depois que a curta fecha;
- nenhum teto, porque duas etapas com ondas de 3 dariam 6 desenvolvedores e ~36 workers do pytest em 20 núcleos, rumo à carga de 60 processos em que a E14 viu workers Qt morrerem (I-2).

Risco registrado (linha 94): um teto baixo demais deixa a E06 com ondas de 2 enquanto a E15 ou a E17 estão abertas. Um teto alto demais traz de volta a instabilidade do Qt sob carga. Nos dois casos, o roadmap manda ajustar a tabela do protocolo.

### D10 revista: a E17 continua na trilha C, aberta pela mesma sessão

Resumo do agente (linhas 95, 976 e 293):

- A E17 continua na trilha C. A trilha A vai direto à E06, no caminho crítico E06 → E07 → E08 → E09, e a E17 abre como segunda etapa quando a E15 fechar (linha 95). Ela abre na mesma sessão, em paralelo com a E06 (linha 976).
- A alternativa "E17 na B depois da E15" continua descartada, agora "porque misturaria cliente e medição na mesma branch, sem ganho de tempo" (linha 95). Antes, o motivo era atrasar a integração da E15. A alternativa "E17 na A antes da E06" segue descartada pelo mesmo motivo: atrasaria o caminho crítico em uma etapa.
- Impacto se errada (linha 95, citação literal): "nenhum além de uma branch a mais no fim do lote. A E17 pode voltar para a A depois da E06 sem mudar o escopo".

Tabela "Janelas" (linhas 288–297). Resumo do agente:

- Cabeçalho: ordem em que a sessão única abre as etapas, até 2 ao mesmo tempo; a elegibilidade real vem das dependências (linha 288).
- Janela 1 (E14 na A, E11 na C): concluída "ainda em duas sessões (antes da D11)", com as duas etapas integradas em `main` (linha 292).
- Janela 2: E06 (A) e E15 (B); depois E17 (C), quando a E15 fechar; E16 (B) quando as folhas chegarem. São duas etapas abertas, com ondas de até 2 em cada. A E06 mexe em `src/` de análise, a E15 em `scripts/benchmark_ficha_poste.py` e a E17 no cliente e em `tests/conftest.py`. Com o limite de 3 etapas, o lote tende a fechar com as três e a integrar as três branches (linha 293).

### Histórico de revisões

A última entrada (linhas 1505–1511) passou a ser a "revisão do arquiteto depois da D8, para alinhar o roadmap às souls novas e à decisão do usuário de ter um orquestrador por vez (D11)". Resumo do agente: uma sessão executa todas as trilhas com até 2 etapas abertas; o prompt perde o parâmetro de trilha; escolha, paradas e fim do lote passam a valer para a sessão; entram o "Orçamento de máquina" (D9) e a E17 na trilha C (D10); "Ondas" vira "Janelas"; o plano traz os campos por tarefa do `orquestrador`.

### Aprendizado possivelmente reutilizável

Interpretação do agente, formulada pelo chamador (não é princípio registrado pelo usuário): com um único orquestrador, o orçamento de máquina fica mais simples e exato, porque a sessão conhece todas as suítes que dispara. O custo é o contexto da sessão, e por isso o limite de etapas simultâneas é baixo (2).

Interpretação do escriba, para o curador: isso refina o aprendizado da 1ecf9413 (limite global à máquina, recalculado ao abrir cada nível). Com sessão única, o limite da sessão coincide com o da máquina, e o recálculo antes de cada onda continua valendo.

## Trechos substituídos

### Na 1ecf9413

- **Seção "D9", citação literal da linha 168:** "... trilhas, ondas e laboratório se somam. O teto é de ~4 agentes escrevendo código ao mesmo tempo, somando todas as trilhas." Fica substituída pela citação da linha 170 acima.
- **Seção "D9", bullets:** substituídos os bullets "Problema" (trilhas × ondas × laboratório), "Teto global" (somando todas as trilhas), "Trilhas ativas" (deixou de existir), "Ondas" (tabela 3/2/1 por trilhas ativas), "Laboratório" (cota da onda; mínimo de 2 mesmo com 3 trilhas) e "Processos" (`-n` = 20 ÷ trilhas ativas × suítes). Também cai a cláusula do `.bat` que tratava como defeito um worker morto com outras trilhas ativas e mandava a carga do momento para o handoff: ela não aparece mais na linha 174 nem em outro ponto do roadmap. O bullet dos leitores visuais segue válido.
- **Seção "D9", alternativas e risco:** "três trilhas com ondas de 3 dariam 9 agentes e ~54 workers" passa a "duas etapas com ondas de 3 dariam 6 desenvolvedores e ~36 workers". "Limite fixo no prompt ... as curtas fecham" passa a "limite fixo de ondas ... a curta fecha". "A E06 sem ondas enquanto E15 e E17 estão abertas" passa a "a E06 com ondas de 2 enquanto a E15 ou a E17 estão abertas".
- **Seção "D10", alternativa "E17 na B depois da E15":** o motivo "atrasaria em uma etapa o fim do lote da B" passa a "misturaria cliente e medição na mesma branch, sem ganho de tempo".
- **Seção "D10", bullet "Custo registrado"** (terceira sessão ao mesmo tempo na janela 2; volta para a A se o usuário preferir duas sessões): substituído pelo impacto da linha 95 citado acima.
- **"Reflexos no índice", janela 2** ("três sessões, e cada trilha começa com ondas de uma tarefa", a E06 recuperando as ondas): substituído pela descrição da linha 293 acima. A janela 1 ganhou a observação "ainda em duas sessões (antes da D11)".
- **"Reflexos no índice", seção da E17** ("ao mesmo tempo que a E06 e a E15", linha 975): substituído pela linha 976 (a mesma sessão a abre quando a E15 fechar, em paralelo com a E06).
- **"Outros ajustes", parágrafo de abertura de "Trilhas e branch":** a seção agora se chama "Trilhas, branch e etapas simultâneas" (D11, linha 126). O parágrafo (linha 128) passa a citar duas trocas em relação ao design: a integração segue a D8, e as sessões paralelas da D6 viram etapas simultâneas na mesma sessão (D11).
- **"Outros ajustes", última entrada do "Histórico de revisões":** substituída pela descrição acima, que agora inclui a D11.
- **"Limitações e incertezas", "tabela 3/2/1":** passa a ser tabela 3/2 (uma ou duas etapas abertas).
- **Números de linha da 1ecf9413:** valem para um estado anterior da working tree. Os atuais são: protocolo de D9 nas linhas 168–175, prompt na linha 230, Trilha C nas linhas 279–286, "Janelas" nas linhas 288–297, seção da E17 na linha 976, "Retomada" na linha 137, plano na linha 187 e histórico nas linhas 1505–1511.

Seguem válidos na 1ecf9413: a motivação da D10 pelo caminho crítico, os reflexos na tabela da Trilha C, o item "Retomada", os campos por tarefa no plano e a relação com a df5912d5 (D8 decidida; merge local no fechamento).

### Na df5912d5

- **D6, "Trilhas paralelas A/B/C":** a frase "Cada uma roda numa sessão `claude --agent orquestrador` própria" fica substituída pela D11. Worktrees e branches por trilha continuam.

## Contexto

Mesma sessão do arquiteto que publicou a 1ecf9413, revisando o roadmap depois da D8. A 1ecf9413 foi publicada antes de a D11 entrar no roadmap: ela não a menciona, e o diff da working tree passou de 38 inserções e 18 remoções (registradas nela) para 63 e 41. O usuário decidiu ter um único orquestrador aberto por vez. O arquiteto redesenhou o protocolo para etapas simultâneas na mesma sessão e reviu D9 e D10 em função disso.

## Origem

- Projeto: ZenyProjectHandler, repositório local `C:\Users\Caio\Desktop\repos\ZenyProjectHandler`. O projeto não tem hub no brain, e esta é uma captura avulsa.
- Arquivo: `C:\Users\Caio\Desktop\repos\ZenyProjectHandler\docs\roadmap-leitura-vetorial-por-poste.md`
  - "Como usar": linha 7;
  - "Hipóteses e decisões em aberto": D9 na linha 94, D10 na 95 e D11 na 96;
  - "Protocolo de execução" → "Trilhas, branch e etapas simultâneas" (D11): linhas 126–143;
  - "Protocolo de execução" → "Orçamento de máquina" (D9): linhas 168–175;
  - "Protocolo de execução" → "Por etapa": passo 1 na linha 179, passo 2 nas linhas 180–183 e passo 4 nas linhas 185–190;
  - "Paradas": linhas 207–216;
  - "Fim do lote": linhas 218–221;
  - "Prompt de execução": linhas 223–242;
  - "Índice de etapas" → tabela "Janelas": linhas 288–297;
  - seção da E17: linha 976;
  - "Histórico de revisões", última entrada: linhas 1505–1511.
- Commit: nenhum. A mudança está na working tree do branch `main`, HEAD `10191eb` (1 commit à frente de `origin/main`). Segundo o `git diff --stat`, o roadmap é o único arquivo alterado, com 63 inserções e 41 remoções.
- Frase literal do usuário: repassada pela sessão chamadora, a partir da conversa de 2026-11-05.
- Data da captura: 2026-11-05.

## Por que registrar

Registra uma decisão de processo do usuário que muda o modelo de execução do roadmap: de várias sessões paralelas para uma sessão com etapas simultâneas. Registra também as revisões de D9 e D10 que decorrem dela e um aprendizado sobre o equilíbrio entre paralelismo e contexto na orquestração de subagentes.

## Limitações e incertezas

- A mudança não estava commitada no momento da captura. Os números de linha valem para a working tree de 2026-11-05 e podem mudar até o commit. O roadmap não foi copiado para o vault.
- A frase literal do usuário veio da sessão chamadora. Não tive acesso à conversa, e o roadmap só traz a paráfrase da linha 96.
- Só o princípio "um orquestrador por vez" é decisão do usuário. O desenho das etapas simultâneas e as revisões de D9 e D10 são do arquiteto, sem registro de aprovação do usuário.
- Comparei com o texto da 1ecf9413, não com uma versão antiga do arquivo: o estado anterior não foi commitado e não pode ser recuperado pelo Git.
- O teto de ~4 desenvolvedores, a tabela 3/2 e as 2 etapas simultâneas ainda não foram testados sob carga real. A primeira validação será a janela 2.

## Possíveis conexões

- [[2026-11-05 - ZenyProjectHandler - decisões D9 e D10 leitura-vetorial-por-poste - 1ecf9413]]
- [[2026-11-05 - ZenyProjectHandler - decisão execução acelerada leitura-vetorial-por-poste - df5912d5]]
- [[ZenyProjectHandler - Leitura vetorial por poste e detector local]] (nota de conhecimento do conteúdo técnico; não trata do processo de execução)
- Temas sem nota no vault (texto simples): ZenyProjectHandler; orquestração de subagentes; paralelismo com git worktrees; souls do Claude Code.
