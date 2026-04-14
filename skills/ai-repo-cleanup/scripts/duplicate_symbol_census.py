#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from census_utils import iter_python_files, parse_python


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def canonical_function(node: ast.AST) -> str:
    if isinstance(node, ast.FunctionDef):
        clone = ast.FunctionDef(
            name="_",
            args=node.args,
            body=node.body,
            decorator_list=[],
            returns=None,
            type_comment=None,
            type_params=getattr(node, "type_params", []),
        )
        return ast.dump(clone, include_attributes=False)
    if isinstance(node, ast.AsyncFunctionDef):
        clone = ast.AsyncFunctionDef(
            name="_",
            args=node.args,
            body=node.body,
            decorator_list=[],
            returns=None,
            type_comment=None,
            type_params=getattr(node, "type_params", []),
        )
        return ast.dump(clone, include_attributes=False)
    return ""


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for path in iter_python_files(root):
        tree = parse_python(path)
        if tree is None:
            continue
        for node in getattr(tree, "body", []):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            canonical = canonical_function(node)
            if not canonical:
                continue
            key = hashlib.sha1(canonical.encode("utf-8")).hexdigest()
            groups[key].append(
                {
                    "path": str(path.relative_to(root)),
                    "symbol": node.name,
                    "kind": "async-function" if isinstance(node, ast.AsyncFunctionDef) else "function",
                    "lineno": node.lineno,
                    "end_lineno": getattr(node, "end_lineno", node.lineno),
                }
            )

    duplicate_groups = []
    for key, items in sorted(groups.items()):
        if len(items) < 2:
            continue
        duplicate_groups.append(
            {
                "group_id": f"dup_{key[:10]}",
                "match_kind": "ast-equivalent",
                "items": items,
                "signals": ["duplicate-implementation"],
            }
        )

    payload = {
        "run_id": out.parent.parent.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "tool_name": "duplicate_symbol_census",
        "schema_version": 1,
        "duplicate_groups": duplicate_groups,
    }
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
