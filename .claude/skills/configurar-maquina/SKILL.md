---
name: configurar-maquina
description: Configura este computador (Linux, macOS ou Windows) para usar o Second Brain com o Claude Code — bloco do vault em ~/.claude/CLAUDE.md, leitura do vault e hooks em ~/.claude/settings.json, links das skills pessoais e das souls (subagentes) em ~/.claude/agents, scanner de dependências (osv-scanner, com confirmação), instalação dos plugins registrados no brain e conferência do hook que os repositórios de projeto usam para carregar o brain. Use quando o usuário pedir para configurar a máquina, instalar ou reinstalar o brain, ou depois de clonar ou mover o vault. Só opera em sessão iniciada na raiz do vault.
---

# Configurar máquina

`99 System/AI/setup.md` é o protocolo oficial. Esta skill resume a ordem de execução; em caso de divergência, siga o protocolo.

1. Confirme que a sessão foi iniciada na raiz do vault (AGENTS.md e `99 System/AI/` no diretório principal). Caso contrário, pare e explique que a configuração exige uma sessão iniciada no vault.
2. Leia `99 System/AI/setup.md`.
3. Identifique o sistema operacional, o caminho absoluto do vault e o diretório de configuração do Claude Code.
4. Faça a detecção e mostre ao usuário o que falta ou aponta para outro caminho. Se a skill foi acionada por pedido direto, siga; se foi uma proposta sua, confirme antes.
5. Execute os passos do protocolo: bloco do `CLAUDE.md`, mescla do `settings.json` (validando o JSON), script de sincronização (que também liga as souls em `~/.claude/agents/second-brain-souls`), instalação dos plugins de `99 System/Skills/plugins.txt`, souls e scanners (`osv-scanner` só instalado com confirmação do usuário), verificação (inclusive Python 3 e o hook do brain usado pelos repositórios de projeto).
6. Relate o que mudou, quais plugins foram instalados ou falharam e o que fica com o usuário.
