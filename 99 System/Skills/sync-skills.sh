#!/usr/bin/env bash
# Mantém ~/.claude/skills/ apontando para as skills versionadas neste diretório do vault.
# Executado pelos hooks SessionStart e SessionEnd de ~/.claude/settings.json; pode ser rodado à mão.
#
# 1. Skill nova instalada ou criada diretamente em ~/.claude/skills/ é movida para cá e
#    substituída por um link simbólico.
# 2. Skill criada aqui sem link em ~/.claude/skills/ ganha o link.
# 3. Links para skills removidas daqui são apagados.
#
# ~/.claude/skills/synced/ (skills sincronizadas do claude.ai) é gerenciado pelo Claude Code e fica de fora.

set -u

VAULT_SKILLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_SKILLS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"

mkdir -p "$USER_SKILLS"
moved=()
linked=()
conflicts=()

for dir in "$USER_SKILLS"/*/; do
  dir="${dir%/}"
  name="$(basename "$dir")"
  [ "$name" = "synced" ] && continue
  [ -L "$dir" ] && continue
  [ -f "$dir/SKILL.md" ] || continue
  if [ -e "$VAULT_SKILLS/$name" ]; then
    conflicts+=("$name")
    continue
  fi
  if mv "$dir" "$VAULT_SKILLS/$name" && ln -s "$VAULT_SKILLS/$name" "$dir"; then
    moved+=("$name")
  fi
done

for dir in "$VAULT_SKILLS"/*/; do
  dir="${dir%/}"
  name="$(basename "$dir")"
  [ -f "$dir/SKILL.md" ] || continue
  link="$USER_SKILLS/$name"
  if [ -L "$link" ]; then
    [ "$(readlink "$link")" = "$dir" ] || conflicts+=("$name")
    continue
  fi
  [ -e "$link" ] && continue
  ln -s "$dir" "$link" && linked+=("$name")
done

for link in "$USER_SKILLS"/*; do
  [ -L "$link" ] && [ ! -e "$link" ] || continue
  case "$(readlink "$link")" in
    "$VAULT_SKILLS"/*) rm "$link" ;;
  esac
done

msg=""
[ ${#moved[@]} -gt 0 ] && msg+="Skills movidas para o Second Brain: ${moved[*]}. "
[ ${#linked[@]} -gt 0 ] && msg+="Skills do Second Brain ativadas: ${linked[*]}. "
[ ${#conflicts[@]} -gt 0 ] && msg+="Conflito de nome entre ~/.claude/skills e o vault (resolver à mão): ${conflicts[*]}. "
if [ -n "$msg" ]; then
  printf '{"systemMessage": "%s"}\n' "${msg% }"
fi
exit 0
