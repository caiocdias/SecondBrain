# Souls

Repositório oficial das *souls* do Claude Code: subagentes especialistas, cada um com uma identidade (como pensa, o que prioriza, o que recusa) e travas reais (ferramentas e hooks que o Claude Code aplica, não apenas pedidos no prompt). Cada arquivo `.md` em `agents/` é uma soul.

Souls não são conhecimento pessoal: não entram em buscas de conteúdo nem no processamento da Inbox. Como as skills e os protocolos em `99 System/AI/`, servem só como portas de entrada; a fonte da verdade continua nos documentos do vault e nas skills do superpowers. O porquê e as decisões do design estão em [`DESIGN.md`](DESIGN.md); o conceito, em [[Souls - alma personalizada para cada agente de desenvolvimento]].

## As seis souls

Cada soul tem três camadas de proteção, de força diferente: o **bloqueio duro** (ferramenta ausente ou hook `soul_guard.py`) impede a ação na hora; a **auditoria** (`check_test_integrity.py`, rodada pelo orquestrador) aponta depois, pelos commits, o que o bloqueio não alcança; o **julgamento** (a `revisor-seguranca`, ou o usuário) decide sobre cada apontamento.

| Soul | Onde roda | Papel | Bloqueio duro | Auditoria e julgamento |
|---|---|---|---|---|
| `orquestrador` | sessão principal: `claude --agent orquestrador` | Planeja (`superpowers:writing-plans`), executa a etapa com `superpowers:subagent-driven-development`, despacha as outras souls, roda a verificação mecânica dos testes e os scanners de dependência. | Hook: só edita `.md` e arquivos sob `.superpowers/`, nunca sob `.claude/` nem nas souls. `Agent(...)` só despacha as souls listadas. | `ORQUESTRADOR_CODIGO` para commits dele fora disso; a revisora julga. |
| `desenvolvedor` | subagente, por tarefa | Implementa com TDD, seguindo o prompt implementer do superpowers. | Sem `Agent`; hook barra `git push`. | `DEV_TESTE_DO_TESTADOR`, `TESTE_REMOVIDO`, `ASSERCAO_REMOVIDA` e `SKIP_ADICIONADO` apontam mexida em testes; a revisora julga. |
| `testador` | subagente, depois de cada tarefa | Analisa, ataca e completa a suíte de testes. | Hook: Edit, Write e NotebookEdit só em caminhos de teste; sem `Agent`; hook barra `git push`. | `TESTADOR_PRODUCAO` aponta código de produção alterado por outros meios (Bash, por exemplo), além das regras de testes removidos ou pulados; a revisora julga. |
| `revisor-seguranca` | subagente, em cada tarefa e na revisão final | Revisa segurança, supply chain, boas práticas e integridade dos testes. | Ferramentas só de leitura: sem `Edit`, `Write` nem Bash. O orquestrador roda os scanners e anexa as saídas ao pacote de revisão. | O veredito dela vai ao orquestrador e, nas decisões do protocolo, ao usuário. |
| `brain-escriba` | subagente, em projetos fora do vault | Consulta o brain e publica capturas em `00 Inbox/`. | Hook: Write só cria arquivo novo em `00 Inbox/`; Bash só com `date`, `uuidgen`, `ls`, `pwd`, git de leitura e a geração de uuid. | O curador avalia cada captura ao processar a Inbox. |
| `brain-curador` | sessão principal no vault: `claude --agent brain-curador` | Opera o vault em modo curador (processa a Inbox, integra, faz manutenção). | Hook barra `git push`, `git reset --hard`, `git clean -f` e `rm -rf`. | Política de mutação do vault: mudanças estruturais, de schema ou de regra dependem do usuário. |

## Como usar

- **Desenvolvimento:** inicie a sessão do projeto com `claude --agent orquestrador`. Ele confere se `desenvolvedor`, `testador` e `revisor-seguranca` estão instaladas e, se faltar alguma, para e avisa. Não há fallback para os prompts padrão. Vale para qualquer plano do superpowers, com ou sem roadmap (skill `development-roadmap`).
- **Vault:** `claude --agent brain-curador` na raiz do vault é opt-in. Torná-lo o padrão das sessões do vault é decisão futura, porque, como sessão principal, o corpo da soul substitui o system prompt padrão do Claude Code.
- **Fora do vault:** o `brain-escriba` é despachado pelo orquestrador (por exemplo, para a captura de fechamento de etapa); não é iniciado à mão.

## Instalação

O `sync-skills` (`sync-skills.sh` no Linux e no macOS, `sync-skills.ps1` no Windows), instalado por [[99 System/AI/setup]], liga `~/.claude/agents/second-brain-souls` a `99 System/Souls/agents` (junction no Windows). O Claude Code varre `~/.claude/agents/` recursivamente, por isso **só arquivos `.md` de souls podem existir em `agents/`** (mais a subpasta `scripts/`, que não contém `.md`). README e DESIGN ficam fora dela de propósito. Subagentes são carregados no início da sessão. Vault movido: apague à mão o link antigo `~/.claude/agents/second-brain-souls`; o sync o reporta como conflito e não o repara.

## Travas e scripts

- [`agents/scripts/soul_guard.py`](agents/scripts/soul_guard.py): hook `PreToolUse` declarado no frontmatter de cada soul (`soul_guard.py <papel>`). Bloqueia na hora o que o papel não pode fazer (por exemplo, o testador editar fora de arquivos de teste, qualquer papel exceto o orquestrador fazer `git push`, o escriba escrever fora de `00 Inbox/`); as regras de Bash também olham dentro de `bash -c`, `sh -c`, `eval` e de shells alimentados por pipe. Diretórios `spec/`, `specs/` e `testing/` não contam como teste; specs de RSpec contam pelo nome (`*_spec.rb`). Falha fechada: papel ausente ou inválido bloqueia.
- [`agents/scripts/check_test_integrity.py`](agents/scripts/check_test_integrity.py): verificação mecânica da integridade dos testes (testes removidos ou pulados, asserções enfraquecidas, testes do testador alterados pelo desenvolvedor, código de produção alterado pelo testador, código alterado pelo orquestrador). Avisos (commit sem trailer, trailer desconhecido, merge, `.gitattributes`) também vão à revisora para justificar. Rodada pelo orquestrador; a saída entra no pacote de revisão. Atribui commits a papéis pelo trailer `Soul: <nome-da-soul>`, que todo commit feito por uma soul carrega.
- Testes: `python3 -I -m unittest discover -s "99 System/Souls/tests"` e `bash "99 System/Souls/tests/test_sync_souls.sh"`. O teste de fumaça `bash "99 System/Souls/tests/smoke_souls.sh"` chama o Claude de verdade (consome tokens) e roda só à mão.

## Criar uma soul nova

1. Crie `99 System/Souls/agents/<nome>.md` com frontmatter (`name`, `description`, `tools`, `model`, `hooks`) e corpo em português com as seis seções: Quem sou, O que prezo, O que recuso, Como trabalho, Como entrego, Quando paro e pergunto. Corpo curto (até 120 linhas), apontando para as fontes da verdade em vez de copiá-las.
2. Declare as travas no frontmatter: `tools` mínimas e o hook `PreToolUse` com o comando-padrão (`python3 "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/second-brain-souls/scripts/soul_guard.py" <papel>`), sem caminho absoluto de máquina.
3. Se o papel precisa de regras próprias, acrescente-o a `ROLES` e às regras de `soul_guard.py`, com testes em `tests/test_soul_guard.py`.
4. Registre a soul em `tests/test_souls_files.py` e rode os testes.
5. Rode o `sync-skills` ou abra uma nova sessão.

## Pendências

- `sync-skills.ps1` (Windows, junction) ainda não foi testado numa máquina Windows.
- O scanner de dependências (`osv-scanner`) precisa estar instalado em cada máquina, conforme [[99 System/AI/setup]]; sem ele, a revisão final da etapa bloqueia e recomenda o scanner do stack.
