#!/bin/zsh
set -euo pipefail

RUN_ROOT="${1:?run root required}"
REPORT="$RUN_ROOT/reports/gitnexus_snapshot.json"
LOG="$RUN_ROOT/logs/gitnexus.log"

repo_root="$(pwd)"
tool_status="missing"
notes=()

if command -v gitnexus >/dev/null 2>&1; then
  tool_status="available"
  { gitnexus status || true; } > "$LOG" 2>&1
  for candidate in .gitnexus .gitnexus-cache gitnexus.json; do
    if [ -e "$candidate" ]; then
      python3 /Users/litiezhu/.codex/skills/ai-repo-cleanup/scripts/externalize_repo_artifacts.py "$RUN_ROOT" "$candidate" >/dev/null 2>&1 || true
      notes+=("externalized:$candidate")
    fi
  done
else
  : > "$LOG"
fi

python3 - "$repo_root" "$REPORT" "$tool_status" "$LOG" "${(j:;:)notes}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
repo_root, report, status, log, notes = sys.argv[1:]
obj = {
    "run_id": Path(report).parent.parent.name,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "repo_root": repo_root,
    "tool_name": "run_gitnexus_snapshot",
    "schema_version": 1,
    "status": status,
    "log_path": log,
    "notes": [item for item in notes.split(';') if item],
}
Path(report).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY
