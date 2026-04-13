#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="${CODEX_HOME:-$HOME/.codex}/skills"

mkdir -p "$SKILLS_DIR"

if [ "$#" -eq 0 ]; then
  targets=(ai-repo-cleanup long-run-execution)
else
  targets=("$@")
fi

for skill in "${targets[@]}"; do
  src="$REPO_ROOT/skills/$skill"
  dst="$SKILLS_DIR/$skill"
  if [ ! -d "$src" ]; then
    echo "[codex-skills] unknown skill: $skill" >&2
    exit 1
  fi
  rm -rf "$dst"
  cp -R "$src" "$dst"
  echo "[codex-skills] installed: $skill -> $dst"
done

printf '
Done. Restart Codex or start a new session to pick up updated skills.
'
