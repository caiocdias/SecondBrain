# Configuração de máquina

Documento principal sobre como preparar um computador (Linux, macOS ou Windows) para usar este vault com o Claude Code. Executado por uma sessão curadora quando o usuário pede ("configure esta máquina", `/configurar-maquina`) ou aceita a proposta feita ao detectar uma máquina não configurada. Ponto de entrada: [[AGENTS]].

## O que fica onde

| Onde | O quê |
|---|---|
| Vault (Git) | Contrato e protocolos; skills pessoais e plugins locais em `99 System/Skills/`; registro dos plugins de marketplace em `99 System/Skills/plugins.txt`; souls (subagentes) em `99 System/Souls/agents/`; skills de projeto em `.claude/skills/`; configuração do Obsidian; scripts de sincronização (`sync-skills.sh` e `sync-skills.ps1`). |
| Máquina, fora do Git | Bloco *Second Brain* em `~/.claude/CLAUDE.md`; leitura do vault e hooks em `~/.claude/settings.json`; links em `~/.claude/skills/`; link `~/.claude/agents/second-brain-souls` para as souls do vault; scanners de dependências instalados (`osv-scanner`); arquivos dos plugins instalados (`~/.claude/plugins/`). Reconstruídos por este procedimento. |
| Repositórios de projeto | `.claude/settings.json` com o hook que carrega o projeto do brain, chamando `load-brain.py` da skill `development-roadmap` pelo link em `~/.claude/skills/` (ver [[99 System/AI/processing]], "Projetos com hub"). Funciona em qualquer máquina configurada por este procedimento. |
| Conta do usuário | Skills e plugins sincronizados do claude.ai (`~/.claude/skills/synced/` e `~/.claude/plugins/synced/`, voltam após o login); memória automática do Claude Code. Não fazem parte do vault. |

O `plugins.txt` registra quais plugins usar, não os arquivos deles: o Claude Code baixa e atualiza cada plugin a partir do marketplace. Plugins instalados no escopo de usuário entram no registro automaticamente pelo script de sincronização; o registro só cresce, e remover um plugin dele é decisão manual do usuário.

`~/.claude` significa `$CLAUDE_CONFIG_DIR`, se definida; senão `~/.claude` no Linux e no macOS e `%USERPROFILE%\.claude` no Windows.

## Pré-requisitos

- Claude Code instalado, com login na conta do usuário.
- Vault clonado ou copiado em qualquer pasta. Sugestão: `~/SecondBrain` ou `%USERPROFILE%\SecondBrain`.
- Windows: PowerShell 5.1 ou superior, que já vem no sistema. Não é preciso administrador nem modo de desenvolvedor, porque os links são junctions.
- Python 3 no PATH como `python3`: usado pelos scripts da skill `development-roadmap` e pelo hook do brain nos repositórios de projeto. No Windows, o comando do hook (`python3` e `${CLAUDE_CONFIG_DIR:-$HOME/.claude}`) pressupõe que o Claude Code rode hooks num shell POSIX como o Git Bash; ainda não foi verificado lá.
- Obsidian é opcional.
- Scanners de vulnerabilidade de dependências (`osv-scanner`, opcional) usados pela soul `revisor-seguranca`; ver o passo 6.

## Detecção

A máquina está configurada quando os itens abaixo existem e apontam para o caminho atual do vault:

1. `~/.claude/CLAUDE.md` contém o bloco entre `<!-- second-brain:begin -->` e `<!-- second-brain:end -->`.
2. `~/.claude/settings.json` tem o vault em `permissions.additionalDirectories` e hooks `SessionStart` e `SessionEnd` que executam o script de sincronização deste vault.
3. Cada skill de `99 System/Skills/` aparece em `~/.claude/skills/` como link para o vault.
4. Cada plugin de `99 System/Skills/plugins.txt` aparece em `claude plugin list`.
5. `~/.claude/agents/second-brain-souls` existe como link para `99 System/Souls/agents` do vault.
6. `python3 --version` responde.
7. `osv-scanner --version` responde (opcional; sem ele a soul `revisor-seguranca` declara a lacuna).

Se algum item faltar ou apontar para outro caminho (vault movido), a sessão curadora informa o usuário e executa o procedimento após confirmação.

## Procedimento

### 1. Identificar o ambiente

- Sistema operacional.
- Caminho absoluto do vault: a raiz da sessão curadora (`pwd` ou `(Get-Location).Path`). Abaixo, `<VAULT>`; no Windows, com barras invertidas.
- Diretório de configuração do Claude Code (ver acima).

### 2. Bloco global em `~/.claude/CLAUDE.md`

Criar o arquivo se não existir. Se o bloco já existir, substituir apenas o trecho entre os marcadores; senão, acrescentá-lo ao final. Preservar todo o resto do arquivo. Substituir `<VAULT>` pelo caminho absoluto.

```markdown
<!-- second-brain:begin -->
## Second Brain

Meu Second Brain pessoal é um vault Obsidian em Markdown em `<VAULT>`. Guarda conhecimento, fontes, projetos e metodologias de qualquer área da vida, e é o repositório oficial das minhas skills do Claude Code.

- Quando eu falar em "meu brain", "Second Brain", salvar, registrar ou capturar algo, consultar meu conhecimento ou usar minha metodologia, use a skill `second-brain`.
- Em sessões iniciadas fora do vault você é agente externo: pode ler notas pertinentes e só cria capturas novas em `<VAULT>/00 Inbox/`. Não processa a Inbox nem altera notas existentes. Contrato: `<VAULT>/AGENTS.md` e `<VAULT>/99 System/AI/external-agents.md`.
- Skills pessoais vivem em `<VAULT>/99 System/Skills/`. Crie ou instale novas skills ali (ou em `~/.claude/skills/`, de onde são movidas para o vault automaticamente). Plugins instalados no escopo de usuário ficam registrados em `<VAULT>/99 System/Skills/plugins.txt`.
- Configuração desta máquina: `<VAULT>/99 System/AI/setup.md`.
<!-- second-brain:end -->
```

### 3. `~/.claude/settings.json`

Ler o arquivo (ou partir de `{}` se não existir) e mesclar, sem remover nada:

- `permissions.additionalDirectories`: acrescentar `<VAULT>`, se ausente.
- `hooks.SessionStart` e `hooks.SessionEnd`: acrescentar a entrada abaixo, se nenhuma entrada já executar o `sync-skills` deste vault. Entrada que aponte para outro caminho do vault (vault movido) é substituída.

Linux e macOS:

```json
{
  "hooks": [
    {
      "type": "command",
      "command": "\"<VAULT>/99 System/Skills/sync-skills.sh\"",
      "timeout": 15
    }
  ]
}
```

Windows (forma de execução direta, sem shell; `-ExecutionPolicy Bypass` evita o bloqueio padrão a scripts):

```json
{
  "hooks": [
    {
      "type": "command",
      "command": "powershell.exe",
      "args": ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "<VAULT>\\99 System\\Skills\\sync-skills.ps1"],
      "timeout": 15
    }
  ]
}
```

Validar o JSON depois de editar (`jq . ~/.claude/settings.json` ou `Get-Content $HOME\.claude\settings.json -Raw | ConvertFrom-Json`). Um `settings.json` inválido desativa todas as configurações do arquivo.

### 4. Ativar as skills

- Linux e macOS: `chmod +x "<VAULT>/99 System/Skills/sync-skills.sh"` e executar o script.
- Windows: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<VAULT>\99 System\Skills\sync-skills.ps1"`.

### 5. Instalar os plugins registrados

Ler `99 System/Skills/plugins.txt` (ignorar linhas com `#`). Cada linha tem `<plugin>@<marketplace> <origem do marketplace>`. Comparar com `claude plugin list --json` e `claude plugin marketplace list` e, para cada plugin que falte:

1. Se o marketplace não estiver configurado: `claude plugin marketplace add <origem>`.
2. `claude plugin install <plugin>@<marketplace>` (escopo de usuário, o padrão).

Se a instalação pedir confirmação de um comando declarado pelo marketplace ou opções de configuração (`--config`), mostrar ao usuário e só prosseguir com a resposta dele; nunca passar `-y` por conta própria. Origem que seja um caminho local de outra máquina não funciona aqui: relatar e pedir ao usuário a origem correta. Falha em um plugin não interrompe os demais.

### 6. Souls e scanners

- Souls: o script de sincronização do passo 4 cria o link `~/.claude/agents/second-brain-souls` para `<VAULT>/99 System/Souls/agents` (junction no Windows). Link para outro lugar ou diretório real com esse nome é conflito: informar o usuário e não alterar. Subagentes são carregados no início da sessão; valem a partir da próxima.
- Scanners: conferir `osv-scanner --version`. Se faltar, propor a instalação pelo método oficial (https://google.github.io/osv-scanner/installation/) e instalar **somente com a confirmação do usuário**, como em qualquer instalação de software. Se ele recusar, registrar no relatório; as demais ferramentas da tabela de `revisor-seguranca` (npm audit, pip-audit, dependency-check) são instaladas por projeto, não aqui.

### 7. Verificar

- Cada skill de `99 System/Skills/` aparece em `~/.claude/skills/` como link para o vault, e `~/.claude/skills/synced/` não foi alterado.
- Cada plugin de `plugins.txt` aparece em `claude plugin list`.
- `ls ~/.claude/agents/second-brain-souls/` lista as souls (arquivos `.md` e `scripts/`).
- `osv-scanner --version` responde; se não, informar que o scanner não está instalado.
- Hook do brain: para um projeto com hub em `10 Projects/`, `python3 -I ~/.claude/skills/development-roadmap/scripts/load-brain.py <Projeto>` imprime `BRAIN: carregado (<Projeto>)`. Sem Python 3, informar o usuário: os repositórios com o hook vão parar pedindo a configuração.
- Opcional: em outro diretório, `claude -p "liste os nomes das skills disponíveis"` deve incluir as skills do vault.
- Se `git config user.name` ou `user.email` estiverem vazios, informar o usuário; não configurar a identidade sem pedido.

### 8. Relatar

Informar o que foi criado ou alterado, quais plugins foram instalados ou falharam, que hooks e plugins valem a partir da próxima sessão e se o scanner foi instalado ou recusado, e o que fica com o usuário: abrir a pasta como vault no Obsidian (opcional) e conferir que as skills do claude.ai voltaram após o login.

## Vault movido ou máquina desativada

- **Vault movido**: repetir o procedimento, que substitui os caminhos antigos. Apagar de `~/.claude/skills/` os links que apontam para o caminho antigo; o script só limpa links do vault atual.
- **Desativar**: remover o bloco do `CLAUDE.md`, as entradas de `settings.json`, os links em `~/.claude/skills/` e o link `~/.claude/agents/second-brain-souls`; desinstalar plugins é opcional. Skills e registro de plugins continuam no vault.

## Limites

- Alterar apenas os itens descritos aqui; não mexer em outras configurações, outras skills, outros agentes de `~/.claude/agents/` ou `synced/`, e não instalar plugins que não estejam em `plugins.txt`. Instalar scanner só com confirmação do usuário.
- Nunca registrar credenciais no vault nem nos arquivos de configuração.
- Não fazer push.
