#!/usr/bin/env bash
# Remove Vank bundle links and vk-* shims that point at this repo.
# Does not delete the git repository.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_DIR="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"
CLAUDE_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
CURSOR_DIR="${CURSOR_SKILLS_DIR:-$HOME/.cursor/skills}"
AGENTS_DIR="${AGENTS_SKILLS_DIR:-$HOME/.agents/skills}"
LOCAL_BIN_DIR="${LOCAL_BIN_DIR:-$HOME/.local/bin}"
DRY_RUN="false"
SKILL_NAMES=()

discover_skill_names() {
  local skill_md name
  local names=()
  shopt -s nullglob
  for skill_md in "$ROOT_DIR"/vk-*/SKILL.md; do
    name="$(basename "$(dirname "$skill_md")")"
    names+=("$name")
  done
  shopt -u nullglob
  if [[ ${#names[@]} -eq 0 ]]; then
    echo "no child skills found under $ROOT_DIR/vk-*/SKILL.md" >&2
    exit 1
  fi
  while IFS= read -r name; do
    SKILL_NAMES+=("$name")
  done < <(printf '%s\n' "${names[@]}" | sort)
}

usage() {
  cat <<'EOF'
Usage:
  scripts/uninstall.sh [--dry-run]

Removes only symlinks that point at this repo (vank bundle, vk-* shims, ~/.local/bin/vkpush).
Does not delete this git repository.
EOF
}

resolve_path() {
  python3 - "$1" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve(strict=False))
PY
}

remove_if_points_here() {
  local path="$1"
  local expected="$2"
  local actual
  [[ -L "$path" || -e "$path" ]] || return 0
  actual="$(resolve_path "$path")"
  expected="$(resolve_path "$expected")"
  if [[ "$actual" != "$expected" ]]; then
    return 0
  fi
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "would_remove=$path"
    return 0
  fi
  rm -rf "$path"
  echo "removed=$path"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

discover_skill_names
echo "repo=$ROOT_DIR"
echo "dry_run=$DRY_RUN"

for root in "$CODEX_DIR" "$CLAUDE_DIR" "$CURSOR_DIR" "$AGENTS_DIR"; do
  remove_if_points_here "$root/vank" "$ROOT_DIR"
  for name in "${SKILL_NAMES[@]}"; do
    remove_if_points_here "$root/$name" "$ROOT_DIR/$name"
  done
done

remove_if_points_here "$LOCAL_BIN_DIR/vkpush" "$ROOT_DIR/vk-submit/scripts/vkpush"

echo "[OK] vank links cleaned."
