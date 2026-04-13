#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = Path("/tmp/skill/ai-repo-cleanup/runs") / stamp
    for name in ("artifacts", "reports", "snapshots", "logs"):
        (root / name).mkdir(parents=True, exist_ok=True)
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
        "repo_root": os.getcwd(),
    }
    out = root / "reports" / "run_manifest.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(str(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
