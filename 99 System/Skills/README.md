# Skills

Repositório oficial das skills pessoais do Claude Code. Cada subpasta com um `SKILL.md` é uma skill disponível em todas as sessões, por qualquer projeto, pelo `/nome-da-skill` ou por acionamento automático.

Skills não são conhecimento pessoal: não entram em buscas de conteúdo nem no processamento da Inbox. Como os protocolos em `99 System/AI/`, servem só como portas de entrada; a fonte da verdade continua nos documentos do vault.

## Como funciona

O Claude Code carrega as skills pessoais de `~/.claude/skills/`. Lá, cada skill deste diretório aparece como um link simbólico para cá, então editar aqui é editar a skill ativa.

O script de sincronização roda nos hooks `SessionStart` e `SessionEnd` de `~/.claude/settings.json`, instalados por [[99 System/AI/setup]]: [`sync-skills.sh`](sync-skills.sh) no Linux e no macOS e [`sync-skills.ps1`](sync-skills.ps1) no Windows, onde os links são junctions. Os dois seguem as mesmas regras:

1. Skill nova instalada ou criada diretamente em `~/.claude/skills/` é movida para cá e substituída por um link.
2. Skill criada aqui ganha o link em `~/.claude/skills/`.
3. Links de skills apagadas daqui são removidos.

Conflitos de nome (a mesma skill nos dois lugares sem link) não são resolvidos automaticamente; o script avisa no início da sessão.

## Criar ou instalar uma skill

- Crie a pasta diretamente aqui (`99 System/Skills/<nome>/SKILL.md`) ou em `~/.claude/skills/<nome>/`; no segundo caso, ela é trazida para cá na próxima abertura ou encerramento de sessão.
- Para ativar sem esperar uma nova sessão, rode o script: `"99 System/Skills/sync-skills.sh"` ou, no Windows, `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "99 System\Skills\sync-skills.ps1"`.

## Plugins

- **Plugins locais**, criados com `claude plugin init` (pasta com `.claude-plugin/plugin.json`), são tratados como skills: vivem aqui e são ligados a `~/.claude/skills/`.
- **Plugins de marketplace** (`/plugin install`) continuam com os arquivos em `~/.claude/plugins/`, gerenciados e atualizados pelo Claude Code. O vault guarda só o registro em [`plugins.txt`](plugins.txt), uma linha `<plugin>@<marketplace> <origem do marketplace>` por plugin. O script acrescenta ali todo plugin instalado no escopo de usuário; para deixar de reinstalar um plugin em máquinas novas, apague a linha à mão.
- Numa máquina nova, a configuração ([[99 System/AI/setup]]) instala todos os plugins registrados.

## O que fica fora deste diretório

- `~/.claude/skills/synced/` e `~/.claude/plugins/synced/`: skills e plugins ativados no claude.ai, sincronizados e gerenciados pelo próprio Claude Code (`anthropic-skills:*`).
- Arquivos dos plugins de marketplace, em `~/.claude/plugins/` (o registro deles fica em `plugins.txt`).
- Skills de projeto, como `processar-inbox` em `.claude/skills/` do vault, que valem só para sessões iniciadas no próprio projeto.
