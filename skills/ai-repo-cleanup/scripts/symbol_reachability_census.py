#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from census_utils import parse_python, resolve_repo_root

TARGET_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate whether exported symbols have meaningful production or test reachability.")
    parser.add_argument("run_root", help="Run root created by prepare_tmp_workspace.py")
    parser.add_argument("--repo-root", default=None, help="Target repository root. Defaults to run_manifest repo_root, then cwd.")
    parser.add_argument("--out", default=None, help="Output JSON path. Defaults to <run_root>/reports/symbol_reachability_census.json")
    return parser.parse_args()


def _token_counts(path: Path) -> Counter[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return Counter(text.replace("(", " ").replace(")", " ").replace(",", " ").split())


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    repo_root = resolve_repo_root(run_root, args.repo_root)
    src_root = repo_root / "src"
    tests_root = repo_root / "tests"
    counters: dict[Path, Counter[str]] = {}
    for root in (src_root, tests_root):
        if root.exists():
            for path in sorted(root.rglob("*.py")):
                counters[path] = _token_counts(path)
    rows = []
    if src_root.exists():
        for path in sorted(src_root.rglob("*.py")):
            tree = parse_python(path)
            if tree is None:
                continue
            for node in tree.body:
                if isinstance(node, TARGET_TYPES) and not node.name.startswith("_"):
                    production_refs = 0
                    test_refs = 0
                    for other, counter in counters.items():
                        count = counter[node.name]
                        if count <= 0:
                            continue
                        if other == path:
                            count = max(count - 1, 0)
                        if count <= 0:
                            continue
                        if tests_root.exists() and other.is_relative_to(tests_root):
                            test_refs += count
                        else:
                            production_refs += count
                    reference_count = production_refs + test_refs + 1
                    suspicion = "do-not-touch-yet"
                    if production_refs == 0 and test_refs == 0:
                        suspicion = "high-suspicion-dead"
                    elif production_refs == 0:
                        suspicion = "test-only-proof"
                    elif production_refs <= 1:
                        suspicion = "needs-proof"
                    rows.append(
                        {
                            "name": node.name,
                            "path": str(path.relative_to(repo_root)),
                            "kind": type(node).__name__,
                            "reference_count": reference_count,
                            "test_reference_count": test_refs,
                            "production_reference_count": production_refs,
                            "suspicion": suspicion,
                        }
                    )
    obj = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "symbol_reachability_census",
        "schema_version": 1,
        "symbols": rows,
    }
    out = Path(args.out).expanduser().resolve() if args.out else run_root / "reports" / "symbol_reachability_census.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
