#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


TARGET_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def main() -> int:
    run_root = Path(sys.argv[1])
    repo_root = Path.cwd()
    src_root = repo_root / "src"
    all_text = []
    for root in (src_root, repo_root / "tests"):
        if root.exists():
            for path in root.rglob("*.py"):
                all_text.append(path.read_text(encoding="utf-8", errors="ignore"))
    haystack = "\n".join(all_text)
    rows = []
    if src_root.exists():
        for path in sorted(src_root.rglob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
            except SyntaxError:
                continue
            for node in tree.body:
                if isinstance(node, TARGET_TYPES) and not node.name.startswith("_"):
                    count = haystack.count(node.name)
                    suspicion = "do-not-touch-yet"
                    if count <= 1:
                        suspicion = "high-suspicion-dead"
                    elif count == 2:
                        suspicion = "needs-proof"
                    rows.append({
                        "name": node.name,
                        "path": str(path.relative_to(repo_root)),
                        "kind": type(node).__name__,
                        "reference_count": count,
                        "test_reference_count": 0,
                        "production_reference_count": max(count - 1, 0),
                        "suspicion": suspicion,
                    })
    obj = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "symbol_reachability_census",
        "schema_version": 1,
        "symbols": rows,
    }
    out = run_root / "reports" / "symbol_reachability_census.json"
    out.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
