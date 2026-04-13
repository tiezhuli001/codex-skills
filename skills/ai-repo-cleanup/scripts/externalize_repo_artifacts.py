#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: externalize_repo_artifacts.py <run_root> <path> [<path> ...]", file=sys.stderr)
        return 2
    run_root = Path(sys.argv[1])
    repo_root = Path.cwd()
    artifacts_dir = run_root / "artifacts"
    moved = []
    for raw in sys.argv[2:]:
        src = repo_root / raw
        if not src.exists():
            continue
        dst = artifacts_dir / src.name
        if dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        shutil.move(str(src), str(dst))
        moved.append({"from": str(src.relative_to(repo_root)), "to": str(dst)})
    obj = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "externalize_repo_artifacts",
        "schema_version": 1,
        "moved": moved,
    }
    out = run_root / "reports" / "artifact_externalization.json"
    out.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
