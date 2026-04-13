#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BRANCH_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.Match)


def main() -> int:
    run_root = Path(sys.argv[1])
    repo_root = Path.cwd()
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
    out = run_root / "reports" / "complexity_budget_census.json"
    out.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
