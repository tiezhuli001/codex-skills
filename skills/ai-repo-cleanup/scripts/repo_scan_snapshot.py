#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from census_utils import resolve_repo_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture git status and diff snapshots for one cleanup run.")
    parser.add_argument("run_root", help="Run root created by prepare_tmp_workspace.py")
    parser.add_argument("--repo-root", default=None, help="Target repository root. Defaults to run_manifest repo_root, then cwd.")
    return parser.parse_args()


def _git_lines(repo_root: Path, *args: str) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), *args],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return []
    return result.stdout.splitlines()


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    repo_root = resolve_repo_root(run_root, args.repo_root)
    report = run_root / "reports" / "repo_scan_snapshot.json"
    status_file = run_root / "snapshots" / "git_status.txt"
    diff_file = run_root / "snapshots" / "git_diff_stat.txt"
    status_file.parent.mkdir(parents=True, exist_ok=True)
    diff_file.parent.mkdir(parents=True, exist_ok=True)

    status_lines = _git_lines(repo_root, "status", "--short")
    diff_lines = _git_lines(repo_root, "diff", "--stat")
    status_file.write_text("\n".join(status_lines) + ("\n" if status_lines else ""), encoding="utf-8")
    diff_file.write_text("\n".join(diff_lines) + ("\n" if diff_lines else ""), encoding="utf-8")

    obj = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "repo_scan_snapshot",
        "schema_version": 1,
        "git_status": status_lines,
        "diff_stat": diff_lines,
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
