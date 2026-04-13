#!/bin/zsh
set -euo pipefail

RUN_ROOT="${1:?run root required}"
REPORT="$RUN_ROOT/reports/repo_scan_snapshot.json"
STATUS_FILE="$RUN_ROOT/snapshots/git_status.txt"
DIFF_FILE="$RUN_ROOT/snapshots/git_diff_stat.txt"

repo_root="$(pwd)"

git status --short > "$STATUS_FILE" || true
git diff --stat > "$DIFF_FILE" || true

python3 - "$repo_root" "$REPORT" "$STATUS_FILE" "$DIFF_FILE" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

repo_root, report, status_file, diff_file = sys.argv[1:]
obj = {
    "run_id": Path(report).parent.parent.name,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "repo_root": repo_root,
    "tool_name": "repo_scan_snapshot",
    "schema_version": 1,
    "git_status": Path(status_file).read_text(encoding="utf-8").splitlines(),
    "diff_stat": Path(diff_file).read_text(encoding="utf-8").splitlines(),
}
Path(report).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY
