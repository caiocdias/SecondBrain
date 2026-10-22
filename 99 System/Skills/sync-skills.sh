#!/usr/bin/env bash
# Mantém ~/.claude/skills/ apontando para as skills versionadas neste diretório do vault
# e registra em plugins.txt os plugins instalados pelo usuário.
# Executado pelos hooks SessionStart e SessionEnd de ~/.claude/settings.json; pode ser rodado à mão.
#
# 1. Skill nova (ou plugin local criado com `claude plugin init`) instalada ou criada diretamente
#    em ~/.claude/skills/ é movida para cá e substituída por um link simbólico.
# 2. Skill criada aqui sem link em ~/.claude/skills/ ganha o link.
# 3. Links para skills removidas daqui são apagados.
# 4. Plugin de marketplace instalado no escopo de usuário e ausente de plugins.txt é acrescentado.
#    O registro só cresce: remoções são feitas à mão.
#
# ~/.claude/skills/synced/ (skills sincronizadas do claude.ai) é gerenciado pelo Claude Code e fica de fora.

set -u

VAULT_SKILLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
USER_SKILLS="$CONFIG_DIR/skills"
PLUGINS_FILE="$VAULT_SKILLS/plugins.txt"

is_skill_dir() { [ -f "$1/SKILL.md" ] || [ -f "$1/.claude-plugin/plugin.json" ]; }

mkdir -p "$USER_SKILLS"
moved=()
linked=()
conflicts=()
registered=()
notes=()

for dir in "$USER_SKILLS"/*/; do
  dir="${dir%/}"
  name="$(basename "$dir")"
  [ "$name" = "synced" ] && continue
  [ -L "$dir" ] && continue
  is_skill_dir "$dir" || continue
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
  is_skill_dir "$dir" || continue
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

# Lista "<plugin>@<marketplace> <origem do marketplace>" dos plugins de escopo de usuário.
list_user_plugins() {
  local installed="$CONFIG_DIR/plugins/installed_plugins.json"
  local known="$CONFIG_DIR/plugins/known_marketplaces.json"
  [ -f "$installed" ] || return 0
  if command -v python3 >/dev/null 2>&1; then
    python3 -I - "$installed" "$known" <<'PY'
import json, sys
def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
installed = load(sys.argv[1]).get("plugins", {})
known = load(sys.argv[2])
for pid, entries in installed.items():
    if not any(e.get("scope") == "user" for e in entries):
        continue
    source = known.get(pid.rsplit("@", 1)[-1], {}).get("source", {})
    origin = source.get("repo") or source.get("url") or source.get("path") or source.get("package") or ""
    print(f"{pid} {origin}".rstrip())
PY
  elif command -v jq >/dev/null 2>&1; then
    local known_json='{}'
    [ -f "$known" ] && known_json="$(cat "$known")"
    jq -r --argjson known "$known_json" '
      (.plugins // {}) | to_entries[]
      | select(any(.value[]; .scope == "user"))
      | .key as $id
      | ($known[$id | split("@") | last].source // {}) as $s
      | "\($id) \($s.repo // $s.url // $s.path // $s.package // "")" | rtrimstr(" ")
    ' "$installed"
  else
    echo "!sem-parser"
  fi
}

while IFS= read -r line; do
  [ -n "$line" ] || continue
  if [ "$line" = "!sem-parser" ]; then
    notes+=("instale python3 ou jq para registrar os plugins no Second Brain")
    continue
  fi
  id="${line%% *}"
  case "$id" in *@skills-dir) continue ;; esac
  if [ ! -f "$PLUGINS_FILE" ]; then
    printf '%s\n' \
      "# Plugins do Claude Code registrados no Second Brain (escopo de usuário)." \
      "# Uma linha por plugin: <plugin>@<marketplace> <origem do marketplace>." \
      "# sync-skills acrescenta plugins novos; remoções são manuais. Reinstalação: 99 System/AI/setup.md." \
      > "$PLUGINS_FILE"
  fi
  grep -v '^#' "$PLUGINS_FILE" | cut -d' ' -f1 | grep -qxF "$id" && continue
  printf '%s\n' "$line" >> "$PLUGINS_FILE"
  registered+=("$id")
done < <(list_user_plugins)

msg=""
[ ${#moved[@]} -gt 0 ] && msg+="Skills movidas para o Second Brain: ${moved[*]}. "
[ ${#linked[@]} -gt 0 ] && msg+="Skills do Second Brain ativadas: ${linked[*]}. "
[ ${#registered[@]} -gt 0 ] && msg+="Plugins registrados no Second Brain: ${registered[*]}. "
[ ${#conflicts[@]} -gt 0 ] && msg+="Conflito de nome entre ~/.claude/skills e o vault (resolver à mão): ${conflicts[*]}. "
[ ${#notes[@]} -gt 0 ] && msg+="Aviso: ${notes[*]}. "
if [ -n "$msg" ]; then
  printf '{"systemMessage": "%s"}\n' "${msg% }"
fi
exit 0
