# Projeto no Second Brain

Todo projeto em que esta skill trabalha guarda o conhecimento técnico no Second Brain do usuário, e não no `CLAUDE.md`. O repositório fica com um `CLAUDE.md` enxuto e com um hook que injeta em cada sessão e subagente a nota de projeto (o **hub**) e as capturas pendentes do projeto.

O vault é o do bloco *Second Brain* de `~/.claude/CLAUDE.md`. Uma sessão iniciada no repositório é **agente externo** do vault: lê notas e só cria capturas novas em `00 Inbox/`, seguindo `99 System/AI/ingestion.md` e `99 System/AI/external-agents.md` do vault (skill `second-brain`). Nunca edita o hub, as notas de tema nem capturas existentes. Quem cria o hub e integra as capturas é o curador, numa sessão do vault (`/processar-inbox`), conforme a seção "Projetos com hub" de `99 System/AI/processing.md`.

## Nome do projeto

É o argumento do hook e o nome do hub (`10 Projects/<Projeto>.md`). Use o que o `.claude/settings.json` do repositório já passa ao `load-brain.py`; sem hook, use o nome da pasta raiz do repositório, sem espaços. Confirme com o usuário na proposta de registro.

## Verificação (toda execução da skill)

Confira, só lendo:

| # | Item | Como |
|---|---|---|
| 1 | Vault acessível | bloco *Second Brain* em `~/.claude/CLAUDE.md` e `AGENTS.md` no caminho dele |
| 2 | Hub existe | `10 Projects/<Projeto>.md` com `type: project`, ou nota `type: project` com `<Projeto>` nos `aliases` |
| 3 | Hook instalado | `.claude/settings.json` do repositório com `SessionStart` e `SubagentStart` chamando `load-brain.py <Projeto>` da skill (comando abaixo) |
| 4 | `CLAUDE.md` enxuto | tem a seção "Conhecimento do projeto no Second Brain" e nada de referência técnica além das seções do modelo abaixo |
| 5 | Hook responde | `python3 -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/development-roadmap/scripts/load-brain.py" <Projeto>` imprime `BRAIN: carregado (<Projeto>)` |

- **Item 1 falhou:** avise o usuário (a máquina se configura numa sessão do vault com `/configurar-maquina`) e siga só com o roadmap.
- **Todos ok:** siga. Leia o hub, as notas de tema ligadas ao escopo do roadmap e as capturas pendentes que o hook lista.
- **Algum dos itens 2 a 5 falhou:** proponha ao usuário o registro (ou só a parte que falta) por entrevista com opção recomendada, dizendo o que muda no repositório e o que vai para a Inbox. Com o ok, faça a migração abaixo antes de escrever o roadmap. Sem o ok, siga só com o roadmap e registre "projeto fora do brain" na resposta final.
- **Hub ausente, mas capturas de registro do projeto já pendentes:** o registro já foi feito e espera o curador. Não capture de novo; peça ao usuário para processar a Inbox.

## Migração

1. **Inventário.** Leia o `CLAUDE.md` inteiro e anote o commit atual (`git rev-parse --short HEAD`). Separe as linhas em:
   - **ficam** no `CLAUDE.md` (seções do modelo abaixo);
   - **vão para o brain**: estado por marco ou etapa, arquitetura detalhada, convenções, banco, segurança, integrações, um bloco por módulo, ou qualquer referência técnica acumulada.
2. **Capturas** em `00 Inbox/` do vault, com publicação segura (temporário e renomeação sem sobrescrever) e `capture_id` próprio:
   - **uma captura-índice** `<Projeto> - registro no brain - índice e decisões`, com: o pedido literal do usuário para registrar o projeto (o curador só cria projetos a pedido); o objetivo do projeto; o repositório local e os documentos de lá; o estado atual em poucas linhas; as decisões do usuário; a tabela das capturas de tema (link, `capture_id`, nota sugerida `<Projeto> - <Tema>`); e o lembrete de manter o hub abaixo de ~8.000 caracteres, porque o hook o injeta inteiro;
   - **uma captura por tema ou módulo** `<Projeto> - <Tema>`, com o texto **literal** das linhas do `CLAUDE.md` (arquivo, linhas e commit na Origem), sem resumir: caminhos, classes e códigos de erro são usados pelos agentes ao editar o código.
   
   Projeto novo ou sem referência técnica: basta a captura-índice. Confira por script que toda linha não vazia do `CLAUDE.md` antigo está numa captura ou no `CLAUDE.md` novo.
3. **Hook.** Mescle no `.claude/settings.json` do repositório, sem remover nada, e valide o JSON:

   ```json
   {
     "hooks": {
       "SessionStart": [{"hooks": [{"type": "command", "timeout": 15,
         "command": "python3 -I \"${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/development-roadmap/scripts/load-brain.py\" <Projeto> SessionStart"}]}],
       "SubagentStart": [{"hooks": [{"type": "command", "timeout": 15,
         "command": "python3 -I \"${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/development-roadmap/scripts/load-brain.py\" <Projeto> SubagentStart"}]}]
     }
   }
   ```

   O script é único e mora na skill: não o copie para o repositório. Se o repositório tiver uma cópia antiga (por exemplo, `.claude/brain/load-brain.py`), troque a chamada por esta e remova a cópia.
4. **`CLAUDE.md` enxuto** no lugar do antigo, conforme o modelo abaixo. O texto antigo continua no histórico do Git (cite o commit na captura-índice).
5. **Teste.** Rode o comando do item 5 da verificação e confira `BRAIN: carregado (<Projeto>)`, as capturas novas listadas e, se o hub ainda não existe, o aviso correspondente. O hook vale a partir da próxima sessão.
6. **Relate**: caminhos das capturas, arquivos alterados no repositório (sem commit) e que o usuário precisa processar a Inbox numa sessão do vault para criar o hub e as notas de tema.

## Modelo do `CLAUDE.md` enxuto

Seções, nesta ordem, só com o que o agente precisa antes de ler o brain:

1. **Projeto**: o que é, o que o repositório contém e onde ficam spec, arquitetura e roadmaps; idioma de documentação e de código.
2. **Conhecimento do projeto no Second Brain (obrigatório)**, com este texto adaptado:

   ```markdown
   Este arquivo guarda só o mínimo. A referência técnica do projeto vive no Second Brain: na nota de projeto `<Projeto>` em `10 Projects/` (o hub) e nas notas de tema ligadas a ela.

   - **Hook obrigatório:** `.claude/settings.json` roda o `load-brain.py` da skill `development-roadmap` em `SessionStart` e `SubagentStart`, que injeta o hub e as capturas pendentes do projeto com a linha `BRAIN: carregado (<Projeto>)`. Se essa linha não estiver no seu contexto, ou aparecer `BRAIN: indisponível`, **pare antes de qualquer alteração** e peça ao usuário para configurar a máquina (`/configurar-maquina` numa sessão do vault). Não trabalhe de memória.
   - **Antes de mexer num tema**, leia a nota de tema dele (link no hub) e as capturas pendentes do projeto que tratem dele: são mais novas que as notas. Vale também para subagentes.
   - **Limites:** sessões deste repositório são agente externo do vault: leem notas e só criam capturas novas em `00 Inbox/`; nunca editam notas nem capturas existentes.
   - **Atualização:** ao fim de cada etapa de roadmap que mude algo descrito no brain, publique a captura `<Projeto> - atualização <slug> Eyy` com o texto novo ou alterado de cada nota afetada, dizendo qual nota ele substitui ou complementa. "Seção X do `CLAUDE.md`" num roadmap ou handoff antigo é a nota de tema correspondente.
   ```

3. **Stack e comandos**: versões principais e a tabela de comandos oficiais (build, teste, lint, subir o ambiente). Os roadmaps mandam lê-los aqui.
4. **Como trabalhar com os roadmaps**: onde ficam, a regra de tags e handoffs, e a validação com `check_roadmap.py`.
5. **Decisões do usuário**: entrevista com opção recomendada.
6. **Git**: branch de trabalho, commit e push só a pedido.

Mire em menos de ~100 linhas. Qualquer outra coisa vai para uma nota de tema.

## Durante a execução do roadmap

A sessão que executa o roadmap não carrega esta skill: as regras abaixo estão no "Protocolo de execução" do template.

- O orquestrador publica a captura de atualização no fechamento de cada etapa que mudou algo descrito no brain, inclusive o estado (marco ou etapa concluída). Implementadores e revisores não publicam capturas.
- Etapas e handoffs nunca mandam "atualizar o `CLAUDE.md`" com referência técnica; só a tabela de comandos e as seções do modelo mudam lá.
