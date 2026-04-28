#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from census_utils import externalize_paths, resolve_repo_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Move repo-local audit artifacts into the run_root artifacts directory.")
    parser.add_argument("run_root", help="Run root created by prepare_tmp_workspace.py")
    parser.add_argument("paths", nargs="+", help="Repo-relative paths to move into run_root/artifacts")
    parser.add_argument("--repo-root", default=None, help="Target repository root. Defaults to run_manifest repo_root, then cwd.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    repo_root = resolve_repo_root(run_root, args.repo_root)
    moved = externalize_paths(repo_root, run_root, args.paths)
    obj = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "externalize_repo_artifacts",
        "schema_version": 1,
        "moved": moved,
    }
    out = run_root / "reports" / "artifact_externalization.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
