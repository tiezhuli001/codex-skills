#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

TEST_DEF = re.compile(r"^\s*def\s+test_|^\s*class\s+Test", re.MULTILINE)


def line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        return sum(1 for _ in fh)


def main() -> int:
    run_root = Path(sys.argv[1])
    repo_root = Path.cwd()
    tests = repo_root / "tests"
    families = []
    if tests.exists():
        for path in sorted(tests.iterdir()):
            if not path.is_dir():
                continue
            files = sorted(path.rglob("test*.py"))
            families.append({
                "path": str(path.relative_to(repo_root)),
                "file_count": len(files),
                "line_count": sum(line_count(f) for f in files),
                "test_count": sum(len(TEST_DEF.findall(f.read_text(encoding="utf-8", errors="ignore"))) for f in files),
            })
        for file in sorted(tests.glob("test_*.py")):
            families.append({
                "path": str(file.relative_to(repo_root)),
                "file_count": 1,
                "line_count": line_count(file),
                "test_count": len(TEST_DEF.findall(file.read_text(encoding="utf-8", errors="ignore"))),
            })
    obj = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "test_surface_census",
        "schema_version": 1,
        "families": families,
    }
    out = run_root / "reports" / "test_surface_census.json"
    out.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
