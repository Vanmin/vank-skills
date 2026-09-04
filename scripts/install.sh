#!/usr/bin/env bash
# Install Vank as one gstack-style bundle.
# Nested vk-* skills are discovered inside the vank directory.
# Pass --with-shims only for hosts that do not recurse into the bundle.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_DIR="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"
CLAUDE_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
CURSOR_DIR="${CURSOR_SKILLS_DIR:-$HOME/.cursor/skills}"
AGENTS_DIR="${AGENTS_SKILLS_DIR:-$HOME/.agents/skills}"
LOCAL_BIN_DIR="${LOCAL_BIN_DIR:-$HOME/.local/bin}"
DRY_RUN="false"
WITH_SHIMS="false"
BACKUP_ROOT=""
LINK_COUNT=0
REMOVED_COUNT=0

SKILL_NAMES=(
  vk-question vk-read vk-roadmap vk-request vk-restrict
  vk-work vk-review vk-submit vk-writer vk-ios-agents
  vk-diagram-guard vk-write-lark vk-skill-man
)

usage() {
  cat <<'EOF'
Usage:
  scripts/install.sh [--dry-run] [--with-shims]

Default:
  - Link this repo to ~/.codex/skills/vank, ~/.claude/skills/vank, ~/.cursor/skills/vank
  - Keep child skills nested in the bundle (gstack-style discovery)
  - Remove host-root vk-* shims that pointed at this repo or a legacy flat package
  - chmod +x vk-submit/scripts/vkpush and pin it to ~/.local/bin/vkpush when present

--with-shims:
  Also plant vk-* directory links at the host skill root for hosts that do not recurse.

Optional env:
  CODEX_SKILLS_DIR CLAUDE_SKILLS_DIR CURSOR_SKILLS_DIR AGENTS_SKILLS_DIR LOCAL_BIN_DIR
EOF
}

resolve_path() {
  python3 - "$1" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve(strict=False))
PY
}

ensure_link() {
  local src="$1"
  local dst="$2"
  local parent current_target=""
  parent="$(dirname "$dst")"

  if [[ "$DRY_RUN" == "true" ]]; then
    echo "link $dst -> $src"
    LINK_COUNT=$((LINK_COUNT + 1))
    return
  fi

  mkdir -p "$parent"

  if [[ -L "$dst" ]]; then
    current_target="$(readlink "$dst")"
    if [[ "$current_target" == "$src" ]]; then
      LINK_COUNT=$((LINK_COUNT + 1))
      return
    fi
    ln -sfn "$src" "$dst"
    LINK_COUNT=$((LINK_COUNT + 1))
    return
  fi

  if [[ -e "$dst" ]]; then
    if [[ -z "$BACKUP_ROOT" ]]; then
      BACKUP_ROOT="$HOME/.skills_link_backup/$(date +%Y%m%d_%H%M%S)"
      mkdir -p "$BACKUP_ROOT"
    fi
    mv "$dst" "$BACKUP_ROOT/$(basename "$dst")"
    echo "backed_up=$BACKUP_ROOT/$(basename "$dst")"
  fi

  ln -s "$src" "$dst"
  LINK_COUNT=$((LINK_COUNT + 1))
}

remove_legacy_shim() {
  local path="$1"
  local child_name="$2"
  local actual expected_vank
  [[ -e "$path" || -L "$path" ]] || return 0
  actual="$(resolve_path "$path")"
  expected_vank="$(resolve_path "$ROOT_DIR/$child_name")"
  if [[ "$actual" != "$expected_vank" && "$actual" != *"/legacy flat package/${child_name}" ]]; then
    return 0
  fi
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "would_remove_shim=$path"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
    return 0
  fi
  rm -rf "$path"
  echo "removed_shim=$path"
  REMOVED_COUNT=$((REMOVED_COUNT + 1))
}

maybe_link_bundle() {
  local dest_root="$1"
  local parent
  parent="$(dirname "$dest_root")"
  if [[ ! -d "$parent" && "$DRY_RUN" != "true" ]]; then
    mkdir -p "$parent"
  fi
  if [[ -d "$parent" || "$DRY_RUN" == "true" ]]; then
    ensure_link "$ROOT_DIR" "$dest_root/vank"
  fi
}

assert_layout() {
  local name
  if [[ ! -f "$ROOT_DIR/SKILL.md" ]]; then
    echo "missing router: $ROOT_DIR/SKILL.md" >&2
    exit 1
  fi
  if [[ ! -f "$ROOT_DIR/shared/vk-core-contract.md" ]]; then
    echo "missing shared contract: $ROOT_DIR/shared/vk-core-contract.md" >&2
    exit 1
  fi
  for name in "${SKILL_NAMES[@]}"; do
    if [[ ! -f "$ROOT_DIR/$name/SKILL.md" ]]; then
      echo "missing child skill: $ROOT_DIR/$name/SKILL.md" >&2
      exit 1
    fi
  done
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    --with-shims)
      WITH_SHIMS="true"
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

assert_layout

echo "repo=$ROOT_DIR"
echo "dry_run=$DRY_RUN"
echo "with_shims=$WITH_SHIMS"

maybe_link_bundle "$CODEX_DIR"
maybe_link_bundle "$CLAUDE_DIR"
maybe_link_bundle "$CURSOR_DIR"
if [[ -d "$(dirname "$AGENTS_DIR")" || "$DRY_RUN" == "true" ]]; then
  maybe_link_bundle "$AGENTS_DIR"
fi

if [[ -f "$ROOT_DIR/vk-submit/scripts/vkpush" ]]; then
  if [[ "$DRY_RUN" != "true" ]]; then
    chmod +x "$ROOT_DIR/vk-submit/scripts/vkpush"
  fi
  ensure_link "$ROOT_DIR/vk-submit/scripts/vkpush" "$LOCAL_BIN_DIR/vkpush"
fi

for name in "${SKILL_NAMES[@]}"; do
  if [[ "$WITH_SHIMS" == "true" ]]; then
    ensure_link "$ROOT_DIR/$name" "$CODEX_DIR/$name"
    ensure_link "$ROOT_DIR/$name" "$CLAUDE_DIR/$name"
    if [[ -d "$CURSOR_DIR" || "$DRY_RUN" == "true" ]]; then
      ensure_link "$ROOT_DIR/$name" "$CURSOR_DIR/$name"
    fi
  else
    remove_legacy_shim "$CODEX_DIR/$name" "$name"
    remove_legacy_shim "$CLAUDE_DIR/$name" "$name"
    remove_legacy_shim "$CURSOR_DIR/$name" "$name"
    remove_legacy_shim "$AGENTS_DIR/$name" "$name"
  fi
done

echo "links=$LINK_COUNT"
echo "removed_shims=$REMOVED_COUNT"
if [[ -n "$BACKUP_ROOT" ]]; then
  echo "backup=$BACKUP_ROOT"
fi
echo "bundle=$CODEX_DIR/vank"
echo "[OK] vank installed as one package."
