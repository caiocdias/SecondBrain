# Configuração de máquina

Documento principal sobre como preparar um computador (Linux, macOS ou Windows) para usar este vault com o Claude Code. Executado por uma sessão curadora quando o usuário pede ("configure esta máquina", `/configurar-maquina`) ou aceita a proposta feita ao detectar uma máquina não configurada. Ponto de entrada: [[AGENTS]].

## O que fica onde

| Onde | O quê |
|---|---|
| Vault (Git) | Contrato e protocolos; skills pessoais em `99 System/Skills/`; skills de projeto em `.claude/skills/`; configuração do Obsidian; scripts de sincronização (`sync-skills.sh` e `sync-skills.ps1`). |
| Máquina, fora do Git | Bloco *Second Brain* em `~/.claude/CLAUDE.md`; leitura do vault e hooks em `~/.claude/settings.json`; links em `~/.claude/skills/`. Reconstruídos por este procedimento. |
| Conta do usuário | Skills sincronizadas do claude.ai (`~/.claude/skills/synced/`, voltam após o login); plugins de marketplace (reinstalar com `/plugin`); memória automática do Claude Code. Não fazem parte do vault. |

`~/.claude` significa `$CLAUDE_CONFIG_DIR`, se definida; senão `~/.claude` no Linux e no macOS e `%USERPROFILE%\.claude` no Windows.

## Pré-requisitos

- Claude Code instalado, com login na conta do usuário.
- Vault clonado ou copiado em qualquer pasta. Sugestão: `~/SecondBrain` ou `%USERPROFILE%\SecondBrain`.
- Windows: PowerShell 5.1 ou superior, que já vem no sistema. Não é preciso administrador nem modo de desenvolvedor, porque os links são junctions.
- Obsidian é opcional.

## Detecção

A máquina está configurada quando os três itens existem e apontam para o caminho atual do vault:

1. `~/.claude/CLAUDE.md` contém o bloco entre `<!-- second-brain:begin -->` e `<!-- second-brain:end -->`.
2. `~/.claude/settings.json` tem o vault em `permissions.additionalDirectories` e hooks `SessionStart` e `SessionEnd` que executam o script de sincronização deste vault.
3. Cada skill de `99 System/Skills/` aparece em `~/.claude/skills/` como link para o vault.

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
- Skills pessoais vivem em `<VAULT>/99 System/Skills/`. Crie ou instale novas skills ali (ou em `~/.claude/skills/`, de onde são movidas para o vault automaticamente).
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

### 5. Verificar

- Cada skill de `99 System/Skills/` aparece em `~/.claude/skills/` como link para o vault, e `~/.claude/skills/synced/` não foi alterado.
- Opcional: em outro diretório, `claude -p "liste os nomes das skills disponíveis"` deve incluir as skills do vault.
- Se `git config user.name` ou `user.email` estiverem vazios, informar o usuário; não configurar a identidade sem pedido.

### 6. Relatar

Informar o que foi criado ou alterado, que os hooks valem a partir da próxima sessão e o que fica com o usuário: abrir a pasta como vault no Obsidian (opcional), reinstalar plugins de marketplace e conferir que as skills do claude.ai voltaram após o login.

## Vault movido ou máquina desativada

- **Vault movido**: repetir o procedimento, que substitui os caminhos antigos. Apagar de `~/.claude/skills/` os links que apontam para o caminho antigo; o script só limpa links do vault atual.
- **Desativar**: remover o bloco do `CLAUDE.md`, as entradas de `settings.json` e os links em `~/.claude/skills/`. As skills continuam no vault.

## Limites

- Alterar apenas os itens descritos aqui; não mexer em outras configurações, outras skills, `synced/` ou plugins.
- Nunca registrar credenciais no vault nem nos arquivos de configuração.
- Não fazer push.
