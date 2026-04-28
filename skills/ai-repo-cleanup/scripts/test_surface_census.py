#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from census_utils import resolve_repo_root

TEST_DEF = re.compile(r"^\s*def\s+test_|^\s*class\s+Test", re.MULTILINE)


def line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        return sum(1 for _ in fh)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure test family size and density across the repository.")
    parser.add_argument("run_root", help="Run root created by prepare_tmp_workspace.py")
    parser.add_argument("--repo-root", default=None, help="Target repository root. Defaults to run_manifest repo_root, then cwd.")
    parser.add_argument("--out", default=None, help="Output JSON path. Defaults to <run_root>/reports/test_surface_census.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    repo_root = resolve_repo_root(run_root, args.repo_root)
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
    out = Path(args.out).expanduser().resolve() if args.out else run_root / "reports" / "test_surface_census.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
