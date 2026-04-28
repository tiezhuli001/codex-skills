#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create one externalized tmp workspace for an ai-repo-cleanup run.")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Target repository root to record in run_manifest.json. Defaults to current working directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = Path("/tmp/skill/ai-repo-cleanup/runs") / stamp
    for name in ("artifacts", "reports", "snapshots", "logs"):
        (root / name).mkdir(parents=True, exist_ok=True)
    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else Path.cwd().resolve()
    manifest = {
        "run_id": stamp,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool_name": "prepare_tmp_workspace",
        "schema_version": 1,
        "run_root": str(root),
        "reports_dir": str(root / "reports"),
        "artifacts_dir": str(root / "artifacts"),
        "snapshots_dir": str(root / "snapshots"),
        "logs_dir": str(root / "logs"),
        "repo_root": str(repo_root),
    }
    out = root / "reports" / "run_manifest.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(str(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
