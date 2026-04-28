#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from datetime import datetime, timezone
from pathlib import Path

from census_utils import resolve_repo_root

BRANCH_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.Match)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure file size, function count, and branch-like density for cleanup budgeting.")
    parser.add_argument("run_root", help="Run root created by prepare_tmp_workspace.py")
    parser.add_argument("--repo-root", default=None, help="Target repository root. Defaults to run_manifest repo_root, then cwd.")
    parser.add_argument("--out", default=None, help="Output JSON path. Defaults to <run_root>/reports/complexity_budget_census.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    repo_root = resolve_repo_root(run_root, args.repo_root)
    rows = []
    for base in (repo_root / "src", repo_root / "tests"):
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue
            rows.append({
                "path": str(path.relative_to(repo_root)),
                "line_count": len(text.splitlines()),
                "function_count": sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree)),
                "branch_like_count": sum(isinstance(n, BRANCH_NODES) for n in ast.walk(tree)),
                "broad_exception_count": text.count("except Exception"),
            })
    obj = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "complexity_budget_census",
        "schema_version": 1,
        "files": rows,
    }
    out = Path(args.out).expanduser().resolve() if args.out else run_root / "reports" / "complexity_budget_census.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
