#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PATTERN = re.compile(r"(support|helper|helpers|view|adapter|util|utils)")
IMPORT_RE = re.compile(r"(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))")


def module_name(path: Path, repo_root: Path) -> str:
    rel = path.relative_to(repo_root / "src").with_suffix("")
    return ".".join(rel.parts)


def main() -> int:
    run_root = Path(sys.argv[1])
    repo_root = Path.cwd()
    src_root = repo_root / "src"
    py_files = list(src_root.rglob("*.py")) if src_root.exists() else []
    texts = {
        path: path.read_text(encoding="utf-8", errors="ignore") for path in py_files + list((repo_root / "tests").rglob("*.py"))
    }
    rows = []
    for path in sorted(py_files):
        if not PATTERN.search(path.name):
            continue
        mod = module_name(path, repo_root)
        real = 0
        test = 0
        for other, text in texts.items():
            if other == path:
                continue
            if mod in text:
                if "/tests/" in str(other) or str(other).startswith(str(repo_root / "tests")):
                    test += 1
                else:
                    real += 1
        rows.append({
            "path": str(path.relative_to(repo_root)),
            "kind": path.stem,
            "real_consumers": real,
            "test_consumers": test,
            "notes": "candidate only; verify ownership before deletion",
        })
    obj = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "support_split_census",
        "schema_version": 1,
        "paths": rows,
    }
    out = run_root / "reports" / "support_split_census.json"
    out.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
