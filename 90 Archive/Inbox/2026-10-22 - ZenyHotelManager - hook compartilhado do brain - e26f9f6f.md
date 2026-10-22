---
type: capture
status: archived
created: 2026-10-22
capture_id: e26f9f6f-f541-4339-bc7d-b74de3e5599f
---
# ZenyHotelManager - hook compartilhado do brain

## Conteúdo capturado

Fatos (sessão curadora do vault, 2026-10-22, a pedido do usuário):

- **Decisão do usuário** (entrevista com opção recomendada): o hook que carrega o brain nos projetos passa a ser um script único na skill `development-roadmap` (`99 System/Skills/development-roadmap/scripts/load-brain.py`), e o ZenyHotelManager foi migrado para ele na mesma sessão ("Sim, agora").
- **Repositório `/home/caio/repos/ZenyHotelManager`** (sem commit):
  - `.claude/settings.json`: `SessionStart` e `SubagentStart` rodam `python3 -I "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/development-roadmap/scripts/load-brain.py" ZenyHotelManager <evento>`;
  - `.claude/brain/load-brain.py` removido;
  - `CLAUDE.md`: a linha exigida passou de `ZENY-BRAIN: carregado` para `BRAIN: carregado (ZenyHotelManager)`; sem ela, ou com `BRAIN: indisponível`, o agente para e pede `/configurar-maquina` numa sessão do vault (ou `SECOND_BRAIN_VAULT`);
  - `README.md`, `docs/roadmaps/README.md` e `docs/roadmaps/roadmap-m5-recepcao-fnrh.md` passaram a citar o hook do `.claude/settings.json` com o `load-brain.py` da skill.
- **Testado:** o comando do `settings.json` pelo bash devolveu `BRAIN: carregado (ZenyHotelManager)` (~7.100 caracteres de contexto); numa sessão `claude -p --model haiku` no repositório, a sessão e um subagente `general-purpose` disparado por ela tinham `BRAIN: carregado (ZenyHotelManager)` no contexto.
- O script acha o hub pelo nome exato `10 Projects/ZenyHotelManager.md` (ou pelos `aliases`), e não mais pela primeira nota de projeto cujo nome contenha o projeto.
- A skill `development-roadmap` passou a registrar projetos no brain e a manter o `CLAUDE.md` enxuto (`references/brain.md`); o template do roadmap ganhou o bloco "Second Brain" no protocolo. Isso responde à pergunta aberta do hub sobre a skill ainda mandar registrar no `CLAUDE.md`.

## Contexto

Continuação da migração do `CLAUDE.md` do ZenyHotelManager para o brain ([[2026-10-22 - ZenyHotelManager - migração do CLAUDE.md para o brain - índice e decisões - 03d0ed3e]]), depois da fase 2 ([[2026-10-22 - ZenyHotelManager - atualização migração do CLAUDE.md fase 2 - cad5c5ad]]).

## Origem

Sessão do Claude Code iniciada na raiz do vault (curador), 2026-10-22, pedido do usuário para generalizar a skill `development-roadmap` e migrar o Zeny para o hook compartilhado.

## Por que registrar

O hub [[ZenyHotelManager]] cita o hook antigo e a pergunta aberta sobre a skill; esta captura atualiza o Estado, os Próximos passos e as Perguntas abertas.

## Limitações e incertezas

- As alterações no repositório estão sem commit.
- O comando do hook não foi testado no Windows.

## Possíveis conexões

- [[ZenyHotelManager]]
