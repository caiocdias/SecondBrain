#!/usr/bin/env bash
# Testa o bloco de souls de 99 System/Skills/sync-skills.sh num vault temporário (caminho com espaço).
set -u

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

VAULT="$TMP/meu vault"
mkdir -p "$VAULT/99 System/Souls"
cp -R "$SRC/Skills" "$VAULT/99 System/Skills"
cp -R "$SRC/Souls/agents" "$VAULT/99 System/Souls/agents"
export CLAUDE_CONFIG_DIR="$TMP/cfg"
SYNC="$VAULT/99 System/Skills/sync-skills.sh"
LINK="$CLAUDE_CONFIG_DIR/agents/second-brain-souls"
EXPECTED="$VAULT/99 System/Souls/agents"

fail=0
check() { if [ "$2" = "ok" ]; then echo "PASS: $1"; else echo "FAIL: $1"; fail=1; fi; }

out1="$("$SYNC")"
[ -L "$LINK" ] && [ "$(readlink "$LINK")" = "$EXPECTED" ] && r=ok || r=no
check "link criado apontando para Souls/agents do vault" "$r"
case "$out1" in *"Souls do Second Brain ativadas"*) r=ok ;; *) r=no ;; esac
check "primeira execução informa a ativação" "$r"

out2="$("$SYNC")"
case "$out2" in *"Souls do Second Brain ativadas"*|*Conflito*) r=no ;; *) r=ok ;; esac
check "segunda execução é silenciosa" "$r"

rm "$LINK"; mkdir -p "$TMP/outro"; ln -s "$TMP/outro" "$LINK"
out3="$("$SYNC")"
case "$out3" in *Conflito*) r=ok ;; *) r=no ;; esac
check "link para outro destino gera Conflito" "$r"
case "$out3" in *"~/.claude/skills"*) r=no ;; *agents/second-brain-souls*) r=ok ;; *) r=no ;; esac
check "conflito das souls cita agents/second-brain-souls, não ~/.claude/skills" "$r"
[ "$(readlink "$LINK")" = "$TMP/outro" ] && r=ok || r=no
check "link em conflito não é alterado" "$r"

rm "$LINK"; mkdir "$LINK"
out4="$("$SYNC")"
case "$out4" in *Conflito*) r=ok ;; *) r=no ;; esac
check "diretório real no lugar do link gera Conflito" "$r"
[ -d "$LINK" ] && [ ! -L "$LINK" ] && r=ok || r=no
check "diretório real não é alterado" "$r"

rm -rf "$CLAUDE_CONFIG_DIR/agents"; printf 'x' > "$CLAUDE_CONFIG_DIR/agents"
out6="$("$SYNC" 2>/dev/null)"
case "$out6" in *"Falha ao sincronizar"*agents/second-brain-souls*) r=ok ;; *) r=no ;; esac
check "falha ao criar o link das souls é relatada" "$r"
rm -f "$CLAUDE_CONFIG_DIR/agents"

rm -rf "$LINK" "$VAULT/99 System/Souls"
out5="$("$SYNC")"
[ ! -e "$LINK" ] && [ -z "$out5" ] && r=ok || r=no
check "sem Souls/agents não faz nada" "$r"

exit "$fail"
