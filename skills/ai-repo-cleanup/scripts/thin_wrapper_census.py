#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from datetime import datetime, timezone
from pathlib import Path

from census_utils import parse_python, resolve_repo_root


WRAPPER_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find thin forwarding wrappers that may be merged back into their only real owner.")
    parser.add_argument("--run-root", required=True, help="Run root created by prepare_tmp_workspace.py or run_full_audit.py")
    parser.add_argument("--repo-root", default=None, help="Target repository root override. Defaults to run_manifest repo_root, then cwd.")
    parser.add_argument("--out", default=None, help="Output JSON path. Defaults to <run_root>/reports/thin_wrapper_census.json")
    return parser.parse_args()


def _target_calls(node: ast.AST) -> list[str]:
    calls: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Name):
                calls.append(func.id)
            elif isinstance(func, ast.Attribute):
                calls.append(func.attr)
    return calls


def _is_thin_wrapper(node: ast.AST) -> tuple[bool, list[str], int]:
    body = getattr(node, "body", [])
    statement_count = len(body)
    if statement_count != 1:
        return False, [], statement_count
    stmt = body[0]
    if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Call):
        calls = _target_calls(stmt.value)
        return len(calls) == 1, calls, statement_count
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        calls = _target_calls(stmt.value)
        return len(calls) == 1, calls, statement_count
    return False, [], statement_count


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).expanduser().resolve()
    repo_root = resolve_repo_root(run_root, args.repo_root)
    out = Path(args.out).expanduser().resolve() if args.out else run_root / "reports" / "thin_wrapper_census.json"
    items = []
    src_root = repo_root / "src"
    if src_root.exists():
        for path in sorted(src_root.rglob("*.py")):
            tree = parse_python(path)
            if tree is None:
                continue
            for node in getattr(tree, "body", []):
                if not isinstance(node, WRAPPER_TYPES):
                    continue
                is_wrapper, target_calls, statement_count = _is_thin_wrapper(node)
                if not is_wrapper:
                    continue
                items.append(
                    {
                        "path": str(path.relative_to(repo_root)),
                        "symbol": node.name,
                        "kind": "async-function" if isinstance(node, ast.AsyncFunctionDef) else "function",
                        "target_calls": target_calls,
                        "statement_count": statement_count,
                        "signals": ["thin-wrapper"],
                    }
                )
    payload = {
        "run_id": run_root.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "tool_name": "thin_wrapper_census",
        "schema_version": 1,
        "items": items,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
