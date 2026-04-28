#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from census_utils import externalize_paths, resolve_repo_root


CANDIDATE_ARTIFACTS = [".gitnexus", ".gitnexus-cache", "gitnexus.json"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture optional gitnexus state without leaving repo-local artifacts behind.")
    parser.add_argument("run_root", help="Run root created by prepare_tmp_workspace.py")
    parser.add_argument("--repo-root", default=None, help="Target repository root. Defaults to run_manifest repo_root, then cwd.")
    parser.add_argument("--out", default=None, help="Output JSON path. Defaults to <run_root>/reports/run_gitnexus_snapshot.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    repo_root = resolve_repo_root(run_root, args.repo_root)
    report = run_root / "reports" / "gitnexus_snapshot.json"
    log = run_root / "logs" / "gitnexus.log"
    log.parent.mkdir(parents=True, exist_ok=True)

    tool_status = "missing"
    notes: list[str] = []
    gitnexus_bin = shutil.which("gitnexus")
    if gitnexus_bin:
        tool_status = "available"
        result = subprocess.run(
            [gitnexus_bin, "status"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
        log.write_text((result.stdout or "") + (result.stderr or ""), encoding="utf-8")
        moved = externalize_paths(repo_root, run_root, [p for p in CANDIDATE_ARTIFACTS if (repo_root / p).exists()])
        notes.extend(f"externalized:{item['from']}" for item in moved)
    else:
        log.write_text("", encoding="utf-8")

    obj = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "run_gitnexus_snapshot",
        "schema_version": 1,
        "status": tool_status,
        "log_path": str(log),
        "notes": notes,
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
